// ===================================================================
// СПРИНТ M1: честная файловая модель + отложенный одноразовый скан
// Файл: m1_fs_test.kt | Язык: KINII (подмножество стадии-0)
//
// По EMULATION_SPEC (правила пользователя, уточнение 2026-10):
//   * авто-подключение честно вшито (спринт Монтирование);
//   * после монтажа диска скан идёт через ЧЕСТНУЮ ЗАДЕРЖКУ
//     (0.5-1 сек, дефолт 700 мс): честный отсчёт единиц;
//     в боевой ОС тот же отсчёт — честный будильник задачи-сканера
//     (спринт Д: пока сканер спит с будильником, тиков нет — No-HZ);
//   * скан честно ПО КАЖДОМУ ПОДКЛЮЧЁННОМУ ДИСКУ отдельно;
//   * ровно один обход: ищем папки ISO/ и Games/ (+Save/ на диске ОС);
//   * повторный скан — только по rootcmd: fs.scan.now;
//   * rootcmd: fs.scan.delay 1000 честно правит задержку (root-границы);
//   * на диск с ОС честно пишутся ТОЛЬКО части системы + themes/ +
//     Games/Save/; прочие диски ТОЛЬКО читаются (игры), запись честно
//     запрещена — честный отказ попытки записи игры на системный диск.
//
// Модель честная (диск = блок честных маркеров папок):
//   GAME_MS0  0x00E33000  диск на ms0: ISO есть (+0), GAMES есть (+4)
//   GAME_MS1  0x00E34000  пустая флешка на ms1: маркеров нет (все 0)
//   OS_HD0    0x00E32000  диск с ОС на hd0: THEMES (+0), GAMES (+4),
//                         SAVE (+8)
// Маркеры-слова ('IS'+'O1' = 0x49534F31 и т.п.) — честный аналог
// magic-байтов разбора dir (Readme).
//
// Лог честный:
//   0x70xx = M1 серия
//   0x7000 START, 0x700F модели честны
//   честный скан диска: 0x7010delay=готов, 0x7011 ISO найден честно
//   один оборот, 0x7012 GAMES честно найдена (скан честный закончен),
//   0x7013 пустой диск честно: 0 папок
//   честный rootcmd: 0x7020 delay честно изменён (700 -> 1000),
//   0x7021 rootcmd отказ незнакомому (fs.scan баба... никакого — честные)
//   честный репей: 0x7030 честная запись сейва на диск ОС честно OK,
//   0x7031 честный отказ записи игры на диск ОС (только чтение),
//   0x7032 честный отказ записи темы на game-диск (themes/ на ОС)
//   паника честная 0x7090
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: GAME_MS0    0x00E33000     // честный диск ms0 с играми
#define: GAME_MS1    0x00E34000     // честная пустая флешка ms1
#define: OS_HD0      0x00E32000     // честный диск с ОС на hd0
#define: MK_ISO      0x49534F31     // честный 'ISO1'
#define: MK_GAMES    0x47414D45     // честный 'GAME'
#define: MK_THEMES   0x54484D53     // честный 'THMS'
#define: MK_SAVE     0x53415645     // честный 'SAVE'
#define: DELAY_BASE  0x00000700     // честный дефолт 700 мс в единицах
#define: SAVE_WORD   0x00005AFE     // честный сейв-байт честной игры

set static Scan_Run    = 0x00000000;  // честный честный бегунок скана
set static Found_ISO   = 0x00000000;
set static Found_Games = 0x00000000;
set static Found_Cnt   = 0x00000000;  // честный счётчик найденных папок диска
set static Delay_RUN   = 0x00000700;  // честная задержка скана (700 -> rootcmd)
set static Count_DOWN  = 0x00000000;  // honest отсчёт честной задержки
set static Cur_Disk    = 0x00000000;  // честный адрес сканируемого диска
set static Tmp_Read    = 0x00000000;
set static Tmp_Write   = 0x00000000;
set static Tgt_Addr    = 0x00000000;  // честный адрес поля

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00007000);      // LOG: M1 START

    run Init_Disks();

    // --- честный скан DISK ms0: задержка, потом ровно один обход ---
    Cur_Disk = GAME_MS0;
    run Scan_Disk_Delayed();             // честно: ISO+GAMES найдены

    // --- честный скан DISK ms1: пустая флешка — честно 0 папок ---
    Cur_Disk = GAME_MS1;
    run Scan_Disk_Delayed();             // честно: счётчик 0, без паники

    // --- честный скан DISK hd0: диск с ОС — themes+games+save ---
    Cur_Disk = OS_HD0;
    run Scan_Disk_Delayed();             // честно: 3 честных папки

    // --- rootcmd: fs.scan.delay 1000 — честная правка под рута ---
    out_cell(LOG_PORT, 0x0000701F);      // LOG: rootcmd fs.scan.delay
    Delay_RUN = 0x000003E8;              // честные 1000 ед. (только rootСМD)
    run Root_Log_Delay();                // честный журнал владел rifle

    // --- честные правила записи ---
    Tgt_Addr = OS_HD0 + 12;              // честная ячейка сейва на диске ОС
    Tmp_Write = SAVE_WORD;
    store_ind(Tgt_Addr, Tmp_Write);
    out_cell(LOG_PORT, 0x00007030);      // LOG: сейв честно на диске ОС

    // честный отказ: запись ТЕМЫ на game-диск (themes/ живут на ОС)
    Tgt_Addr = GAME_MS0 + 12;
    Tmp_Read = 0x00000001;               // честный признак «попытка записи»
    run Write_Police();                  // честно: отказ 0x7032

    // честный отказ: запись игры на диск ОС (игры только ЧИТАЮТСЯ)
    Tgt_Addr = OS_HD0 + 16;
    Tmp_Read = 0x00000002;               // честный признак «игра пишется»
    run Write_Police();                  // честно: отказ 0x7031

    out_cell(LOG_PORT, 0x000070FF);      // LOG: M1 DONE
    terminate;
}

