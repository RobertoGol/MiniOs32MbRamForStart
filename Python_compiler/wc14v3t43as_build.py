# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te d3 wc d2 as'
# Shape-T4×T3-as (веха-23, спринт 46, W-66, TKT-052). База =
# wc14v3t43va_build.py (кросс-формный T4×T3-va 612 ток, W-64) + честная
# карта probe58/62 (свежий stage1 на каждую цель): stage1 для T4×T3-as
# целей = 62 Б 0xFF Token 7, emit = 05 15 BE32(d31) + 12 15 [слот] +
# 55 [слот] (16 Б); база 'wc 5 te 3 wc 5 as' = eb265d64 (probe58).
# **ОБА BE32 = ОДИН И ТОТ ЖЕ СЛОТ** (честная карта probe62, 17 кейсов):
# as-emit = U8 0x12 + U8 0x15 (LOAD 0x15, аудит вехи-12) +
# BE32(адрес-слота = cell[wc0]) + U8 0x55 (STORE_AT) + BE32(тот же
# слот) — честная семантика 'as' = cell[wcN] += acc (load, add, store
# back); младший байт ОБОИХ BE32 = 0xF3 + d2 (probe62: d2=0 -> F3
# 51a1f22b, d2=5 -> F8 база, d2=7 -> FA 0bba0bfb); reslot из CHECK2
# НЕСУЩИЙ; d1-ИНВАРИАНТНОСТЬ ('wc 7 te 3 wc 5 as' = база eb265d64);
# явная точка = база; Token = 7. Честные соседи-кроссы (том обязан
# молчать): T4×T4-as 8-ток 'wc 5 te 3 wc 5 as 3' (stage1 ПРИНИМАЕТ =
# 67 Б 2855788a, word7 = '3' -> ppunkt = 0); T4×T4-sv 8-ток =
# fe6aeb2b; reversed W-57 'wc 5 as 3 wc 5 te 3' (stage1 принимает =
# 67 Б b49d99cf, emit 12 15 [слот] 55 [слот] 15 BE32(3) 05 15
# BE32(3)); T4×T3-te (W-59) = 32448898; T4×T3-pr (W-60) = 26a8b48c;
# T4×T3-sv (W-61) = b904f09d; T4×T3-sp (W-62) = 122ce84e; T4×T3-vw
# (W-63) = b9a6ae3e; T4×T3-va (W-64) = 18824443; T4×T3-if (W-65) =
# c46313a6; новый вид probe58: T4×T3-ow = 36a16cbd; голые формы
# 'wc as' (56 Б 3078ad75, слот F1 = 15732721!) / 'wc 0 as' (56 Б
# 23942602, слот F3 — stage1 принимает, том обязан молчать по
# затвору); сирота-цифра 'wc 5 te 3 wc 5' = 8b2c4a6f (stage1
# принимает, том молчит: word6 = '.'); 9-ток '...as 3 wc 5 as' =
# 0bd73dac (принят, второй хвост тоже двойной BE32); мусор после
# слоя = FAIL 0xFE stage1 — том молчит.
# Честный дизайн (= W-64 + as-хвост):
#   CHECK1 = канон T4 (A,B,C,D,B2 без F/G)          203 ток
#   CHECK2 = скан T3-стейтмента (слова 4..6):
#     p0-2 (word4 == 'wc', PA += )                  23 ток
#     valid(d2) digit-block (word5)                 57 ток
#     reslot: RESET cell[wc0] = F3_MINUS_48 (13) +
#             'wc 0 as' на word5 (13) — НЕСУЩИЙ:
#             cell[wc0] = 15732723 + d2 = адрес-слот  26 ток
#             (оба BE32 хвоста читают cell[wc0])
#     pAs (word6 == LE2('as'), PD += )              23 ток
#     (LE2('as') = 0x7361 = 29537 — первый символ
#     в МЛАДШЕМ байте [урок W-65: LE2 = низкий
#     байт = первая буква; 'a' = 0x61 младший];
#     конст cell wc3 = F6 — та же ячейка, что
#     'pr'-конст W-60, 'sv'-конст W-61,
#     'sp'-конст W-62, 'vw'-конст W-63, 'va'-конст
#     W-64 и 'if'-конст W-65; wc5 НЕ свободна: COPY
#     читает 'wc 5' как emit-указатель — честная
#     находка probe57/W-61; T3 = 3 токена: НЕТ
#     второго digit-block — word7 = терминатор)
#   RELOAD1: d31 -> wc2 (= F5) ПОСЛЕ последнего F5-cp
#   G-затвор: PA (5) + PD (2) + ppunkt == 8 — ИДЕНТИЧЕН W-59..W-65
#   ('eq 8' одноразрядный); терминатор на word7 — ключ-развязка:
#   у 8-ток двойников (T4×T4-as/sv/pr) word7 = '3' -> молчание.
#   AS_TAIL (заменяет VA_TAIL W-64): U8 0x12 + U8 0x15 +
#   BE32(cell[wc0]) + U8 0x55 + BE32(cell[wc0]) — каждый U8 =
#   'nb X' 'em' 'nb 3 0 8' 'sc' (8 ток; уроки probe57/W-61/W-64:
#   nb-литералы ДЕСЯТИЧНЫЕ по цифрам — 'nb 1 8' = 18₁₀ = 0x12,
#   'nb 2 1' = 21₁₀ = 0x15, 'nb 8 5' = 85₁₀ = 0x55), каждый BE32 =
#   'wc 0 ow' (acc-based, перезагрузка cell[wc0] перед каждым
#   выводом). 30 ток (против 21 у va / 12 у sv/sp / 3 у vw).
#   Token = 7. Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t43as.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te')
WORD4      = 10485772        # word3 (d31)
WORD5      = 10485776        # word4 ('wc' stmt-2)
WORD6      = 10485780        # word5 (d2)
WORD7      = 10485784        # word6 ('as' stmt-2)
WORD8      = 10485788        # word7 ('.' терминатор слоя T4×T3-as)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
WC0 = 15732723               # адрес слота: cell[wc0] = F3 + d (reslot)
F5 = 15732725
F6 = 15732726                # wc 3 - конст LE2('as') = 29537 (INIT)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('te') = 25972 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (LE2)
        nb(46), 'ne', 'wc', '8', 'sv',               # '.' (терминатор)
        nb(29537), 'ne', 'wc', '3', 'sv']            # 'as' (LE2)

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

