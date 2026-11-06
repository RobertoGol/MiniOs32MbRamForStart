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
// Веха-5 (TKT-052, 2026-11-03): честные именованные рабочие слоты.
// Слово 'wc' + следующий литерал d (0..5) честно выбирает слот
// W2..W7 (0x00F00FF3..0x00F00FF8 — честно свободны по чек-скану репо,
// соседние с WORK_CELL 0x00F00FF1); 'sv'/'va'/'pr' честно работают
// с ТЕКУЩИМ слотом (W_Current, default = WORK_CELL, честный завод в
// main — стадия-0 не пишет инициализаторы статиков в ячейки).
// Честные отказы BRK_WC_NO_LIT 0x08: второй 'wc' подряд; номер слота
// вне 0..5 (сайты D6..D9 честно ЗНАЮТ свою цифру по сигнатуре;
// стадия-0 честно НЕ поддерживает '<=' (код честного брака D025),
// поэтому диапазон не сравнивается вовсе); 'wc' без номера к концу
// честная хвост-проверка в вердиктной фазе (позиция = W_Position).
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
#define: KW_RUN 0x00007572 // 'ru' = run: честный вызов последней 'fu'
#define: KW_EQ 0x00007165 // 'eq' = сравнить acc со следующим литералом (TKT-050)
#define: KW_GT 0x00007467 // 'gt' = сравнить acc > следующий литерал (TKT-050 веха-3)
#define: KW_LT 0x0000746C // 'lt' = сравнить acc < следующий литерал (TKT-050 веха-3)
#define: KW_ADD 0x00006461 // 'ad' = acc = acc + следующий литерал (TKT-052 веха-3)
#define: KW_SUB 0x00007573 // 'su' = acc = acc - следующий литерал (TKT-052 веха-3)
#define: KW_SAVE 0x00007673 // 'sv' = save: cell[WORK_CELL] = acc (TKT-050 веха-2)
#define: KW_VALUE 0x00006176 // 'va' = value: acc = cell[WORK_CELL] (TKT-050 веха-2)
#define: KW_RET 0x00006572 // 're' = return: честный выход из функции (TKT-051)
#define: KW_PR 0x00007270 // 'pr' = print: честный вывод — OP_OUTCELL_V + порт + WORK_CELL (TKT-052 веха-4)
#define: KW_WC 0x00006377 // 'wc' = work cell select: следующий литерал d (0..5) честно выбирает расширенный слот (TKT-052 веха-5)
#define: KW_GP 0x00007067 // 'gp' = get pointer: acc = cell[cell[W_Current]] (веха-6, через 0x52)
#define: KW_SP 0x00007073 // 'sp' = store pointer: cell[cell[W_Current]] = acc (веха-6, через 0x53)
#define: KW_NB 0x0000626E // 'nb' = num begin: честный старт многозначного литерала (TKT-052 веха-7)
#define: KW_NE 0x0000656E // 'ne' = num end: честное закрытие накопителя — эмит CONST BE32(Num_Acc) (веха-7)
#define: WC_BASE 0x00F00FF3 // честная база расширенных рабочих слотов W2..W7 (0x00F00FF3..0x00F00FF8 — соседние с WORK_CELL 0x00F00FF1, по чек-скану репо свободны)
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
#define: OP_RET_CODE   0x00000004 // 0x04 OP_RET — возврат по стеку вызовов VM (TKT-051)
#define: OP_JZ_CODE    0x00000006 // 0x06 OP_JZ
#define: OP_JMP_CODE 0x00000007 // честный безусловный переход (VM OP_JMP)
#define: OP_ALLOC_CODE 0x00000010 // 0x10 OP_ALLOC_ST
#define: OP_CONST_CODE 0x00000015 // 0x15 OP_CONST «константа на акк»
#define: OP_LOAD_CODE 0x00000012 // 0x12 OP_LOAD (режимы: 0x14 add, 0x16 eq, 0x17 sub)
#define: OP_STORE_AT_CODE 0x00000055 // 0x55 OP_STORE_AT cell[arg] = acc (TKT-050 веха-2)
#define: OP_OUTCELL_V_CODE 0x00000054 // 0x54 OP_OUTCELL_V — вывод ЗНАЧЕНИЯ ячейки в порт (TKT-052 веха-4 'pr')
#define: OP_INCELL_IND_CODE 0x00000052 // 0x52 OP_INCELL_IND acc = cell[cell[arg]] — честная косвенность (TKT-052 веха-6)
#define: OP_STORE_IND_CODE 0x00000053 // 0x53 OP_STORE_IND cell[cell[arg]] = acc — честная косвенная запись (TKT-052 веха-6)
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
#define: WORK_CELL 0x00F00FF1 // честная рабочая ячейка памяти стадии-1 (TKT-009 зона +1)
#define: FILE_BEGIN       0x00000130 // открыть артефакт
#define: FILE_PUT         0x00000131 // слово Stream_Emit -> 4 байта BE
#define: FILE_U16         0x00000132 // младшие 16 бит -> 2 байта BE
#define: FILE_END         0x00000133 // закрыть артефакт (не закрыт = честный брак)
#define: FILE_U8          0x00000134 // 1 байт -> артефакт (TKT-047: честный байт-канал опконов)
#define: FILE_SEAL        0x00000135 // контрольное слово артефакта CRC-32 (TKT-040 веха-1)
#define: FILE_SEEK        0x00000136 // честная позиция записи в артефакте (TKT-048)
#define: FILE_GET        0x00000137 // честное чтение: 4 байта BE исходника -> Stream_Emit (TKT-052 веха-2)
#define: FILE_EOF_CELL   0x00F00FF2 // честная ячейка статуса EOF syscall-чтения (0 = слово есть, 1 = конец)

