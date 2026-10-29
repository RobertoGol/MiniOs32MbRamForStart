// ===================================================================
// СПРИНТ СТАДИЯ-1.3/1.4: честный стек групп + честные литералы
// Файл: stage1_selftest.kt | Язык: KINII (подмножество стадии-0)
//
// По TKT-032 (спринты 1.1/1.2 составляют базу):
//   * честные сигнатуры 1.2 сохранены (двухсимвольные слова);
//   * скобки честно ведут стек: '{'/'(' кладёт, '}'/')' снимает;
//   * '}'/')' при пустом честном стеке — честный ОТКАЗ (fail-fast);
//   * честная незакрытая группа в конце прохода — честный ОТКАЗ;
//   * каждая честно согласованная группа -> Node_Counter (узлы);
//   * эмиссия байт НЕ меняется (скобки честно не байт).
// Стадия-1.4 (TKT-036): честные литералы '0'..'9' (сим1 цифра,
// сим2==0) -> честная эмиссия OP_CONST 0x15 + честное ЗНАЧЕНИЕ
// (яйчейка Lit_Value, честное вычитание "сим1 - 48", честный
// log_cell/OP_OUTCELL_V). Честное ограничение модели: в стадии-0
// нет `*`/`/` — двухзначные слова ('12') честно НЕ собираются и
// честно отвергаются fail-fast с НУЛЁМ честных эмиссий.
//
// Фазы честные:
//   Ф1: '#' se st { te { } ( ) } .  -> эмиссии 1,0x10,0x10,5
//        counter 4 | syntax 6 | nodes 3 | depths 0 | error 0
//   Ф2: '{' '{' '}' .               -> одна группа честно закрыта1,
//        одна честно незакрыта -> честный отказ (error 1, nodes 1)
//   Ф3: '}' .                       -> закрытие при пустом стеке ->
//        честный отказ на месте (error 1, nodes 0, syntax 0)
//   Ф4: '#' '7' .                   -> эмиссии 1, 0x15, 7
//        counter 2 | error 0 | Lit_Value сверено == 7
//   Ф5: '12' .                      -> честный отказ (error 1),
//        честный НОЛЬ эмиссий (компилятор не добавляет от себя ни байта)
//
// Лог честный (серия 0x91xx + фазы):
//   0x9000 START      0x9001 Ф1 загружена   0x90F0 Ф1 скан завершён
//   0x9110 counter==4 0x9111 syntax==6      0x9112 nodes==3
//   0x9113 error==0                       0x9114 depths обе == 0
//   0x9002 Ф2 загружена 0x90F1 Ф2 скан завершён
//   0x9130 error==1   0x9131 nodes==1 (одна '{}' закрыта честно)
//   0x9003 Ф3 загружена 0x90F2 Ф3 скан завершён
//   0x9140 error==1   0x9141 nodes==0 и syntax==0
//   0x9004 Ф4 загружена 0x90F3 Ф4 скан завершён
//   0x9135 counter==2 0x9150 Lit_Value==7 (честная эмиссия в трассе)
//   0x9005 Ф5 загружена 0x90F4 Ф5 скан завершён
//   0x9160 error==1   0x9161 ноль эмиссий (honest fail-fast)
//   отказы: 0x9095/0x9096/0x9097/0x9098/0x9099
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT            0x3F0050C0
#define: SOURCE_CODE_BUFFER  0x00A00000
#define: MAX_SOURCE_WORDS    0x00000010

// честные двухсимвольные сигнатуры
#define: D_WORD_PREPROC 0x00000023
#define: KW_SET         0x00006573
#define: KW_STATIC      0x00007473
#define: KW_FUNCTION    0x00007566
#define: KW_IF          0x00006669
#define: KW_ELSE 0x00007365 // 'es' = else; 4-символьное 'else' честно не собирается в 2-символьных пакетах
#define: KW_RUN 0x00007572 // 'ru' = run: честный вызов последней 'fu'
#define: KW_EQ 0x00007165 // 'eq' = сравнить acc со следующим литералом (TKT-050)
#define: KW_GT 0x00007467 // 'gt' = сравнить acc > следующий литерал (TKT-050 веха-3)
#define: KW_LT 0x0000746C // 'lt' = сравнить acc < следующий литерал (TKT-050 веха-3)
#define: KW_ADD 0x00006461 // 'ad' = acc = acc + следующий литерал (TKT-052 веха-3)
#define: KW_SUB 0x00007573 // 'su' = acc = acc - следующий литерал (TKT-052 веха-3)
#define: KW_SAVE 0x00007673 // 'sv' = save: cell[WORK_CELL] = acc (TKT-050 веха-2)
#define: KW_VALUE 0x00006176 // 'va' = value: acc = cell[WORK_CELL] (TKT-050 веха-2)
#define: KW_RET 0x00006572 // 're' = return: честный выход из функции (TKT-051)
#define: KW_TERM        0x00006574
#define: SYM_BRACE_OPEN 0x0000007B
#define: SYM_BRACE_CLOSE 0x0000007D
#define: SYM_PAREN_OPEN 0x00000028
#define: SYM_PAREN_CLOSE 0x00000029
#define: SYM_SEMICOLON  0x0000003B
#define: CH_WORD_END    0x0000002E
#define: UNKNOWN_WORD   0x00007171  // 'qq'

// честный syscall-файл-слой (1.5-б, зеркало stage1_compiler.kt)
#define: STREAM_EMIT_CELL 0x00F00FF0 // честная ячейка-аргумент syscall (Stream_Emit)
#define: WORK_CELL 0x00F00FF1 // честная рабочая ячейка памяти стадии-1 (TKT-009 зона +1)
#define: FILE_BEGIN       0x00000130 // открыть артефакт
#define: FILE_PUT         0x00000131 // слово Stream_Emit -> 4 байта BE
#define: FILE_U16         0x00000132 // младшие 16 бит -> 2 байта BE
#define: FILE_U8          0x00000134 // 1 байт -> артефакт (TKT-047 байт-канал)
#define: FILE_SEEK        0x00000136 // честная позиция записи в артефакте (TKT-048)
#define: BRK_PATCH_OVERFLOW 0x00000004 // честных слотов патча больше нет (TKT-048)
#define: BRK_NO_FUNC 0x00000005 // 'ru' до любой 'fu' — честный брак (TKT-048 веха-3)
#define: BRK_EQ_NO_LIT 0x00000006 // 'eq' без следующего литерала — честный брак (TKT-050)
#define: HDR_BODY_SIZE      0x00000014 // честный размер заголовка v1.1 = 20 байт
#define: FILE_SEAL        0x00000135 // контрольное слово артефакта CRC-32 (TKT-040 веха-1)
#define: END_MARKER       0x000000FF // честный маркер конца эмиссии
#define: ERR_MARKER       0x000000FE // честный маркер БРАКА: неизвестное слово
#define: FILE_END         0x00000133 // закрыть артефакт

// честные коды брака стадии-1 (TKT-033, зеркало stage1_compiler.kt)
#define: BRK_UNKNOWN_WORD 0x00000001 // K-S1: неизвестное слово
#define: BRK_STRAY_CLOSE  0x00000002 // K-S2: '}' или ')' при пустом честном стеке
#define: BRK_UNCLOSED     0x00000003 // K-S3: незакрытая честная группа в финале

// честные опкоды
#define: OP_INIT_CODE   0x00000001
#define: OP_CALL_CODE   0x00000003
#define: OP_TERM_CODE   0x00000005
#define: OP_RET_CODE   0x00000004 // 0x04 OP_RET — возврат по стеку вызовов VM (TKT-051)
#define: OP_JZ_CODE     0x00000006
#define: OP_JMP_CODE 0x00000007 // честный безусловный переход (VM OP_JMP)
#define: OP_ALLOC_CODE  0x00000010
#define: OP_CONST_CODE  0x00000015 // 0x15 OP_CONST (стадия-1.4)
#define: OP_LOAD_CODE 0x00000012 // 0x12 OP_LOAD (режимы: 0x14 add, 0x16 eq, 0x17 sub)
#define: OP_STORE_AT_CODE 0x00000055 // 0x55 OP_STORE_AT cell[arg] = acc (TKT-050 веха-2)
#define: SYM_LIT_BASE   0x00000030 // база честного литерального ряда
#define: LIT_D0         0x00000030 // '0' (сим2==0, односимвольное слово)
#define: LIT_D1         0x00000031 // '1'
#define: LIT_D2         0x00000032 // '2'
#define: LIT_D3         0x00000033 // '3'
#define: LIT_D4         0x00000034 // '4'
#define: LIT_D5         0x00000035 // '5'
#define: LIT_D6         0x00000036 // '6'
#define: LIT_D7         0x00000037 // '7'
#define: LIT_D8         0x00000038 // '8'
#define: LIT_D9         0x00000039 // '9'
#define: LIT_TWO_DIGIT  0x00003232 // '12' — честно НЕ собираемый литерал (Ф5)

