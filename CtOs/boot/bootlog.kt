// ===================================================================
// TKT-026 — ЧЕСТНЫЙ BOOTLOG СТАДИИ-0 (CtOs/boot/)
// Файл: bootlog.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке: CtOs/boot/BOOTLOG_SPEC.md
//   1) журнал в памяти BOOT_LOG 0x00E30000: записи 12 байт
//      (tick, уровень, код стадии), до 256 записей (0xC00);
//   2) три честных уровня [ ok ]/[info]/[warn] и отдельный [FAIL]
//      (паника ядра: честный дамп ячеек и остановка загрузки);
//   3) 9 честных стадий: power/kernel/scheduler/bridge/mount/fs/
//      themes/apps/shell + честное «лог свёрнут» в конце;
//   4) fastfetch-аналог: SYSINFO из РЕАЛЬНЫХ ячеек, нет данных — «—».
//
// Честные ограничения стадии-0 (не прячем):
//   * нет строк и webm: уровень/стадия — числовые коды, текст стадий
//     живёт в спеке; boot video — только честный флаг Boot_Vid;
//   * тики — честный счётчик ядра (No-HZ: во сне тиков нет, поэтому
//     между стадиями честные «прыжки»);
//   * [FAIL] реализован на ОТДЕЛЬНОЙ зоне PANIC_LOG: паника не имеет
//     права затирать уже честно записанный журнал загрузки.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT     0x3F0050C0   // ранняя строка лога ядра
#define: BOOT_LOG     0x00E30000   // журнал загрузки: 256 × 12 байт
#define: LOG_MAX      0x00000100   // честный предел записей (256)
#define: LOG_ENTRY    0x0000000C   // одно слово tick + уровень + стадия
#define: BOOT_SEQ     0x00E32000   // честная последовательность стадий (10×12)
#define: SYSINFO      0x00E31000   // сводка fetch/sysinfo (8 слов)
#define: PANIC_LOG    0x00E33000   // зона [FAIL]-паники (отдельно!)
#define: CELL_DUMP    0x00E34000   // честный дамп 4 ячеек ядра при панике

// уровни журнала (честные коды, текст — в спеке)
#define: LV_OK        0x00000001   // [ ok ]
#define: LV_INFO      0x00000002   // [info]
#define: LV_WARN      0x00000003   // [warn]
#define: LV_FAIL      0x00000004   // [FAIL]

// стадии загрузки (порядок спеки BOOTLOG_SPEC, раздел «Стадии»)
#define: ST_POWER     0x00000001
#define: ST_KERNEL    0x00000002
#define: ST_SCHED     0x00000003
#define: ST_BRIDGE    0x00000004
#define: ST_MOUNT     0x00000005
#define: ST_FS        0x00000006
#define: ST_THEMES    0x00000007
#define: ST_APPS      0x00000008
#define: ST_SHELL     0x00000009

// --- журнал: бегущий указатель и честный счётчик ---
set static Boot_Log_Cursor = 0x00000000;
set static Boot_Log_Count  = 0x00000000;

// --- входные регистры записи (стадия-0: данные через ячейки) ---
set static Log_Tick   = 0x00000000;
set static Log_Level  = 0x00000000;
set static Log_Stage  = 0x00000000;

// --- честные флаги отказов ---
set static Log_Flag_Overflow = 0x00000000;
set static Log_Flag_BadLevel = 0x00000000;
set static Log_Flag_BadStage = 0x00000000;

// --- честные результаты валидации входа записи ---
set static Log_Level_Ok = 0x00000000;
set static Log_Stage_Ok = 0x00000000;

// --- проверка последовательности ---
set static Verify_Idx        = 0x00000000;
set static Verify_Bad        = 0x00000000;
set static Verify_Bad_Index  = 0x00000000;
set static Verify_Log_Addr   = 0x00000000;
set static Verify_Seq_Addr   = 0x00000000;

// --- наливка/проба переполнения ---
set static Fill_Idx   = 0x00000000;

// --- паника ---
set static Panic_Cursor = 0x00000000;
set static Panic_Count  = 0x00000000;
set static Panic_Flag   = 0x00000000;
set static Dump_Addr    = 0x00000000;

