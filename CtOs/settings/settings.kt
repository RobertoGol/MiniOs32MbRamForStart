// ===================================================================
// TKT-028 — SETTINGS: 12 подменю, честные метки, реальные параметры
// Файл: CtOs/settings/settings.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке: CtOs/settings/SETTINGS_SPEC.md + TERMINAL_SPEC (rootcmd)
//
// ЧЕСТНЫЕ ПРАВИЛА (не нарушаем):
//   * 12 подменю — ровно как в спеке; ничего не «тихо скрываем»;
//   * [limited R3700] — пункт ОСТАЁТСЯ в списке, но честно помечен
//     битом в маске подменю (не выкинут, не подделан);
//   * обычные параметры правятся из меню и `set`; СЕКРЕТНЫЕ
//     (ring0.guard / fs.scan.delay / fake.plus / debug) в белом списке
//     меню ОТСУТСТВУЮТ — Settings их честно отвергает (только rootcmd);
//   * значение вне честного диапазона — отказ ДО записи (0 байт);
//   * «Fake Plus» и «Debug Settings» на розничной — честно НЕТ;
//   * Terminal — приложение сразу под Settings (соседний id).
//
// Карта памяти:
//   0x00E2D004  Boot_Vid      (общий с rootcmd — один источник правды)
//   0x00E2D008  Mem_Pool      (общий с rootcmd)
//   0x00E2B000  SHELL_PAL     акцент оболочки (применённая тема)
//   0x00E40000  SETTINGS      значения: theme/governor/thermal/nohz/
//                             nickname/video/audio
//   0x00E42000  SUBMENUS      12 записей по 12 Б (id, items, limited)
//   0x00E43000  MENU_APPS     порядок: settings, terminal (соседние)
//   0x00E44000  PARAMS        честный белый список: 9 id по 4 Б
//   0x00E45000  Custom_Pres 1 = есть кастомная тема (приоритет custom)
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT     0x3F0050C0
#define: BOOT_VID     0x00E2D004
#define: MEM_POOL     0x00E2D008
#define: SHELL_PAL    0x00E2B000
#define: SETTINGS     0x00E40000
#define: SUBMENUS     0x00E42000
#define: MENU_APPS    0x00E43000
#define: PARAMS       0x00E44000
#define: CUSTOM_PRES  0x00E45000

// offsets внутри SETTINGS
#define: OFF_THEME    0x00000000
#define: OFF_GOV      0x00000004
#define: OFF_THERM    0x00000008
#define: OFF_NOHZ     0x0000000C
#define: OFF_NICK     0x00000010
#define: OFF_VIDEO    0x00000014
#define: OFF_AUDIO    0x00000018

// честные id подменю (порядок спеки)
#define: SM_SYS       0x00000001
#define: SM_UPDATE    0x00000002
#define: SM_DISPLAY   0x00000003
#define: SM_SOUND     0x00000004
#define: SM_NETWORK   0x00000005
#define: SM_DEVICES   0x00000006
#define: SM_ACCOUNT   0x00000007
#define: SM_POWER     0x00000008
#define: SM_DATETIME  0x00000009
#define: SM_APPEAR    0x0000000A
#define: SM_GAMEPLAY  0x0000000B
#define: SM_DISC      0x0000000C

// честные id параметров
#define: P_THEME     0x00000001
#define: P_GOV       0x00000002
#define: P_THERM     0x00000003
#define: P_NOHZ      0x00000004
#define: P_BOOTVID   0x00000005
#define: P_MEMPOOL   0x00000006
#define: P_VIDEO     0x00000007
#define: P_AUDIO     0x00000008
#define: P_NICK      0x00000009

// секретные id — В МЕНЮ ИХ НЕТ (только rootcmd)
#define: P_GUARD     0x00000020
#define: P_SCANDELAY 0x00000021
#define: P_FAKEPLUS  0x00000023
#define: P_DEBUG     0x00000024

// честные акценты тем (4 темы из ТЗ)
#define: ACC_CLASSIC 0x00002048
#define: ACC_ARK4    0x000000F0
#define: ACC_GEND3    0x00000F80
#define: ACC_LEOPARD  0x00000A18
#define: ACC_CUSTOM  0x0000C0DE

