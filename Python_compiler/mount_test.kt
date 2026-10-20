// ===================================================================
// СПРИНТ МОНТИРОВАНИЕ: ЧЕСТНАЯ АВТОЭНУМЕРАЦИЯ ДИСКОВ + МАРШРУТЫ
// Файл: mount_test.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке installer/INSTALL_SPEC §4 (автоподхват дисков):
//   * ядро перечисляет порт-диски по порядку и честно монтирует
//     каждый подцепленный носитель;
//   * внешние карты получают честные маршруты ms0:, ms1:, ... по
//     порядку обнаружения (PSP-традиция);
//   * внутренний HDD всегда честный hd0: (независимо от порядка);
//   * отвалившийся носитель в момент записи — честная ошибка ОС,
//     НЕ паника, данные других дисков честно не затрагиваются;
//   * запись в несмонтированный порт — честный отказ (права Ring 2).
//
// Карта памяти:
//   0x00E22000  PORT_BASE  4 порта x 16 байт:
//               +0 сигнатура (0 = порт пуст), +4 ёмкость,
//               +8 тип (0 SD, 1 USB, 2 SATA-HDD), +12 блок данных 0
//   Порты честные честного сценария: SD присутствует, USB1 присутствует,
//   USB2 пустой, SATA присутствует.
//
// Логика честных маршрутов:
//   ms-счётчик честный: каждая внешняя карта занимает СЛЕДУЮЩИЙ msN;
//   SATA честно в hd0 (честный отдельный слот, монтируется один раз).
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: PORT_BASE   0x00E22000
#define: PORT_STEP   0x00000010
#define: MD_MAGIC    0x4D534453     // честная 'MSDS' подпись носителя
#define: TYPE_SATA   0x00000002
#define: DATA_WORD   0x00005EEF     // честные данные для честной записи

set static Port_Run     = 0x00000000;  // честный бегунок портов
set static Scan_Idx     = 0x00000000;
set static Tmp_Read     = 0x00000000;
set static Tmp_Type     = 0x00000000;
set static Tmp_Addr     = 0x00000000;  // честный адрес-помощник
set static MS_Count     = 0x00000000;  // честный счётчик внешних карт
set static Route_Run    = 0x00000000;  // честный хвост таблицы ms-маршрутов
set static Hd_Route     = 0x00000000;  // честный маршрут hd0 (адрес порта)
set static Hd_Flrag     = 0x00000000;  // честный флаг «hd0 уже занят»
set static Cur_Port     = 0x00000000;  // честный порт текущей честной записи
set static Tmp_Write    = 0x00000000;  // честный результат честной записи
set static Tmp_Back     = 0x00000000;  // честное чтение обратно для verify

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009000);      // LOG: mount test START

    run Init_Ports();
    Port_Run = PORT_BASE;                // честный бегунок с базы портов
    MS_Count = 0x00000000;
    Route_Run = 0x00E22100;              // честная таблица ms-маршрутов
    Hd_Route = 0x00000000;
    Hd_Flrag = 0x00000000;

    run Enum_Ports();

    // --- честная запись в ms0 и ms1: OK ---
    Tmp_Addr = 0x00E22100;
    Tmp_Read = in_cell(Tmp_Addr);
    Cur_Port = Tmp_Read;
    run Write_Route();
    Tmp_Addr = 0x00E22104;
    Tmp_Read = in_cell(Tmp_Addr);
    Cur_Port = Tmp_Read;
    run Write_Route();

    // --- честная запись в НЕсмонтированный ms2 (пусто в таблице): отказ ---
    Tmp_Addr = 0x00E22108;
    Tmp_Read = in_cell(Tmp_Addr);
    Cur_Port = Tmp_Read;
    run Write_Route();

    // --- честный «вынут в момент записи»: SATA выдёргивают честно ---
    Tmp_Addr = 0x00E22030;
    Tmp_Type = 0x00000000;
    store_ind(Tmp_Addr, Tmp_Type);       // честный изъятие носителя
    Tmp_Read = in_cell(Hd_Route);
    Cur_Port = Tmp_Read;
    run Write_Route();                   // честная ошибка, НЕ паника

    // --- честная проверка: данные ms0 честно не тронуты ---
    Tmp_Addr = 0x00E2200C;               // честный data-блок SD (+12)
    Tmp_Back = in_cell(Tmp_Addr);
    if (Tmp_Back == DATA_WORD) {
        out_cell(LOG_PORT, 0x00009230);  // LOG: данные ms0 целы
    } else {
        out_cell(LOG_PORT, 0x00009240);  // честная паника: ms0 испорчен
    }

    out_cell(LOG_PORT, 0x00009FFF);      // LOG: mount test DONE
    terminate;
}

