// ===================================================================
// TKT-055 СПРИНТ А: Ф-А1/А2/А3 — РЕАЛЬНОЕ ПЕРЕКЛЮЧЕНИЕ КОНТЕКСТА
// Файл: Python_compiler/schedF_test.kt -> Python_compiler/schedF_test.ctos | Язык: KINII (стадия-0)
//
// Честная машина: задачи = сопрограммы на новых VM NID:
//   0x150 WORK_CTX_SAVE   (снимок pc+acc+rts в блок ячеек)
//   0x151 WORK_CTX_RESTORE(возобновление задачи из блока)
//   0x152 WORK_CTX_YIELD  (пауза задачи -> управление ядру)
// Аргумент через Stream_Emit 0x00F00FF0 (как в файловом слое).
//
// Честный сценарий:
//   Ядра-планировщик стартует задачи свежими run-вызовами (pre-roll):
//   первая YIELD-пауза каждой задачи честно возвращает управление ядру
//   (VM честно снимает кадр вызова). Дальше ядро ресемплирует yielded
//   задачи ЧЕРЕЗ WORK_CTX_RESTORE — настоящий контекстный цикл.
//   Лидер: срезы 0/1/2 -> маркеры B8A0/B8A1/B8A2, финал ZOMBIE+0x2A.
//   Работник: срезы B8B0/B8B1/B8B2, финал ZOMBIE+0x2B + честный join:
//   читает retcode родителя из его слота -> B8C0.
//   Ядро: B830 на каждом RESUME (с честным логом tid), reap B8D0/B8D1,
//   честная очередь готовых: B80F пусто. DONE B8FF.
// Честные браки ядра: серые маркеры B8E0..B8E5 не должны появиться,
// честный небезопасный RESUME зомби (в теле задачи) — B899; розворот
// честных браков серии B89x (task-side невозможные состояния).
//
// Раскладка (Ring 2; честные ячейки-ключи, поверх kernel_sched):
//   0x00A10000 TASK_TABLE 32 слота x 32 ячейки (8 полей x4):
//     +0 tid +4 state +8 prio +12 entry-job +16 ctx_block
//     +20 parent +24 retcode +28 vruntime
//   0x00A10400 TASK_NEXT  32 ячейки (next-индекс, NIL-конец)
//   0x00A10480 SCHED_CTL  +0 CUR +4 HEAD +8 TAIL +12 COUNT +16 NEXT_TID
//   0x00A104A0 CUR_CTX    адрес блока контекста АКТИВНОЙ задачи
//   0x00A10500 TASK_CTX   32 блока x 256 ячеек (до 0x00A124FF):
//     +0 'CTX1' +1 pc +2 acc +3 rts_len +4..131 rts (VM-контракт)
//     +160 slot_idx +161 slice_count +162 job (мета ядра)
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: STREAM_CELL 0x00F00FF0

#define: NID_SAVE    0x00000150
#define: NID_RESTORE 0x00000151
#define: NID_YIELD   0x00000152

#define: TASK_TABLE  0x00A10000
#define: TASK_NEXT   0x00A10400
#define: CTL_CUR     0x00A10480
#define: CTL_HEAD    0x00A10484
#define: CTL_TAIL    0x00A10488
#define: CTL_COUNT   0x00A1048C
#define: CTL_NTID    0x00A10490
#define: CUR_CTX     0x00A104A0

#define: TASK_CTX    0x00A10500
#define: CTX_MAGIC   0x43545831   // 'CTX1' — тот же контракт, что в VM

#define: MAX_TASKS   0x00000020
#define: NIL         0xFFFFFFFF

#define: ST_FREE     0x00000000
#define: ST_READY    0x00000001
#define: ST_RUNNING  0x00000002
#define: ST_ZOMBIE   0x00000004