// --- входые регистры Settings_Set ---
set static Param_Id  = 0x00000000;
set static New_Val   = 0x00000000;

// --- честные результаты ---
set static Param_Found = 0x00000000;
set static Val_Ok      = 0x00000000;
set static Set_Result  = 0x00000000;  // 0 ok, 1 нет в меню, 2 значение вне диапазона
set static Eth_Refused = 0x00000000;  // 1 = бандл-значение «[limited R3700]»

// --- рабочие ---
set static Tmp_A    = 0x00000000;
set static Tmp_B    = 0x00000000;
set static Ptr      = 0x00000000;
set static Idx      = 0x00000000;
set static Pal_Val  = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009B01);      // LOG: settings test START

    run Init_Store();
    run Init_Submenus();
    run Init_Params();
    run Init_Menu();

    // ---- 12 подменю: счёт и курсор --------------------------------
    Ptr = SUBMENUS;
    Idx = 0x00000000;
    run Check_Submenus();

    // ---- честные метки [limited R3700] (пункт НЕ выкинут) ---------
    Tmp_B = SUBMENUS;
    Tmp_B = Tmp_B + 32;                  // запись 3 (DISPLAY), поле маски
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000018) {
        out_cell(LOG_PORT, 0x00009B13);  // LOG: DISPLAY: 1440p/4K помечены
    } else {
        out_cell(LOG_PORT, 0x000099B3);
    }
    Tmp_B = SUBMENUS;
    Tmp_B = Tmp_B + 92;                  // запись 8 (POWER), поле маски
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        out_cell(LOG_PORT, 0x00009B17);  // LOG: POWER: батарея помечена
    } else {
        out_cell(LOG_PORT, 0x000099B7);
    }

    // ---- Terminal сразу под Settings ------------------------------
    Ptr = MENU_APPS;
    Tmp_A = in_cell(Ptr);
    Ptr = Ptr + 4;
    Tmp_B = in_cell(Ptr);
    Tmp_A = Tmp_A + 1;                  // Terminal обязан быть соседним id
    if (Tmp_B == Tmp_A) {
        out_cell(LOG_PORT, 0x00009B14);  // LOG: Terminal соседний под Settings
    } else {
        out_cell(LOG_PORT, 0x000099B4);
    }

    // ---- обычные настройки: честное применение -------------------
    Param_Id = P_THEME;
    New_Val = 0x00000003;                // Mac OS X Leopard
    run Settings_Set();
    Tmp_B = SETTINGS;
    Tmp_A = in_cell(Tmp_B);
    Ptr = SHELL_PAL;
    Pal_Val = in_cell(Ptr);
    if (Tmp_A == 0x00000003) {
        if (Pal_Val == ACC_LEOPARD) {
            out_cell(LOG_PORT, 0x00009B15);  // LOG: тема Leopard честно применена
        } else {
            out_cell(LOG_PORT, 0x000099B5);
        }
    } else {
        out_cell(LOG_PORT, 0x000099B5);
    }

    // ---- приоритет custom > builtin (правило TKT-024) ------------
    Tmp_A = 0x00000001;
    Tmp_B = CUSTOM_PRES;
    store_ind(Tmp_B, Tmp_A);             // кастомка есть
    Param_Id = P_THEME;
    New_Val = 0x00000001;                // просим builtin ark4_dark
    run Settings_Set();
    Ptr = SHELL_PAL;
    Pal_Val = in_cell(Ptr);
    if (Pal_Val == ACC_CUSTOM) {
        out_cell(LOG_PORT, 0x00009B16);  // LOG: custom честно бьёт builtin
    } else {
        out_cell(LOG_PORT, 0x000099B6);
    }
    Tmp_A = 0x00000000;
    Tmp_B = CUSTOM_PRES;
    store_ind(Tmp_B, Tmp_A);             // снова чисто
    // честная проверка: после снятия кастомки builtin снова честно применяется
    Param_Id = P_THEME;
    New_Val = 0x00000003;                // Leopard
    run Settings_Set();
    Ptr = SHELL_PAL;
    Pal_Val = in_cell(Ptr);
    if (Pal_Val == ACC_LEOPARD) {
        out_cell(LOG_PORT, 0x00009B27);  // LOG: без custom builtin снова виден
    } else {
        out_cell(LOG_PORT, 0x000099C7);
    }

    // ---- энергосбережение: governor/thermal/No-HZ ----------------
    Param_Id = P_GOV;
    New_Val = 0x00000002;                // максимум (честный допустимый)
    run Settings_Set();
    Param_Id = P_THERM;
    New_Val = 0x00000001;                // спад частоты
    run Settings_Set();
    Param_Id = P_NOHZ;
    New_Val = 0x00000000;                // No-HZ выключен
    run Settings_Set();
    Param_Id = P_NOHZ;
    New_Val = 0x00000001;                // и честно включён обратно
    run Settings_Set();
    Ptr = SETTINGS;
    Ptr = Ptr + 4;
    Tmp_A = in_cell(Ptr);                // governor
    Ptr = SETTINGS;
    Ptr = Ptr + 8;
    Tmp_B = in_cell(Ptr);                // thermal
    if (Tmp_A == 0x00000002) {
        if (Tmp_B == 0x00000001) {
            out_cell(LOG_PORT, 0x00009B19);  // LOG: governor/thermal честны
        } else {
            out_cell(LOG_PORT, 0x000099B9);
        }
    } else {
        out_cell(LOG_PORT, 0x000099B9);
    }

    // ---- память: mem.pool 32 (общая ячейка rootcmd) --------------
    Param_Id = P_MEMPOOL;
    New_Val = 0x00000020;
    run Settings_Set();
    Ptr = MEM_POOL;
    Tmp_A = in_cell(Ptr);
    if (Tmp_A == 0x00000020) {
        out_cell(LOG_PORT, 0x00009B18);  // LOG: mem.pool 32 МБ принят
    } else {
        out_cell(LOG_PORT, 0x000099B8);
    }

    // ---- видео 720p принято --------------------------------------
    Param_Id = P_VIDEO;
    New_Val = 0x00000001;
    run Settings_Set();
    Ptr = SETTINGS;
    Ptr = Ptr + 20;
    Tmp_A = in_cell(Ptr);
    if (Tmp_A == 0x00000001) {
        out_cell(LOG_PORT, 0x00009B1A);  // LOG: 720p честно принят
    } else {
        out_cell(LOG_PORT, 0x000099BA);
    }

    // ---- ЧЕСТНЫЕ НЕГАТИВЫ ----------------------------------------
    // 1) секрет через меню: ring0.guard — отказано, меню его не знает
    Param_Id = P_GUARD;
    New_Val = 0x00000000;
    run Settings_Set();
    if (Set_Result == 0x00000001) {
        out_cell(LOG_PORT, 0x00009B20);  // LOG: секрет честно отвергнут
    } else {
        out_cell(LOG_PORT, 0x000099C0);
    }
    // 2) Fake Plus — честно НЕТ
    Param_Id = P_FAKEPLUS;
    New_Val = 0x00000001;
    run Settings_Set();
    if (Set_Result == 0x00000001) {
        out_cell(LOG_PORT, 0x00009B21);  // LOG: Fake Plus честно отсутствует
    } else {
        out_cell(LOG_PORT, 0x000099C1);
    }
    // 3) Debug Settings — на розничной честно НЕТ
    Param_Id = P_DEBUG;
    New_Val = 0x00000001;
    run Settings_Set();
    if (Set_Result == 0x00000001) {
        out_cell(LOG_PORT, 0x00009B22);  // LOG: Debug честно отсутствует
    } else {
        out_cell(LOG_PORT, 0x000099C2);
    }
    // 4) governor = 3 — вне диапазона, значение НЕ меняется
    Param_Id = P_GOV;
    New_Val = 0x00000003;
    run Settings_Set();
    Ptr = SETTINGS;
    Ptr = Ptr + 4;
    Tmp_A = in_cell(Ptr);
    if (Set_Result == 0x00000002) {
        if (Tmp_A == 0x00000002) {
            out_cell(LOG_PORT, 0x00009B23);  // LOG: governor 3 отвергнут, 2 цел
        } else {
            out_cell(LOG_PORT, 0x000099C3);
        }
    } else {
        out_cell(LOG_PORT, 0x000099C3);
    }
    // 5) 1440p — честная метка [limited R3700], отказ
    Param_Id = P_VIDEO;
    New_Val = 0x00000003;
    run Settings_Set();
    if (Set_Result == 0x00000002) {
        out_cell(LOG_PORT, 0x00009B24);  // LOG: 1440p = [limited R3700]
    } else {
        out_cell(LOG_PORT, 0x000099C4);
    }
    // 6) 3D-звук — честная метка [limited R3700], отказ
    Param_Id = P_AUDIO;
    New_Val = 0x00000003;
    run Settings_Set();
    if (Set_Result == 0x00000002) {
        out_cell(LOG_PORT, 0x00009B25);  // LOG: 3D-звук = [limited R3700]
    } else {
        out_cell(LOG_PORT, 0x000099C5);
    }
    // 7) mem.pool 33 — не поддержано честно (только 16/32/64)
    Param_Id = P_MEMPOOL;
    New_Val = 0x00000021;
    run Settings_Set();
    Ptr = MEM_POOL;
    Tmp_A = in_cell(Ptr);
    if (Tmp_A == 0x00000020) {
        out_cell(LOG_PORT, 0x00009B26);  // LOG: mem.pool 33 отвергнут, 32 цел
    } else {
        out_cell(LOG_PORT, 0x000099C6);
    }

    out_cell(LOG_PORT, 0x00009BFF);      // LOG: settings test DONE
    terminate;
}

