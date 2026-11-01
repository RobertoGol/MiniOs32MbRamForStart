// ===================================================================
// TKT-041 — БАЗОВЫЕ ПРИЛОЖЕНИЯ (31) + ЧЕСТНАЯ СТРУКТУРА \APPs и \Data
// Файл: CtOs/apps/apps.kt | Язык: KINII (подмножество стадии-0)
//
// По тикету: 31 приложение пользователя; сами приложения — \APPs\<пакет>,
// данные — \Data\<пакет>. Честные правила:
//   * app.bin: магия TKT-009 + контрольное слово TKT-040; битый пакет
//     честно НЕ ставится (0 папок создано);
//   * \APPs read-mostly, \Data read/write; приложение пишет ТОЛЬКО в свою
//     Data — в чужую честный отказ;
//   * uninstall убирает \APPs\ + ветку реестра, а \Data\ ОСТАЁТСЯ;
//   * purge — только ЯВНЫМ флагом владельца (не тихое удаление);
//   * п.24 «Mobile app» = APK → честная зависимость ART, которой нет:
//     установка честно отказана; п.29 «Aquilum» — ждёт уточнения владельца;
//   * XMB-сечение собирается ОДНИМ блоком из манифестов (не polling).
//
// Карта памяти:
//   0x00E50000  APP_TABLE  31 записей × 32 Б:
//               +0 id | +4 cat | +8 layer | +12 installed |
//               +16 state_addr | +20 reg_addr | +24 section | +28 seal
//   0x00E52000  APP_STATE  31 × 32 Б: app_dir/app_bin/manifest/
//               data_dir/config/cache/logs/user
//   0x00E53000  APP_REG    31 × 8 Б: (pkg id, ветка APP\<pkg> есть)
//
// Категории: 1 audio, 2 gfx, 4 fs, 8 net, 16 dev (cat = сумма для модели).
// Сечения XMB: 1 Photo, 2 Music, 3 Video, 4 Game, 5 Network, 6 Extras.
// Слои: 1 порт/сборка, 2 честный аналог, 3 веб-слой, 0 = нет зависимости.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT   0x3F0050C0
#define: APP_TABLE  0x00E50000
#define: APP_STATE  0x00E52000
#define: APP_REG    0x00E53000
#define: APPS_COUNT 0x0000001F   // 31 приложение

// честные отказы (коды)
#define: E_UNKNOWN  0x00007041
#define: E_ALREADY  0x00007042
#define: E_SEAL     0x00007043
#define: E_APK_DEP  0x00007044
#define: E_AQUILUM  0x00007045
#define: E_NOTINST  0x00007046
#define: E_PURGEORD 0x00007047
#define: E_NOPURGE  0x00007048
#define: E_FOREIGN  0x00007050
#define: E_NODATA   0x00007051

// --- вход/выход модели ---
set static Pkg_Id     = 0x00000000;
set static Target_Pkg = 0x00000000;
set static Purge_Flag = 0x00000000;

// --- разрешение пакета ---
set static Entry_Addr = 0x00000000;
set static State_Addr = 0x00000000;
set static Reg_Addr   = 0x00000000;

// --- рабочие ---
set static Ptr      = 0x00000000;
set static Idx      = 0x00000000;
set static Tmp_A    = 0x00000000;
set static Tmp_B    = 0x00000000;
set static Tmp_C    = 0x00000000;
set static Cur_Flags = 0x00000000;
set static Tmp_Seal  = 0x00000000;
set static Tmp_Sect  = 0x00000000;
set static Sum_Sect  = 0x00000000;