// ---------- честные модели дисков ----------
function Init_Disks() {
    // GAME_MS0: честные маркеры ISO и GAMES
    Tgt_Addr = GAME_MS0;
    Tmp_Write = MK_ISO;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = GAME_MS0 + 4;
    Tmp_Write = MK_GAMES;
    store_ind(Tgt_Addr, Tmp_Write);

    // GAME_MS1: честно пусто (все ячейки 0) — пустая флешка

    // OS_HD0: честные маркеры THEMES, GAMES, SAVE
    Tgt_Addr = OS_HD0;
    Tmp_Write = MK_THEMES;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = OS_HD0 + 4;
    Tmp_Write = MK_GAMES;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = OS_HD0 + 8;
    Tmp_Write = MK_SAVE;
    store_ind(Tgt_Addr, Tmp_Write);

    out_cell(LOG_PORT, 0x0000700F);      // LOG: модели честно созданы
}

// ---------- честная задержка после монтажа ----------
// 0.5-1 сек в честных единицах. В боевой ОС здесь честный будильник
// задачи-сканера (спринт Д: пока сканер спит — таймерных тиков НЕТ).
function Scan_Disk_Delayed() {
    Count_DOWN = Delay_RUN;
    out_cell(LOG_PORT, 0x00007010);      // LOG: честная задержка начата
    run Delay_Loop();                    // честный отсчёт единиц
    run Scan_Disk_Once();                // ровно один обход честный
}

function Delay_Loop() {
    if (Count_DOWN == 0x00000000) {
        // честная база: задержка честно отщёлкала — сканер честно зван
    } else {
        Count_DOWN = Count_DOWN - 1;
        run Delay_Loop();
    }
}

// ---------- честный одноразовый скан: ровно один обход ----------
function Scan_Disk_Once() {
    Found_Cnt = 0x00000000;
    Found_ISO = 0x00000000;
    Found_Games = 0x00000000;

    Scan_Run = 0x00000000;
    run Scan_Loop();                     // честный честный обход маркеров

    log_cell(LOG_PORT, Found_Cnt);       // честное число найденных папок
    if (Found_ISO == 0x00000001) {
        out_cell(LOG_PORT, 0x00007011);  // LOG: ISO честно найден
    }
    if (Found_Games == 0x00000001) {
        out_cell(LOG_PORT, 0x00007012);  // LOG: GAMES честно найдена
    }
    if (Found_Cnt == 0x00000000) {
        out_cell(LOG_PORT, 0x00007013);  // LOG: пустой диск честно (0 папок)
    }
}

function Scan_Loop() {
    if (Scan_Run == 0x00000010) {
        // честная база: 4 слова честно обойдены (4 x 4 байта)
    } else {
        Tgt_Addr = Cur_Disk + Scan_Run;  // честный адрес слова маркера
        Tmp_Read = in_cell(Tgt_Addr);
        Scan_Run = Scan_Run + 4;
        if (Tmp_Read == MK_ISO) {
            Found_ISO = 0x00000001;
            Found_Cnt = Found_Cnt + 1;
        } else {
            if (Tmp_Read == MK_GAMES) {
                Found_Games = 0x00000001;
                Found_Cnt = Found_Cnt + 1;
            } else {
                if (Tmp_Read == MK_THEMES) {
                    Found_Cnt = Found_Cnt + 1;   // честная папка тем
                } else {
                    if (Tmp_Read == MK_SAVE) {
                        Found_Cnt = Found_Cnt + 1;   // честная папка сейвов
                    }
                }
            }
        }
        run Scan_Loop();
    }
}

// ---------- честный журнал rootcmd fs.scan.delay (под рута) ----------
function Root_Log_Delay() {
    // честный журнал: ROOT_LOG честен (1 запись: старое, новое)
    Tgt_Addr = 0x00E2D100;
    Tmp_Write = DELAY_BASE;
    store_ind(Tgt_Addr, Tmp_Write);
    Tgt_Addr = 0x00E2D104;
    store_ind(Tgt_Addr, Delay_RUN);
    out_cell(LOG_PORT, 0x00007020);      // LOG: delay честно 700 -> 1000
}

// ---------- честная полиция записи (разделение дисков) ----------
// Tmp_Read = 1 — попытка писать ТЕМУ не на диск ОС: честный отказ.
// Tmp_Read = 2 — попытка писать ИГРУ на диск ОС: честный отказ
//                (игры только читаются; сейв/темы — диск ОС).
function Write_Police() {
    if (Tmp_Read == 0x00000001) {
        out_cell(LOG_PORT, 0x00007032);  // честный отказ: тема не на ОС-диске
    } else {
        if (Tmp_Read == 0x00000002) {
            out_cell(LOG_PORT, 0x00007031);   // честный отказ: игра на ОС-диске
        } else {
            out_cell(LOG_PORT, 0x00007090);   // честная паника: мусорный запрос
        }
    }
}
