# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te wc d2 as d32'
# Shape-T3×T4-as (веха-23, спринт 64, W-84, TKT-052). База =
# wc14v3t34va-дизайн (кросс T3×T4-va, W-82) с as-хвостом второго
# стейтмента + honest карта probe84 (свежий stage1 на каждую цель, 49
# кейсов): stage1 для T3×T4-as целей = 62 Б 0xFF Token 7, emit = 05 +
# [12 15 + BE32(слот F3+d2) + 55 + BE32(слот F3+d2)] + 15 BE32(d32)
# (17 Б); база 'wc 5 te wc 5 as 3' = fe37197e (СОВПАЛ с пином
# probe77). ЕДИНЫЙ ЗАКОН ЭМИССИИ (карты probe77..probe84): каждый
# стейтмент эмитит [tail(kind)] + ([15 BE32(digit)] если есть digit-
# tail): T3×T4-as = 05 (T3-te хвост stmt1, БЕЗ chain1) + [as-хвост T4
# = U8 0x12 + U8 0x15 + BE32(слот) + U8 0x55 + BE32(слот) = 11 Б,
# закон W-75: 'as' = ADD 0x15 + LOAD 0x12: U8 0x12 (LOAD-адрес), U8
# 0x15, BE32(слот), U8 0x55 (STORE-конста), BE32(слот) — ДВА BE32,
# ОБА честно читают cell[wc0]; урок probe57/W-75: 'nb 8 5' = 85₁₀ =
# 0x55, 'nb 5 5' = 55₁₀ = 0x37 НЕВЕРНО; честный байт-счёт 11 Б — в
# комментарии regr75 стоит [10 Б], арифметическая описка (доказано:
# 62 Б базы = 20 + 05 + 11 + 5 + 25; 67 Б T4×T4-as = 20 + 6 + 11 +
# 5 + 25)] + 15 BE32(d32). T3-as-одиночка 'wc 5 as' = 56 Б 1176c0df,
# emit '12 15 BE32(слот F3+d1) 55 BE32(слот F3+d1)' (11 Б — хвост и в
# одиночке); T4-as-одиночка 'wc 5 as 3' = 61 Б cbb9ba26 (16 Б).
# **СЛОТ НЕСУЩИЙ В ОБОИХ BE32** (d2=0 → F3 e536d4d7, d2=5 → F8 база
# fe37197e, d2=7 → FA 58d99d43 — reslot CHECK2 НЕСУЩИЙ: ОБА BE32
# as-хвоста честно читают cell[wc0] = 15732723 + d2 = 0x00F00FF3 +
# d2; как у pr/sv/sp/vw/va, в отличие от te W-77 и if W-83); d32
# НЕСУЩИЙ (d32=7 → 65ad6127, d32=9 → ae65bd55, d32=0 → d449d0a4);
# d1-ИНВАРИАНТНОСТЬ ('wc 7 te wc 5 as 3' = база); явная точка на
# word7 = база; МУСОР ПОСЛЕ точки честно игнорируется ('... as 3 . 3'
# = fe37197e); Token = 7 (rep BE32 = 7, честный полный hex probe84:
# header CRC 5646e94b + emit 05121500f00ff85500f00ff81500000003 + FF
# + BE32(7) + 20 нулей). Честные соседи-кроссы (том обязан молчать,
# ВСЕ пины сняты честно — видовой хвост у каждого вида СВОЙ): T3×T4-te
# 'wc 5 te wc 5 te 3' = 52 Б df520cf9 (своя соседняя ячейка W-77 —
# stage1 ПРИНИМАЕТ, as-том молчит: word5 = 'te' != 'as' → PD < 2);
# T3×T4-соседи pr 60 Б 8f5455db / sv 56 Б c29827f9 / sp 56 Б
# 4cf32400 / vw 55 Б c8e17647 / va 57 Б a014b73e / if 56 Б 1d69a38a /
# ow 65 Б 3f013021 (probe77..probe83); T4×T4-as 8-ток 67 Б
# 2855788a (W-75) и T4×T3-as 7-ток 62 Б eb265d64 (СОВПАЛ с прецедентом
# W-66) — word3 = '3' → p0-2 bad → PA < 5; T4×T4-соседы te 45188fc1 /
# pr 3f3634ef / sv fe6aeb2b / sp 1d8ce3fa / vw cadd33b5 / va 4746dfb8
# / if af49bd85 / ow 1591c6b2 — свои полки W-68..W-76; T4-single 'wc 5
# te 3' 51 Б 495e8056 и T3-single 'wc 5 te' 46 Б bac85372 (word3
# пусто → p0-2 = 0); T3-as-single 'wc 5 as' 56 Б 1176c0df (НОВЫЙ
# пин) и T4-as-single 'wc 5 as 3' 61 Б cbb9ba26 (НОВЫЙ пин); T4-ow-
# single 'wc 5 ow 3' 64 Б fb10fa26; T3×T3 'wc 5 te wc 5 te' 47 Б
# c49e444f; 9-ток 'wc 5 te wc 5 as 3 3' = 67 Б 0f001bb0 (stage1
# ПРИНИМАЕТ, Token = 9, emit 05 + as-хвост + 15 BE32(3) + 15
# BE32(3)) — том молчит: word7 = '3' != '.' → ppunkt = 0; 11-ток
# 'wc 5 te wc 5 as 3 wc 5 as 3' = 78 Б 8a85e996 (ТРИ стейтмента T3 T4
# T4, emit 05 + [as-хвост + 15 BE32(3)] ×2) — том молчит: word7 =
# 'w'; сирота-цифра 'wc 5 te wc 5' = 46 Б a3bac192 (emit 05, stage1
# принимает — том молчит: word5 = '.'); голая 'wc as 3' = 56 Б
# 929d65cf (слот F1 = 15732721 = 0x00F00FF1!, emit '12 15 BE32(F1)
# 55 BE32(F1)' — stage1 принимает, том обязан молчать: word1 = 'as'
# → valid1 bad); 'wc 5 te 3 wc as' = 62 Б 79849069 (слот F8 от d1 —
# слот-канал; том молчит: word3 = '3' → p0-2 bad); bad d1/d2/d32,
# bad word0/word2/word3/word5, мусор/zz = FAIL 0xFE — том молчит
# (bad d32 as = 0xFE 57 Б f676ca3e, emit 05121500f00ff85500f00ff8).
# Честный дизайн (= T3×T4-va W-82 + as-хвост второго стейтмента):
#   CHECK1 = скан T3-стейтмента (слова 0..2):
#     p0 (word0 == 'wc', PA = )               23 ток
#     valid(d1) digit-block тома-C (word1)    57 ток
#     C1: слот chain1: cell[wc0] = F3 + d1    13 ток
#     pTe1 (word2 == LE2('te'), PD = )        23 ток
#     (T3 = 3 токена: НЕТ digit-block d31)
#   CHECK2 = скан T4-стейтмента (слова 3..6):
#     p0-2 (word3 == 'wc', PA += )            23 ток
#     valid(d2) digit-block (word4)           57 ток
#     reslot: RESET cell[wc0] = F3_MINUS_48   26 ток
#             (13) + 'wc 0 as' на word4 (13)
#             — НЕСУЩИЙ: ОБА BE32 as-хвоста
#             честно читают cell[wc0] =
#             15732723 + d2 (адрес-слот)
#     pAs2 (word5 == LE2('as'), PD += )       23 ток
#     valid(d32) digit-block (word7)          57 ток
#     (LE2('as') = 0x7361 = 29537 — 'a' =
#     0x61 в МЛАДШЕМ байте [урок W-65/W-67];
#     конст cell wc3 = F6 — та же ячейка, что
#     'te'-конст W-77 [25972] и kind-консты
#     W-60..W-83; PB остаётся 'te' = 25972 —
#     ПЕРВЫЙ стейтмент в T3×T4-полке всегда
#     'te'; wc5 НЕ свободна: COPY читает
#     'wc 5' как emit-указатель — честная
#     находка probe57/W-61)
#   RELOAD2: d32 (word6) -> wc2 (= F5) ПОСЛЕ
#   CHECK2 (все F5-cp уже прошли, затвор F5 не
#   читает — честно; в T3×T4 НЕТ RELOAD1)
#   G-затвор: PA 5 + PD 2 + ppunkt (word7=='.') == 8 ('eq 8'), терминатор
#   word7 (WORD8 = 10485788), Token = 7; НЕТ RELOAD1; RELOAD2 d32
#   (word6) → wc2 (F5) ПОСЛЕ CHECK2; CHECK1 = T3-скан (слова 0..2),
#   CHECK2 = T4-скан (слова 3..6) с НЕСУЩИМ reslot.
#   EMIT: TERM1 (05 — ТОЛЬКО TERM, честный хвост T3-'te' первого
#   стейтмента) -> RELOAD2 -> AS_TAIL2 (U8 0x12 + U8 0x15 +
#   BE32(slot F3+d2 НЕСУЩИЙ) + U8 0x55 + BE32(slot F3+d2 НЕСУЩИЙ)
#   + U8 0x15 + BE32(d32), 16 Б — закон W-75) -> вердец -> отчёт
#   (Token = 7) -> SEAL/END.
#   Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t34as.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('as' stmt-2)
WORD7      = 10485784        # word6 (d32)
WORD8      = 10485788        # word7 ('.' терминатор слоя T3×T4)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
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
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv',               # '.' (терминатор)
        nb(29537), 'ne', 'wc', '3', 'sv']            # 'as' (F6, LE2)

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = скан T3-стейтмента (слова 0..2; 3 токена — БЕЗ digit-
# block d31: word3 = 'wc' второго стейтмента)
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
          # (для as НЕ несущий через chain1 — несущий через reslot
          # CHECK2; оставлен для единообразия)
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pTe1 = (word2 == LE2('te'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']

# CHECK2 = скан T4-стейтмента (слова 3..6; 4 токена — С digit-block
# d32: word7 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (as-аккумулятор)
          nb(WORD4), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word4 (d2): bad3 в PF.
          # d2 НЕСУЩИЙ ЧЕРЕЗ СЛОТ: ОБА BE32 as-хвоста читают cell[wc0]
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: честный reslot chain2: RESET cell[wc0] = F3 минус 48,
          # затем 'wc 0 as' на word4 -> cell[wc0] = 15732723 + d2.
          # НЕСУЩИЙ (emit = 05 + 12 15 + BE32(cell[wc0]) + 55 +
          # BE32(cell[wc0]) + 15 BE32(d32); probe84: d2=0 → F3
          # e536d4d7, d2=7 → FA 58d99d43)
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD5), 'va',
          'wc', '0', 'as',
          # D2: pAs2 = (word5 == LE2('as')), PD += (конст F6 = wc 3 =
          # 0x7361 = 29537 — 'a' = 0x61 в МЛАДШЕМ байте [урок
          # W-65/W-67]; PB остаётся 'te' = 25972 — первый стейтмент
          # всегда 'te')
          nb(WORD6), 'va', nb(F6), 'cp',
          'wc', '9', 'as',
          # B4: честный digit-block на word6 (d32): bad4 в PF.
          # d32 НЕСУЩИЙ: BE32 хвоста (probe84: d32=7 → 65ad6127,
          # d32=9 → ae65bd55)
          nb(WORD7), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as']              # PA += valid4

# RELOAD2: d32 в ячейку wc2 (= F5) для BE32 хвоста. Честный порядок
# (прецедент W-59/W-68/W-77..W-83): reload стоит ПОСЛЕ CHECK2 — все
# F5-cp уже прошли (valid3/valid4 сравнились), затвор F5 не читает;
# в T3×T4 НЕТ RELOAD1 (d31 не существует — первый стейтмент в T3-форме)
RELOAD2 = [nb(WORD7), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d32

# F2/G2: ppunkt = (word7 == '.' — терминатор слоя T3×T4-as: ровно 7
# токенов; ключ-развязка с T4×T4: word3 = '3' -> p0-2 bad; с 9-ток:
# word7 = '3' -> ppunkt = 0); затвор: PA (5) + PD (2) + ppunkt == 8
# ('eq 8' — одноразрядный immediate, без cell-конст; дефект 'eq 13'
# W-58) — ИДЕНТИЧЕН W-59/W-77..W-83
TAIL_CHECK = [nb(WORD8), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '8',
              'if']

# EMIT: TERM1 (05 — ТОЛЬКО TERM: честный хвост T3-'te' первого
# стейтмента, карта probe77..probe84) -> RELOAD2 -> AS_TAIL2 (честный
# хвост второго стейтмента as в T4-форме (закон probe84/W-75): emit
# второго = as-хвост T4 + 15 BE32(d32) = U8 0x12 + U8 0x15 +
# BE32(слот) + U8 0x55 + BE32(слот) + U8 0x15 + BE32(d32), 16 Б):
# U8 0x12 ('nb 1 8' = 18₁₀ [урок probe57/W-64: nb-литералы
# ДЕСЯТИЧНЫЕ; урок W-75: 'nb 5 5' = 55₁₀ = 0x37 НЕВЕРНО]) + U8 0x15
# ('nb 2 1' = 21₁₀) + BE32(cell[wc0] = адрес-слота F3+d2 — НЕСУЩИЙ,
# reslot CHECK2, 'wc 0 ow' = 3 ток) + U8 0x55 ('nb 8 5' = 85₁₀ =
# 0x55 — ЛОВУШКА probe57: НЕ 'nb 5 5'!) + BE32(cell[wc0]) ('wc 0 ow'
# — ВТОРОЙ слотовый BE32, тоже НЕСУЩИЙ) + U8 0x15 ('nb 2 1') +
# BE32(d32) ('wc 2 ow' после RELOAD2)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
TERM1 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (TERM, хвост T3-te)
# AS_TAIL2 = честный хвост второго стейтмента as в T4-форме (закон
# probe84: emit второго = as-хвост T4 + 15 BE32(d32) = U8 0x12 + U8
# 0x15 + BE32(слот) + U8 0x55 + BE32(слот) + U8 0x15 + BE32(d32),
# 16 Б; ОБА слотовых BE32 читают cell[wc0] = F3 + d2 — НЕСУЩИЕ)
AS_TAIL2 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',       # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',       # U8 21 (0x15)
            'wc', '0', 'ow',                        # BE32(слот F3+d2)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',       # U8 85 (0x55)
            'wc', '0', 'ow',                        # BE32(слот F3+d2)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',       # U8 21 (0x15)
            'wc', '2', 'ow']                        # BE32(d32)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 7', 'wo',                                    # Token = 7 (слой
                                                          # T3×T4-as: 7
                                                          # токенов до
                                                          # терминатора;
                                                          # точка не
                                                          # считается)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD2 + TAIL_CHECK + EMIT_HEAD + TERM1 \
       + AS_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe84\pos_wc14v3t34as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t34as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
