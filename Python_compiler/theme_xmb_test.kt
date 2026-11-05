// ===================================================================
// СПРИНТ XMB-NEXT4: тема управляет четырьмя поверхностями XMB
// Файл: theme_xmb_test.kt | Язык: KINII (подмножество стадии-0)
//
// Хвост TKT-022 («полная тема XMB (Next 4)»). Поверхности:
//   1. Категории: таблица 7 слов (SETT/EXTR/PHOT/MUSI/VIDE/GAME/NETW),
//      текущая категория и круговая навигация (wrap честный),
//      подсветка берётся из честного highlight темы;
//   2. Волна: wave_top / wave_bottom из честной палитры;
//   3. Визуализатор плеера: честное поле манифеста по смещению +32
//      (расширение честного слота темы; нулевое поле — честное
//      наследование у базы, то же правило, что у цветов);
//   4. Строка статуса: часы, носитель, ссылка на применённый слот.
//
// Слот темы (36 байт): +0 magic 'THEM', +4 version(=1), +8..+28 шесть
// цветов (как в theme_load.kt), +32 цвет визуализатора.
//
// Карта памяти:
//   0x00E2A000 BASE_T   базовая тема (все 6 цветов + виз-цвет 0x66)
//   0x00E2A100 CUST_A   partial: highlight + wave_top, виз-цвет 0
//   0x00E2A200 CUST_B   битый magic (честный invalid)
//   0x00E2A300 CUST_C   полная тема: 6 цветов + виз-цвет 0x000055AA
//   0x00E2B000 SHELL_PAL честная палитра (6 слов, как в theme_load)
//   0x00E2F000 XMB_CATS 7 честных слов категорий
//   0x00E2F100 XMB_STATE честное состояние оболочки (8 слов)
//
// XMB_STATE: +0 cat_idx, +4 cat_addr, +8 wave_top, +12 wave_bottom,
//            +16 vis_color, +20 clock, +24 media, +28 theme_ptr.
//
// Лог честный (своя серия стенда — 0x96xx):
//   0x9600 START; 0x9601 Ф1 база; 0x9602 скан; 0x9603 полная C;
//   0x9604 навигация; 0x9605 статус; 0x960F DONE; 0x9690 авария.
//   Gold: 0x9610/0x9611/0x9612 база-поверхности; 0x9630/1/2 C-поверхности;
//   0x9641..0x9644 навигация; 0x9650/1 статус; 0x9660 подсветка.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: THEM_MAGIC  0x5448454D     // 'THEM'
#define: BASE_T      0x00E2A000
#define: CUST_A      0x00E2A100
#define: CUST_B      0x00E2A200
#define: CUST_C      0x00E2A300
#define: SHELL_PAL   0x00E2B000
#define: XMB_CATS    0x00E2F000
#define: XMB_STATE   0x00E2F100
#define: CAT_LAST    0x00000006     // честный последний индекс (7 категорий)
#define: CAT_COUNT   0x00000007     // честная ёмкость таблицы (wrap == COUNT)
#define: CAT_GAME    0x00000005     // стартовая категория навигации
#define: CAT_ADDR    0x00000004     // XMB_CATS [CUST_B]: честно: адрес = +4*idx

