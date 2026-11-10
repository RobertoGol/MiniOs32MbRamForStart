# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc vw' Shape-B (веха-21б, спринт 13,
# TKT-052). База = wc14v2pr_build.py / wc14v2te_build.py
# (рецепт Shape-B заморожен regr49/regr50: честный INIT, CHECK =
# p0('wc' F4) & p1(лексема PB) & p2('.' PC) == 3 с честным
# F5-сбросом; EMIT = vw-T1 окно + вердец FF + Token = сч-1 +
# rep[3] = 1 ('nb 1 wo') + FC = 8@0 ('nb 8 wo') + pos 0 — честные
# консты B-семейства, CRC пересчитывается по ним (regr49).
# Scout-пин цели vw (probe37): acde33b3.
# pos_wc14v2vw.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764
WORD3      = 10485768
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725
PA = 15732729
PB = 15732730                # wc 7 - АДРЕС ячейки ('vw' = 30582 хранится в INIT)
PC = 15732731
PD = 15732732
PF = 15732733
F4 = 15732724

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(30582), 'ne', 'wc', '7', 'sv',          # 'v2vw'
        nb(46), 'ne', 'wc', '8', 'sv',             # точка в word2
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_WIN = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 1 5 7 3 2 7 2 1', 'wo',                      # BE32 F1
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 1', 'wo',                                    # rep[3] = 1
        'nb 8', 'wo',                                    # FC = 8@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',
         nb(PA), 'sv',
         nb(SRC_WORD2), 'va', nb(PB), 'cp',
         nb(PD), 'sv',
         nb(WORD3), 'va', nb(PC), 'cp',
         nb(PF), 'sv',
         nb(F5), 'va',                 # acc = 0 (честный сброс)
         nb(PA), 'aa',
         nb(PD), 'aa',
         nb(PF), 'aa',
         'eq', '3',
         'if']

MAIN = CHECK + EMIT_WIN + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v2vw.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v2vw tokens:', TOKENS)