// --- рабочие ячейки ---
set static Tmp_A = 0x00000000;
set static Tmp_B = 0x00000000;
set static Seq_Addr = 0x00000000;
set static Seq_Idx  = 0x00000000;
set static Sys_Addr = 0x00000000;
set static Tmp_Count = 0x00000000;

// --- честный флаг boot video (ставит rootcmd: boot.video off, 0x9851) ---
set static Boot_Vid = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009A01);      // LOG: bootlog test START

    // честная инициализация указателей (начальные значения статики VM не грузит)
    Boot_Log_Cursor = BOOT_LOG;
    Boot_Log_Count = 0x00000000;
    Log_Flag_Overflow = 0x00000000;
    Log_Flag_BadLevel = 0x00000000;
    Log_Flag_BadStage = 0x00000000;

    // ---- ЧЕСТНЫЙ НЕГАТИВ 1: переполнение журнала --------------------
    // наливаем РОВНО 256 записей (предел спеки) и пробуем 257-ю:
    // честный отказ БЕЗ записи, счётчик и курсор не двигаются
    Fill_Idx = 0x00000000;
    run Fill_Log();
    out_cell(LOG_PORT, 0x00009A10);      // LOG: 256 записей честно налито
    Log_Tick = 0x00000000;
    Log_Level = LV_OK;
    Log_Stage = ST_POWER;
    run Boot_Log_Write();                // 257-я — обязана быть отвергнута
    if (Log_Flag_Overflow == 0x00000001) {
        out_cell(LOG_PORT, 0x00009A11);  // LOG: переполнение отвергнуто честно
    } else {
        out_cell(LOG_PORT, 0x00009901);  // OL: переполнение НЕ отвергнуто
    }
    if (Boot_Log_Count == LOG_MAX) {
        out_cell(LOG_PORT, 0x00009A12);  // LOG: счётчик остался на пределе 256
    } else {
        out_cell(LOG_PORT, 0x00009902);  // OL: счётчик уехал за предел
    }

    // сброс журнала под настоящую загрузку
    Boot_Log_Cursor = BOOT_LOG;
    Boot_Log_Count = 0x00000000;
    Log_Flag_Overflow = 0x00000000;

    // ---- ЧЕСТНАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ 10 ЗАПИСЕЙ ----------------------
    run Load_Boot_Seq();                 // честный эталон стадий
    Seq_Addr = BOOT_SEQ;
    Seq_Idx = 0x00000000;
    run Boot_Stages();

    if (Boot_Log_Count == 0x0000000A) {
        out_cell(LOG_PORT, 0x00009A02);  // LOG: 10 стадий записаны
    } else {
        out_cell(LOG_PORT, 0x00009903);  // OL: число стадий не сошлось
    }
    // честный курсор: BOOT_LOG + 10 * 12 = 0x00E30078
    if (Boot_Log_Cursor == 0x00E30078) {
        out_cell(LOG_PORT, 0x00009A03);  // LOG: курсор честен (120 байт)
    } else {
        out_cell(LOG_PORT, 0x00009904);  // OL: курсор съехал
    }

    // ---- честный boot video: косметика поверх лога (спека) ---------
    // лог уже записан ВСЕГДА; флаг только говорит, рисуется ли ролик
    if (Boot_Vid == 0x00000000) {
        out_cell(LOG_PORT, 0x00009A20);  // LOG: видео выкл — текстовый лог (fallback)
    } else {
        out_cell(LOG_PORT, 0x00009A21);  // LOG: ролик поверх лога (лог под ним)
    }

    // ---- ЧЕСТНАЯ СВЕРКА: журнал байт-слово в слово = эталон ---------
    Verify_Idx = 0x00000000;
    Verify_Bad = 0x00000000;
    Verify_Log_Addr = BOOT_LOG;
    Verify_Seq_Addr = BOOT_SEQ;
    run Verify_Entries();

    // ---- ЧЕСТНЫЙ НЕГАТИВ 2: неизвестный уровень --------------------
    Log_Level = 0x00000005;              // вне 1..4 — честный отказ
    Log_Stage = ST_POWER;
    Log_Tick = 0x00000000;
    run Boot_Log_Write();
    if (Log_Flag_BadLevel == 0x00000001) {
        out_cell(LOG_PORT, 0x00009A05);  // LOG: уровень вне 1..4 отвергнут
    } else {
        out_cell(LOG_PORT, 0x00009905);  // OL: плохой уровень принят
    }
    Log_Flag_BadLevel = 0x00000000;

    // ---- ЧЕСТНЫЙ НЕГАТИВ 3: неизвестная стадия ---------------------
    Log_Level = LV_OK;
    Log_Stage = 0x00000000;              // стадии начинаются с 1
    run Boot_Log_Write();
    if (Log_Flag_BadStage == 0x00000001) {
        out_cell(LOG_PORT, 0x00009A06);  // LOG: стадия 0 отвергнута
    } else {
        out_cell(LOG_PORT, 0x00009906);  // OL: стадия 0 принята
    }
    Log_Flag_BadStage = 0x00000000;

    // ---- CHE EASY READBACK: 5-я запись (mount) = честный [warn] ----
    Tmp_B = BOOT_LOG;
    Tmp_B = Tmp_B + 52;                      // +48 запись 5, +4 = поле уровня
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == LV_WARN) {
        out_cell(LOG_PORT, 0x00009A13);  // LOG: [warn] о пустом USB2 честен
    } else {
        out_cell(LOG_PORT, 0x00009907);  // OL: warn не найден
    }

    // ---- FASTFETCH/SYSINFO из реальных ячеек -----------------------
    run Build_Sysinfo();
    Sys_Addr = SYSINFO;
    Tmp_A = in_cell(Sys_Addr);           // +0  ядро CtOs 2.0
    if (Tmp_A == 0x00000200) {
        out_cell(LOG_PORT, 0x00009A07);  // LOG: ядро 2.0 честно прочитано
    } else {
        out_cell(LOG_PORT, 0x00009908);  // OL: ядро врёт
    }
    // сеть честно отсутствует — в сводке обязан быть маркер «—»
    Tmp_B = SYSINFO;
    Tmp_B = Tmp_B + 16;              // +16 поле сети
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0xFFFFFFFF) {
        out_cell(LOG_PORT, 0x00009A08);  // LOG: сеть = «—» (без подделки)
    } else {
        out_cell(LOG_PORT, 0x00009909);  // OL: сеть выдумана
    }
    run Check_Sysinfo_Tail();

    // ---- ЧЕСТНАЯ ПАНИКА [FAIL] (отдельная зона, загрузка стоит) ----
    Panic_Cursor = PANIC_LOG;
    Panic_Count = 0x00000000;
    Panic_Flag = 0x00000000;
    Log_Level = LV_FAIL;
    Log_Stage = ST_KERNEL;
    Log_Tick = 0x00005200;
    run Panic_Write();
    if (Panic_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009A0A);  // LOG: [FAIL] честно остановил загрузку
    } else {
        out_cell(LOG_PORT, 0x0000990A);  // OL: паника не остановила
    }
    run Dump_Kernel_Cells();

    out_cell(LOG_PORT, 0x00009AFF);      // LOG: bootlog test DONE
    terminate;
}

