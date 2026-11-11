# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te d3 wc d2 te'
# Shape-T4×T3 (веха-23, спринт 39, W-59, TKT-052). База =
# wc14v3te2_build.py (двойной te-том 683 ток, W-56) + честная карта
# probe55 (свежий stage1 на каждую цель): stage1 для T4×T3-целей =
# 52 Б 0xFF Token 7, emit = 05 15 BE32(d31) + 05 (7 Б); база
# 'wc 5 te 3 wc 5 te' = 32448898; T3-'te' хвост = ТОЛЬКО TERM '05'
# (T3-одиночка 'wc 0 te' = 46 Б emit '05', bac85372, d-инвариант);
# d1- и d2-ИНВАРИАНТНОСТЬ артефакта ('wc 7 te 3 wc 5 te' = 'wc 5 te
# 3 wc 0 te' = база — слоты не входят в emit); явная точка = база;
# МУСОР ПОСЛЕ точки честно игнорируется ('wc 5 te 3 wc 5 te . 3' =
# 32448898 — точка-терминатор останавливает скан); Token отчёта =
# токенов потока (loader, честно). Честные соседи-кроссы: T4×T4
# (8 ток) = 57 Б 45188fc1/ae58af4c — том T4×T3 МОЛЧИТ (word7 = '3');
# 'wc 5 te 3 wc 5 pr' = 26a8b48c и 'wc 5 te 3 wc 5 sv' = b904f09d —
# stage1 принимает, соседние тома-ячейки (не эта полка); 'wc 5 te 3
# wc te' = 6265b72a и 'wc 5 te 3 te' = 2da04646 (голые формы) — том
# молчит (не слой 'wc d te'); мусор/zz после T3 = FAIL 0xFE stage1 —
# том молчит; 9-ток 'wc 5 te 3 wc 5 te 3 3' = 3d825fd7 0xFF — том
# молчит (word7 = '3').
# Честный дизайн: CHECK1 = канон T4 (A,B,C,D,B2 без F/G):
#   p0 (word0 == 'wc', PA = )               23 ток
#   valid(d1) digit-block тома-C (word1)    57 ток
#   C1: слот chain1: cell[wc0] = F3 + d1 (add-only, INIT pristine)
#   p2 (word2 == LE2('te'), PD = )          23 ток
#   valid(d31) digit-block (word3)          57 ток
# CHECK2 = скан T3-стейтмента (слова 4..6):
#   p0-2 (word4 == 'wc', PA += )            23 ток
#   valid(d2) digit-block (word5)           57 ток
#   reslot: RESET cell[F3] = F3_MINUS_48 (13) + 'wc 0 as' на word5
#           (13) = честный side-effect слота chain2         26 ток
#   p2-2 (word6 == LE2('te'), PD += )       23 ток
#   (T3 = 3 токена: НЕТ второго digit-block — word7 = терминатор)
# RELOAD1: d31 -> wc2 (= F5) ПОСЛЕ последнего F5-cp (теперь B3,
# прецедент W-56/probe52). G-затвор: PA (= p0+v1+v2+p0-2+v3 = 5) +
# PD (= p2+p2-2 = 2) + ppunkt == 8. ppunkt = (word7 == '.') —
# терминатор на СЕДЬМОМ слове: слой = РОВНО 7 токенов + '.'; ключ-
# развязка с T4×T4: у 8-ток двойника word7 = '3' -> ppunkt = 0 ->
# молчание (EOF-слово потока честно читается как '.'). 'eq 8' —
# одноразрядный immediate (без cell-конст; дефект 'eq 13' W-58).
# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) + chain2
# (05 — ТОЛЬКО TERM, честный хвост T3-'te') -> вердец -> отчёт ->
# SEAL/END. Слот Token отчёта = 7: токенов слоя ДО терминатора
# (точка не считается — probe55: '... te .' и '... te . 3' = тот же
# Token 7; дефект-находка: te2-плейсхолдер 'nb 8' давал MISMATCH
# при честной длине слоя 7 — md5 различался ровно слотом Token).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t43.words

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
WORD8      = 10485788        # word7 ('.' терминатор слоя T4×T3)
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
          # затем 'wc 0 as' на word5 -> cell[wc0] = F3 + d2
          # (без RESET слот бы честно сложился с d1)
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD6), 'va',
          'wc', '0', 'as',
          # D2: p2-2 = (word6 == LE2('te')), PD +=
          nb(WORD7), 'va', nb(PB), 'cp',
          'wc', '9', 'as']

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (прецедент W-56/probe52): reload обязан стоять ПОСЛЕ последнего
# F5-cp (теперь B3) — иначе cell[F5] = d31 портит сравнение valid3
# (d31 != 0 -> цели молчат).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word7 == '.' — терминатор слоя T4×T3: ровно 7
# токенов; ключ-развязка с T4×T4: word7 = '3' -> ppunkt = 0);
# затвор: PA (5) + PD (2) + ppunkt == 8 ('eq 8' — одноразрядный
# immediate, без cell-конст; дефект 'eq 13' W-58)
TAIL_CHECK = [nb(WORD8), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '8',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) -> chain2
# (05 — ТОЛЬКО TERM: честный хвост T3-'te') -> вердец -> отчёт ->
# SEAL/END ('nb 8 wo' — плейсхолдер, loader пишет токенов потока)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
CHAIN1 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d31)
CHAIN2 = ['nb 5', 'em', 'nb 3 0 8', 'sc']     # U8 5 (TERM, хвост T3-te)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 7', 'wo',                                    # Token = 7 (слой
                                                         # T4×T3: 7 токенов
                                                         # до терминатора;
                                                         # точка не считается)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + CHAIN1 \
       + CHAIN2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3t43.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t43 tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