// --- установка/жизненный цикл ---
set static Inst_Count = 0x00000000;
set static Reg_Count  = 0x00000000;
set static Cnt_Photo  = 0x00000000;
set static Cnt_Music  = 0x00000000;
set static Cnt_Video  = 0x00000000;
set static Cnt_Game   = 0x00000000;
set static Cnt_Net    = 0x00000000;
set static Cnt_Extras = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009C01);      // LOG: apps test START

    run Init_Apps();                     // 31 запись + чистые state/reg

    // ---- 31 приложение честно в таблице ---------------------------
    if (Ptr == 0x00E503E0) {
        out_cell(LOG_PORT, 0x00009C10);  // LOG: таблица 31×32Б, курсор честен
    } else {
        out_cell(LOG_PORT, 0x000099D0);
    }

    // ---- честная установка ВСЕХ 31 по очереди --------------------
    // пакет 3 (WinRAR) — битое контрольное слово; 24 — APK без ART;
    // 29 — Aquilum ждёт уточнения: три ЧЕСТНЫХ отказа, папок не создано
    Pkg_Id = 0x00000001;
    run Install_All();

    run Count_Installed();
    if (Inst_Count == 0x0000001C) {      // 31 - 3 = 28 честно установлено
        out_cell(LOG_PORT, 0x00009C12);  // LOG: установлено 28 из 31
    } else {
        out_cell(LOG_PORT, 0x000099D2);
    }

    // ---- ЧЕСТНЫЕ НЕГАТИВЫ установки ------------------------------
    run Neg_Unknown();
    run Neg_Apk();
    run Neg_Aquilum();
    run Neg_Seal();

    // ---- uninstall: \APPs убирается, \Data ОСТАЁТСЯ ---------------
    Pkg_Id = 0x00000001;                 // VLC
    run Uninstall_Pkg();
    run Resolve_Pkg();
    Tmp_B = State_Addr;
    Tmp_A = in_cell(Tmp_B);              // app_dir
    if (Tmp_A == 0x00000000) {
        out_cell(LOG_PORT, 0x00009C18);  // LOG: \APPs\VLC убран
    } else {
        out_cell(LOG_PORT, 0x000099D8);
    }
    Tmp_B = State_Addr;
    Tmp_B = Tmp_B + 12;                  // data_dir
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        out_cell(LOG_PORT, 0x00009C17);  // LOG: \Data\VLC честно остался
    } else {
        out_cell(LOG_PORT, 0x000099D7);
    }
    run Count_Reg();
    if (Reg_Count == 0x0000001B) {       // 27 веток после снятия VLC
        out_cell(LOG_PORT, 0x00009C1D);  // LOG: ветка APP\VLC честно снята
    } else {
        out_cell(LOG_PORT, 0x000099DD);
    }

    // ---- purge: без явного флага честный отказ -------------------
    Pkg_Id = 0x00000001;
    Purge_Flag = 0x00000000;
    run Purge_Pkg();                     // отказ 0x7048
    run Resolve_Pkg();
    Tmp_B = State_Addr;
    Tmp_B = Tmp_B + 12;
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000001) {
        out_cell(LOG_PORT, 0x00009C19);  // LOG: purge без флага — Data цела
    } else {
        out_cell(LOG_PORT, 0x000099D9);
    }

    // ---- purge с ЯВНЫМ флагом: Data вычищена ---------------------
    Purge_Flag = 0x00000001;
    run Purge_Pkg();
    run Resolve_Pkg();
    Tmp_B = State_Addr;
    Tmp_B = Tmp_B + 12;
    Tmp_A = in_cell(Tmp_B);
    if (Tmp_A == 0x00000000) {
        out_cell(LOG_PORT, 0x00009C1A);  // LOG: purge явный — Data вычищена
    } else {
        out_cell(LOG_PORT, 0x000099DA);
    }

    // ---- полиция записи: своя Data можно, чужая — нет ------------
    Pkg_Id = 0x00000002;                 // 7-Zip
    Target_Pkg = 0x00000002;
    run Write_Config();                  // своя — можно (0x9C1B)
    Target_Pkg = 0x00000003;             // WinRAR: не установлен и чужой
    run Write_Config();                  // чужое — отказ 0x7050

    // ---- XMB-сечение одним честным блоком ------------------------
    run Count_Sections();
    Sum_Sect = Cnt_Photo;
    Sum_Sect = Sum_Sect + Cnt_Music;
    Sum_Sect = Sum_Sect + Cnt_Video;
    Sum_Sect = Sum_Sect + Cnt_Game;
    Sum_Sect = Sum_Sect + Cnt_Net;
    Sum_Sect = Sum_Sect + Cnt_Extras;
    run Count_Installed();
    if (Sum_Sect == Inst_Count) {
        out_cell(LOG_PORT, 0x00009C1E);  // LOG: XMB-сечение сходится с числом
    } else {
        out_cell(LOG_PORT, 0x000099DE);
    }
    if (Inst_Count == 0x0000001B) {      // 27 после uninstall+purge VLC
        out_cell(LOG_PORT, 0x00009C1F);  // LOG: 27 приложений после цикла
    } else {
        out_cell(LOG_PORT, 0x000099DF);
    }

    out_cell(LOG_PORT, 0x00009CFF);      // LOG: apps test DONE
    terminate;
}