# CHECK2 = честный скан T3-стейтмента (слова 4..6; 3 токена —
# БЕЗ второго digit-block: word7 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word4 == 'wc'), PA += (as-аккумулятор)
          nb(WORD5), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word5 (d2): bad3 в PF
          nb(WORD6), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: честный reslot chain2: RESET cell[wc0] = F3 минус 48,
          # затем 'wc 0 as' на word5 -> cell[wc0] = 15732723 + d2 =
          # адрес-слот (БЕЗ RESET слот бы честно сложился с d1).
          # НЕСУЩИЙ: ОБА слот-байта AS_TAIL честно берутся из
          # cell[wc0] (двойной 'wc 0 ow' — перезагрузка перед каждым)
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD6), 'va',
          'wc', '0', 'as',
          # D2: pAs = (word6 == LE2('as')), PD += (конст F6 = wc 3 —
          # та же ячейка, что 'pr'/W-60, 'sv'/W-61, 'sp'/W-62,
          # 'vw'/W-63, 'va'/W-64 и 'if'/W-65)
          nb(WORD7), 'va', nb(F6), 'cp',
          'wc', '9', 'as']

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (прецедент W-56/probe52): reload обязан стоять ПОСЛЕ последнего
# F5-cp (теперь B3) — иначе cell[F5] = d31 портит сравнение valid3
# (d31 != 0 -> цели молчат).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word7 == '.' — терминатор слоя T4×T3-as: ровно 7
# токенов; ключ-развязка с T4×T4-as/sv/pr: word7 = '3' -> ppunkt = 0);
# затвор: PA (5) + PD (2) + ppunkt == 8 ('eq 8' — одноразрядный
# immediate, без cell-конст; дефект 'eq 13' W-58) — ИДЕНТИЧЕН W-59
TAIL_CHECK = [nb(WORD8), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '8',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) -> AS_TAIL
# (12 15 [слот] 55 [слот]) -> вердец -> отчёт -> SEAL/END.
# Слот Token отчёта = 7 (слой до терминатора).
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
CHAIN1 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d31)
# AS_TAIL = честный хвост T3-'as' (probe62: emit 12 15 [слот] 55
# [слот] — ОБА BE32 = один и тот же слот; аудит вехи-12: 'as' =
# cell[wcN] += acc = load + add + store back; прецедент 'wc 0 ow' =
# BE32(F3+d) W-57..W-65): U8 0x12 ('nb 1 8' = 18₁₀, урок W-64) + U8
# 0x15 ('nb 2 1' = 21₁₀, как CHAIN1) + BE32(cell[wc0]) ('wc 0 ow') +
# U8 0x55 ('nb 8 5' = 85₁₀, урок W-61) + BE32(cell[wc0]) ('wc 0 ow'
# повторно — перезагрузка acc). Reslot CHECK2 несущий (оба BE32).
AS_TAIL = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 0x12 (= 18 десятичных)
           'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 0x15 (= 21 десятичных)
           'wc', '0', 'ow',                    # BE32(адрес-слота) #1
           'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 0x55 (= 85 десятичных)
           'wc', '0', 'ow']                    # BE32(адрес-слота) #2
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 7', 'wo',                                    # Token = 7 (слой
                                                         # T4×T3-as: 7
                                                         # токенов до
                                                         # терминатора)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + CHAIN1 \
       + AS_TAIL + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3t43as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t43as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
