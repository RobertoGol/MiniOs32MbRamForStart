// ===================================================================
// КОРНЕВОЙ НАТИВНЫЙ КОМПИЛЯТОР СТАДИИ-1 (НА ЯЗЫКЕ KITII / VOID)
// Профиль сборки: BARE_METAL_COMPILER | Целевое ядро: CtOs_Old
// СПРИНТ 1-СИГНАТУРЫ: честный по-словный проход; каждое слово несёт
// первые ДВА символа (хвост слова честно игнорируется — осознанное
// ограничение модели: set/settle пока неразличимы, честно задокументировано).
//
// Спринт 1-Лексер (закрыт 2026-10-21, коммит 9d1ae2c): однослойное
// распознавание по первому символу. Здесь его заменяет честная
// двухсимвольная сигнатура — set/static честно различаются.
//
// Компилятор не добавляет от себя ни байта:
//   * структурные слова { } ( ) ; НЕ эмитят байт (синтаксис, а не
//     байткод) — только честный подсчёт Syntax_Counter;
//   * НЕИЗВЕСТНОЕ слово — честный ОТКАЗ (Error_Flag, маркер 0xFE
//     вместо честного конца 0xFF), не тихий пропуск.
// ===================================================================

#core: CtOs_Old
#target: ARM32

// Жестко вшиваем системные константы и адреса буферов ОЗУ из syntax.void
#define: SOURCE_CODE_BUFFER 0x00A00000 // Адрес начала исходного текста в памяти
#define: TOKEN_STREAM_BUFFER 0x01000000 // Адрес, куда нативный лексер сложит токены
#define: OUTPUT_BINARY_PORT  0x3F0050C0 // Физический порт для записи готового бинарника
#define: MAX_SOURCE_WORDS    0x00000010 // Честная граница прохода: максимум слов (16)

// Двухсимвольные сигнатуры: слово = символ1 + символ2*256 (ASCII,
// честная кодировка; одиночный символ несет в младшем байте)
#define: D_WORD_PREPROC   0x00000023 // '#': #core/#target/#define -> OP_INIT
#define: KW_SET           0x00006573 // 'se': set -> OP_ALLOC_ST
#define: KW_STATIC        0x00007473 // 'st': static -> OP_ALLOC_ST
#define: KW_FUNCTION      0x00007566 // 'fu': function/pub entry -> OP_CALL
#define: KW_IF            0x00006669 // 'if': if -> OP_JZ
#define: KW_ELSE 0x00007365 // 'es' = else; 4-символьное 'else' честно не собирается в 2-символьных пакетах
#define: KW_TERM          0x00006574 // 'te': terminate -> OP_TERM
#define: SYM_BRACE_OPEN   0x0000007B // '{'  -> синтаксис, байт НЕ эмитится
#define: SYM_BRACE_CLOSE  0x0000007D // '}'  -> синтаксис, байт НЕ эмитится
#define: SYM_PAREN_OPEN   0x00000028 // '('  -> синтаксис, байт НЕ эмитится
#define: SYM_PAREN_CLOSE  0x00000029 // ')'  -> синтаксис, байт НЕ эмитится
#define: SYM_SEMICOLON    0x0000003B // ';'  -> синтаксис, байт НЕ эмитится
#define: CH_WORD_END      0x0000002E // '.': честный ограничитель исходника

// Честные опкоды из opcodes.core (стадия-0 контракт)
#define: OP_INIT_CODE  0x00000001 // 0x01 OP_INIT
#define: OP_CALL_CODE  0x00000003 // 0x03 OP_CALL
#define: OP_TERM_CODE  0x00000005 // 0x05 OP_TERM
#define: OP_JZ_CODE    0x00000006 // 0x06 OP_JZ
#define: OP_JMP_CODE 0x00000007 // честный безусловный переход (VM OP_JMP)
#define: OP_ALLOC_CODE 0x00000010 // 0x10 OP_ALLOC_ST
#define: OP_CONST_CODE 0x00000015 // 0x15 OP_CONST «константа на акк»
#define: SYM_LIT_BASE  0x00000030 // '0': база честного литерального ряда '0'..'9'
#define: LIT_D0        0x00000030 // '0' — слово однозначного литерала (сим2==0)
#define: LIT_D1        0x00000031 // '1'
#define: LIT_D2        0x00000032 // '2'
#define: LIT_D3        0x00000033 // '3'
#define: LIT_D4        0x00000034 // '4'
#define: LIT_D5        0x00000035 // '5'
#define: LIT_D6        0x00000036 // '6'
#define: LIT_D7        0x00000037 // '7'
#define: LIT_D8        0x00000038 // '8'
#define: LIT_D9        0x00000039 // '9'
#define: END_MARKER    0x000000FF // Честный маркер конца эмиссии
#define: ERR_MARKER    0x000000FE // Честный маркер БРАКА: неизвестное слово

