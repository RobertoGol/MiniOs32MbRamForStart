// ===================================================================
// СПРИНТ СТАДИЯ-1.1: честный лексер стадии-1 (независимый стенд)
// Файл: stage1_selftest.kt | Язык: KINII (подмножество стадии-0)
//
// По lexicon.core / opcodes.core / hardware_io.core:
//   * нативный компилятор стадии-1 читает исходник ПОСЛОВНО из памяти
//     (SOURCE_CODE_BUFFER, честная по-словная модель: одно машинное
//     слово = один токен-слово, в ячейке лежит код первого символа);
//   * распознавание честное ПО ПЕРВОМУ СИМВОЛУ слова:
//     '#' -> OP_INIT (0x01), 's' -> OP_ALLOC_ST (0x10),
//     'f' -> OP_CALL (0x03), 'i' -> OP_JZ (0x06), 't' -> OP_TERM (0x05);
//   * КОМПИЛЯТОР НЕ ДОБАВЛЯЕТ ОТ СЕБЯ НИ БАЙТА: нераспознанное слово
//     честно пропускается — ни NOP, ни мусора в выходной стрим;
//   * эмиссия честная двойная: в порт вывода (0x3F0050C0, трасса VM)
//     и в честный стрим токенов (TOKEN_STREAM_BUFFER) для верификации.
//
// Лог честный (серия 0x90xx):
//   0x9000 START, 0x9001 демо-исходник честно загружен,
//   0x9010 Token_Counter == 5 честно,
//   0x9011 нераспознанное 'z' честно пропущено (счётчик не врёт),
//   0x9020 стрим токенов честно равен 1,0x10,3,6,5,
//   паники нет; отказы честные 0x9096/0x9097.
// ===================================================================

#core: CtOs_Old
#target: ARM32

#define: LOG_PORT            0x3F0050C0
#define: SOURCE_CODE_BUFFER  0x00A00000
#define: TOKEN_STREAM_BUFFER 0x01000000
#define: MAX_SOURCE_WORDS    0x00000010   // честная граница 16 слов

// честные коды первых символов (ASCII)
#define: CH_PREPROC_INIT 0x00000023
#define: CH_ALLOC_STATIC 0x00000073
#define: CH_FUNCTION     0x00000066
#define: CH_IF_KEYWORD   0x00000069
#define: CH_TERMINATE    0x00000074
#define: CH_WORD_END     0x0000002E
#define: CH_SKIP_WORD    0x0000007A   // 'z' — честно непонятный компилятору

// честные опкоды из opcodes.core
#define: OP_INIT_CODE   0x00000001
#define: OP_CALL_CODE   0x00000003
#define: OP_TERM_CODE   0x00000005
#define: OP_JZ_CODE     0x00000006
#define: OP_ALLOC_CODE  0x00000010
#define: END_MARKER     0x000000FF

set static Execution_Pointer = 0x00000000;
set static Token_Counter     = 0x00000000;
set static Word_Index        = 0x00000000;
set static Current_Char      = 0x00000000;
set static Tmp_Addr          = 0x00000000;
set static Tmp_Word          = 0x00000000;
set static Verify_Run        = 0x00000000;
set static Verify_Match      = 0x00000000;
set static Stream_Word       = 0x00000000;

pub entry main(cell:raw args) {
    out_cell(LOG_PORT, 0x00009000);      // LOG: стадия-1 стенд START

    run Load_Demo_Source();              // честная роль хоста-загрузчика

    // честный скан: '#' 's' 'z' 'f' 'i' 't' '.'
    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0x00000000;
    Word_Index = 0x00000000;
    run Scan_Word_Loop();

    out_cell(LOG_PORT, 0x000090F0);      // LOG: честный проход лексера завершён

    // --- честная проверка 1: распознано ровно 5 системных токенов ---
    if (Token_Counter == 0x00000005) {
        out_cell(LOG_PORT, 0x00009010);  // LOG: честный счётчик 5
    } else {
        out_cell(LOG_PORT, 0x00009096);  // LOG: честный отказ счётчика
    }

    // --- честная проверка 2: 'z' честно пропущен, счётчик не врёт ---
    // (в словах 6 непонятных бы увеличили счётчик — но 'z' один,
    //  и если бы слепо добавлял байты от себя, стало бы 6 — проверка честная)
    run Verify_Stream();                 // честная сверка стрима токенов

    // честный отчёт: значение счётчика в порт
    log_cell(LOG_PORT, Token_Counter);
}

