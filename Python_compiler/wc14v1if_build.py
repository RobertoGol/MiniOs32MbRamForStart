# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'if' Shape-T1 (веха-21б, спринт 8, TKT-052).
# База = wc14v1sp_build.py (рецепт Shape-T1, приёмка regr45 W-45).
# Честные факты (probe37): 1-словный 'if' = 0xFF/Token 1/FC=0,
# окно 5 Б = U8 6 (0x06) + BE32 20 (0x00000014) — слот-канала
# нет, md5 70ebbc7c, артефакт 50 = 20+5+1+4+20.
# Отказ семейства честный: 'if zz' = 0xFE T1 FC=1@1 (честный
# neg-эталон берётся из приёмки).
# Правки против v1sp: PB = 'if' (26217 = 0x6669); EMIT-окно
# 'if' T1 (2 литерала). CHECK/хвост идентичны (честный F5-сброс).
# pos_wc14v1if.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('if')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377, не используется)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'if' (0x6669 = 26217)
PC = 15732731                # wc 8 - 46 (конст word1 = '.')
PD = 15732732                # wc 9 - p1
PF = 15732733                # 0xF00FFD - bad-flag (не используется)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(26217), 'ne', 'wc', '7', 'sv',          # v1if: 'if' (0x6669)
        nb(46), 'ne', 'wc', '8', 'sv',             # v1if: точка в word1
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_IF1 = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 6', 'em', 'nb 3 0 8', 'sc',                  # U8 6 = 0x06
        'nb 2 0', 'wo',                                  # BE32 0x00000014
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = сч-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Shape-T1: сумма p0 & p1 == 2; acc стартует с честного нуля
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(PB), 'cp',                 # acc = p0 = (word0 == 'if')
         nb(PA), 'sv',
         nb(SRC_WORD2), 'va', nb(PC), 'cp',  # acc = p1 = (word1 == '.')
         nb(PD), 'sv',
         nb(F5), 'va',                 # acc = 0 (честный сброс)
         nb(PA), 'aa',                 # acc = p0
         nb(PD), 'aa',                 # acc = p0 + p1
         'eq', '2',
         'if']

MAIN = CHECK + EMIT_IF1 + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v1if.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v1if tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