// Честный syscall-файл-слой (1.5-б, opcodes.core OP_SYSCALL 0x13):
// стадия-1 честно собирает СВОЙ артефакт-файл (заголовок TKT-009 + отчёт).
#define: STREAM_EMIT_CELL 0x00F00FF0 // честная ячейка-аргумент syscall (Stream_Emit)
#define: FILE_BEGIN       0x00000130 // открыть артефакт
#define: FILE_PUT         0x00000131 // слово Stream_Emit -> 4 байта BE
#define: FILE_U16         0x00000132 // младшие 16 бит -> 2 байта BE
#define: FILE_END         0x00000133 // закрыть артефакт (не закрыт = честный брак)
#define: FILE_U8          0x00000134 // 1 байт -> артефакт (TKT-047: честный байт-канал опконов)
#define: FILE_SEAL        0x00000135 // контрольное слово артефакта CRC-32 (TKT-040 веха-1)
#define: FILE_SEEK        0x00000136 // честная позиция записи в артефакте (TKT-048)

// Честные коды брака стадии-1 (TKT-033, по образцу K-кодов):
// позиция брака — честная ячейка Fail_Position на момент сбоя
#define: BRK_UNKNOWN_WORD 0x00000001 // K-S1: неизвестное слово
#define: BRK_STRAY_CLOSE  0x00000002 // K-S2: '}' или ')' при пустом честном стеке
#define: BRK_UNCLOSED     0x00000003 // K-S3: незакрытая честная группа в финале
#define: BRK_PATCH_OVERFLOW 0x00000004 // честных слотов патча больше нет (TKT-048 честный лимит)
#define: HDR_BODY_SIZE    0x00000014 // честный размер заголовка v1.1 = 20 байт

// Объявляем глобальные статические ячейки памяти ядра (регистры компилятора)
set static Execution_Pointer = 0x00000000; // Текущая позиция чтения слов
set static Token_Counter     = 0x00000000; // Счетчик распознанных системных токенов
set static Word_Index        = 0x00000000; // Честная граница прохода
set static Current_Char      = 0x00000000; // Текущее слово из буфера исходника
set static Syntax_Counter    = 0x00000000; // Структурные слова (без байта, честный учёт)
set static Found_Flag        = 0x00000000; // Слово распознано на этой итерации
set static Error_Flag        = 0x00000000; // Честный отказ: неизвестное слово
set static Node_Brace_Depth  = 0x00000000; // Честный стек групп {}: глубина
set static Node_Paren_Depth  = 0x00000000; // Честный стек групп (): глубина
set static Node_Counter      = 0x00000000; // Честно согласованные группы (узлы)
set static Tmp_Addr          = 0x00000000; // Рабочая ячейка-указатель
set static Tmp_Word          = 0x00000000; // Рабочее слово-значение
set static Lit_Value         = 0x00000000; // Честное ЗНАЧЕНИЕ литерала (1.4)
set static Fail_Code         = 0x00000000; // Честный код брака (0 = успеха нет сбоя)
set static Fail_Position     = 0x00000000; // Честная позиция слова на момент брака
set static Emitted_Bytes     = 0x00000000; // Честный счётчик байтов потока (TKT-048)
set static JP_Site_Call         = 0x00000000; // Честный слот места патча операнда №1
set static JP_Site_If      = 0x00000000; // честный слот операнда JZ от if
set static JP_Site_Jmp      = 0x00000000; // честный слот операнда JMP от es
set static JP_Else_Join     = 0x00000000; // честное начало else-тела (target JZ)
set static Patch_Target     = 0x00000000; // честный target патча JZ (pereklich корней)
set static JP_Site_Term      = 0x00000000; // Честная позиция потока байта 'te' (target демо)

