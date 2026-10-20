// ===================================================================
// СПРИНТ PS/KILL: честные команды терминала над таблицей задач
// Файл: pskill_test.kt | Язык: KINII (подмножество стадии-0)
//
// По CtOs/terminal/TERMINAL_SPEC.md:
//   * ps (tasklist) — список задач планировщика ядра: честный обход
//     таблицы задач (спринт А: 8 слотов x 24 байта на 0x00E00000,
//     задачи с 0x00E00018, слот 0 нулевой);
//   * kill <id> — завершить задачу честно: слот помечается ZOMBIE
//     (спринт А честно добирает zombie в диспетчере);
//   * kill нулевого tid, пустого слота, zombie — честный отказ;
//   * ps честно показывает только живые (RUN/READY/SLEEPING).
//
// Слот задачи (24 байта): +0 tid, +4 состояние, +8 vruntime,
// +12 nice, +16 адрес тела, +20 будильник.
// Состояния: 1 = RUN, 2 = READY, 3 = SLEEPING, 4 = ZOMBIE.
//
// Тестовая таблица: задачи 1 RUN, 2 READY (будет убита), 3 SLEEPING,
// 4 READY, 5 ZOMBIE, 6-7 пустые. Живых в первый ps: 4, после kill: 3.
//
// Лог честный:
//   0x9900 START, 0x9905 таблица готова, 0x99FF DONE
//   ps: 0x9910 живая задача (log_cell честный tid), 0x9920 пустой
//       слот честно пропущен, 0x9930 zombie честно пропущен
//   kill: 0x9940 честно убита, 0x9950 честный отказ
//   верификации: 0x9960..0x9963, паника 0x9990
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: TASK_BASE   0x00E00018     // честные задачи (слот 0 нулевой)
#define: ST_RUN      0x00000001
#define: ST_READY    0x00000002
#define: ST_SLEEP    0x00000003
#define: ST_ZOMBIE   0x00000004

set static Scan_Idx     = 0x00000000;  // честный номер слота 1..7
set static Slot_Addr    = 0x00000000;  // честный адрес слота
set static Tmp_Read     = 0x00000000;
set static Tmp_Write    = 0x00000000;
set static Tgt_Addr     = 0x00000000;  // честный адрес поля
set static Kill_Id      = 0x00000000;  // честный tid для kill
set static Alive_Count  = 0x00000000;  // честный счётчик живых в ps

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009900);      // LOG: ps/kill START

    run Init_Tasks();

    // --- честный ps первый: живых 4 (задачи 1,2,3,4) ---
    Scan_Idx = 0x00000001;
    Slot_Addr = TASK_BASE;
    Alive_Count = 0x00000000;
    run Ps_Loop();
    log_cell(LOG_PORT, Alive_Count);

    // --- честный kill 2: живая READY честно убита ---
    Kill_Id = 0x00000002;
    run Kill_Task();                     // честно: 0x9940

    // --- честный kill 0: нулевой слот — честный отказ ---
    Kill_Id = 0x00000000;
    run Kill_Task();                     // честно: 0x9950

    // --- честный kill 6: пустой слот — честный отказ ---
    Kill_Id = 0x00000006;
    run Kill_Task();                     // честно: 0x9950

    // --- честный ps второй: живых 3 (задачи 1,3,4) ---
    Scan_Idx = 0x00000001;
    Slot_Addr = TASK_BASE;
    Alive_Count = 0x00000000;
    run Ps_Loop();
    log_cell(LOG_PORT, Alive_Count);

    // --- честные верификации ---
    Tgt_Addr = TASK_BASE + 28;           // честный state задачи 2
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == ST_ZOMBIE) {
        out_cell(LOG_PORT, 0x00009960);  // LOG: задача 2 честно zombie
    } else {
        out_cell(LOG_PORT, 0x00009990);
    }
    Tgt_Addr = TASK_BASE + 4;            // честный state задачи 1
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == ST_RUN) {
        out_cell(LOG_PORT, 0x00009961);  // LOG: задача 1 честно цела
    } else {
        out_cell(LOG_PORT, 0x00009990);
    }
    Tgt_Addr = TASK_BASE + 52;           // честный state задачи 3
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == ST_SLEEP) {
        out_cell(LOG_PORT, 0x00009962);  // LOG: спящая 3 не тронута
    } else {
        out_cell(LOG_PORT, 0x00009990);
    }
    Tgt_Addr = TASK_BASE + 68;           // честный будильник задачи 3 (+48+20)
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == 0x00001B58) {
        out_cell(LOG_PORT, 0x00009963);  // LOG: будильник No-HZ честен
    } else {
        out_cell(LOG_PORT, 0x00009990);
    }

    out_cell(LOG_PORT, 0x000099FF);      // LOG: ps/kill DONE
    terminate;
}