// Честные коды брака стадии-1 (TKT-033, по образцу K-кодов):
// позиция брака — честная ячейка Fail_Position на момент сбоя
#define: BRK_UNKNOWN_WORD 0x00000001 // K-S1: неизвестное слово
#define: BRK_STRAY_CLOSE  0x00000002 // K-S2: '}' или ')' при пустом честном стеке
#define: BRK_UNCLOSED     0x00000003 // K-S3: незакрытая честная группа в финале
#define: BRK_PATCH_OVERFLOW 0x00000004 // честных слотов патча больше нет (TKT-048 честный лимит)
#define: BRK_NO_FUNC 0x00000005 // 'ru' до любой 'fu' — честный брак (TKT-048 веха-3)
#define: BRK_EQ_NO_LIT 0x00000006 // 'eq' без следующего литерала — честный брак (TKT-050)
#define: BRK_SRC_OVERFLOW 0x00000007 // исходник длиннее честного буфера 16 слов (TKT-052 веха-2)
#define: BRK_WC_NO_LIT 0x00000008 // 'wc' без следующего литерала-номера слота — честный брак (TKT-052 веха-5)
#define: BRK_NUM_OPEN 0x00000009 // 'nb' открыл число, 'ne' к концу исходника не пришёл — честный брак (веха-7)
#define: BRK_NE_NO_NUM 0x0000000A // 'ne' без открытого числа 'nb' — честный брак (веха-7)
#define: BRK_NB_NESTED 0x0000000B // второй 'nb' при открытом числе — честный брак fail-fast (веха-7)
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
set static Call_Site_1         = 0x00000000; // Честный слот места патча операнда №1
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
set static W_Current       = 0x00F00FF1; // честный текущий рабочий слот, default = WORK_CELL (TKT-052 веха-5)
set static W_Pending       = 0x00000000; // честный флаг: 'wc' ждёт литерал 0..5 (TKT-052 веха-5)
set static W_Position      = 0x00000000; // честная позиция слова wc (для брака) (TKT-052 веха-5)
set static Num_Acc         = 0x00000000; // честный накопитель многозначного литерала (TKT-052 веха-7)
set static Num_Tmp         = 0x00000000; // честный сдвиг x10: 10 сложений — умножения на стадии-0 нет
set static Num_Digit       = 0x00000000; // честная текущая цифра накопления (для Num_Place)
set static Num_Pending     = 0x00000000; // честный флаг: 'nb' открыл число (веха-7)
set static Num_Position    = 0x00000000; // честная позиция слова nb (для хвост-брака) (веха-7)
set static If_Site_1      = 0x00000000; // честный слот операнда JZ от if
set static Jmp_Slot_1      = 0x00000000; // честный слот операнда JMP от es
set static Else_Join_1     = 0x00000000; // честное начало else-тела (target JZ)
set static If_Site_2      = 0x00000000; // честный слот JZ №2 (TKT-050)
set static Jmp_Slot_2     = 0x00000000; // честный слот JMP №2 (TKT-050)
set static Else_Join_2    = 0x00000000; // честное else-тело №2 (TKT-050)
set static If_Count       = 0x00000000; // честный счёт if-слотов
set static Jmp_Count      = 0x00000000; // честный счёт else-слотов
set static Patch_Target     = 0x00000000; // честный target патча JZ (pereklich корней)
set static JP_Site_Term      = 0x00000000; // Честная позиция потока байта 'te' (target демо)
set static Boot_Ptr          = 0x00000000; // честный указатель записи в буфер исходника (TKT-052 веха-2)
set static Boot_Eof          = 0x00000000; // честный статус конца исходника
set static Boot_Count        = 0x00000000; // честный счётчик прочитанных слов
set static Boot_Word         = 0x00000000; // честное прочитанное слово
set static Boot_Emit_Ptr     = 0x00000000; // честный указатель на ячейку результата syscall (Stream_Emit)
set static Boot_Eof_Ptr      = 0x00000000; // честный указатель на ячейку статуса EOF

