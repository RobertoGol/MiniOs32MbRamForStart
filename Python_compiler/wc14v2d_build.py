# -*- coding: utf-8 -*-
# Сборщик тома-словаря 'wc d' Shape-C (веха-21б, спринт 1, TKT-052).
# База = wc14v9te_build.py (рецепт Token-3, приёмки regr30..regr38).
# Честные факты (probe36/probe37/probe38/probe40):
#   stage1 принимает 2-словные 'wc d' = 0xFF/Token 2/FC=0, ПУСТОЕ
#   окно, md5 a154e85f НЕ зависит от d (d=0,1,5,9 подтверждены);
#   артефакт 45 = 20(hdr) + 0(окно) + 1(вердец FF) + 4(Token=2) + 20(хвост).
#   Отказы честные: 'wc 00'/'wc zz'/'wc 10' = 0xFE T1 FC=1@1 md5
#   29ba6852 (word1-цифра); 'wc 0 zz' = 0xFE T2 FC=1@2 md5 4ff7c705
#   (word2 обязан быть точкой — VM дописывает '.' как слово2 у
#   2-словного исходника).
# Правки против te-T3:
#   1) PB: 'te'(25972) -> 46: word2 у 2-словного исходника = '.',
#      p2 = (word2 == 46) через PB, слот WORD3 (0x00A00008);
#      PC-конст (word3-точка te-T3) не нужна, wc8 = 0 честно.
#   2) CHECK: только p0 & p2 & valid == 3, 'eq 3' (без p4).
#   3) EMIT: БЕЗ OP-блока и БЕЗ слот-канала; вердец U8 FF сразу
#      после CRC-заполнителя; Token-канал (счётчик-1 = 2), meta.
#   4) pos_wc14v2d.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc')
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 = '.' (VM дописал)
EOF_CELL  = 15732722         # 0x00F00FF2
EMIT_CELL = 15732720         # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 46 (конст word2 = '.')
PC = 15732731                # wc 8 - не используется, честно 0
PD = 15732732                # wc 9 - p2
PF = 15732733                # 0xF00FFD - bad-flag
PG = 15732734                # 0xF00FFE - p4 (не используется)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(46), 'ne', 'wc', '7', 'sv',             # v2d: точка-конста
        nb(0), 'ne', 'wc', '8', 'sv',              # v2d: PC не нужен
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT_C = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo',                                    # CRC-заполнитель
        'nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',  # Token = сч-1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK Shape-C: сумма p0 & p2 & valid == 3 (точка в word2)
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word2 == '.') - v2d
         nb(PD), 'sv',
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         'gt', '9',
         nb(PF), 'sv',
         nb(PF), 'va', nb(F5), 'cp',   # valid = (bad == 0)
         nb(PD), 'aa', nb(PA), 'aa',
         'eq', '3',
         'if']

MAIN = CHECK + EMIT_C + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v2d.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v2d tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
