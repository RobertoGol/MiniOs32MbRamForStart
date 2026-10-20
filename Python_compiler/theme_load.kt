// ===================================================================
// СПРИНТ ТЕМЫ: честная загрузка манифеста темы (тема theme.json)
// Файл: theme_load.kt | Язык: KINII (подмножество стадии-0)
//
// По контракту CtMusic/themes/README.md:
//   * «скинул — привязалось»: скан custom-тем, каждая валидная
//     добавляется в список, битая (magic не тот) честно помечается
//     invalid и пропускается — оболочка не падает;
//   * манифест темы: magic, version, 6 цветов (highlight, text,
//     text_dim, wave_top, wave_bottom, info_panel);
//   * базовое наследование честно: нулевой цвет честно берётся
//     у базовой темы;
//   * применение честно: палитра оболочки SHELL_PAL честно
//     заполняется с честным наследованием.
//
// Честное уточнение: JSON-парсер в стадию-0 не входит; манифест
// честно представлен бинарной структурой (тот же набор полей).
//
// Карта памяти:
//   0x00E2A000  BASE_T     базовая тема: magic + version + 6 цветов
//   0x00E2A100  CUST_A     custom A: magic, version, 2 цвета, остальное 0
//   0x00E2A200  CUST_B     custom B: битый magic (честный invalid)
//   0x00E2A300  CUST_C     custom C: валидная (все 6 цветов честно)
//   0x00E2B000  SHELL_PAL  честная палитра оболочки (6 слов)
//
// Слот темы (32 байта): +0 magic, +4 version, с +8 по +28 — 6 цветов:
//   +8 highlight, +12 text, +16 text_dim, +20 wave_top,
//   +24 wave_bottom, +28 info_panel.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: THEM_MAGIC  0x5448454D     // честная 'THEM' подпись темы
#define: BASE_T      0x00E2A000
#define: CUST_A      0x00E2A100
#define: CUST_B      0x00E2A200
#define: CUST_C      0x00E2A300
#define: SHELL_PAL   0x00E2B000

set static Scan_Idx     = 0x00000000;
set static Slot_Run     = 0x00000000;  // честный бегунок сканируемых слотов
set static Ver_Addr     = 0x00000000;  // честный адрес поля version
set static Src_Run      = 0x00000000;  // честный бегунок записи Init
set static Tmp_Read     = 0x00000000;
set static Tmp_Write    = 0x00000000;
set static Valid_Count  = 0x00000000;  // честный счётчик валидных custom
set static Bad_Count    = 0x00000000;  // честный счётчик битых custom
set static Apply_Slot   = 0x00000000;  // честный слот применяемой темы
set static Src_Col      = 0x00000000;  // честный адрес цвета применяемой темы
set static Base_Col     = 0x00000000;  // честный адрес цвета базы
set static Pal_Dst      = 0x00000000;  // честный адрес цвета палитры

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009500);      // LOG: theme load START

    run Init_Themes();

    // честная загрузка и применение БАЗЫ (системная тема)
    Apply_Slot = BASE_T;
    run Normalize_Theme();               // честно: палитра = база

    // честный скан custom: «скинул — привязалось»
    Slot_Run = CUST_A;
    run Scan_Custom();
    Slot_Run = CUST_B;
    run Scan_Custom();
    Slot_Run = CUST_C;
    run Scan_Custom();

    // честный отчёт счётчиков: 2 валидных, 1 битая
    log_cell(LOG_PORT, Valid_Count);
    log_cell(LOG_PORT, Bad_Count);

    // честное применение custom A с честным наследованием у базы
    Apply_Slot = CUST_A;
    run Normalize_Theme();

    // честная верификация палитры: цвет A, цвет A, цвет базы
    Pal_Dst = SHELL_PAL;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x0000FF9A) {
        out_cell(LOG_PORT, 0x00009580);  // LOG: highlight честно от A
    } else {
        out_cell(LOG_PORT, 0x00009590);  // честная паника: палитра врёт
    }
    Pal_Dst = SHELL_PAL + 12;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x00002E2E) {
        out_cell(LOG_PORT, 0x00009581);  // LOG: wave_top честно от A
    } else {
        out_cell(LOG_PORT, 0x00009590);
    }
    Pal_Dst = SHELL_PAL + 20;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x00002020) {
        out_cell(LOG_PORT, 0x00009582);  // LOG: info_panel честно от базы
    } else {
        out_cell(LOG_PORT, 0x00009590);
    }

    // честное применение custom C (полная тема) и честный контроль
    Apply_Slot = CUST_C;
    run Normalize_Theme();
    Pal_Dst = SHELL_PAL + 20;
    Tmp_Read = in_cell(Pal_Dst);
    if (Tmp_Read == 0x0000BBCC) {
        out_cell(LOG_PORT, 0x00009583);  // LOG: полная тема честно применилась
    } else {
        out_cell(LOG_PORT, 0x00009590);
    }

    out_cell(LOG_PORT, 0x000095FF);      // LOG: theme load DONE
    terminate;
}

// ---------- честная инициализация тем на носителе ----------
function Init_Themes() {
    // БАЗА: все 6 цветов честно стоят
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

    // CUSTOM A: magic, version и 2 честных цвета; остальные честные нули
    // (пусто = 0 = честно унаследовать у базы)
    Src_Run = CUST_A;
    Tmp_Write = THEM_MAGIC;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = Src_Run + 4;
    Tmp_Write = 0x00000001;
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 8;
    Tmp_Write = 0x0000FF9A;              // честный highlight A
    store_ind(Src_Run, Tmp_Write);
    Src_Run = CUST_A + 20;
    Tmp_Write = 0x00002E2E;              // честный wave_top A
    store_ind(Src_Run, Tmp_Write);

    // CUSTOM B: честный битый magic (инвалид честный)
    Src_Run = CUST_B;
    Tmp_Write = 0x00000000;
    store_ind(Src_Run, Tmp_Write);

    // CUSTOM C: валидная честная, все 6 цветов своим числом
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
    Tmp_Write = 0x0000BBCC;              // честный info_panel C
    store_ind(Src_Run, Tmp_Write);

    out_cell(LOG_PORT, 0x00009510);      // LOG: темы честно на носителе
}

// ---------- честный скан custom-темы: «скинул — привязалось» ----------
// Slot_Run — адрес слота. Валидная = magic честный И version = 1.
function Scan_Custom() {
    Tmp_Read = in_cell(Slot_Run);
    if (Tmp_Read == THEM_MAGIC) {
        Ver_Addr = Slot_Run + 4;
        Tmp_Read = in_cell(Ver_Addr);
        if (Tmp_Read == 0x00000001) {
            Valid_Count = Valid_Count + 1;
            out_cell(LOG_PORT, 0x00009530);   // LOG: тема валидна, привязана
        } else {
            Bad_Count = Bad_Count + 1;
            out_cell(LOG_PORT, 0x00009540);   // LOG: версия не поддержана
        }
    } else {
        Bad_Count = Bad_Count + 1;
        out_cell(LOG_PORT, 0x00009540);       // LOG: битая тема честно пропущена
    }
}

// ---------- честная нормализация: применить + наследовать у базы ----------
// Apply_Slot — честный слот применяемой темы. Нулевой цвет честно
// заменяется честным цветом базы. Результат честно в SHELL_PAL.
function Normalize_Theme() {
    Src_Col = Apply_Slot + 8;
    Base_Col = BASE_T + 8;
    Pal_Dst = SHELL_PAL;
    Scan_Idx = 0x00000000;
    run Norm_Loop();
    out_cell(LOG_PORT, 0x00009550);      // LOG: палитра честно собрана
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
