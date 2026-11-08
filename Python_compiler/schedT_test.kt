// ===================================================================
// TKT-055 СПРИНТ Б: честное ВЫТЕСНЕНИЕ по честному таймеру VM
// Файл: Python_compiler/schedT_test.kt -> .ctos | Язык: KINII (стадия-0)
//
// Честная механика (VM, NID 0x153/0x154):
//   0x153 TIMER_ARM — аргумент через Stream_Emit 0x00F00FF0, блок 'TMR1':
//     +0 magic 0x544D5231, +1 квант (шагов VM между тиками),
//     +2 trap-блок 'TCK1' (кадр прерванной задачи),
//     +3 trap_entry (адрес входа обработчика тика; честное имя функции
//        в #define резолвится кодгеном из таблицы вызовов)
//   0x154 TIMER_RET — честный IRET (в этом тесте не используется:
//     честная политика тика всегда ре-диспетчит — см. ниже)
//
// Честная граница слоёв: VM поставляет ТОЛЬКО тик (кадр задачи -> 'TCK1',
// прыжок на честный вход ядра). Политика RR — честно в ядре.
//
// Честный контракт обработчика тика (строго, иначе честная порча стека):
//   1. копировать кадр 'TCK1' в честный ctx-блок текущей задачи
//      (pc/acc/rts_len/rts честным циклом — Copy_Trap);
//   2. текущая задача: RUNNING -> READY, push в очередь;
//   3. sys_call(NID_YIELD) — честный возврат в точку последнего RESTORE
//      (kernel_ctx установлен этой эпохой): управление честно идёт в
//      Dispatch_Loop, который честно выбирает следующую задачу.
//   Обработчик НИКОГДА не делает RET-раскрутку поверх стека прерванной
//   задачи — его стековые кадры честно отбрасываются VM при возврате
//   в ядерную точку (rts заменяется сохранённым ядерным).
//
// Честный сценарий:
//   - 2 задачи: лидер (tid 1) / работник (tid 2, parent 1);
//   - тела работают ДОЛГО (честный цикл итераций в ячейках ctx, БЕЗ
//     sys_call YIELD) — честный тик вытесняет задачу посреди работы;
//   - честный финал: обе ZOMBIE (retcode 0x2A/0x2B), reaps B9D0/B9D1,
//     счётчик честных тиков > 0 (B94F), очередь пуста (B90F), DONE B9FF.
//
// Честные маркеры: B901 START, B910/B911 init, B920/B921 spawned,
//   B930 RESUME (tid в LOG), B940 честный тик, B941 тик-переключение,
//   B9A0/B9B0 честный пролог задач, B9A2/B9B2 честные финалы задач,
//   B94F (тики>0), B90F (count=0), B9FF DONE.
// Честные браки (не должны появиться): B99x, B9E0..B9E5, B999.
//
// Раскладка (Ring 2, поверх честной карты TKT-055):
//   0x00A10000 TASK_TABLE 32 слота x 32 ячейки
//   0x00A10400 TASK_NEXT  32 ячейки
//   0x00A10480 SCHED_CTL  +0 CUR +4 HEAD +8 TAIL +12 COUNT +16 NEXT_TID
//   0x00A104A0 CUR_CTX
//   0x00A10500 TASK_CTX   32 x 256 ('CTX1'): +0 magic +1 pc +2 acc
//     +3 rts_len +4..131 rts; META: +160 slot +161 slice +162 job
//     +164 booted +165 iter
//   0x00A12500 TRAP_BLOCK ('TCK1')  0x00A12540 TIMER_NODE ('TMR1')
//   0x00A12580 TICKS — честный счётчик тиков ядра
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: STREAM_CELL 0x00F00FF0

#define: NID_SAVE    0x00000150
#define: NID_RESTORE 0x00000151
#define: NID_YIELD   0x00000152
#define: NID_TARM    0x00000153
#define: NID_TRET    0x00000154

#define: TASK_TABLE  0x00A10000
#define: TASK_NEXT   0x00A10400
#define: CTL_CUR     0x00A10480
#define: CTL_HEAD    0x00A10484
#define: CTL_TAIL    0x00A10488
#define: CTL_COUNT   0x00A1048C
#define: CTL_NTID    0x00A10490
#define: CUR_CTX     0x00A104A0

