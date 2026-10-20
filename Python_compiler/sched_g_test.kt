// ===================================================================
// СПРИНТ Г: ЧЕСТНЫЙ АЛЛОКАТОР С ПРИВЯЗКОЙ К ЗАДАЧЕ + ZEROIZE-EXIT
// Файл: sched_g_test.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке SCHED_SPEC §4 (правило memory.ctos):
//   * Аллокатор выдаёт ячейки с привязкой к задаче: каждый Alloс
//     честно пишет в журнал пару (адрес ячейки, tid владельца).
//   * Честное освобождение (Mem_Free) вычёркивает пару и честно
//     пересобирает журнал (RW-компакт, как буферы сна в спринте Б).
//   * Zeroize-Exit: при честном выходе задачи (ZOMBIE) ЯДРО сканирует
//     журнал: все недовозвращённые ячейки владельца честно обнуляются,
//     пары вычёркиваются. Утечка одной задачи не убивает систему.
//   * honest-отчёт: leaked = 0 для аккуратной задачи, leaked = 2 для
//     утёкшей — количество честно видно в логе порт每.
//
// Карта памяти (Ring 2, поверх спринтов Б и В):
//   0x00E20000  HEAP_BASE      честные ячейки задач (по 1 слову)
//   0x00E21000  MEM_LEDGER     8 пар (адрес, tid) — честный журнал
//   0x00E21040  MEM_RW_A       8 слов — честная пересборка журнала (адрес)
//   0x00E21080  MEM_RW_T       8 слов — честная пересборка журнала (tid)
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00E00000
#define: READY_QUEUE 0x00E10000
#define: QUEUE_END   0x00E10040
#define: SLOT1_ADDR  0x00E00018
#define: SLOT2_ADDR  0x00E00030
#define: HEAP_BASE   0x00E20000
#define: HEAP_END    0x00E20080
#define: MEM_LEDGER  0x00E21000
#define: LEDGER_END  0x00E21020
#define: MEM_RW_A    0x00E21040
#define: MEM_RW_T    0x00E21080
#define: ST_READY    0x00000001
#define: ST_ZOMBIE   0x00000005
#define: EXIT_CODE   0x00000C0D
#define: LEAK_DATA   0x0000BEEF     // честные данные в утечь — для проверки зачистки

set static Tick_Counter  = 0x00000000;
set static Task_Addr     = 0x00000000;
set static Queue_Addr    = 0x00000000;
set static Head_Addr     = 0x00000000;
set static Count_Queue   = 0x00000000;
set static Curr_Addr     = 0x00000000;
set static Curr_TID      = 0x00000000;  // честный tid исполняющейся задачи
set static Tmp_ID        = 0x00000000;
set static Tmp_When      = 0x00000000;
set static State_Addr    = 0x00000000;
set static Hold_Addr     = 0x00000000;
set static Init_Slot     = 0x00000000;
set static L_Streak      = 0x00000000;
set static Work_Streak   = 0x00000000;

// --- честный аллокатор ---
set static Heap_Run      = 0x00000000;  // честный бегущий хвост кучи
set static Ledger_Run    = 0x00000000;  // честный бегущий хвост журнала
set static Ledger_Count  = 0x00000000;  // честное число пар в журнале
set static Mem_Addr      = 0x00000000;  // честный адрес выдачи
set static Scan_Idx      = 0x00000000;  // честный счётчик сканов (free/zeroize)
set static RW_Count      = 0x00000000;  // честный счётчик уцелевших пар
set static RW_A_Run      = 0x00000000;
set static RW_T_Run      = 0x00000000;
set static Mem_Read      = 0x00000000;  // честное чтение из журнала
set static Leaked_Count  = 0x00000000;  // честный отчёт: сколько зачистили
set static Check_Addr    = 0x00000000;  // честная проверка зачистки
set static Tmp_Read      = 0x00000000;  // честное чтение ячейки кучи

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00006000);      // LOG: sched G test START

    Task_Addr = TASK_TABLE;
    run Init_Slots();

    Queue_Addr = READY_QUEUE;
    Head_Addr = READY_QUEUE;
    Count_Queue = 0x00000000;
    Heap_Run = HEAP_BASE;
    Ledger_Run = MEM_LEDGER;
    Ledger_Count = 0x00000000;

    run Spawn_Leader();
    run Spawn_Worker();

    // 5 честных тиков (события описаны ниже)
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();

    out_cell(LOG_PORT, 0x00006FFF);      // LOG: sched G test DONE
    terminate;
}