// ---------- честные значения по умолчанию ----------
function Init_Store() {
    Ptr = SETTINGS;
    Tmp_A = 0x00000000;                  // theme = xmb_classic
    store_ind(Ptr, Tmp_A);
    Ptr = Ptr + 4;
    store_ind(Ptr, Tmp_A);               // governor = idle
    Ptr = Ptr + 4;
    store_ind(Ptr, Tmp_A);               // thermal = предупреждение
    Ptr = Ptr + 4;
    Tmp_A = 0x00000001;
    store_ind(Ptr, Tmp_A);               // No-HZ = вкл (правило железа)
    Ptr = Ptr + 4;
    Tmp_A = 0x00000000;
    store_ind(Ptr, Tmp_A);               // псевдоним не задан = «—»
    Ptr = Ptr + 4;
    store_ind(Ptr, Tmp_A);               // видео 480p
    Ptr = Ptr + 4;
    store_ind(Ptr, Tmp_A);               // звук stereo
    Ptr = Ptr + 4;

    Ptr = BOOT_VID;
    Tmp_A = 0x00000001;
    store_ind(Ptr, Tmp_A);               // ролик есть (как в rootcmd)
    Ptr = MEM_POOL;
    Tmp_A = 0x00000040;
    store_ind(Ptr, Tmp_A);               // пул 64 МБ по умолчанию
    Ptr = SHELL_PAL;
    Tmp_A = ACC_CLASSIC;
    store_ind(Ptr, Tmp_A);               // база xmb_classic
    Ptr = CUSTOM_PRES;
    Tmp_A = 0x00000000;
    store_ind(Ptr, Tmp_A);               // кастомных тем нет
}

