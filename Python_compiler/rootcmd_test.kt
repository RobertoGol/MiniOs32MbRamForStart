// ===================================================================
// СПРИНТ ROOTCMD: честные скрытые параметры + журнал ядра
// Файл: rootcmd_test.kt | Язык: KINII (подмножество стадии-0)
//
// По CtOs/terminal/TERMINAL_SPEC.md:
//   * rootcmd: <параметр> <значение> — скрытые настройки владельца;
//   * rootcmd: help и rootcmd без параметров НЕ выдают списка
//     скрытых команд — только подсказка «доступ к секретам ограничен»;
//   * каждый вызов rootcmd пишется в журнал ядра: старое и новое
//     значение (ROOT_LOG, пары слов);
//   * ring0.guard off — честный эффект: охраняемая ячейка честно
//     становится записываемой (до off — честный отказ записи);
//   * boot.video off — честный флаг загрузочного ролика;
//   * mem.pool 32 — честный лимит пула ОЗУ;
//   * theme.force builtin/ark4_dark — честная интеграция спринта
//     builtin: встроенный пресет применяется честно;
//   * незнакомый параметр — честный отказ (и запись в журнал).
//
// Карта памяти:
//   0x00E2D000  Guard_Word   честная охрана Ring 0 (1 =guard on)
//   0x00E2D004  Boot_Vid     честный флаг загрузочного ролика
//   0x00E2D008  Mem_Pool     честный лимит пула ОЗУ в МБ
//   0x00E2D0F0  Guard_Target охраняемая ячейка (тест записи)
//   0x00E2D100  ROOT_LOG     журнал rootcmd: пары (старое, новое)
//
// Честные ключи (Key_Idx): 0 = help/пусто (подсказка), 1 = ring0.guard,
// 2 = boot.video, 3 = mem.pool, 4 = theme.force, прочее = отказ.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT      0x3F0050C0
#define: GUARD_WORD    0x00E2D000
#define: BOOT_VID      0x00E2D004
#define: MEM_POOL      0x00E2D008
#define: GUARD_TARGET  0x00E2D0F0
#define: ROOT_LOG      0x00E2D100
#define: GUARD_VAL     0x00005BEE     // честное слово для теста записи
#define: THEM_MAGIC    0x5448454D     // честная 'THEM' подпись темы
#define: LOG_END       0x00E2D128     // ROOT_LOG + 5 записей по 8 байт
#define: PRESET_0      0x00E2C100     // честная база xmb_classic
#define: PRESET_1      0x00E2C200     // честный ark4_dark
#define: SHELL_PAL     0x00E2B000     // честная палитра оболочки