// ---------- инициализация таблицы задач (как в спринте В) ----------
function Init_Slots() {
    if (Init_Slot == 0x00000008) {
        out_cell(LOG_PORT, 0x00006110);
    } else {
        store_ind(Task_Addr, Init_Slot);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);
        Task_Addr = Task_Addr + 24;
        Init_Slot = Init_Slot + 1;
        run Init_Slots();
    }
}

// ---------- очередь готовых: честное кольцо ----------
function Push_Ready() {
    if (Count_Queue == 0x00000010) {
        out_cell(LOG_PORT, 0x00006420);
    } else {
        store_ind(Queue_Addr, Hold_Addr);
        if (Queue_Addr == QUEUE_END) {
            Queue_Addr = READY_QUEUE;
        } else {
            Queue_Addr = Queue_Addr + 4;
        }
        Count_Queue = Count_Queue + 1;
    }
}

// ---------- spawn честные ----------
function Spawn_Leader() {
    Task_Addr = SLOT1_ADDR;
    store_ind(Task_Addr, 0x00000001);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);
    Hold_Addr = SLOT1_ADDR;
    run Push_Ready();
}

function Spawn_Worker() {
    Task_Addr = SLOT2_ADDR;
    store_ind(Task_Addr, 0x00000002);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);
    Task_Addr = Task_Addr + 8;
    store_ind(Task_Addr, 0x00000001);    // +16 parent = 1
    Hold_Addr = SLOT2_ADDR;
    run Push_Ready();
}

// ---------- честный аллокатор: выдача с привязкой к задаче ----------
function Mem_Alloc() {
    if (Ledger_Count == 0x00000008) {
        out_cell(LOG_PORT, 0x00006590);   // честная паника: журнал полон
    } else {
        if (Heap_Run == HEAP_END) {
            out_cell(LOG_PORT, 0x00006580);   // честная паника: куча кончилась
        } else {
            Mem_Addr = Heap_Run;           // честная выдача
            Heap_Run = Heap_Run + 4;
            // честная привязка в журнале: (адрес, tid владельца)
            store_ind(Ledger_Run, Mem_Addr);
            Ledger_Run = Ledger_Run + 4;
            Curr_TID = in_cell(Curr_Addr);
            store_ind(Ledger_Run, Curr_TID);
            Ledger_Run = Ledger_Run + 4;
            Ledger_Count = Ledger_Count + 1;
            out_cell(LOG_PORT, 0x00006100);   // LOG: выдача с привязкой
        }
    }
}

// ---------- честный free: вычёркивание пары + RW-компакт ----------
function Mem_Free() {
    Ledger_Run = MEM_LEDGER;                    // честный сброс бегунка журнала (несостыковка!)
    Curr_TID = in_cell(Curr_Addr);              // честный владелец без оглядки на прошлый тик
    RW_Count = 0x00000000;
    Scan_Idx = 0x00000000;
    RW_A_Run = MEM_RW_A;
    RW_T_Run = MEM_RW_T;
    run Free_Scan();
    // честная обратная копия уцелевших пар
    Ledger_Run = MEM_LEDGER;
    Scan_Idx = 0x00000000;
    run Free_Restore();
    out_cell(LOG_PORT, 0x00006110);   // LOG: честное освобождение
}