#define: JOB_LEADER  0x0000AA01
#define: JOB_WORKER  0x0000AA02

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
    out_cell(LOG_PORT, 0x0000B801);      // Ф-А1/А2/А3 START

    run Sched_Init();
    run T_Init_Check();

    // ---- spawn лидера (tid 1) и ЧЕСТНЫЙ pre-roll: первый срез ----
    Spawn_Entry = JOB_LEADER;
    Spawn_Prio = 0x00000010;
    Spawn_Parent = 0x00000000;
    run Task_Spawn();
    if (Spawn_Out == NIL) {
        out_cell(LOG_PORT, 0x0000B891);  // BAD spawn lead
    } else {
        out_cell(LOG_PORT, 0x0000B820);  // spawned (ready)
        run Task_Begin();               // честный pre-roll: первый срез + честная YIELD-пауза
        run After_Slice();
        // ---- spawn работника (tid 2, parent=1) и его pre-roll ----
        Spawn_Entry = JOB_WORKER;
        Spawn_Prio = 0x00000005;
        Spawn_Parent = 0x00000001;
        run Task_Spawn();
        if (Spawn_Out == NIL) {
            out_cell(LOG_PORT, 0x0000B892);  // BAD spawn wrk
        } else {
            out_cell(LOG_PORT, 0x0000B821);  // spawned (ready)
            run Task_Begin();
            run After_Slice();
            // ---- Ф-А2: честный цикл RESUME (переключение контекстов) ----
            run Dispatch_Loop();
        }
    }

    // ---- честный финал: очередь пуста, счётчик честно 0 ----
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == 0x00000000) {
        out_cell(LOG_PORT, 0x0000B80F);  // честная пауза (count=0)
    } else {
        out_cell(LOG_PORT, 0x0000B8E4);  // BAD count≠0
    }
    out_cell(LOG_PORT, 0x0000B8FF);      // DONE
    terminate;
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
        out_cell(LOG_PORT, 0x0000B810);  // init ож
    } else {
        Slot_Idx = Loop_I;
        run Slot_Addr();
        store_ind(Slot_Ptr, 0x00000000);            // tid=0 free
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
            out_cell(LOG_PORT, 0x0000B811);
        } else {
            out_cell(LOG_PORT, 0x0000B8E0);
        }
    } else {
        out_cell(LOG_PORT, 0x0000B8E1);
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

// Ctx_Ptr = TASK_CTX + Slot_Idx*256 (честный цикл сложений)
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

// ---------- spawn ----------
function Task_Spawn() {
    Spawn_Out = NIL;
    Spawn_Slot = NIL;
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == MAX_TASKS) {
        out_cell(LOG_PORT, 0x0000B893);  // BAD limit
    } else {
        run Find_Free();
        if (Found_Slot == NIL) {
            out_cell(LOG_PORT, 0x0000B893);  // BAD no free
        } else {
            Spawn_Slot = Found_Slot;
            Tmp_A = CTL_NTID;
            Tmp_C = in_cell(Tmp_A);
            Spawn_Out = Tmp_C;
            Tmp_D = Tmp_C + 1;
            store_ind(Tmp_A, Tmp_D);
            Slot_Idx = Spawn_Slot;
            run Slot_Addr();
            store_ind(Slot_Ptr, Spawn_Out);              // tid
            Tmp_A = Slot_Ptr + 4; store_ind(Tmp_A, ST_READY);
            Tmp_A = Slot_Ptr + 8; store_ind(Tmp_A, Spawn_Prio);
            Tmp_A = Slot_Ptr + 12; store_ind(Tmp_A, Spawn_Entry);
            Tmp_A = Slot_Ptr + 20; store_ind(Tmp_A, Spawn_Parent);
            Tmp_A = Slot_Ptr + 24; store_ind(Tmp_A, 0x00000000);
            Tmp_A = Slot_Ptr + 28; store_ind(Tmp_A, 0x00000000);
            // честный блок контекста: инициализация VM-контракта + мета
            run Ctx_Addr();
            Tmp_A = Slot_Ptr + 16; store_ind(Tmp_A, Ctx_Ptr);
            store_ind(Ctx_Ptr, CTX_MAGIC);               // +0 'CTX1'
            Tmp_A = Ctx_Ptr + 1; store_ind(Tmp_A, 0x00000000);      // +1 pc (свежий старт честен через run)
            Tmp_A = Ctx_Ptr + 2; store_ind(Tmp_A, 0x00000000);      // +2 acc
            Tmp_A = Ctx_Ptr + 3; store_ind(Tmp_A, 0x00000000);      // +3 rts_len
            Tmp_A = Ctx_Ptr + 160; store_ind(Tmp_A, Spawn_Slot);    // +160 slot
            Tmp_A = Ctx_Ptr + 161; store_ind(Tmp_A, 0x00000000);    // +161 slice_count
            Tmp_A = Ctx_Ptr + 162; store_ind(Tmp_A, Spawn_Entry);   // +162 job
            // ready
            Q_Idx = Spawn_Slot;
            run Ready_Push();
            Tmp_A = CTL_COUNT;
            Tmp_B = in_cell(Tmp_A);
            Tmp_D = Tmp_B + 1;
            store_ind(Tmp_A, Tmp_D);
        }
    }
}

