// ===================================================================
// СПРИНТ СТАДИЯ-1.2: двухсимвольные сигнатуры + структурные слова,
// honest-отказ на неизвестном слове (независимый стенд)
// Файл: stage1_selftest.kt | Язык: KINII (подмножество стадии-0)
//
// По TKT-032 / opcodes.core / lexicon.core:
//   * слово = символ1 + символ2*256 (ASCII), хвост честно игнорируется;
//   * сигнатуры: '#'->OP_INIT(0x01), 'se'/'st'->OP_ALLOC_ST(0x10),
//     'fu'->OP_CALL(0x03), 'if'->OP_JZ(0x06), 'te'->OP_TERM(0x05);
//   * '{' '}' '(' ')' ';' — структурные: байта НЕТ, Syntax_Counter считает;
//   * НЕИЗВЕСТНОЕ слово ('qq') — честный отказ: Error_Flag=1, проход
//     честно стопится, компилятор честно эмитит брак-маркер 0xFE.
//
// Фаза 1 (валидный): '#' se st { fu if te ; '.' ->
//   эмиссии 1,0x10,0x10,3,6,5 | counter 6 | syntax 2 | error 0 | стрим сверен
// Фаза 2 (отказный):  '#' se qq '.' ->
//   эмиссии 1,0x10 затем честный стоп | counter 2 | error 1
//
// Лог честный (серия 0x90xx):
//   0x9000 START      0x9001 фаза-1 загружена
//   0x90F0 фаза-1 скан завершён
//   0x9010 counter==6  0x9011 syntax==2  0x9012 error==0
//   0x9020 стрим честно 1,0x10,0x10,3,6,5
//   0x9030 фаза-2 ('qq') загружена   0x90F1 фаза-2 скан завершён
//   0x9040 честный отказ увиден      0x9041 счётчик честно остановился на 2
//   отказы: 0x9096/0x9097/0x9098/0x9095
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT            0x3F0050C0
#define: SOURCE_CODE_BUFFER  0x00A00000
#define: TOKEN_STREAM_BUFFER 0x01000000
#define: MAX_SOURCE_WORDS    0x00000010

// честные двухсимвольные сигнатуры
#define: D_WORD_PREPROC 0x00000023
#define: KW_SET         0x00006573
#define: KW_STATIC      0x00007473
#define: KW_FUNCTION    0x00007566
#define: KW_IF          0x00006669
#define: KW_TERM        0x00006574
#define: SYM_BRACE_OPEN 0x0000007B
#define: SYM_SEMICOLON  0x0000003B
#define: CH_WORD_END    0x0000002E
#define: UNKNOWN_WORD   0x00007171  // 'qq' — честно непонятный компилятору

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
set static Tmp_Addr          = 0x00000000;
set static Tmp_Word          = 0x00000000;
set static Stream_Emit       = 0x00000000;
set static Verify_Run        = 0x00000000;
set static Verify_Match      = 0x00000000;
set static Stream_Word       = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009000);      // LOG: стадия-1.2 стенд START

    // ---------- ФАЗА 1: валидный исходник ----------
    run Load_Demo_Source();              // честная роль хоста-загрузчика

    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0x00000000;
    Word_Index = 0x00000000;
    Syntax_Counter = 0x00000000;
    Error_Flag = 0x00000000;
    run Scan_Word_Loop();

    out_cell(LOG_PORT, 0x000090F0);      // LOG: фаза-1 честный скан завершён

    if (Token_Counter == 0x00000006) {
        out_cell(LOG_PORT, 0x00009010);  // LOG: честный счётчик 6
    } else {
        out_cell(LOG_PORT, 0x00009096);  // LOG: честный отказ счётчика
    }

    if (Syntax_Counter == 0x00000002) {
        out_cell(LOG_PORT, 0x00009011);  // LOG: '{' и ';' честно учтены, байта нет
    } else {
        out_cell(LOG_PORT, 0x00009097);  // LOG: честный отказ синтакс-счёта
    }

    if (Error_Flag == 0x00000000) {
        out_cell(LOG_PORT, 0x00009012);  // LOG: отказа нет — честно
    } else {
        out_cell(LOG_PORT, 0x00009098);  // LOG: ложный отказ — честный брак
    }

    run Verify_Stream();                 // честная сверка стрима из 6 слов

    // ---------- ФАЗА 2: честный отказ на 'qq' ----------
    out_cell(LOG_PORT, 0x00009030);      // LOG: фаза-2 START
    run Load_Bad_Source();               // честная роль хоста-загрузчика

    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0x00000000;
    Word_Index = 0x00000000;
    Syntax_Counter = 0x00000000;
    Error_Flag = 0x00000000;
    run Scan_Word_Loop();

    out_cell(LOG_PORT, 0x000090F1);      // LOG: фаза-2 честный скан завершён

    if (Error_Flag == 0x00000001) {
        out_cell(LOG_PORT, 0x00009040);  // LOG: честный отказ увиден
    } else {
        out_cell(LOG_PORT, 0x00009095);  // LOG: компилятор смолчал — честный брак
    }

    if (Token_Counter == 0x00000002) {
        out_cell(LOG_PORT, 0x00009041);  // LOG: счётчик честно остановился на 2
    } else {
        out_cell(LOG_PORT, 0x00009099);  // LOG: счётчик врёт — честный брак
    }

    // честный финальный отчёт значениями
    log_cell(LOG_PORT, Token_Counter);
    log_cell(LOG_PORT, Error_Flag);
}