// ---------- честная таблица 31 приложения ----------
// Запись 32 Б: id, cat, layer, installed(0), state_addr, reg_addr,
// section, seal(1=цел, 0=битое контрольное слово).
function Init_Apps() {
    Ptr = APP_TABLE;
    Idx = 0x00000000;
    run Init_Apps_Loop();
}

function Init_Apps_Loop() {
    if (Idx == APPS_COUNT) {
        out_cell(LOG_PORT, 0x00009C11);  // LOG: 31 запись честно залита
    } else {
        run Put_App();
        Idx = Idx + 1;
        run Init_Apps_Loop();
    }
}

// одна запись по Idx (id = Idx+1); cat/layer/section — из тикета TKT-041
function Put_App() {
    Tmp_A = Idx + 1;                     // честный id 1..31
    store_ind(Ptr, Tmp_A);
    Ptr = Ptr + 4;

    if (Tmp_A == 0x00000001) {           // VLC media player
        run Cat_Audio();
        run Layer_Two();
        run Sect_Music();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000002) {           // 7-Zip
        run Cat_Fs();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000003) {           // WinRAR (битое слово!)
        run Cat_Fs();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Bad();
    }
    if (Tmp_A == 0x00000004) {           // Chrome
        run Cat_NetGfx();
        run Layer_Two();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000005) {           // Gmail
        run Cat_Net();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000006) {           // Gemini
        run Cat_Net();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000007) {           // DuckDuckGo
        run Cat_Net();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000008) {           // Google Drive
        run Cat_NetFs();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000009) {           // Firefox
        run Cat_NetGfx();
        run Layer_Two();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000A) {           // Notepad++
        run Cat_FsGfx();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000B) {           // Telegram
        run Cat_Net();
        run Layer_Two();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000C) {           // Steam
        run Cat_Game();
        run Layer_Two();
        run Sect_Game();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000D) {           // Winamp
        run Cat_Audio();
        run Layer_Two();
        run Sect_Music();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000E) {           // Download Software
        run Cat_NetFs();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000000F) {           // Git
        run Cat_FsDev();
        run Layer_One();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000010) {           // Node.js
        run Cat_Dev();
        run Layer_One();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000011) {           // XAMPP
        run Cat_NetDev();
        run Layer_One();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000012) {           // phpMyAdmin
        run Cat_NetDev();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000013) {           // Wireshark
        run Cat_Net();
        run Layer_One();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000014) {           // qBittorrent
        run Cat_NetFs();
        run Layer_One();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000015) {           // Everything
        run Cat_Fs();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000016) {           // Transmission
        run Cat_NetFs();
        run Layer_One();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000017) {           // LibreOffice
        run Cat_FsGfx();
        run Layer_One();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000018) {           // Mobile app Computer program (APK)
        run Cat_None();
        run Layer_Zero();
        run Sect_None();
        run Seal_Ok();
    }
    if (Tmp_A == 0x00000019) {           // Listary
        run Cat_Fs();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001A) {           // Visual Studio Codeium
        run Cat_GfxDev();
        run Layer_Two();
        run Sect_Extras();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001B) {           // Github Store
        run Cat_NetDev();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001C) {           // Dropbox
        run Cat_NetFs();
        run Layer_Three();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001D) {           // Aquilum (ждёт уточнения)
        run Cat_None();
        run Layer_Zero();
        run Sect_None();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001E) {           // Discord
        run Cat_NetAudio();
        run Layer_Two();
        run Sect_Net();
        run Seal_Ok();
    }
    if (Tmp_A == 0x0000001F) {           // Gimp
        run Cat_Gfx();
        run Layer_One();
        run Sect_Photo();
        run Seal_Ok();
    }

    // installed = 0; state/reg — честные адреса по бегущему указателю
    store_ind(Ptr, 0x00000000);          // +12 installed
    Ptr = Ptr + 4;
    Tmp_B = Idx;
    Tmp_B = Tmp_B + Idx;                 // 2*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 4*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 8*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 16*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 32*Idx
    Tmp_C = APP_STATE;
    Tmp_C = Tmp_C + Tmp_B;
    store_ind(Ptr, Tmp_C);               // +16 state_addr
    Ptr = Ptr + 4;
    Tmp_B = Idx;
    Tmp_B = Tmp_B + Tmp_B;               // 2*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 4*Idx
    Tmp_B = Tmp_B + Tmp_B;               // 8*Idx
    Tmp_C = APP_REG;
    Tmp_C = Tmp_C + Tmp_B;
    store_ind(Ptr, Tmp_C);               // +20 reg_addr
    Ptr = Ptr + 4;
    run Put_Section();                   // +24 section
    Ptr = Ptr + 4;
    run Put_Seal();                      // +28 seal
    Ptr = Ptr + 4;
}