set static Key_Idx      = 0x00000000;  // честный ключ rootcmd
set static New_Val      = 0x00000000;  // честное новое значение
set static Old_Val      = 0x00000000;  // честное старое значение (журнал)
set static Guard_Run    = 0x00000000;  // честная копия Guard_Word для теста
set static Log_Run      = 0x00000000;  // честный бегунок журнала
set static Tmp_Read     = 0x00000000;
set static Tmp_Write    = 0x00000000;
set static Tgt_Addr     = 0x00000000;  // честный адрес цели записи
set static Custom_Has   = 0x00000000;  // честный флаг custom (всегда нет)
set static Builtin_Idx  = 0x00000000;  // честный builtin-запрос темы
set static Apply_Slot   = 0x00000000;  // честный слот применяемой темы
set static Src_Col      = 0x00000000;  // честный адрес цвета темы
set static Base_Col     = 0x00000000;  // честный адрес цвета базы
set static Pal_Dst      = 0x00000000;  // честный адрес цвета палитры
set static Scan_Idx     = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009800);      // LOG: rootcmd START

    run Init_Presets();

    // честная инициализация системы: guard on, ролик есть, пул 64 МБ
    Tgt_Addr = GUARD_WORD;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = BOOT_VID;
    store_ind(Tgt_Addr, Tmp_Write);
    Tmp_Write = 0x00000040;              // честные 64 МБ
    Tgt_Addr = MEM_POOL;
    store_ind(Tgt_Addr, Tmp_Write);
    Log_Run = ROOT_LOG;

    // --- rootcmd без параметров: честная подсказка, БЕЗ списка ---
    Key_Idx = 0x00000000;
    run Root_Set();                      // честно: 0x9810 «доступ ограничен»

    // --- охраняемая запись ДО off: честный отказ ---
    run Write_Guarded();                 // честно: отказ 0x9820

    // --- rootcmd: ring0.guard off — честный эффект ---
    Key_Idx = 0x00000001;
    New_Val = 0x00000000;
    run Root_Set();                      // журнал: (1, 0)
    run Write_Guarded();                 // честно: запись прошла 0x9830

    // --- rootcmd: boot.video off ---
    Key_Idx = 0x00000002;
    New_Val = 0x00000000;
    run Root_Set();                      // журнал: (1, 0)

    // --- rootcmd: mem.pool 32 ---
    Key_Idx = 0x00000003;
    New_Val = 0x00000020;
    run Root_Set();                      // журнал: (64, 32)

    // --- rootcmd: theme.force builtin/ark4_dark ---
    Key_Idx = 0x00000004;
    New_Val = 0x00000001;                // честный индекс ark4_dark
    run Root_Set();                      // журнал: (0, 1), ark4 применён

    // --- незнакомый параметр: честный отказ + честная запись в журнал ---
    Key_Idx = 0x00000005;
    New_Val = 0x00000000;
    run Root_Set();                      // отказ 0x9840, журнал-маркер

    // --- честные верификации ---
    Tgt_Addr = GUARD_TARGET;
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == GUARD_VAL) {
        out_cell(LOG_PORT, 0x00009850);  // LOG: охраняемая ячейка честно записана
    } else {
        out_cell(LOG_PORT, 0x00009890);  // честная паника: guard не снялся
    }
    Tgt_Addr = BOOT_VID;
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == 0x00000000) {
        out_cell(LOG_PORT, 0x00009851);  // LOG: ролик честно выключен
    } else {
        out_cell(LOG_PORT, 0x00009890);
    }
    Tgt_Addr = MEM_POOL;
    Tmp_Read = in_cell(Tgt_Addr);
    if (Tmp_Read == 0x00000020) {
        out_cell(LOG_PORT, 0x00009852);  // LOG: пул честно 32 МБ
    } else {
        out_cell(LOG_PORT, 0x00009890);
    }
    Pal_Dst = SHELL_PAL;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x000000F0) {
        out_cell(LOG_PORT, 0x00009853);  // LOG: ark4 честно применился
    } else {
        out_cell(LOG_PORT, 0x00009890);
    }
    Tmp_Read = Log_Run;
    if (Tmp_Read == LOG_END) {
        out_cell(LOG_PORT, 0x00009860);  // LOG: журнал честно 5 записей
    } else {
        out_cell(LOG_PORT, 0x00009890);
    }

    out_cell(LOG_PORT, 0x000098FF);      // LOG: rootcmd DONE
    terminate;
}

// ---------- честная инициализация builtin-пресетов ----------
function Init_Presets() {
    // PRESET_0 xmb_classic: база наследования, все 6 цветов
    Tgt_Addr = PRESET_0;
    Tmp_Write = THEM_MAGIC;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 4;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 8;
    Tmp_Write = 0x00002048;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 12;
    Tmp_Write = 0x0000FFFF;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 16;
    Tmp_Write = 0x0000B0B8;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 20;
    Tmp_Write = 0x00001848;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 24;
    Tmp_Write = 0x00000A18;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 28;
    Tmp_Write = 0x0000DEE6;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_0 + 32;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);

    // PRESET_1 ark4_dark: оранжевый акцент 0xF0, тёмные тона
    Tgt_Addr = PRESET_1;
    Tmp_Write = THEM_MAGIC;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 4;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 8;
    Tmp_Write = 0x000000F0;              // честный оранжевый акцент
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 12;
    Tmp_Write = 0x0000E8E8;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 16;
    Tmp_Write = 0x00008888;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 20;
    Tmp_Write = 0x00001028;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 24;
    Tmp_Write = 0x00000814;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 28;
    Tmp_Write = 0x00002020;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = PRESET_1 + 32;
    Tmp_Write = 0x00000001;
    store_ind(Tgt_Addr, Tmp_Write);
}