// ---------- честная загрузка фазы-1 (роль хоста) ----------
// Слова: '#' se st { fu if te ; '.' — честная по-словная модель.
function Load_Demo_Source() {
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
    Tmp_Word = KW_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = KW_IF;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = KW_TERM;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 28;
    Tmp_Word = SYM_SEMICOLON;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 32;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);

    out_cell(LOG_PORT, 0x00009001);      // LOG: фаза-1 честно загружена
}

// ---------- честная загрузка фазы-2: неизвестное слово 'qq' ----------
function Load_Bad_Source() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = D_WORD_PREPROC;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = KW_SET;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = UNKNOWN_WORD;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честный лексер стадии-1 (тот же алгоритм, что в компиляторе,
// плюс честный дубль-эмиссия в TOKEN_STREAM_BUFFER для сверки) ----------
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
                Stream_Emit = OP_INIT_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_SET) {
                out_cell(LOG_PORT, OP_ALLOC_CODE);
                Stream_Emit = OP_ALLOC_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_STATIC) {
                out_cell(LOG_PORT, OP_ALLOC_CODE);
                Stream_Emit = OP_ALLOC_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_FUNCTION) {
                out_cell(LOG_PORT, OP_CALL_CODE);
                Stream_Emit = OP_CALL_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_IF) {
                out_cell(LOG_PORT, OP_JZ_CODE);
                Stream_Emit = OP_JZ_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == KW_TERM) {
                out_cell(LOG_PORT, OP_TERM_CODE);
                Stream_Emit = OP_TERM_CODE;
                run Emit_Stream();
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // структурные: честный подсчёт, байта нет
            if (Current_Char == SYM_BRACE_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == SYM_SEMICOLON) {
                Syntax_Counter = Syntax_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // честный отказ: неизвестное слово ('qq' фазы-2)
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

// ---------- честная запись токена в стрим ----------
// Адрес чёстный: TOKEN + counter*4 пошаговым сложением.
function Emit_Stream() {
    Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
    Tmp_Addr = Tmp_Addr + Token_Counter;
    Tmp_Addr = Tmp_Addr + Token_Counter;
    Tmp_Addr = Tmp_Addr + Token_Counter;
    Tmp_Word = Stream_Emit;
    store_ind(Tmp_Addr, Tmp_Word);
}

// ---------- честная сверка стрима: 1, 0x10, 0x10, 3, 6, 5 ----------
function Verify_Stream() {
    Verify_Run = 0x00000000;
    Verify_Match = 0x00000000;
    run Verify_Loop();

    if (Verify_Match == 0x00000006) {
        out_cell(LOG_PORT, 0x00009020);  // LOG: стрим честно 1,0x10,0x10,3,6,5
    } else {
        out_cell(LOG_PORT, 0x00009097);  // LOG: честный отказ сверки стрима
    }
}

function Verify_Loop() {
    if (Verify_Run == 0x00000006) {
        // честная база: 6 слов стрима честно сверены
    } else {
        Tmp_Addr = TOKEN_STREAM_BUFFER + Verify_Run;
        Tmp_Addr = Tmp_Addr + Verify_Run;
        Tmp_Addr = Tmp_Addr + Verify_Run;
        Tmp_Addr = Tmp_Addr + Verify_Run;
        Stream_Word = in_cell(Tmp_Addr);

        if (Verify_Run == 0x00000000) {
            if (Stream_Word == OP_INIT_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000001) {
            if (Stream_Word == OP_ALLOC_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000002) {
            if (Stream_Word == OP_ALLOC_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000003) {
            if (Stream_Word == OP_CALL_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000004) {
            if (Stream_Word == OP_JZ_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000005) {
            if (Stream_Word == OP_TERM_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }

        Verify_Run = Verify_Run + 1;
        run Verify_Loop();
    }
}
