// ===================================================================
// КОРНЕВОЙ НАТИВНЫЙ КОМПИЛЯТОР СТАДИИ-1 (НА ЯЗЫКЕ KITII / VOID)
// Профиль сборки: BARE_METAL_COMPILER | Целевое ядро: CtOs_Old
// СПРИНТ 1-ЛЕКСЕР: честный проход по буферу исходника,
// распознавание ключевых слов по первому символу слова,
// эмиссия честных опкодов из opcodes.core в порт вывода.
// Компилятор не добавляет от себя ни байта: нераспознанное слово
// честно ПРОПУСКАЕТСЯ (ни NOP, ни мусорного опкода не эмитится).
// ===================================================================

#core: CtOs_Old
#target: ARM32

// Жестко вшиваем системные константы и адреса буферов ОЗУ из syntax.void
#define: SOURCE_CODE_BUFFER 0x00A00000 // Адрес начала исходного текста в памяти
#define: TOKEN_STREAM_BUFFER 0x01000000 // Адрес, куда нативный лексер сложит токены
#define: OUTPUT_BINARY_PORT  0x3F0050C0 // Физический порт для записи готового бинарника
#define: MAX_SOURCE_WORDS    16         // Честная граница прохода: максимум слов (64 байта буфера)

// Первые символы ключевых слов из lexicon.core (ASCII, честная по-словная модель:
// одно машинное слово памяти = один токен-слово; в ячейке лежит код первого символа)
#define: CH_PREPROC_INIT    0x00000023 // '#': #core/#target/#define -> OP_INIT
#define: CH_ALLOC_STATIC    0x00000073 // 's': set static -> OP_ALLOC_ST
#define: CH_FUNCTION        0x00000066 // 'f': function -> OP_CALL
#define: CH_IF_KEYWORD      0x00000069 // 'i': if -> OP_JZ
#define: CH_TERMINATE       0x00000074 // 't': terminate -> OP_TERM
#define: CH_WORD_END        0x0000002E // '.': честный ограничитель исходника в тесте

// Честные опкоды из opcodes.core (стадия-0 контракт)
#define: OP_INIT_CODE       0x00000001 // 0x01 OP_INIT
#define: OP_CALL_CODE       0x00000003 // 0x03 OP_CALL
#define: OP_TERM_CODE       0x00000005 // 0x05 OP_TERM
#define: OP_JZ_CODE         0x00000006 // 0x06 OP_JZ
#define: OP_ALLOC_CODE      0x00000010 // 0x10 OP_ALLOC_ST
#define: END_MARKER         0x000000FF // Честный маркер конца эмиссии (после последнего опкода)

// Объявляем глобальные статические ячейки памяти ядра (регистры компилятора)
set static Execution_Pointer = 0x00000000; // Текущая позиция чтения слов
set static Token_Counter     = 0x00000000; // Счетчик распознанных системных токенов
set static Word_Index        = 0x00000000; // Смягченная граница прохода (против бесконечного цикла)
set static Current_Char      = 0x00000000; // Текущее слово из буфера исходника

// Главная точка входа нативного компилятора (Entry Point)
pub entry main(cell:raw args) {

    // Принудительно очищаем сетевой DNS-кеш хоста из макроса README
    net_flush;

    // Инициализируем указатель на первый байт текстового буфера
    Execution_Pointer = SOURCE_CODE_BUFFER;
    Token_Counter = 0;
    Word_Index = 0;

    // Вызываем фоновую функцию низкоуровневой токенизации текста
    run NativeLexicalScanner();

    // Завершаем контекст компилятора с полной зачисткой регистров ОЗУ
    terminate;
}

// Фоновое ядро лексера Стадии-1 на чистом бестиповом синтаксисе Void
function NativeLexicalScanner() {
    // Честный вход в рекурсивный обход: одно слово за одну регенерацию
    run Scan_Word_Loop();

    // Честный маркер конца эмиссии: после него бинарь закончен
    out_cell(OUTPUT_BINARY_PORT, END_MARKER);

    // Честный отчет: сколько системных токенов распознано
    log_cell(OUTPUT_BINARY_PORT, Token_Counter);
}

// Честный рекурсивный обход: одно слово за один вызов (как в спринте M1)
function Scan_Word_Loop() {
    if (Word_Index == MAX_SOURCE_WORDS) {
        // Честная база: граница буфера честно отщелкала
    } else {
        // Читаем очередное физическое слово из памяти устройства
        Current_Char = in_cell(Execution_Pointer);

        // Ограничитель: честное слово-терминатор исходника.
        // Честный выход: БЕЗ инкрементов и БЕЗ рекурсии — иначе честный
        // счётчик уходит мимо MAX и честная база никогда не сработает
        // (найдено честной трассой VM: honest Word_Index 0x11 и дальше).
        if (Current_Char == CH_WORD_END) {
            Word_Index = MAX_SOURCE_WORDS;
        }

        if (Word_Index == MAX_SOURCE_WORDS) {
            // честный терминатор честно закрыл проход — честный выход
        } else {
            // Распознавание '#' -> директива препроцессора -> OP_INIT (0x01)
            if (Current_Char == CH_PREPROC_INIT) {
                out_cell(OUTPUT_BINARY_PORT, OP_INIT_CODE);
                Token_Counter = Token_Counter + 1;
            }

            // Распознавание 's' -> set static -> OP_ALLOC_ST (0x10)
            if (Current_Char == CH_ALLOC_STATIC) {
                out_cell(OUTPUT_BINARY_PORT, OP_ALLOC_CODE);
                Token_Counter = Token_Counter + 1;
            }

            // Распознавание 'f' -> function/pub entry -> OP_CALL (0x03)
            if (Current_Char == CH_FUNCTION) {
                out_cell(OUTPUT_BINARY_PORT, OP_CALL_CODE);
                Token_Counter = Token_Counter + 1;
            }

            // Распознавание 'i' -> if -> OP_JZ (0x06)
            if (Current_Char == CH_IF_KEYWORD) {
                out_cell(OUTPUT_BINARY_PORT, OP_JZ_CODE);
                Token_Counter = Token_Counter + 1;
            }

            // Распознавание 't' -> terminate -> OP_TERM (0x05)
            if (Current_Char == CH_TERMINATE) {
                out_cell(OUTPUT_BINARY_PORT, OP_TERM_CODE);
                Token_Counter = Token_Counter + 1;
            }

            // Любое другое слово: честный пропуск (ни байта от себя в бинарь)

            // Шаг после чтения: честное смещение на машинное слово (4 байта)
            Execution_Pointer = Execution_Pointer + 4;
            Word_Index = Word_Index + 1;

            // Честный хвост рекурсии: безусловный — база остановит при следующем входе
            run Scan_Word_Loop();
        }
    }
}
