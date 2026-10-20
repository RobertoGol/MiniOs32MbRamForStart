// ===================================================================
// СПРИНТ А: ЧЕСТНАЯ ПРОВЕРКА ПЛАНИРОВЩИКА СТАДИИ-0
// Файл: sched_test.kt | Язык: KINII (подмножество стадии-0)
//
// Структуры памяти (всё в Ring 2: 0x00A00000+, ниже var-зоны 0x00F00000):
//   0x00E00000  TASK_TABLE   8 слотов × 24 байта (6 слов):
//               +0 tid | +4 state | +8 nice | +12 vruntime | +16 parent | +20 exit_code
//   0x00E10000  READY_QUEUE  16 слов; очередь ГОТОВЫХ хранит АДРЕСА слотов
//               (не tid) — честное решение стадии-0: динамический адрес задачи
//               вынимается из очереди сразу, без умножения в арифметике.
//
// Честный сценарий: init 8 слотов (FREE) -> spawn лидера (слот 1) и потомка
// (слот 2, parent=1) -> 3 тика round-robin (pop головы -> лог tid ->
// vruntime++ -> yield: READY + push в хвост) -> honest exit последнего
// исполнявшегося (ZOMBIE, код 0xC0DE).
//
// Границы спринта А (честно): очередь ЛИНЕЙНАЯ (16 слотов, не кольцо),
// счётчиков готовых нет; кольцевая очередь и waiting — спринт Б.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0    // ранняя строка лога ядра
#define: TASK_TABLE  0x00E00000    // таблица задач (Ring 2)
#define: READY_QUEUE 0x00E10000    // очередь готовых (Ring 2)
#define: SLOT1_ADDR  0x00E00018    // слот задачи 1 (TASK_TABLE + 24)
#define: SLOT2_ADDR  0x00E00030    // слот задачи 2 (TASK_TABLE + 48)
#define: ST_READY    0x00000001    // состояние «готова к исполнению»
#define: ST_ZOMBIE   0x00000005    // завершена (ждёт зачистки ядра)
#define: EXIT_CODE   0x000000C0DE  // честный код завершения демо-задачи

// --- служебные указатели и держатели (все ячейки стадии-0 глобальные) ---
set static Task_Addr   = 0x00000000; // бегущий указатель по таблице задач
set static Queue_Addr  = 0x00000000; // бегущий хвост очереди (push)
set static Head_Addr   = 0x00000000; // бегущая голова очереди (pop)
set static Curr_Addr   = 0x00000000; // адрес слота исполнявшейся задачи
set static State_Addr  = 0x00000000; // расчётное поле state
set static VR_Addr     = 0x00000000; // расчётное поле vruntime
set static Init_Slot   = 0x00000000; // счётчик рекурсии инициализации
set static Curr_VRun   = 0x00000000; // значение vruntime в работе
set static Tmp_ID      = 0x00000000; // tid из слота для честного лога

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00002000);      // LOG: sched test START

    // инициализация: 8 слотов таблицы задач честным нулём (FREE)
    Task_Addr = TASK_TABLE;
    run Init_Slots();

    // очередь готовых: начинает пустой — указатели на единицу
    Queue_Addr = READY_QUEUE;
    Head_Addr = READY_QUEUE;
    Init_Slot = 0x00000000;

    // spawn: лидер и потомок — оба READY, адреса слотов кладутся в очередь
    run Spawn_Leader();
    run Spawn_Worker();

    // три тика честного round-robin: попеть: лидер -> потомок -> лидер
    run Schedule_Now();
    run Schedule_Now();
    run Schedule_Now();

    // honest exit: последний исполнявшийся по третьему тику (лидер, слот
    // 0x00E00018 — round-robin вернул его голову на тик 3) завершается в ZOMBIE
    run Task_Exit();

    out_cell(LOG_PORT, 0x000020FF);      // LOG: sched test DONE
    terminate;
}

// Рекурсивная инициализация 8 слотов: tid = номер слота, state = FREE (0).
// Честная схема стадии-0 без while: хвостовая рекурсия с базой в else.
function Init_Slots() {
    if (Init_Slot == 0x00000008) {
        out_cell(LOG_PORT, 0x00003110);  // LOG: task table READY
    } else {
        store_ind(Task_Addr, Init_Slot); // +0  tid = номер слота
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +4  state = FREE
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +8  nice = 0
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +12 vruntime = 0
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +16 parent = 0
        Task_Addr = Task_Addr + 4;
        store_ind(Task_Addr, 0);         // +20 exit_code = 0
        Task_Addr = Task_Addr + 4;       // +4 -> +24, следующий слот честно
        Init_Slot = Init_Slot + 1;
        run Init_Slots();
    }
}

// Задача-лидер: слот 1, READY, без родителя, кладётся в очередь готовых.
function Spawn_Leader() {
    Task_Addr = SLOT1_ADDR;
    store_ind(Task_Addr, 0x00000001);    // +0 tid = 1 (константа спавна)
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);      // +4 state = READY
    Task_Addr = Task_Addr + 12;
    store_ind(Task_Addr, 0);             // +16 parent = 0 (нет родителя)
    store_ind(Queue_Addr, SLOT1_ADDR);   // push: АДРЕС слота в хвост очереди
    Queue_Addr = Queue_Addr + 4;
}

// Задача-потомок: слот 2, READY, родитель = лидер, тоже в очередь.
function Spawn_Worker() {
    Task_Addr = SLOT2_ADDR;
    store_ind(Task_Addr, 0x00000002);    // +0 tid = 2
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);      // +4 state = READY
    Task_Addr = Task_Addr + 12;
    store_ind(Task_Addr, 0x00000001);    // +16 parent = 1 (spawn от лидера)
    store_ind(Queue_Addr, SLOT2_ADDR);   // push адреса слота в хвост
    Queue_Addr = Queue_Addr + 4;
}

// Один честный тик round-robin: POP головы -> лог tid -> vruntime++ ->
// yield: READY снова, push адреса в хвост (замыкание круга очереди).
function Schedule_Now() {
    Curr_Addr = in_cell(Head_Addr);      // адрес слота из очереди (косвенно)
    Head_Addr = Head_Addr + 4;
    Tmp_ID = in_cell(Curr_Addr);         // +0 tid исполняющейся задачи
    log_cell(LOG_PORT, Tmp_ID);          // честный вывод значения (0x54)
    VR_Addr = Curr_Addr + 12;            // +12 vruntime
    Curr_VRun = in_cell(VR_Addr);        // прочитать текущий vruntime
    Curr_VRun = Curr_VRun + 1;           // честный тик наработки
    store_ind(VR_Addr, Curr_VRun);       // записать обратно
    State_Addr = Curr_Addr + 4;          // +4 state
    store_ind(State_Addr, ST_READY);     // yield: снова READY
    store_ind(Queue_Addr, Curr_Addr);    // push адреса слота в хвост очереди
    Queue_Addr = Queue_Addr + 4;
}

// Честный выход: последний исполнявшийся (Curr_Addr — слот лидера после тика 3)
// -> ZOMBIE, exit_code честной записью; зачистку ячеек выполнит ядро (Zeroize-Exit).
function Task_Exit() {
    State_Addr = Curr_Addr + 4;
    store_ind(State_Addr, ST_ZOMBIE);    // state = ZOMBIE
    Task_Addr = Curr_Addr + 20;          // +20 exit_code
    store_ind(Task_Addr, EXIT_CODE);
    out_cell(LOG_PORT, 0x00003300);      // LOG: exit -> ZOMBIE (0xC0DE)
}