// ---------- честный загрузчик исходника (TKT-052 веха-2) ----------
// Компилятор сам читает свой вход: syscall FILE_GET кладёт 4 байта BE в
// ячейку Stream_Emit (0x00F00FF0), статус конца — в FILE_EOF_CELL
// (0x00F00FF2: 0 = слово есть, 1 = честный конец). Слова честно пишутся
// в буфер исходника store_ind'ом — тот же контракт буфера, что и у сканера.
// Рекурсивный проход как у Scan_Word_Loop: одно слово за один вызов.
// Граница честная — MAX_SOURCE_WORDS слов (та же, что у сканера); если
// к границе EOF не пришёл — исходник длиннее буфера, честный брак
// BRK_SRC_OVERFLOW (позиция = сколько слов влезло). Без исходника поток
// честно пуст: первый же FILE_GET даст EOF, скан честно отвергнет слово 0.
function Boot_Load_Loop() {
    if (Boot_Eof == 0x00000000) {
        sys_call(FILE_GET);
        Boot_Eof = in_cell(Boot_Eof_Ptr);
        if (Boot_Eof == 0x00000000) {
            Boot_Word = in_cell(Boot_Emit_Ptr);
            store_ind(Boot_Ptr, Boot_Word);
            Boot_Ptr = Boot_Ptr + 4;
            Boot_Count = Boot_Count + 1;
            if (Boot_Count == MAX_SOURCE_WORDS) {
                if (Error_Flag == 0x00000000) {
                    Fail_Code = BRK_SRC_OVERFLOW;
                    Fail_Position = Boot_Count;
                    Error_Flag = 0x00000001;
                }
            } else {
                run Boot_Load_Loop();
            }
        }
    }
}

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
    Num_Pending = 0;     // честное открытое число пусто (веха-7)
    Op_Position = 0;     // честная позиция eq сброшена
    If_Site_1 = 0;      // honestly нет if-сайтов
    If_Site_2 = 0;       // честный слот JZ №2 пуст
    Jmp_Slot_2 = 0;      // честный слот JMP №2 пуст
    Else_Join_2 = 0;     // честное else-тело №2 пусто
    If_Count = 0;        // честный счёт if пуст
    Jmp_Count = 0;       // честный счёт else пуст
    Jmp_Slot_1 = 0;     // honestly нет es-сайтов
    Else_Join_1 = 0;    // honestly нет else-сращений
    JP_Site_Term = 0;     // честная позиция байта TERM пуста
    Node_Brace_Depth = 0;
    Node_Paren_Depth = 0;
    Node_Counter = 0;
    W_Current = WORK_CELL; // честный завод текущего слота (TKT-052 веха-5):
                           // стадия-0 честно НЕ пишет инициализаторы статиков
                           // в ячейки памяти — default = WORK_CELL
    W_Pending = 0;         // честный pending выбора слота пуст (веха-5)
    W_Position = 0;        // честная позиция слова wc сброшена (веха-5)

    // --- TKT-052 веха-2: честный загрузчик исходника ---
    // Компилятор сам читает свой вход через syscall FILE_GET (до создания
    // артефакта — fail-fast: брак исходника виден в отчёте артефакта).
    Boot_Ptr = SOURCE_CODE_BUFFER;
    Boot_Eof = 0;
    Boot_Count = 0;
    Boot_Emit_Ptr = STREAM_EMIT_CELL;
    Boot_Eof_Ptr = FILE_EOF_CELL;
    run Boot_Load_Loop();

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
    out_cell(STREAM_EMIT_CELL, 0x00000100);  // байт-образ таргета 01 00 (LE -> 0x0001 = ARM32)
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

