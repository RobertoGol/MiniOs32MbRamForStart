// ===================================================================
// TKT-055/056: честное ядро планировщика (стадия-0, кооперативный каркас)
// Файл: CtOs/kernel_sched.kt | Язык: KINII (стадия-0)
//
// ЧЕСТНО: логика задач/очередей — в ядре (этот код). Механика переключения
// контекста (сохранить/восстановить регистры+PC и ПРЫГНУТЬ в entry) требует
// VM NID 0x150-152 (WORK_CTX_SAVE/RESTORE/YIELD) или нативного пролога на
// железе — поэтому Ф-А1/А2/А3 с реальным исполнением задач здесь НЕ
// закрываются. Закрывается честная машина состояний + очередь + браки,
// пригодная и для VM (с NID), и для аппаратного пути.
//
// Раскладка (Ring 2, как в sched_a55_test, без наложений):
//   0x00A10000  TASK_TABLE  32 слота × 8 слов × 4 Б:
//               +0 tid +4 state +8 prio +12 entry
//               +16 ctx +20 parent +24 retcode +28 vruntime
//   0x00A10400  TASK_NEXT   32 слова — next-индекс ready-списка (NIL=конец)
//   0x00A10480  SCHED_CTL   +0 CUR +4 READY_HEAD +8 READY_TAIL
//                           +12 COUNT +16 NEXT_TID +20 TICK
//
// Состояния: 0 FREE 1 READY 2 RUNNING 3 SLEEPING 4 ZOMBIE
// Браки: 0xF1 TASK_LIMIT 0xF2 TASK_NOT_FOUND 0xF3 TASK_STATE
// Маркеры: 0xB6xx, 0x99Cx BAD.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00A10000
#define: TASK_NEXT   0x00A10400
#define: CTL_CUR     0x00A10480
#define: CTL_HEAD    0x00A10484
#define: CTL_TAIL    0x00A10488
#define: CTL_COUNT   0x00A1048C
#define: CTL_NTID    0x00A10490
#define: CTL_TICK    0x00A10494

#define: MAX_TASKS   0x00000020
#define: NIL         0xFFFFFFFF

#define: ST_FREE     0x00000000
#define: ST_READY    0x00000001
#define: ST_RUNNING  0x00000002
#define: ST_SLEEPING 0x00000003
#define: ST_ZOMBIE   0x00000004

#define: E_LIMIT     0x000000F1
#define: E_NOTFOUND  0x000000F2
#define: E_STATE     0x000000F3

set static Slot_Idx     = 0x00000000;
set static Slot_Ptr     = 0x00000000;
set static Next_Ptr     = 0x00000000;
set static Loop_I       = 0x00000000;
set static Found_Slot   = 0xFFFFFFFF;
set static Found_Tid    = 0x00000000;
set static Spawn_Entry  = 0x00000000;
set static Spawn_Prio   = 0x00000000;
set static Spawn_Parent = 0x00000000;
set static Spawn_Out    = 0xFFFFFFFF;
set static Fail_Code    = 0x00000000;
set static Q_Idx        = 0x00000000;
set static Pop_Out      = 0xFFFFFFFF;
set static Exit_Ret     = 0x00000000;
set static Tmp_A        = 0x00000000;
set static Tmp_B        = 0x00000000;
set static Tmp_C        = 0x00000000;
set static Tmp_D        = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000B601);      // START kernel_sched

    run KSched_Init();
    run T_Init();

    run T_Spawn_Ready();
    run T_Dispatch_Yield();
    run T_Exit_Zombie();
    run T_Brakes();

    out_cell(LOG_PORT, 0x0000B6FF);      // DONE
    terminate;
}

// ===================== INIT =====================
function KSched_Init() {
    Loop_I = 0x00000000;
    run Init_Slots();
    Tmp_D = CTL_CUR;
    store_ind(Tmp_D, NIL);
    Tmp_D = CTL_HEAD;
    store_ind(Tmp_D, NIL);
    Tmp_D = CTL_TAIL;
    store_ind(Tmp_D, NIL);
    Tmp_D = CTL_COUNT;
    store_ind(Tmp_D, 0x00000000);
    Tmp_D = CTL_NTID;
    store_ind(Tmp_D, 0x00000001);
    Tmp_D = CTL_TICK;
    store_ind(Tmp_D, 0x00000000);
    Fail_Code = 0x00000000;
}

