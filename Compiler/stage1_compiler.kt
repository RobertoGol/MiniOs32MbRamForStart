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
// Слово 'wc' + следующий литерал d (0..5 по вехе-5, 0..9 с вехи-15)
// честно выбирает слот
// W2..WB (0x00F00FF3..0x00F00FFC — веха-15: диапазон цифр 'wc' 0..9;
// F3..F8 свободны по чек-скану репо, F9..FB совпадают с TMP-ячейками
// кольца 'ml' вехи-12б, FFC свободен); 'sv'/'va'/'pr' честно работают
// с ТЕКУЩИМ слотом (W_Current, default = WORK_CELL, честный завод в
// main — стадия-0 не пишет инициализаторы статиков в ячейки).
// Честный отказ BRK_WC_NO_LIT 0x08: второй 'wc' подряд; 'wc' без
// номера к концу исходника — честная хвост-проверка в вердиктной
// фазе (позиция = W_Position). Диапазон цифр 'wc': стадия-0 честно
// НЕ поддерживает '<=' (код честного брака D025) — сравнения нет,
// каждый сайт цифр честно знает свою цифру по сигнатуре; веха-15
// честно расширила диапазон 0..5 -> 0..9 (W_Pending-ветви сайтов
// D6..D9 активированы: слот = WC_BASE + d = 0x00F00FF9..0x00F00FFC);
// ДО вехи-15 цифры 6..9 честно браковались этим кодом (факт d=6:
// Fail_Code 0x08@1, вердец 0xFE, эталон стадии-1 45 Б).
// Веха-10 (TKT-052, 2026-11-06): 'wc' стал честным ПЯТЫМ поглотителем
// nb-числа (вехи-8 список непоглотителей 13 -> 12): форма 'nb X wc'
// выбирает слот АБСОЛЮТНО — W_Current = BE32(Num_Acc), но только по
// честному номиналу рабочих слотов {0x00F00FF1 (WORK), 0x00F00FF3..
// 0x00F00FFC (W2..WB; веха-15)} — вне номинала честный брак
// BRK_WC_RANGE 0x0D
// (fail-fast, позиция = слово 'wc'); '<=' на стадии-0 нет — номинал
// честно развёрнут в цепь равенств; цифровые ветки и 'ne' не изменены.
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
#define: MAX_SOURCE_WORDS    0x00000200 // Честная граница прохода: максимум слов (512; веха-9: 16→64, веха-12г: 64→128, веха-13: 128→256, веха-14v4: 256→512 — честному выводу Syntax/Node отчёта word-компилятора нужно 261 токен, лимит 254 = честный OVERFLOW; как вехи-12г/13, граница растёт от честной механики, «просто так» не двигается)

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
#define: KW_WC 0x00006377 // 'wc' = work cell select: следующий литерал d (0..5 по вехе-5, 0..9 с вехи-15) честно выбирает расширенный слот (TKT-052 веха-5)
#define: KW_GP 0x00007067 // 'gp' = get pointer: acc = cell[cell[W_Current]] (веха-6, через 0x52)
#define: KW_SP 0x00007073 // 'sp' = store pointer: cell[cell[W_Current]] = acc (веха-6, через 0x53)
#define: KW_NB 0x0000626E // 'nb' = num begin: честный старт многозначного литерала (TKT-052 веха-7)
#define: KW_NE 0x0000656E // 'ne' = num end: честное закрытие накопителя — эмит CONST BE32(Num_Acc) (веха-7)
#define: WC_BASE 0x00F00FF3 // честная база расширенных рабочих слотов W2..WB (0x00F00FF3..0x00F00FFC — веха-15: диапазон цифр 'wc' 0..9; F3..F8 свободны по чек-скану, F9..FB совпадают с TMP 'ml' вехи-12б, FFC свободен)
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
#define: OP_SYSCALL_CODE 0x00000013 // 0x13 OP_SYSCALL — честный syscall-канал слова 'sc' (веха-12в)
#define: OP_OUTCELL_CODE 0x00000051 // 0x51 OP_OUTCELL cell[arg] = val — честная запись КОНСТАНТЫ в ячейку слова 'em' (веха-12в)
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
#define: BRK_WC_NO_LIT 0x00000008 // 'wc' без следующего литерала-номера слота — честный брак (TKT-052 веха-5; до вехи-15 им же браковались цифры 6..9)
#define: BRK_NUM_OPEN 0x00000009 // 'nb' открыл число, 'ne' к концу исходника не пришёл — честный брак (веха-7)
#define: BRK_NE_NO_NUM 0x0000000A // 'ne' без открытого числа 'nb' — честный брак (веха-7)
#define: BRK_NB_NESTED 0x0000000B // второй 'nb' при открытом числе — честный брак fail-fast (веха-7)
#define: BRK_NB_NO_CONS 0x0000000C // оператор без поглощения при открытом nb-числе — честный брак fail-fast (веха-8)
#define: BRK_WC_RANGE 0x0000000D // поглощённый 'wc' вне честного номинала рабочих слотов — честный брак fail-fast (веха-10; веха-15: номинал цифр 0..9)
// Веха-10: честный номинал слот-зоны для 'nb X wc' (адреса абсолютные):
// WORK_CELL + расширенные W2..WB (веха-15: цифры 0..9); системные ячейки
// 0x00F00FF0 (Stream_Emit) и 0x00F00FF2 (FILE_EOF) в номинал НЕ входят —
// 'wc' выбирает только рабочие слоты. Веха-15: W8/W9/WA честно совпадают
// с TMP_CNT/TMP_ACC/TMP_X кольца 'ml' (веха-12б) — совместное
// использование 'wc 6..8' и 'ml' в одной программе честно не определено.
#define: KW_MK          0x00006B6D // 'mk' = честная метка цикла: НЕ эмитит байт, Mark_Pos = Emitted_Bytes (веха-12а)
#define: KW_JB          0x0000626A // 'jb' = честный обратный прыжок: OP_JMP 0x07 + BE32(Mark_Pos + 20) = 5 Б (веха-12а)
#define: KW_ML          0x00006C6D // 'ml' = честное умножение acc на цифру-литерал 0..9 (веха-12б)
#define: BRK_ML_NO_LIT  0x0000000F // 'ml' без цифры-множителя — честный брак fail-fast (веха-12б)
#define: TMP_X   0x00F00FFB // честная TMP-ячейка: множимое (копия acc) кольца 'ml' (веха-12б)
#define: TMP_CNT 0x00F00FF9 // честная TMP-ячейка: счётчик кольца 'ml' (веха-12б)
#define: TMP_ACC 0x00F00FFA // честная TMP-ячейка: накопитель произведения 'ml' (веха-12б)
#define: BRK_JB_NO_MARK 0x0000000E // 'jb' без честной метки 'mk' — честный брак fail-fast (веха-12а)
// Веха-12в (TKT-052): честный «эмиттер-минима» — syscall и запись константы
// в произвольную ячейку. Аддитивные слова: ничего из сделанного не тронуто.
#define: KW_SC 0x00006373 // 'sc' = syscall: OP_SYSCALL 0x13 + BE32(N) = 5 Б; ШЕСТОЙ поглотитель nb-числа (веха-12в)
#define: KW_EM 0x00006D65 // 'em' = emit: OP_OUTCELL 0x51 + BE32(STREAM_EMIT_CELL) + BE32(N) = 9 Б; СЕДЬМОЙ поглотитель nb-числа (веха-12в)
#define: BRK_SC_NO_NUM 0x00000010 // 'sc' без открытого nb-числа — честный брак fail-fast (веха-12в)
#define: BRK_EM_NO_NUM 0x00000011 // 'em' без открытого nb-числа — честный брак fail-fast (веха-12в)
#define: KW_WO 0x00006F77 // 'wo' = word out: OP_OUTCELL(STREAM, N) + OP_SYSCALL(FILE_PUT) = 14 Б; ВМЕСТО пары 'em'+sc 0x131 (~5 слов языка → 1 слово) (веха-12г)
#define: KW_OW 0x0000776F // 'ow' = out word-slot: OP_OUTCELL_V(STREAM, W_Current) + OP_SYSCALL(FILE_PUT) = 14 Б; честный канал «значение слота → файл» — эмиссия-runtime значения вместо литерал-константы (веха-14v2); 'ow' НЕ поглотитель nb — открытый nb честно бракует 0x0C
#define: KW_AA 0x00006161 // 'aa' = add acc cell: OP_LOAD 0x12 + режим 0x15 (acc += cell[X]) + BE32(X) = 6 Б; ДЕСЯТЫЙ поглотитель nb (веха-14v3); честный режим 0x15 есть в VM (ctos_vm.py:395); без открытого nb — fail-fast 0x0C
#define: KW_AS 0x00007361 // 'as' = add slot: acc += cell[W_Current]; cell[W_Current] = acc — OP_LOAD 0x12 + режим 0x15 + BE32(W_Current) [6 Б] + OP_STORE_AT 0x55 + BE32(W_Current) [5 Б] = 11 Б (веха-14v3); честный слот-аккумулятор; НЕ поглотитель nb — открытый nb честно бракует 0x0C
#define: KW_VW 0x00007776 // 'vw' = value word: W_Current -> STREAM_EMIT_CELL -> FILE_PUT = 4 Б в поток (веха-14v3); честный КОМПИЛ-ВРЕМЕННЫЙ канал: в артефакт честно ложится АДРЕС СЛОТА-константа BE32(W_Current), а НЕ runtime-значение ячейки (проба pos_vw1: факт байтов "00 F0 0F F5"); runtime-значение честно даёт только 'ow' (веха-14v2) — потому wc14v3 честно берёт 'ow'; честный var_addr-близнец 'pr'/'ow' без конверта 0x54; НЕ поглотитель nb — открытый nb честно бракует 0x0C
#define: BRK_WO_NO_NUM 0x00000012 // 'wo' без открытого nb-числа — честный брак fail-fast (веха-12г)
#define: KW_CP 0x00007063 // 'cp' = cell compare: ДЕВЯТЫЙ поглотитель nb — acc = (acc == cell[Num_Acc]): OP_LOAD 0x12 + режим 0x18 + BE32(адрес) = 6 Б (веха-13, честный словарь word-компилятора)
#define: BRK_CP_NO_NUM 0x00000013 // 'cp' без открытого nb-числа — честный брак fail-fast (веха-13)
#define: WC_LIT_WORK 0x00F00FF1 // номинал: WORK_CELL (десятичный 15732721)
#define: WC_LIT_W2 0x00F00FF3 // номинал: W2 = WC_BASE + 0 (десятичный 15732723)
#define: WC_LIT_W3 0x00F00FF4 // номинал: W3 = WC_BASE + 1 (десятичный 15732724)
#define: WC_LIT_W4 0x00F00FF5 // номинал: W4 = WC_BASE + 2 (десятичный 15732725)
#define: WC_LIT_W5 0x00F00FF6 // номинал: W5 = WC_BASE + 3 (десятичный 15732726)
#define: WC_LIT_W6 0x00F00FF7 // номинал: W6 = WC_BASE + 4 (десятичный 15732727)
#define: WC_LIT_W7 0x00F00FF8 // номинал: W7 = WC_BASE + 5 (десятичный 15732728)
#define: WC_LIT_W8 0x00F00FF9 // номинал: W8 = WC_BASE + 6 (десятичный 15732729) — веха-15 (совпадает с TMP_CNT кольца 'ml' — граница совместного использования)
#define: WC_LIT_W9 0x00F00FFA // номинал: W9 = WC_BASE + 7 (десятичный 15732730) — веха-15 (совпадает с TMP_ACC кольца 'ml' — граница совместного использования)
#define: WC_LIT_WA 0x00F00FFB // номинал: WA = WC_BASE + 8 (десятичный 15732731) — веха-15 (совпадает с TMP_X кольца 'ml' — граница совместного использования)
#define: WC_LIT_WB 0x00F00FFC // номинал: WB = WC_BASE + 9 (десятичный 15732732) — веха-15
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
set static Mark_Pos       = 0x00000000; // честная метка цикла: эмиссионный адрес тела (веха-12а)
set static Ml_Mult        = 0x00000000; // честный множитель 'ml' (цифра 0..9) (веха-12б)
set static Ml_L0          = 0x00000000; // честный эмиссионный адрес тела кольца ml (веха-12б)
set static Emit_Val       = 0x00000000; // честный переносчик значения эмиссии (веха-12б)
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
set static W_Pending       = 0x00000000; // честный флаг: 'wc' ждёт литерал 0..9 (веха-15; было 0..5, TKT-052 веха-5)
set static W_Position      = 0x00000000; // честная позиция слова wc (для брака) (TKT-052 веха-5)
set static Sl_OK           = 0x00000000; // честный признак номинала слота для поглощённого wc (веха-10)
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
    Mark_Pos = 0;        // честная метка цикла пуста (веха-12а)
    Ml_Mult = 0;         // честный множитель ml пуст (веха-12б)
    Ml_L0 = 0;           // честный адрес тела кольца ml пуст (веха-12б)
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
    If_Site_1 = 0;      // честный слот JZ №1 пуст
    If_Site_2 = 0;       // честный слот JZ №2 пуст
    Jmp_Slot_2 = 0;      // честный слот JMP №2 пуст
    Else_Join_2 = 0;     // честное else-тело №2 пусто
    If_Count = 0;        // честный счёт if пуст
    Jmp_Count = 0;       // честный счёт else пуст
    Jmp_Slot_1 = 0;     // честный слот JMP №1 пуст
    Else_Join_1 = 0;    // честное else-тело №1 пусто
    JP_Site_Term = 0;     // честная позиция байта TERM пуста
    Node_Brace_Depth = 0;
    Node_Paren_Depth = 0;
    Node_Counter = 0;
    W_Current = WORK_CELL; // честный завод текущего слота (TKT-052 веха-5):
                           // стадия-0 честно НЕ пишет инициализаторы статиков
                           // в ячейки памяти — default = WORK_CELL
    W_Pending = 0;         // честный pending выбора слота пуст (веха-5)
    W_Position = 0;        // честная позиция слова wc сброшена (веха-5)
    Sl_OK = 0;             // честный признак номинала слота сброшен (веха-10)

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
// веха-12б: честные микропомощники эмиссии (байт/слово), ровно та же
// семантика, что у инлайн-сайтов: FILE_U8 / FILE_PUT + честный счётчик.
function Emit_Op_Byte() {
    log_cell(STREAM_EMIT_CELL, Emit_Val);
    sys_call(FILE_U8);
    Emitted_Bytes = Emitted_Bytes + 1;
}