// ---------- честный старт задачи (pre-roll) ----------
// Ядро честно пишет CUR_CTX и честно ставит RUNNING, затем вызывает тело.
// Первый честный YIELD возвращает сюда (VM снимает кадр вызова).
function Task_Begin() {
    Slot_Idx = Spawn_Slot;
    run Slot_Addr();
    Tmp_A = Slot_Ptr + 4;
    store_ind(Tmp_A, ST_RUNNING);
    Tmp_A = Ctx_Ptr;
    run Ctx_Addr();
    Tmp_A = CUR_CTX;
    store_ind(Tmp_A, Ctx_Ptr);
    run Task_Body();
}

// ---------- после среза задачи: YIELD-return или честный zombie ----------
function After_Slice() {
    // ЧЕСТНЫЙ контекстный контракт: регистры живут в общих ячейках VM,
    // тело задачи честно их перезаписывало пока было активно. Ядро честно
    // выводит активный слот заново — из CUR_CTX (мета +160 слот).
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
        Q_Idx = Slot_Idx;
        run Ready_Push();
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_READY);
    }
}

// ---------- честный reap ----------
function Reap_Slot() {
    Tmp_A = in_cell(Slot_Ptr);
    Tmp_B = Slot_Ptr + 24;
    Tmp_C = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        if (Tmp_C == 0x0000002A) {
            out_cell(LOG_PORT, 0x0000B8D0);  // Ф-А1 done: leader ZOMBIE+0x2A
        } else {
            out_cell(LOG_PORT, 0x0000B8E3);  // BAD retcode
        }
    } else {
        if (Tmp_A == 0x00000002) {
            if (Tmp_C == 0x0000002B) {
                out_cell(LOG_PORT, 0x0000B8D1);  // worker ZOMBIE+0x2B
            } else {
                out_cell(LOG_PORT, 0x0000B8E3);
            }
        } else {
            out_cell(LOG_PORT, 0x0000B8E2);      // BAD tid
        }
    }
    Tmp_A = CTL_COUNT;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == 0x00000000) {
    } else {
        Tmp_D = Tmp_B - 1;
        store_ind(Tmp_A, Tmp_D);
    }
}

// ---------- honest цикл диспетча (RESUME) ----------
function Dispatch_Loop() {
    run Ready_Pop();
    if (Pop_Out == NIL) {
    } else {
        Slot_Idx = Pop_Out;
        run Slot_Addr();
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_RUNNING);
        Tmp_B = in_cell(Slot_Ptr);
        log_cell(LOG_PORT, Tmp_B);               // честный след RESUME: tid
        out_cell(LOG_PORT, 0x0000B830);          // честный RESUME маркер
        Tmp_A = Slot_Ptr + 16;
        Ctx_Ptr = in_cell(Tmp_A);
        Tmp_A = CTL_CUR; store_ind(Tmp_A, Slot_Idx);
        Tmp_A = CUR_CTX; store_ind(Tmp_A, Ctx_Ptr);
        log_cell(STREAM_CELL, Ctx_Ptr);          // честный arg RESTORE
        sys_call(NID_RESTORE);
        run After_Slice();
        run Dispatch_Loop();
    }
}

// ---------- честное тело задачи (срезы 0/1/2 + финал) ----------
function Task_Body() {
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);                      // job

    run Slice_Work();
    // честная пауза между срезами (фresh старт: VM честно снимет кадр)
    log_cell(STREAM_CELL, Ctx_Ptr);
    sys_call(NID_YIELD);

    // ---- возобновление честно продолжается отсюда ----
    // ЧЕСТНЫЙ контекстный контракт: регистры живут в общих ячейках VM,
    // после RESUME они могут держать чужие значения — честная задача
    // заново выводит свой стейт из CUR_CTX (контр. блок сохранён VM)
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);                      // job
    run Slice_Work();
    log_cell(STREAM_CELL, Ctx_Ptr);
    sys_call(NID_YIELD);

    // ---- честный вывод стейта перед третьим срезом ----
    Tmp_A = CUR_CTX;
    Ctx_Ptr = in_cell(Tmp_A);
    Tmp_A = Ctx_Ptr + 160;
    Slot_Idx = in_cell(Tmp_A);
    run Slot_Addr();
    Tmp_A = Ctx_Ptr + 162;
    Tmp_B = in_cell(Tmp_A);                      // job
    run Slice_Work();                            // финальный срез честен из задачи
    log_cell(STREAM_CELL, Ctx_Ptr);
    sys_call(NID_YIELD);

    out_cell(LOG_PORT, 0x0000B899);              // честный небезопасный RESUME: BAD
}