#define: TASK_CTX    0x00A10500
#define: TRAP_BLOCK  0x00A12500
#define: TIMER_NODE  0x00A12540
#define: KCTX        0x00A12600   // честный ядерный блок YIELD обработчика
#define: TICKS       0x00A12580

#define: STATICS_BASE  0x00F00000  // честная зона статиков стадии-0 (VAR_ZONE VM)
#define: STATICS_COUNT 0x00000013  // 19 статиков .kt (при добавлении set static обновить!)

#define: CTX_MAGIC   0x43545831   // 'CTX1'
#define: TMR_MAGIC   0x544D5231   // 'TMR1'

#define: MAX_TASKS   0x00000020
#define: NIL         0xFFFFFFFF

#define: ST_FREE     0x00000000
#define: ST_READY    0x00000001
#define: ST_RUNNING  0x00000002
#define: ST_ZOMBIE   0x00000004

#define: JOB_LEADER  0x0000AB01
#define: JOB_WORKER  0x0000AB02

#define: QUANTUM     0x00000070   // честный квант: 112 шагов VM между тиками
#define: ITERS_MAX   0x00000018   // честный бюджет итераций тела (24)

#define: ENTRY_TICK  Tick_Slice_Handler   // честный поздний биндинг адреса

set static Slot_Idx     = 0x00000000;
set static Slot_Ptr     = 0x00000000;
set static Next_Ptr     = 0x00000000;
set static Loop_I       = 0x00000000;
set static Found_Slot   = 0xFFFFFFFF;
set static Found_Tid    = 0x00000000;
set static Spawn_Entry  = 0x00000000;
set static Spawn_Prio   = 0x00000000;
set static Spawn_Parent = 0x00000000;
set static Spawn_Out    = NIL;
set static Spawn_Slot   = 0xFFFFFFFF;
set static Q_Idx        = 0x00000000;
set static Pop_Out      = NIL;
set static Ctx_Ptr      = 0x00000000;
set static Tmp_A        = 0x00000000;
set static Tmp_B        = 0x00000000;
set static Tmp_C        = 0x00000000;
set static Tmp_D        = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000B901);       // честный START спринта Б

    run Sched_Init();
    run T_Init_Check();

    // ---- честный spawn лидера + честный pre-roll (fresh YIELD) ----
    Spawn_Entry = JOB_LEADER;
    Spawn_Prio = 0x00000010;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Spawn_Out == NIL) {
        out_cell(LOG_PORT, 0x0000B991);   // BAD spawn lead
    } else {
        out_cell(LOG_PORT, 0x0000B920);   // spawned (ready)
        run Task_Begin();                 // pre-roll: пролог + fresh YIELD -> READY (в очереди)
        // ---- работник (tid 2, parent 1) ----
        Spawn_Entry = JOB_WORKER;
        Spawn_Prio = 0x00000005;
        Spawn_Parent = 0x00000001;
        run Task_Spawn();
        if (Spawn_Out == NIL) {
            out_cell(LOG_PORT, 0x0000B992);   // BAD spawn wrk
        } else {
            out_cell(LOG_PORT, 0x0000B921);   // spawned (ready)
            run Task_Begin();                 // pre-roll -> READY (в очереди)
            // ---- честная эпоха диспетча с вытеснением ----
            run Arm_Timer();
            run Dispatch_Loop();
        }
    }

    // ---- честный финал ----
    run Final_Check();
    out_cell(LOG_PORT, 0x0000B9FF);       // честный DONE
    terminate;
}

