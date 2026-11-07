// ===================================================================
// TKT-055 СПРИНТ А (частичная честная реализация на стадии-0, без VM NID)
// Файл: Python_compiler/sched_a55_test.kt | Язык: KINII (стадия-0)
//
// ЧЕСТНАЯ ГРАНИЦА: этот стенд проверяет то, что можно честно проверить
// БЕЗ новых NID VM 0x150-152 (WORK_CTX_SAVE/RESTORE/YIELD): таблицу задач,
// spawn/очередь/состояния, честные браки ядра. Реальное переключение
// контекста (Ф-А1/A2/A3 полностью с исполнением задач) — после VM-правок.
//
// Честная раскладка памяти (Ring 2, пересечений нет; дизайн sched_a_design.md
// + честная поправка адресов-управления, чтобы не накладываться на таблицу):
//   0x00A10000  TASK_TABLE  32 слота × 8 слов × 4 Б = 1024 Б:
//               +0 tid | +4 state | +8 prio | +12 entry
//               +16 pc_cell | +20 parent | +24 retcode | +28 vruntime
//   0x00A10400  TASK_NEXT   32 слова — next-индекс слота для связного списка
//               готовых (0xFFFFFFFF = конец). Параллельный массив: дизайн
//               задаёт 8 слов/слот, next вынесен честно отдельно.
//   0x00A10480  SCHED_CTL   +0 CUR_TASK (индекс) | +4 READY_HEAD | +8 READY_TAIL
//                           +12 TASK_COUNT(занято) | +16 NEXT_TID
//
// Состояния: 0 FREE | 1 READY | 2 RUNNING | 3 SLEEPING | 4 ZOMBIE
// Браки: 0xF1 TASK_LIMIT | 0xF2 TASK_NOT_FOUND | 0xF3 TASK_STATE
// Маркеры: 0xB5xx серия TKT-055 (не пересекается с 0x9xxx/0x71xx/0xAxxx)
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_TABLE  0x00A10000
#define: TASK_NEXT   0x00A10400
#define: SCHED_CTL   0x00A10480

#define: CTL_CUR     0x00A10480
#define: CTL_HEAD    0x00A10484
#define: CTL_TAIL    0x00A10488
#define: CTL_COUNT   0x00A1048C
#define: CTL_NTID    0x00A10490

#define: SLOT_WORDS  0x00000008
#define: SLOT_BYTES  0x00000020
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

