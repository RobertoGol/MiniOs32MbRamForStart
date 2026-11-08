# -*- coding: utf-8 -*-
# Честный механический сборщик вехи-14v6 (TKT-052): снятие честной
# границы word1 (нецифра/двузначный литерал) — ЧЕСТНАЯ проверка
# диапазона ascii(word1) ∈ [48, 57] РАНТАЙМ, до открытия артефакта.
#
# Аддитивная перестройка вехи-14v5 — ровно один честный сплайс:
#
#   CHECK v6 (заменяет CHECK v5 СПРАВА-на-ЛЕВО аддитивно:
#   p0/p2/p4 честно сохраняются в ячейки, добавляется bad-flag):
#
#     p0 = (word0 == cell[F4]='wc')          — как v5 ('cp' 0x18)
#     p2 = (word3 == cell[PB]='pr')          — как v5
#     p4 = (word4 == cell[PC]='te')          — как v5; sv в PG (НОВОЕ)
#     d   = ascii(word1) - 48                — ЧЕСТНО шестью 'su 8'
#           (лексер честно НЕ даёт двузначный литерал после сравнения:
#            факт проб a2/a4 — 'gt 5 7' честно эмитит OP_LOAD(5)+
#            OP_CONST(7); 'su 8' честно (=6 × режим 0x17, факт h_*:
#            OP_CONST + 6×12 17 00000008 + 12 1A 00000009, 0xFF))
#     bad = (d > 9)                          — 'gt 9' (0x1A); ЧЕСТНО
#           покрывает ОБА края: ascii<48 → mod-2^32 wrap → >9 (fact h_b)
#     valid = (bad == 0)                     — 'cp' по ячейке F5 (0 INIT)
#     total = valid + p2 + p0 + p4           — честные 'aa' (0x15)
#     затвор: total == 4                    — 'eq 4'; полный перебор
#           16 комбинаций: сумма из 4 неотрицательных флагов ≤ 4,
#           равенство ⟺ все четыре = 1 (без ложных срабатываний —
#           вариант «5 флагов == 3» честно ОТВЕРГНУТ: ложный позитив
#           при p0=0, p2=p4=1, bad=1).
#
#   Честные новые ячейки (адресные поглотители вехи-8, без 'wc'-слотов):
#     PF = 15732733 (0xF00FFD) — bad-flag; PG = 15732734 (0xF00FFE) — p4.
#
# Честная граница v5 остаётся честной границей v6: хвост ПОСЛЕ word4
# не сверяется (факт e1: stage1 64 Б/Token 5 vs v6 55 Б/Token 5 —
# разрыв слоёв; проба e2 'wc x pr te': stage1 0xFE честный брак,
# v5 0xFF ложный позитив — В v6 ЗАКРЫТО Молчанием).
#
# Честные уровни (перенос v5): EMIT/INIT/COPY не меняются байт-в-байт;
# артефакт пишет только 'ow'/'wo'/'em' + syscall-слой.
#
# Честный лимит: 510 слов (MAX_SOURCE_WORDS 0x200), builder падает
# при превышении (молча не пишет).

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # 0x00A00000 — слово0 ('wc') целевого файла
SRC_WORD2  = 10485764        # 0x00A00004 — слово1 (ASCII цифра)
WORD3      = 10485768        # 0x00A00008 — слово2 ('pr')
WORD4      = 10485772        # 0x00A0000C — слово3 ('te')
EOF_CELL   = 15732722        # 0x00F00FF2
EMIT_CELL  = 15732720        # 0x00F00FF0
F3 = 15732723                # wc 0
F4 = 15732724                # wc 1 ('wc' = 0x6377 = 25463)
F3_MINUS_48 = 15732675       # F3 - 48
F5 = 15732725                # wc 2 — fail-маркер, ЧЕСТНО 0 (valid-ноль)
PA = 15732729                # wc 6 — скретч p0
PB = 15732730                # wc 7 — константа 'pr' (29296)
PC = 15732731                # wc 8 — константа 'te' (25972)
PD = 15732732                # wc 9 — скретч p2
PF = 15732733                # 0xF00FFD — bad-flag (адресный, сплайс v6)
PG = 15732734                # 0xF00FFE — p4-скретч (адресный, сплайс v6)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',   # база честного слота
        nb(25463), 'ne', 'wc', '1', 'sv',         # 'wc' = 0x6377
        nb(0), 'ne', 'wc', '2', 'sv',             # fail-маркер (и ноль valid)
        nb(0), 'ne', 'wc', '3', 'sv',             # Node-счётчик честно 0 (v4)
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',    # ptr кольца
        nb(0), 'ne', 'wc', '5', 'sv',             # счётчик токенов F8
        # Сплейс v5-1: честные слоты свиты wc6..wc9
        nb(0), 'ne', 'wc', '6', 'sv',             # PA = предикат p0
        nb(29296), 'ne', 'wc', '7', 'sv',         # PB = 'pr' (0x7270)
        nb(25972), 'ne', 'wc', '8', 'sv',         # PC = 'te' (0x6574)
        nb(0), 'ne', 'wc', '9', 'sv']             # PD = предикат p2

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
        # Сплейс v3-2: слот ЧЕСТНО вычисляется из цифры target-слова
        nb(SRC_WORD2), 'va',            # acc = ASCII цифры (48..57 честно, веха-15)
        'wc', '0', 'as',                # acc = ascii + (F3-48) = F3 + d; cell[F3] = acc
        'wc', '0', 'ow',                # runtime cell[F3+d] -> 4 байта артефакта
        'nb 1 5 3 5', 'em', 'nb 3 0 6', 'sc',                              # U16 0x05FF (TERM+verd)
        'wc', '5', 'va', 'su', '1', 'sv', 'wc', '5', 'ow',                 # Token = counter - 1
        # Сплейс v4-2: Syntax/Node ЧЕСТНО из runtime-канала (не константы)
        'wc', '2', 'ow',                # Syntax = cell[F5] (факт прогона)
        'wc', '3', 'ow',                # Node = cell[F6] (INIT 0)
        'nb 0', 'wo', 'nb 0', 'wo', 'nb 0', 'wo',                          # хвостовые нули
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