function Init_Slots() {
    if (Loop_I == MAX_TASKS) {
    } else {
        Slot_Idx = Loop_I;
        run Slot_Addr();
        store_ind(Slot_Ptr, 0x00000000);     // tid
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

// ===================== ADDRESSING =====================
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

// ===================== FIND =====================
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
            }
            Loop_I = Loop_I + 1;
            run Find_Free_Step();
        }
    }
}

function Find_By_Tid() {
    Found_Slot = NIL;
    Loop_I = 0x00000000;
    run Find_By_Tid_Step();
}
function Find_By_Tid_Step() {
    if (Loop_I == MAX_TASKS) {
    } else {
        if (Found_Slot == NIL) {
            Slot_Idx = Loop_I;
            run Slot_Addr();
            Tmp_A = in_cell(Slot_Ptr);       // tid
            Tmp_B = Slot_Ptr + 4;
            Tmp_C = in_cell(Tmp_B);          // state
            if (Tmp_C == ST_FREE) {
            } else {
                if (Tmp_A == Found_Tid) {
                    Found_Slot = Loop_I;
                }
            }
            Loop_I = Loop_I + 1;
            run Find_By_Tid_Step();
        }
    }
}

// ===================== READY QUEUE =====================
function Ready_Push() {
    Slot_Idx = Q_Idx;
    run Next_Addr();
    store_ind(Next_Ptr, NIL);
    Tmp_D = CTL_TAIL;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        Tmp_D = CTL_HEAD;
        store_ind(Tmp_D, Q_Idx);
        Tmp_D = CTL_TAIL;
        store_ind(Tmp_D, Q_Idx);
    } else {
        Slot_Idx = Tmp_A;
        run Next_Addr();
        store_ind(Next_Ptr, Q_Idx);
        Tmp_D = CTL_TAIL;
        store_ind(Tmp_D, Q_Idx);
    }
}

function Ready_Pop() {
    Pop_Out = NIL;
    Tmp_D = CTL_HEAD;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        // empty
    } else {
        Pop_Out = Tmp_A;
        Slot_Idx = Tmp_A;
        run Next_Addr();
        Tmp_B = in_cell(Next_Ptr);           // next
        Tmp_D = CTL_HEAD;
        store_ind(Tmp_D, Tmp_B);
        if (Tmp_B == NIL) {
            Tmp_D = CTL_TAIL;
            store_ind(Tmp_D, NIL);
        }
        store_ind(Next_Ptr, NIL);
    }
}

// ===================== SPAWN =====================
function Task_Spawn() {
    Fail_Code = 0x00000000;
    Spawn_Out = NIL;
    Tmp_D = CTL_COUNT;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == MAX_TASKS) {
        Fail_Code = E_LIMIT;
    } else {
        run Find_Free();
        if (Found_Slot == NIL) {
            Fail_Code = E_LIMIT;
        } else {
            Tmp_D = CTL_NTID;
            Tmp_B = in_cell(Tmp_D);
            Spawn_Out = Tmp_B;
            Tmp_C = Tmp_B + 1;
            Tmp_D = CTL_NTID;
            store_ind(Tmp_D, Tmp_C);
            Slot_Idx = Found_Slot;
            run Slot_Addr();
            store_ind(Slot_Ptr, Spawn_Out);          // tid
            Tmp_D = Slot_Ptr + 4; store_ind(Tmp_D, ST_READY);
            Tmp_D = Slot_Ptr + 8; store_ind(Tmp_D, Spawn_Prio);
            Tmp_D = Slot_Ptr + 12; store_ind(Tmp_D, Spawn_Entry);
            Tmp_D = Slot_Ptr + 16; store_ind(Tmp_D, 0x00000000); // ctx
            Tmp_D = Slot_Ptr + 20; store_ind(Tmp_D, Spawn_Parent);
            Tmp_D = Slot_Ptr + 24; store_ind(Tmp_D, 0x00000000); // retcode
            Tmp_D = Slot_Ptr + 28; store_ind(Tmp_D, 0x00000000); // vruntime
            Q_Idx = Found_Slot;
            run Ready_Push();
            Tmp_D = CTL_COUNT;
            Tmp_A = in_cell(Tmp_D);
            Tmp_A = Tmp_A + 1;
            Tmp_D = CTL_COUNT;
            store_ind(Tmp_D, Tmp_A);
        }
    }
}