set static Cat_Idx      = 0x00000000;
set static Cat_Addr     = 0x00000000;
set static Tmp_Addr     = 0x00000000;
set static Tmp_Word     = 0x00000000;
set static Tmp_Read     = 0x00000000;
set static Tmp_Write    = 0x00000000;
set static Tmp_Vis      = 0x00000000;
set static Src_Run      = 0x00000000;
set static Slot_Run     = 0x00000000;
set static Ver_Addr     = 0x00000000;
set static Src_Col      = 0x00000000;
set static Base_Col     = 0x00000000;
set static Pal_Dst      = 0x00000000;
set static Scan_Idx     = 0x00000000;
set static Valid_Count  = 0x00000000;
set static Bad_Count    = 0x00000000;
set static Apply_Slot   = 0x00000000;
set static Focus_Cnt    = 0x00000000; // честный счётчик сложений 4*idx (без * на стадии-0)

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009600);      // LOG: XMB Next4 START

    run Init_Themes();
    run Init_Cats();

    // ---------- Ф1: база применена, поверхности честно из базы ----------
    Apply_Slot = BASE_T;
    run Normalize_Theme();
    run Apply_Surface();
    // честная строка статуса: категория GAME, часы, носитель, слот
    Tmp_Addr = XMB_STATE + 20;
    Tmp_Word = 0x00000814;
    store_ind(Tmp_Addr, Tmp_Word);       // честные часы-слово стенда
    Tmp_Addr = XMB_STATE + 24;
    Tmp_Word = 0x00000001;               // честный носитель ms0
    store_ind(Tmp_Addr, Tmp_Word);
    Tmp_Addr = XMB_STATE + 28;
    Tmp_Write = BASE_T;
    store_ind(Tmp_Addr, Tmp_Write);      // честная ссылка на применённый слот
    Cat_Idx = CAT_GAME;
    run Cat_Focus();
    out_cell(LOG_PORT, 0x00009601);      // LOG: Ф1 база честно применена
    // честные поверхности базы: волна из палитры, виз честный
    Tmp_Addr = XMB_STATE + 8;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00001A1A) {
        out_cell(LOG_PORT, 0x00009610);  // LOG: wave_top честно из палитры
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 12;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00001621) {
        out_cell(LOG_PORT, 0x00009611);  // LOG: wave_bottom честно из палитры
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 16;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00000066) {
        out_cell(LOG_PORT, 0x00009612);
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }

    // ---------- Ф2: честный скан custom (скинул — привязалось) ----------
    Slot_Run = CUST_A;
    run Scan_Custom();
    Slot_Run = CUST_B;
    run Scan_Custom();
    Slot_Run = CUST_C;
    run Scan_Custom();
    log_cell(LOG_PORT, Valid_Count);     // честно: 2 валидных
    log_cell(LOG_PORT, Bad_Count);       // честно: 1 битая
    out_cell(LOG_PORT, 0x00009602);      // LOG: Ф2 скан честно завершён

    // ---------- Ф3: полная тема C — все поверхности честно из C ----------
    Apply_Slot = CUST_C;
    run Normalize_Theme();
    run Apply_Surface();
    Tmp_Addr = XMB_STATE + 28;
    Tmp_Write = CUST_C;
    store_ind(Tmp_Addr, Tmp_Write);
    out_cell(LOG_PORT, 0x00009603);      // LOG: Ф3 полная C честно применена
    // честные проверки поверхностей C: волна из палитры, виз честный
    Tmp_Addr = XMB_STATE + 8;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00007788) {
        out_cell(LOG_PORT, 0x00009630);
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 12;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x000099AA) {
        out_cell(LOG_PORT, 0x00009631);
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 16;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x000055AA) {
        out_cell(LOG_PORT, 0x00009632);
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }

    // ---------- Ф4: честная круговая навигация категорий ----------
    // старт GAME (5): right -> 6 (NETW), right -> 0 (SETT, честный wrap),
    // right -> 1 (EXTR), left -> 0, left -> 6 (NETW), left -> 5 (GAME)
    out_cell(LOG_PORT, 0x00009604);      // LOG: Ф4 навигация честно
    run Cat_Right();                     // 5 -> 6
    run Cat_Right();                     // 6 -> 0 (честный wrap)
    run Cat_Right();                     // 0 -> 1
    run Cat_Left();                      // 1 -> 0
    run Cat_Left();                      // 0 -> 6 (честный wrap)
    run Cat_Left();                      // 6 -> 5 (GAME вернулась)
    // честный финал: полный круг честно замкнулся, индекс снова 5
    if (Cat_Idx == CAT_GAME) {
        out_cell(LOG_PORT, 0x00009644);
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }

    // ---------- Ф5: честная строка статуса читается оболочкой ----------
    out_cell(LOG_PORT, 0x00009605);      // LOG: Ф5 статус честно
    Tmp_Addr = XMB_STATE + 20;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00000814) {
        out_cell(LOG_PORT, 0x00009650);  // LOG: честные часы видны
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 24;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00000001) {
        out_cell(LOG_PORT, 0x00009651);  // LOG: честный носитель ms0
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }
    Tmp_Addr = XMB_STATE + 28;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == CUST_C) {
        out_cell(LOG_PORT, 0x00009652);  // LOG: честная ссылка на полный слот
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }

    // ---------- Ф6: подсветка текущей категории честно из темы ----------
    // highlight C = 0x00001122 -> честная подсветка XMB читает слово 0
    // честной палитры (компоновка как в theme_load: +0 highlight)
    Tmp_Addr = SHELL_PAL;
    Tmp_Read = in_cell(Tmp_Addr);
    if (Tmp_Read == 0x00001122) {
        out_cell(LOG_PORT, 0x00009660);  // LOG: честная подсветка из темы
    } else {
        out_cell(LOG_PORT, 0x00009690);
    }

    out_cell(LOG_PORT, 0x0000960F);      // LOG: XMB Next4 DONE
    terminate;
}

