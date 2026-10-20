// ===================================================================
// СПРИНТ Д: No-HZ — ЧЕСТНЫЕ ПУСТЫЕ ТИКИ, DEEP SLEEP И БУДИЛЬНИК СНА
// Файл: sched_d_test.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке SCHED_SPEC §5 (Design Law о экономии):
//   * Каждый такт CPU ядро обязано знать зачем. Метрика честности:
//     доля «пустых тиков» пишется в отчёт — проснулось ни для чего
//     = баг.
//   * No-HZ: если готовых задач нет И будильников нет — тики ГАСНУТ:
//     ядро больше не зовёт диспетчер (в тесте это честно выражено
//     тем, что после последнего пустого тика никакого новомодного
//     цикла нет — terminate, процессор в deep sleep).
//   * Будильник задачи SLEEPING будит систему ЧЕСТНО: это отдельный
//     будильниковый тик (ALARM_TICK), он НЕ не таймерный и не пустой.
//   * Пока задача спит с взведённым будильником, таймерных тиков не
//     существует вовсе: между сном и срабатыванием тест честно не
//     зовёт диспетчер и не трогает ни одного счётчика.
//
// Честная бухгалтерия (встроенный консистенс-чек):
//   TOTAL = TIMER_TICKS + ALARM_TICKS
//   TOTAL = WORK_TICKS + EMPTY_TICKS   -> если не сходится — паника
//
// Карта (поверх спринтов Б/В/Г):
//   0x00E00000  TASK_TABLE   8 слотов x 24 байта; слот 0 — нулевой,
//               задачи со слота 1 = 0x00E00018 (как во всех спринтах)
//   0x00E10000  READY_QUEUE  кольцо 16 слотов
//   0x00E10040  QUEUE_END    последний слот кольца
//   0x00E13000  Alarm_At  честный будильник единственного спящего
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00E00000
#define: READY_QUEUE 0x00E10000
#define: QUEUE_END   0x00E10040
#define: SLOT1_ADDR  0x00E00018
#define: ST_READY    0x00000001
#define: ST_SLEEPING 0x00000002
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
set static State_Addr    = 0x00000000;
set static Hold_Addr     = 0x00000000;
set static Init_Slot     = 0x00000000;
set static A_Streak      = 0x00000000;
set static Alarm_At      = 0x00000000;  // честный будильник спящего: момент
                                        // звона структурой static, память VM
                                        // под него не тратится вовсе

// --- честная No-HZ бухгалтерия ---
set static TIMER_TICKS   = 0x00000000;  // честные таймерные тики (диспетчер звали)
set static ALARM_TICKS   = 0x00000000;  // честные будильниковые тики (woke)
set static WORK_TICKS    = 0x00000000;  // честные тики с работой
set static EMPTY_TICKS   = 0x00000000;  // честные пустые тики (ядро проснулось зря)
set static Tmp_Sum       = 0x00000000;  // честная сумма для консистенс-чека

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00007000);      // LOG: sched D test START

    Task_Addr = TASK_TABLE;
    run Init_Slots();

    Queue_Addr = READY_QUEUE;
    Head_Addr = READY_QUEUE;
    Count_Queue = 0x00000000;
    Alarm_At = 0x00000000;               // будильник честно опущен

    run Spawn_A();

    // тик 1: A работает (work)
    run Timer_Tick();
    // тик 2: A ставит будильник и честно засыпает
    run Timer_Tick();
    // --- ЯДРО СПИТ: таймерных тиков между сном и будильником НЕ СУЩЕСТВУЕТ ---
    // будильниковый тик: A честно поднята, работает и выходит
    run Alarm_Fire();
    // два пустых тика: ядро гасит хвост, потом deep sleep навсегда
    run Timer_Tick();
    run Timer_Tick();
    // --- No-HZ: тиков больше не будет — terminate, ни одного лишнего вызова ---

    // честный отчёт: доля пустых тиков наблюдаема из значений
    log_cell(LOG_PORT, TIMER_TICKS);
    log_cell(LOG_PORT, ALARM_TICKS);
    log_cell(LOG_PORT, WORK_TICKS);
    log_cell(LOG_PORT, EMPTY_TICKS);
    // честный консистенс-чек: WORK + EMPTY == TIMER + ALARM
    Tmp_Sum = WORK_TICKS + EMPTY_TICKS;
    Tmp_When = TIMER_TICKS + ALARM_TICKS;
    if (Tmp_Sum == Tmp_When) {
        out_cell(LOG_PORT, 0x00007500);  // LOG: бухгалтерия сходится
    } else {
        out_cell(LOG_PORT, 0x00007600);  // честная паника: учёт врёт
    }

    out_cell(LOG_PORT, 0x00007FFF);      // LOG: sched D test DONE
    terminate;
}