set static Execution_Pointer = 0x00000000;
set static Token_Counter     = 0x00000000;
set static Word_Index        = 0x00000000;
set static Current_Char      = 0x00000000;
set static Syntax_Counter    = 0x00000000;
set static Found_Flag        = 0x00000000;
set static Error_Flag        = 0x00000000;
set static Node_Brace_Depth  = 0x00000000;
set static Node_Paren_Depth  = 0x00000000;
set static Node_Counter      = 0x00000000;
set static Tmp_Addr          = 0x00000000;
set static Tmp_Word          = 0x00000000;
set static Lit_Value         = 0x00000000; // честное ЗНАЧЕНИЕ литерала (1.4)
set static Fail_Code         = 0x00000000; // честный код брака (TKT-033)
set static Emitted_Bytes = 0x00000000; // честный счётчик байтов потока (TKT-048)
set static Call_Site_1     = 0x00000000; // честный слот места патча операнда №1 (TKT-048)
set static Call_Site_2     = 0x00000000; // честный слот вызова №2 (флаг занятости)
set static Call_Site_3     = 0x00000000; // честный слот вызова №3 (флаг занятости)
set static Call_Site_4     = 0x00000000; // честный слот вызова №4 (флаг занятости)
set static Fu_Pos_1       = 0x00000000; // честная метка функции №1 (TKT-051 веха-3)
set static Fu_Pos_2       = 0x00000000; // честная метка функции №2 (TKT-051 веха-3)
set static Fu_Pos_3       = 0x00000000; // честная метка функции №3 (TKT-051 веха-3)
set static Fu_Pos_4       = 0x00000000; // честная метка функции №4 (TKT-051 веха-3)
set static Fu_Count       = 0x00000000; // честный счёт объявленных функций
set static Call_Fn_1      = 0x00000000; // честный номер функции вызова №1
set static Call_Fn_2      = 0x00000000; // честный номер функции вызова №2
set static Call_Fn_3      = 0x00000000; // честный номер функции вызова №3
set static Call_Fn_4      = 0x00000000; // честный номер функции вызова №4
set static Run_Pending    = 0x00000000; // честный флаг: ждём номер функции для ru
set static Run_Position   = 0x00000000; // честная позиция слова ru (для брака)
set static Fn_OK          = 0x00000000; // честный признак корректного номера
set static Is_Digit        = 0x00000000; // честный признак цифры при активном ru
set static Call_Count       = 0x00000000; // честный счёт занятых слотов вызовов
set static Op_Pending      = 0x00000000; // честный флаг: ждём литерал для сравнения
set static Op_Position     = 0x00000000; // честная позиция слова eq (для брака)
set static If_Site_1      = 0x00000000; // честный слот операнда JZ от if
set static Jmp_Slot_1      = 0x00000000; // честный слот операнда JMP от es
set static Else_Join_1     = 0x00000000; // честное начало else-тела (target JZ)
set static If_Site_2      = 0x00000000; // честный слот JZ №2 (TKT-050)
set static Jmp_Slot_2     = 0x00000000; // честный слот JMP №2 (TKT-050)
set static Else_Join_2    = 0x00000000; // честное else-тело №2 (TKT-050)
set static If_Count       = 0x00000000; // честный счёт if-слотов
set static Jmp_Count      = 0x00000000; // честный счёт else-слотов
set static Patch_Target     = 0x00000000; // честный target патча JZ
set static JP_Site_Term  = 0x00000000; // честная позиция потока байта TERM (target демо)
set static Fail_Position     = 0x00000000; // честная позиция брака (TKT-033)