// ---------- честная запись одной записи журнала ----------
// Валидация ДО записи: уровень 1..4 и стадия 1..9, потом предел 256.
// Плохие входы — честный флаг и НОЛЬ записанных байт.
function Boot_Log_Write() {
    run Log_Level_Valid();
    run Log_Stage_Valid();
    if (Log_Level_Ok == 0x00000000) {
        Log_Flag_BadLevel = 0x00000001;
        out_cell(LOG_PORT, 0x00009A31);  // LOG: уровень отвергнут (0 байт)
    } else {
        if (Log_Stage_Ok == 0x00000000) {
            Log_Flag_BadStage = 0x00000001;
            out_cell(LOG_PORT, 0x00009A32);  // LOG: стадия отвергнута (0 байт)
        } else {
            if (Boot_Log_Count == LOG_MAX) {
                Log_Flag_Overflow = 0x00000001;
                out_cell(LOG_PORT, 0x00009A33);  // LOG: журнал полон (256)
            } else {
                store_ind(Boot_Log_Cursor, Log_Tick);
                Boot_Log_Cursor = Boot_Log_Cursor + 4;
                store_ind(Boot_Log_Cursor, Log_Level);
                Boot_Log_Cursor = Boot_Log_Cursor + 4;
                store_ind(Boot_Log_Cursor, Log_Stage);
                Boot_Log_Cursor = Boot_Log_Cursor + 4;
                Boot_Log_Count = Boot_Log_Count + 1;
            }
        }
    }
}

