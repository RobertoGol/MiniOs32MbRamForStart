// ===================================================================
// terminal_fetch.kt — терминал CtOS: честные `fetch` и `sysinfo`
// Файл: CtOs/terminal/terminal_fetch.kt | Язык: KINII (стадия-0)
// Тикет: TKT-053_terminal_fetch_sysinfo
//
// ЧЕСТНО: это ТОЛЬКО вывод сводки. Источник один — SYSINFO 0x00E31000,
// те же 8 слов, что собирает загрузка (TKT-026, Build_Sysinfo):
//   +0  версия CtOs         +16 сеть (0xFFFFFFFF = «—», данных нет)
//   +4  аптайм (тики)       +20 тема
//   +8  пул ОЗУ, МБ         +24 видео
//   +12 носители (биты)     +28 записей журнала загрузки
//
// Правила:
//   * fetch   — компактная сводка: 6 слов (+0..+20);
//   * sysinfo — полный экран: все 8 слов;
//   * данных нет -> честное «—» (0xFFFFFFFF), не подделка;
//   * только по требованию: ни одного фонового чтения (не polling);
//     каждая команда = ровно один честный проход по снимку.
// ===================================================================
#core: CtOs_Old
#target: ARM32

#define: LOG_PORT  0x3F0050C0
#define: SYSINFO   0x00E31000     // общая честная точка правды (TKT-026)
#define: OUT       0x00E80000     // снимок для вывода (8 слов)
#define: STATE     0x00E80100     // счётчики: проходы, строки, слова

#define: ROWS_FETCH   0x00000006
#define: ROWS_SYSINFO 0x00000008

#define: DASH        0xFFFFFFFF   // честное «—»

// коды отказов терминала
#define: E_CMD       0x00007130

// теги команд (4 ASCII LE)
#define: TAG_FETCH2  0x43544546     // 'FETC'
#define: TAG_SYSINFO 0x49535953     // 'SYSI'
#define: TAG_SYSTEM  0x54535953     // 'SYST' (алиас systeminfo)
#define: TAG_ECHO    0x4F484345     // 'ECHO' — не команда CtOS (честный отказ)

set static Ptr        = 0x00000000;
set static Tmp_A      = 0x00000000;
set static Tmp_B      = 0x00000000;
set static Tmp_C      = 0x00000000;
set static Idx        = 0x00000000;
set static Cmd_Tag    = 0x00000000;
set static Rows       = 0x00000000;
set static Passes     = 0x00000000;   // сколько раз читали SYSINFO
set static Words_Read = 0x00000000;   // сколько слов честно прочитали
set static Dash_State = 0x00000000;   // 1 = сеть честно «—»
set static Last_Cmd   = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009C01);      // LOG: terminal fetch START

    // статики VM не инициализирует — заводим честно
    Passes = 0x00000000;
    Words_Read = 0x00000000;
    Dash_State = 0x00000000;
    Last_Cmd = 0x00000000;

    // ---- SYSINFO: в полной ОС пишет загрузка (TKT-026) ----
    // Здесь та же честная сводка того же запуска, без «своих» чисел.
    run Init_Sysinfo();
    out_cell(LOG_PORT, 0x00009C09);      // LOG: снимок SYSINFO готов

    // ---- до первой команды НИ ОДНОГО чтения (не polling) ----
    if (Passes == 0x00000000) {
        if (Words_Read == 0x00000000) {
            out_cell(LOG_PORT, 0x00009C10);   // LOG: polling нет
        } else {
            out_cell(LOG_PORT, 0x000099D0);   // BAD: читали до команды
        }
    } else {
        out_cell(LOG_PORT, 0x000099D0);       // BAD: проход до команды
    }

    // ---- fetch: 6 слов ----
    Cmd_Tag = TAG_FETCH2;
    run Dispatch();
    if (Rows == ROWS_FETCH) {
        if (Last_Cmd == TAG_FETCH2) {
            Tmp_A = in_cell(OUT);
            Tmp_B = SYSINFO;
            Tmp_C = in_cell(Tmp_B);
            if (Tmp_A == Tmp_C) {
                out_cell(LOG_PORT, 0x00009C11);   // fetch: версия честная
            } else {
                out_cell(LOG_PORT, 0x000099D1);   // BAD: версия не та
            }
        } else {
            out_cell(LOG_PORT, 0x000099D2);       // BAD: чужая команда
        }
    } else {
        out_cell(LOG_PORT, 0x000099D3);           // BAD: число строк fetch
    }

    // ---- sysinfo: 8 слов ----
    Cmd_Tag = TAG_SYSINFO;
    run Dispatch();
    if (Rows == ROWS_SYSINFO) {
        Tmp_A = OUT;
        Tmp_A = Tmp_A + 28;
        Tmp_B = in_cell(Tmp_A);
        Tmp_C = SYSINFO;
        Tmp_C = Tmp_C + 28;
        Tmp_A = in_cell(Tmp_C);
        if (Tmp_B == Tmp_A) {
            out_cell(LOG_PORT, 0x00009C12);       // sysinfo: хвост честный
        } else {
            out_cell(LOG_PORT, 0x000099D4);       // BAD: хвост не тот
        }
    } else {
        out_cell(LOG_PORT, 0x000099D5);           // BAD: число строк sysinfo
    }

    // ---- сеть не поднялась: честное «—» ----
    Tmp_A = OUT;
    Tmp_A = Tmp_A + 16;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == DASH) {
        if (Dash_State == 0x00000001) {
            out_cell(LOG_PORT, 0x00009C13);       // «—» честное
        } else {
            out_cell(LOG_PORT, 0x000099D6);       // BAD: флаг «—» не выставлен
        }
    } else {
        out_cell(LOG_PORT, 0x000099D7);           // BAD: вместо «—» выдумка
    }

    // ---- сеть появилась: показываем ровно то, что в SYSINFO ----
    Ptr = SYSINFO;
    Ptr = Ptr + 16;
    store_ind(Ptr, 0x0A000001);                   // честный адрес из загрузки
    Cmd_Tag = TAG_FETCH2;
    run Dispatch();
    Tmp_A = OUT;
    Tmp_A = Tmp_A + 16;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == 0x0A000001) {
        if (Dash_State == 0x00000000) {
            out_cell(LOG_PORT, 0x00009C14);       // сеть показана честно
        } else {
            out_cell(LOG_PORT, 0x000099D8);       // BAD: «—» при живых данных
        }
    } else {
        out_cell(LOG_PORT, 0x000099D9);           // BAD: значение подменено
    }

    // ---- неизвестная команда: честный отказ, чтения нет ----
    Tmp_A = Passes;
    Cmd_Tag = TAG_ECHO;
    run Dispatch();
    if (Rows == 0x00000000) {
        if (Passes == Tmp_A) {
            if (Last_Cmd == 0x00000000) {
                out_cell(LOG_PORT, 0x00009C15);   // отказ без чтения
            } else {
                out_cell(LOG_PORT, 0x000099DA);   // BAD: команда «выполнилась»
            }
        } else {
            out_cell(LOG_PORT, 0x000099DB);       // BAD: читали на отказе
        }
    } else {
        out_cell(LOG_PORT, 0x000099DC);           // BAD: строки на отказе
    }

    // ---- ровно по требованию: 3 прохода, 20 слов ----
    if (Passes == 0x00000003) {
        if (Words_Read == 0x00000014) {
            out_cell(LOG_PORT, 0x00009C16);       // проходы/слова честные
        } else {
            out_cell(LOG_PORT, 0x000099DD);       // BAD: число слов
        }
    } else {
        out_cell(LOG_PORT, 0x000099DE);           // BAD: число проходов
    }

    out_cell(LOG_PORT, 0x00009CFF);      // LOG: terminal fetch DONE
    terminate;
}

