# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te d3 wc d2 te d32'
# Shape-T4×T4-te (веха-23, спринт 48, W-68, TKT-052). База =
# wc14v3t43te-дизайн (кросс T4×T3-te, W-59) + honest карта probe58/64
# (свежий stage1 на каждую цель): stage1 для T4×T4-te целей = 57 Б
# 0xFF Token 8, emit = 05 15 BE32(d31) + 05 15 BE32(d32) (12 Б); база
# 'wc 5 te 3 wc 5 te 3' = 45188fc1 (probe64). **ВТОРОЙ СТЕЙТМЕНТ =
# ПОЛНЫЙ T4-EMIT** (05 15 BE32(d32) — тот же вид, что первый, честная
# карта probe64, 17 кейсов): d32 НЕСУЩИЙ во ВТОРОМ BE32 (d32=7 -> AE58
# ae58af4c, d32=9 -> 2328361c); d2 в emit НЕ входит ВООБЩЕ (ни в
# первый BE32 — там d31, ни во второй — там d32; valid(d2) digit-block
# несущий только для ЗАТВОРА — как у T4/первый стейтмент, где d1 тоже
# не входит); d1-ИНВАРИАНТНОСТЬ ('wc 7 te 3 wc 5 te 3' = база
# 45188fc1); явная точка на word8 = база (терминатор слоя = слово №8);
# Token = 8 (rep BE32 = 8, честный дамп хвоста probe64: FF + BE32(8) +
# 20 нулей = 25 Б — тот же хвост, что T4×T3, но Token = 8). Честные
# соседи-кроссы (том обязан молчать): T4×T3-te 7-ток 'wc 5 te 3 wc 5
# te' (stage1 ПРИНИМАЕТ = 52 Б 32448898, emit 05 15 BE32(3) + голый
# U8 0x05 — te-хвост T3 = 1 Б; word7 = 'te' НЕ цифра -> valid4 bad ->
# PA < 9 -> молчание); T4×T4-pr 'wc 5 te 3 wc 5 pr 3' (stage1
# принимает, том обязан молчать: word6 = 'pr' != 'te' -> PD < 2);
# T4×T4-sv 'wc 5 te 3 wc 5 sv 3' (то же); T4-том 5-ток 'wc 5 te 3'
# (51 Б 495e8056 — своя полка, этот том молчит: word4 = пусто ->
# p0-2 = 0 -> PA < 9); 9-ток 'wc 5 te 3 wc 5 te 3 3' (stage1
# ПРИНИМАЕТ = 62 Б 3d825fd7, Token = 9 — том обязан молчать: word8 =
# '3' != '.' -> ppunkt = 0); 12-ток 'wc 5 te 3 wc 5 te 3 wc 5 te 3'
# (stage1 принимает = 63 Б d52f8215 — том молчит: word8 = 'w');
# голая форма 'wc te 3' (46 Б bac85372, emit 05 — stage1 принимает,
# том обязан молчать: word1 = 'te' -> valid1 bad); сирота-цифра
# 'wc 5 te 3 wc 5' = 8b2c4a6f (stage1 принимает, том молчит: word6 =
# '.'); хвост-мусор, bad d1/d2/d31/d32, bad cells, bad word0/word4/
# word6 — том молчит.
# Честный дизайн (= T4×T3-те W-59 + digit-block d32 + T4-emit-2):
#   CHECK1 = канон T4 (A,B,C,D,B2 без F/G)          173 ток
#   CHECK2 = скан T4-стейтмента (слова 4..7):
#     p0-2 (word4 == 'wc', PA += )                  23 ток
#     valid(d2) digit-block (word5)                 57 ток
#     reslot: RESET cell[wc0] = F3_MINUS_48 (13) +
#             'wc 0 as' на word5 (13) — для te НЕ
#             НЕСУЩИЙ (d2 в emit не входит),
#             оставлен для единообразия             26 ток
#     pTe2 (word6 == LE2('te'), PD += )             23 ток
#     valid(d32) digit-block (word7)                57 ток
#     (LE2('te') = 0x6574? НЕТ: LE2('te') = 't' в
#     МЛАДШЕМ байте = 0x74 + 'e' 0x65 в старшем =
#     0x6574 = 25972 — та же конста, что statement1
#     'te' (PB = wc7); для te-тома ОВЕ kind-консты =
#     25972: wc3 = F6 = 25972 И wc7 = PB = 25972;
#     wc5 НЕ свободна: COPY читает 'wc 5' как
#     emit-указатель — честная находка probe57/W-61)
#   RELOAD1: d31 -> wc2 (= F5) ПОСЛЕ последнего F5-cp
#   G-затвор: PA (6) + PD (2) + ppunkt == 9 ('eq 9' —
#   одноразрядный immediate); терминатор на word8
#   (ячейка WORD9 = 10485792) — ключ-развязка: у
#   7-ток соседа (T4×T3-te) word7 = 'te' (bad-цифра
#   -> PA < 9), у 9-ток '…te 3 3' word8 = '3' !=
#   '.' -> ppunkt = 0; прецедент терминатора-слова
#   (EOF-слово пишется в SRC-ячейку как '.') —
#   W-59..W-67 (7-ток без точки = база, BYTE-OK).
#   EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из
#   RELOAD1) -> RELOAD2 (d32 -> wc2, 25 ток — wc2
#   переиспользуется честно, emit-указатель не
#   трогается) -> chain2 (05 15 BE32(d32), wc2 = d32)
#   -> вердец -> отчёт (Token = 8) -> SEAL/END.
#   Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t44te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te')
WORD4      = 10485772        # word3 (d31)
WORD5      = 10485776        # word4 ('wc' stmt-2)
WORD6      = 10485780        # word5 (d2)
WORD7      = 10485784        # word6 ('te' stmt-2)
WORD8      = 10485788        # word7 (d32)
WORD9      = 10485792        # word8 ('.' терминатор слоя T4×T4-te)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
WC0 = 15732723               # слот (для te НЕ читается хвостом)
F5 = 15732725
F6 = 15732726                # wc 3 - конст LE2('te') = 25972 (INIT)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('te') = 25972 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv',               # '.' (терминатор)
        nb(25972), 'ne', 'wc', '3', 'sv']            # 'te' (F6, LE2)

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = канон T4 (A,B,C,D,B2 без F/G — ppunkt и затвор общие)
CHECK1 = [nb(SRC_BUFFER), 'va',
          nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
          'wc', '6', 'sv',              # PA = p0
          # B1: честный digit-block (v2d, без правок): bad в PF
          nb(SRC_WORD2), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid1 = (bad == F5=0)
          'wc', '6', 'as',              # PA += valid1
          # C1: честный v3-слот chain1: cell[wc0] = F3 + d1
          # (для te d2 НЕ входит в emit — блок оставлен для
          # единообразия дизайна)
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: p2 = (word2 == LE2('te'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv',
          # B2: честный второй digit-block на word3 (d31)
          nb(WORD4), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid2 = (bad2 == 0)
          'wc', '6', 'as']              # PA += valid2

# CHECK2 = честный скан T4-стейтмента (слова 4..7; 4 токена —
# С digit-block d32: word8 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word4 == 'wc'), PA += (as-аккумулятор)
          nb(WORD5), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word5 (d2): bad3 в PF.
          # Для te d2 НЕ входит в emit (probe64: ни в первый BE32 —
          # там d31, ни во второй — там d32); несущий для ЗАТВОРА
          nb(WORD6), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: reslot chain2: RESET cell[wc0] = F3 минус 48, затем
          # 'wc 0 as' на word5 -> cell[wc0] = 15732723 + d2. Для te
          # НЕ НЕСУЩИЙ (emit = 05 15 BE32(d31) + 05 15 BE32(d32),
          # слота нет) — оставлен для единообразия
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD6), 'va',
          'wc', '0', 'as',
          # D2: pTe2 = (word6 == LE2('te')), PD += (конст F6 = wc 3 =
          # 25972 — та же конста, что PB statement1 'te'; для te-тома
          # ОВЕ kind-консты = 25972)
          nb(WORD7), 'va', nb(F6), 'cp',
          'wc', '9', 'as',
          # B4: честный digit-block на word7 (d32): bad4 в PF.
          # d32 НЕСУЩИЙ: второй BE32 emit (probe64: d32=7 -> ae58af4c,
          # d32=9 -> 2328361c)
          nb(WORD8), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as']              # PA += valid4

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (прецедент W-56/probe52): reload обязан стоять ПОСЛЕ последнего
# F5-cp (теперь B4) — иначе cell[F5] = d31 портит сравнение valid4
# (d31 != 0 -> цели молчат).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word8 == '.' — терминатор слоя T4×T4-te: ровно 8
# токенов; прецедент терминатора-слова: EOF-слово пишется в SRC-ячейку
# как '.' — 7-ток без точки = база, BYTE-OK W-59..W-67); затвор: PA (6)
# + PD (2) + ppunkt == 9 ('eq 9' — одноразрядный immediate); развязки:
# 7-ток сосед T4×T3-te: word7 = 'te' -> valid4 bad -> PA < 9; 9-ток
# '…te 3 3': word8 = '3' != '.' -> ppunkt = 0; 12-ток: word8 = 'w'.
TAIL_CHECK = [nb(WORD9), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '9',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) -> RELOAD2
# (d32 -> wc2 — wc2 переиспользуется честно, emit-указатель не
# трогается) -> chain2 (05 15 BE32(d32), wc2 = d32) -> вердец ->
# отчёт (Token = 8) -> SEAL/END.
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
CHAIN1 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d31)
# RELOAD2 = d32 -> wc2 (честное переиспользование wc2 ПОСЛЕ chain1;
# прецедент RELOAD1 после последнего F5-cp — здесь затвор уже прошёл,
# поток линейный, emit-указатель не трогается)
RELOAD2 = [nb(WORD8), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d32
# CHAIN2 = честный emit T4-statement2 'te' (probe64: второй стейтмент
# = ПОЛНЫЙ T4-emit 05 15 BE32(d32) — тот же вид, что chain1; d32
# НЕСУЩИЙ)
CHAIN2 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d32)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 8', 'wo',                                    # Token = 8 (слой
                                                         # T4×T4-te: 8
                                                         # токенов до
                                                         # терминатора)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + CHAIN1 \
       + RELOAD2 + CHAIN2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3t44te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t44te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