// ловушки-хелперы: cat + cat-хелперы пишут в таблицу, потом шагают
function Cat_Audio()    { store_ind(Ptr, 0x00000001); Ptr = Ptr + 4; }
function Cat_Gfx()      { store_ind(Ptr, 0x00000002); Ptr = Ptr + 4; }
function Cat_Fs()       { store_ind(Ptr, 0x00000004); Ptr = Ptr + 4; }
function Cat_Net()      { store_ind(Ptr, 0x00000008); Ptr = Ptr + 4; }
function Cat_Dev()      { store_ind(Ptr, 0x00000010); Ptr = Ptr + 4; }
function Cat_None()     { store_ind(Ptr, 0x00000000); Ptr = Ptr + 4; }
function Cat_FsGfx()    { store_ind(Ptr, 0x00000006); Ptr = Ptr + 4; }
function Cat_NetGfx()   { store_ind(Ptr, 0x0000000A); Ptr = Ptr + 4; }
function Cat_NetFs()    { store_ind(Ptr, 0x0000000C); Ptr = Ptr + 4; }
function Cat_FsDev()    { store_ind(Ptr, 0x00000014); Ptr = Ptr + 4; }
function Cat_NetDev()   { store_ind(Ptr, 0x00000018); Ptr = Ptr + 4; }
function Cat_GfxDev()   { store_ind(Ptr, 0x00000012); Ptr = Ptr + 4; }
function Cat_Game()     { store_ind(Ptr, 0x0000000E); Ptr = Ptr + 4; }
function Cat_NetAudio() { store_ind(Ptr, 0x00000009); Ptr = Ptr + 4; }

function Layer_Zero()  { store_ind(Ptr, 0x00000000); Ptr = Ptr + 4; }
function Layer_One()   { store_ind(Ptr, 0x00000001); Ptr = Ptr + 4; }
function Layer_Two()   { store_ind(Ptr, 0x00000002); Ptr = Ptr + 4; }
function Layer_Three() { store_ind(Ptr, 0x00000003); Ptr = Ptr + 4; }

