# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc te' Shape-B (веха-21б, спринт 12, TKT-052).
# База = wc14v2pr_build.py (рецепт Shape-B, приёмка regr49 W-49).
# Честные факты (probe37): 2-словный 'wc te' = 0xFF/Token 2/FC=8@0/
# rep[3]=1 (консты B-семейства), окно = тe-T1 окно (1 Б = OP 05),
# md5 11c0d87c, артефакт 46 = 20+1+1+4+20; word2 = '.' (WORD3).
# Отказ семейства честный: 'wc te zz' = 0xFE (эталон из приёмки).
# Правки против v2pr: PB = 'te' (25972 = 0x6574); EMIT-окно
# 'te' T1 (одиночный OP). CHECK идентичен (p0 F4 & p1 PB & p2 PC
# == 3, честный F5-сброс). pos_wc14v2te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 ('te')
WORD3      = 10485768        # 0x00A00008 - слово2 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 - 'wc' (0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'te' (0x6574 = 25972)
PC = 15732731                # wc 8 - 46 (конст word2 = '.')
PD = 15732732                # wc 9 - p1
PF = 15732733                # 0xF00FFD - p2-скретч (без digit-цепочки)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(25972), 'ne', 'wc', '7', 'sv',          # v2te: 'te' (0x6574)
        nb(46), 'ne', 'wc', '8', 'sv',             # v2te: точка в word2
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_TE2 = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 5', 'em', 'nb 3 0 8', 'sc',                  # OP 0x05 (1 Б)
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = сч-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 1', 'wo',                                    # rep[3] = 1 (B-честно)
        'nb 8', 'wo',                                    # FC = 8@0 (B-честно)
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Shape-B: сумма p0 & p1 & p2 == 3; acc стартует с честного нуля
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(SRC_WORD2), 'va', nb(PB), 'cp',  # acc = p1 = (word1 == 'te')
         nb(PD), 'sv',
         nb(WORD3), 'va', nb(PC), 'cp',      # acc = p2 = (word2 == '.')
         nb(PF), 'sv',
         nb(F5), 'va',                 # acc = 0 (честный сброс)
         nb(PA), 'aa',                 # acc = p0
         nb(PD), 'aa',                 # acc = p0 + p1
         nb(PF), 'aa',                 # acc = p0 + p1 + p2
         'eq', '3',
         'if']

MAIN = CHECK + EMIT_TE2 + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v2te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v2te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
