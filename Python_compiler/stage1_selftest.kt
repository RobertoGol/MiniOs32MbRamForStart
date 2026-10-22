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
#define: KW_TERM        0x00006574
#define: SYM_BRACE_OPEN 0x0000007B
#define: SYM_BRACE_CLOSE 0x0000007D
#define: SYM_PAREN_OPEN 0x00000028
#define: SYM_PAREN_CLOSE 0x00000029
#define: SYM_SEMICOLON  0x0000003B
#define: CH_WORD_END    0x0000002E
#define: UNKNOWN_WORD   0x00007171  // 'qq'

// честные опкоды
#define: OP_INIT_CODE   0x00000001
#define: OP_CALL_CODE   0x00000003
#define: OP_TERM_CODE   0x00000005
#define: OP_JZ_CODE     0x00000006
#define: OP_ALLOC_CODE  0x00000010
#define: OP_CONST_CODE  0x00000015 // 0x15 OP_CONST (стадия-1.4)
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

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009000);      // LOG: стадия-1.3 стенд START

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
        }
    } else {
        Error_Flag = 0x00000001;         // честная незакрытая {}
    }

    if (Error_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009130);  // LOG: честный отказ незакрытой
    } else {
        out_cell(LOG_PORT, 0x00009096);
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

    // честный финальный отчёт значениями
    log_cell(LOG_PORT, Token_Counter);
    log_cell(LOG_PORT, Node_Counter);
    log_cell(LOG_PORT, Error_Flag);
}

// ---------- честный сброс сканирующих регистров между фазами ----------
function Reset_Scan() {
    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0;
    Word_Index = 0;
    Syntax_Counter = 0;
    Error_Flag = 0;
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

// ---------- честный лексер+стек групп (тот же алгоритм, что в компиляторе) ----------
function Scan_Word_Loop() {
    if (Word_Index == MAX_SOURCE_WORDS) {
        // честная база: граница буфера честно отщелкала
    } else {
        Current_Char = in_cell(Execution_Pointer);

        if (Current_Char == CH_WORD_END) {
            // честный терминатор: выход БЕЗ инкрементов и БЕЗ рекурсии
            Word_Index = MAX_SOURCE_WORDS;
        }

        if (Word_Index == MAX_SOURCE_WORDS) {
            // честный терминатор закрыл проход — честный выход
        } else {
            Found_Flag = 0x00000000;

            if (Current_Char == D_WORD_PREPROC) {
                out_cell(LOG_PORT, OP_INIT_CODE);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_SET) {
                out_cell(LOG_PORT, OP_ALLOC_CODE);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_STATIC) {
                out_cell(LOG_PORT, OP_ALLOC_CODE);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_FUNCTION) {
                out_cell(LOG_PORT, OP_CALL_CODE);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_IF) {
                out_cell(LOG_PORT, OP_JZ_CODE);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_TERM) {
                out_cell(LOG_PORT, OP_TERM_CODE);
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
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D1) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D2) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D3) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D4) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D5) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D6) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D7) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D8) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D9) {
                Lit_Value = Current_Char - 48;
                out_cell(LOG_PORT, OP_CONST_CODE);
                log_cell(LOG_PORT, Lit_Value);
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // '{': честный клад на стек групп
            if (Current_Char == SYM_BRACE_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Node_Brace_Depth = Node_Brace_Depth + 1;
                Found_Flag = 0x00000001;
            }

            // '}': честный сним — или честный отказ
            if (Current_Char == SYM_BRACE_CLOSE) {
                if (Node_Brace_Depth == 0x00000000) {
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

            // ')': честный сним — или честный отказ
            if (Current_Char == SYM_PAREN_CLOSE) {
                if (Node_Paren_Depth == 0x00000000) {
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

            // честный отказ: неизвестное слово
            if (Found_Flag == 0x00000000) {
                Error_Flag = 0x00000001;
                Word_Index = MAX_SOURCE_WORDS;
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