// честный снимок 8 слов — ровно как Build_Sysinfo в bootlog.kt (TKT-026)
function Init_Sysinfo() {
    Ptr = SYSINFO;
    store_ind(Ptr, 0x00000200);          // +0  CtOs 2.0
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00005101);          // +4  аптайм
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000020);          // +8  пул 32 МБ
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000007);          // +12 ms0, ms1, hd0
    Ptr = Ptr + 4;
    store_ind(Ptr, DASH);                // +16 сети нет — честное «—»
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000003);          // +20 тема builtin/ps5_style
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // +24 видео 2D
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x0000000A);          // +28 записей журнала загрузки
}

// ---------- командный слой: ровно по требованию ----------
function Dispatch() {
    Rows = 0x00000000;
    Dash_State = 0x00000000;
    Last_Cmd = 0x00000000;
    if (Cmd_Tag == TAG_FETCH2) {
        Rows = ROWS_FETCH;
        Last_Cmd = TAG_FETCH2;
        run Snapshot();
    } else {
        if (Cmd_Tag == TAG_SYSINFO) {
            Rows = ROWS_SYSINFO;
            Last_Cmd = TAG_SYSINFO;
            run Snapshot();
        } else {
            if (Cmd_Tag == TAG_SYSTEM) {
                Rows = ROWS_SYSINFO;
                Last_Cmd = TAG_SYSTEM;
                run Snapshot();
            } else {
                out_cell(LOG_PORT, E_CMD);   // честный отказ, без чтений
            }
        }
    }
}

function Snapshot() {
    Ptr = SYSINFO;
    Idx = 0x00000000;
    Tmp_A = OUT;
    run Copy_Loop();
    Passes = Passes + 1;
    Tmp_A = OUT;
    Tmp_A = Tmp_A + 16;
    Tmp_B = in_cell(Tmp_A);
    if (Tmp_B == DASH) {
        Dash_State = 0x00000001;
    } else {
        Dash_State = 0x00000000;
    }
}

function Copy_Loop() {
    if (Idx == Rows) {
        // снимок честно закончен
    } else {
        Tmp_B = in_cell(Ptr);
        store_ind(Tmp_A, Tmp_B);
        Ptr = Ptr + 4;
        Tmp_A = Tmp_A + 4;
        Idx = Idx + 1;
        Words_Read = Words_Read + 1;
        run Copy_Loop();
    }
}