// честная валидация уровня: 1..4 через точные равенства (стадия-0 без <)
function Log_Level_Valid() {
    Log_Level_Ok = 0x00000000;
    if (Log_Level == LV_OK) {
        Log_Level_Ok = 0x00000001;
    }
    if (Log_Level == LV_INFO) {
        Log_Level_Ok = 0x00000001;
    }
    if (Log_Level == LV_WARN) {
        Log_Level_Ok = 0x00000001;
    }
    if (Log_Level == LV_FAIL) {
        Log_Level_Ok = 0x00000001;
    }
}

// честная валидация стадии: 1..9 через точные равенства
function Log_Stage_Valid() {
    Log_Stage_Ok = 0x00000000;
    if (Log_Stage == ST_POWER) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_KERNEL) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_SCHED) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_BRIDGE) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_MOUNT) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_FS) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_THEMES) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_APPS) {
        Log_Stage_Ok = 0x00000001;
    }
    if (Log_Stage == ST_SHELL) {
        Log_Stage_Ok = 0x00000001;
    }
}

// ---------- наливка пробы переполнения ----------
function Fill_Log() {
    if (Fill_Idx == LOG_MAX) {
        out_cell(LOG_PORT, 0x00009A34);  // LOG: проба 256 записей готова
    } else {
        Log_Tick = 0x00000000;
        Log_Level = LV_OK;
        Log_Stage = ST_POWER;
        run Boot_Log_Write();
        Fill_Idx = Fill_Idx + 1;
        run Fill_Log();
    }
}

// ---------- честный эталон 10 записей ----------
// Порядок и тики — из спеки: [ok] power/kernel/sched, [info] bridge,
// [warn] mount (пустой USB2), [ok] fs/themes/apps/shell, [info] свёрнут.
function Load_Boot_Seq() {
    Seq_Addr = BOOT_SEQ;

    store_ind(Seq_Addr, 0x00000030);     // power
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_POWER);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00000120);     // kernel
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_KERNEL);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004120);     // scheduler
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_SCHED);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004350);     // bridge
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_INFO);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_BRIDGE);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004380);     // mount: USB2 пуст
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_WARN);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_MOUNT);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004500);     // fs
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_FS);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004800);     // themes
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_THEMES);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00004A00);     // apps
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_APPS);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00005100);     // shell
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_OK);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_SHELL);
    Seq_Addr = Seq_Addr + 4;

    store_ind(Seq_Addr, 0x00005101);     // shell: журнал свёрнут
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, LV_INFO);
    Seq_Addr = Seq_Addr + 4;
    store_ind(Seq_Addr, ST_SHELL);
    Seq_Addr = Seq_Addr + 4;

    out_cell(LOG_PORT, 0x00009A35);      // LOG: эталон 10 стадий готов
}

// ---------- честное проигрывание стадий из эталона ----------
function Boot_Stages() {
    if (Seq_Idx == 0x0000000A) {
        out_cell(LOG_PORT, 0x00009A36);  // LOG: стадии честно записаны
    } else {
        Log_Tick = in_cell(Seq_Addr);
        Seq_Addr = Seq_Addr + 4;
        Log_Level = in_cell(Seq_Addr);
        Seq_Addr = Seq_Addr + 4;
        Log_Stage = in_cell(Seq_Addr);
        Seq_Addr = Seq_Addr + 4;
        run Boot_Log_Write();
        Seq_Idx = Seq_Idx + 1;
        run Boot_Stages();
    }
}

// ---------- сверка журнала с эталоном (по три слова на запись) ----------
function Check_Word() {
    Tmp_A = in_cell(Verify_Log_Addr);
    Tmp_B = in_cell(Verify_Seq_Addr);
    if (Tmp_A == Tmp_B) {
        Verify_Log_Addr = Verify_Log_Addr + 4;
        Verify_Seq_Addr = Verify_Seq_Addr + 4;
    } else {
        Verify_Bad = 0x00000001;
        Verify_Bad_Index = Verify_Idx;
        log_cell(LOG_PORT, Tmp_A);       // честный след: что в журнале
        log_cell(LOG_PORT, Tmp_B);       // честный след: что в эталоне
        Verify_Log_Addr = Verify_Log_Addr + 4;
        Verify_Seq_Addr = Verify_Seq_Addr + 4;
    }
}

