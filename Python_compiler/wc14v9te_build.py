# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'te' Token-3 (полка вехи-21а хвост, спринт 10, TKT-052).
# База = wc14v8te_build.py (приёмка regr27 W-27, том 4-словных 'wc d te te').
# Честный факт probe30: stage1 сам принимает 'wc d te' = Token 3
# (0xFF, FC=0, md5-серия константная bac85372 x10, артефакт 46 Б),
# окно 'te' Token-3 = 1 Б (OP 0x05) БЕЗ страддл-хвоста U16 1535.
# Правки против 4-словного 'te':
#   1) PC: 'te'(25972) -> 46 (конст word4='.' - точка-терминатор
#      лежит в слове word4 = 0x00A0000C, честно из потока brk-потока:
#      'wc d L' = 3 слова, VM допишет '.' на word4; SRC5 = 0x00A00010
#      уже ЗА терминатором - p5 проверки тома там больше нет)
#   2) CHECK: p4 = (word4 == 46) через PC; SRC5-ветка удалена
#      (по потоку данных честно: SRC5 не читается); сумма
#      p0 & p2 & p4 & valid == 4, 'eq 4' (вместо 'eq 5')
#   3) EMIT_TE3 = OP 0x05 (U8 5) БЕЗ страддл-хвоста (факт probe30)
#   4) СТРАДДЛ-ХВОСТ убран: окна Token-3 не имеют '05 FF'-хвоста
#   5) pos_wc14v9te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('te')
WORD4      = 10485772        # 0x00A0000C - слово3 = '.' (терминатор)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'te' (0x6574 = 25972)
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
        nb(25972), 'ne', 'wc', '7', 'sv',          # v9te: 'te' (0x6574)
        nb(46), 'ne', 'wc', '8', 'sv',             # v9te: точка-конста
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_TE3 = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 5', 'em', 'nb 3 0 8', 'sc',                  # OP 0x05 (окно 1 Б)
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF (probe33)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = counter-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Token-3: сумма p0 & p2 & p4 & valid == 4 (word4 = '.')
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word2 == 'te') - v9te
         nb(PD), 'sv',
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = p4 = (word3 == '.') - v9te
         nb(PG), 'sv',
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # valid = (bad == 0)
         nb(PD), 'aa', nb(PA), 'aa', nb(PG), 'aa',
         'eq', '4',                    # v9te: 4 проверки (без p5)
         'if']

MAIN = CHECK + EMIT_TE3 + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v9te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v9te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
