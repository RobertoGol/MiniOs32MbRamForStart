# -*- coding: utf-8 -*-
# Сборщик вехи-14v8as (TKT-052, спринт 2 вехи-21а): том-словарь 'as'.
# Решение пользователя: словарь разбит на тома (v7 = том 'pr', v8as = том 'as'),
# полка = серия честных двоичных компиляторов. БЕЗ правок stage1.
# База = wc14v7_build.py; правки:
#   1) PB-константа 'pr'(29296) -> 'as'(25561): CHECK p2 = (word3 == 'as')
#   2) EMIT_PR -> EMIT_AS: честный шаблон as-артефакта (57 Б):
#      U16 0x1215 + слот BE32(F3+d) + U8 0x55 + ow(BE32(F3+d) повтор) + _TAIL
#      (в _TAIL U16 0x05FF даёт финальные байты 05 FF; CRC-заполнитель nb 0 wo
#       - VM-seal честно патчит CRC, факт v7)
#   3) pos_wc14v8as.words
# Отказы (word0 != 'wc' etc) - как v7: затвор eq 5 -> else -> молчание.

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('as')
WORD4      = 10485772        # 0x00A0000C - слово3 ('te')
SRC5       = 10485776        # 0x00A00010 - слово4 ИЛИ терминатор '.'
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'as' (0x6173 = 25561)
PC = 15732731                # wc 8 - 'te' (25972)
PD = 15732732                # wc 9 - p2 (потом константа 46)
PF = 15732733                # 0xF00FFD - bad-flag
PG = 15732734                # 0xF00FFE - p4 (потом total4)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(29537), 'ne', 'wc', '7', 'sv',          # v8as: 'as' (0x7361) вместо 'pr'
        nb(25972), 'ne', 'wc', '8', 'sv',
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_AS = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 4 6 2 9', 'em', 'nb 3 0 6', 'sc',            # U16 4629 = 0x1215
        nb(SRC_WORD2), 'va',
        'wc', '0', 'as',
        'wc', '0', 'ow',                                 # BE32(F3+d) первый
        'nb 8 5', 'em', 'nb 3 0 8', 'sc',                # U8 85 = 0x55
        'ow',                                            # BE32(F3+d) повтор
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',            # U16 0x05FF (05 FF)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = counter-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK v7-структура (конъюнкция p0 & p2 & p4 & valid & p5 через сумму == 5)
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word3 == 'as') - v8as
         nb(PD), 'sv',
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = p4 = (word4 == 'te')
         nb(PG), 'sv',
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # valid = (bad == 0)
         nb(PD), 'aa', nb(PA), 'aa', nb(PG), 'aa',
         nb(PG), 'sv',
         nb(46), 'ne',
         nb(PD), 'sv',
         nb(SRC5), 'va', nb(PD), 'cp',  # p5 = (cell[0xA00010] == 46)
         nb(PG), 'aa',
         'eq', '5',
         'if']

MAIN = CHECK + EMIT_AS + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v8as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v8as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