function Emit_Op_Word() {
    log_cell(STREAM_EMIT_CELL, Emit_Val);
    sys_call(FILE_PUT);
    Emitted_Bytes = Emitted_Bytes + 4;
}

// веха-12б: честное умножение acc = acc * Ml_Mult через runtime-кольцо.
// Эмиссия 92 Б: setup 25 + тело 22 + body_add 39 + EXIT 6.
// Все цели прыжков статичны (известны в момент эмиссии):
//   L0 = база + 25 (эмиссионный адрес тела)
//   body_add = L0 + 22; EXIT = L0 + 61; файл = цель + 20 (заголовок v1.1)
// Ячейки: TMP_X 0x00F00FFB, TMP_CNT 0x00F00FF9, TMP_ACC 0x00F00FFA.
function Emit_Ml_Ring() {
    Ml_L0 = Emitted_Bytes + 25;
    // setup: TMP_X <- acc (множимое)
    Emit_Val = OP_STORE_AT_CODE;
    run Emit_Op_Byte();
    Emit_Val = TMP_X;
    run Emit_Op_Word();
    // setup: TMP_CNT <- Ml_Mult (множитель)
    Emit_Val = OP_CONST_CODE;
    run Emit_Op_Byte();
    Emit_Val = Ml_Mult;
    run Emit_Op_Word();
    Emit_Val = OP_STORE_AT_CODE;
    run Emit_Op_Byte();
    Emit_Val = TMP_CNT;
    run Emit_Op_Word();
    // setup: TMP_ACC <- 0 (накопитель)
    Emit_Val = OP_CONST_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0;
    run Emit_Op_Word();
    Emit_Val = OP_STORE_AT_CODE;
    run Emit_Op_Byte();
    Emit_Val = TMP_ACC;
    run Emit_Op_Word();
    // тело: acc = TMP_CNT; acc = (acc == 0)
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000019;
    run Emit_Op_Byte();
    Emit_Val = TMP_CNT;
    run Emit_Op_Word();
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000016;
    run Emit_Op_Byte();
    Emit_Val = 0;
    run Emit_Op_Word();
    // JZ -> body_add (счётчик != 0: acc == 0)
    Emit_Val = OP_JZ_CODE;
    run Emit_Op_Byte();
    Emit_Val = Ml_L0 + 42;
    run Emit_Op_Word();
    // JMP -> EXIT (счётчик == 0: acc == 1)
    Emit_Val = OP_JMP_CODE;
    run Emit_Op_Byte();
    Emit_Val = Ml_L0 + 81;
    run Emit_Op_Word();
    // body_add: acc = TMP_ACC; acc += TMP_X; TMP_ACC = acc
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000019;
    run Emit_Op_Byte();
    Emit_Val = TMP_ACC;
    run Emit_Op_Word();
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000015;
    run Emit_Op_Byte();
    Emit_Val = TMP_X;
    run Emit_Op_Word();
    Emit_Val = OP_STORE_AT_CODE;
    run Emit_Op_Byte();
    Emit_Val = TMP_ACC;
    run Emit_Op_Word();
    // body_add: acc = TMP_CNT; acc -= 1; TMP_CNT = acc
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000019;
    run Emit_Op_Byte();
    Emit_Val = TMP_CNT;
    run Emit_Op_Word();
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000017;
    run Emit_Op_Byte();
    Emit_Val = 1;
    run Emit_Op_Word();
    Emit_Val = OP_STORE_AT_CODE;
    run Emit_Op_Byte();
    Emit_Val = TMP_CNT;
    run Emit_Op_Word();
    // body_add: JMP -> тело (обратный прыжок, цель статична)
    Emit_Val = OP_JMP_CODE;
    run Emit_Op_Byte();
    Emit_Val = Ml_L0 + 20;
    run Emit_Op_Word();
    // EXIT: acc = TMP_ACC (произведение)
    Emit_Val = OP_LOAD_CODE;
    run Emit_Op_Byte();
    Emit_Val = 0x00000019;
    run Emit_Op_Byte();
    Emit_Val = TMP_ACC;
    run Emit_Op_Word();
    Ml_Mult = 0x00000000;
    Op_Pending = 0x00000000;
    Token_Counter = Token_Counter + 1;
    Found_Flag = 0x00000001;
}

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
            if (Op_Pending == 0x00000090) {
                Fail_Code = BRK_ML_NO_LIT;   // веха-12б: 'ml' без множителя
            } else {
                Fail_Code = BRK_EQ_NO_LIT;
            }
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
Mark_Pos = 0x00000000;
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

            // 'mk' (веха-12а): честная метка цикла — байта НЕ эмитит;
            // Mark_Pos = Emitted_Bytes (позиция СЛЕДУЮЩЕГО эмитнутого байта).
            if (Current_Char == KW_MK) {
                if (Num_Pending == 0x00000001) {
                    // веха-12а: 'mk' НЕ поглощает открытое nb-число —
                    // честный брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                Mark_Pos = Emitted_Bytes;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
                }
            }

            // 'jb' (веха-12а): честный обратный прыжок — OP_JMP 0x07 +
            // BE32(Mark_Pos + 20) = 5 Б; адрес честно файловый (как у
            // патчей if/fu: эмиссионный адрес + 20 заголовка артефакта).
            if (Current_Char == KW_JB) {
                if (Num_Pending == 0x00000001) {
                    // 'jb' НЕ поглощает открытое nb-число — честный 0x0C
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                if (Mark_Pos == 0x00000000) {
                    // честный брак: метки не было (fail-fast, 0x0E)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_JB_NO_MARK;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                out_cell(STREAM_EMIT_CELL, OP_JMP_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Tmp_Addr = Mark_Pos + 20;
                log_cell(STREAM_EMIT_CELL, Tmp_Addr);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
                }
                Mark_Pos = 0x00000000; // честная одноразовость метки
                }
            }
            // 'ml' (веха-12б): честное умножение acc на СЛЕДУЮЩУЮ цифру 0..9.
            // Слово байта НЕ эмитит: ставит честный pending-режим 0x90; цифра-
            // множитель разворачивает runtime-кольцо Emit_Ml_Ring (92 Б).
            if (Current_Char == KW_ML) {
                if (Num_Pending == 0x00000001) {
                    // 'ml' НЕ поглощает открытое nb-число — честный 0x0C
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                if (Op_Pending == 0x00000000) {
                    Op_Pending = 0x00000090; // честный режим множителя 'ml'
                    Op_Position = Word_Index;
                    Token_Counter = Token_Counter + 1;
                    Found_Flag = 0x00000001;
                } else {
                    // честный отказ: два оператора подряд (множителя нет)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EQ_NO_LIT;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                }
            }
            if (Current_Char == KW_SET) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
                }
            }

            // 'st' -> static -> OP_ALLOC_ST (0x10)
            if (Current_Char == KW_STATIC) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                out_cell(STREAM_EMIT_CELL, OP_ALLOC_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
                }
            }

            // 'fu' -> function/pub entry -> OP_CALL (0x03) + честный слот:
            // операнд BE32 запоминается у Call_Site_1 (позиция = после байта
            // опкода), честный плейсхолдер 00000000 — патч в вердиктной фазе
            // 'fu' -> честная МЕТКА функции (TKT-051 веха-3): байт не эмитится,
            // позиция потока честно пишется в слот Fu_Pos_N (первый свободный
            // из 4, счётчик Fu_Count); 'ru N' честно прыгает на функцию N
            if (Current_Char == KW_FUNCTION) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            // 'ru' -> run -> OP_CALL (0x03) + плейсхолдер BE32 + первый свободный
            // слот из Call_Site_1..4; честные отказы: 'ru' до любой 'fu' —
            // BRK_NO_FUNC (0x05); все 4 слота заняты — BRK_PATCH_OVERFLOW (0x04)
            // 'ru' -> run (TKT-051 веха-3): честный вызов функции ПО НОМЕРУ.
            // Сам байта НЕ эмитит: ставит Run_Pending, следующий литерал честно
            // эмитит CALL + слот + номер функции (Call_Fn_i). 'ru' без номера —
            // честный брак BRK_NO_FUNC (хвост-проверка, ноль эмиссий).
            if (Current_Char == KW_RUN) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            // Слово байта НЕ эмитит: ставит W_Pending = 1, следующий
            // литерал d (0..9 — веха-15) честно переключает W_Current (сайт цифр).
            // 'wc' при активном ожидании — честный брак BRK_WC_NO_LIT.
            if (Current_Char == KW_WC) {
                if (Num_Pending == 0x00000001) {
                    // веха-10: 'wc' стал честным ПЯТЫМ поглотителем nb-числа
                    // (вехи-8 список непоглотителей 13 -> 12): форма 'nb X wc'
                    // выбирает слот АБСОЛЮТНО — W_Current = BE32(Num_Acc),
                    // НО только по честному номиналу рабочих слотов
                    // {WORK_CELL, W2..WB; веха-15}. Системные ячейки 0x00F00FF0
                    // (Stream_Emit) и 0x00F00FF2 (FILE_EOF) в номинал НЕ
                    // входят. '<=' на стадии-0 нет — номинал честно развёрнут
                    // в цепь равенств (11 ветвей; веха-15). Вне номинала — честный брак
                    // BRK_WC_RANGE (fail-fast ДО эмиссии: 'wc' байта не эмитит,
                    // позиция = текущее слово). Успешное поглощение честно
                    // сбрасывает и W_Pending — 'nb X wc' самодостаточная форма
                    // выбора слота (прежний цифровой pending честно накрыт).
                    if (Num_Acc == WC_LIT_WORK) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W2) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W3) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W4) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W5) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W6) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W7) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W8) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_W9) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_WA) {
                        Sl_OK = 0x00000001;
                    } else {
                    if (Num_Acc == WC_LIT_WB) {
                        Sl_OK = 0x00000001;
                    } else {
                        // честно: число вне номинала рабочих слотов (веха-15:
                        // номинал {WORK 0x00F00FF1, W2..WB = 0x00F00FF3..0x00F00FFC})
                        Sl_OK = 0x00000000;
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
                    }
                    if (Sl_OK == 0x00000001) {
                        W_Current = Num_Acc;
                        W_Pending = 0x00000000;
                        Num_Pending = 0x00000000;
                        Num_Acc = 0x00000000;
                        Token_Counter = Token_Counter + 1;
                        Found_Flag = 0x00000001;
                    } else {
                        if (Error_Flag == 0x00000000) {
                            Fail_Code = BRK_WC_RANGE;
                            Fail_Position = Word_Index;
                            Error_Flag = 0x00000001;
                            Word_Index = MAX_SOURCE_WORDS;
                        }
                    }
                } else {
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
                if (Num_Pending == 0x00000001) {
                    // веха-8: 'sv' честно ПОГЛОЩАЕТ открытое nb-число как
                    // адрес: cell[Num_Acc] = acc. Длина та же 5 Б — честно
                    // меняется только операнд BE32(W_Current) -> BE32(Num_Acc)
                    out_cell(STREAM_EMIT_CELL, OP_STORE_AT_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                out_cell(STREAM_EMIT_CELL, OP_STORE_AT_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'va' (TKT-050 веха-2): честная загрузка памяти — OP_LOAD 0x12
            // + режим 0x19 (acc = cell[arg]) + BE32(W_Current). 6 байт.
            if (Current_Char == KW_VALUE) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: 'va' честно ПОГЛОЩАЕТ открытое nb-число как
                    // адрес: acc = cell[Num_Acc]. Длина та же 6 Б.
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000019);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                out_cell(STREAM_EMIT_CELL, 0x00000019);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'gp' (TKT-052 веха-6): честная косвенная загрузка —
            // OP_INCELL_IND 0x52 + BE32(W_Current): acc =
            // cell[cell[текущий слот]]. Указатель честно живёт в
            // рабочем слоте: кладётся обычным 'sv' из acc. 5 байт.
            if (Current_Char == KW_GP) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: 'gp' честно ПОГЛОЩАЕТ открытое nb-число как
                    // адрес: acc = cell[cell[Num_Acc]]. Длина та же 5 Б.
                    out_cell(STREAM_EMIT_CELL, OP_INCELL_IND_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                out_cell(STREAM_EMIT_CELL, OP_INCELL_IND_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'sp' (TKT-052 веха-6): честная косвенная запись —
            // OP_STORE_IND 0x53 + BE32(W_Current):
            // cell[cell[текущий слот]] = acc. Адрес 0 честно бракует
            // сама VM (BRK_IND_ADDR_0) — эмит всегда честен. 5 байт.
            if (Current_Char == KW_SP) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: 'sp' честно ПОГЛОЩАЕТ открытое nb-число как
                    // адрес: cell[cell[Num_Acc]] = acc. Адрес 0 честно
                    // бракует сама VM (BRK_IND_ADDR_0). Длина та же 5 Б.
                    out_cell(STREAM_EMIT_CELL, OP_STORE_IND_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                out_cell(STREAM_EMIT_CELL, OP_STORE_IND_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                log_cell(STREAM_EMIT_CELL, W_Current);
                sys_call(FILE_PUT);
                Emitted_Bytes = Emitted_Bytes + 4;
                }
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

            // 'sc' (веха-12в, TKT-052): честный syscall-канал слово-языка —
            // OP_SYSCALL 0x13 + BE32(N) = 5 Б, где N — открытое nb-число
            // (NID syscall: FILE_* 0x130-0x137 и далее). Дефолта по образцу
            // 'sv' у syscall нет ЧЕСТНО: NID без открытого числа — fail-fast
            // брак (в отличие от sv, дефолт которого = текущий слот).
            if (Current_Char == KW_SC) {
                if (Num_Pending == 0x00000001) {
                    // веха-12в: 'sc' честно ШЕСТОЙ поглотитель nb-числа
                    // (вехи-8 список поглотителей sv/va/gp/sp/wc -> +sc):
                    // 'nb X sc' эмитит OP_SYSCALL 0x13 + BE32(X)
                    out_cell(STREAM_EMIT_CELL, OP_SYSCALL_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_SC_NO_NUM;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'em' (веха-12в, TKT-052): честная запись КОНСТАНТЫ в
            // произвольную ячейку по образцу out_cell стадии-0 —
            // OP_OUTCELL 0x51 + BE32(адрес) + BE32(значение) = 9 Б.
            // АЦК НЕ ТРОГАЕТСЯ (0x51 пишет значение мимо акумулятора —
            // честно по VM-контракту). Значение честно из открытого
            // nb-числа; по умолчанию адреса = STREAM_EMIT_CELL — syscall-
            // аргумент (0x00F00FF0), что открывает путь к эмиттеру-миниме
            // самосборки на слово-языке.
            if (Current_Char == KW_EM) {
                if (Num_Pending == 0x00000001) {
                    // веха-12в: 'em' честно СЕДЬМОЙ поглотитель nb-числа:
                    // 'nb X em' эмитит 0x51 + BE32(Stream_Emit) + BE32(X)
                    out_cell(STREAM_EMIT_CELL, OP_OUTCELL_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    // адрес-операнд = константа Stream_Emit — честный
                    // out_cell (стадия-0 D015/D016: константа -> out_cell,
                    // переменная -> log_cell); дальше значение из nb.
                    out_cell(STREAM_EMIT_CELL, STREAM_EMIT_CELL);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_EM_NO_NUM;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'wo' (веха-12г): честный word-эмиттер — пара 'em' + 'sc 0x131'
            // свернута в одно слово языка: OP_OUTCELL 0x51 +
            // BE32(STREAM_EMIT_CELL) + BE32(Num_Acc) [9 Б] + OP_SYSCALL
            // 0x13 + BE32(FILE_PUT 0x131) [5 Б] = 14 Б. Смысл во времени:
            // во время работы cell(Stream_Emit) = N, затем FILE_PUT
            // записывает это слово в артефакт как 4 байта BE. Контакт с
            // acc отсутствует (OP_OUTCELL честно не трогает acc).
            // Открытое nb-число поглощается честно (ВОСЬМОЙ поглотитель
            // nb в языке); 'wo' без открытого nb — fail-fast
            // BRK_WO_NO_NUM 0x12.
            if (Current_Char == KW_WO) {
                if (Num_Pending == 0x00000001) {
                    // пара 1-2: OP_OUTCELL 0x51 (байт) + адрес Stream (слово)
                    out_cell(STREAM_EMIT_CELL, OP_OUTCELL_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, STREAM_EMIT_CELL);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    // пара 3: значение N из открытого nb-числа (слово)
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    // пара 4-5: runtime-syscall FILE_PUT 0x131 в потоке
                    // (честно как у 'sc': байт-код 0x13 + слово NID)
                    out_cell(STREAM_EMIT_CELL, OP_SYSCALL_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, FILE_PUT);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_WO_NO_NUM;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'cp' (веха-13): честное сравнение С ЯЧЕЙКОЙ — режим VM 0x18
            // уже честен (stage-0 тесты), в слово-языке триггера не было:
            // `nb X cp` эмитит OP_LOAD 0x12 + режим 0x18 + BE32(Num_Acc)
            // [1+1+4 = 6 Б] → acc = (acc == cell[X]). Словарное сравнение
            // word-компилятора: word-code против ячейки с KW_* (многознач-
            // ный честный литерал живёт в ячейке через 'nb d..X ne' + 'sv').
            // ДЕВЯТЫЙ поглотитель nb; 'cp' без открытого nb — fail-fast
            // BRK_CP_NO_NUM 0x13.
            if (Current_Char == KW_CP) {
                if (Num_Pending == 0x00000001) {
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000018);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_CP_NO_NUM;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'aa' (веха-14v3): честное СЛОЖЕНИЕ СО ЗНАЧЕНИЕМ ЯЧЕЙКИ —
            // acc = acc + cell[X], где X — открытое nb-число. Байткод:
            // OP_LOAD 0x12 + режим 0x15 + BE32(X) = 6 Б. Честный режим
            // 0x15 уже есть в VM (acc += cell[arg], ctos_vm.py:395) —
            // новых опкодов честно НЕ требуется. ДЕСЯТЫЙ поглотитель
            // nb-числа (вехи-8..13 непоглотителей; по образцу 'va'/'gp'/
            // 'sp'); 'aa' без открытого nb — честный fail-fast
            // BRK_NB_NO_CONS 0x0C. Смысл: снятие честной границы v2
            // (слот целевого артефакта вычисляется честно из цифры).
            if (Current_Char == KW_AA) {
                if (Num_Pending == 0x00000001) {
                    // честный сложитель по образцу 'gp': OP_LOAD (байт) +
                    // режим 0x15 (байт) + адрес X из nb (слово)
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000015);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, Num_Acc);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    Num_Pending = 0x00000000;
                    Num_Acc = 0x00000000;
                } else {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'as' (веха-14v3): честное СЛОЖЕНИЕ СО СЛОТОМ + ЗАПИСЬ ОБРАТНО —
            // acc = acc + cell[W_Current]; cell[W_Current] = acc. Байткод:
            // OP_LOAD 0x12 + режим 0x15 (acc += cell[arg]) + BE32(W_Current)
            // [6 Б] + OP_STORE_AT 0x55 + BE32(W_Current) [5 Б] = 11 Б.
            // Честный режим 0x15 уже есть в VM (ctos_vm.py:395). Смысл:
            // слот-аккумулятор — база (F3-48) + ASCII-цифра = честный адрес
            // слота. НЕ поглотитель nb: открытый nb → fail-fast 0x0C.
            if (Current_Char == KW_AS) {
                if (Num_Pending == 0x00000001) {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    out_cell(STREAM_EMIT_CELL, OP_LOAD_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, 0x00000015);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, W_Current);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    out_cell(STREAM_EMIT_CELL, OP_STORE_AT_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    log_cell(STREAM_EMIT_CELL, W_Current);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                }
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
            }

            // 'vw' (веха-14v3): честный КОМПИЛ-ВРЕМЕННЫЙ примитив «АДРЕС
            // ТЕКУЩЕГО СЛОТА → 4 БАЙТА ПОТОКА» — без 14-байтного конверта
            // 'ow'. Тело ровно var_addr-часть 'ow': log_cell(STREAM_EMIT_CELL,
            // W_Current) + sys_call(FILE_PUT) → в артефакт честно ложатся
            // 4 байта ЧИСЛА-АДРЕСА (константа компилятора W_Current), а НЕ
            // runtime-значение ячейки. Факт пробы pos_vw1 (nb 5 ne wc 2 sv
            // wc 2 vw te): в потоке "00 F0 0F F5" — адрес F5, не 5. Runtime
            // -> FILE_PUT честно даёт только 'ow' (веха-14v2) — его и взял
            // слово-компилятор wc14v3 (в артефакте ему нужны runtime-байты
            // уже ВЫЧИСЛЕННОГО слота, а не константа). НЕ поглотитель nb:
            // открытый nb → fail-fast 0x0C.
            if (Current_Char == KW_VW) {
                if (Num_Pending == 0x00000001) {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    log_cell(STREAM_EMIT_CELL, W_Current);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                }
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

            // 'ow' (веха-14v2): честный канал «ЗНАЧЕНИЕ СЛОТА → ФАЙЛ» — то же
            // тело 0x54, что у 'pr', но порт-получатель = STREAM_EMIT_CELL
            // (0x00F00FF0, ячейка-аргумент syscall), затем runtime-syscall
            // FILE_PUT в потоке (0x13 + BE32 0x131) — ячейка-источник
            // FILE_PUT честно получает cell[W_Current]. Итог байткода:
            // 0x54 + BE32(0x00F00FF0) + BE32(W_Current) [9 Б] + 0x13 +
            // BE32(0x131) [5 Б] = 14 Б. Слово НЕ поглотитель nb: открытый
            // nb-числитель без потребителя — честный fail-fast
            // BRK_NB_NO_CONS 0x0C (веха-8 модель, форма как у структурных).
            if (Current_Char == KW_OW) {
                if (Num_Pending == 0x00000001) {
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                    // конверт: 0x54 (байт) + адрес Stream (слово)
                    out_cell(STREAM_EMIT_CELL, OP_OUTCELL_V_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, STREAM_EMIT_CELL);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    log_cell(STREAM_EMIT_CELL, W_Current);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                    // хвост: runtime-syscall FILE_PUT 0x131 в потоке
                    out_cell(STREAM_EMIT_CELL, OP_SYSCALL_CODE);
                    sys_call(FILE_U8);
                    Emitted_Bytes = Emitted_Bytes + 1;
                    out_cell(STREAM_EMIT_CELL, FILE_PUT);
                    sys_call(FILE_PUT);
                    Emitted_Bytes = Emitted_Bytes + 4;
                }
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
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            if (Current_Char == KW_GT) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            if (Current_Char == KW_LT) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            if (Current_Char == KW_ADD) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            if (Current_Char == KW_SUB) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            // 'if' -> if -> OP_JZ (0x06) + честный слот (тот же честный механизм)
            // 'if' -> OP_JZ (0x06) + честный слот If_Site_1; второй 'if' —
            // честный брак BRK_PATCH_OVERFLOW (fail-fast, правило первый-сбой)
            if (Current_Char == KW_IF) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            // 'es' -> else -> OP_JMP (0x07) + честный слот Jmp_Slot_1;
            // честное начало else-тела = позиция после операнда (туда прыгнет JZ)
            if (Current_Char == KW_ELSE) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
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
            }

            // 'te' -> terminate -> OP_TERM (0x05); честное запоминание позиции
            // байта TERM — честный target патча демо (адрес честного останова)
            if (Current_Char == KW_TERM) {
                if (Num_Pending == 0x00000001) {
                    // веха-8: открытое nb-число потребляется честно только
                    // 'sv'/'va'/'gp'/'sp' или закрывается 'ne' — честный
                    // брак fail-fast (позиция = текущее слово)
                    if (Error_Flag == 0x00000000) {
                        Fail_Code = BRK_NB_NO_CONS;
                        Fail_Position = Word_Index;
                        Error_Flag = 0x00000001;
                        Word_Index = MAX_SOURCE_WORDS;
                    }
                } else {
                out_cell(STREAM_EMIT_CELL, OP_TERM_CODE);
                sys_call(FILE_U8);
                Emitted_Bytes = Emitted_Bytes + 1;
                JP_Site_Term = Emitted_Bytes - 1;  // честная позиция самого байта
                Token_Counter = Token_Counter + 1;
                Found_Flag = 0x00000001;
                }
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
                    // по сигнатуре (значение = 0) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W2
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D1) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D1 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 1) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W3
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D2) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D2 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 2) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W4
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D3) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D3 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 3) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W5
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D4) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D4 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 4) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W6
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D5) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5): сайт D5 честно ЗНАЕТ свою цифру
                    // по сигнатуре (значение = 5) — она по построению в честном
                    // диапазоне 0..9 (веха-15), проверка не нужна: слот = WC_BASE + d = W7
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D6) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5 + веха-15): сайт D6 честно ЗНАЕТ
                    // свою цифру по сигнатуре (значение = 6): честный слот =
                    // WC_BASE + 6 = 0x00F00FF9 (W8) — веха-15 расширила честный
                    // номинал рабочих слотов до диапазона цифр 0..9; слово
                    // по-прежнему не эмитит байта
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D7) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5 + веха-15): сайт D7 честно ЗНАЕТ
                    // свою цифру по сигнатуре (значение = 7): честный слот =
                    // WC_BASE + 7 = 0x00F00FFA (W9) — веха-15 расширила честный
                    // номинал рабочих слотов до диапазона цифр 0..9; слово
                    // по-прежнему не эмитит байта
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D8) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5 + веха-15): сайт D8 честно ЗНАЕТ
                    // свою цифру по сигнатуре (значение = 8): честный слот =
                    // WC_BASE + 8 = 0x00F00FFB (WA) — веха-15 расширила честный
                    // номинал рабочих слотов до диапазона цифр 0..9; слово
                    // по-прежнему не эмитит байта
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
            }

            if (Current_Char == LIT_D9) {
                Lit_Value = Current_Char - 48;
                if (W_Pending == 0x00000001) {
                    // 'wc d' (TKT-052 веха-5 + веха-15): сайт D9 честно ЗНАЕТ
                    // свою цифру по сигнатуре (значение = 9): честный слот =
                    // WC_BASE + 9 = 0x00F00FFC (WB) — веха-15 расширила честный
                    // номинал рабочих слотов до диапазона цифр 0..9; слово
                    // по-прежнему не эмитит байта
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
                        if (Op_Pending == 0x00000090) {
                        // веха-12б: цифра-множитель 'ml' — честное кольцо
                        Ml_Mult = Lit_Value;
                        run Emit_Ml_Ring();
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
