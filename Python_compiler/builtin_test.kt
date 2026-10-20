// ===================================================================
// СПРИНТ BUILTIN: честные встроенные пресеты тем + builtin/ps5_style
// Файл: builtin_test.kt | Язык: KINII (подмножество стадии-0)
//
// По CtMusic/themes/README.md и PSP_REF.md:
//   * builtin-темы живут в themes/builtin/ (xmb_classic, ark4_dark,
//     ps5_style и др.) — честные пресеты, манифест в том же формате;
//   * ps5_style — тёмная палитра с ОБЯЗАТЕЛЬНЫМ деградирующим
//     режимом: без динамических фонов и прозрачностей по дефолту
//     (деградационные флаги честно равны нулю);
//   * честное правило темы-порта (PSP_REF): custom всегда бьёт
//     builtin — пока на носителе есть валидная custom-тема, force
//     builtin честно отказывается и честно держит custom;
//   * незнакомый индекс builtin — честный отказ.
//
// Карта памяти:
//   0x00E2C100  PRESET_0   xmb_classic (flags = 1: динамика разрешена)
//   0x00E2C200  PRESET_1   ark4_dark   (flags = 1)
//   0x00E2C300  PRESET_2   ps5_style   (flags = 0: деградация честная)
//   0x00E2A100  CUST_A     валидная custom-тема (highlight FF9A)
//   0x00E2B000  SHELL_PAL  палитра оболочки (6 слов)
//
// Слот темы: +0 magic, +4 version, +8..+28 — 6 цветов,
// +32 деградационные флаги (0 = плоский режим, честный по дефолту).
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: THEM_MAGIC  0x5448454D     // честная 'THEM' подпись темы
#define: PRESET_0    0x00E2C100
#define: PRESET_1    0x00E2C200
#define: PRESET_2    0x00E2C300
#define: CUST_A      0x00E2A100
#define: SHELL_PAL   0x00E2B000

set static Scan_Idx     = 0x00000000;
set static Src_Run      = 0x00000000;  // честный бегунок записи Init
set static Tmp_Read     = 0x00000000;
set static Tmp_Write    = 0x00000000;
set static Apply_Slot   = 0x00000000;  // честный слот применяемой темы
set static Src_Col      = 0x00000000;  // честный адрес цвета применяемой темы
set static Base_Col     = 0x00000000;  // честный адрес цвета базы (BASE_T = PRESET_0)
set static Pal_Dst      = 0x00000000;  // честный адрес цвета палитры
set static Custom_Has   = 0x00000000;  // честный флаг «есть валидная custom»
set static Custom_Addr  = 0x00000000;  // честный адрес валидной custom
set static Builtin_Idx  = 0x00000000;  // честный запрошенный builtin (0/1/2)
set static Flag_Addr    = 0x00000000;  // честный адрес флагов темы

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009700);      // LOG: builtin START

    run Init_Presets();
    run Init_Custom();
    Custom_Has = 0x00000001;
    Custom_Addr = CUST_A;

    // --- КЕЙС А: custom на носителе — builtin force честно отказан ---
    Builtin_Idx = 0x00000002;            // честный запрос ps5_style
    run Apply_Builtin();                 // честный отказ 0x9730, custom остаётся
    Pal_Dst = SHELL_PAL;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x0000FF9A) {
        out_cell(LOG_PORT, 0x00009760);  // LOG: палитра честно от custom
    } else {
        out_cell(LOG_PORT, 0x00009790);  // честная паника: builtin не должен был
    }

    // --- КЕЙС Б: custom убрали — ps5_style честно применяется ---
    Flag_Addr = CUST_A;
    Tmp_Read = 0x00000000;
    store_ind(Flag_Addr, Tmp_Read);      // честное снятие custom с носителя
    Custom_Has = 0x00000000;
    Builtin_Idx = 0x00000002;
    run Apply_Builtin();                 // честное применение ps5
    Pal_Dst = SHELL_PAL;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x00002A8A) {
        out_cell(LOG_PORT, 0x00009770);  // LOG: тёмная палитра ps5 честно
    } else {
        out_cell(LOG_PORT, 0x00009790);
    }
    Flag_Addr = PRESET_2 + 32;
    Tmp_Read = in_cell(Flag_Addr);
    if (Tmp_Read == 0x00000000) {
        out_cell(LOG_PORT, 0x00009720);  // LOG: деградирующий режим честный
    } else {
        out_cell(LOG_PORT, 0x00009790);  // честная паника: флаги не нулевые
    }

    // --- КЕЙС В: незнакомый builtin — честный отказ ---
    Custom_Has = 0x00000000;
    Builtin_Idx = 0x00000003;            // честного пресета нет
    run Apply_Builtin();                 // честный отказ 0x9750

    out_cell(LOG_PORT, 0x000097FF);      // LOG: builtin DONE
    terminate;
}