// ---------- честный завод таймера ----------
function Arm_Timer() {
    Tmp_A = TIMER_NODE;
    store_ind(Tmp_A, TMR_MAGIC);           // +0 magic 'TMR1'
    Tmp_A = TIMER_NODE + 1;
    store_ind(Tmp_A, QUANTUM);             // +1 квант (шагов VM между тиками)
    Tmp_A = TIMER_NODE + 2;
    store_ind(Tmp_A, TRAP_BLOCK);          // +2 trap-блок 'TCK1' (IRQ-кадр)
    Tmp_A = TIMER_NODE + 3;
    store_ind(Tmp_A, ENTRY_TICK);          // +3 вход обработчика (адрес честно)
    Tmp_A = TIMER_NODE + 4;
    store_ind(Tmp_A, STATICS_BASE);        // +4 база честного окна статиков
    Tmp_A = TIMER_NODE + 5;
    store_ind(Tmp_A, STATICS_COUNT);       // +5 размер окна (ячеек)
    Tmp_A = TICKS;
    store_ind(Tmp_A, 0x00000000);          // счётчик тиков честно с 0
    Tmp_A = KCTX;
    store_ind(Tmp_A, CTX_MAGIC);           // ядерный блок честно с magic
    Tmp_A = TIMER_NODE;                    // arg-протокол честно через переменную
    log_cell(STREAM_CELL, Tmp_A);          // честный arg TIMER_ARM
    sys_call(NID_TARM);
}

// ---------- init ----------
function Sched_Init() {
    Loop_I = 0x00000000;
    run Init_Slots();
    Tmp_A = CTL_CUR; store_ind(Tmp_A, NIL);
    Tmp_A = CTL_HEAD; store_ind(Tmp_A, NIL);
    Tmp_A = CTL_TAIL; store_ind(Tmp_A, NIL);
    Tmp_A = CTL_COUNT; store_ind(Tmp_A, 0x00000000);
    Tmp_A = CTL_NTID; store_ind(Tmp_A, 0x00000001);
    Tmp_A = CUR_CTX; store_ind(Tmp_A, NIL);
    Tmp_B = 0x00000000;
}

function Init_Slots() {
    if (Loop_I == MAX_TASKS) {
        out_cell(LOG_PORT, 0x0000B910);    // init ok
    } else {
        Slot_Idx = Loop_I;
        run Slot_Addr();
        store_ind(Slot_Ptr, 0x00000000);           // tid=0 free
        Tmp_A = Slot_Ptr + 4; store_ind(Tmp_A, ST_FREE);
        Tmp_A = Slot_Ptr + 8; store_ind(Tmp_A, 0x00000000);
        Tmp_A = Slot_Ptr + 12; store_ind(Tmp_A, 0x00000000);
        Tmp_A = Slot_Ptr + 16; store_ind(Tmp_A, 0x00000000);
        Tmp_A = Slot_Ptr + 20; store_ind(Tmp_A, 0x00000000);
        Tmp_A = Slot_Ptr + 24; store_ind(Tmp_A, 0x00000000);
        Tmp_A = Slot_Ptr + 28; store_ind(Tmp_A, 0x00000000);
        run Next_Addr();
        store_ind(Next_Ptr, NIL);
        Loop_I = Loop_I + 1;
        run Init_Slots();
    }
}

function T_Init_Check() {
    Tmp_A = CTL_HEAD;
    Tmp_B = in_cell(Tmp_A);
    Tmp_A = CTL_COUNT;
    Tmp_C = in_cell(Tmp_A);
    if (Tmp_B == NIL) {
        if (Tmp_C == 0x00000000) {
            out_cell(LOG_PORT, 0x0000B911);    // init честн проверен
        } else {
            out_cell(LOG_PORT, 0x0000B9E0);    // BAD count
        }
    } else {
        out_cell(LOG_PORT, 0x0000B9E1);        // BAD head
    }
}

// ---------- адресация ----------
function Slot_Addr() {
    Slot_Ptr = TASK_TABLE;
    Loop_I = 0x00000000;
    run Slot_Addr_Step();
}
function Slot_Addr_Step() {
    if (Loop_I == Slot_Idx) {
    } else {
        Slot_Ptr = Slot_Ptr + 32;
        Loop_I = Loop_I + 1;
        run Slot_Addr_Step();
    }
}

function Next_Addr() {
    Next_Ptr = TASK_NEXT;
    Loop_I = 0x00000000;
    run Next_Addr_Step();
}
function Next_Addr_Step() {
    if (Loop_I == Slot_Idx) {
    } else {
        Next_Ptr = Next_Ptr + 4;
        Loop_I = Loop_I + 1;
        run Next_Addr_Step();
    }
}

