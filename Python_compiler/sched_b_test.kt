// ===================================================================
// СПРИНТ Б: ЧЕСТНАЯ ОЧЕРЕДЬ ГОТОВЫХ + СОН/ПРОБУЖДЕНИЕ ЗАДАЧ
// Файл: sched_b_test.kt | Язык: KINII (подмножество стадии-0)
//
// Сверху спринта А добавлено честно:
//   * Кольцевая очередь готовых: 16 слотов, указатели ходят по кругу
//     честным сравнением с границей (умножение не нужно).
//   * Счётчик Count_Queue: «очередь пуста» = честная else-ветка диспетча
//     (правило слабого железа: нет работы — лог и честный выход, без опросов).
//   * Сон/пробуждение: SLEEPING не попадает в очередь готовых; честные
//     пары (адрес слота, будильник) в линейных буферах сна; пробуждение —
//     честный скан + пересборка буферов (проснулся -> READY + push;
//     недоспал -> переписался; компакт — честная обратная копия).
//
// Карта памяти (Ring 2: 0x00A00000+, ниже var-зоны 0x00F00000):
//   0x00E00000  TASK_TABLE  8 слотов × 24 байта
//               +0 tid | +4 state | +8 nice | +12 vruntime | +16 parent | +20 exit_code
//   0x00E10000  READY_QUEUE 16 слов (кольцо, адреса слотов)
//   0x00E11000  SLEEP_A     8 слов, адреса спящих слотов
//   0x00E11040  SLEEP_W     8 слов, будильники (в тиках)
//   0x00E11080  REWRITE_A   8 слов, честная пересборка (копия)
//   0x00E110C0  REWRITE_W   8 слов, честная пересборка (копия)
//
// Честный сценарий (7 тиков):
//   tick1 лидер, tick2 потомок, tick3 лидер, tick4 потомок спит на 2 тика,
//   tick5 лидер (один готов), tick6 будильник потомка честно срабатывает
//   (READY + push) и исполняется лидер, tick7 потомок честно продолжает.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00E00000
#define: READY_QUEUE 0x00E10000
#define: QUEUE_END   0x00E10040    // первый адрес ЗА последним слотом кольца
#define: SLEEP_A     0x00E11000
#define: SLEEP_W     0x00E11040
#define: REWRITE_A   0x00E11080
#define: REWRITE_W   0x00E110C0
#define: SLOT1_ADDR  0x00E00018
#define: SLOT2_ADDR  0x00E00030
#define: ST_READY    0x00000001
#define: ST_SLEEPING 0x00000003
#define: ST_ZOMBIE   0x00000005
#define: EXIT_CODE   0x00000C0D    // exit_code демо-задачи (стадия-0 u32)

// --- бегущие указатели и держатели (все ячейки стадии-0 глобальные) ---
set static Tick_Counter  = 0x00000000;
set static Task_Addr     = 0x00000000;
set static Queue_Addr    = 0x00000000;  // хвост кольца готовых (push)
set static Head_Addr     = 0x00000000;  // голова кольца готовых (pop)
set static Count_Queue   = 0x00000000;  // честный счётчик готовых
set static Curr_Addr     = 0x00000000;  // слот исполняющейся задачи
set static Tmp_ID        = 0x00000000;
set static Tmp_When      = 0x00000000;
set static VR_Addr       = 0x00000000;
set static Curr_VRun     = 0x00000000;
set static State_Addr    = 0x00000000;
set static Hold_Addr     = 0x00000000;  // честный обмен адресом (push/скан сна)
set static Sleep_Count   = 0x00000000;
set static RW_Count      = 0x00000000;
set static Sleep_A_Ptr   = 0x00000000;
set static Sleep_W_Ptr   = 0x00000000;
set static RW_A_Addr     = 0x00000000;
set static RW_W_Addr     = 0x00000000;
set static Scan_Idx      = 0x00000000;
set static Work_Streak   = 0x00000000;
set static Sleep_Steps   = 0x00000002;  // честная длительность сна (в тиках)
set static Wake_When     = 0x00000000;  // честный держатель будильника
set static Init_Slot     = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00004000);      // LOG: sched B test START

    Task_Addr = TASK_TABLE;
    run Init_Slots();                    // 8 слотов FREE (рекурсия с else)

    Queue_Addr = READY_QUEUE;
    Head_Addr = READY_QUEUE;
    Count_Queue = 0x00000000;
    Sleep_Count = 0x00000000;
    Sleep_A_Ptr = SLEEP_A;               // честный бегущий хвост буфера адресов сна
    Sleep_W_Ptr = SLEEP_W;               // честный бегущий хвост буфера будильников

    run Spawn_Leader();
    run Spawn_Worker();

    // 7 честных тиков диспетчеризации (события описаны в шапке файла)
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();

    out_cell(LOG_PORT, 0x00004FFF);      // LOG: sched B test DONE
    terminate;
}