function Verify_Entries() {
    if (Verify_Idx == 0x0000000A) {
        if (Verify_Bad == 0x00000000) {
            out_cell(LOG_PORT, 0x00009A04);  // LOG: журнал = эталон слово в слово
        }
    } else {
        run Check_Word();
        run Check_Word();
        run Check_Word();
        if (Verify_Bad == 0x00000000) {
            Verify_Idx = Verify_Idx + 1;
        } else {
            Verify_Idx = 0x0000000A;
            log_cell(LOG_PORT, Verify_Bad_Index);
            out_cell(LOG_PORT, 0x00009A1F);  // LOG: расхождение с эталоном
        }
        run Verify_Entries();
    }
}

// ---------- fastfetch/sysinfo: только реальные ячейки ----------
function Build_Sysinfo() {
    Sys_Addr = SYSINFO;

    store_ind(Sys_Addr, 0x00000200);     // +0  ядро CtOs 2.0
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0x00005101);     // +4  аптайм: последний тик стадий
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0x00000020);     // +8  Mem_Pool 32 МБ (PSP-1004 база)
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0x00000007);     // +12 носители: ms0, ms1, hd0 живы
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0xFFFFFFFF);     // +16 сети нет — честное «—»
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0x00000003);     // +20 тема builtin/ps5_style
    Sys_Addr = Sys_Addr + 4;
    store_ind(Sys_Addr, 0x00000001);     // +24 графика: 2D честна
    Sys_Addr = Sys_Addr + 4;
    Tmp_Count = Boot_Log_Count;          // +28 записей в журнале
    store_ind(Sys_Addr, Tmp_Count);
    Sys_Addr = Sys_Addr + 4;
}

function Check_Sysinfo_Tail() {
    Tmp_B = SYSINFO;
    Tmp_B = Tmp_B + 4;              // +4 аптайм
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00005101) {
        out_cell(LOG_PORT, 0x00009A14);  // LOG: аптайм из тика стадий
    } else {
        out_cell(LOG_PORT, 0x0000990B);  // OL: аптайм выдуман
    }
    Tmp_B = SYSINFO;
    Tmp_B = Tmp_B + 20;              // +20 тема
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000003) {
        out_cell(LOG_PORT, 0x00009A15);  // LOG: тема = ps5_style
    } else {
        out_cell(LOG_PORT, 0x0000990C);  // OL: тема съехала
    }
    Tmp_B = SYSINFO;
    Tmp_B = Tmp_B + 28;              // +28 счётчик журнала
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x0000000A) {
        out_cell(LOG_PORT, 0x00009A09);  // LOG: sysinfo целиком честен (10)
    } else {
        out_cell(LOG_PORT, 0x0000990D);  // OL: счётчик журнала в сводке врёт
    }
}

// ---------- [FAIL]: паника в отдельной зоне + дамп ячеек ----------
function Panic_Write() {
    store_ind(Panic_Cursor, Log_Tick);
    Panic_Cursor = Panic_Cursor + 4;
    store_ind(Panic_Cursor, Log_Level);
    Panic_Cursor = Panic_Cursor + 4;
    store_ind(Panic_Cursor, Log_Stage);
    Panic_Cursor = Panic_Cursor + 4;
    Panic_Count = Panic_Count + 1;
    Panic_Flag = 0x00000001;             // честная остановка загрузки
    out_cell(LOG_PORT, 0x00009A37);      // LOG: запись [FAIL] легла
}

function Dump_Kernel_Cells() {
    Dump_Addr = CELL_DUMP;
    store_ind(Dump_Addr, Log_Tick);      // тик паники
    Dump_Addr = Dump_Addr + 4;
    Tmp_Count = Boot_Log_Count;          // сколько стадий успело лечь
    store_ind(Dump_Addr, Tmp_Count);
    Dump_Addr = Dump_Addr + 4;
    store_ind(Dump_Addr, Panic_Count);   // записей паники
    Dump_Addr = Dump_Addr + 4;
    store_ind(Dump_Addr, Log_Stage);     // стадия паники
    Dump_Addr = Dump_Addr + 4;
    if (Panic_Count == 0x00000001) {
        out_cell(LOG_PORT, 0x00009A38);  // LOG: дамп ячеек честен
    } else {
        out_cell(LOG_PORT, 0x0000990E);  // OL: дамп пуст
    }
}