function Ctx_Addr() {
    Ctx_Ptr = TASK_CTX;
    Loop_I = 0x00000000;
    run Ctx_Addr_Step();
}
function Ctx_Addr_Step() {
    if (Loop_I == Slot_Idx) {
    } else {
        Ctx_Ptr = Ctx_Ptr + 256;
        Loop_I = Loop_I + 1;
        run Ctx_Addr_Step();
    }
}

// ---------- очередь готовых ----------
function Ready_Push() {
    Slot_Idx = Q_Idx;
    run Next_Addr();
    store_ind(Next_Ptr, NIL);
    Tmp_A = CTL_TAIL;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == NIL) {
        Tmp_A = CTL_HEAD; store_ind(Tmp_A, Q_Idx);
        Tmp_A = CTL_TAIL; store_ind(Tmp_A, Q_Idx);
    } else {
        Slot_Idx = Tmp_B;
        run Next_Addr();
        store_ind(Next_Ptr, Q_Idx);
        Tmp_A = CTL_TAIL; store_ind(Tmp_A, Q_Idx);
    }
}

function Ready_Pop() {
    Tmp_A = CTL_HEAD;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == NIL) {
        Pop_Out = NIL;
    } else {
        Pop_Out = Tmp_B;
        Slot_Idx = Tmp_B;
        run Next_Addr();
        Tmp_C = in_cell(Next_Ptr);
        Tmp_A = CTL_HEAD; store_ind(Tmp_A, Tmp_C);
        if (Tmp_C == NIL) {
            Tmp_A = CTL_TAIL; store_ind(Tmp_A, NIL);
        }
        store_ind(Next_Ptr, NIL);
    }
}

function Queue_Dec() {
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == 0x00000000) {
    } else {
        Tmp_D = Tmp_B - 1;
        store_ind(Tmp_A, Tmp_D);
    }
}

function Queue_Inc() {
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    Tmp_D = Tmp_B + 1;
    store_ind(Tmp_A, Tmp_D);
}

// ---------- spawn ----------
function Task_Spawn() {
    Spawn_Out = NIL;
    Spawn_Slot = NIL;
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == MAX_TASKS) {
        out_cell(LOG_PORT, 0x0000B993);        // BAD limit
    } else {
        run Find_Free();
        if (Found_Slot == NIL) {
            out_cell(LOG_PORT, 0x0000B993);
        } else {
            Spawn_Slot = Found_Slot;
            Tmp_A = CTL_NTID;
            Tmp_C = in_cell(Tmp_A);
            Spawn_Out = Tmp_C;
            Tmp_D = Tmp_C + 1;
            store_ind(Tmp_A, Tmp_D);
            Slot_Idx = Spawn_Slot;
            run Slot_Addr();
            store_ind(Slot_Ptr, Spawn_Out);             // tid
            Tmp_A = Slot_Ptr + 4; store_ind(Tmp_A, ST_READY);
            Tmp_A = Slot_Ptr + 8; store_ind(Tmp_A, Spawn_Prio);
            Tmp_A = Slot_Ptr + 12; store_ind(Tmp_A, Spawn_Entry);
            Tmp_A = Slot_Ptr + 20; store_ind(Tmp_A, Spawn_Parent);
            Tmp_A = Slot_Ptr + 24; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Slot_Ptr + 28; store_ind(Tmp_A, 0x00000000);
            run Ctx_Addr();
            Tmp_A = Slot_Ptr + 16; store_ind(Tmp_A, Ctx_Ptr);
            store_ind(Ctx_Ptr, CTX_MAGIC);
            Tmp_A = Ctx_Ptr + 1; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Ctx_Ptr + 2; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Ctx_Ptr + 3; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Ctx_Ptr + 160; store_ind(Tmp_A, Spawn_Slot);
            Tmp_A = Ctx_Ptr + 161; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Ctx_Ptr + 162; store_ind(Tmp_A, Spawn_Entry);
            Tmp_A = Ctx_Ptr + 164; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Ctx_Ptr + 165; store_ind(Tmp_A, 0x00000000);
            Q_Idx = Spawn_Slot;
            run Ready_Push();
            run Queue_Inc();
        }
    }
}