// ---------- 12 подменю: id, число пунктов, маска [limited R3700] ----------
// Честно: маска НЕ уменьшает число пунктов — пункт остаётся, но помечен.
function Init_Submenus() {
    Ptr = SUBMENUS;

    store_ind(Ptr, SM_SYS);              // 1 Система и память
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000014);          // 20 пунктов
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000002);          // батарея: источник БП
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_UPDATE);           // 2 Обновление
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000003);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_DISPLAY);          // 3 Экран/видео
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000009);          // 9 пунктов остаются все
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000018);          // 1440p/4K помечены
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_SOUND);            // 4 Звук
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x0000000C);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000008);          // 3D-звук помечен
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_NETWORK);          // 5 Сеть
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000007);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_DEVICES);          // 6 Устройства
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000008);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000080);          // VR помечен
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_ACCOUNT);          // 7 Учётка/безопасность
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x0000000A);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_POWER);            // 8 Энергосбережение
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000008);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // батарея помечена
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_DATETIME);         // 9 Дата/время
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000005);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_APPEAR);           // 10 Оформление/темы
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000006);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_GAMEPLAY);         // 11 Игровой процесс
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000007);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    store_ind(Ptr, SM_DISC);             // 12 Диски BD/DVD
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000006);
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000000);
    Ptr = Ptr + 4;

    out_cell(LOG_PORT, 0x00009B10);      // LOG: 12 подменю честно залиты
}

