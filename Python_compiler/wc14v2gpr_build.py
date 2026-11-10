# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc d pr pr pr' Shape-G (веха-21б, спринт 14,
# TKT-052). База = wc14v2pr_build.py (Shape-B, regr49/W-49) + честный
# digit-check от wc14v2d_build.py (Shape-C, regr39/W-39: su 8 ×6, gt 9,
# bad-flag, valid = (bad == 0)).
# Честные факты (probeG 1/2, честные stage1-refs):
#   'wc 5 pr pr pr' = 0xFF/Token 5/FC=0@0/rep[3]=0, len 72, md5
#   1a2a0638, rep = [5,0,0,0,0,0]; 5 слов -> Token = 5 (та же честная
#   формула «Token = число слов исходника»). Артефакт 72 = 20 + 27
#   (окно 9 Б ×3) + 1 + 4 + 20.
#   Окно = pr-T1 окно (U8 84 + BE32 0x3F0050C0 + BE32 слот) ×3,
#   честный слот в КАЖДОМ повторе = BE32(F3 + d), где d = word1 - 48:
#   d=5 -> 0x00F00FF8, d=0 -> 0x00F00FF3. Подтверждено честно и на
#   других лексемах: 'wc 5 te te te' (te-окно OP 05 ×3, md5
#   5866cb8c), 'wc 7 ow ow ow' (ow-окно ×3, второй слот BE32
#   заменён на F3+d = 0x00F00FFA, md5 0241b483).
#   Honest cross-рифма: 'wc 0 pr pr pr' md5 f675745d и
#   'wc 5 te te te' md5 5866cb8c — пины из честного списка вехи-22.
# Слова честного исходника: word0 'wc' (A00000), word1 = цифра
# (A00004), word2..4 = 'pr' (A00008/A0000C/A00010), честная точка
# дописана VM как word5 (0x00A00014).
# CHECK честный: p0 = (word0 == 'wc', F4=25463) & valid = (word1 -
# 48 в 0..9; честный digit-block тома-C: 6 × su 8 + gt 9, bad в PF,
# valid = (bad == 0)) & p2 = (word2 == 'pr', PB = 29296) &
# p3 = (word3 == PB, слот PG = wc 11) & p4 = (word4 == PB, PHD =
# wc 12) & ppunct = (word5 == 46, PC) == 6 ('eq 6', затвор 'if').
# Честные экономии ток-бюджета (468 <= 510): 'cp' НЕ имеет
# select-режима ('wc 1 cp' честно бракуется, fail-артефакт
# 77e27834, fail на токене 110) — сравнение только nb-поглотителем;
# 'sv'/'as' честны в select-режиме ('wc N sv' = INIT/COPY-факт,
# 'wc N as' = v3-факт pos_as1: acc = acc + cell + writeback);
# valid+p3+p4 сливаются в PA через 'wc 6 as', p2 хранится в PD
# ('wc 9 sv'). EMIT честный: header-слова как у B; окно =
# [U8 84 + BE32 0x3F0050C0 + BE32(F3+d)] ×3 — динамичное
# слот-слово по v3-факту: 'nb(SRC_WORD2) va; wc 0 as' ->
# cell[wc0] = F3 + d (INIT хранит F3 - 48), эмит честным
# 'wc 0 ow' (3 токена, в каждом из трёх повторов); вердец U8 FF;
# Token = честная конста 5 ('nb 5 wo'); честный rep-хвост
# [5,0,0,0,0,0]: 'wc 2 ow' / 'wc 3 ow' + 'nb 0 wo' ×3.
# pos_wc14v2gpr.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('pr')
WORD4      = 10485772        # 0x00A0000C - слово3 ('pr')
WORD5      = 10485776        # 0x00A00010 - слово4 ('pr')
WORD6      = 10485780        # 0x00A00014 - слово5 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 - 'wc' (0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
ZERO_CELL = 15732726         # wc 3 - честный нуль
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'pr' (0x7270 = 29296)
PC = 15732731                # wc 8 - 46 (конст word5 = '.')
PD = 15732732                # wc 9 - p2
PF = 15732733                # 0xF00FFD (wc 10) - bad-flag (том-C честно)
PG = 15732734                # 0xF00FFE (wc 11) - p3
PHD = 15732735               # 0xF00FFF (wc 12) - p4

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',     # gpr: база слота (v3-факт)
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29296), 'ne', 'wc', '7', 'sv',          # gpr: 'pr' (0x7270), const PB
        nb(46), 'ne', 'wc', '8', 'sv']             # gpr: точка word5

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# честный слот: 'nb(SRC_WORD2) va; wc 0 as' — acc = ascii + cell[F3]
# (= F3 − 48) = F3 + d; ЯЧЕЙКА wc0 сама становится слотом — EMIT
# честно выводит её через 'wc 0 ow' (v3-факт веха-14v3). Отдельный
# DCELL не нужен — см. CHECK, C-фаза (as-трюк).

# CHECK Shape-G: сумма p0 & valid & p2 & p3 & p4 & ppunkt == 6
# (A: p0; B: честный digit-block тома-C + valid в PA; C: честный
# v3-слот 'wc 0 as'; D: p2..p4; E: ppunkt; F: aa-цепочка + 'eq 6')
CHECK = [nb(SRC_BUFFER), 'va',
         nb(F4), 'cp',                 # acc = p0 = (word0 == cell[F4]='wc')
         'wc', '6', 'sv',              # PA = p0 (sv-режим выбора: INIT-факт)
         # B: честный digit-block (v2d-паттерн, без правок): bad в PF
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # acc = valid = (bad == cell[F5]=0)
         'wc', '6', 'as',              # PA = p0 + valid (as-аккумулятор)
         # C: честный v3-слот: cell[wc0] = F3 + d (INIT: F3 минус 48)
         nb(SRC_WORD2), 'va',
         'wc', '0', 'as',
         # D: p2..p4 = (word2..4 == 'pr', const PB = wc 7)
         nb(WORD3), 'va', nb(PB), 'cp',
         'wc', '9', 'sv',
         nb(WORD4), 'va', nb(PB), 'cp',
         'wc', '6', 'as',              # PA += p3 (as-аккумулятор)
         nb(WORD5), 'va', nb(PB), 'cp',
         'wc', '6', 'as',              # PA += p4 (as-аккумулятор)
         # E: ppunkt = (word5 == '.', const PC = wc 8 = 46)
         nb(WORD6), 'va', nb(PC), 'cp',
         # F: сумма и честный затвор
         nb(PA), 'aa',                 # + p0 + valid
         nb(PD), 'aa',                 # + p2 (p3/p4 уже в PA)
         'eq', '6',
         'if']

# окно: [U8 84 + BE32 0x3F0050C0 + BE32(F3+d)] ×3
GWIN = ['nb', '8', '4', 'em', 'nb', '3', '0', '8', 'sc',   # U8 84
        'nb', '1', '0', '5', '6', '9', '8', '5', '2', '8', '0', 'wo',
        'wc', '0', 'ow']                                   # BE32(F3+d)

EMIT_G = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        ] + GWIN + GWIN + GWIN + [
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 5', 'wo',                                    # Token = 5 (чек)
        'wc', '2', 'ow',                                 # wr2 = сч (0)
        'wc', '3', 'ow',                                 # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK + EMIT_G + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v2gpr.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v2gpr tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