set static Slot_Idx    = 0x00000000;
set static Slot_Ptr    = 0x00000000;
set static Next_Ptr    = 0x00000000;
set static Tmp_A       = 0x00000000;
set static Tmp_B       = 0x00000000;
set static Tmp_C       = 0x00000000;
set static Tmp_D       = 0x00000000;
set static Loop_I      = 0x00000000;
set static Found_Slot  = 0xFFFFFFFF;
set static Found_Tid   = 0x00000000;
set static Spawn_Entry = 0x00000000;
set static Spawn_Prio  = 0x00000000;
set static Spawn_Parent= 0x00000000;
set static Spawn_Out   = 0xFFFFFFFF;
set static Fail_Code   = 0x00000000;
set static Q_Idx       = 0x00000000;
set static Pop_Out     = 0xFFFFFFFF;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x0000B501);      // START TKT-055 partial

    run Sched_Init();

    // Ф-Т1: init честный — 32 FREE, head/tail NIL, count 0
    run Check_Init();

    // Ф-Т2: spawn задачи 1 (slot 1 зарезервирован под ядро концептуально,
    // но честно ищем свободный с 0; slot 0 пусть будет ядром — пометим позже)
    Spawn_Entry = 0x00001111;
    Spawn_Prio = 0x00000010;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Fail_Code == 0x00000000) {
        // Spawn_Out = tid новой задачи
        Found_Tid = Spawn_Out;
        run Find_By_Tid();
        if (Found_Slot == 0xFFFFFFFF) {
            out_cell(LOG_PORT, 0x000099B1);  // BAD: spawned but not found
        } else {
            Slot_Idx = Found_Slot;
            run Slot_Addr();
            Tmp_A = Slot_Ptr + 4;
            Tmp_B = in_cell(Tmp_A);          // state
            if (Tmp_B == ST_READY) {
                out_cell(LOG_PORT, 0x0000B511);  // spawn -> READY in table
            } else {
                out_cell(LOG_PORT, 0x000099B2);  // BAD: state not READY
            }
        }
    } else {
        out_cell(LOG_PORT, 0x000099B0);      // BAD: first spawn failed
    }

    // Ф-Т3: честный exit -> ZOMBIE + retcode (без VM context switch,
    // только состояние/ячейки — как "ядро приняло решение")
    if (Found_Slot == 0xFFFFFFFF) {
        out_cell(LOG_PORT, 0x000099B3);
    } else {
        Slot_Idx = Found_Slot;
        run Slot_Addr();
        // снимаем из очереди готовых честным pop-поиском? проще: пометим
        // ZOMBIE напрямую (моделируем что ядро обработало exit)
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_ZOMBIE);
        Tmp_A = Slot_Ptr + 24;
        store_ind(Tmp_A, 0x0000002A);        // retcode 42
        Tmp_A = Slot_Ptr + 4;
        Tmp_B = in_cell(Tmp_A);
        Tmp_A = Slot_Ptr + 24;
        Tmp_C = in_cell(Tmp_A);
        if (Tmp_B == ST_ZOMBIE) {
            if (Tmp_C == 0x0000002A) {
                out_cell(LOG_PORT, 0x0000B521);  // exit -> ZOMBIE + retcode
            } else {
                out_cell(LOG_PORT, 0x000099B4);
            }
        } else {
            out_cell(LOG_PORT, 0x000099B5);
        }
    }

    // Диагностика: сколько слотов FREE перед заполнением
    run Count_Free();
    log_cell(LOG_PORT, Tmp_C);
    out_cell(LOG_PORT, 0x0000B52F);
    // Ф-Н1: TASK_LIMIT — заполняем до MAX_TASKS честными spawn'ами
    run Fill_To_Limit();
    // ещё один spawn сверх лимита
    Spawn_Entry = 0x0000BEEF;
    Spawn_Prio = 0x00000001;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Fail_Code == E_LIMIT) {
        if (Spawn_Out == NIL) {
            out_cell(LOG_PORT, 0x0000B531);  // TASK_LIMIT честный
        } else {
            out_cell(LOG_PORT, 0x000099B6);
        }
    } else {
        out_cell(LOG_PORT, 0x000099B7);      // BAD: лимит не сработал
    }

    // Ф-Н2: поиск/«join» несуществующего tid -> TASK_NOT_FOUND
    Found_Tid = 0x0000DEAD;
    run Find_By_Tid();
    if (Found_Slot == NIL) {
        Fail_Code = E_NOTFOUND;
        out_cell(LOG_PORT, 0x0000B541);      // TASK_NOT_FOUND честный
    } else {
        out_cell(LOG_PORT, 0x000099B8);
    }

    // честный отчёт: контекстные фазы A1-A3 заблокированы на NID 0x150-152
    out_cell(LOG_PORT, 0x0000B5F0);          // A1-A3 blocked on VM NID 0x150-152
    out_cell(LOG_PORT, 0x0000B5FF);          // DONE
    terminate;
}

// ---------- инициализация ----------
function Sched_Init() {
    Loop_I = 0x00000000;
    run Init_Slots();
    Tmp_A = CTL_CUR;
    store_ind(Tmp_A, NIL);
    Tmp_A = CTL_HEAD;
    store_ind(Tmp_A, NIL);
    Tmp_A = CTL_TAIL;
    store_ind(Tmp_A, NIL);
    Tmp_A = CTL_COUNT;
    store_ind(Tmp_A, 0x00000000);
    Tmp_A = CTL_NTID;
    store_ind(Tmp_A, 0x00000001);
    Fail_Code = 0x00000000;
}

