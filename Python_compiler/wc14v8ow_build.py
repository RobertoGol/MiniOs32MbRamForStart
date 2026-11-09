# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'ow' (полка вехи-21а, спринт 4, TKT-052).
# База = wc14v8va_build.py (рецепт v8as/v8va, приёмки regr22/regr23).
# Правки:
#   1) PB: 'va'(24950) -> 'ow'(30575 = 0x776F, 2-char LE)
#   2) EMIT -> EMIT_OW: окно 'ow' из probe28 (60 Б = 15 Б окно):
#      U8 84 (0x54) + BE32 15732720 (0x00F00FF0) + слот BE32(F3+d)
#      + BE32 318767105 (0x13000001) + U8 49 (0x31) + хвост U16 1535 (05 FF)
#   3) INIT-elision PA/PD-нулей: ячейки wc 6 (PA/p0) и wc 9 (PD/p2)
#      по потоку данных ЗАПИСЫВАЮТСЯ в CHECK до первого чтения
#      ('nb(PA) sv' перед 'nb(PA) aa'; 'nb(PD) sv' перед 'nb(PD) aa'
#      и перед сверкой SRC5) - elide доказуемо не меняет поведение,
#      целевые артефакты байт-в-байт (проверяет приёмка regr24).
#      Причина: окно 'ow' самое длинное (два const-слота + два U8),
#      без elide 517 ток > 510.
#   4) pos_wc14v8ow.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('ow')
WORD4      = 10485772        # 0x00A0000C - слово3 ('te')
SRC5       = 10485776        # 0x00A00010 - слово4 ИЛИ терминатор '.'
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0 (INIT-elide: пишет CHECK)
PB = 15732730                # wc 7 - 'ow' (0x776F = 30575)
PC = 15732731                # wc 8 - 'te' (25972)
PD = 15732732                # wc 9 - p2 (INIT-elide: пишет CHECK)
PF = 15732733                # 0xF00FFD - bad-flag
PG = 15732734                # 0xF00FFE - p4

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(30575), 'ne', 'wc', '7', 'sv',          # v8ow: 'ow' (0x776F)
        nb(25972), 'ne', 'wc', '8', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_OW = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                # U8 84 = 0x54
        'nb 1 5 7 3 2 7 2 0', 'wo',                      # BE32 0x00F00FF0
        nb(SRC_WORD2), 'va',                             # слот BE32(F3+d)
        'wc', '0', 'as',
        'wc', '0', 'ow',                                 # BE32(F3+d)
        'nb 3 1 8 7 6 7 1 0 5', 'wo',                    # BE32 0x13000001
        'nb 4 9', 'em', 'nb 3 0 8', 'sc',                # U8 49 = 0x31
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',            # хвост U16 1535 (05 FF)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = counter-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word3 == 'ow') - v8ow
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

MAIN = CHECK + EMIT_OW + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v8ow.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v8ow tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
