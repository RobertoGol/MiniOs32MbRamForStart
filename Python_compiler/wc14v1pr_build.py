# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'pr' Shape-T1 (веха-21б, спринт 3, TKT-052).
# База = wc14v1te_build.py (рецепт Shape-T1 + F5-сброс, regr40 W-40).
# Честные факты (probe37/probe42): stage1 принимает 1-словный 'pr'
# = 0xFF/Token 1/FC=0, окно 9 Б = U8 84 (0x54) + BE32 1056985280
# (0x3F0050C0) + BE32 15732721 (0x00F00FF1; слот-канала нет —
# хвост-слот честная конста F1), md5 80d530cd, артефакт
# 54 = 20 + 9 + 1(FF) + 4(Token=1) + 20.
# Отказ оного семейства честный: 'pr zz' = 0xFE T1 FC=1@1 (окно
# внутри neg-артефакта заполнено stage1, вердец 0xFE — том обязан
# молчать).
# Правки против v1te: PB = 'pr' (29296 = 0x7270); EMIT-окно
# pr-T1 (три литерала U8/BE32). CHECK и хвост идемичны (ловушка
# 'sv'-остатка: сумма стартует с честного нуля 'nb(F5) va').
# pos_wc14v1pr.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('pr')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377, не используется)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'pr' (0x7270 = 29296)
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
        nb(29296), 'ne', 'wc', '7', 'sv',          # v1pr: 'pr' (0x7270)
        nb(46), 'ne', 'wc', '8', 'sv',             # v1pr: точка в word1
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_PR1 = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                # U8 84 = 0x54
        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',                  # BE32 0x3F0050C0
        'nb 1 5 7 3 2 7 2 1', 'wo',                      # BE32 0x00F00FF1
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = сч-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Shape-T1: сумма p0 & p1 == 2; acc стартует с честного нуля
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(PB), 'cp',                 # acc = p0 = (word0 == 'pr')
         nb(PA), 'sv',
         nb(SRC_WORD2), 'va', nb(PC), 'cp',  # acc = p1 = (word1 == '.')
         nb(PD), 'sv',
         nb(F5), 'va',                 # acc = 0 (честный сброс)
         nb(PA), 'aa',                 # acc = p0
         nb(PD), 'aa',                 # acc = p0 + p1
         'eq', '2',
         'if']

MAIN = CHECK + EMIT_PR1 + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v1pr.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v1pr tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