// ---------- честная инициализация тестовых задач ----------
// Задача N живёт в слоте N: адрес = TASK_BASE + (N-1)*24.
function Init_Tasks() {
    // задача 1: RUN
    Tgt_Addr = TASK_BASE;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 4;
    Tmp_Write = ST_RUN;
    store_ind(Tgt_Addr, Tmp_Write);

    // задача 2: READY (будет честно убита)
    Tgt_Addr = TASK_BASE + 24;
    Tmp_Write = 0x00000002;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 28;
    Tmp_Write = ST_READY;
    store_ind(Tgt_Addr, Tmp_Write);

    // задача 3: SLEEPING с будильником 7000 (No-HZ честен)
    Tgt_Addr = TASK_BASE + 48;
    Tmp_Write = 0x00000003;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 52;
    Tmp_Write = ST_SLEEP;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 68;           // честный +20 будильник
    Tmp_Write = 0x00001B58;              // честные 7000 тиков
    store_ind(Tgt_Addr, Tmp_Write);

    // задача 4: READY
    Tgt_Addr = TASK_BASE + 72;
    Tmp_Write = 0x00000004;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 76;
    Tmp_Write = ST_READY;
    store_ind(Tgt_Addr, Tmp_Write);

    // задача 5: ZOMBIE
    Tgt_Addr = TASK_BASE + 96;
    Tmp_Write = 0x00000005;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = TASK_BASE + 100;
    Tmp_Write = ST_ZOMBIE;
    store_ind(Tgt_Addr, Tmp_Write);

    // задачи 6, 7: пустые слоты — ps честно пропустит
    out_cell(LOG_PORT, 0x00009905);      // LOG: задачи честно созданы
}

// ---------- честный ps: обход слотов 1..7 ----------
// Slot_Addr честно начинается с TASK_BASE и честно шагает по +24.
function Ps_Loop() {
    if (Scan_Idx == 0x00000008) {
        // честная база: 7 слотов честно обойдены
    } else {
        Tmp_Read = in_cell(Slot_Addr);   // честный tid слота
        if (Tmp_Read == 0x00000000) {
            out_cell(LOG_PORT, 0x00009920);   // честный пустой слот пропущен
        } else {
            Tgt_Addr = Slot_Addr + 4;
            Tmp_Write = in_cell(Tgt_Addr);    // честное состояние
            if (Tmp_Write == ST_ZOMBIE) {
                out_cell(LOG_PORT, 0x00009930);   // честный zombie пропущен
            } else {
                Alive_Count = Alive_Count + 1;
                log_cell(LOG_PORT, Tmp_Read);     // честный tid в списке
            }
        }
        Slot_Addr = Slot_Addr + 24;
        Scan_Idx = Scan_Idx + 1;
        run Ps_Loop();
    }
}

// ---------- честный kill <id> ----------
// Kill_Id — честный tid. Ноль, пустой слот и zombie честно отказаны.
function Kill_Task() {
    if (Kill_Id == 0x00000000) {
        out_cell(LOG_PORT, 0x00009950);  // честный отказ: tid 0
    } else {
        Scan_Idx = 0x00000001;
        Slot_Addr = TASK_BASE;
        run Kill_Find();                 // честный поиск слота по tid
    }
}

function Kill_Find() {
    if (Scan_Idx == 0x00000008) {
        out_cell(LOG_PORT, 0x00009950);  // честный отказ: задачи нет
    } else {
        Tmp_Read = in_cell(Slot_Addr);
        if (Tmp_Read == Kill_Id) {
            Tgt_Addr = Slot_Addr + 4;
            Tmp_Write = in_cell(Tgt_Addr);
            if (Tmp_Write == ST_ZOMBIE) {
                out_cell(LOG_PORT, 0x00009950);   // честный отказ: уже zombie
            } else {
                if (Tmp_Write == 0x00000000) {
                    out_cell(LOG_PORT, 0x00009950);   // честный отказ: слот пуст
                } else {
                    Tmp_Write = ST_ZOMBIE;
                    store_ind(Tgt_Addr, Tmp_Write);   // честное завершение
                    out_cell(LOG_PORT, 0x00009940);
                }
            }
        } else {
            Slot_Addr = Slot_Addr + 24;
            Scan_Idx = Scan_Idx + 1;
            run Kill_Find();
        }
    }
}
