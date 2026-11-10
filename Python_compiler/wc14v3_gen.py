# -*- coding: utf-8 -*-
# Генератор 9 томов Shape-T4 'wc d L d3' (веха-21б, спринт 15, TKT-052).
# База = wc14v2gpr_build.py (Shape-G, regr52/W-52, 468 ток честно) +
# честная карта probe43/probe44 (артефакты в Temp/_probe44_facts.py).
# Честные факты stage1 T4: 'wc d L d3' = 0xFF/Token 4/FC=0@0/rep
# [4,0,0,0,0,0]; окно = L-T1 окно, честные BE32-F1-слоты заменены на
# BE32(F3 + d) ('wc 0 ow', G-факт regr52), хвост = U8 21 + BE32(d3)
# ('wc 2 ow'); d-spread d0/d9/d5 сходится байт-в-байт (probe44).
# Окна честные (probe43/44, слоты -> 'wc 0 ow'):
#   te '05' | va U16 4633 + slot | sp '53' + slot | sv '55' + slot |
#   pr '54 3F 00 50 C0' + slot | as U16 4629 + slot + '55' + slot |
#   ow '54 00F00FF0' + slot + '13 00 00 01' + '31' | if '06' + BE32 20 |
#   vw slot (4 Б). Честные пины-цели: PINS ниже (md5 артефактов stage1).
# CHECK честный (G-рецепт): p0 (word0 == 'wc', F4=25463) &
#   valid(d, честный digit-block тома-C: 6 × su 8 + gt 9, bad в PF,
#   valid = (bad == F5=0)) & v3-слот (cell[wc0] = F3 + d, 'wc 0 as')
#   & p2 (word2 == LE2(L), PB = wc 7) & valid(d3, второй честный
#   digit-block на word3 0x00A0000C) & ppunkt (word4 0x00A00010 = '.') -
#   сумма == 5 ('eq 5', затвор 'if'). d3 в честную ячейку wc2 ('wc 2 sv')
#   ПОСЛЕ последнего F5-cp (F5 = wc 2 — fail-маркер, честно 0) и при
#   reload word3 на честных su ×6 — второй reload = G-факт честных
#   nb-погрузчиков; EMIT-Blok = B-консты + окно + хвост U8 21 + BE32(d3),
#   вердец FF, Token = честная конста 4 ('nb 4 wo') + 'nb 0 wo' ×5,
#   CRC-блок честный (nb 3 0 9 sc, nb 3 0 7 sc). Неги честно МОЛЧАТ
#   (затвор 'if' — regr39/regr49 фактор).
# pos-файлы в Temp (pos_wc14v3{L}.words).

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра d)
WORD3      = 10485768        # 0x00A00008 - слово2 = L
WORD4      = 10485772        # 0x00A0000C - слово3 (ASCII цифра d3)
WORD5      = 10485776        # 0x00A00010 - слово4 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0 (слот-база, INIT F3 - 48)
F4 = 15732724                # wc 1 - 'wc' (0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0; в T4 - ячейка d3
PA = 15732729                # wc 6 - p0 + valid1 + valid2
PB = 15732730                # wc 7 - LE2(L)
PC = 15732731                # wc 8 - 46 (конст word4 = '.')
PD = 15732732                # wc 9 - p2
PF = 15732733                # 0xF00FFD (wc 10) - bad-flag (том-C честно)