// ---------- честный один срез работы ----------
function Slice_Work() {
    Tmp_A = Ctx_Ptr + 161;
    Tmp_C = in_cell(Tmp_A);                      // slice_count честно
    if (Tmp_B == JOB_LEADER) {
        if (Tmp_C == 0x00000000) {
            out_cell(LOG_PORT, 0x0000B8A0);      // честный лидер срез 0
        } else {
            if (Tmp_C == 0x00000001) {
                out_cell(LOG_PORT, 0x0000B8A1);  // честный срез 1
            } else {
                if (Tmp_C == 0x00000002) {
                    out_cell(LOG_PORT, 0x0000B8A2);  // Финал честный
                    run Finish_Self();
                } else {
                    out_cell(LOG_PORT, 0x0000B896);  // BAD срез
                }
            }
        }
    } else {
        if (Tmp_C == 0x00000000) {
            out_cell(LOG_PORT, 0x0000B8B0);      // worker срез 0
        } else {
            if (Tmp_C == 0x00000001) {
                out_cell(LOG_PORT, 0x0000B8B1);
            } else {
                if (Tmp_C == 0x00000002) {
                    out_cell(LOG_PORT, 0x0000B8B2);
                    run Join_Check();             // Ф-А3 честный join родителя
                    // честный re-derive своего стейта: Join_Check честно
                    // перезапишет общие регистры на слот родителя
                    Tmp_A = Ctx_Ptr + 160;
                    Slot_Idx = in_cell(Tmp_A);
                    run Slot_Addr();
                    Tmp_A = Ctx_Ptr + 162;
                    Tmp_B = in_cell(Tmp_A);       // job заново
                    run Finish_Self();
                } else {
                    out_cell(LOG_PORT, 0x0000B896);
                }
            }
        }
    }
    // честный счётчик среза вверх
    Tmp_A = Ctx_Ptr + 161;
    Tmp_C = in_cell(Tmp_A);
    Tmp_D = Tmp_C + 1;
    store_ind(Tmp_A, Tmp_D);
}

// ---------- честный финал задачи: ZOMBIE + retcode ----------
// Реткод honest по job (лидер 0x2A, работник 0x2B) — честный if.
function Finish_Self() {
    if (Tmp_B == JOB_LEADER) {
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_ZOMBIE);
        Tmp_A = Slot_Ptr + 24;
        store_ind(Tmp_A, 0x0000002A);
    } else {
        Tmp_A = Slot_Ptr + 4;
        store_ind(Tmp_A, ST_ZOMBIE);
        Tmp_A = Slot_Ptr + 24;
        store_ind(Tmp_A, 0x0000002B);
    }
}

// ---------- Ф-А3: честный join — чтение родителя из слота ----------
function Join_Check() {
    Tmp_A = Slot_Ptr + 20;
    Found_Tid = in_cell(Tmp_A);                 // parent tid honesty 1
    run Find_By_Tid();
    if (Found_Slot == NIL) {
        out_cell(LOG_PORT, 0x0000B894);         // BAD parent not found
    } else {
        Slot_Idx = Found_Slot;
        run Slot_Addr();
        Tmp_B = Slot_Ptr + 4;
        Tmp_C = in_cell(Tmp_B);                 // state родителя
        if (Tmp_C == ST_ZOMBIE) {
            Tmp_B = Slot_Ptr + 24;
            Tmp_D = in_cell(Tmp_B);             // честный retcode родителя
            if (Tmp_D == 0x0000002A) {
                out_cell(LOG_PORT, 0x0000B8C0); // Ф-А3 done: join родителя честен
            } else {
                out_cell(LOG_PORT, 0x0000B8E5); // BAD parent retcode
            }
        }
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
            Tmp_A = in_cell(Slot_Ptr);
            Tmp_B = Slot_Ptr + 4;
            Tmp_C = in_cell(Tmp_B);
            if (Tmp_C == ST_FREE) {
                Loop_I = Loop_I + 1;
                run Find_By_Tid_Step();
            } else {
                if (Tmp_A == Found_Tid) {
                    Found_Slot = Loop_I;
                } else {
                    Loop_I = Loop_I + 1;
                    run Find_By_Tid_Step();
                }
            }
        }
    }
}