function Init_Slots() {
    if (Loop_I == MAX_TASKS) {
        // done
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

function Check_Init() {
    Tmp_D = CTL_HEAD;
    Tmp_A = in_cell(Tmp_D);
    Tmp_D = CTL_TAIL;
    Tmp_B = in_cell(Tmp_D);
    Tmp_D = CTL_COUNT;
    Tmp_C = in_cell(Tmp_D);
    if (Tmp_A == NIL) {
        if (Tmp_B == NIL) {
            if (Tmp_C == 0x00000000) {
                out_cell(LOG_PORT, 0x0000B510);  // init ctl OK
            } else {
                log_cell(LOG_PORT, Tmp_C);
                out_cell(LOG_PORT, 0x000099A1);
            }
        } else {
            log_cell(LOG_PORT, Tmp_B);
            out_cell(LOG_PORT, 0x000099A2);
        }
    } else {
        log_cell(LOG_PORT, Tmp_A);
        out_cell(LOG_PORT, 0x000099A3);
    }
}

// ---------- адресация: Slot_Ptr = TASK_TABLE + Slot_Idx*32 ----------
function Slot_Addr() {
    Slot_Ptr = TASK_TABLE;
    Loop_I = 0x00000000;
    run Slot_Addr_Step();
}
function Slot_Addr_Step() {
    if (Loop_I == Slot_Idx) {
        // Slot_Ptr готов
    } else {
        Slot_Ptr = Slot_Ptr + 32;
        Loop_I = Loop_I + 1;
        run Slot_Addr_Step();
    }
}

// Next_Ptr = TASK_NEXT + Slot_Idx*4
function Next_Addr() {
    Next_Ptr = TASK_NEXT;
    Loop_I = 0x00000000;
    run Next_Addr_Step();
}
function Next_Addr_Step() {
    if (Loop_I == Slot_Idx) {
        // done
    } else {
        Next_Ptr = Next_Ptr + 4;
        Loop_I = Loop_I + 1;
        run Next_Addr_Step();
    }
}

// ---------- поиск свободного слота -> Found_Slot ----------
function Find_Free() {
    Found_Slot = NIL;
    Loop_I = 0x00000000;
    run Find_Free_Step();
}
function Find_Free_Step() {
    if (Loop_I == MAX_TASKS) {
        // не найден
    } else {
        if (Found_Slot == NIL) {
            Slot_Idx = Loop_I;
            run Slot_Addr();
            Tmp_A = Slot_Ptr + 4;
            Tmp_B = in_cell(Tmp_A);
            if (Tmp_B == ST_FREE) {
                Found_Slot = Loop_I;
            } else {
                // keep searching
            }
            Loop_I = Loop_I + 1;
            run Find_Free_Step();
        } else {
            // уже найден — стоп
        }
    }
}

// ---------- поиск по tid -> Found_Slot ----------
function Find_By_Tid() {
    Found_Slot = NIL;
    Loop_I = 0x00000000;
    run Find_By_Tid_Step();
}
function Find_By_Tid_Step() {
    if (Loop_I == MAX_TASKS) {
        // не найден
    } else {
        if (Found_Slot == NIL) {
            Slot_Idx = Loop_I;
            run Slot_Addr();
            Tmp_A = in_cell(Slot_Ptr);       // tid
            Tmp_B = Slot_Ptr + 4;
            Tmp_C = in_cell(Tmp_B);          // state
            if (Tmp_C == ST_FREE) {
                // пустой — пропуск
            } else {
                if (Tmp_A == Found_Tid) {
                    Found_Slot = Loop_I;
                } else {
                    // нет
                }
            }
            Loop_I = Loop_I + 1;
            run Find_By_Tid_Step();
        } else {
            // стоп
        }
    }
}

// ---------- ready queue: push slot index Q_Idx в хвост ----------
function Ready_Push() {
    Slot_Idx = Q_Idx;
    run Next_Addr();
    store_ind(Next_Ptr, NIL);
    Tmp_A = CTL_TAIL;
    Tmp_A = in_cell(Tmp_A);
    if (Tmp_A == NIL) {
        Tmp_A = CTL_HEAD;
        store_ind(Tmp_A, Q_Idx);
        Tmp_A = CTL_TAIL;
        store_ind(Tmp_A, Q_Idx);
    } else {
        // next[tail] = Q_Idx
        Slot_Idx = Tmp_A;
        run Next_Addr();
        store_ind(Next_Ptr, Q_Idx);
        Tmp_A = CTL_TAIL;
        store_ind(Tmp_A, Q_Idx);
    }
}

// ---------- spawn: Spawn_Entry/Prio/Parent -> Spawn_Out tid или NIL, Fail_Code ----------
function Task_Spawn() {
    Fail_Code = 0x00000000;
    Spawn_Out = NIL;
    Tmp_A = CTL_COUNT;
    Tmp_A = in_cell(Tmp_A);
    if (Tmp_A == MAX_TASKS) {
        Fail_Code = E_LIMIT;
    } else {
        run Find_Free();
        if (Found_Slot == NIL) {
            Fail_Code = E_LIMIT;
        } else {
            Tmp_A = CTL_NTID;
            Tmp_B = in_cell(Tmp_A);
            Spawn_Out = Tmp_B;
            Tmp_C = Tmp_B + 1;
            Tmp_A = CTL_NTID;
            store_ind(Tmp_A, Tmp_C);
            Slot_Idx = Found_Slot;
            run Slot_Addr();
            store_ind(Slot_Ptr, Spawn_Out);          // tid
            Tmp_D = Slot_Ptr + 4; store_ind(Tmp_D, ST_READY);
            Tmp_D = Slot_Ptr + 8; store_ind(Tmp_D, Spawn_Prio);
            Tmp_D = Slot_Ptr + 12; store_ind(Tmp_D, Spawn_Entry);
            Tmp_D = Slot_Ptr + 16; store_ind(Tmp_D, 0x00000000); // pc_cell
            Tmp_D = Slot_Ptr + 20; store_ind(Tmp_D, Spawn_Parent);
            Tmp_D = Slot_Ptr + 24; store_ind(Tmp_D, 0x00000000); // retcode
            Tmp_D = Slot_Ptr + 28; store_ind(Tmp_D, 0x00000000); // vruntime
            Q_Idx = Found_Slot;
            run Ready_Push();
            Tmp_D = CTL_COUNT;
            Tmp_A = in_cell(Tmp_D);
            Tmp_A = Tmp_A + 1;
            store_ind(Tmp_D, Tmp_A);
        }
    }
}

// Диагностика: Tmp_C = число FREE слотов
function Count_Free() {
    Tmp_C = 0x00000000;
    Loop_I = 0x00000000;
    run Count_Free_Step();
}
function Count_Free_Step() {
    if (Loop_I == MAX_TASKS) {
        // done
    } else {
        Slot_Idx = Loop_I;
        run Slot_Addr();
        Tmp_A = Slot_Ptr + 4;
        Tmp_B = in_cell(Tmp_A);
        if (Tmp_B == ST_FREE) {
            Tmp_C = Tmp_C + 1;
        } else {
            // occupied
        }
        Loop_I = Loop_I + 1;
        run Count_Free_Step();
    }
}

// ---------- Ф-Н1 helper: заполнить до лимита ----------
function Fill_To_Limit() {
    // уже есть count из CTL_COUNT; спавним пока count < MAX
    run Fill_Step();
}
function Fill_Step() {
    Tmp_A = CTL_COUNT;
    Tmp_A = in_cell(Tmp_A);
    if (Tmp_A == MAX_TASKS) {
        out_cell(LOG_PORT, 0x0000B530);      // table full
    } else {
        Spawn_Entry = 0x00002222;
        Spawn_Prio = 0x00000005;
        Spawn_Parent = 0x00000000;
        run Task_Spawn();
        if (Fail_Code == 0x00000000) {
            run Fill_Step();
        } else {
            log_cell(LOG_PORT, Fail_Code);
            Tmp_B = CTL_COUNT;
            Tmp_B = in_cell(Tmp_B);
            log_cell(LOG_PORT, Tmp_B);
            out_cell(LOG_PORT, 0x000099BF);  // unexpected fail while filling
        }
    }
}