// Главная точка входа нативного компилятора (Entry Point)
pub entry main(cell:raw args) {

    // Принудительно очищаем сетевой DNS-кеш хоста из макроса README
    net_flush;

    // Инициализируем указатель на первый байт текстового буфера
    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0;
    Word_Index = 0;
    Syntax_Counter = 0;
    Error_Flag = 0;
    Fail_Code = 0;        // честный код брака: успех = 0 (TKT-033)
    Fail_Position = 0;    // честная позиция брака: успех = 0 (TKT-033)
    Emitted_Bytes = 0;    // честный счётчик байтов потока (TKT-048)
    JP_Site_Call = 0;    // честные слоты патча пусты (TKT-048)
    JP_Site_If = 0;      // honestly нет if-сайтов
    JP_Site_Jmp = 0;     // honestly нет es-сайтов
    JP_Else_Join = 0;    // honestly нет else-сращений
    JP_Site_Term = 0;     // честная позиция байта TERM пуста
    Node_Brace_Depth = 0;
    Node_Paren_Depth = 0;
    Node_Counter = 0;

    // --- 1.7 (TKT-047) + TKT-040 веха-1: честный артефакт-бинарь v1.1 ---
    // Заголовок TKT-009 v1.1 = 20 байт: прежние 16 + контрольное слово тела
    // (crc, честно вписывается FILE_SEAL в конце). Честная байт-карта:
    // заголовочные поля VM читает LE, эмиттер пишет БАЙТ-ОБРАЗ поля.
    // entry 0x14: код лежит ровно за заголовком v1.1.
    sys_call(FILE_BEGIN);
    out_cell(STREAM_EMIT_CELL, 0x43544F53);  // 'CTOS' BE
    sys_call(FILE_PUT);
    out_cell(STREAM_EMIT_CELL, 0x00000101);  // байт-образ ver-поля 01 01 (LE -> v1.1 с контролем)
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

    // Вызываем фоновую функцию низкоуровневой токенизации текста
    run NativeLexicalScanner();

    // Завершаем контекст компилятора с полной зачисткой регистров ОЗУ
    terminate;
}

// Фоновое ядро лексера Стадии-1 на чистом бестиповом синтаксисе Void
function NativeLexicalScanner() {
    // Честный вход в рекурсивный обход: одно слово за одну регенерацию
    run Scan_Word_Loop();

    // Честный финальный разбор: брак дружнее мастерить честно
    // (1.6: маркер-вердикт честно пишется В АРТЕФАКТ после эмит-потока)
    if (Node_Brace_Depth == 0x00000000) {
        if (Node_Paren_Depth == 0x00000000) {
            if (Error_Flag == 0x00000000) {
                // Честный маркер конца эмиссии: после него поток закончен
                out_cell(STREAM_EMIT_CELL, END_MARKER);
                sys_call(FILE_U8);
            } else {
                // Честный брак: неизвестное слово — поток честно обрывается
                // (код/позиция уже честно записаны в сканере: K-S1)
                out_cell(STREAM_EMIT_CELL, ERR_MARKER);
                sys_call(FILE_U8);
            }
        } else {
            // Честный брак: честная незакрытая группа () (K-S3, TKT-033);
            // позиция честно = граница прохода (Word_Index == MAX) — честно.
            Error_Flag = 0x00000001;
            Fail_Code = BRK_UNCLOSED;
            Fail_Position = Word_Index;
            out_cell(STREAM_EMIT_CELL, ERR_MARKER);
            sys_call(FILE_U8);
        }
    } else {
        // Честный брак: честная незакрытая группа {} (K-S3, TKT-033)
        Error_Flag = 0x00000001;
        Fail_Code = BRK_UNCLOSED;
        Fail_Position = Word_Index;
        out_cell(STREAM_EMIT_CELL, ERR_MARKER);
        sys_call(FILE_PUT);
    }

    // --- 1.6 (TKT-036): честный отчёт ДОПИСЫВАЕТСЯ в тот же артефакт ---
    // (артефакт открыт в main; вердикт-маркер выше; отчёт честно следует
    // после него, затем FILE_END — тишины нет, файл закрыт всегда).
    log_cell(STREAM_EMIT_CELL, Token_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Syntax_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Node_Counter);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Error_Flag);
    sys_call(FILE_PUT);
    // 1.5-б + TKT-033: 2 честных слова кода и позиции брака (артефакт = 40 байт)
    log_cell(STREAM_EMIT_CELL, Fail_Code);
    sys_call(FILE_PUT);
    log_cell(STREAM_EMIT_CELL, Fail_Position);
    sys_call(FILE_PUT);
    // TKT-048 веха-1: честная патч-фаза — адрес честного target в слоты
    // (позиция в файле = честный поток + размер заголовка v1.1)
        if (JP_Site_Call == 0x00000000) {
        // честно: вызовов не было
    } else {
        Stream_Emit = JP_Site_Call + 20;     // честная позиция операнда CALL в файле
        sys_call(FILE_SEEK);
        Stream_Emit = JP_Site_Term + 20;     // честный target: позиция байта OP_TERM
        sys_call(FILE_PUT);
        JP_Site_Call = 0x00000000;
    }
    if (JP_Site_If == 0x00000000) {
        // честно: if-ветвлений не было
    } else {
        if (JP_Else_Join == 0x00000000) {
            Patch_Target = JP_Site_Term;     // честно без else: обход до TERM
        } else {
            Patch_Target = JP_Else_Join;     // честно с else: вход в else-тело
        }
        Stream_Emit = JP_Site_If + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = Patch_Target + 20;
        sys_call(FILE_PUT);
        JP_Site_If = 0x00000000;
        JP_Else_Join = 0x00000000;
    }
    if (JP_Site_Jmp == 0x00000000) {
        // честно: else-переходов не было
    } else {
        Stream_Emit = JP_Site_Jmp + 20;
        sys_call(FILE_SEEK);
        Stream_Emit = JP_Site_Term + 20;     // честное схождение ветвей: TERM
        sys_call(FILE_PUT);
        JP_Site_Jmp = 0x00000000;
    }

    // TKT-040 веха-1: честное контрольное слово — VM патчит CRC-32 тела
    sys_call(FILE_SEAL);
    sys_call(FILE_END);
    // Честный отчет: токены / синтаксика / узлы / статус отказа
    // + честные код и позиция брака (TKT-033)
    log_cell(OUTPUT_BINARY_PORT, Token_Counter);
    log_cell(OUTPUT_BINARY_PORT, Syntax_Counter);
    log_cell(OUTPUT_BINARY_PORT, Node_Counter);
    log_cell(OUTPUT_BINARY_PORT, Error_Flag);
    log_cell(OUTPUT_BINARY_PORT, Fail_Code);
    log_cell(OUTPUT_BINARY_PORT, Fail_Position);
}