// ---------- белый список обычных параметров (секретов тут НЕТ) ----------
function Init_Params() {
    Ptr = PARAMS;
    store_ind(Ptr, P_THEME);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_GOV);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_THERM);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_NOHZ);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_BOOTVID);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_MEMPOOL);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_VIDEO);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_AUDIO);
    Ptr = Ptr + 4;
    store_ind(Ptr, P_NICK);
    Ptr = Ptr + 4;
    out_cell(LOG_PORT, 0x00009B11);      // LOG: белый список = 9 параметров
}

// ---------- порядок приложений: Settings, затем Terminal ----------
function Init_Menu() {
    Ptr = MENU_APPS;
    store_ind(Ptr, 0x00000001);          // Settings
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000002);          // Terminal — сразу под ним
    Ptr = Ptr + 4;
}

// ---------- проверка 12 подменю ----------
function Check_Submenus() {
    if (Idx == 0x0000000C) {
        // курсор обязан стоять на SUBMENUS + 12*12 = +144
        if (Ptr == 0x00E42090) {
            out_cell(LOG_PORT, 0x00009B12);  // LOG: 12 подменю, курсор честен
        } else {
            out_cell(LOG_PORT, 0x000099B2);
        }
    } else {
        Tmp_A = in_cell(Ptr);            // id подменю
        Tmp_B = Idx + 1;                 // честный ожидаемый id 1..12
        if (Tmp_A == Tmp_B) {
            Ptr = Ptr + 12;              // следующая запись
            Idx = Idx + 1;
            run Check_Submenus();
        } else {
            out_cell(LOG_PORT, 0x000099B1);  // честный брак: порядок id
        }
    }
}

// ---------- честная установка обычного параметра ----------
function Settings_Set() {
    Set_Result = 0x00000000;
    Eth_Refused = 0x00000000;
    run Whitelist_Check();
    if (Param_Found == 0x00000000) {
        Set_Result = 0x00000001;         // нет в меню: секрет/несуществующий
        out_cell(LOG_PORT, 0x00009950);
    } else {
        run Apply_Value();
    }
}

// честный обход белого списка (9 id)
function Whitelist_Check() {
    Param_Found = 0x00000000;
    Ptr = PARAMS;
    Idx = 0x00000000;
    run Whitelist_Loop();
}

function Whitelist_Loop() {
    if (Idx == 0x00000009) {
        // конец списка — Param_Found уже честен
    } else {
        Tmp_A = in_cell(Ptr);
        if (Tmp_A == Param_Id) {
            Param_Found = 0x00000001;
        } else {
            Ptr = Ptr + 4;
            Idx = Idx + 1;
            run Whitelist_Loop();
        }
    }
}

// ---------- честное применение значения ----------
function Apply_Value() {
    if (Param_Id == P_THEME) {
        run V_Theme();
    }
    if (Param_Id == P_GOV) {
        run V_Governor();
    }
    if (Param_Id == P_THERM) {
        run V_Thermal();
    }
    if (Param_Id == P_NOHZ) {
        run V_Nohz();
    }
    if (Param_Id == P_BOOTVID) {
        run V_BootVid();
    }
    if (Param_Id == P_MEMPOOL) {
        run V_MemPool();
    }
    if (Param_Id == P_VIDEO) {
        run V_Video();
    }
    if (Param_Id == P_AUDIO) {
        run V_Audio();
    }
    if (Param_Id == P_NICK) {
        run V_Nick();
    }
}

// общий честный вердикт по диапазону: 0..Max (Max мал, проверяем равенствами)
function V_Theme() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Set_Theme_Classic();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Set_Theme_Ark4();
    }
    if (New_Val == 0x00000002) {
        Set_Result = 0x00000000;
        run Set_Theme_GenD3();
    }
    if (New_Val == 0x00000003) {
        Set_Result = 0x00000000;
        run Set_Theme_Leopard();
    }
}