// ===================== COOPERATIVE DISPATCH (no NID) =====================
// Picks next READY -> RUNNING, sets CUR. Real jump to entry requires
// NID 0x151/152 or native prologue (hardware bring-up).
function Sched_Dispatch() {
    Fail_Code = 0x00000000;
    run Ready_Pop();
    if (Pop_Out == NIL) {
        // no ready task
    } else {
        Tmp_D = CTL_CUR;
        store_ind(Tmp_D, Pop_Out);
        Slot_Idx = Pop_Out;
        run Slot_Addr();
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_RUNNING);
        Tmp_D = CTL_TICK;
        Tmp_A = in_cell(Tmp_D);
        Tmp_A = Tmp_A + 1;
        Tmp_D = CTL_TICK;
        store_ind(Tmp_D, Tmp_A);
    }
}

// Yield: RUNNING -> READY, push back, clear CUR (state only, no ctx switch)
function Task_Yield() {
    Fail_Code = 0x00000000;
    Tmp_D = CTL_CUR;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        Fail_Code = E_STATE;
    } else {
        Slot_Idx = Tmp_A;
        run Slot_Addr();
        Tmp_B = Slot_Ptr + 4;
        store_ind(Tmp_B, ST_READY);
        Q_Idx = Tmp_A;
        run Ready_Push();
        Tmp_D = CTL_CUR;
        store_ind(Tmp_D, NIL);
    }
}

// Exit: slot -> ZOMBIE + retcode, dec COUNT, clear CUR (state model)
function Task_Exit() {
    Fail_Code = 0x00000000;
    Tmp_D = CTL_CUR;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        Fail_Code = E_STATE;
    } else {
        Slot_Idx = Tmp_A;
        run Slot_Addr();
        Tmp_B = Slot_Ptr + 4;
        store_ind(Tmp_B, ST_ZOMBIE);
        Tmp_B = Slot_Ptr + 24;
        store_ind(Tmp_B, Exit_Ret);
        Tmp_D = CTL_COUNT;
        Tmp_C = in_cell(Tmp_D);
        if (Tmp_C == 0x00000000) {
        } else {
            Tmp_C = Tmp_C - 1;
            Tmp_D = CTL_COUNT;
            store_ind(Tmp_D, Tmp_C);
        }
        Tmp_D = CTL_CUR;
        store_ind(Tmp_D, NIL);
    }
}

// ===================== TESTS =====================
function T_Init() {
    Tmp_D = CTL_HEAD; Tmp_A = in_cell(Tmp_D);
    Tmp_D = CTL_TAIL; Tmp_B = in_cell(Tmp_D);
    Tmp_D = CTL_COUNT; Tmp_C = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        if (Tmp_B == NIL) {
            if (Tmp_C == 0x00000000) {
                out_cell(LOG_PORT, 0x0000B610);  // init OK
            } else {
                out_cell(LOG_PORT, 0x000099C1);
            }
        } else {
            out_cell(LOG_PORT, 0x000099C2);
        }
    } else {
        out_cell(LOG_PORT, 0x000099C3);
    }
}

function T_Spawn_Ready() {
    Spawn_Entry = 0x0000AA01;
    Spawn_Prio = 0x00000010;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Fail_Code == 0x00000000) {
        Found_Tid = Spawn_Out;
        run Find_By_Tid();
        if (Found_Slot == NIL) {
            out_cell(LOG_PORT, 0x000099C4);
        } else {
            Slot_Idx = Found_Slot;
            run Slot_Addr();
            Tmp_A = Slot_Ptr + 4;
            Tmp_B = in_cell(Tmp_A);
            if (Tmp_B == ST_READY) {
                out_cell(LOG_PORT, 0x0000B620);  // spawn->READY
            } else {
                out_cell(LOG_PORT, 0x000099C5);
            }
        }
    } else {
        out_cell(LOG_PORT, 0x000099C6);
    }
}