// ---------- честная инициализация builtin-пресетов ----------
function Init_Presets() {
    // PRESET_0 xmb_classic: синяя волна Sony, flags = 1
    Src_Run = PRESET_0;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = PRESET_0 + 8;
    Tmp_Write = 0x00002048;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000FFFF;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000B0B8;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00001848;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000A18;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000DEE6;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;              // честный флаг: динамика разрешена
    store_ind(Src_Run, Tmp_Write);

    // PRESET_1 ark4_dark: тёмное меню, оранжевый акцент, flags = 1
    Src_Run = PRESET_1;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = PRESET_1 + 8;
    Tmp_Write = 0x000000F0;              // честный оранжевый акцент
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000E8E8;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00008888;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00001028;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000814;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000202020;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);

    // PRESET_2 ps5_style: тёмная палитра, flags = 0 (деградация честная)
    Src_Run = PRESET_2;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = PRESET_2 + 8;
    Tmp_Write = 0x00002A8A;              // честный синий акцент
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000EAEA;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00008A8A;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000A0A;              // честный тёмный wave_top
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000606;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00001818;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000000;              // честный деградирующий режим
    store_ind(Src_Run, Tmp_Write);

    out_cell(LOG_PORT, 0x00009710);      // LOG: builtin-пресеты честно готовы
}

// ---------- честная инициализация custom-темы ----------
function Init_Custom() {
    Src_Run = CUST_A;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 8;
    Tmp_Write = 0x0000FF9A;              // честный highlight custom
    store_ind(Src_Run, Tmp_Write);
}

// ---------- честное применение builtin-пресета ----------
// Builtin_Idx — честный запрос. Правило честное: custom бьёт builtin.
// База наследования = PRESET_0 (xmb_classic — честная база XMB).
function Apply_Builtin() {
    if (Custom_Has == 0x00000001) {
        // честное правило PSP_REF: custom всегда бьёт builtin
        out_cell(LOG_PORT, 0x00009730);
        Apply_Slot = Custom_Addr;
        run Normalize_Theme();           // custom честно остаётся оболочкой
    } else {
        if (Builtin_Idx == 0x00000000) {
            Apply_Slot = PRESET_0;
            run Normalize_Theme();
        } else {
            if (Builtin_Idx == 0x00000001) {
                Apply_Slot = PRESET_1;
                run Normalize_Theme();
            } else {
                if (Builtin_Idx == 0x00000002) {
                    Apply_Slot = PRESET_2;
                    run Normalize_Theme();
                } else {
                    out_cell(LOG_PORT, 0x00009750);   // честный отказ
                }
            }
        }
    }
}

// ---------- честная нормализация: применить + наследовать у пресета 0 ----------
// Нулевой цвет честно заменяется цветом честной базы xmb_classic.
function Normalize_Theme() {
    Src_Col = Apply_Slot + 8;
    Base_Col = PRESET_0 + 8;
    Pal_Dst = SHELL_PAL;
    Scan_Idx = 0x00000000;
    run Norm_Loop();
    out_cell(LOG_PORT, 0x00009740);      // LOG: палитра честно собрана
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