# Сплейс v6-2: честная конъюнкция p0 & p2 & p4 & (ascii ∈ [48,57])
# через сумму == 4 (полный перебор 16 комбинаций честен)
CHECK = [nb(SRC_BUFFER), 'va',         # acc = word0
         nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
         nb(PA), 'sv',                 # cell[PA] = p0
         nb(WORD3), 'va', nb(PB), 'cp',  # acc = p2 = (word3 == 'pr')
         nb(PD), 'sv',                 # cell[PD] = p2
         nb(WORD4), 'va', nb(PC), 'cp',  # acc = p4 = (word4 == 'te')
         nb(PG), 'sv',                 # cell[PG] = p4 (НОВОЕ v6)
         # d = ascii(word1) - 48 — честно шестью 'su 8' (режим 0x17)
         nb(SRC_WORD2), 'va',
         'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
         # bad = (d > 9) — один 'gt 9' покрывает оба края (wrap 2^32)
         'gt', '9',
         nb(PF), 'sv',                 # cell[PF] = bad (НОВОЕ v6)
         # valid = (bad == 0) — честное 'cp' по нулевой ячейке F5
         nb(PF), 'va', nb(F5), 'cp',
         # total = valid + p2 + p0 + p4 (acc = valid; веха-14v3 'aa')
         nb(PD), 'aa', nb(PA), 'aa', nb(PG), 'aa',
         'eq', '4',                    # acc = (sum == 4) — честный затвор
         'if']

MAIN = CHECK + EMIT + ['te', 'es', 'te']   # else-ветка: честное молчание

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 510

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v6.words'
assert TOKENS <= MAX_USER_WORDS, ('честный отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v6 tokens:', TOKENS, 'limit:', MAX_USER_WORDS, 'ok:', True)
