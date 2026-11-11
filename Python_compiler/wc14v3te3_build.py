# -*- coding: utf-8 -*-
# Сборщик ТРОЙНОГО честного тома 'wc d te d3 wc d2 te d32 wc d3 te d33'
# Shape-T4×3 (веха-23, спринт 38, W-58, TKT-052). База =
# wc14v3te2_build.py (двойной te-том 683 ток, W-56) + честная карта
# probe54: stage1 для тройных целей = 63 Б 0xFF Token 12, emit =
# 05 15 BE32(d31) + 05 15 BE32(d32) + 05 15 BE32(d33) (18 Б); база
# 'wc 5 te 3 wc 5 te 3 wc 5 te 3' = d52f8215 (пин W-56 «3-цепочки
# аддитивны» подтверждён); d1/d2-ИНВАРИАНТНОСТЬ te-артефакта
# ('wc 7 te 3 ...' = 'wc 5 te 3 ...' = d52f8215 — слот-байт не входит
# в emit, d несёт только честный side-effect слота cell[F3] = F3+d);
# trailing-dot честно игнорируется; 4-цепочка stage1 компилит
# (69 Б efb4c55c, Token 16) — тройной том обязан МОЛЧАТЬ (гейт 12).
# Честный дизайн: CHECK3 по словам 8..11 третьего стейтмента:
#   p0-3 (word8 == 'wc', PA += )            23 ток
#   valid(d3) digit-block тома-C (word9)    57 ток
#   reslot3: RESET cell[F3] = F3_MINUS_48 (13 ток) + повторный
#           'wc 0 as' на word9 (13 ток) = честный side-effect слота
#           chain3 без сложения с d1+d2             26 ток
#   p2-3 (word10 == LE2('te'), PD += )      23 ток
#   valid(d33) digit-block (word11)         57 ток
#   reload d33 -> wc2 (E3) — в СЕКЦИИ ЭМИССИИ между BE32(d32) и
#   BE32(d33), т.к. 'wc 2 ow' честно читает ту же ячейку wc2  25 ток
#   chain3-em (05 15 BE32(d33))             20 ток
# G-затвор: PA (= p0 + v1 + v2 + p0-2 + v3 + v4 + p0-3 + v5 + v6 = 9)
# + PD (= p2 + p2-2 + p2-3 = 3) + ppunkt == 13. ppunkt = (word12 ==
# '.') — терминатор-слово потока: слой = РОВНО 12 токенов + '.'.
# **Честный дефект, пойманный первым прогоном probe54:** 'eq' честно
# берёт ОДНО following-token immediate — 'eq 13' распарсился как
# 'eq 1' + осиротевший токен '3' (голая цифра вне nb = не-опкод ->
# fail 0xFE Token 708 = точный индекс сироты); исправлено по
# прецеденту W-57 (конст F6='pr' в wc 3): конст 13 честно живёт в
# cell F6 (wc 3, INIT 'nb 1 3 ne wc 3 sv'), сравнение — 'cp' против
# cell[F6] (тот же механизм, что ppunkt/PC и F6/'pr' W-57).
# Кросс-молчания честны: single (сумма 4) / double (9) / 4-цепочка
# (12) / 3-form ('pr' в слое) / хвост-мусор -> сумма != 13.
# Token = 12 (конст отчёта). Лимит честного тома вехи-23 = 1022 ток
# (поток = N ток + терминатор, брак при чтении №1024; regr55).
# pos_wc14v3te3.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te')
WORD4      = 10485772        # word3 (d31)
WORD5      = 10485776        # word4 ('wc' chain2)
WORD6      = 10485780        # word5 (d2)
WORD7      = 10485784        # word6 ('te' chain2)
WORD8      = 10485788        # word7 (d32)
WORD9      = 10485792        # word8 ('wc' chain3)
WORD10     = 10485796        # word9 (d3)
WORD11     = 10485800        # word10 ('te' chain3)
WORD12     = 10485804        # word11 (d33)
WORD13     = 10485808        # word12 ('.' терминатор)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725
F6 = 15732726                # wc 3 - конст затвора = 13 (INIT 'nb 1 3')
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
        nb(13), 'ne', 'wc', '3', 'sv']               # конст затвора = 13

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = канон (A,B,C,D,B2,E1 без F/G — ppunkt и затвор общие)
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

# CHECK2 = честный скан второго стейтмента (слова 4..7)
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
          # затем 'wc 0 as' на word5 -> cell[wc0] = F3 + d2
          # (без RESET слот бы честно сложился с d1)
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD6), 'va',
          'wc', '0', 'as',
          # D2: p2-2 = (word6 == LE2('te')), PD +=
          nb(WORD7), 'va', nb(PB), 'cp',
          'wc', '9', 'as',
          # B4: честный digit-block на word7 (d32): bad4 в PF
          nb(WORD8), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as']              # PA += valid4

# CHECK3 = честный скан третьего стейтмента (слова 8..11)
CHECK3 = [
          # A3: p0-3 = (word8 == 'wc'), PA +=
          nb(WORD9), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B5: честный digit-block на word9 (d3): bad5 в PF
          nb(WORD10), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid5 = (bad5 == 0)
          'wc', '6', 'as',              # PA += valid5
          # C3: честный reslot chain3: RESET cell[wc0] = F3 минус 48,
          # затем 'wc 0 as' на word9 -> cell[wc0] = F3 + d3
          # (без RESET слот бы честно сложился с d1+d2)
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD10), 'va',
          'wc', '0', 'as',
          # D3: p2-3 = (word10 == LE2('te')), PD +=
          nb(WORD11), 'va', nb(PB), 'cp',
          'wc', '9', 'as',
          # B6: честный digit-block на word11 (d33): bad6 в PF
          nb(WORD12), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid6 = (bad6 == 0)
          'wc', '6', 'as']              # PA += valid6

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (прецедент W-56/probe52): reload обязан стоять ПОСЛЕ последнего
# F5-cp (теперь B6) — иначе cell[F5] = d31 портит сравнения valid3/
# valid4/valid5/valid6 (d31 != 0 -> цели молчат).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word12 == '.' — терминатор: ровно 12 токенов);
# затвор: PA (9) + PD (3) + ppunkt == 13 (конст 13 в cell F6 —
# 'cp' против cell[F6]; дефект 'eq 13' -> сирота '3' — probe54)
TAIL_CHECK = [nb(WORD13), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(F6), 'cp',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) -> E2 reload
# d32 -> chain2 -> E3 reload d33 -> chain3 -> вердец -> Token 12 ->
# отчёт -> SEAL/END
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
CHAIN1 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d31)
E2 = [nb(WORD8), 'va',
      'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
      'wc', '2', 'sv']                        # reload d32 -> wc2
CHAIN2 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d32)
E3 = [nb(WORD12), 'va',
      'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
      'wc', '2', 'sv']                        # reload d33 -> wc2
CHAIN3 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d33)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 1 2', 'wo',                                  # Token = 12 (конст)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + CHECK3 + RELOAD1 + TAIL_CHECK + EMIT_HEAD \
       + CHAIN1 + E2 + CHAIN2 + E3 + CHAIN3 + EMIT_TAIL \
       + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3te3.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3te3 tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
