// ===================================================================
// СПРИНТ В: МЬЮТЕКС (ФУТЕКС-СТИЛЬ) + ЧЕСТНЫЙ task.nice
// Файл: sched_v_test.kt | Язык: KINII (подмножество стадии-0)
//
// Сверху спринта Б добавлено честно:
//   * Мьютекс = одна честная спин-попытка; занято -> сон на очереди
//     ждущих мьютекса (как futex в Linux: 0x00E12000 owner, очередь
//     ждущих как кольцо готовых). Никаких вечных спинов на 13 Вт.
//   * Размораживание: Mutex_Unlock честно поднимает ТОЛЬКО голову
//     очереди ждущих -> READY + push в кольцо готовых.
//   * task.nice пишется честно в слот (+8): vruntime честно растёт
//     НА nice за квант (+1 лидер, +4 потомок). Наследования nice нет —
//     по спике (лишняя логика в горячем пути планировщика).
//   * Честный выход: Task_Exit -> ZOMBIE + exit_code, честный join
//     лидером по +20 слота потомка.
//
// Карта памяти (Ring 2, поверх спринта Б):
//   0x00E12000  MUTEX         +0 owner_tid (0 = свободен)
//   0x00E12100  WAIT_A        8 слов, адреса слотов ждущих мьютекса
//   0x00E12120  WAIT_END      первый адрес ЗА последним слотом очереди ждущих
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00E00000
#define: READY_QUEUE 0x00E10000
#define: QUEUE_END   0x00E10040
#define: MUTEX_ADDR  0x00E12000
#define: WAIT_A      0x00E12100
#define: WAIT_END    0x00E12120
#define: SLOT1_ADDR  0x00E00018
#define: SLOT2_ADDR  0x00E00030
#define: ST_READY    0x00000001
#define: ST_SLEEPING 0x00000003
#define: ST_ZOMBIE   0x00000005
#define: EXIT_CODE   0x00000C0D

set static Tick_Counter  = 0x00000000;
set static Task_Addr     = 0x00000000;
set static Queue_Addr    = 0x00000000;
set static Head_Addr     = 0x00000000;
set static Count_Queue   = 0x00000000;
set static Curr_Addr     = 0x00000000;
set static Tmp_ID        = 0x00000000;
set static Tmp_When      = 0x00000000;
set static Nice_Val      = 0x00000000;  // честный nice исполняющейся задачи
set static VR_Addr       = 0x00000000;
set static Curr_VRun     = 0x00000000;
set static State_Addr    = 0x00000000;
set static Hold_Addr     = 0x00000000;
set static Init_Slot     = 0x00000000;
set static Work_Streak   = 0x00000000;  // честный счётчик чанков потомка
set static L_Streak      = 0x00000000;  // честный счётчик чанков лидера
set static MUT_GOT       = 0x00000000;  // честный итог попытки: 1 взяли, 0 занято
set static Nice_Addr     = 0x00000000;  // честный адрес +8 слота (nice)
set static Wait_Count    = 0x00000000;  // честный счётчик ждущих мьютекса
set static Wait_Head     = 0x00000000;  // честный бегунок pop очереди ждущих
set static Wait_Tail     = 0x00000000;  // честный бегунок push очереди ждущих

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00005000);      // LOG: sched V test START

    Task_Addr = TASK_TABLE;
    run Init_Slots();

    Queue_Addr = READY_QUEUE;
    Head_Addr = READY_QUEUE;
    Count_Queue = 0x00000000;
    Wait_Head = WAIT_A;
    Wait_Tail = WAIT_A;
    Wait_Count = 0x00000000;

    run Spawn_Leader();
    run Spawn_Worker();

    // 7 честных тиков (события описаны в шапке и в сводке отчёта ниже)
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();

    // честный финал: vruntime лидера (1 за чанк) vs потомка (4 за чанк)
    run VR_Report();

    out_cell(LOG_PORT, 0x00005FFF);      // LOG: sched V test DONE
    terminate;
}