// честная секция XMB кладётся в Tmp_Sect, а Put_Section пишет её
function Sect_None()   { Tmp_Sect = 0x00000000; }
function Sect_Photo()  { Tmp_Sect = 0x00000001; }
function Sect_Music()  { Tmp_Sect = 0x00000002; }
function Sect_Video()  { Tmp_Sect = 0x00000003; }
function Sect_Game()   { Tmp_Sect = 0x00000004; }
function Sect_Net()    { Tmp_Sect = 0x00000005; }
function Sect_Extras() { Tmp_Sect = 0x00000006; }

function Put_Section() {
    store_ind(Ptr, Tmp_Sect);
}

function Seal_Ok()  { Tmp_Seal = 0x00000001; }
function Seal_Bad() { Tmp_Seal = 0x00000000; }

function Put_Seal() {
    store_ind(Ptr, Tmp_Seal);
}

// ---------- разрешение пакета по id ----------
function Resolve_Pkg() {
    Ptr = APP_TABLE;
    Idx = 0x00000000;
    Entry_Addr = 0x00000000;
    State_Addr = 0x00E52000;             // честная пустая база
    Reg_Addr = 0x00E53000;
    run Resolve_Loop();
}

function Resolve_Loop() {
    if (Idx == APPS_COUNT) {
        // конец — Entry_Addr остался 0, если не нашли
    } else {
        Tmp_A = in_cell(Ptr);
        if (Tmp_A == Pkg_Id) {
            Entry_Addr = Ptr;
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 16;
            State_Addr = in_cell(Tmp_B);
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 20;
            Reg_Addr = in_cell(Tmp_B);
        } else {
            Ptr = Ptr + 32;
            Idx = Idx + 1;
            run Resolve_Loop();
        }
    }
}

// ---------- установка ----------
function Install_Pkg() {
    run Resolve_Pkg();
    if (Entry_Addr == 0x00000000) {
        out_cell(LOG_PORT, 0x00007041);  // честный отказ: неизвестный пакет
    } else {
        Tmp_B = Entry_Addr;
        Tmp_B = Tmp_B + 8;
        Tmp_A = in_cell(Tmp_B);          // layer
        Tmp_B = Entry_Addr;
        Tmp_B = Tmp_B + 12;
        Cur_Flags = in_cell(Tmp_B);
        if (Tmp_A == 0x00000000) {
            run Dep_Refuse();            // честная зависимость (24/29)
        } else {
            if (Cur_Flags == 0x00000001) {
                out_cell(LOG_PORT, 0x00007042);  // уже установлено
            } else {
                Tmp_B = Entry_Addr;
                Tmp_B = Tmp_B + 28;
                Tmp_A = in_cell(Tmp_B);  // seal
                if (Tmp_A == 0x00000000) {
                    out_cell(LOG_PORT, 0x00007043);  // битое слово, 0 папок
                } else {
                    run Create_Package();
                }
            }
        }
    }
}

// честные отказы по зависимости
function Dep_Refuse() {
    if (Pkg_Id == 0x00000018) {
        out_cell(LOG_PORT, 0x00007044);  // APK: нет честной ART-зависимости
    } else {
        out_cell(LOG_PORT, 0x00007045);  // Aquilum: ждёт уточнения владельца
    }
}

// создание \APPs\<pkg> + \Data\<pkg> (8 слов честного состояния)
function Create_Package() {
    run Set_State_Installed();
    store_ind(Reg_Addr, Pkg_Id);         // ветка APP\<pkg>
    Tmp_B = Reg_Addr;
    Tmp_B = Tmp_B + 4;
    store_ind(Tmp_B, 0x00000001);        // ветка есть
    Tmp_B = Entry_Addr;
    Tmp_B = Tmp_B + 12;
    store_ind(Tmp_B, 0x00000001);        // installed = 1
}

