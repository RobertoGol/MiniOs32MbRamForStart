# -*- coding: utf-8 -*-
# Генератор 7 томов Shape-B 'wc L' (веха-21б, спринт 13, TKT-052).
# База = ученная байт-дифом приёмка W-49/W-50 (regr49/regr50):
# рецепт Shape-B заморожен: INIT честный (F4 'wc' 25463, PB = LE2
# лексемы, PC = 46), CHECK = p0 & p1 & p2 == 3 ('eq 3') с честным
# F5-сбросом, EMIT = T1-окно лексемы + вердец U8 FF + Token =
# сч-1 + rep[3] = 1 ('nb 1 wo') + FC = 8@0 ('nb 8 wo') + pos 0
# (B-консты отчёта, CRC пересчитывается по ним).
# Честные scout-пины целей (probe37): as 3078ad75, va 2d164d6e,
# ow b4cc0b3b, sp 46f6a7dd, if c2877852, sv be7bdf42, vw acde33b3.
# Лексемы pr/te уже на полке (W-49/W-50); здесь — оставшиеся 7:
# as va ow sp if sv vw. pos-файлы в TMP.

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (лексема)
WORD3      = 10485768        # 0x00A00008 - слово2 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - LE2 лексемы
PC = 15732731                # wc 8 - 46 (конст word2 = '.')

# EMIT-окна = T1-окна лексем (probe37 / тома W-40..W-48, байт-честно):
# fpn: (эмит-токены после CRC-заполнителя, до вердеца)
WINDOWS = {
    'as': ["'nb 4 6 2 9', 'em', 'nb 3 0 6', 'sc',            # U16 4629",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1",
           "        'nb 8 5', 'em', 'nb 3 0 8', 'sc',            # U8 85",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1"],
    'va': ["'nb 4 6 3 3', 'em', 'nb 3 0 6', 'sc',            # U16 4633",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1"],
    'ow': ["'nb 8 4', 'em', 'nb 3 0 8', 'sc',                # U8 84",
           "        'nb 1 5 7 3 2 7 2 0', 'wo',                  # BE32 F0",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1",
           "        'nb 3 1 8 7 6 7 1 0 5', 'wo',                # 0x13000001",
           "        'nb 4 9', 'em', 'nb 3 0 8', 'sc',            # U8 49"],
    'sp': ["'nb 8 3', 'em', 'nb 3 0 8', 'sc',                # U8 83",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1"],
    'if': ["'nb 6', 'em', 'nb 3 0 8', 'sc',                  # U8 6",
           "        'nb 2 0', 'wo',                              # BE32 20"],
    'sv': ["'nb 8 5', 'em', 'nb 3 0 8', 'sc',                # U8 85",
           "        'nb 1 5 7 3 2 7 2 1', 'wo',                  # BE32 F1"],
    'vw': ["'nb 1 5 7 3 2 7 2 1', 'wo',                      # BE32 F1"],
}
LE2 = {'as': 29537, 'va': 24950, 'ow': 30575, 'sp': 28787,
       'if': 26217, 'sv': 30323, 'vw': 30582}
PINS = {'as': '3078ad75', 'va': '2d164d6e', 'ow': 'b4cc0b3b',
        'sp': '46f6a7dd', 'if': 'c2877852', 'sv': 'be7bdf42',
        'vw': 'acde33b3'}

TEMPLATE = """# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc %(lex)s' Shape-B (веха-21б, спринт 13,
# TKT-052). База = wc14v2pr_build.py / wc14v2te_build.py
# (рецепт Shape-B заморожен regr49/regr50: честный INIT, CHECK =
# p0('wc' F4) & p1(лексема PB) & p2('.' PC) == 3 с честным
# F5-сбросом; EMIT = %(lex)s-T1 окно + вердец FF + Token = сч-1 +
# rep[3] = 1 ('nb 1 wo') + FC = 8@0 ('nb 8 wo') + pos 0 — честные
# консты B-семейства, CRC пересчитывается по ним (regr49).
# Scout-пин цели %(lex)s (probe37): %(pin)s.
# pos_wc14v2%(lex)s.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = %(src_buffer)d
SRC_WORD2  = %(src_word2)d
WORD3      = %(word3)d
EOF_CELL  = %(eof_cell)d
EMIT_CELL = %(emit_cell)d
F3_MINUS_48 = %(f3m48)d
F5 = %(f5)d
PA = %(pa)d
PB = 15732730                # wc 7 - АДРЕС ячейки ('%(lex)s' = %(pb)d хранится в INIT)
PC = %(pc)d
PD = %(pd)d
PF = %(pf)d
F4 = %(f4)d

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(%(pb)d), 'ne', 'wc', '7', 'sv',          # 'v2%(lex)s'
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
        %(window)s
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
POS_PATH = r'%(pospath)s'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %%d > %%d'
                                  %% (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\\n')
print('%(posname)s tokens:', TOKENS)
"""

FIELDS = {
    'src_buffer': SRC_BUFFER, 'src_word2': SRC_WORD2, 'word3': WORD3,
    'eof_cell': EOF_CELL, 'emit_cell': EMIT_CELL, 'f3m48': F3_MINUS_48,
    'f5': F5, 'pa': PA, 'pc': PC, 'pd': 15732732, 'pf': 15732733,
    'f4': 15732724,
}

import io, os
TMP = r'G:\Windows\RJ\AppData\Local\Temp\opencode'
GEN = os.path.dirname(os.path.abspath(__file__))
GEN_LEXES = ['as', 'va', 'ow', 'sp', 'if', 'sv', 'vw']

for lex in GEN_LEXES:
    pb = LE2[lex]
    win = '\n'.join(WINDOWS[lex])
    fields = dict(FIELDS)
    fields.update(pb=pb, lex=lex, window=win,
                  pin=PINS[lex],
                  pospath=os.path.join(TMP, 'pos_wc14v2%s.words' % lex),
                  posname='pos_wc14v2%s' % lex)
    body = TEMPLATE % fields
    path = os.path.join(GEN, 'wc14v2%s_build.py' % lex)
    with io.open(path, 'w', encoding='utf-8') as f:
        f.write(body)
    print('wrote', path)