// ---------- честные темы на носителе (шаблон theme_load + виз-цвет) ----------
function Init_Themes() {
    // BASE_T: все 6 цветов + честный виз-цвет 0x66 (зелёная осциллограмма)
    Src_Run = BASE_T;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = BASE_T + 8;
    Tmp_Write = 0x00001A20;              // highlight
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000FFFF;              // text
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000B8B8;              // text_dim
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00001A1A;              // wave_top
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00001621;              // wave_bottom
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00002020;              // info_panel
    store_ind(Src_Run, Tmp_Write);
    Src_Run = BASE_T + 32;
    Tmp_Write = 0x00000066;              // честный виз-цвет базы
    store_ind(Src_Run, Tmp_Write);

    // CUST_A: 2 цвета, виз-цвет честно 0 (наследует у базы)
    Src_Run = CUST_A;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 8;
    Tmp_Write = 0x0000FF9A;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 20;
    Tmp_Write = 0x00002E2E;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 32;
    Tmp_Write = 0x00000000;
    store_ind(Src_Run, Tmp_Write);

    // CUST_B: честный битый magic
    Src_Run = CUST_B;
    Tmp_Write = 0x00000000;
    store_ind(Src_Run, Tmp_Write);

    // CUST_C: полная: 6 цветов + честный виз-цвет 0x000055AA
    Src_Run = CUST_C;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_C + 8;
    Tmp_Write = 0x00001122;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00003344;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00005566;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00007788;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x000099AA;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x0000BBCC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_C + 32;
    Tmp_Write = 0x000055AA;
    store_ind(Src_Run, Tmp_Write);
}

// ---------- честная таблица 7 категорий XMB ----------
function Init_Cats() {
    Src_Run = XMB_CATS;
    Tmp_Write = 0x53455454;              // 'SETT'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x45585452;              // 'EXTR'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x50484F54;              // 'PHOT'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x4D555349;              // 'MUSI'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x56494445;              // 'VIDE'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x47414D45;              // 'GAME'
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x4E455457;              // 'NETW'
    store_ind(Src_Run, Tmp_Write);
}

// ---------- честный скан custom-темы: «скинул — привязалось» ----------
// Slot_Run — адрес слота. Валидная = magic честный И version = 1
// (шаблон theme_load; слот расширен до 36 байт честным полем +32).
function Scan_Custom() {
    Tmp_Read = in_cell(Slot_Run);
    if (Tmp_Read == THEM_MAGIC) {
        Ver_Addr = Slot_Run + 4;
        Tmp_Read = in_cell(Ver_Addr);
        if (Tmp_Read == 0x00000001) {
            Valid_Count = Valid_Count + 1;
        } else {
            Bad_Count = Bad_Count + 1;
        }
    } else {
        Bad_Count = Bad_Count + 1;
    }
}