# EMIT-окна = T1-окна лексем с честными BE32-F1-слотами, заменёнными
# на динамичный слот BE32(F3+d) ('wc 0 ow', G-факт regr52):
WINDOWS = {
    'te': ["'nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'va': ["'nb 4 6 3 3', 'em', 'nb 3 0 6', 'sc',  # U16 4633",
           "        'wc', '0', 'ow',               # BE32(F3+d)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'sp': ["'nb 8 3', 'em', 'nb 3 0 8', 'sc',   # U8 83",
           "        'wc', '0', 'ow',             # BE32(F3+d)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'sv': ["'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 85",
           "        'wc', '0', 'ow',             # BE32(F3+d)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'pr': ["'nb 8 4', 'em', 'nb 3 0 8', 'sc',   # U8 84",
           "        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',   # 0x3F0050C0",
           "        'wc', '0', 'ow',             # BE32(F3+d)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'as': ["'nb 4 6 2 9', 'em', 'nb 3 0 6', 'sc',  # U16 4629",
           "        'wc', '0', 'ow',            # BE32(F3+d)",
           "        'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 85",
           "        'wc', '0', 'ow',            # BE32(F3+d)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'ow': ["'nb 8 4', 'em', 'nb 3 0 8', 'sc',   # U8 84",
           "        'nb 1 5 7 3 2 7 2 0', 'wo',     # BE32 0xF00FF0",
           "        'wc', '0', 'ow',            # BE32(F3+d)",
           "        'nb 3 1 8 7 6 7 1 0 5', 'wo',   # 0x13000001",
           "        'nb 4 9', 'em', 'nb 3 0 8', 'sc',   # U8 49",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'if': ["'nb 6', 'em', 'nb 3 0 8', 'sc',     # U8 6 (слота нет)",
           "        'nb 2 0', 'wo',             # BE32 20",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
    'vw': ["'wc', '0', 'ow',                    # BE32(F3+d) (слот один)",
           "        'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # T4-хвост U8 21",
           "        'wc', '2', 'ow',                      # BE32(d3)"],
}
LE2 = {'as': 29537, 'va': 24950, 'ow': 30575, 'sp': 28787,
       'if': 26217, 'sv': 30323, 'vw': 30582,
       'pr': 29296, 'te': 25972}

TEMPLATE = """# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc d %(lex)s d3' Shape-T4 (веха-21б, спринт
# 15, TKT-052). База = wc14v2gpr_build.py (Shape-G, regr52/W-52) +
# честная карта probe43/probe44: stage1 принимает 'wc d %(lex)s d3'
# = 0xFF/Token 4/FС=0@0/rep [4,0,0,0,0,0]; окно = %(lex)s-T1 окно с
# честными BE32-F1-слотами, заменёнными на BE32(F3 + d) ('wc 0 ow',
# G-факт regr52: 'wc 0 as' -> cell[wc0] = F3 + d, INIT F3 - 48), хвост
# = U8 21 + BE32(d3) ('wc 2 ow'; d3 хранится в ячейке wc2 по 'wc 2 sv'
# ПОСЛЕ честных F5-cp — wc2 = F5, fail-маркер, честно 0).
# Честный scout-пин цели %(lex)s (probe43/44): %(pin)s.
# pos_wc14v3%(lex)s.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = %(src_buffer)d
SRC_WORD2  = %(src_word2)d
WORD3      = %(word3)d
WORD4      = %(word4)d
WORD5      = %(word5)d
EOF_CELL  = %(eof_cell)d
EMIT_CELL = %(emit_cell)d
F3_MINUS_48 = %(f3m48)d
F5 = %(f5)d
PA = %(pa)d
PB = 15732730                # wc 7 - АДРЕС-конст LE2('%(lex)s') = %(pb)d (через INIT)
PC = %(pc)d
PD = %(pd)d
PF = 15732733                # 0xF00FFD (wc 10) - bad-flag (том-C честно)
F4 = %(f4)d

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(%(pb)d), 'ne', 'wc', '7', 'sv',           # '%(lex)s' (LE2)
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
         # D: честный p2 = (word2 == LE2('%(lex)s'), const PB = wc 7)
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

# окно: %(lex)s-T1 + честный T4-хвост: U8 21 + BE32(d3)
EMIT_WIN = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        %(window)s
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
POS_PATH = r'%(pospath)s'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %%d > %%d'
                                  %% (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\\n')
print('%(posname)s tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
"""

FIELDS = {
    'src_buffer': SRC_BUFFER, 'src_word2': SRC_WORD2, 'word3': WORD3,
    'word4': WORD4, 'word5': WORD5,
    'eof_cell': EOF_CELL, 'emit_cell': EMIT_CELL, 'f3m48': F3_MINUS_48,
    'f5': F5, 'pa': PA, 'pc': PC, 'pd': PD, 'f4': F4,
}

import io, os
TMP = r'G:\Windows\RJ\AppData\Local\Temp\opencode'
GEN = os.path.dirname(os.path.abspath(__file__))
GEN_LEXES = ['te', 'va', 'sp', 'sv', 'pr', 'as', 'ow', 'if', 'vw']

# честные scout-пины (probe43/probe44, md5 artifact'ов stage1)
PINS = {'te': '6a650f6e', 'va': 'ea21edd9', 'sp': 'd6e6b1d6',
        'sv': 'd0efc383', 'pr': '0bde2719', 'as': '36c2c8b9',
        'ow': '4372c123', 'if': '5f97427c', 'vw': '77e58387'}

for lex in GEN_LEXES:
    pb = LE2[lex]
    win = '\n'.join(WINDOWS[lex])
    fields = dict(FIELDS)
    fields.update(pb=pb, lex=lex, window=win,
                  pin=PINS[lex],
                  pospath=os.path.join(TMP, 'pos_wc14v3%s.words' % lex),
                  posname='pos_wc14v3%s' % lex)
    body = TEMPLATE % fields
    path = os.path.join(GEN, 'wc14v3%s_build.py' % lex)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(body)
    print('wrote', path)
