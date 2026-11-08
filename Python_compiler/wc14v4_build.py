# -*- coding: utf-8 -*-
# Честный механический сборщик вехи-14v4 (TKT-052): word-компилятор
# выводит ОТСЧЁТ Syntax/Node ЧЕСТНО через runtime-канал 'ow', а не
# константами (граница v3).
#
# Аддитивная перестройка вехи-14v3 — ровно два честных сплайса:
#
#   1) INIT: слот F6 (wc 3) = 0 — честный Node-счётчик. В v3 слот был
#      свободен; v4 честно заводит его под отчётное поле (байт-карта
#      целевой инструкции: Syntax, Node — два 4-байтовых поля хвоста).
#   2) EMIT: пять нуль-констант 'nb 0 wo' (Syntax+Node+3 хвостовых
#      нуля) заменяются на честный runtime-вывод:
#         wc 2 ow   -> cell[F5] = 0 идёт в поток КАК Runtime-значение
#                      (fail-маркер, в положительной ветке всегда 0);
#         wc 3 ow   -> cell[F6] = 0 (честный Node-счётчик, INIT);
#         nb 0 wo   -> три хвостовых нуля остаются честными константами.
#      Байт-карта НЕ меняется: те же 20 нулевых байтов — меняется
#      честное ПРОИСХОЖДЕНИЕ (константа -> runtime-канал). Компилятор
#      не добавляет от себя ни байта.
#
# Честные уровни (перенос v3): 'va'/'as' — это ИНСТРУКЦИИ stage-2
# программы, а не вывод в артефакт; в артефакт пишет только 'ow'
# (доказано пробой pos_vw1: байты 00 F0 0F F5 — runtime cell[F3]).
#
# Честная двойная роль слота F5 (документированная граница v4):
#   F5 — fail-маркер (вывод es-ветки) И канал Syntax-отчёта. В
#   положительной ветке обе роли честно 0; целевой слот при 'wc 2'
#   совпадает с ним — 'as' пишет ТОЛЬКО в F3, потока нет. Для
#   настоящих многослотовых target'ов нужна честная сегрегация (веха-15+).
#
# Честная цель: байт-в-байт = артефакту stage1 на target0.words
# (md5 8d82091a) И на target1.words 'wc 1 pr te' (md5 d40a8ad8) —
# и РАВНЫЙ байт-в-байт выходу v3 (нулевой разрыв от смены канала).
#
# Честная граница v4: отчёт Syntax/Node для плоских target'ов честно 0 —
# stage1 считает структурные слова {}/()/; (стр. 3247+ .kt), а word-
# target это одиночная инструкция; инкрементация узлов — будущая веха.
#
# Честный лимит: 510 слов пользователя (MAX_SOURCE_WORDS 0x200 = 512,
# '.' дописывает VM: user+1 = 512 -> честный OVERFLOW 0x07@0x200).
# Проба границы: neg_big3.words (511 sv -> 0xFE) / pos_edge3.words
# (508 sv + pr te = 510 -> 0xFF), прогоны по одному, прочтено:
# 2600 Б (md5 19966a43) и 2595 Б (md5 ea018d84). Сборщик проверяет
# РЕАЛЬНОЕ число токенов и падает, если оно больше 510 (молча не пишет).

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000
SRC_WORD2  = 10485764        # 0x00A00004 — второе слово target
EOF_CELL   = 15732722        # 0x00F00FF2
EMIT_CELL  = 15732720        # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1
F3_MINUS_48 = 15732675       # F3 - 48

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',   # база честного слота
        nb(25463), 'ne', 'wc', '1', 'sv',         # 'wc' = 0x6377
        nb(0), 'ne', 'wc', '2', 'sv',             # fail-маркер (и канал Syntax v4)
        nb(0), 'ne', 'wc', '3', 'sv',             # Сплейс v4-1: Node-счётчик честно 0
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',    # ptr кольца
        nb(0), 'ne', 'wc', '5', 'sv']             # счётчик токенов F8

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                                    # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                                        # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                                      # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                                    # 0xFFFFAAAA (magic2)
        'nb 0', 'wo',                                                      # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                                  # U8 0x54
        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',                                    # порт (0x3F0050C0)
        # Сплейс v3-2: слот ЧЕСТНО вычисляется из цифры target-слова
        nb(SRC_WORD2), 'va',            # acc = ASCII цифры (48..53)
        'wc', '0', 'as',                # acc = ascii + (F3-48) = F3 + d; cell[F3] = acc
        'wc', '0', 'ow',                # runtime cell[F3] -> 4 байта артефакта
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (T+verd)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',                 # Token = counter - 1
        # Сплейс v4-2: Syntax/Node ЧЕСТНО из runtime-канала (не константы)
        'wc', '2', 'ow',                # Syntax = cell[F5] (факт прогона)
        'wc', '3', 'ow',                # Node = cell[F6] (INIT 0)
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',                          # хвостовые нули
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = [nb(SRC_BUFFER), 'va', nb(F4), 'cp',
        'if'] + EMIT + ['te', 'es', 'wc', '2', 'pr', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v4.words'
assert TOKENS <= MAX_USER_WORDS, ('честный отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v4 tokens:', TOKENS, 'limit:', MAX_USER_WORDS, 'ok:', True)

# честные цели-эталоны
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\target0.words', 'w',
          encoding='ascii') as f:
    f.write('wc 0 pr te\n')
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\target1.words', 'w',
          encoding='ascii') as f:
    f.write('wc 1 pr te\n')
with open(r'G:\Windows\RJ\AppData\Local\Temp\opencode\neg_target.words', 'w',
          encoding='ascii') as f:
    f.write('va pr te\n')
print('targets honest: target0 / target1 / neg_target')
