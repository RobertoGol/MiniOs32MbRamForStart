# -*- coding: utf-8 -*-
# Сборщик вехи-14v7 (TKT-052): снятие границы хвоста после word4 (факт e1).
# Граница v6: 5-словная цель 'wc 0 pr te pr' - stage1 принимает (64 Б,
# Token 5), v6 давал 0xFF/55 Б - разрыв слоёв. v7 добавляет p5:
# «ровно 4 слова». Копи-луп loader'а кладёт терминатор '.' (0x2E = 46)
# последним словом потока (build_source_words); для 4-словной цели
# он падает на cell[0xA00010]:
#     p5 = (cell[0xA00010] == 46)       - 'cp' по ячейке-константе
#     total = valid+p2+p0+p4+p5 == 5    - затвор 'eq 5'
# Единственный сплайс в CHECK v6: eq 4 -> eq 5 + добавка p5; НОВЫХ ЯЧЕЕК
# НЕТ - PD/PG переиспользуются ПОСЛЕ их чтения суммой (потреблены):
#     total4 -> sv PG; 46 -> ne, sv PD.
# INIT/COPY/EMIT v6 не меняются байт-в-байт. Лимит 510 слов.

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 - слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 - слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 - слово2 ('pr')
WORD4      = 10485772        # 0x00A0000C - слово3 ('te')
SRC5       = 10485776        # 0x00A00010 - слово4 ИЛИ терминатор '.'
EOF_CELL   = 15732722        # 0x00F00FF2
EMIT_CELL  = 15732720        # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 - fail-маркер, честно 0
PA = 15732729                # wc 6 - p0
PB = 15732730                # wc 7 - 'pr' (29296)
PC = 15732731                # wc 8 - 'te' (25972)
PD = 15732732                # wc 9 - p2 (v7: потом константа 46)
PF = 15732733                # 0xF00FFD - bad-flag
PG = 15732734                # 0xF00FFE - p4 (v7: потом total4)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(0), 'ne', 'wc', '2', 'sv',
        nb(0), 'ne', 'wc', '3', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(0), 'ne', 'wc', '5', 'sv',
        nb(0), 'ne', 'wc', '6', 'sv',
        nb(29296), 'ne', 'wc', '7', 'sv',
        nb(25972), 'ne', 'wc', '8', 'sv',
        nb(0), 'ne', 'wc', '9', 'sv']

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

EMIT = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                                    # 0x43544F53 'CTOS'
        'nb 1 6 8 4 3 0 0 8', 'wo',                                        # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                                      # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                                    # 0xFFFFAAAA (magic2)
        'nb 0', 'wo',                                                      # CRC-заполнитель
        'nb 8 4', 'em', 'nb 3 0 8', 'sc',                                  # U8 0x54
        'nb 1 0 5 6 9 8 5 2 8 0', 'wo',                                    # порт (0x3F0050C0)
        nb(SRC_WORD2), 'va',
        'wc', '0', 'as',
        'wc', '0', 'ow',
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (TERM+verd)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',                 # Token = counter - 1
        'wc', '2', 'ow',
        'wc', '3', 'ow',
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# CHECK v7: конъюнкция p0 & p2 & p4 & valid & p5 через сумму == 5
# (полный перебор 32 комбинаций: сумма 5 неотрицательных флагов <= 5
# равна 5 только при всех пяти = 1).
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',                 # cell[PA] = p0
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word3 == 'pr')
         nb(PD), 'sv',                 # cell[PD] = p2
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = p4 = (word4 == 'te')
         nb(PG), 'sv',                 # cell[PG] = p4
         # d = ascii(word1) - 48 шестью 'su 8' (режим 0x17, одна цифра)
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         # bad = (d > 9) - mod-2^32 wrap покрывает оба края диапазона
         'gt', '9',
         nb(PF), 'sv',                 # cell[PF] = bad
         # valid = (bad == 0) - 'cp' по нулевой ячейке F5
         nb(PF), 'va', nb(F5), 'cp',
         # total4 = valid + p2 + p0 + p4
         nb(PD), 'aa', nb(PA), 'aa', nb(PG), 'aa',
         # Сплайс v7: total4 -> PG (p4 потреблена); PD = 46 (p2 потреблена)
         nb(PG), 'sv',
         nb(46), 'ne',                 # acc = 46 ('.')
         nb(PD), 'sv',                 # cell[PD] = 46 - константа
         # p5 = (cell[0xA00010] == 46) - «ровно 4 слова»
         nb(SRC5), 'va', nb(PD), 'cp',
         # total = p5 + total4; затвор == 5
         nb(PG), 'aa',
         'eq', '5',
         'if']

MAIN = CHECK + EMIT + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v7.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v7 tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