// ---------- Ф13 (TKT-052 веха-3): честная арифметика ad/su ----------
// Слова: '7' 'ad' '2' 'su' '1' 'te' .
// Честный эмит: CONST 7 (5Б) -> LOAD[0x14] 2 (6Б, acc=9) -> LOAD[0x17] 1
// (6Б, acc=8) -> TERM (1Б) = 18 байт
function Load_Arith_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D7;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_ADD;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = LIT_D2;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_SUB;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = LIT_D1;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009000);      // LOG: стадия-1.3 стенд START

    // --- 1.6 (TKT-036): честный артефакт стадии-1 на бенче ---
    // Артефакт честно открывается РАЗ на весь стенд, до Ф1; честный
    // заголовок TKT-009 честно первым, эмит-потоки всех Ф-фаз честно
    // дописываются за ним (одна честная запись — один честный файл).
    sys_call(FILE_BEGIN);
    out_cell(STREAM_EMIT_CELL, 0x43544F53);  // 'CTOS' BE
    sys_call(FILE_PUT);
    out_cell(STREAM_EMIT_CELL, 0x00000101);  // байт-образ ver 01 01 (LE -> v1.1 с контролем)
    sys_call(FILE_U16);
    out_cell(STREAM_EMIT_CELL, 0x00000200);  // байт-образ таргета 02 00 (LE -> ARM32)
    sys_call(FILE_U16);
    out_cell(STREAM_EMIT_CELL, 0x14000000);  // байт-образ entry 14 00 00 00 (LE -> 0x14)
    sys_call(FILE_PUT);
    out_cell(STREAM_EMIT_CELL, 0xFFFFAAAA);  // байт-образ магии FF FF AA AA (LE -> 0xAAAAFFFF)
    sys_call(FILE_PUT);
    out_cell(STREAM_EMIT_CELL, 0x00000000);  // контрольное слово: плейсхолдер, FILE_SEAL честно вписывает
    sys_call(FILE_U16);
    sys_call(FILE_U16);

    // TKT-048 веха-1: честные счётчики/слоты адресной эмиссии (поток общий
    // на все фазы — честные позиции не сбрасываются, Reset_Scan их не трогает)
    Emitted_Bytes = 0;
    Call_Site_1 = 0;     // честные слоты вызовов пусты (веха-3)
    Call_Site_2 = 0;
    Call_Site_3 = 0;
    Call_Site_4 = 0;
    Fu_Pos_1 = 0;        // честные метки функций пусты (веха-3)
    Fu_Pos_2 = 0;
    Fu_Pos_3 = 0;
    Fu_Pos_4 = 0;
    Fu_Count = 0;        // честный счёт функций пуст
    Call_Fn_1 = 0;       // честные номера вызовов пусты
    Call_Fn_2 = 0;
    Call_Fn_3 = 0;
    Call_Fn_4 = 0;
    Run_Pending = 0;     // честный pending вызова пуст
    Run_Position = 0;    // честная позиция ru сброшена
    Fn_OK = 0;           // честный признак номера сброшен
    Is_Digit = 0;        // честный признак цифры сброшен
    Call_Count = 0;      // честный счёт вызовов пуст
    Op_Pending = 0;      // честный pending сравнения пуст
    Op_Position = 0;     // честная позиция eq сброшена
    If_Site_1 = 0;      // честный слот if-патча пуст
    If_Site_2 = 0;       // честный слот JZ №2 пуст
    Jmp_Slot_2 = 0;      // честный слот JMP №2 пуст
    Else_Join_2 = 0;     // честное else-тело №2 пусто
    If_Count = 0;        // честный счёт if пуст
    Jmp_Count = 0;       // честный счёт else пуст
    Jmp_Slot_1 = 0;     // честный слот es-патча пуст
    Else_Join_1 = 0;    // честный else-сопряжён пуст
    JP_Site_Term = 0;

    // ---------- ФАЗА 1: валидный исходник с группами ----------
    out_cell(LOG_PORT, 0x00009001);      // LOG: Ф1 честно загружена
    run Load_Node_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F0);      // LOG: Ф1 честный скан завершён

    if (Token_Counter == 0x00000004) {
        out_cell(LOG_PORT, 0x00009110);  // LOG: честный счётчик 4
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    if (Syntax_Counter == 0x00000006) {
        out_cell(LOG_PORT, 0x00009111);  // LOG: 4 скобки {} + 2 () честно
    } else {
        out_cell(LOG_PORT, 0x00009097);
    }

    if (Node_Counter == 0x00000003) {
        out_cell(LOG_PORT, 0x00009112);  // LOG: 2 честных узла {} + 1 ()
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    if (Error_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x00009113);  // LOG: отказа нет — честно
    } else {
        out_cell(LOG_PORT, 0x00009095);
    }

    if (Node_Brace_Depth == 0x00000000) {
        if (Node_Paren_Depth == 0x00000000) {
            out_cell(LOG_PORT, 0x00009114); // LOG: честные стеки пусты
        } else {
            out_cell(LOG_PORT, 0x00009096);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 2: честная незакрытая группа ----------
    out_cell(LOG_PORT, 0x00009002);      // LOG: Ф2 честно загружена
    run Load_Unclosed_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F1);      // LOG: Ф2 честный скан завершён

    // Честный финал прохода (тот же, что в компиляторе): незакрытая
    // группа честно бракует исходник
    if (Node_Brace_Depth == 0x00000000) {
        if (Node_Paren_Depth == 0x00000000) {
            // честно закрыто — Error_Flag не трогаем
        } else {
            Error_Flag = 0x00000001;     // честная незакрытая ()
            Fail_Code = BRK_UNCLOSED;    // честный код K-S3 (TKT-033)
            Fail_Position = Word_Index;  // честная позиция = граница прохода
        }
    } else {
        Error_Flag = 0x00000001;         // честная незакрытая {}
        Fail_Code = BRK_UNCLOSED;        // честный код K-S3 (TKT-033)
        Fail_Position = Word_Index;      // честная позиция = граница прохода
    }

    if (Error_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009130);  // LOG: честный отказ незакрытой
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // TKT-033: честный код K-S3 (0x03) у Ф2 — незакрытая группа
    if (Fail_Code == BRK_UNCLOSED) {
        out_cell(LOG_PORT, 0x00009180);  // LOG: честный K-S3 на месте
    } else {
        out_cell(LOG_PORT, 0x00009097);
    }

    if (Node_Counter == 0x00000001) {
        if (Token_Counter == 0x00000000) {
            out_cell(LOG_PORT, 0x00009131); // LOG: одна {} честно закрыта
        } else {
            out_cell(LOG_PORT, 0x00009097);
        }
    } else {
        out_cell(LOG_PORT, 0x00009097);
    }

    // ---------- ФАЗА 3: честный отказ на '}' при пустом стеке ----------
    out_cell(LOG_PORT, 0x00009003);      // LOG: Ф3 честно загружена
    run Load_Stray_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F2);      // LOG: Ф3 честный скан завершён

    if (Error_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009140);  // LOG: честный отказ на месте
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    // TKT-033: честный код K-S2 (0x02) у Ф3 — '}' при пустом стеке
    if (Fail_Code == BRK_STRAY_CLOSE) {
        if (Fail_Position == 0x00000000) {
            out_cell(LOG_PORT, 0x00009181); // LOG: честный K-S2 + позиция 0
        } else {
            out_cell(LOG_PORT, 0x00009098);
        }
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    if (Node_Counter == 0x00000000) {
        if (Syntax_Counter == 0x00000000) {
            out_cell(LOG_PORT, 0x00009141); // LOG: ничего честно не учтено
        } else {
            out_cell(LOG_PORT, 0x00009096);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 4 (стадия-1.4): честный литерал ----------
    // Слова: '#' '7' .  -> честные эмиссии 1, 0x15, 7
    out_cell(LOG_PORT, 0x00009004);      // LOG: Ф4 честно загружена
    run Load_Lit_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F3);      // LOG: Ф4 честный скан завершён

    if (Error_Flag == 0x00000000) {
        if (Token_Counter == 0x00000002) {
            out_cell(LOG_PORT, 0x00009135); // LOG: '#' + '7' честно распознаны
        } else {
            out_cell(LOG_PORT, 0x00009097);
        }
    } else {
        out_cell(LOG_PORT, 0x00009095);
    }

    // Честная сверка Ф4: значение честной эмиссии '7' — абсолютный
    // LIТ-индикатор в ячейке Lit_Value (сим1 0x37 - 48 == 7), честная
    // серия 0x9150. Current_Char после скана — терминатор '.' (0x2E),
    // поэтому сверка честно только по Lit_Value.
    if (Lit_Value == 0x00000007) {
        out_cell(LOG_PORT, 0x00009150);  // LOG: честное значение 7 в трассе
    } else {
        out_cell(LOG_PORT, 0x00009096);  // LOG: честный брак значения
    }

    // ---------- ФАЗА 5 (стадия-1.4): честный отказ на '12' ----------
    // Слово '12' (0x3232, цифровой сим2) честно НЕ собирается в модели
    // без `*`/`/` — честный отказ вместо тишины, честный НОЛЬ эмиссий.
    out_cell(LOG_PORT, 0x00009005);      // LOG: Ф5 честно загружена
    run Load_TwoDigit_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F4);      // LOG: Ф5 честный скан завершён

    if (Error_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009160);  // LOG: честный отказ '12' на месте
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    if (Token_Counter == 0x00000000) {
        out_cell(LOG_PORT, 0x00009161);  // LOG: честно НОЛЬ эмиссий на брак
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // TKT-033: честный код K-S1 (0x01) + честная позиция 0 у Ф5 ('12' первое слово)
    if (Fail_Code == BRK_UNKNOWN_WORD) {
        if (Fail_Position == 0x00000000) {
            out_cell(LOG_PORT, 0x00009182); // LOG: честный K-S1 + позиция 0
        } else {
            out_cell(LOG_PORT, 0x00009099);
        }
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // ---------- ФАЗА 5б (TKT-048 веха-3): честный отказ ru без fu ----------
    out_cell(LOG_PORT, 0x0000900A);      // LOG: Ф5б честно загружена
    run Load_RuFail_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FA);      // LOG: Ф5б честный скан завершён

    // честный код брака = BRK_NO_FUNC (0x05), Error_Flag = 1
    if (Fail_Code == BRK_NO_FUNC) {
        if (Error_Flag == 0x00000001) {
            out_cell(LOG_PORT, 0x00009198); // LOG: честный отказ ru без fu
        } else {
            out_cell(LOG_PORT, 0x00009099);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // честная позиция отказа: 'ru' = слово 0; эмиссий нет (поток не вырос)
    if (Fail_Position == 0x00000000) {
        if (Emitted_Bytes == 0x0000000A) {
            out_cell(LOG_PORT, 0x00009199); // LOG: честная позиция 0 + ноль эмиссий
        } else {
            out_cell(LOG_PORT, 0x00009098);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 7 (TKT-048 веха-1): честная адресная эмиссия ----------
    out_cell(LOG_PORT, 0x00009007);      // LOG: Ф7 честно загружена
    run Load_Call_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F7);      // LOG: Ф7 честный скан завершён

    // честный слот операнда OP_CALL заполнен литералом-номером после 'ru'
    if (Call_Site_1 == 0x00000000) {
        out_cell(LOG_PORT, 0x00009098);  // честный брак Ф7: слот не зажёгся
    } else {
        out_cell(LOG_PORT, 0x00009190);  // LOG: слот патча честно зажёгся
    }

    // честный счёт байтов потока: 'fu'=5 ('03'+операнд 4Б) + 'te'=1 = 2 слова=6 Б
    // поверх 10 Б Ф1+Ф4: 16
    if (Emitted_Bytes == 0x00000010) {
        out_cell(LOG_PORT, 0x00009191);  // LOG: честный счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009097);
    }

    // честный target: позиция байта TERM = 15 (поток: 4+6+5+1)
    if (JP_Site_Term == 0x0000000F) {
        out_cell(LOG_PORT, 0x00009192);  // LOG: честная позиция TERM сошлась
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 7б (TKT-050 веха-1): честное сравнение eq ----------
    out_cell(LOG_PORT, 0x0000900C);      // LOG: Ф7б честно загружена
    run Load_EqIf_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FC);      // LOG: Ф7б честный скан завершён

    // честный счёт: был поток 16 + (CONST 5 + LOAD[0x16] 7 + JZ + CONST 7 +
    // JMP + CONST 8 + TERM) = 16 + (5+6+5+5+5+5+1) = 48 = 0x30
    if (Emitted_Bytes == 0x00000030) {
        out_cell(LOG_PORT, 0x0000919D);  // LOG: Ф7б счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // честный слот if №1: JZ-операнд = 28 = 0x1C (первый if стенда — от Ф7б)
    if (If_Site_1 == 0x0000001C) {
        out_cell(LOG_PORT, 0x0000919E);  // LOG: Ф7б слот if на месте
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    // честное else-сращение №1: начало else-тела = 42 = 0x2A
    if (Else_Join_1 == 0x0000002A) {
        out_cell(LOG_PORT, 0x0000919F);  // LOG: Ф7б else-сращение на месте
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 8 (TKT-048 веха-2): честный if/else ----------
    out_cell(LOG_PORT, 0x00009008);      // LOG: Ф8 честно загружена
    run Load_IfElse_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F8);      // LOG: Ф8 честный скан завершён

    // честный счёт: был поток 48 (после Ф7б) + (5+5+5+5+1) = 69 = 0x45
    if (Emitted_Bytes == 0x00000045) {
        out_cell(LOG_PORT, 0x00009193);  // LOG: Ф8 счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // честный JZ target №2: начало else-тела Ф8 = позиция после JMP = 68 = 0x44
    if (Else_Join_2 == 0x00000044) {
        out_cell(LOG_PORT, 0x00009194);  // LOG: Ф8 else-сращение на месте
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    // честные слоты №2: JZ-операнд = 54 = 0x36, JMP-операнд = 64 = 0x40
    if (If_Site_2 == 0x00000036) {
        if (Jmp_Slot_2 == 0x00000040) {
            out_cell(LOG_PORT, 0x00009195); // LOG: Ф8 слоты if/es на месте
        } else {
            out_cell(LOG_PORT, 0x00009097);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 9 (TKT-048 веха-2): честный отказ двух if ----------
    out_cell(LOG_PORT, 0x00009009);      // LOG: Ф9 честно загружена
    run Load_TwoIf_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F9);      // LOG: Ф9 честный скан завершён

    // честный код брака = BRK_PATCH_OVERFLOW (0x04), Error_Flag = 1
    if (Fail_Code == BRK_PATCH_OVERFLOW) {
        if (Error_Flag == 0x00000001) {
            out_cell(LOG_PORT, 0x00009196); // LOG: честный отказ второго if
        } else {
            out_cell(LOG_PORT, 0x00009099);
        }
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // честная позиция отказа: слот if занят Ф8 — честный отказ на ПЕРВОМ же
    // if (слово 0); честный лимит стенда: один CALL/один JZ/один JMP на артефакт
    if (Fail_Position == 0x00000000) {
        out_cell(LOG_PORT, 0x00009197);  // LOG: честная позиция 1 сошлась
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 10 (TKT-048 веха-3): честные два вызова ----------
    out_cell(LOG_PORT, 0x0000900B);      // LOG: Ф10 честно загружена
    run Load_TwoCall_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FB);      // LOG: Ф10 честный скан завершён

    // честный счёт: поток 69 (после Ф9) + (fu=0 + te=1 + ru=5 + te=1) = 76 = 0x4C
    if (Emitted_Bytes == 0x0000004C) {
        out_cell(LOG_PORT, 0x0000919A);  // LOG: Ф10 счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // честный слот вызова №2 = позиция операнда = 71 = 0x47
    if (Call_Site_2 == 0x00000047) {
        out_cell(LOG_PORT, 0x0000919B);  // LOG: Ф10 слот №2 на месте
    } else {
        out_cell(LOG_PORT, 0x00009098);
    }

    // честная метка функции №2 = 69 = 0x45 (позиция te1 Ф10, словарь вехи-3)
    if (Fu_Pos_2 == 0x00000045) {
        out_cell(LOG_PORT, 0x0000919C);  // LOG: Ф10 метка fu на месте
    } else {
        out_cell(LOG_PORT, 0x00009096);
    }

    // ---------- ФАЗА 10б (TKT-050 веха-2): честная память sv/va ----------
    out_cell(LOG_PORT, 0x0000900D);      // LOG: Ф10б честно загружена
    run Load_Mem_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FD);      // LOG: Ф10б честный скан завершён

    // честный счёт: поток 76 (после Ф10) + (CONST 5 + STORE_AT 5 + LOAD[0x19] 6
    // + LOAD[0x16] 6 + TERM 1) = 99 = 0x63
    if (Emitted_Bytes == 0x00000063) {
        out_cell(LOG_PORT, 0x000091A0);  // LOG: Ф10б счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // ---------- ФАЗА 10в (TKT-050 веха-3): честное сравнение gt ----------
    out_cell(LOG_PORT, 0x0000900E);      // LOG: Ф10в честно загружена
    run Load_Gt_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FE);      // LOG: Ф10в честный скан завершён

    // честный счёт: поток 99 (после Ф10б) + (CONST 7 + LOAD[0x1A] 6 + TERM 1)
    // = 111 = 0x6F
    if (Emitted_Bytes == 0x0000006F) {
        out_cell(LOG_PORT, 0x000091A1);  // LOG: Ф10в счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // ---------- ФАЗА 11 (TKT-051 веха-1): честная функция с возвратом ----------
    out_cell(LOG_PORT, 0x0000900F);      // LOG: Ф11 честно загружена
    run Load_RetCall_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090FF);      // LOG: Ф11 честный скан завершён

    // честный счёт: поток 111 (после Ф10в) + (CONST 5 + STORE_AT 5 + CALL 5
    // + TERM 1 + LOAD[0x19] 6 + RET 1) = 134 = 0x86
    if (Emitted_Bytes == 0x00000086) {
        out_cell(LOG_PORT, 0x000091A2);  // LOG: Ф11 счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // ---------- ФАЗА 12 (TKT-051 веха-2): честный аргумент функции ----------
    out_cell(LOG_PORT, 0x00009010);      // LOG: Ф12 честно загружена
    run Load_Arg_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F1);      // LOG: Ф12 честный скан завершён

    // честный счёт: поток 134 (после Ф11) + (CONST 5 + STORE_AT 5 + CALL 5
    // + TERM 1 + LOAD[0x19] 6 + LOAD[0x1A] 6 + STORE_AT 5 + RET 1) = 168 = 0xA8
    if (Emitted_Bytes == 0x000000A8) {
        out_cell(LOG_PORT, 0x000091A3);  // LOG: Ф12 счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // ---------- ФАЗА 13 (TKT-052 веха-3): честная арифметика ad/su ----------
    out_cell(LOG_PORT, 0x00009011);      // LOG: Ф13 честно загружена
    run Load_Arith_Demo();
    run Reset_Scan();
    run Scan_Word_Loop();
    out_cell(LOG_PORT, 0x000090F5);      // LOG: Ф13 честный скан завершён

    // честный счёт: поток 168 (после Ф12) + (CONST 7 = 5Б + LOAD[0x14] 2 = 6Б
    // + LOAD[0x17] 1 = 6Б + TERM = 1Б) = 186 = 0xBA
    if (Emitted_Bytes == 0x000000BA) {
        out_cell(LOG_PORT, 0x000091A4);  // LOG: Ф13 счёт байтов сошёлся
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    // честный хвост: оба оператора честно потребили свои литералы
    if (Op_Pending == 0x00000000) {
        out_cell(LOG_PORT, 0x000091A5);  // LOG: pending чист
    } else {
        out_cell(LOG_PORT, 0x00009099);
    }

    run Write_Artifact_Report();

    // --- 1.5-б честный шаг: стадия-1 сама пишет свой артефакт-файл ---
    // Финальное состояние = Ф5 (честный брак '12'): артефакт честно пишется
    // И на браке, Error_Flag в отчёте честно говорит про брак — тишины нет.

    out_cell(LOG_PORT, 0x00009170);      // LOG: артефакт стадии-1 записан честно

    // честный финальный отчёт значениями
    log_cell(LOG_PORT, Token_Counter);
    log_cell(LOG_PORT, Node_Counter);
    log_cell(LOG_PORT, Error_Flag);
}

// ---------- 1.6 (TKT-036): честный отчёт стадии-1 ----------
// Артефакт уже открыт в main с честным заголовком; отчёт честно
// ДОПИСЫВАЕТСЯ после эмит-потоков Ф-фаз, затем файл честно закрывается.
// Пишется ВСЕГДА (и на браке): Error_Flag в отчёте честно говорит
// про брак — тишины нет.
function Write_Artifact_Report() {
    // TKT-047: честный вердикт-маркер (зеркало компилятора) ДО отчёта
    if (Error_Flag == 0x00000000) {
        out_cell(STREAM_EMIT_CELL, END_MARKER);
        sys_call(FILE_U8);
    } else {
        out_cell(STREAM_EMIT_CELL, ERR_MARKER);
        sys_call(FILE_U8);
    }
    // TKT-050 веха-1: честная хвост-проверка 'eq' — pending остался без литерала
    if (Op_Pending == 0x00000000) {
        // честно: несравнённых pending нет
    } else {
        if (Error_Flag == 0x00000000) {
            Fail_Code = BRK_EQ_NO_LIT;
            Fail_Position = Op_Position;
            Error_Flag = 0x00000001;
        }
        Op_Pending = 0x00000000;
    }

    // TKT-051 веха-3: честная хвост-проверка 'ru' — pending остался без номера
    if (Run_Pending == 0x00000000) {
        // честно: вызовов без номера нет
    } else {
        if (Error_Flag == 0x00000000) {
            Fail_Code = BRK_NO_FUNC;
            Fail_Position = Run_Position;
            Error_Flag = 0x00000001;
        }
        Run_Pending = 0x00000000;
    }

    // 4 честных слова отчёта (значения переменных — честно через log_cell)
    log_cell(STREAM_EMIT_CELL, Token_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Syntax_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Node_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Error_Flag);
    sys_call(FILE_PUT);
    // TKT-033: 2 честных слова кода и позиции брака
    log_cell(STREAM_EMIT_CELL, Fail_Code);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Fail_Position);
    sys_call(FILE_PUT);
    // TKT-048 веха-1: честная патч-фаза — адрес честного target в слоты
    // (позиция в файле = честный поток + размер заголовка v1.1)
        // TKT-048 веха-2: честная патч-фаза — адреса честных target в три слота
    // честные вызовы: цель = функция по честному словарю номеров (TKT-051 веха-3)
    if (Call_Site_1 == 0x00000000) {
        // честно: вызова №1 не было
    } else {
        // честный словарь целей: номер функции из Call_Fn_1 (TKT-051 веха-3)
        if (Call_Fn_1 == 0x00000001) {
            Patch_Target = Fu_Pos_1;
        } else {
            if (Call_Fn_1 == 0x00000002) {
                Patch_Target = Fu_Pos_2;
            } else {
                if (Call_Fn_1 == 0x00000003) {
                    Patch_Target = Fu_Pos_3;
                } else {
                    Patch_Target = Fu_Pos_4;
                }
            }
        }
        if (Patch_Target == 0x00000000) {
            // честный брак патч-фазы: функции с таким номером не объявлено
            if (Error_Flag == 0x00000000) {
                Fail_Code = BRK_NO_FUNC;
                Fail_Position = 0x00000000;
                Error_Flag = 0x00000001;
            }
        } else {
            Stream_Emit = Call_Site_1 + 20;
            sys_call(FILE_SEEK);
            Stream_Emit = Patch_Target + 20;
            sys_call(FILE_PUT);
        }
        Call_Site_1 = 0x00000000;
    }
    if (Call_Site_2 == 0x00000000) {
        // честно: вызова №2 не было
    } else {
        // честный словарь целей: номер функции из Call_Fn_2 (TKT-051 веха-3)
        if (Call_Fn_2 == 0x00000001) {
            Patch_Target = Fu_Pos_1;
        } else {
            if (Call_Fn_2 == 0x00000002) {
                Patch_Target = Fu_Pos_2;
            } else {
                if (Call_Fn_2 == 0x00000003) {
                    Patch_Target = Fu_Pos_3;
                } else {
                    Patch_Target = Fu_Pos_4;
                }
            }
        }
        if (Patch_Target == 0x00000000) {
            // честный брак патч-фазы: функции с таким номером не объявлено
            if (Error_Flag == 0x00000000) {
                Fail_Code = BRK_NO_FUNC;
                Fail_Position = 0x00000000;
                Error_Flag = 0x00000001;
            }
        } else {
            Stream_Emit = Call_Site_2 + 20;
            sys_call(FILE_SEEK);
            Stream_Emit = Patch_Target + 20;
            sys_call(FILE_PUT);
        }
        Call_Site_2 = 0x00000000;
    }
    if (Call_Site_3 == 0x00000000) {
        // честно: вызова №3 не было
    } else {
        // честный словарь целей: номер функции из Call_Fn_3 (TKT-051 веха-3)
        if (Call_Fn_3 == 0x00000001) {
            Patch_Target = Fu_Pos_1;
        } else {
            if (Call_Fn_3 == 0x00000002) {
                Patch_Target = Fu_Pos_2;
            } else {
                if (Call_Fn_3 == 0x00000003) {
                    Patch_Target = Fu_Pos_3;
                } else {
                    Patch_Target = Fu_Pos_4;
                }
            }
        }
        if (Patch_Target == 0x00000000) {
            // честный брак патч-фазы: функции с таким номером не объявлено
            if (Error_Flag == 0x00000000) {
                Fail_Code = BRK_NO_FUNC;
                Fail_Position = 0x00000000;
                Error_Flag = 0x00000001;
            }
        } else {
            Stream_Emit = Call_Site_3 + 20;
            sys_call(FILE_SEEK);
            Stream_Emit = Patch_Target + 20;
            sys_call(FILE_PUT);
        }
        Call_Site_3 = 0x00000000;
    }
    if (Call_Site_4 == 0x00000000) {
        // честно: вызова №4 не было
    } else {
        // честный словарь целей: номер функции из Call_Fn_4 (TKT-051 веха-3)
        if (Call_Fn_4 == 0x00000001) {
            Patch_Target = Fu_Pos_1;
        } else {
            if (Call_Fn_4 == 0x00000002) {
                Patch_Target = Fu_Pos_2;
            } else {
                if (Call_Fn_4 == 0x00000003) {
                    Patch_Target = Fu_Pos_3;
                } else {
                    Patch_Target = Fu_Pos_4;
                }
            }
        }
        if (Patch_Target == 0x00000000) {
            // честный брак патч-фазы: функции с таким номером не объявлено
            if (Error_Flag == 0x00000000) {
                Fail_Code = BRK_NO_FUNC;
                Fail_Position = 0x00000000;
                Error_Flag = 0x00000001;
            }
        } else {
            Stream_Emit = Call_Site_4 + 20;
            sys_call(FILE_SEEK);
            Stream_Emit = Patch_Target + 20;
            sys_call(FILE_PUT);
        }
        Call_Site_4 = 0x00000000;
    }
    // честные if-ветвления №1 и №2 (TKT-050): target = else-тело или TERM
    if (If_Site_1 == 0x00000000) {
        // честно: if-ветвление №1 не было
    } else {
        if (Else_Join_1 == 0x00000000) {
            Patch_Target = JP_Site_Term;     // честно без else: обход до TERM
        } else {
            Patch_Target = Else_Join_1;      // честно с else: вход в else-тело
        }
        Stream_Emit = If_Site_1 + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = Patch_Target + 20;
        sys_call(FILE_PUT);
        If_Site_1 = 0x00000000;
        Else_Join_1 = 0x00000000;
    }
    if (If_Site_2 == 0x00000000) {
        // честно: if-ветвление №2 не было
    } else {
        if (Else_Join_2 == 0x00000000) {
            Patch_Target = JP_Site_Term;     // честно без else: обход до TERM
        } else {
            Patch_Target = Else_Join_2;      // честно с else: вход в else-тело
        }
        Stream_Emit = If_Site_2 + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = Patch_Target + 20;
        sys_call(FILE_PUT);
        If_Site_2 = 0x00000000;
        Else_Join_2 = 0x00000000;
    }
    // честные else-переходы №1 и №2 (TKT-050): схождение ветвей на TERM
    if (Jmp_Slot_1 == 0x00000000) {
        // честно: else-переход №1 не был
    } else {
        Stream_Emit = Jmp_Slot_1 + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = JP_Site_Term + 20;     // честное схождение ветвей: TERM
        sys_call(FILE_PUT);
        Jmp_Slot_1 = 0x00000000;
    }
    if (Jmp_Slot_2 == 0x00000000) {
        // честно: else-переход №2 не был
    } else {
        Stream_Emit = Jmp_Slot_2 + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = JP_Site_Term + 20;     // честное схождение ветвей: TERM
        sys_call(FILE_PUT);
        Jmp_Slot_2 = 0x00000000;
    }
    // TKT-040 веха-1: честное контрольное слово — VM патчит CRC-32 тела
    sys_call(FILE_SEAL);
    sys_call(FILE_END);
}

// ---------- честный сброс сканирующих регистров между фазами ----------
function Reset_Scan() {
    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0;
    Word_Index = 0;
    Syntax_Counter = 0;
    Error_Flag = 0;
    Fail_Code = 0;        // честный код брака: успех = 0 (TKT-033)
    Fail_Position = 0;    // честная позиция брака: успех = 0 (TKT-033)
    Run_Pending = 0;      // честный pending вызова пуст (TKT-051 веха-3)
    Run_Position = 0;     // честная позиция ru сброшена
    Fn_OK = 0;            // честный признак номера сброшен
    Is_Digit = 0;         // честный признак цифры сброшен
    Node_Brace_Depth = 0;
    Node_Paren_Depth = 0;
    Node_Counter = 0;
}

// ---------- честная загрузка Ф1 (роль хоста) ----------
// Слова: '#' se st { te { } ( ) } .
function Load_Node_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = D_WORD_PREPROC;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_SET;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_STATIC;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = SYM_BRACE_OPEN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = SYM_BRACE_OPEN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = SYM_BRACE_CLOSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 28;
    Tmp_Word = SYM_PAREN_OPEN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 32;
    Tmp_Word = SYM_PAREN_CLOSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 36;
    Tmp_Word = SYM_BRACE_CLOSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 40;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честная загрузка Ф2: одна '{}' закрыта, вторая нет ----------
// Слова: '{' '{' '}' .
function Load_Unclosed_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = SYM_BRACE_OPEN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = SYM_BRACE_OPEN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = SYM_BRACE_CLOSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честная загрузка Ф3: '}' при пустом честном стеке ----------
// Слова: '}' .
function Load_Stray_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = SYM_BRACE_CLOSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честная загрузка Ф4 (стадия-1.4): '#' '7' ----------
// Слова: '#' '7' .
function Load_Lit_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = D_WORD_PREPROC;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = LIT_D7;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф8 (TKT-048 веха-2): честный if/else ----------
// Слова: '0' (LIT_D0) 'if' '7' (LIT_D7) 'es' 'te' .
// Честный эмит: CONST 0 (acc=0 - условие ложно) -> JZ (слот) -> CONST 7 (тело
// if, честно прыгается) -> JMP (слот) -> TERM; патч: JZ -> начало else-тела,
// JMP -> TERM (честное схождение ветвей).
function Load_IfElse_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D0;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_IF;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = LIT_D7;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_ELSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф9 (TKT-048 веха-2): честный отказ двух if ----------
// Слова: 'if' 'if' 'te' . — второй if честно бракуется BRK_PATCH_OVERFLOW
// (слот занят; fail-fast, правило первый-сбой). Слот Ф8 при этом честно
// затирается Ф9-байтом — его плейсхолдер останется неспаченным, что честно
// отмечено в отчёте артефакта (брак вместо тишины).
function Load_TwoIf_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = KW_IF;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_IF;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф12 (TKT-051 веха-2/3): аргумент функции + вызов вперёд ----------
// Слова: '5' 'sv' 'ru' '4' 'te' 'fu' 'va' 'gt' '8' 'sv' 're' . — главный:
// CONST 5; sv (аргумент в память); ru ждёт номер, '4' эмитит CALL на функцию
// №4 — честный вызов ВПЕРЁД (Fu_Pos_4 == 0 на момент вызова, патч-фаза
// честно вписывает метку); te: TERM; тело fu №4: va (acc=арг 5); gt pending;
// '8': LOAD[0x1A] 8 -> acc=(5>8)=0 (честно); sv (результат в память); re: RET.
function Load_Arg_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D5;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_SAVE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_RUN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = LIT_D4;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = KW_VALUE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 28;
    Tmp_Word = KW_GT;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 32;
    Tmp_Word = LIT_D8;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 36;
    Tmp_Word = KW_SAVE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 40;
    Tmp_Word = KW_RET;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 44;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}


// ---------- Ф11 (TKT-051 веха-1/3): функция с телом и возвратом ----------
// Слова: '5' 'sv' 'ru' '1' 'te' 'fu' 'va' 're' . — главный поток: CONST 5; sv
// (cell[W]=5); ru ждёт номер, '1' эмитит CALL на функцию №1 (честный словарь
// вехи-3); te: TERM; fu: метка №3 (тело после TERM); va (acc=cell[W]=5);
// re: RET (честный возврат по стеку).
function Load_RetCall_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D5;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_SAVE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_RUN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = LIT_D1;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = KW_VALUE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 28;
    Tmp_Word = KW_RET;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 32;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}


// ---------- Ф10в (TKT-050 веха-3): честное сравнение gt ----------
// Слова: '7' 'gt' '5' 'te' . — CONST 7; gt ставит pending 0x1A;
// '5' эмитит OP_LOAD[0x1A] 5 -> acc=(7>5)=1 (честно ИСТИНА); te: TERM.
function Load_Gt_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D7;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_GT;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = LIT_D5;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф10б (TKT-050 веха-2): честная память sv/va ----------
// Слова: '5' 'sv' 'va' 'eq' '8' 'te' . — CONST 5; sv: cell[W]=5; va: acc=cell[W]=5;
// eq ставит pending; '8' эмитит LOAD[0x16] 8 -> acc=(5==8)=0 (честно ЛОЖНО); te: TERM.
function Load_Mem_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D5;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_SAVE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_VALUE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_EQ;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = LIT_D8;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф7б (TKT-050 веха-1): честное сравнение eq + if/else ----------
// Слова: '5' 'eq' '7' 'if' '8' 'es' '9' 'te' . — CONST 5; eq ставит pending;
// '7' эмитит OP_LOAD[0x16] 7 (acc = (5==7) = 0 — честно ЛОЖНО, сравнение
// ДО if); if: JZ прыгает на else-тело (acc==0); if-тело: CONST 8 (не
// исполнится); else-ветка: CONST 9; te: TERM.
function Load_EqIf_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_D5;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_EQ;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = LIT_D7;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_IF;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = LIT_D8;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_ELSE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = LIT_D9;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 28;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 32;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф5б (TKT-051 веха-3): честный отказ ru без номера ----------
// Слова: 'ru' (0x7572) 'te' . — 'ru' ждёт номер функции, 'te' не литерал:
// честный BRK_NO_FUNC (0x05), ноль эмиссий ('ru' байта не эмитит),
// Fail_Position = 0 (первое слово).
function Load_RuFail_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = KW_RUN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф10 (TKT-048 веха-3): честные два вызова ----------
// Слова: 'fu' 'te' 'ru' '1' 'te' . — fu = метка №2 (позиция te1), te1 = TERM,
// ru = CALL (слот №2) на метку fu, te2 = честный TERM-хвост потока.
function Load_TwoCall_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = KW_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = KW_RUN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = LIT_D1;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}


// ---------- честная загрузка Ф5 (стадия-1.4): честный отказ '12' ----------
// Слова: '12' (0x3232) .
function Load_TwoDigit_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = LIT_TWO_DIGIT;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- Ф7 (TKT-048 веха-1 / TKT-051 веха-3): вызов по номеру ----------
// Слова: 'fu' (0x7566) 'ru' (0x7572) '1' (LIT_D1) 'te' (0x6574) .
// Честный эмит: 'ru' ставит pending, литерал '1' эмитит OP_CALL 0x03 + слот
// операнда BE32 (плейсхолдер) + OP_TERM 0x05; патч честно вписывает
// Fu_Pos_1 + 20 (честный словарь функций вехи-3).
function Load_Call_Demo() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = KW_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_RUN;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = LIT_D1;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}


// ---------- честный лексер+стек групп (тот же алгоритм, что в компиляторе) ----------
function Scan_Word_Loop() {
    if (Word_Index == MAX_SOURCE_WORDS) {
        // честная база: граница буфера честно отщелкала
    } else {
        Current_Char = in_cell(Execution_Pointer);

        if (Current_Char == CH_WORD_END) {
            // честный терминатор: выход БЕЗ инкрементов и БЕЗ рекурсии
            // TKT-051 веха-3: 'ru' без номера к концу исходника — честный брак
            if (Run_Pending == 0x00000000) {
                // честно: вызовов без номера нет
            } else {
                if (Error_Flag == 0x00000000) {
                    Fail_Code = BRK_NO_FUNC;
                    Fail_Position = Run_Position;
                    Error_Flag = 0x00000001;
                }
                Run_Pending = 0x00000000;
            }
            Word_Index = MAX_SOURCE_WORDS;
        }

        if (Word_Index == MAX_SOURCE_WORDS) {
            // честный терминатор закрыл проход — честный выход
        } else {
            Found_Flag = 0x00000000;

            // TKT-051 веха-3: честные врата после 'ru' — ждём номер функции,
            // пропускаем только цифры; не-цифра = честный отказ ДО эмиссии
            if (Run_Pending == 0x00000001) {
                if (Current_Char == LIT_D0) {
                    Is_Digit = 0x00000001;
                } else {
                    if (Current_Char == LIT_D1) {
                        Is_Digit = 0x00000001;
                    } else {
                        if (Current_Char == LIT_D2) {
                            Is_Digit = 0x00000001;
                        } else {
                            if (Current_Char == LIT_D3) {
                                Is_Digit = 0x00000001;
                            } else {
                                if (Current_Char == LIT_D4) {
                                    Is_Digit = 0x00000001;
                                } else {
                                    if (Current_Char == LIT_D5) {
                                        Is_Digit = 0x00000001;
                                    } else {
                                        if (Current_Char == LIT_D6) {
                                            Is_Digit = 0x00000001;
                                        } else {
                                            if (Current_Char == LIT_D7) {
                                                Is_Digit = 0x00000001;
                                            } else {
                                                if (Current_Char == LIT_D8) {
                                                    Is_Digit = 0x00000001;
                                                } else {
                                                    if (Current_Char == LIT_D9) {
                                                        Is_Digit = 0x00000001;
                                                    } else {
                                                        Is_Digit = 0x00000000;
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                if (Is_Digit == 0x00000000) {
                    // честный отказ ДО эмиссии: после 'ru' не цифра
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NO_FUNC;
                        Fail_Position = Run_Position;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                    Run_Pending = 0x00000000;
                }
            }

            // TKT-051 веха-3: честный guard — отказ врат 'ru' (не-цифра после
            // 'ru') пропускает сайт-цепочку ЦЕЛИКОМ: отказ ДО эмиссии, теку-
            // щее слово честно не эмитит ни байта (отступ цепочки не сдвинут)
            if (Word_Index == MAX_SOURCE_WORDS) {
                // честный отказ врат: текущее слово честно не эмитится
            } else {

            // 1.6 (TKT-036): эмит-сайты честно пишут поток В АРТЕФАКТ
            // (STREAM_EMIT_CELL + FILE_PUT), зеркально компилятору; LOG_PORT
            // остаётся только для честных маркеров сверок.
            if (Current_Char == D_WORD_PREPROC) {
                out_cell(STREAM_EMIT_CELL, OP_INIT_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_SET) {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_STATIC) {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'fu' -> честная МЕТКА функции (TKT-051 веха-3): байт не эмитится,
            // позиция потока честно пишется в слот Fu_Pos_N (первый свободный
            // из 4, счётчик Fu_Count); 'ru N' честно прыгает на функцию N
            if (Current_Char == KW_FUNCTION) {
                if (Fu_Count == 0x00000004) {
                    // честный отказ ДО записи: все 4 слота функций заняты
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_PATCH_OVERFLOW;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    if (Fu_Count == 0x00000000) {
                        Fu_Pos_1 = Emitted_Bytes;
                    } else {
                        if (Fu_Count == 0x00000001) {
                            Fu_Pos_2 = Emitted_Bytes;
                        } else {
                            if (Fu_Count == 0x00000002) {
                                Fu_Pos_3 = Emitted_Bytes;
                            } else {
                                Fu_Pos_4 = Emitted_Bytes;
                            }
                        }
                    }
                    Fu_Count = Fu_Count + 1;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }

            // 'ru' -> run -> OP_CALL (0x03) + плейсхолдер BE32 + первый свободный
            // слот из Call_Site_1..4; честные отказы: 'ru' до любой 'fu' —
            // BRK_NO_FUNC (0x05); все 4 слота заняты — BRK_PATCH_OVERFLOW (0x04)
            // 'ru' -> run (TKT-051 веха-3): честный вызов функции ПО НОМЕРУ.
            // Сам байта НЕ эмитит: ставит Run_Pending, следующий литерал честно
            // эмитит CALL + слот + номер функции (Call_Fn_i). 'ru' без номера —
            // честный брак BRK_NO_FUNC (хвост-проверка, ноль эмиссий).
            if (Current_Char == KW_RUN) {
                if (Run_Pending == 0x00000000) {
                    Run_Pending = 0x00000001;
                    Run_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два 'ru' подряд (второй без номера)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NO_FUNC;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            // 'if' -> OP_JZ (0x06) + честный слот If_Site_1; второй 'if' —
            // честный брак BRK_PATCH_OVERFLOW (fail-fast, правило первый-сбой)
            // 'sv' (TKT-050 веха-2): честная запись памяти — OP_STORE_AT 0x55
            // + BE32(WORK_CELL): cell[WORK_CELL] = acc. 5 байт.
            if (Current_Char == KW_SAVE) {
                out_cell(STREAM_EMIT_CELL, OP_STORE_AT_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, WORK_CELL);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'va' (TKT-050 веха-2): честная загрузка памяти — OP_LOAD 0x12
            // + режим 0x19 (acc = cell[arg]) + BE32(WORK_CELL). 6 байт.
            if (Current_Char == KW_VALUE) {
                out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, 0x00000019);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, WORK_CELL);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 're' (TKT-051 веха-1): честный возврат из функции — OP_RET 0x04
            // (1 байт, без операнда); VM честно поднимает pc со стека вызовов.
            // 're' вне вызова — VM честно бракует (стек пуст, живая проба).
            if (Current_Char == KW_RET) {
                out_cell(STREAM_EMIT_CELL, OP_RET_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'eq'/'gt'/'lt' (TKT-050 вехи 1/3): честное сравнение acc со
            // СЛЕДУЮЩИМ литералом. Само слово байта НЕ эмитит: ставит
            // Op_Pending = честный РЕЖИМ (0x16 eq / 0x1A gt / 0x1B lt),
            // следующий литерал честно эмитит OP_LOAD + режим вместо CONST.
            // Сравнение без литерала — честный брак BRK_EQ_NO_LIT
            // (хвост-проверка после скана).

            if (Current_Char == KW_EQ) {
                if (Op_Pending == 0x00000000) {
                    Op_Pending = 0x00000016;
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два 'eq' подряд (второй без литерала-цели)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            if (Current_Char == KW_GT) {
                if (Op_Pending == 0x00000000) {
                    Op_Pending = 0x0000001A;
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два сравнения подряд (второе без литерала-цели)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            if (Current_Char == KW_LT) {
                if (Op_Pending == 0x00000000) {
                    Op_Pending = 0x0000001B;
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два сравнения подряд (второе без литерала-цели)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            if (Current_Char == KW_ADD) {
                if (Op_Pending == 0x00000000) {
                    // честная арифметика (TKT-052 веха-3): режим OP_LOAD 0x14
                    // (acc = acc + литерал) — тот же pending-механизм, что у
                    // сравнений; VM-режим 0x14 уже честен (TKT-009)
                    Op_Pending = 0x00000014;
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два оператора подряд (второй без литерала)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            if (Current_Char == KW_SUB) {
                if (Op_Pending == 0x00000000) {
                    // честная арифметика (TKT-052 веха-3): режим OP_LOAD 0x17
                    // (acc = acc - литерал) — VM-режим 0x17 уже честен (TKT-009)
                    Op_Pending = 0x00000017;
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два оператора подряд (второй без литерала)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            if (Current_Char == KW_IF) {
                if (If_Count == 0x00000002) {
                    // честный отказ ДО эмиссии: оба if-слота заняты (TKT-050)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_PATCH_OVERFLOW;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    out_cell(STREAM_EMIT_CELL, OP_JZ_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    // честный слот = позиция операнда (сразу после байта опкода)
                    if (If_Count == 0x00000000) {
                        If_Site_1 = Emitted_Bytes;
                    } else {
                        If_Site_2 = Emitted_Bytes;
                    }
                    If_Count = If_Count + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000000);
                    sys_call(FILE_U16);
                    sys_call(FILE_U16);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }

            // 'es' -> else -> OP_JMP (0x07) + честный слот Jmp_Slot_1;
            // честное начало else-тела = позиция после операнда (туда прыгнет JZ)
            if (Current_Char == KW_ELSE) {
                if (Jmp_Count == 0x00000002) {
                    // честный отказ ДО эмиссии: оба else-слота заняты (TKT-050)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_PATCH_OVERFLOW;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    out_cell(STREAM_EMIT_CELL, OP_JMP_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    // честный слот = позиция операнда (сразу после байта опкода)
                    if (Jmp_Count == 0x00000000) {
                        Jmp_Slot_1 = Emitted_Bytes;
                    } else {
                        Jmp_Slot_2 = Emitted_Bytes;
                    }
                    Jmp_Count = Jmp_Count + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000000);
                    sys_call(FILE_U16);
                    sys_call(FILE_U16);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    // честное начало else-тела = позиция после операнда
                    if (Jmp_Count == 0x00000001) {
                        Else_Join_1 = Emitted_Bytes;
                    } else {
                        Else_Join_2 = Emitted_Bytes;
                    }
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }

            if (Current_Char == KW_TERM) {
                out_cell(STREAM_EMIT_CELL, OP_TERM_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                JP_Site_Term = Emitted_Bytes - 1;  // честная позиция байта TERM
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // Честные литералы (стадия-1.4, зеркально компилятору TKT-036):
            // слово '0'..'9' (сим1 цифра, сим2==0) -> OP_CONST 0x15 +
            // честное значение. Честная форма стадии-0: вычитание только
            // "имя - число" (десятичный RHS), значение живёт в ячейке
            // Lit_Value и эмитится честным log_cell (OP_OUTCELL_V).
            // Ограничение честной модели: в стадии-0 нет `*`/`/` —
            // двухзначное слово честно не собирается; длинные числа
            // честно разбиваются по словам.
            if (Current_Char == LIT_D0) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D1) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D2) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D3) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D4) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D5) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D6) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D7) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D8) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            if (Current_Char == LIT_D9) {
                Lit_Value = Current_Char - 48;
                if (Run_Pending == 0x00000001) {
                    // честный вызов по номеру (TKT-051 веха-3): номер 1..4
                    Run_Pending = 0x00000000;
                    if (Lit_Value == 0x00000001) {
                        Fn_OK = 0x00000001;
                    } else {
                        if (Lit_Value == 0x00000002) {
                            Fn_OK = 0x00000001;
                        } else {
                            if (Lit_Value == 0x00000003) {
                                Fn_OK = 0x00000001;
                            } else {
                                if (Lit_Value == 0x00000004) {
                                    Fn_OK = 0x00000001;
                                } else {
                                    Fn_OK = 0x00000000;
                                }
                            }
                        }
                    }
                    if (Fn_OK == 0x00000001) {
                        if (Call_Count == 0x00000004) {
                            // честный отказ ДО эмиссии: все 4 слота заняты
                            if (Error_Flag == 0x00000000) {
                                Fail_Code = BRK_PATCH_OVERFLOW;
                                Fail_Position = Word_Index;
                                Error_Flag = 0x00000001;
                                Word_Index = MAX_SOURCE_WORDS;
                            }
                        } else {
                            out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                            sys_call(FILE_U8);
                            Emitted_Bytes = Emitted_Bytes + 1;
                            // честный слот = позиция операнда + номер функции
                            if (Call_Count == 0x00000000) {
                                Call_Site_1 = Emitted_Bytes;
                                Call_Fn_1 = Lit_Value;
                            } else {
                                if (Call_Count == 0x00000001) {
                                    Call_Site_2 = Emitted_Bytes;
                                    Call_Fn_2 = Lit_Value;
                                } else {
                                    if (Call_Count == 0x00000002) {
                                        Call_Site_3 = Emitted_Bytes;
                                        Call_Fn_3 = Lit_Value;
                                    } else {
                                        Call_Site_4 = Emitted_Bytes;
                                        Call_Fn_4 = Lit_Value;
                                    }
                                }
                            }
                            Call_Count = Call_Count + 1;
                            out_cell(STREAM_EMIT_CELL, 0x00000000);
                            sys_call(FILE_U16);
                            sys_call(FILE_U16);
                            Emitted_Bytes = Emitted_Bytes + 4;
                            Token_Counter = Token_Counter + 1;
                            Found_Flag = 0x00000001;
                        }
                    } else {
                        // честный отказ ДО эмиссии: номера функции нет (вне 1..4)
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_NO_FUNC;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честная операция (TKT-050 + TKT-052 веха-3): acc = (acc ОП
                    // Lit_Value); режим честно из Op_Pending (0x14 ad / 0x16 eq /
                    // 0x17 su / 0x1A gt / 0x1B lt) — OP_LOAD 0x12 + режим + BE32
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Op_Pending);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Lit_Value);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Op_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
                }
            }

            // '{': честный клад на стек групп
            if (Current_Char == SYM_BRACE_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Node_Brace_Depth = Node_Brace_Depth + 1;
                Found_Flag = 0x00000001;
            }

            // '}': честный сним — или честный отказ (K-S2, TKT-033)
            if (Current_Char == SYM_BRACE_CLOSE) {
                if (Node_Brace_Depth == 0x00000000) {
                    Fail_Code = BRK_STRAY_CLOSE;
                    Fail_Position = Word_Index;
                    Error_Flag = 0x00000001;
                    Word_Index = MAX_SOURCE_WORDS;
                } else {
                    Syntax_Counter = Syntax_Counter + 1;
                    Node_Brace_Depth = Node_Brace_Depth - 1;
                    Node_Counter = Node_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }

            // '(': честный клад
            if (Current_Char == SYM_PAREN_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Node_Paren_Depth = Node_Paren_Depth + 1;
                Found_Flag = 0x00000001;
            }

            // ')': честный сним — или честный отказ (K-S2, TKT-033)
            if (Current_Char == SYM_PAREN_CLOSE) {
                if (Node_Paren_Depth == 0x00000000) {
                    Fail_Code = BRK_STRAY_CLOSE;
                    Fail_Position = Word_Index;
                    Error_Flag = 0x00000001;
                    Word_Index = MAX_SOURCE_WORDS;
                } else {
                    Syntax_Counter = Syntax_Counter + 1;
                    Node_Paren_Depth = Node_Paren_Depth - 1;
                    Node_Counter = Node_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }

            if (Current_Char == SYM_SEMICOLON) {
                Syntax_Counter = Syntax_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // честный отказ: неизвестное слово (K-S1, TKT-033)
            // позиция честно запоминается ДО обрыва (Word_Index = MAX затёр бы);
            // приоритет честный: код брака = ПЕРВЫЙ честный сбой (см. stage1_compiler)
            if (Found_Flag == 0x00000000) {
                if (Error_Flag == 0x00000000) {
                    Fail_Code = BRK_UNKNOWN_WORD;
                    Fail_Position = Word_Index;
                    Error_Flag = 0x00000001;
                    Word_Index = MAX_SOURCE_WORDS;
                }
            }
            }


            if (Word_Index == MAX_SOURCE_WORDS) {
                // честный отказ или граница — выход без шага
            } else {
                Execution_Pointer = Execution_Pointer + 4;
                Word_Index = Word_Index + 1;

                // Честный хвост рекурсии: безусловный — база остановит
                run Scan_Word_Loop();
            }
        }
    }
}