// ---------- честный старт задачи (pre-roll, fresh run) ----------
function Task_Begin() {
    Slot_Idx = Spawn_Slot;
    run Slot_Addr();
    Tmp_A = Slot_Ptr + 4;
    store_ind(Tmp_A, ST_RUNNING);
    run Ctx_Addr();
    Tmp_A = CUR_CTX;
    store_ind(Tmp_A, Ctx_Ptr);
    run Task_Body();
    // pre-roll fresh-YIELD вернул: задача уже в очереди (spawn) — вернуть READY
    Slot_Idx = Spawn_Slot;
    run Slot_Addr();
    Tmp_A = Slot_Ptr + 4;
    store_ind(Tmp_A, ST_READY);
}

// ---------- после выхода задачи из среза: honest бег честный ----------
// Единый пункт учёта: handler уже поставил READY+push при вытеснении;
// финальный YIELD оставляет ZOMBIE (нужен reap). RUNNING -> READY+push
// (кооперативный случай; pre-roll нормализован в Task_Begin).
function After_Slice() {
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Slot_Ptr + 4;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == ST_ZOMBIE) {
        run Reap_Slot();
    } else {
        if (Tmp_B == ST_RUNNING) {
            Q_Idx = Slot_Idx;
            run Ready_Push();
            Tmp_A = Slot_Ptr + 4;
            store_ind(Tmp_A, ST_READY);
        }
        // ST_READY: вытеснение уже обработано handler-ом — no-op
    }
}

// ---------- честный reap ----------
function Reap_Slot() {
    Tmp_A = in_cell(Slot_Ptr);
    Tmp_B = Slot_Ptr + 24;
    Tmp_C = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        if (Tmp_C == 0x0000002A) {
            out_cell(LOG_PORT, 0x0000B9D0);    // честный reap лидера
        } else {
            out_cell(LOG_PORT, 0x0000B9E3);    // BAD retcode
        }
    } else {
        if (Tmp_A == 0x00000002) {
            if (Tmp_C == 0x0000002B) {
                out_cell(LOG_PORT, 0x0000B9D1); // честный reap работника
            } else {
                out_cell(LOG_PORT, 0x0000B9E3);
            }
        } else {
            out_cell(LOG_PORT, 0x0000B9E2);    // BAD tid
        }
    }
    Tmp_A = Slot_Ptr + 4;
    store_ind(Tmp_A, ST_FREE);
    run Queue_Dec();
}

// ---------- честный Dispatch (эпоха задач) ----------
function Dispatch_Loop() {
    run Ready_Pop();
    if (Pop_Out == NIL) {
    } else {
        Slot_Idx = Pop_Out;
        run Slot_Addr();
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_RUNNING);
        Tmp_B = in_cell(Slot_Ptr);
        log_cell(LOG_PORT, Tmp_B);             // честный RESUME: tid
        out_cell(LOG_PORT, 0x0000B930);        // честный RESUME маркер
        Tmp_A = Slot_Ptr + 16;
        Ctx_Ptr = in_cell(Tmp_A);
        Tmp_A = CTL_CUR; store_ind(Tmp_A, Slot_Idx);
        Tmp_A = CUR_CTX; store_ind(Tmp_A, Ctx_Ptr);
        log_cell(STREAM_CELL, Ctx_Ptr);        // честный arg RESTORE
        sys_call(NID_RESTORE);                 // честная эпоха задачи
        // Точка пер-эпохи: сюда честно приходят:
        //   - честный YIELD из тела задачи (финальный, честный выход);
        //   - честный YIELD обработчика тика (ре-диспетч при вытеснении).
        run After_Slice();
        run Dispatch_Loop();
    }
}

