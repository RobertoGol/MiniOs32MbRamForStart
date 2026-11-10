# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc d as d3' Shape-T4 (веха-21б, спринт
# 15, TKT-052). База = wc14v2gpr_build.py (Shape-G, regr52/W-52) +
# честная карта probe43/probe44: stage1 принимает 'wc d as d3'
# = 0xFF/Token 4/FС=0@0/rep [4,0,0,0,0,0]; окно = as-T1 окно с
# честными BE32-F1-слотами, заменёнными на BE32(F3 + d) ('wc 0 ow',
# G-факт regr52: 'wc 0 as' -> cell[wc0] = F3 + d, INIT F3 - 48), хвост
# = U8 21 + BE32(d3) ('wc 2 ow'; d3 хранится в ячейке wc2 по 'wc 2 sv'
# ПОСЛЕ честных F5-cp — wc2 = F5, fail-маркер, честно 0).
# Честный scout-пин цели as (probe43/44): 36c2c8b9.
# pos_wc14v3as.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764
WORD3      = 10485768
WORD4      = 10485772
WORD5      = 10485776
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725
PA = 15732729
PB = 15732730                # wc 7 - АДРЕС-конст LE2('as') = 29537 (через INIT)
PC = 15732731
PD = 15732732
PF = 15732733                # 0xF00FFD (wc 10) - bad-flag (том-C честно)
F4 = 15732724

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29537), 'ne', 'wc', '7', 'sv',           # 'as' (LE2)
        nb(46), 'ne', 'wc', '8', 'sv']               # точка word4

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK Shape-T4: сумма p0 & valid & p2 & valid2 & ppunkt == 5
# (A: p0; B: честный digit-block тома-C; C: честный v3-слот
# 'wc 0 as'; D: p2 + второй digit-block d3 (F5-cp ПОСЛЕДНИЙ);
# E: d3 в wc2 ('wc 2 sv') на честных reload su ×6; F: ppunkt;
# G: aa-цепочка + 'eq 5')
CHECK = [nb(SRC_BUFFER), 'va',
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         'wc', '6', 'sv',              # PA = p0
         # B: честный digit-block (v2d, без правок): bad в PF
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # acc = valid = (bad == F5=0)
         'wc', '6', 'as',              # PA += valid (as-аккумулятор)
         # C: честный v3-слот: cell[wc0] = F3 + d (INIT: F3 минус 48)
         nb(SRC_WORD2), 'va',
         'wc', '0', 'as',
         # D: честный p2 = (word2 == LE2('as'), const PB = wc 7)
         nb(WORD3), 'va', nb(PB), 'cp',
         'wc', '9', 'sv',
         # честный второй digit-block на word3 (d3, F5-cp последний)
         nb(WORD4), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # acc = valid2 = (bad2 == 0)
         'wc', '6', 'as',              # PA += valid2
         # E: d3 в ячейку wc2 (для честного хвоста BE32(d3)): су ×6
         # честным reload word3 = (F5-cp уже отработан, wc2 = F5 честно
         # теперь d3 - НЕ нарушает valid/valid2)
         nb(WORD4), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'wc', '2', 'sv',              # cell[wc2] = d3 (tail 'wc 2 ow')
         # F: ppunkt = (word4 == '.', const PC = wc 8 = 46)
         nb(WORD5), 'va', nb(PC), 'cp',
         # G: сумма и честный затвор
         nb(PA), 'aa',                 # + p0 + valid + valid2
         nb(PD), 'aa',                 # + p2
         'eq', '5',
         'if']

# окно: as-T1 + честный T4-хвост: U8 21 + BE32(d3)
EMIT_WIN = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 4 6 2 9', 'em', 'nb 3 0 6', 'sc',  # U16 4629
        'wc', '0', 'ow',            # BE32(F3+d)
        'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 85
        'wc', '0', 'ow',            # BE32(F3+d)
        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21
        'wc', '2', 'ow',                      # BE32(d3)
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 4', 'wo',                                    # Token = 4 (конст)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK + EMIT_WIN + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