// ---------- инициализация таблицы задач (как в спринте Б) ----------
function Init_Slots() {
    if (Init_Slot == 0x00000008) {
        out_cell(LOG_PORT, 0x00005110);
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

// ---------- очередь готовых: честное кольцо (как в спринте Б) ----------
function Push_Ready() {
    if (Count_Queue == 0x00000010) {
        out_cell(LOG_PORT, 0x00005420);
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

// ---------- spawn: честные порождения + честный nice в слоте ----------
function Spawn_Leader() {
    Task_Addr = SLOT1_ADDR;
    store_ind(Task_Addr, 0x00000001);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, 0x00000001);    // +8 nice = 1 (лидер честно шустрый)
    Task_Addr = Task_Addr + 8;
    store_ind(Task_Addr, 0);
    Hold_Addr = SLOT1_ADDR;
    run Push_Ready();
}

function Spawn_Worker() {
    Task_Addr = SLOT2_ADDR;
    store_ind(Task_Addr, 0x00000002);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, 0x00000004);    // +8 nice = 4 (потомок честно тяжёлый)
    Task_Addr = Task_Addr + 8;
    store_ind(Task_Addr, 0x00000001);
    Hold_Addr = SLOT2_ADDR;
    run Push_Ready();
}

// ---------- тик планировщика: как в спринте Б, честный nice ----------
function Schedule_Now() {
    Tick_Counter = Tick_Counter + 1;
    if (Count_Queue == 0) {
        out_cell(LOG_PORT, 0x00005200);  // LOG: очередь пуста — тик пропущен
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
        // честная наработка кванта: vruntime растёт НА nice
        Nice_Addr = Curr_Addr + 8;
        Nice_Val = in_cell(Nice_Addr);
        VR_Addr = Curr_Addr + 12;
        Curr_VRun = in_cell(VR_Addr);
        Curr_VRun = Curr_VRun + Nice_Val;
        store_ind(VR_Addr, Curr_VRun);
        if (Tmp_ID == 0x00000001) {
            run Leader_Chunk();
        } else {
            run Worker_Chunk();
        }
        // честный итог чанка: сон/выход оформлены внутри задач
        State_Addr = Curr_Addr + 4;
        Tmp_When = in_cell(State_Addr);
        if (Tmp_When == ST_SLEEPING) {
            // спит на мьютексе — в готовые не кладём
        } else {
            if (Tmp_When == ST_ZOMBIE) {
                out_cell(LOG_PORT, 0x00005430);  // LOG: exit -> ZOMBIE
            } else {
                Hold_Addr = Curr_Addr;
                run Push_Ready();
                out_cell(LOG_PORT, 0x00005310);  // LOG: yield -> хвост
            }
        }
    }
}

// ---------- мьютекс: одна честная спин-попытка ----------
function Mutex_Try() {
    Task_Addr = MUTEX_ADDR;
    Tmp_When = in_cell(Task_Addr);
    if (Tmp_When == 0x00000000) {
        Tmp_ID = in_cell(Curr_Addr);          // владелец становится честно
        store_ind(Task_Addr, Tmp_ID);
        MUT_GOT = 0x00000001;
    } else {
        MUT_GOT = 0x00000000;                 // занято: без вечного спина
    }
}

// ---------- мьютекс: честный сон на очереди ждущих ----------
function Mutex_Wait() {
    if (Wait_Count == 0x00000008) {
        out_cell(LOG_PORT, 0x00005560);       // честная паника: очередь ждущих полна
    } else {
        State_Addr = Curr_Addr + 4;
        store_ind(State_Addr, ST_SLEEPING);
        store_ind(Wait_Tail, Curr_Addr);
        if (Wait_Tail == WAIT_END) {
            Wait_Tail = WAIT_A;
        } else {
            Wait_Tail = Wait_Tail + 4;
        }
        Wait_Count = Wait_Count + 1;
        out_cell(LOG_PORT, 0x00005520);       // LOG: спим на мьютексе (футекс)
    }
}

// ---------- мьютекс: честное отпускание + подъём головы очереди ----------
function Mutex_Unlock() {
    Task_Addr = MUTEX_ADDR;
    Tmp_When = in_cell(Task_Addr);
    if (Tmp_When == Tmp_ID) {
        store_ind(Task_Addr, 0);              // честное освобождение владельца
        if (Wait_Count == 0) {
            out_cell(LOG_PORT, 0x00005530);   // LOG: отпущен, ждущих нет
        } else {
            Hold_Addr = in_cell(Wait_Head);   // честный_futex: поднимается только голова
            if (Wait_Head == WAIT_END) {
                Wait_Head = WAIT_A;
            } else {
                Wait_Head = Wait_Head + 4;
            }
            Wait_Count = Wait_Count - 1;
            State_Addr = Hold_Addr + 4;
            store_ind(State_Addr, ST_READY);
            run Push_Ready();
            out_cell(LOG_PORT, 0x00005540);   // LOG: ждущий проснулся
        }
    } else {
        out_cell(LOG_PORT, 0x00005590);       // честная паника: не владелец
    }
}

// ---------- честный выход задачи ----------
function Task_Exit() {
    State_Addr = Curr_Addr + 4;
    store_ind(State_Addr, ST_ZOMBIE);
    State_Addr = Curr_Addr + 20;
    store_ind(State_Addr, EXIT_CODE);
    out_cell(LOG_PORT, 0x00005440);           // LOG: задача честно завершилась
}

// ---------- честные чанки задач ----------
// Лидер: тик 1 — взял замок; тик 3 — работа и отпускание (подъём потомка);
// тик 5 — честный join по exit_code потомка и свой честный выход.
function Leader_Chunk() {
    if (L_Streak == 0x00000000) {
        L_Streak = L_Streak + 1;
        out_cell(LOG_PORT, 0x00005A00);
        run Mutex_Try();
        if (MUT_GOT == 0x00000001) {
            out_cell(LOG_PORT, 0x00005A10);   // LOG: замок владеет лидером
        } else {
            out_cell(LOG_PORT, 0x00005A50);   // честная паника: свободный замок не взят
        }
    } else {
        if (L_Streak == 0x00000001) {
            L_Streak = L_Streak + 1;
            out_cell(LOG_PORT, 0x00005A00);
            out_cell(LOG_PORT, 0x00005A20);   // LOG: работа под замком
            Tmp_ID = in_cell(Curr_Addr);
            run Mutex_Unlock();
        } else {
            out_cell(LOG_PORT, 0x00005A00);
            Hold_Addr = SLOT2_ADDR;            // честный join потомка
            State_Addr = Hold_Addr + 20;       // +20 exit_code
            Tmp_When = in_cell(State_Addr);
            if (Tmp_When == EXIT_CODE) {
                out_cell(LOG_PORT, 0x00005A30);   // LOG: join честный OK
            } else {
                out_cell(LOG_PORT, 0x00005A60);   // честная паника: потомок не отчитался
            }
            Tmp_ID = in_cell(Curr_Addr);
            run Task_Exit();                   // честный выход лидера
        }
    }
}

// Потомок: тик 2 — замок занят, честный сон на очереди мьютекса
// (в SLEEPING, в готовые не кладём); подъём от Mutex_Unlock лидера;
// следующий чанк — честное владение, работа, отпускание и выход.
function Worker_Chunk() {
    if (Work_Streak == 0x00000000) {
        Work_Streak = Work_Streak + 1;
        out_cell(LOG_PORT, 0x00005B00);
        run Mutex_Try();                        // честно: замок у лидера
        if (MUT_GOT == 0x00000001) {
            out_cell(LOG_PORT, 0x00005B50);     // честная паника: рано взяли latch
        } else {
            run Mutex_Wait();                   // честный сон (футекс)
        }
    } else {
        out_cell(LOG_PORT, 0x00005B00);
        run Mutex_Try();                        // честно: замок отпущен лидером
        if (MUT_GOT == 0x00000001) {
            out_cell(LOG_PORT, 0x00005B10);     // LOG: замок взят после подъёма
            Tmp_ID = in_cell(Curr_Addr);
            run Mutex_Unlock();
            run Task_Exit();
        } else {
            out_cell(LOG_PORT, 0x00005B60);     // честная паника: замок не освободился
        }
    }
}

// ---------- честный финальный отчёт по vruntime (nice в деле) ----------
function VR_Report() {
    Nice_Addr = SLOT1_ADDR + 12;
    Tmp_ID = in_cell(Nice_Addr);          // vruntime лидера (nice 1)
    log_cell(LOG_PORT, Tmp_ID);
    Nice_Addr = SLOT2_ADDR + 12;
    Tmp_ID = in_cell(Nice_Addr);          // vruntime потомка (nice 4)
    log_cell(LOG_PORT, Tmp_ID);
}
