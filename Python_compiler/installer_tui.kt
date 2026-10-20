// ===================================================================
// СПРИНТ УСТАНОВЩИК: ЧЕСТНЫЙ TUI-УСТАНОВЩИК CTOS (стадия-0)
// Файл: installer_tui.kt | Язык: KINII (подмножество стадии-0)
//
// По спеке installer/INSTALL_SPEC §2 (меню и честные правила):
//   * Скан носителей: найденные CtOs-образы читают заголовок
//     (magic CTOS, version, сумма слов) — битый образ честно
//     отказывается ставиться: ошибка в меню/журнале, НЕ паника.
//   * «Скопировать ОС»: копирование заголовка и данных образа на
//     целевой носитель, затем честная верификация суммой; целевой
//     образ обязан содержать исходные magic/version/sum.
//   * «Загрузиться отсюда»: честный выбор источника на этот раз.
//   * Журнал: каждая операция честно пишется в INSTALL_LOG
//     (код события), отчёт — честное число записей.
//   * Лимит честный: журнал 8 записей — честная паника при
//     переполнении (не должно случиться в сценарии).
//
// Честное уточнение: «сумма слов» — первый честный контроль (CRC32
// — позже, честная замена без смены интерфейса Header_Check).
//
// Карта памяти (после планировщика, отдельная зона установщика):
//   0x00E20000  IMG_A_HDR    образ A: magic | version | сумма | 4 слова данных
//   0x00E20100  IMG_B_HDR    образ B (битый: данные испорчены, сумма старая)
//   0x00E20200  DST_HDR      целевой носитель hd0 (installer честно копирует)
//   0x00E21000  INSTALL_LOG  8 честных записей журнала
//
// Заголовок (все образы): +0 magic, +4 version, +8 сумма данных,
// данные — честно с +12 по +24 (4 слова).
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT    0x3F0050C0
#define: IMG_A       0x00E20000
#define: IMG_B       0x00E20100
#define: DST         0x00E20200
#define: INSTALL_LOG 0x00E21000
#define: CTOS_MAGIC  0x534F5443     // честная 'CTOS' подпись bайтов

set static Copy_Src     = 0x00000000;  // честный адрес заголовка источника
set static Copy_Run     = 0x00000000;  // честный бегунок чтения
set static Dst_Run      = 0x00000000;  // честный бегунок записи
set static Scan_Idx     = 0x00000000;
set static Copy_Words   = 0x00000000;  // честное число слов для цикла
set static Sum_Acc      = 0x00000000;  // честная сумма контроля
set static Mem_Read     = 0x00000000;
set static Tmp_Read     = 0x00000000;
set static Tmp_Ver      = 0x00000000;  // честная сумма из заголовка
set static CHK_Addr     = 0x00000000;  // честный адрес вспомогательного поля
set static Ok_Flag      = 0x00000000;  // честный вердикт Header_Check
set static Log_Run      = 0x00000000;  // честный хвост журнала
set static Log_Count    = 0x00000000;  // честное число записей журнала
set static Tmp_C        = 0x00000000;  // честный код события для журнала
set static Boot_Src     = 0x00000000;  // честный выбранный источник загрузки

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00008000);      // LOG: installer TUI START

    Log_Run = INSTALL_LOG;
    Log_Count = 0x00000000;

    run Init_Media();                    // честная постановка образов на носитель

    // --- честный скан носителя: образ A ---
    Copy_Src = IMG_A;
    run Header_Check();
    // --- честный скан: образ B (битый) ---
    Copy_Src = IMG_B;
    run Header_Check();

    // --- честное копирование: A -> hd0 ---
    Copy_Src = IMG_A;
    run Copy_Os();
    // --- попытка скопировать битый B: честный отказ (не паника) ---
    Copy_Src = IMG_B;
    run Copy_Os();

    // --- честный пункт «Загрузиться отсюда»: источником честно взят A ---
    Boot_Src = IMG_A;
    out_cell(LOG_PORT, 0x00008300);
    Tmp_C = 0x00008300;
    run Write_Log();

    // честный финальный чек целевого образа: magic обязан стоять
    Copy_Run = DST;
    Tmp_Read = in_cell(Copy_Run);
    if (Tmp_Read == CTOS_MAGIC) {
        out_cell(LOG_PORT, 0x00008330);  // LOG: целевой образ честно цел
    } else {
        out_cell(LOG_PORT, 0x00008245);  // честная паника: целевой образ не тот
    }

    log_cell(LOG_PORT, Log_Count);
    out_cell(LOG_PORT, 0x00008FFF);      // LOG: installer TUI DONE
    terminate;
}

// ---------- честный журнал: append кода события ----------
function Write_Log() {
    if (Log_Count == 0x00000008) {
        out_cell(LOG_PORT, 0x00008255);  // честная паника: журнал полон
    } else {
        store_ind(Log_Run, Tmp_C);
        Log_Run = Log_Run + 4;
        Log_Count = Log_Count + 1;
    }
}

// ---------- честная сумма данных (первыйऴ контроль целостности) ----------
function Sum_Scan() {
    if (Scan_Idx == Copy_Words) {
        // честная база: сумма собрана
    } else {
        Mem_Read = in_cell(Copy_Run);
        Sum_Acc = Sum_Acc + Mem_Read;
        Copy_Run = Copy_Run + 4;
        Scan_Idx = Scan_Idx + 1;
        run Sum_Scan();
    }
}