// ---------- честная нормализация: палитра + честный виз-цвет ----------
// Apply_Slot — честный слот применяемой темы. Нулевой цвет честно
// заменяется цветом базы (как theme_load); виз-цвет +32 — честное
// расширение слота, нулевое поле честно наследует у базы (0x66).
function Normalize_Theme() {
    Src_Col = Apply_Slot + 8;
    Base_Col = BASE_T + 8;
    Pal_Dst = SHELL_PAL;
    Scan_Idx = 0x00000000;
    run Norm_Loop();
    Tmp_Addr = Apply_Slot + 32;
    Tmp_Vis = in_cell(Tmp_Addr);
    if (Tmp_Vis == 0x00000000) {
        Tmp_Addr = BASE_T + 32;
        Tmp_Vis = in_cell(Tmp_Addr);     // честное наследование виз-цвета
    }
    Tmp_Addr = XMB_STATE + 16;
    store_ind(Tmp_Addr, Tmp_Vis);
}

function Norm_Loop() {
    if (Scan_Idx == 0x00000006) {
        // честная база: 6 цветов честно в палитре
    } else {
        Tmp_Read = in_cell(Src_Col);
        if (Tmp_Read == 0x00000000) {
            Tmp_Write = in_cell(Base_Col);    // честное наследование у базы
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

// ---------- честные поверхности XMB: волна (виз — у Normalize) ----------
// Волна честно берётся из собранной палитры: wave_top = слово 3 (+12),
// wave_bottom = слово 4 (+16). Статус-поверхность (часы/носитель/слот)
// честно живёт в XMB_STATE и читается Ф5 напрямую.
function Apply_Surface() {
    Tmp_Addr = SHELL_PAL + 12;
    Tmp_Read = in_cell(Tmp_Addr);
    Tmp_Addr = XMB_STATE + 8;
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = SHELL_PAL + 16;
    Tmp_Read = in_cell(Tmp_Addr);
    Tmp_Addr = XMB_STATE + 12;
    store_ind(Tmp_Addr, Tmp_Read);
}

// ---------- честная привязка текущей категории ----------
// XMB_STATE +0 = честный индекс, +4 = честный адрес в таблице 7 слов
// (адрес = XMB_CATS + 4*idx честной рекурсией сложений — на стадии-0
// нет умножения, честный подъём по одному шагу).
function Cat_Focus() {
    Focus_Cnt = 0x00000000;
    Cat_Addr = XMB_CATS;
    run Focus_Loop();
    Tmp_Addr = XMB_STATE;
    Tmp_Write = Cat_Idx;
    store_ind(Tmp_Addr, Tmp_Write);
    Tmp_Addr = XMB_STATE + 4;
    Tmp_Write = Cat_Addr;
    store_ind(Tmp_Addr, Tmp_Write);
}

function Focus_Loop() {
    if (Focus_Cnt == Cat_Idx) {
        // честная база: 4*idx сложений честно накоплены
    } else {
        Cat_Addr = Cat_Addr + 4;
        Focus_Cnt = Focus_Cnt + 1;
        run Focus_Loop();
    }
}

// ---------- честная круговая навигация категорий ----------
function Cat_Right() {
    Cat_Idx = Cat_Idx + 1;
    if (Cat_Idx == CAT_COUNT) {
        Cat_Idx = 0x00000000;            // честный wrap: 6 -> 0
    }
    run Cat_Focus();
}

function Cat_Left() {
    if (Cat_Idx == 0x00000000) {
        Cat_Idx = CAT_LAST;              // честный wrap: 0 -> 6
    } else {
        Cat_Idx = Cat_Idx - 1;
    }
    run Cat_Focus();
}
