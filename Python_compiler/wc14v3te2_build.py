# -*- coding: utf-8 -*-
# Сборщик ДВОЙНОГО честного тома 'wc d te d3 wc d2 te d32' Shape-T4×2
# (веха-23, спринт 36, W-56, TKT-052). База = wc14v3te_build.py
# (одиночный te-канон 452 ток, regr54/regr55) + честная карта probe52:
# stage1 для двойных целей = 57 Б 0xFF Token 8, emit = 05 15 BE32(d31)
# + 05 15 BE32(d32) (12 Б); d-ИНВАРИАНТНОСТЬ te-артефакта ('wc 7 te 3
# wc 5 te 3' md5 = 'wc 5 te 3 wc 5 te 3' 45188fc1 — слот-байт не входит
# в emit, d несёт только честный side-effect слота cell[F3] = F3+d);
# точка-слово честно игнорируется ('wc 5 te 3 .' = 0xFF Token 4
# 495e8056); 3-цепочки аддитивны (Token 12, 63 Б d52f8215).
# Честный дизайн (бюджет W-54, оценка +233 — superseded измеренной
# сборкой): CHECK2 по словам 4..7 второго стейтмента:
#   p0-2 (word4 == 'wc', PA += )            20 ток
#   valid(d2) digit-block тома-C (word5)    57 ток
#   reslot: RESET cell[F3] = F3_MINUS_48 ('nb.. ne wc 0 sv', 13 ток) +
#           повторный 'wc 0 as' на word5 (13 ток) = честный side-effect
#           слота chain2 без сложения с d1          26 ток
#   p2-2 (word6 == LE2('te'), PD += )       20 ток
#   valid(d32) digit-block (word7)          57 ток
#   reload d32 -> wc2 (E2) — в СЕКЦИИ ЭМИССИИ между BE32(d31) и
#   BE32(d32), т.к. 'wc 2 ow' честно читает ту же ячейку wc2  25 ток
#   chain2-em (05 15 BE32(d32))             20 ток
# G-затвор: PA (= p0 + v1 + v2 + p0-2 + v3 + v4 = 6) + PD (= p2 +
# p2-2 = 2) + ppunkt == 9. ppunkt = (word8 == '.') — терминатор-слово
# потока: слой = РОВНО 8 токенов + '.'. Кросс-молчания честны: single
# (word4='.') / 3-form (word8='wc') / хвост-мусор -> сумма != 9.
# Token = 8 (конст отчёта). Лимит честного тома вехи-23 = 1022 ток
# (поток = N ток + терминатор, брак при чтении №1024; regr55).
# pos_wc14v3te2.words

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
WORD9      = 10485792        # word8 ('.' терминатор)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725
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
        nb(46), 'ne', 'wc', '8', 'sv']               # '.' (терминатор)

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

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (probe52, первый прогон поймал дефект): reload обязан стоять ПОСЛЕ
# последнего F5-cp (B4) — иначе cell[F5] = d31 портит сравнения
# valid3/valid4 (d31 != 0 -> цели молчат); прецедент канона: 'wc 2 sv'
# ПОСЛЕ честных F5-cp («...НЕ нарушает valid/valid2»).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word8 == '.' — терминатор: ровно 8 токенов);
# затвор: PA (6) + PD (2) + ppunkt == 9
TAIL_CHECK = [nb(WORD9), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '9',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из E1) -> E2 reload d32 ->
# chain2 (05 15 BE32(d32)) -> вердец -> Token 8 -> отчёт -> SEAL/END
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
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 8', 'wo',                                    # Token = 8 (конст)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + CHAIN1 + E2 \
       + CHAIN2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3te2.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3te2 tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