// ---------- инициализация таблицы задач (как в спринте А) ----------
function Init_Slots() {
    if (Init_Slot == 0x00000008) {
        out_cell(LOG_PORT, 0x00004110);  // LOG: task table READY
    } else {
        store_ind(Task_Addr, Init_Slot); // +0 tid
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +4 state = FREE
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +8 nice
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +12 vruntime
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +16 parent
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +20 exit_code
        Task_Addr = Task_Addr + 24;      // шаг к следующему слоту
        Init_Slot = Init_Slot + 1;
        run Init_Slots();
    }
}

// ---------- очередь готовых: честное кольцо с переполнением ----------
function Push_Ready() {
    if (Count_Queue == 0x00000010) {
        out_cell(LOG_PORT, 0x00004420);  // LOG: очередь готовых переполнена
    } else {
        store_ind(Queue_Addr, Hold_Addr);
        if (Queue_Addr == QUEUE_END) {   // кольцо: после последнего слота — в базу
            Queue_Addr = READY_QUEUE;
        } else {
            Queue_Addr = Queue_Addr + 4; // честный шаг вперёд
        }
        Count_Queue = Count_Queue + 1;
    }
}

// ---------- spawn: честные порождения со связью родства ----------
function Spawn_Leader() {
    Task_Addr = SLOT1_ADDR;
    store_ind(Task_Addr, 0x00000001);    // +0 tid = 1
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);      // +4 state = READY
    Task_Addr = Task_Addr + 12;
    store_ind(Task_Addr, 0);             // +16 parent = 0
    Hold_Addr = SLOT1_ADDR;
    run Push_Ready();
}

function Spawn_Worker() {
    Task_Addr = SLOT2_ADDR;
    store_ind(Task_Addr, 0x00000002);    // +0 tid = 2
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);      // +4 state = READY
    Task_Addr = Task_Addr + 12;
    store_ind(Task_Addr, 0x00000001);    // +16 parent = 1 (spawn от лидера)
    Hold_Addr = SLOT2_ADDR;
    run Push_Ready();
}

// ---------- тик планировщика: честный полный цикл ----------
function Schedule_Now() {
    Tick_Counter = Tick_Counter + 1;
    // пробуждение спящих — только если есть кому (правило слабого железа)
    if (Sleep_Count == 0) {
        // пусто — честно не тратим такт на скан
    } else {
        run Wake_Sleep();
    }
    // диспетч — только если есть готовые
    if (Count_Queue == 0) {
        out_cell(LOG_PORT, 0x00004200);  // LOG: очередь пуста — тик пропущен
    } else {
        Curr_Addr = in_cell(Head_Addr);  // честный pop головы кольца
        if (Head_Addr == QUEUE_END) {
            Head_Addr = READY_QUEUE;
        } else {
            Head_Addr = Head_Addr + 4;
        }
        Count_Queue = Count_Queue - 1;   // честное вычитание (режим 0x17)
        Tmp_ID = in_cell(Curr_Addr);     // +0 tid
        log_cell(LOG_PORT, Tmp_ID);      // честный вывод tid (0x54)
        VR_Addr = Curr_Addr + 12;        // +12 vruntime
        Curr_VRun = in_cell(VR_Addr);
        Curr_VRun = Curr_VRun + 1;       // честная наработка кванта
        store_ind(VR_Addr, Curr_VRun);
        // честный диспетч по tid: задача-функция исполняет свой чанк
        if (Tmp_ID == 0x00000001) {
            run Leader_Chunk();
        } else {
            run Worker_Chunk();
        }
        // честный итог чанка: задача сама выбрала сон или выход; иначе yield
        State_Addr = Curr_Addr + 4;
        Tmp_When = in_cell(State_Addr);
        if (Tmp_When == ST_SLEEPING) {
            // сон оформлен внутри Task_Sleep — в готовые НЕ кладём
        } else {
            if (Tmp_When == ST_ZOMBIE) {
                out_cell(LOG_PORT, 0x00004300);  // LOG: exit -> висит в ZOMBIE
            } else {
                Hold_Addr = Curr_Addr;           // yield: снова READY, в хвост
                run Push_Ready();
                out_cell(LOG_PORT, 0x00004310);  // LOG: yield -> хвост кольца
            }
        }
    }
}