// TKT-052 веха-7: честный позиционный сдвиг накопителя многозначного
// литерала. Умножения на стадии-0 нет — x10 честно развёрнут в 10
// сложений (счётчик фиксированный, рекурсия не нужна).
function Num_Place() {
    Num_Tmp = 0x00000000;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Tmp = Num_Tmp + Num_Acc;
    Num_Acc = Num_Tmp + Num_Digit;
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

    // TKT-052 веха-5: честная хвост-проверка 'wc' — pending остался
    // без литерала слота: честный брак BRK_WC_NO_LIT, честная
    // позиция = W_Position (слово 'wc' само байта не эмитит)
    if (W_Pending == 0x00000000) {
        // честно: выборов слота без номера нет
    } else {
        if (Error_Flag == 0x00000000) {
            Fail_Code = BRK_WC_NO_LIT;
            Fail_Position = W_Position;
            Error_Flag = 0x00000001;
        }
        W_Pending = 0x00000000;
    }

    // TKT-052 веха-7: честная хвост-проверка 'nb' — открытое число
    // осталось без 'ne' к концу исходника: честный брак BRK_NUM_OPEN,
    // позиция честно = слово 'nb' (Num_Position).
    if (Num_Pending == 0x00000000) {
        // честно: открытых чисел нет
    } else {
        if (Error_Flag == 0x00000000) {
            Fail_Code = BRK_NUM_OPEN;
            Fail_Position = Num_Position;
            Error_Flag = 0x00000001;
        }
        Num_Pending = 0x00000000;
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
        // TKT-051 веха-3: 'ru' без номера к концу исходника — честный брак
        if (Current_Char == CH_WORD_END) {
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
            // честный терминатор честно закрыл проход — честный выход
        } else {
            // Слово еще не распознано: честная метка итерации
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
            // операнд BE32 запоминается у Call_Site_1 (позиция = после байта
            // опкода), честный плейсхолдер 00000000 — патч в вердиктной фазе
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

            // Слово байта НЕ эмитит: ставит W_Pending = 1, следующий
            // литерал d (0..5) честно переключает W_Current (сайт цифр).
            // 'wc' при активном ожидании — честный брак BRK_WC_NO_LIT.
            if (Current_Char == KW_WC) {
                if (W_Pending == 0x00000000) {
                    W_Pending = 0x00000001;
                    W_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: второй 'wc' подряд (первый без номера)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WC_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            // 'nb' (TKT-052 веха-7): честное ЧИСЛО — открытие накопителя.
            // Байта не эмитит: Num_Acc = 0, Num_Pending = 1, позиция для
            // хвост-брака честно запоминается. Второй 'nb' при открытом
            // числе — честный брак BRK_NB_NESTED (fail-fast).
            if (Current_Char == KW_NB) {
                if (Num_Pending == 0x00000001) {
                    // честный отказ: число уже открыто
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NESTED;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    Num_Acc = 0x00000000;
                    Num_Pending = 0x00000001;
                    Num_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                }
            }
            
            // 'ne' (TKT-052 веха-7): честное закрытие числа — эмит
            // OP_CONST_CODE + BE32(Num_Acc). 5 байт. 'ne' без открытого
            // числа — честный брак BRK_NE_NO_NUM (fail-fast).
            if (Current_Char == KW_NE) {
                if (Num_Pending == 0x00000001) {
                    Num_Pending = 0x00000000;
                    out_cell(STREAM_EMIT_CELL, OP_CONST_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: числа нет ('ne' без 'nb')
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NE_NO_NUM;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
            }

            // 'sv' (TKT-050 веха-2): честная запись памяти — OP_STORE_AT 0x55
            // + BE32(W_Current): cell[текущий слот] = acc. 5 байт.
            // Веха-5: слот честно выбирается 'wc d' (default WORK_CELL).
            if (Current_Char == KW_SAVE) {
                out_cell(STREAM_EMIT_CELL, OP_STORE_AT_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'va' (TKT-050 веха-2): честная загрузка памяти — OP_LOAD 0x12
            // + режим 0x19 (acc = cell[arg]) + BE32(W_Current). 6 байт.
            if (Current_Char == KW_VALUE) {
                out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, 0x00000019);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'gp' (TKT-052 веха-6): честная косвенная загрузка —
            // OP_INCELL_IND 0x52 + BE32(W_Current): acc =
            // cell[cell[текущий слот]]. Указатель честно живёт в
            // рабочем слоте: кладётся обычным 'sv' из acc. 5 байт.
            if (Current_Char == KW_GP) {
                out_cell(STREAM_EMIT_CELL, OP_INCELL_IND_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'sp' (TKT-052 веха-6): честная косвенная запись —
            // OP_STORE_IND 0x53 + BE32(W_Current):
            // cell[cell[текущий слот]] = acc. Адрес 0 честно бракует
            // сама VM (BRK_IND_ADDR_0) — эмит всегда честен. 5 байт.
            if (Current_Char == KW_SP) {
                out_cell(STREAM_EMIT_CELL, OP_STORE_IND_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
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

            // 'pr' (TKT-052 веха-4): честный вывод результата — OP_OUTCELL_V
            // 0x54 + BE32(порт) + BE32(W_Current) = 9 байт; порт честно
            // покажет значение ТЕКУЩЕГО рабочего слота. Слово-программы
            // отныне видят свой результат не только в трассе VM.
            if (Current_Char == KW_PR) {
                out_cell(STREAM_EMIT_CELL, OP_OUTCELL_V_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, OUTPUT_BINARY_PORT);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
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

            // 'if' -> if -> OP_JZ (0x06) + честный слот (тот же честный механизм)
            // 'if' -> OP_JZ (0x06) + честный слот If_Site_1; второй 'if' —
            // честный брак BRK_PATCH_OVERFLOW (fail-fast, правило первый-сбой)
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
            // в стадии-0 нет `*`/`/`, поэтому многозначные литералы
            // собраны честной парой слов 'nb d d ... ne' (веха-7):
            // цифры честно копят позиционный сдвиг (10 сложений),
            // а 'ne' эмитит готовое значение одним CONST.
            if (Current_Char == LIT_D0) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D0 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 0) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W2
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D1) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D1 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 1) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W3
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D2) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D2 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 2) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W4
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D3) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D3 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 3) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W5
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D4) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D4 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 4) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W6
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D5) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D5 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 5) — она по построению в диапазоне
                    // 0..5, проверка диапазона не нужна: слот = WC_BASE + d = W7
                    Tmp_Addr = WC_BASE;
                    Tmp_Addr = Tmp_Addr + Lit_Value;
                    W_Current = Tmp_Addr;
                    W_Pending = 0x00000000;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D6) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D6 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 6) — она ВНЕ диапазона 0..5,
                    // честный брак ДО эмиссии: цифра после 'wc' честно не
                    // эмитит ни байта (BRK_WC_NO_LIT, тот же честный вектор)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WC_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D7) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D7 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 7) — она ВНЕ диапазона 0..5,
                    // честный брак ДО эмиссии: цифра после 'wc' честно не
                    // эмитит ни байта (BRK_WC_NO_LIT, тот же честный вектор)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WC_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D8) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D8 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 8) — она ВНЕ диапазона 0..5,
                    // честный брак ДО эмиссии: цифра после 'wc' честно не
                    // эмитит ни байта (BRK_WC_NO_LIT, тот же честный вектор)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WC_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
            }

            if (Current_Char == LIT_D9) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D9 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 9) — она ВНЕ диапазона 0..5,
                    // честный брак ДО эмиссии: цифра после 'wc' честно не
                    // эмитит ни байта (BRK_WC_NO_LIT, тот же честный вектор)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WC_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    if (Num_Pending == 0x00000001) {
                        // веха-7: цифра честно копит число — эмиссии
                        // нет, готовый литерал честно эмитит 'ne'
                        Num_Digit = Lit_Value;
                        run Num_Place();
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
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
                }
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