function Store_Theme() {
    Ptr = SETTINGS;
    store_ind(Ptr, Pal_Val);             // theme id
    Ptr = SHELL_PAL;
    store_ind(Ptr, Tmp_A);               // акцент (или custom)
}

function Set_Theme_Classic() {
    Pal_Val = 0x00000000;
    Tmp_A = ACC_CLASSIC;
    run Theme_Apply();
}
function Set_Theme_Ark4() {
    Pal_Val = 0x00000001;
    Tmp_A = ACC_ARK4;
    run Theme_Apply();
}
function Set_Theme_GenD3() {
    Pal_Val = 0x00000002;
    Tmp_A = ACC_GEND3;
    run Theme_Apply();
}
function Set_Theme_Leopard() {
    Pal_Val = 0x00000003;
    Tmp_A = ACC_LEOPARD;
    run Theme_Apply();
}

// честное правило TKT-024: custom всегда бьёт builtin
function Theme_Apply() {
    Ptr = CUSTOM_PRES;
    Tmp_B = in_cell(Ptr);
    if (Tmp_B == 0x00000001) {
        Tmp_A = ACC_CUSTOM;              // кастомка сильнее
    }
    run Store_Theme();
}

function V_Governor() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Gov();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Gov();
    }
    if (New_Val == 0x00000002) {
        Set_Result = 0x00000000;
        run Store_Gov();
    }
}

function Store_Gov() {
    Ptr = SETTINGS;
    Ptr = Ptr + 4;
    store_ind(Ptr, New_Val);
}

function V_Thermal() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Therm();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Therm();
    }
    if (New_Val == 0x00000002) {
        Set_Result = 0x00000000;
        run Store_Therm();
    }
}

function Store_Therm() {
    Ptr = SETTINGS;
    Ptr = Ptr + 8;
    store_ind(Ptr, New_Val);
}

function V_Nohz() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Nohz();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Nohz();
    }
}

function Store_Nohz() {
    Ptr = SETTINGS;
    Ptr = Ptr + 12;
    store_ind(Ptr, New_Val);
}

function V_BootVid() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_BootVid();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_BootVid();
    }
}

function Store_BootVid() {
    Ptr = BOOT_VID;
    store_ind(Ptr, New_Val);
}

function V_MemPool() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000010) {
        Set_Result = 0x00000000;
        run Store_MemPool();
    }
    if (New_Val == 0x00000020) {
        Set_Result = 0x00000000;
        run Store_MemPool();
    }
    if (New_Val == 0x00000040) {
        Set_Result = 0x00000000;
        run Store_MemPool();
    }
}

function Store_MemPool() {
    Ptr = MEM_POOL;
    store_ind(Ptr, New_Val);
}

function V_Video() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Video();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Video();
    }
    if (New_Val == 0x00000002) {
        Set_Result = 0x00000000;
        run Store_Video();
    }
    if (New_Val == 0x00000003) {
        Eth_Refused = 0x00000001;    // 1440p/4K/8K = [limited R3700]
    }
}

function Store_Video() {
    Ptr = SETTINGS;
    Ptr = Ptr + 20;
    store_ind(Ptr, New_Val);
}

function V_Audio() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Audio();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Audio();
    }
    if (New_Val == 0x00000002) {
        Set_Result = 0x00000000;
        run Store_Audio();
    }
    if (New_Val == 0x00000003) {
        Eth_Refused = 0x00000001;    // 3D-звук/Atmos = [limited R3700]
    }
}

function Store_Audio() {
    Ptr = SETTINGS;
    Ptr = Ptr + 24;
    store_ind(Ptr, New_Val);
}

function V_Nick() {
    Set_Result = 0x00000002;         // честный отказ по умолчанию: вне диапазона
    if (New_Val == 0x00000000) {
        Set_Result = 0x00000000;
        run Store_Nick();
    }
    if (New_Val == 0x00000001) {
        Set_Result = 0x00000000;
        run Store_Nick();
    }
}

function Store_Nick() {
    Ptr = SETTINGS;
    Ptr = Ptr + 16;
    store_ind(Ptr, New_Val);
}