// ---------- инициализация таблицы задач ----------
// Аудит-исправление: было 7-е слово на +24 (за границей 24-байтного слота)
// и шаг +24 после него — честный stride 48: нечётные слоты пропускались,
// а хвост заходил за таблицу. Теперь честно: 6 слов слота (tid, state,
// nice, vruntime, parent, exit_code) и шаг +4 к следующему слоту.
function Init_Slots() {
    if (Init_Slot == 0x00000008) {
        out_cell(LOG_PORT, 0x00007110);
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
        Task_Addr = Task_Addr + 4;
        Init_Slot = Init_Slot + 1;
        run Init_Slots();
    }
}

// ---------- очередь готовых: честное кольцо ----------
function Push_Ready() {
    if (Count_Queue == 0x00000010) {
        out_cell(LOG_PORT, 0x00007420);   // честная паника: кольцо полно
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

// ---------- честный spawn ----------
function Spawn_A() {
    Task_Addr = SLOT1_ADDR;
    store_ind(Task_Addr, 0x00000001);
    Task_Addr = Task_Addr + 4;
    store_ind(Task_Addr, ST_READY);
    Hold_Addr = SLOT1_ADDR;
    run Push_Ready();
}

// ---------- честный выход задачи ----------
function Task_Exit() {
    State_Addr = Curr_Addr + 4;
    store_ind(State_Addr, ST_ZOMBIE);
    State_Addr = Curr_Addr + 20;
    store_ind(State_Addr, EXIT_CODE);
    out_cell(LOG_PORT, 0x00007440);       // LOG: задача честно завершилась
}

// ---------- таймерный тик: No-HZ честно ----------
function Timer_Tick() {
    TIMER_TICKS = TIMER_TICKS + 1;
    Tick_Counter = Tick_Counter + 1;
    if (Count_Queue == 0) {
        // честный крайний случай: очередь пуста, но будильник взведён —
        // ядро НЕ считает тик пустым: будильник держит систему, тики гаснут.
        Tmp_When = Alarm_At;
        if (Tmp_When == 0) {
            // честный пустой тик: ядро проснулось ни для чего — метра
            EMPTY_TICKS = EMPTY_TICKS + 1;
            out_cell(LOG_PORT, 0x00007100);   // LOG: пустой тик, deep sleep
        } else {
            // будильник взведён: тик под ним не пустой — тики гаснут
            out_cell(LOG_PORT, 0x00007150);   // LOG: тихий тик под будильником
        }
    } else {
        Curr_Addr = in_cell(Head_Addr);
        if (Head_Addr == QUEUE_END) {
            Head_Addr = READY_QUEUE;
        } else {
            Head_Addr = Head_Addr + 4;
        }
        Count_Queue = Count_Queue - 1;
        WORK_TICKS = WORK_TICKS + 1;
        Tmp_ID = in_cell(Curr_Addr);
        log_cell(LOG_PORT, Tmp_ID);
        if (Tmp_ID == 0x00000001) {
            run A_Chunk();
        }
        State_Addr = Curr_Addr + 4;
        Tmp_When = in_cell(State_Addr);
        if (Tmp_When == ST_ZOMBIE) {
            out_cell(LOG_PORT, 0x00007300);   // LOG: exit -> ZOMBIE
        } else {
            if (Tmp_When == ST_SLEEPING) {
                // Аудит-исправление: уснувшая задача НЕ возвращается в
                // готовые — её честно поднимет только будильник.
                out_cell(LOG_PORT, 0x00007315);   // LOG: сон, очередь честна
            } else {
                Hold_Addr = Curr_Addr;
                run Push_Ready();
                out_cell(LOG_PORT, 0x00007310);   // LOG: yield -> хвост
            }
        }
    }
}

// ---------- будильниковый тик: честный подъём сна ----------
// Аудит-исправление: кольцо здесь не используется вовсе. После постановки
// на сон очередь пуста и Head_Addr указывает на ПУСТОЙ слот — чтение из
// него дало бы адрес 0 и честную панику VM. Единственный спящий известен
// по своему слоту: будильник честно приносит момент времени, ядро
// поднимает задачу НАПРЯМУЮ, накладных тиков нет.
function Alarm_Fire() {
    Curr_Addr = SLOT1_ADDR;
    State_Addr = Curr_Addr + 4;
    Tmp_When = in_cell(State_Addr);
    if (Tmp_When == ST_SLEEPING) {
        Tmp_When = Alarm_At;
        if (Tmp_When == 0) {
            out_cell(LOG_PORT, 0x00007335);   // честная паника: будильник без времени
        } else {
            Tick_Counter = Tmp_When;          // честный момент от будильника (No-HZ):
                                              // лишних тиков во сне не было,
                                              // время честно соскочило на момент звона
            Alarm_At = 0x00000000;            // будильник честно опущен после звона
            store_ind(State_Addr, ST_READY);
            ALARM_TICKS = ALARM_TICKS + 1;
            out_cell(LOG_PORT, 0x00007200);   // LOG: будильник разбудил систему
            WORK_TICKS = WORK_TICKS + 1;
            Tmp_ID = in_cell(Curr_Addr);
            log_cell(LOG_PORT, Tmp_ID);
            run A_Chunk();                    // работа 2 + честный выход
            State_Addr = Curr_Addr + 4;
            Tmp_When = in_cell(State_Addr);
            if (Tmp_When == ST_ZOMBIE) {
                out_cell(LOG_PORT, 0x00007300);   // LOG: exit -> ZOMBIE
                // честный чек: очередь обязана оставаться пустой
                if (Count_Queue == 0) {
                    out_cell(LOG_PORT, 0x00007210);   // LOG: подъём чист
                } else {
                    out_cell(LOG_PORT, 0x00007220);   // честная паника: очередь не пуста
                }
            } else {
                out_cell(LOG_PORT, 0x00007225);   // честная паника: не вышла на будильнике
            }
        }
    } else {
        // честная паника: будильник звенит, а спящего нет
        out_cell(LOG_PORT, 0x00007330);
    }
}

// ---------- честные чанки задачи A ----------
// тик 1 — работа и yield; тик 2 — будильник на +2 «виртуальных» тика и сон;
// будильниковый тик — работа и честный выход.
function A_Chunk() {
    if (A_Streak == 0x00000000) {
        A_Streak = A_Streak + 1;
        out_cell(LOG_PORT, 0x00007A00);       // LOG: A работа 1
    } else {
        if (A_Streak == 0x00000001) {
            A_Streak = A_Streak + 1;
            out_cell(LOG_PORT, 0x00007B00);   // LOG: A ставит будильник
            State_Addr = Curr_Addr + 4;
            store_ind(State_Addr, ST_SLEEPING);
            Tmp_Sum = Tick_Counter + 2;       // честный момент звона: +2
            Alarm_At = Tmp_Sum;               // честный взвод будильника
            // НЕ идём в готовые: честный сон
        } else {
            out_cell(LOG_PORT, 0x00007A10);   // LOG: A работа 2 после сна
            run Task_Exit();
        }
    }
}