// Честный рекурсивный обход: одно слово за один вызов (как в спринте M1)
// Ловушка честная (найдена 1.1 трассой VM): база доходит ТОЛЬКО если
// после Word_Index = MAX не делать инкремент/рекурсию.
function Scan_Word_Loop() {
    if (Word_Index == MAX_SOURCE_WORDS) {
        // Честная база: граница буфера честно отщелкала
    } else {
        // Читаем очередное физическое слово из памяти устройства
        Current_Char = in_cell(Execution_Pointer);

        // Ограничитель: честное слово-терминатор исходника
        if (Current_Char == CH_WORD_END) {
            Word_Index = MAX_SOURCE_WORDS;
        }

        if (Word_Index == MAX_SOURCE_WORDS) {
            // честный терминатор честно закрыл проход — честный выход
        } else {
            // Слово еще не распознано: честная метка итерации
            Found_Flag = 0x00000000;

            // 1.6 (TKT-036): эмит-сайты честно пишут поток В АРТЕФАКТ
            // (STREAM_EMIT_CELL + FILE_PUT); порт остаётся только для
            // честного консольного отчёта (log_cell) — двойного честного
            // канала верификации нет: файл теперь единственный артефакт.
            // '#' -> директива препроцессора -> OP_INIT (0x01)
            if (Current_Char == D_WORD_PREPROC) {
                out_cell(STREAM_EMIT_CELL, OP_INIT_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'se' -> set -> OP_ALLOC_ST (0x10)
            if (Current_Char == KW_SET) {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'st' -> static -> OP_ALLOC_ST (0x10)
            if (Current_Char == KW_STATIC) {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'fu' -> function/pub entry -> OP_CALL (0x03) + честный слот:
            // операнд BE32 запоминается у JP_Site_Call (позиция = после байта
            // опкода), честный плейсхолдер 00000000 — патч в вердиктной фазе
            if (Current_Char == KW_FUNCTION) {
                out_cell(STREAM_EMIT_CELL, OP_CALL_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                JP_Site_Call = Emitted_Bytes;      // честная позиция операнда
                out_cell(STREAM_EMIT_CELL, 0x00000000);
                sys_call(FILE_U16);
                sys_call(FILE_U16);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'if' -> if -> OP_JZ (0x06) + честный слот (тот же честный механизм)
            // 'if' -> OP_JZ (0x06) + честный слот JP_Site_If; второй 'if' —
            // честный брак BRK_PATCH_OVERFLOW (fail-fast, правило первый-сбой)
            if (Current_Char == KW_IF) {
                if (JP_Site_If == 0x00000000) {
                    out_cell(STREAM_EMIT_CELL, OP_JZ_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    JP_Site_If = Emitted_Bytes;      // честная позиция операнда
                    out_cell(STREAM_EMIT_CELL, 0x00000000);
                    sys_call(FILE_U16);
                    sys_call(FILE_U16);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_PATCH_OVERFLOW;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            // 'es' -> else -> OP_JMP (0x07) + честный слот JP_Site_Jmp;
            // честное начало else-тела = позиция после операнда (туда прыгнет JZ)
            if (Current_Char == KW_ELSE) {
                out_cell(STREAM_EMIT_CELL, OP_JMP_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                JP_Site_Jmp = Emitted_Bytes;     // честная позиция операнда
                out_cell(STREAM_EMIT_CELL, 0x00000000);
                sys_call(FILE_U16);
                sys_call(FILE_U16);
                Emitted_Bytes = Emitted_Bytes + 4;
                JP_Else_Join = Emitted_Bytes;    // честное начало else-тела
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'te' -> terminate -> OP_TERM (0x05); честное запоминание позиции
            // байта TERM — честный target патча демо (адрес честного останова)
            if (Current_Char == KW_TERM) {
                out_cell(STREAM_EMIT_CELL, OP_TERM_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                JP_Site_Term = Emitted_Bytes - 1;  // честная позиция самого байта
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // Честные литералы (стадия-1.4, TKT-036): слово '0'..'9',
            // где сим1 == цифра 0x30..0x39 и сим2 == 0x00 (односимвольное
            // слово) -> честный OP_CONST 0x15 + честное ЗНАЧЕНИЕ.
            // Честная форма стадии-0: вычитание только "имя - число"
            // (десятичный RHS), значение честно живёт в ячейке Lit_Value
            // и эмитится честным log_cell (OP_OUTCELL_V), а не out_cell.
            // Ограничение честной модели (документировано в тикете):
            // в стадии-0 нет `*`/`/`, поэтому двухзначное слово честно
            // не собирается (d1*10+d2 нечем посчитать); длинные числа
            // честно разбиваются по словам — последовательные литералы.
            if (Current_Char == LIT_D0) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D1) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D2) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D3) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D4) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D5) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D6) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D7) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D8) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == LIT_D9) {
                Lit_Value = Current_Char - 48;
                out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, Lit_Value);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // Структурные слова: НЕ эмитят байт — честный подсчёт.
            // Скобки честно ведут стек групп (стадия-1.3): ловят
            // преждевременное закрытие и незакрытые группы в финале.
            if (Current_Char == SYM_BRACE_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Node_Brace_Depth = Node_Brace_Depth + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == SYM_BRACE_CLOSE) {
                if (Node_Brace_Depth == 0x00000000) {
                    // Честный отказ: '}' при пустом честном стеке {} (K-S2, TKT-033)
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

            if (Current_Char == SYM_PAREN_OPEN) {
                Syntax_Counter = Syntax_Counter + 1;
                Node_Paren_Depth = Node_Paren_Depth + 1;
                Found_Flag = 0x00000001;
            }

            if (Current_Char == SYM_PAREN_CLOSE) {
                if (Node_Paren_Depth == 0x00000000) {
                    // Честный отказ: ')' при пустом честном стеке () (K-S2, TKT-033)
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

            // Честный отказ: слово не совпало ни с одной честной сигнатурой
            // (K-S1, TKT-033) — честная позиция слова ЗАПОМИНАЕТСЯ ДО обрыва,
            // иначе Word_Index = MAX затирает честную позицию брака.
            // Приоритет честный: код брака = ПЕРВЫЙ честный сбой; если брак
            // уже был (Error_Flag == 1), честный код и позиция не трогаются —
            // иначе следом идущий unknown затёр бы честный код (ловлено
            // трассой Ф3: stray '}' не ставит Found_Flag и тянул K-S1 сверху).
            if (Found_Flag == 0x00000000) {
                if (Error_Flag == 0x00000000) {
                    Fail_Code = BRK_UNKNOWN_WORD;
                    Fail_Position = Word_Index;
                    Error_Flag = 0x00000001;
                    Word_Index = MAX_SOURCE_WORDS;
                }
            }

            if (Word_Index == MAX_SOURCE_WORDS) {
                // честный отказ или граница — выход без шага
            } else {
                // Шаг после чтения: честное смещение на машинное слово (4 байта)
                Execution_Pointer = Execution_Pointer + 4;
                Word_Index = Word_Index + 1;

                // Честный хвост рекурсии: безусловный — база остановит
                run Scan_Word_Loop();
            }
        }
    }
}