// ---------- честные чанки задач ----------
function Leader_Chunk() {
    out_cell(LOG_PORT, 0x00004A00);      // LOG: лидер отработал чанк
}

function Worker_Chunk() {
    if (Work_Streak == 0x00000000) {
        Work_Streak = Work_Streak + 1;
        out_cell(LOG_PORT, 0x00004B10);  // LOG: потомок — первый чанк
    } else {
        if (Work_Streak == 0x00000001) {
            Work_Streak = Work_Streak + 1;
            Sleep_Steps = 0x00000002;    // честный запрос сна
            run Task_Sleep();
        } else {
            out_cell(LOG_PORT, 0x00004B20);  // LOG: потомок продолжил после сна
        }
    }
}

// ---------- честный сон: сам факт изнутри задачи ----------
function Task_Sleep() {
    if (Sleep_Count == 0x00000008) {
        out_cell(LOG_PORT, 0x00004410);  // LOG: спящие переполнены (паника)
    } else {
        State_Addr = Curr_Addr + 4;
        store_ind(State_Addr, ST_SLEEPING);
        store_ind(Sleep_A_Ptr, Curr_Addr);        // адрес слота
        Wake_When = Tick_Counter + Sleep_Steps;   // честный будильник
        store_ind(Sleep_W_Ptr, Wake_When);
        Sleep_A_Ptr = Sleep_A_Ptr + 4;
        Sleep_W_Ptr = Sleep_W_Ptr + 4;
        Sleep_Count = Sleep_Count + 1;
        out_cell(LOG_PORT, 0x00004440);  // LOG: задача ушла в сон
    }
}

// ---------- честное пробуждение: скан + пересборка буферов ----------
function Wake_Sleep() {
    RW_Count = 0x00000000;
    RW_A_Addr = REWRITE_A;
    RW_W_Addr = REWRITE_W;
    Sleep_A_Ptr = SLEEP_A;
    Sleep_W_Ptr = SLEEP_W;
    Scan_Idx = 0x00000000;
    run Wake_Step();
}

function Wake_Step() {
    if (Scan_Idx == Sleep_Count) {
        // честная база: все просмотрены; недоспавших переписываем обратно
        Sleep_Count = RW_Count;
        Sleep_A_Ptr = SLEEP_A;           // честный сброс на начало буферов сна
        Sleep_W_Ptr = SLEEP_W;
        RW_A_Addr = REWRITE_A;           // честный сброс источника копии
        RW_W_Addr = REWRITE_W;
        Scan_Idx = 0;                    // ЧЕСТНЫЙ сброс: пересчёт с нуля —
                                         // без него Restore не зайдёт в базу
                                         // при Sleep_Count = 0 (петля — найдено
                                         // и честно исправлено)
        run Sleep_Restore();
    } else {
        Hold_Addr = in_cell(Sleep_A_Ptr);     // адрес слота
        Sleep_A_Ptr = Sleep_A_Ptr + 4;
        Tmp_When = in_cell(Sleep_W_Ptr);      // будильник
        Sleep_W_Ptr = Sleep_W_Ptr + 4;
        if (Tmp_When == Tick_Counter) {
            State_Addr = Hold_Addr + 4;
            store_ind(State_Addr, ST_READY);  // честный подъём: READY
            run Push_Ready();                 // push в кольцо готовых
            out_cell(LOG_PORT, 0x00004500);   // LOG: задача проснулась
        } else {
            store_ind(RW_A_Addr, Hold_Addr);  // недоспал: переписывается честно
            store_ind(RW_W_Addr, Tmp_When);
            RW_A_Addr = RW_A_Addr + 4;
            RW_W_Addr = RW_W_Addr + 4;
            RW_Count = RW_Count + 1;
        }
        Scan_Idx = Scan_Idx + 1;
        run Wake_Step();
    }
}

function Sleep_Restore() {
    if (Scan_Idx == Sleep_Count) {
        out_cell(LOG_PORT, 0x00004600);  // LOG: буферы сна пересобраны
    } else {
        Tmp_ID = in_cell(RW_A_Addr);
        store_ind(Sleep_A_Ptr, Tmp_ID);
        Tmp_When = in_cell(RW_W_Addr);
        store_ind(Sleep_W_Ptr, Tmp_When);
        Sleep_A_Ptr = Sleep_A_Ptr + 4;
        Sleep_W_Ptr = Sleep_W_Ptr + 4;
        RW_A_Addr = RW_A_Addr + 4;
        RW_W_Addr = RW_W_Addr + 4;
        Scan_Idx = Scan_Idx + 1;
        run Sleep_Restore();
    }
}