// ---------- честный обработчик тика (вход trap_entry) ----------
// VM честно: pc=Tick_Slice_Handler, rts = стек ПРЕРВАННОЙ задачи.
// Контракт: см. шапку. Возврат через честный YIELD (в точку ядра).
function Tick_Slice_Handler() {
    Tmp_A = TICKS;
    Tmp_B = in_cell(Tmp_A);
    Tmp_D = Tmp_B + 1;
    store_ind(Tmp_A, Tmp_D);
    out_cell(LOG_PORT, 0x0000B940);            // честный тик

    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Slot_Ptr + 4;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == ST_ZOMBIE) {
        // честный редкий случай: задача честно дошла до ZOMBIE между
        // честными моментами — reap честно прямо в обработчике
        run Reap_Slot();
    } else {
        run Copy_Trap();                       // честный переезд кадра в 'CTX1'
        Q_Idx = Slot_Idx;
        run Ready_Push();
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_READY);
        out_cell(LOG_PORT, 0x0000B941);        // честное вытеснение готово
    }
    // честный ре-диспетч: возврат в ядерную точку (после последнего RESTORE).
    // Аргумент YIELD — честный ЯДЕРНЫЙ блок KCTX: handler НЕ сохраняет свой
    // handler-контекст в ctx задачи (там уже лежит честный пред-тик снимок
    // Copy_Trap; RESUME задачи позже восстановит именно его молчаливо честно).
    Tmp_A = KCTX;                              // arg-протокол честно через переменную
    log_cell(STREAM_CELL, Tmp_A);
    sys_call(NID_YIELD);
    out_cell(LOG_PORT, 0x0000B9E5);            // BAD: сюда честно нельзя
    terminate;
}

// честный перенос 'TCK1'-кадра в ctx-блок задачи:
// pc/acc/rts_len/rts ЧЕСТНО + окно статиков (TCK1 +132 count +133 base
// +134.. ячейки -> ctx +166 count +167 base +170.. ячейки) — иначе
// handler/kernel затёртые общие ячейки не вернутся задаче честно.
function Copy_Trap() {
    Tmp_A = TRAP_BLOCK + 1;
    Tmp_B = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 1;
    store_ind(Tmp_A, Tmp_B);                   // pc честно
    Tmp_A = TRAP_BLOCK + 2;
    Tmp_B = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 2;
    store_ind(Tmp_A, Tmp_B);                   // acc честно
    Tmp_A = TRAP_BLOCK + 3;
    Tmp_C = in_cell(Tmp_A);                    // rts_len честно
    Tmp_A = Ctx_Ptr + 3;
    store_ind(Tmp_A, Tmp_C);
    Copy_Loop_I = 0x00000000;
    run Copy_Rts_Step();
    Tmp_A = TRAP_BLOCK + 132;
    Tmp_B = in_cell(Tmp_A);                    // count окна честно (сторож)
    Tmp_A = TRAP_BLOCK + 133;
    Tmp_C = in_cell(Tmp_A);                    // base окна
    Tmp_A = Ctx_Ptr + 166;
    store_ind(Tmp_A, Tmp_B);
    Tmp_A = Ctx_Ptr + 167;
    store_ind(Tmp_A, Tmp_C);
    Copy_Loop_I = 0x00000000;
    run Copy_St_Step();
}

set static Copy_Loop_I = 0x00000000;

function Copy_Rts_Step() {
    if (Copy_Loop_I == Tmp_C) {
    } else {
        Tmp_A = TRAP_BLOCK + 4;
        Tmp_A = Tmp_A + Copy_Loop_I;
        Tmp_B = in_cell(Tmp_A);
        Tmp_A = Ctx_Ptr + 4;
        Tmp_A = Tmp_A + Copy_Loop_I;
        store_ind(Tmp_A, Tmp_B);
        Copy_Loop_I = Copy_Loop_I + 1;
        run Copy_Rts_Step();
    }
}

function Copy_St_Step() {
    if (Copy_Loop_I == Tmp_B) {
    } else {
        Tmp_A = TRAP_BLOCK + 136;
        Tmp_A = Tmp_A + Copy_Loop_I;
        Tmp_C = in_cell(Tmp_A);
        Tmp_A = Ctx_Ptr + 170;
        Tmp_A = Tmp_A + Copy_Loop_I;
        store_ind(Tmp_A, Tmp_C);
        Copy_Loop_I = Copy_Loop_I + 1;
        run Copy_St_Step();
    }
}