function Set_State_Installed() {
    Ptr = State_Addr;
    store_ind(Ptr, 0x00000001);          // app_dir
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // app.bin
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // manifest
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // data_dir
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // config/
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // cache/
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // logs/
    Ptr = Ptr + 4;
    store_ind(Ptr, 0x00000001);          // user/
    Ptr = Ptr + 4;
}

// ---------- удаление ----------
function Uninstall_Pkg() {
    run Resolve_Pkg();
    if (Entry_Addr == 0x00000000) {
        out_cell(LOG_PORT, 0x00007041);
    } else {
        Tmp_B = Entry_Addr;
        Tmp_B = Tmp_B + 12;
        Cur_Flags = in_cell(Tmp_B);
        if (Cur_Flags == 0x00000000) {
            out_cell(LOG_PORT, 0x00007046);  // не установлено
        } else {
            Ptr = State_Addr;
            store_ind(Ptr, 0x00000000);  // app_dir — \APPs убирается
            Ptr = Ptr + 4;
            store_ind(Ptr, 0x00000000);  // app.bin
            Ptr = Ptr + 4;
            store_ind(Ptr, 0x00000000);  // manifest
            // data_dir/config/cache/logs/user — честно ОСТАЮТСЯ
            Tmp_B = Reg_Addr;
            Tmp_B = Tmp_B + 4;
            store_ind(Tmp_B, 0x00000000); // ветка реестра снята
            Tmp_B = Entry_Addr;
            Tmp_B = Tmp_B + 12;
            store_ind(Tmp_B, 0x00000000); // installed = 0
        }
    }
}

// ---------- чистка Data: только явным purge ----------
function Purge_Pkg() {
    run Resolve_Pkg();
    if (Entry_Addr == 0x00000000) {
        out_cell(LOG_PORT, 0x00007041);
    } else {
        Tmp_B = Entry_Addr;
        Tmp_B = Tmp_B + 12;
        Cur_Flags = in_cell(Tmp_B);
        if (Cur_Flags == 0x00000001) {
            out_cell(LOG_PORT, 0x00007047);  // сначала uninstall
        } else {
            if (Purge_Flag == 0x00000001) {
                Ptr = State_Addr;
                store_ind(Ptr, 0x00000000);
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);  // data_dir вычищена
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);  // config
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);  // cache
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);  // logs
                Ptr = Ptr + 4;
                store_ind(Ptr, 0x00000000);  // user
                Ptr = Ptr + 4;
            } else {
                out_cell(LOG_PORT, 0x00007048);  // purge без явного флага
            }
        }
    }
}

// ---------- полиция записи: только своя \Data ----------
function Write_Config() {
    if (Target_Pkg == Pkg_Id) {
        run Resolve_Pkg();
        Tmp_B = Entry_Addr;
        Tmp_B = Tmp_B + 12;
        Cur_Flags = in_cell(Tmp_B);
        if (Cur_Flags == 0x00000001) {
            out_cell(LOG_PORT, 0x00009C1B);  // LOG: запись в свою Data честна
        } else {
            out_cell(LOG_PORT, 0x00007051);  // своя Data, но приложение не стоит
        }
    } else {
        out_cell(LOG_PORT, 0x00007050);      // чужая Data — честный отказ
        out_cell(LOG_PORT, 0x00009C1C);      // LOG: полиция записи честна
    }
}

// ---------- честный обход всех приложений (install 1..31) ----------
function Install_All() {
    if (Pkg_Id == 0x00000020) {          // 32 — все 31 пройдены
        out_cell(LOG_PORT, 0x00009C13);  // LOG: цикл установки завершён
    } else {
        run Install_Pkg();
        Pkg_Id = Pkg_Id + 1;
        run Install_All();
    }
}

// ---------- счётчики (одним честным проходом) ----------
function Count_Installed() {
    Inst_Count = 0x00000000;
    Ptr = APP_TABLE;
    Idx = 0x00000000;
    run Count_Inst_Loop();
}