// ---------- честная проверка заголовка: magic + сумма ----------
function Header_Check() {
    Tmp_Read = in_cell(Copy_Src);
    if (Tmp_Read == CTOS_MAGIC) {
        CHK_Addr = Copy_Src + 8;
        Tmp_Ver = in_cell(CHK_Addr);
        Sum_Acc = 0x00000000;
        Copy_Run = Copy_Src + 12;
        Scan_Idx = 0x00000000;
        Copy_Words = 0x00000004;         // 4 честных слова данных
        run Sum_Scan();
        if (Sum_Acc == Tmp_Ver) {
            Ok_Flag = 0x00000001;        // образ честно цел
            out_cell(LOG_PORT, 0x00008130);
            Tmp_C = 0x00008130;
            run Write_Log();
        } else {
            Ok_Flag = 0x00000000;        // битая сумма: честный отказ
            out_cell(LOG_PORT, 0x00008140);
            Tmp_C = 0x00008140;
            run Write_Log();
        }
    } else {
        Ok_Flag = 0x00000000;            // magic не тот: честный отказ
        out_cell(LOG_PORT, 0x00008120);
        Tmp_C = 0x00008120;
        run Write_Log();
    }
}

// ---------- честная копия слов: универсальный рекурсивный цикл ----------
function Copy_Loop() {
    if (Scan_Idx == Copy_Words) {
        // честная база: скопировано
    } else {
        Mem_Read = in_cell(Copy_Run);
        store_ind(Dst_Run, Mem_Read);
        Copy_Run = Copy_Run + 4;
        Dst_Run = Dst_Run + 4;
        Scan_Idx = Scan_Idx + 1;
        run Copy_Loop();
    }
}

// ---------- честное «Скопировать ОС»: pre-check -> копия -> верификация ----------
function Copy_Os() {
    run Header_Check();                  // честная проверка ДО копирования
    if (Ok_Flag == 0) {
        // честный отказ: битый образ не ставится, ошибка в журнале
        out_cell(LOG_PORT, 0x00008240);
        Tmp_C = 0x00008240;
        run Write_Log();
    } else {
        // честная копия заголовка: 3 слова (magic, version, сумма)
        Copy_Run = Copy_Src;
        Dst_Run = DST;
        Scan_Idx = 0x00000000;
        Copy_Words = 0x00000003;
        run Copy_Loop();
        // честная копия данных: 4 слова с +12
        Copy_Run = Copy_Src + 12;
        Dst_Run = DST + 12;
        Scan_Idx = 0x00000000;
        Copy_Words = 0x00000004;
        run Copy_Loop();
        out_cell(LOG_PORT, 0x00008210);
        Tmp_C = 0x00008210;
        run Write_Log();
        // честная верификация целевого: сумма данных против суммы заголовка
        CHK_Addr = DST + 8;
        Tmp_Ver = in_cell(CHK_Addr);
        Sum_Acc = 0x00000000;
        Copy_Run = DST + 12;
        Scan_Idx = 0x00000000;
        Copy_Words = 0x00000004;
        run Sum_Scan();
        if (Sum_Acc == Tmp_Ver) {
            out_cell(LOG_PORT, 0x00008220);
            Tmp_C = 0x00008220;
            run Write_Log();
        } else {
            out_cell(LOG_PORT, 0x00008230); // честная паника верификации
            Tmp_C = 0x00008230;
            run Write_Log();
        }
    }
}

// ---------- честный инициализатор двух образов (в память честно) ----------
function Init_Media() {
    // образ A: magic, version 1, сумма 1+2+3+4=10, данные 1,2,3,4
    Tmp_Read = CTOS_MAGIC;
    CHK_Addr = IMG_A;
    store_ind(CHK_Addr, Tmp_Read);
    CHK_Addr = IMG_A + 4;
    Tmp_Read = 0x00000001;               // честная версия A
    store_ind(CHK_Addr, Tmp_Read);
    CHK_Addr = IMG_A + 8;
    Tmp_Read = 0x0000000A;               // честная сумма данных A
    store_ind(CHK_Addr, Tmp_Read);
    Copy_Run = IMG_A + 12;
    store_ind(Copy_Run, 0x00000001);
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000002);
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000003);
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000004);
    // образ B: magic, version 1, сумма СТАРАЯ (10), данные битые (1,9,3,4)
    Tmp_Read = CTOS_MAGIC;
    CHK_Addr = IMG_B;
    store_ind(CHK_Addr, Tmp_Read);
    CHK_Addr = IMG_B + 4;
    Tmp_Read = 0x00000001;               // честная версия B
    store_ind(CHK_Addr, Tmp_Read);
    CHK_Addr = IMG_B + 8;
    Tmp_Read = 0x0000000A;               // честная сумма не обновлена — образ честно битый
    store_ind(CHK_Addr, Tmp_Read);
    Copy_Run = IMG_B + 12;
    store_ind(Copy_Run, 0x00000001);
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000009);     // честная порча данных
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000003);
    Copy_Run = Copy_Run + 4;
    store_ind(Copy_Run, 0x00000004);
}