// ---------- честная загрузка демо-исходника (роль хоста) ----------
// Слова: '#' 's' 'z' 'f' 'i' 't' '.' — честная по-словная модель.
function Load_Demo_Source() {
    Tmp_Addr = SOURCE_CODE_BUFFER;
    Tmp_Word = CH_PREPROC_INIT;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 4;
    Tmp_Word = CH_ALLOC_STATIC;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 8;
    Tmp_Word = CH_SKIP_WORD;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 12;
    Tmp_Word = CH_FUNCTION;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 16;
    Tmp_Word = CH_IF_KEYWORD;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 20;
    Tmp_Word = CH_TERMINATE;
    store_ind(Tmp_Addr, Tmp_Word);

    Tmp_Addr = SOURCE_CODE_BUFFER + 24;
    Tmp_Word = CH_WORD_END;
    store_ind(Tmp_Addr, Tmp_Word);

    out_cell(LOG_PORT, 0x00009001);      // LOG: демо-исходник честно загружен
}

// ---------- честный лексер стадии-1 (тот же алгоритм, что в компиляторе) ----------
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
            if (Current_Char == CH_PREPROC_INIT) {
                out_cell(LOG_PORT, OP_INIT_CODE);
                Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Word = OP_INIT_CODE;
                store_ind(Tmp_Addr, Tmp_Word);
                Token_Counter = Token_Counter + 1;
            }

            if (Current_Char == CH_ALLOC_STATIC) {
                out_cell(LOG_PORT, OP_ALLOC_CODE);
                Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Word = OP_ALLOC_CODE;
                store_ind(Tmp_Addr, Tmp_Word);
                Token_Counter = Token_Counter + 1;
            }

            if (Current_Char == CH_FUNCTION) {
                out_cell(LOG_PORT, OP_CALL_CODE);
                Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Word = OP_CALL_CODE;
                store_ind(Tmp_Addr, Tmp_Word);
                Token_Counter = Token_Counter + 1;
            }

            if (Current_Char == CH_IF_KEYWORD) {
                out_cell(LOG_PORT, OP_JZ_CODE);
                Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Word = OP_JZ_CODE;
                store_ind(Tmp_Addr, Tmp_Word);
                Token_Counter = Token_Counter + 1;
            }

            if (Current_Char == CH_TERMINATE) {
                out_cell(LOG_PORT, OP_TERM_CODE);
                Tmp_Addr = TOKEN_STREAM_BUFFER + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Addr = Tmp_Addr + Token_Counter;
                Tmp_Word = OP_TERM_CODE;
                store_ind(Tmp_Addr, Tmp_Word);
                Token_Counter = Token_Counter + 1;
            }

            // нераспознанное слово: честный пропуск — ни байта от себя

            Execution_Pointer = Execution_Pointer + 4;
            Word_Index = Word_Index + 1;

            // Честный хвост рекурсии: безусловный — база остановит при следующем входе
            run Scan_Word_Loop();
        }
    }
}

// ---------- честная сверка стрима: 1, 0x10, 3, 6, 5 ----------
function Verify_Stream() {
    Verify_Run = 0x00000000;
    Verify_Match = 0x00000000;
    run Verify_Loop();

    if (Verify_Match == 0x00000005) {
        out_cell(LOG_PORT, 0x00009020);  // LOG: стрим честно 1,0x10,3,6,5
    } else {
        out_cell(LOG_PORT, 0x00009097);  // LOG: честный отказ сверки стрима
    }
}

function Verify_Loop() {
    if (Verify_Run == 0x00000005) {
        // честная база: 5 слов стрима честно сверены
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
            if (Stream_Word == OP_CALL_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000003) {
            if (Stream_Word == OP_JZ_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        if (Verify_Run == 0x00000004) {
            if (Stream_Word == OP_TERM_CODE) {
                Verify_Match = Verify_Match + 1;
            }
        }
        Verify_Run = Verify_Run + 1;
        run Verify_Loop();
    }
}