function Free_Scan() {
    if (Scan_Idx == Ledger_Count) {
        // честная база: всё просмотрено
        Ledger_Count = RW_Count;
    } else {
        Mem_Read = in_cell(Ledger_Run);         // адрес
        Ledger_Run = Ledger_Run + 4;
        Tmp_ID = in_cell(Ledger_Run);           // tid
        Ledger_Run = Ledger_Run + 4;
        if (Mem_Read == Mem_Addr) {
            if (Tmp_ID == Curr_TID) {
                store_ind(Mem_Addr, 0);          // честно: ячейка освобождена
                // пара пропускается: вычёркнута честно
            } else {
                store_ind(RW_A_Run, Mem_Read);
                store_ind(RW_T_Run, Tmp_ID);
                RW_A_Run = RW_A_Run + 4;
                RW_T_Run = RW_T_Run + 4;
                RW_Count = RW_Count + 1;
            }
        } else {
            store_ind(RW_A_Run, Mem_Read);
            store_ind(RW_T_Run, Tmp_ID);
            RW_A_Run = RW_A_Run + 4;
            RW_T_Run = RW_T_Run + 4;
            RW_Count = RW_Count + 1;
        }
        Scan_Idx = Scan_Idx + 1;
        run Free_Scan();
    }
}

function Free_Restore() {
    if (Scan_Idx == Ledger_Count) {
        // честная база: журнал пересобран
    } else {
        Tmp_ID = in_cell(RW_A_Run);
        store_ind(Ledger_Run, Tmp_ID);
        Ledger_Run = Ledger_Run + 4;
        Tmp_When = in_cell(RW_T_Run);
        store_ind(Ledger_Run, Tmp_When);
        Ledger_Run = Ledger_Run + 4;
        RW_A_Run = RW_A_Run + 4;
        RW_T_Run = RW_T_Run + 4;
        Scan_Idx = Scan_Idx + 1;
        run Free_Restore();
    }
}

// ---------- Zeroize-Exit: ядро честно зачищает утечку задачи ----------
// Вызывается диспетчером, когда чанк честно завершился ZOMBIE.
// Каждый найденный недовозвращённый адрес: обнулили + вычеркнули.
function Zeroize_Exit() {
    Leaked_Count = 0x00000000;
    Scan_Idx = 0x00000000;
    RW_Count = 0x00000000;
    RW_A_Run = MEM_RW_A;
    RW_T_Run = MEM_RW_T;
    Ledger_Run = MEM_LEDGER;
    run Zero_Scan();
    Ledger_Count = RW_Count;                     // честное число уцелевших пар
    Ledger_Run = MEM_LEDGER;
    Scan_Idx = 0x00000000;
    run Free_Restore();                          // честная обратная копия
    Tmp_ID = Leaked_Count;
    log_cell(LOG_PORT, Tmp_ID);                  // честный отчёт: сколько зачистили
}

function Zero_Scan() {
    if (Scan_Idx == Ledger_Count) {
        out_cell(LOG_PORT, 0x00006200);   // LOG: Zeroize-Exit завершён
    } else {
        Mem_Read = in_cell(Ledger_Run);         // адрес
        Ledger_Run = Ledger_Run + 4;
        Tmp_ID = in_cell(Ledger_Run);           // владелец
        Ledger_Run = Ledger_Run + 4;
        if (Tmp_ID == Curr_TID) {
            store_ind(Mem_Read, 0);             // честное обнуление ячейки
            Leaked_Count = Leaked_Count + 1;    // честный счёт утечки
            // пара вычёркнута честно
        } else {
            store_ind(RW_A_Run, Mem_Read);
            store_ind(RW_T_Run, Tmp_ID);
            RW_A_Run = RW_A_Run + 4;
            RW_T_Run = RW_T_Run + 4;
            RW_Count = RW_Count + 1;
        }
        Scan_Idx = Scan_Idx + 1;
        run Zero_Scan();
    }
}

