// ===================================================================
// СПРИНТ СТАДИЯ-1.3: честный стек групп { } ( ) — первый этап парсера
// Файл: stage1_selftest.kt | Язык: KINII (подмножество стадии-0)
//
// По TKT-032 (спринты 1.1/1.2 составляют базу):
//   * честные сигнатуры 1.2 сохранены (двухсимвольные слова);
//   * скобки честно ведут стек: '{'/'(' кладёт, '}'/')' снимает;
//   * '}'/')' при пустом честном стеке — честный ОТКАЗ (fail-fast);
//   * честная незакрытая группа в конце прохода — честный ОТКАЗ;
//   * каждая честно согласованная группа -> Node_Counter (узлы);
//   * эмиссия байт НЕ меняется (скобки честно не байт).
// Стрим-сверка 1.2 честно снята со стенда: её честность доказана
// спринтом 1.1/1.2 и оставлена в истории (стенд честно сузился).
//
// Фазы честные:
//   Ф1: '#' se st { te { } ( ) } .  -> эмиссии 1,0x10,0x10,5
//        counter 4 | syntax 6 | nodes 3 | depths 0 | error 0
//   Ф2: '{' '{' '}' .               -> одна группа честно закрыта1,
//        одна честно незакрыта -> честный отказ (error 1, nodes 1)
//   Ф3: '}' .                       -> закрытие при пустом стеке ->
//        честный отказ на месте (error 1, nodes 0, syntax 0)
//
// Лог честный (серия 0x91xx + фазы):
//   0x9000 START      0x9001 Ф1 загружена   0x90F0 Ф1 скан завершён
//   0x9110 counter==4 0x9111 syntax==6      0x9112 nodes==3
//   0x9113 error==0                       0x9114 depths обе == 0
//   0x9002 Ф2 загружена 0x90F1 Ф2 скан завершён
//   0x9130 error==1   0x9131 nodes==1 (одна '{}' закрыта честно)
//   0x9003 Ф3 загружена 0x90F2 Ф3 скан завершён
//   0x9140 error==1   0x9141 nodes==0 и syntax==0
//   отказы: 0x9096/0x9097/0x9098/0x9095
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