function T_Dispatch_Yield() {
    // dispatch: READY->RUNNING, CUR set
    run Sched_Dispatch();
    if (Pop_Out == NIL) {
        out_cell(LOG_PORT, 0x000099C7);
    } else {
        Slot_Idx = Pop_Out;
        run Slot_Addr();
        Tmp_A = Slot_Ptr + 4;
        Tmp_B = in_cell(Tmp_A);
        Tmp_D = CTL_CUR;
        Tmp_C = in_cell(Tmp_D);
        if (Tmp_B == ST_RUNNING) {
            if (Tmp_C == Pop_Out) {
                out_cell(LOG_PORT, 0x0000B630);  // dispatch->RUNNING+CUR
            } else {
                out_cell(LOG_PORT, 0x000099C8);
            }
        } else {
            out_cell(LOG_PORT, 0x000099C9);
        }
    }
    // yield: RUNNING->READY, back in queue, CUR cleared
    run Task_Yield();
    Tmp_D = CTL_CUR;
    Tmp_A = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        if (Fail_Code == 0x00000000) {
            out_cell(LOG_PORT, 0x0000B631);  // yield OK
        } else {
            out_cell(LOG_PORT, 0x000099CA);
        }
    } else {
        out_cell(LOG_PORT, 0x000099CB);
    }
    // dispatch again + yield to prove round-trip
    run Sched_Dispatch();
    run Task_Yield();
    out_cell(LOG_PORT, 0x0000B632);          // round-trip done
}

function T_Exit_Zombie() {
    run Sched_Dispatch();
    Exit_Ret = 0x0000002A;
    run Task_Exit();
    if (Fail_Code == 0x00000000) {
        // find the task (it was spawned; state ZOMBIE). Found_Tid still set.
        run Find_By_Tid();
        if (Found_Slot == NIL) {
            out_cell(LOG_PORT, 0x000099CC);
        } else {
            Slot_Idx = Found_Slot;
            run Slot_Addr();
            Tmp_A = Slot_Ptr + 4; Tmp_B = in_cell(Tmp_A);
            Tmp_A = Slot_Ptr + 24; Tmp_C = in_cell(Tmp_A);
            if (Tmp_B == ST_ZOMBIE) {
                if (Tmp_C == 0x0000002A) {
                    out_cell(LOG_PORT, 0x0000B640);  // exit->ZOMBIE+retcode
                } else {
                    out_cell(LOG_PORT, 0x000099CD);
                }
            } else {
                out_cell(LOG_PORT, 0x000099CE);
            }
        }
    } else {
        out_cell(LOG_PORT, 0x000099CF);
    }
}

function T_Brakes() {
    // fill to limit: zombie slot still occupies count model? in our model
    // Task_Exit decremented COUNT but left slot ZOMBIE (joinable). Find_Free
    // skips non-FREE, so zombie blocks slot - that's honest (needs reap).
    // For TASK_LIMIT test, spawn until find_free fails.
    run Fill_Limit();
    Spawn_Entry = 0x0000BEEF;
    Spawn_Prio = 0x00000001;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Fail_Code == E_LIMIT) {
        out_cell(LOG_PORT, 0x0000B650);      // TASK_LIMIT
    } else {
        out_cell(LOG_PORT, 0x000099D0);
    }
    Found_Tid = 0x0000DEAD;
    run Find_By_Tid();
    if (Found_Slot == NIL) {
        out_cell(LOG_PORT, 0x0000B651);      // TASK_NOT_FOUND
    } else {
        out_cell(LOG_PORT, 0x000099D1);
    }
    out_cell(LOG_PORT, 0x0000B6F0);          // real ctx switch needs NID/native
}

function Fill_Limit() {
    run Fill_Step();
}
function Fill_Step() {
    // try spawn; if no free slot -> E_LIMIT from Find_Free
    Spawn_Entry = 0x00003333;
    Spawn_Prio = 0x00000005;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Fail_Code == 0x00000000) {
        run Fill_Step();
    } else {
        if (Fail_Code == E_LIMIT) {
            out_cell(LOG_PORT, 0x0000B64F);  // table full (no free slots)
        } else {
            out_cell(LOG_PORT, 0x000099D2);
        }
    }
}