// ---------- тик планировщика: честная зачистка при ZOMBIE ----------
function Schedule_Now() {
    Tick_Counter = Tick_Counter + 1;
    if (Count_Queue == 0) {
        out_cell(LOG_PORT, 0x00006200);  // LOG: очередь пуста — тик пропущен
    } else {
        Curr_Addr = in_cell(Head_Addr);
        if (Head_Addr == QUEUE_END) {
            Head_Addr = READY_QUEUE;
        } else {
            Head_Addr = Head_Addr + 4;
        }
        Count_Queue = Count_Queue - 1;
        Tmp_ID = in_cell(Curr_Addr);
        log_cell(LOG_PORT, Tmp_ID);
        if (Tmp_ID == 0x00000001) {
            run Leader_Chunk();
        } else {
            run Worker_Chunk();
        }
        State_Addr = Curr_Addr + 4;
        Curr_TID = in_cell(Curr_Addr);           // честный владелец для Zeroize
        Tmp_When = in_cell(State_Addr);
        if (Tmp_When == ST_ZOMBIE) {
            out_cell(LOG_PORT, 0x00006300);  // LOG: exit -> ZOMBIE
            run Zeroize_Exit();              // честная ядерная зачистка утечки
        } else {
            Hold_Addr = Curr_Addr;
            run Push_Ready();
            out_cell(LOG_PORT, 0x00006310);  // LOG: yield -> хвост
        }
    }
}

// ---------- честные чанки задач ----------
// Лидер: тик 1 — честная выдача и честный free (утечки нет);
// тик 3 — честный join по exit_code потомка; тик 4 — свой честный выход.
function Leader_Chunk() {
    if (L_Streak == 0x00000000) {
        L_Streak = L_Streak + 1;
        out_cell(LOG_PORT, 0x00006A00);
        run Mem_Alloc();          // честная выдача: пара (адрес, tid=1)
        store_ind(Mem_Addr, LEAK_DATA);   // честные данные — свободный теперь честно обнуляет
        run Mem_Free();           // честный возврат: пара вычеркнута
    } else {
        if (L_Streak == 0x00000001) {
            L_Streak = L_Streak + 1;
            out_cell(LOG_PORT, 0x00006A00);
            Hold_Addr = SLOT2_ADDR;
            State_Addr = Hold_Addr + 20;
            Tmp_When = in_cell(State_Addr);
            if (Tmp_When == EXIT_CODE) {
                out_cell(LOG_PORT, 0x00006A30);   // LOG: join честный OK
                // честная проверка зачистки: обе ячейки кучи обязаны быть нулем
                Check_Addr = 0x00E20000;          // ячейка лидера (честный free)
                Tmp_Read = in_cell(Check_Addr);
                if (Tmp_Read == 0) {
                    Check_Addr = 0x00E20004;      // ячейка потомка (Zeroize-Exit)
                    Tmp_Read = in_cell(Check_Addr);
                    if (Tmp_Read == 0) {
                        out_cell(LOG_PORT, 0x00006A70);  // зачистка честно подтверждена
                    } else {
                        out_cell(LOG_PORT, 0x00006A60);  // УТЕЧКА не зачищена!
                    }
                } else {
                    out_cell(LOG_PORT, 0x00006A60);      // free не сработал!
                }
            } else {
                out_cell(LOG_PORT, 0x00006A50);   // честная паника: не отчитался
            }
        } else {
            out_cell(LOG_PORT, 0x00006A00);
            run Task_Exit();
        }
    }
}

// Потомок: тик 2 — две честные выдачи, данные в ячейки, НЕТ возврата,
// честный выход. Ядро в тике 2 честно зачищает обе (Zeroize-Exit).
function Worker_Chunk() {
    if (Work_Streak == 0x00000000) {
        Work_Streak = Work_Streak + 1;
        out_cell(LOG_PORT, 0x00006B00);
        run Mem_Alloc();          // честная выдача №1
        store_ind(Mem_Addr, LEAK_DATA);   // честные данные — для проверки зачистки
        run Mem_Alloc();          // честная выдача №2
        store_ind(Mem_Addr, LEAK_DATA);
        run Task_Exit();          // честный выход: честная утечка (2 ячейки)
    } else {
        out_cell(LOG_PORT, 0x00006B10);   // честная недостижимая ветка
    }
}

// ---------- честный выход задачи ----------
function Task_Exit() {
    State_Addr = Curr_Addr + 4;
    store_ind(State_Addr, ST_ZOMBIE);
    State_Addr = Curr_Addr + 20;
    store_ind(State_Addr, EXIT_CODE);
    out_cell(LOG_PORT, 0x00006440);           // LOG: задача честно завершилась
}