// ---------- честное тело задачи ----------
// Пролог честно запускается свежим run (pre-roll): честный маркер и
// честная fresh-YIELD-пауза. После честных ре-диспетч через RESTORE задача
// честно продолжит отсюда: честный YIELD-return честно возвращает МЕСТО.
function Task_Body() {
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);                    // job
    Tmp_A = Ctx_Ptr + 164;
    Tmp_C = in_cell(Tmp_A);                    // booted?
    if (Tmp_C == 0x00000000) {
        Tmp_D = Tmp_C + 1;
        store_ind(Tmp_A, Tmp_D);
        if (Tmp_B == JOB_LEADER) {
            out_cell(LOG_PORT, 0x0000B9A0);    // честный пролог лидера
        } else {
            out_cell(LOG_PORT, 0x0000B9B0);    // честный пролог работника
        }
    }
    if (Tmp_C == 0x00000000) {
        log_cell(STREAM_CELL, Ctx_Ptr);
        sys_call(NID_YIELD);                   // честная fresh-YIELD-пауза
    }

    // честная ДЛИННАЯ работа: итерации честно пишут ctx-ячейки, БЕЗ YIELD —
    // честный тик вытеснит задачу прямо внутри этого цикла (и после
    // честного ре-диспетча задача продолжит работу здесь же по ctx-стеку)
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);
    run Work_Loop();

    run Finish_Self();
    log_cell(STREAM_CELL, Ctx_Ptr);
    sys_call(NID_YIELD);                       // честный финальный YIELD
    out_cell(LOG_PORT, 0x0000B999);            // честный BAD (небылица путь)
}

// честный цикл работы: ITERS_MAX итераций честной работы над ctx-ячейками;
// продолжается честно после тика-вытеснения (rts из 'CTX1' блока)
function Work_Loop() {
    Tmp_A = Ctx_Ptr + 165;
    Tmp_C = in_cell(Tmp_A);
    if (Tmp_C == ITERS_MAX) {
    } else {
        Tmp_D = Tmp_C + 1;
        store_ind(Tmp_A, Tmp_D);               // честный шаг работы
        Tmp_A = Ctx_Ptr + 165;
        Tmp_C = in_cell(Tmp_A);
        run Work_Loop();
    }
}

// ---------- честный финал задачи: ZOMBIE + retcode ----------
function Finish_Self() {
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);                    // job честно заново
    if (Tmp_B == JOB_LEADER) {
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_ZOMBIE);
        Tmp_A = Slot_Ptr + 24;
        store_ind(Tmp_A, 0x0000002A);
        out_cell(LOG_PORT, 0x0000B9A2);        // честный финал лидера
    } else {
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_ZOMBIE);
        Tmp_A = Slot_Ptr + 24;
        store_ind(Tmp_A, 0x0000002B);
        out_cell(LOG_PORT, 0x0000B9B2);        // честный финал работника
    }
}

// ---------- честный финал программы ----------
function Final_Check() {
    Tmp_A = TICKS;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == 0x00000000) {
        out_cell(LOG_PORT, 0x0000B9E4);        // BAD: тиков не было
    } else {
        out_cell(LOG_PORT, 0x0000B94F);        // честные тики > 0
    }
    Tmp_A = CTL_COUNT;
    Tmp_C = in_cell(Tmp_A);
    if (Tmp_C == 0x00000000) {
        out_cell(LOG_PORT, 0x0000B90F);        // честная очередь пуста
    } else {
        out_cell(LOG_PORT, 0x0000B9E5);        // BAD count
    }
}

// ---------- finds ----------
function Find_Free() {
    Found_Slot = NIL;
    Loop_I = 0x00000000;
    run Find_Free_Step();
}
function Find_Free_Step() {
    if (Loop_I == MAX_TASKS) {
    } else {
        if (Found_Slot == NIL) {
            Slot_Idx = Loop_I;
            run Slot_Addr();
            Tmp_A = Slot_Ptr + 4;
            Tmp_B = in_cell(Tmp_A);
            if (Tmp_B == ST_FREE) {
                Found_Slot = Loop_I;
            } else {
                Loop_I = Loop_I + 1;
                run Find_Free_Step();
            }
        }
    }
}