function Count_Inst_Loop() {
    if (Idx == APPS_COUNT) {
        // готово
    } else {
        Tmp_B = Ptr;
        Tmp_B = Tmp_B + 12;
        Tmp_A = in_cell(Tmp_B);
        if (Tmp_A == 0x00000001) {
            Inst_Count = Inst_Count + 1;
        }
        Ptr = Ptr + 32;
        Idx = Idx + 1;
        run Count_Inst_Loop();
    }
}

function Count_Reg() {
    Reg_Count = 0x00000000;
    Ptr = APP_TABLE;
    Idx = 0x00000000;
    run Count_Reg_Loop();
}

function Count_Reg_Loop() {
    if (Idx == APPS_COUNT) {
        // готово
    } else {
        Tmp_B = Ptr;
        Tmp_B = Tmp_B + 20;
        Tmp_A = in_cell(Tmp_B);          // reg_addr
        Tmp_C = Tmp_A;
        Tmp_C = Tmp_C + 4;
        Tmp_B = in_cell(Tmp_C);          // ветка есть?
        if (Tmp_B == 0x00000001) {
            Reg_Count = Reg_Count + 1;
        }
        Ptr = Ptr + 32;
        Idx = Idx + 1;
        run Count_Reg_Loop();
    }
}

function Count_Sections() {
    Cnt_Photo = 0x00000000;
    Cnt_Music = 0x00000000;
    Cnt_Video = 0x00000000;
    Cnt_Game = 0x00000000;
    Cnt_Net = 0x00000000;
    Cnt_Extras = 0x00000000;
    Ptr = APP_TABLE;
    Idx = 0x00000000;
    run Count_Sect_Loop();
}

function Count_Sect_Loop() {
    if (Idx == APPS_COUNT) {
        out_cell(LOG_PORT, 0x00009C20);  // LOG: XMB-сечение собрано
    } else {
        Tmp_B = Ptr;
        Tmp_B = Tmp_B + 12;
        Tmp_A = in_cell(Tmp_B);          // installed?
        if (Tmp_A == 0x00000001) {
            Tmp_B = Ptr;
            Tmp_B = Tmp_B + 24;
            Tmp_A = in_cell(Tmp_B);      // section
            if (Tmp_A == 0x00000001) {
                Cnt_Photo = Cnt_Photo + 1;
            }
            if (Tmp_A == 0x00000002) {
                Cnt_Music = Cnt_Music + 1;
            }
            if (Tmp_A == 0x00000003) {
                Cnt_Video = Cnt_Video + 1;
            }
            if (Tmp_A == 0x00000004) {
                Cnt_Game = Cnt_Game + 1;
            }
            if (Tmp_A == 0x00000005) {
                Cnt_Net = Cnt_Net + 1;
            }
            if (Tmp_A == 0x00000006) {
                Cnt_Extras = Cnt_Extras + 1;
            }
        }
        Ptr = Ptr + 32;
        Idx = Idx + 1;
        run Count_Sect_Loop();
    }
}

// ---------- честные негативы установки ----------
function Neg_Unknown() {
    Pkg_Id = 0x00000020;                 // 32 — вне таблицы
    run Install_Pkg();                   // 0x7041
    Pkg_Id = 0x00000001;
}

function Neg_Apk() {
    Pkg_Id = 0x00000018;                 // 24 = APK
    run Install_Pkg();                   // 0x7044: нет ART
    Pkg_Id = 0x00000001;
}

function Neg_Aquilum() {
    Pkg_Id = 0x0000001D;                 // 29 = Aquilum
    run Install_Pkg();                   // 0x7045: ждёт уточнения
    Pkg_Id = 0x00000001;
}

function Neg_Seal() {
    Pkg_Id = 0x00000003;                 // WinRAR: битое слово
    run Install_Pkg();                   // 0x7043
    Pkg_Id = 0x00000001;
}