// ---------- честная подсказка/исполнение rootcmd ----------
// Key_Idx/New_Val — честный запрос. Каждый вызов честно в журнале.
function Root_Set() {
    if (Key_Idx == 0x00000000) {
        // честная подсказка: списка скрытых команд НЕ выдаётся
        out_cell(LOG_PORT, 0x00009810);
    } else {
        if (Key_Idx == 0x00000001) {
            Tgt_Addr = GUARD_WORD;
            Tmp_Read = in_cell(Tgt_Addr);
            Old_Val = Tmp_Read;
            store_ind(Tgt_Addr, New_Val);
            run Root_Log();
        } else {
            if (Key_Idx == 0x00000002) {
                Tgt_Addr = BOOT_VID;
                Tmp_Read = in_cell(Tgt_Addr);
                Old_Val = Tmp_Read;
                store_ind(Tgt_Addr, New_Val);
                run Root_Log();
            } else {
                if (Key_Idx == 0x00000003) {
                    Tgt_Addr = MEM_POOL;
                    Tmp_Read = in_cell(Tgt_Addr);
                    Old_Val = Tmp_Read;
                    store_ind(Tgt_Addr, New_Val);
                    run Root_Log();
                } else {
                    if (Key_Idx == 0x00000004) {
                        // честная тема: old = текущий builtin (0 = нет)
                        Old_Val = Builtin_Idx;
                        Builtin_Idx = New_Val;
                        run Apply_Builtin();     // честное применение пресета
                        run Root_Log();
                    } else {
                        // честный отказ незнакомого параметра
                        out_cell(LOG_PORT, 0x00009840);
                        Old_Val = 0x0000E000;    // честный маркер отказа
                        New_Val = 0x0000E000;
                        run Root_Log();
                    }
                }
            }
        }
    }
}

// ---------- честный журнал rootcmd: пара (старое, новое) ----------
function Root_Log() {
    store_ind(Log_Run, Old_Val);
    Tgt_Addr = Log_Run + 4;
    store_ind(Tgt_Addr, New_Val);
    Log_Run = Log_Run + 8;
}

// ---------- честная охраняемая запись ----------
// Guard_Word = 1 — запись в Guard_Target честно отказана.
// После честного ring0.guard off — запись честно проходит.
function Write_Guarded() {
    Tgt_Addr = GUARD_WORD;
    Guard_Run = in_cell(Tgt_Addr);
    if (Guard_Run == 0x00000001) {
        out_cell(LOG_PORT, 0x00009820);  // честный отказ: guard стоит
    } else {
        Tgt_Addr = GUARD_TARGET;
        store_ind(Tgt_Addr, GUARD_VAL);  // честная запись под снимленным guard
        out_cell(LOG_PORT, 0x00009830);
    }
}

// ---------- честное применение builtin-пресета (из спринта builtin) ----------
function Apply_Builtin() {
    if (Builtin_Idx == 0x00000001) {
        Apply_Slot = 0x00E2C200;         // честный ark4_dark
        run Normalize_Theme();
    } else {
        out_cell(LOG_PORT, 0x00009750);  // честный отказ прочих пресетов
    }
}

function Normalize_Theme() {
    Src_Col = Apply_Slot + 8;
    Base_Col = 0x00E2C100 + 8;           // честная база xmb_classic
    Pal_Dst = 0x00E2B000;
    Scan_Idx = 0x00000000;
    run Norm_Loop();
}

function Norm_Loop() {
    if (Scan_Idx == 0x00000006) {
        // честная база: 6 цветов честно в палитре
    } else {
        Tmp_Read = in_cell(Src_Col);
        if (Tmp_Read == 0x00000000) {
            Tmp_Write = in_cell(Base_Col);    // честное наследование
        } else {
            Tmp_Write = Tmp_Read;
        }
        store_ind(Pal_Dst, Tmp_Write);
        Src_Col = Src_Col + 4;
        Base_Col = Base_Col + 4;
        Pal_Dst = Pal_Dst + 4;
        Scan_Idx = Scan_Idx + 1;
        run Norm_Loop();
    }
}