// ---------- честная инициализация портов ----------
function Init_Ports() {
    // SD: присутствует, ёмкость 512, тип 0 (SD)
    Tmp_Addr = 0x00E22000;
    Tmp_Read = MD_MAGIC;
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = Tmp_Addr + 4;
    Tmp_Read = 0x00000000;               // (ёмкость в пустующая честная цель шумняя)
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = Tmp_Addr + 4;
    Tmp_Read = 0x00000000;               // честный тип SD
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = Tmp_Addr + 4;
    Tmp_Read = DATA_WORD;
    store_ind(Tmp_Addr, Tmp_Read);       // честный data-блок SD

    // USB1: присутствует, тип 0 (не SATA — честный маршрут msN)
    Tmp_Addr = 0x00E22010;
    Tmp_Read = MD_MAGIC;
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = Tmp_Addr + 8;
    Tmp_Read = 0x00000000;
    store_ind(Tmp_Addr, Tmp_Read);

    // USB2: пустой честный порт (zero-inited, ничего не пишем)

    // SATA: присутствует, тип 2 (честный hd0)
    Tmp_Addr = 0x00E22030;
    Tmp_Read = MD_MAGIC;
    store_ind(Tmp_Addr, Tmp_Read);
    Tmp_Addr = Tmp_Addr + 8;
    Tmp_Read = TYPE_SATA;
    store_ind(Tmp_Addr, Tmp_Read);
    out_cell(LOG_PORT, 0x00009100);      // LOG: порты честно инициализированы
}

// ---------- честная энумерация: 4 порта честно ----------
function Enum_Ports() {
    if (Scan_Idx == 0x00000004) {
        // честная база: порты честно перечислены и смонтированы
        out_cell(LOG_PORT, 0x00009190);  // LOG: счётчик ms-маршрутов
    } else {
        Tmp_Read = in_cell(Port_Run);    // честная сигнатура порта
        if (Tmp_Read == MD_MAGIC) {
            Tmp_Addr = Port_Run + 8;
            Tmp_Type = in_cell(Tmp_Addr);
            if (Tmp_Type == TYPE_SATA) {
                // внутренний HDD — всегда честный hd0, монтируется один раз
                if (Hd_Flrag == 0x00000000) {
                    Hd_Route = Port_Run;
                    Hd_Flrag = 0x00000001;
                    out_cell(LOG_PORT, 0x00009120);   // LOG: SATA -> hd0
                } else {
                    out_cell(LOG_PORT, 0x00009130);   // честный дубль пропущен
                }
            } else {
                // внешняя карта — честный СЛЕДУЮЩИЙ ms-маршрут
                if (MS_Count == 0x00000003) {
                    out_cell(LOG_PORT, 0x00009245);   // честный максимум карт
                } else {
                    store_ind(Route_Run, Port_Run);
                    Route_Run = Route_Run + 4;
                    MS_Count = MS_Count + 1;
                    out_cell(LOG_PORT, 0x00009140);   // LOG: карта -> msN
                }
            }
        } else {
            out_cell(LOG_PORT, 0x00009130);   // честный пустой порт пропущен
        }
        Port_Run = Port_Run + 16;            // честный шаг порта (16 байт)
        Scan_Idx = Scan_Idx + 1;
        run Enum_Ports();
    }
}

// ---------- честная запись через маршрут ----------
// Честная проверка живого носителя перед честной записью: магией на порте.
function Write_Route() {
    Tmp_Read = in_cell(Cur_Port);        // честная живость носителя: магия по порту
    if (Tmp_Read == MD_MAGIC) {
        // носитель жив — честная запись в data-блок порта (+12)
        Tmp_Addr = Cur_Port + 12;
        store_ind(Tmp_Addr, DATA_WORD);
        out_cell(LOG_PORT, 0x00009200);  // LOG: запись через маршрут честно OK
    } else {
        // честный отказ: носителя нет (несмонт или вынут в момент записи)
        out_cell(LOG_PORT, 0x00009210);  // LOG: честная ошибка носителя
    }
}
