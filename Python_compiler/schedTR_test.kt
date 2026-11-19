// ===================================================================
// TKT-055 / Ф3: честный позитивный TIMER_RET (IRET из обработчика тика)
// Файл: Python_compiler/schedTR_test.kt -> .ctos | Язык: KINII (стадия-0)
//
// Отличие от schedT_test.kt: обработчик тика НЕ ре-диспетчит через YIELD,
// а честно возвращается в прерванную точку через NID 0x154 TIMER_RET.
// VM и native_rt.c обязаны дать одну и ту же последовательность:
//   RESTORE(151) -> TIMER_ARM(153) -> TICK -> TIMER_RET(154) -> продолжение -> DONE
//
// Честный контракт тика (из native_rt.c / ctos_vm.py, без правки семантики):
//   have_kernel_ctx выставляется ТОЛЬКО в WORK_CTX_RESTORE (NID 0x151);
//   условие тика: tick_armed && have_kernel_ctx && ops>=tick_next && !tick_pending;
//   TIMER_RET (0x154) читает кадр 'TCK1', возвращает pc/acc/rts и снимает
//   tick_pending, НО не трогает have_kernel_ctx — таймер может тикать дальше.
//
// Маркеры: C901 START, C910 ARM OK, C940 тик, C941 IRET,
//   C94F тики>0, C9FF DONE; C9E0/C9E1/C9E5 — честные браки (не должны
//   появиться).
//
// Раскладка (Ring 2, ячейки, без пересечений):
//   0x00A12800 TMR1 (6), 0x00A12900 TCK1 (до 140),
//   0x00A12A00 TICKS, 0x00A12B00 WORK, 0x00A12C00 CTX1 (до ~172),
//   0x00F00000 окно статиков (4 ячейки); STREAM_CELL 0x00F00FF0.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: STREAM_CELL 0x00F00FF0
#define: NID_RESTORE 0x00000151
#define: NID_TARM    0x00000153
#define: NID_TRET    0x00000154

#define: TIMER_NODE  0x00A12800
#define: TRAP_BLOCK  0x00A12900
#define: TICKS       0x00A12A00
#define: WORK        0x00A12B00
#define: CTX_NODE    0x00A12C00

#define: STATICS_BASE  0x00F00000
#define: STATICS_COUNT 0x00000004
#define: TMR_MAGIC     0x544D5231
#define: CTX_MAGIC     0x43545831
#define: QUANTUM       0x00000040
#define: ITERS         0x00000020
#define: ENTRY_TICK    Tick_Ret_Handler
#define: ENTRY_TASK    Task_Entry

set static A = 0x00000000;
set static B = 0x00000000;
set static C = 0x00000000;
set static D = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000C901);       // START

    // ---- честный ядерный ctx-блок для RESTORE ----
    // magic 'CTX1', pc = Task_Entry, acc = 0, rts_len = 0,
    // окно статиков в +166 пустое (count = 0) — RESTORE не трогает статики.
    A = CTX_NODE;
    store_ind(A, CTX_MAGIC);
    A = CTX_NODE + 1;
    store_ind(A, ENTRY_TASK);
    A = CTX_NODE + 2;
    store_ind(A, 0x00000000);
    A = CTX_NODE + 3;
    store_ind(A, 0x00000000);
    A = CTX_NODE + 166;
    store_ind(A, 0x00000000);

    // RESTORE: kernel_ctx <- точка после sys_call, have_kernel_ctx = 1,
    // переход на Task_Entry с пустым rts.
    A = CTX_NODE;
    log_cell(STREAM_CELL, A);
    sys_call(NID_RESTORE);
    out_cell(LOG_PORT, 0x0000C9E1);       // BAD: сюда после RESTORE нельзя
    terminate;
}

// Эпоха задачи: haben_kernel_ctx уже = 1, тики разрешены.
function Task_Entry() {
    A = TIMER_NODE;
    store_ind(A, TMR_MAGIC);              // +0 'TMR1'
    A = TIMER_NODE + 1;
    store_ind(A, QUANTUM);                // +1 квант
    A = TIMER_NODE + 2;
    store_ind(A, TRAP_BLOCK);             // +2 trap-блок 'TCK1'
    A = TIMER_NODE + 3;
    store_ind(A, ENTRY_TICK);             // +3 вход обработчика
    A = TIMER_NODE + 4;
    store_ind(A, STATICS_BASE);           // +4 окно статиков
    A = TIMER_NODE + 5;
    store_ind(A, STATICS_COUNT);          // +5 размер окна
    A = TICKS;
    store_ind(A, 0x00000000);
    A = WORK;
    store_ind(A, 0x00000000);

    A = TIMER_NODE;
    log_cell(STREAM_CELL, A);
    sys_call(NID_TARM);                   // заводим таймер
    out_cell(LOG_PORT, 0x0000C910);       // ARM OK

    run Work();

    B = TICKS;
    C = in_cell(B);
    if (C == 0x00000000) {
        out_cell(LOG_PORT, 0x0000C9E0);   // BAD: тиков не было
    } else {
        out_cell(LOG_PORT, 0x0000C94F);   // тики > 0
    }
    out_cell(LOG_PORT, 0x0000C9FF);       // DONE
    terminate;
}

// Длинная работа без YIELD: тик вытесняет её по опкодам;
// TIMER_RET возвращает в прерванную точку этой же работы.
function Work() {
    B = WORK;
    D = in_cell(B);
    if (D == ITERS) {
    } else {
        D = D + 1;
        B = WORK;
        store_ind(B, D);
        run Work();
    }
}

// Честный IRET: кадр 'TCK1' уже записан VM/нативом по адресу TRAP_BLOCK.
// Статики, изменённые здесь, будут честно восстановлены TIMER_RET из кадра —
// счётчик тиков лежит в обычной ячейке TICKS и потому сохраняется.
function Tick_Ret_Handler() {
    out_cell(LOG_PORT, 0x0000C940);       // тик доставлен

    B = TICKS;
    C = in_cell(B);
    C = C + 1;
    store_ind(B, C);

    out_cell(LOG_PORT, 0x0000C941);       // IRET выполняется
    A = TRAP_BLOCK;
    log_cell(STREAM_CELL, A);             // arg: кадр прерванной точки
    sys_call(NID_TRET);                   // честный возврат в Work()
    out_cell(LOG_PORT, 0x0000C9E5);       // BAD: сюда после IRET нельзя
    terminate;
}
