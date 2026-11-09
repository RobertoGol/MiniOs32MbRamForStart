# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'va' Token-3 (веха-21а хвост, спринт 13, TKT-052).
# База = wc14v9as_build.py (рецепт Token-3, приёмка regr31/regr32).
# Правки против as-T3:
#   1) PB: 'as'(29537) -> 'va'(24950 = 0x6176, 2-char LE)
#   2) EMIT -> EMIT_VA3: окно 'va' Token-3 из probe30 (5 Б):
#      U16 4633 (0x1219) + слот BE32(F3+d) + вердец U8 FF
#      (каркас probe33); окно 4-словного va = то же + 05 FF.
#   3) pos_wc14v9va.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('va')
WORD4      = 10485772        # 0x00A0000C - слово3 = '.' (терминатор)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'va' (0x6176 = 24950)
PC = 15732731                # wc 8 - 46 (конст word4 = '.')
PD = 15732732                # wc 9 - p2
PF = 15732733                # 0xF00FFD - bad-flag
PG = 15732734                # 0xF00FFE - p4

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(24950), 'ne', 'wc', '7', 'sv',          # v9va: 'va' (0x6176)
        nb(46), 'ne', 'wc', '8', 'sv',             # v9va: точка-конста
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_VA3 = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 4 6 3 3', 'em', 'nb 3 0 6', 'sc',            # U16 4633 = 0x1219
        nb(SRC_WORD2), 'va',                             # слот BE32(F3+d)
        'wc', '0', 'as',
        'wc', '0', 'ow',                                 # BE32(F3+d)
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = сч-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Token-3 (idем te/pr/as-T3): сумма p0 & p2 & p4 & valid == 4
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word2 == 'va') - v9va
         nb(PD), 'sv',
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = p4 = (word3 == '.') - v9va
         nb(PG), 'sv',
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # valid = (bad == 0)
         nb(PD), 'aa', nb(PA), 'aa', nb(PG), 'aa',
         'eq', '4',
         'if']

MAIN = CHECK + EMIT_VA3 + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v9va.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v9va tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
