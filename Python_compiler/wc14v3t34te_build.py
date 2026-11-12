# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te wc d2 te d32'
# Shape-T3×T4-te (веха-23, спринт 57, W-77, TKT-052). База =
# wc14v3t43-дизайн (кросс T4×T3-te, W-59: 7-ток слой, терминатор
# word7, 'eq 8') + T4-скан CHECK2/RELOAD2 из wc14v3t44te-дизайна
# (T4×T4-te, W-68) + honest карта probe77 (свежий stage1 на каждую
# цель, 39 кейсов): stage1 для T3×T4-te целей = 52 Б 0xFF Token 7,
# emit = 05 + 05 15 BE32(d32) (7 Б); база 'wc 5 te wc 5 te 3' =
# df520cf9. **ПЕРВЫЙ СТЕЙТМЕНТ В T3-ФОРМЕ = ГОЛЫЙ ХВОСТ U8 0x05**
# (te-хвост T3, БЕЗ chain1 — честная карта probe77; T3-одиночка
# 'wc 5 te' = 46 Б bac85372, emit '05' — тот же хвост, d-инвариант);
# ВТОРОЙ СТЕЙТМЕНТ = ПОЛНЫЙ T4-EMIT (05 15 BE32(d32) — тот же вид,
# что W-68). ЕДИНЫЙ ЗАКОН (probe77, 39 кейсов): каждый стейтмент
# эмитит [tail(kind)] + ([15 BE32(digit)] если есть digit-tail):
# T4×T3 'wc 5 te 3 wc 5 te' = 05 15 BE32(d31) + 05 (32448898);
# T4×T4-te = 05 15 BE32(d31) + 05 15 BE32(d32) (45188fc1); T3×T3
# 'wc 5 te wc 5 te' = 05 05 (47 Б c49e444f = НОВЫЙ пин, совпал с
# голой формой 'wc te 3 wc 5 te' — слоты НЕ входят). d32 НЕСУЩИЙ
# (d32=7 -> 9999e5a5, d32=9 -> 188a4508, d32=0 -> 5ef4e525);
# d1-ИНВАРИАНТНОСТЬ ('wc 7 te wc 5 te 3' = база df520cf9);
# d2-ИНВАРИАНТНОСТЬ ('wc 5 te wc 0 te 3' = 'wc 5 te wc 7 te 3' =
# база — valid(d2) несущий только для ЗАТВОРА, reslot для te НЕ
# несущий, оставлен для единообразия); явная точка на word7 = база;
# МУСОР ПОСЛЕ точки честно игнорируется ('... te 3 . 3' = df520cf9);
# Token = 7 (rep BE32 = 7, честный полный hex probe77: FF +
# BE32(7) + 20 нулей). Честные соседи-кроссы (том обязан молчать,
# ВСЕ пины сняты probe77 свежим stage1 — видовой хвост у каждого
# вида СВОЙ): T3×T4-pr 'wc 5 te wc 5 pr 3' = 60 Б 8f5455db, emit
# 05 + 54 BE32(0x3F0050C0) + BE32(слот F8) + 15 BE32(d32) — pr-
# хвост T4 = 9 Б (совпал с W-69); sv = 56 Б c29827f9, 05 + 55
# BE32(F8) + 15 BE32(d32) (W-70); sp = 56 Б 4cf32400, 05 + 53
# BE32(F8) + 15 BE32(d32) (W-71); vw = 55 Б c8e17647, 05 + BE32(F8)
# + 15 BE32(d32) (W-72); va = 57 Б a014b73e, 05 + 12 19 BE32(F8) +
# 15 BE32(d32) (W-73); if = 56 Б 1d69a38a, 05 + 06 BE32(0x14) +
# 15 BE32(d32) (W-74); as = 62 Б fe37197e, 05 + 12 15 BE32(F8) 55
# BE32(F8) + 15 BE32(d32) (W-75); ow = 65 Б 3f013021, 05 + 54
# BE32(0x00F00FF0) + BE32(F8) + 13 BE32(0x131) + 15 BE32(d32)
# (W-76) — stage1 ПРИНИМАЕТ, том молчит: word5 != 'te' -> PD < 2;
# T4×T4-te 8-ток 45188fc1 и T4×T3-te 7-ток 32448898 (word3 = '3' ->
# p0-2 bad -> PA < 5); T4-single 'wc 5 te 3' 495e8056 и T3-single
# 'wc 5 te' bac85372 (word3 пусто -> p0-2 = 0); T4-ow-single 'wc 5
# ow 3' fb10fa26; 9-ток 'wc 5 te wc 5 te 3 3' = 57 Б 6a6f0a94
# (stage1 ПРИНИМАЕТ, Token = 9, emit 05 05 15 BE32(3) + 15
# BE32(3)) — том молчит: word7 = '3' != '.' -> ppunkt = 0; 11-ток
# 'wc 5 te wc 5 te 3 wc 5 te 3' = 58 Б 03124111 (ТРИ стейтмента
# T3 T4 T4, emit 05 05 15 BE32(3) + 05 15 BE32(3)) — том молчит:
# word7 = 'w'; сирота-цифра 'wc 5 te wc 5' = 46 Б a3bac192 (emit
# 05, stage1 принимает — том молчит: word5 = '.'); голая 'wc te 3'
# bac85372 (word1 = 'te' -> valid1 bad); 'wc 5 te 3 wc te'
# 6265b72a; T3×T3 'wc 5 te wc 5 te' c49e444f (word6 = 'te' ->
# valid(d32) bad); bad d1/d2/d32, bad word0/word2/word3/word5,
# мусор/zz = FAIL 0xFE — том молчит.
# Честный дизайн (= T4×T3-те W-59: 7-ток слой + T4-скан CHECK2
# W-68, БЕЗ B2/RELOAD1 — d31 не существует в T3):
#   CHECK1 = скан T3-стейтмента (слова 0..2):
#     p0 (word0 == 'wc', PA = )               23 ток
#     valid(d1) digit-block тома-C (word1)    57 ток
#     C1: слот chain1: cell[wc0] = F3 + d1    13 ток
#         (для te НЕ несущий — d1 в emit не
#         входит, оставлен для единообразия)
#     pTe1 (word2 == LE2('te'), PD = )        23 ток
#     (T3 = 3 токена: НЕТ digit-block d31)
#   CHECK2 = скан T4-стейтмента (слова 3..6):
#     p0-2 (word3 == 'wc', PA += )            23 ток
#     valid(d2) digit-block (word4)           57 ток
#     reslot: RESET cell[wc0] = F3_MINUS_48   26 ток
#             (13) + 'wc 0 as' на word4 (13)
#             — для te НЕ несущий (единообразие)
#     pTe2 (word5 == LE2('te'), PD += )       23 ток
#     valid(d32) digit-block (word6)          57 ток
#   RELOAD2: d32 (word6) -> wc2 (= F5) ПОСЛЕ
#   CHECK2 (прецедент W-59/W-68: все F5-cp уже
#   прошли, затвор не читает F5 — честно)
#   G-затвор: PA (= p0+v1+p0-2+v3+v4 = 5) + PD
#   (= pTe1+pTe2 = 2) + ppunkt (word7 == '.') ==
#   8 ('eq 8' — одноразрядный immediate, дефект
#   'eq 13' W-58); терминатор на СЕДЬМОМ слове
#   (ячейка WORD8 = 10485788) — ключ-развязка с
#   T4×T4: у 8-ток двойника word3 = '3' -> p0-2
#   bad; у 9-ток '…te 3 3' word7 = '3' -> ppunkt
#   = 0; у 11-ток word7 = 'w'.
#   EMIT: TERM1 (05 — ТОЛЬКО TERM, честный хвост
#   T3-'te' первого стейтмента) -> chain2 (05 15
#   BE32(d32), wc2 = d32 из RELOAD2) -> вердец ->
#   отчёт (Token = 7: 'nb 7' 'wo' — токенов слоя
#   ДО терминатора, точка не считается — дефект-
#   находка probe55) -> SEAL/END.
#   Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t34te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('te' stmt-2)
WORD7      = 10485784        # word6 (d32)
WORD8      = 10485788        # word7 ('.' терминатор слоя T3×T4)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
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
          # (для te d1 НЕ входит в emit — блок оставлен для
          # единообразия дизайна)
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
          # Для te d2 НЕ входит в emit (probe77: d1/d2-инварианты);
          # несущий для ЗАТВОРА
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: честный reslot chain2: RESET cell[wc0] = F3 минус 48,
          # затем 'wc 0 as' на word4 -> cell[wc0] = 15732723 + d2.
          # Для te НЕ НЕСУЩИЙ (emit = 05 + 05 15 BE32(d32), слота
          # нет) — оставлен для единообразия
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD5), 'va',
          'wc', '0', 'as',
          # D2: pTe2 = (word5 == LE2('te')), PD += (конст F6 = wc 3 =
          # 25972 — та же конста, что PB statement1 'te'; для te-тома
          # ОВЕ kind-консты = 25972)
          nb(WORD6), 'va', nb(F6), 'cp',
          'wc', '9', 'as',
          # B4: честный digit-block на word6 (d32): bad4 в PF.
          # d32 НЕСУЩИЙ: BE32 chain2 (probe77: d32=7 -> 9999e5a5,
          # d32=9 -> 188a4508)
          nb(WORD7), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as']              # PA += valid4

# RELOAD2: d32 в ячейку wc2 (= F5) для BE32 chain2. Честный порядок
# (прецедент W-59/W-68): reload стоит ПОСЛЕ CHECK2 — все F5-cp уже
# прошли (valid3/valid4 сравнились), затвор F5 не читает; в T3×T4
# НЕТ RELOAD1 (d31 не существует — первый стейтмент в T3-форме)
RELOAD2 = [nb(WORD7), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d32

# F2/G2: ppunkt = (word7 == '.' — терминатор слоя T3×T4: ровно 7
# токенов; ключ-развязка с T4×T4: word3 = '3' -> p0-2 bad; с 9-ток:
# word7 = '3' -> ppunkt = 0); затвор: PA (5) + PD (2) + ppunkt == 8
# ('eq 8' — одноразрядный immediate, без cell-конст; дефект 'eq 13'
# W-58) — ИДЕНТИЧЕН W-59 (T4×T3), но PA = 5 по-новому: v1+p0-2+v3+v4
# (d32 несущий для затвора, d31 отсутствует)
TAIL_CHECK = [nb(WORD8), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '8',
              'if']

# EMIT: TERM1 (05 — ТОЛЬКО TERM: честный хвост T3-'te' первого
# стейтмента, карта probe77) -> chain2 (05 15 BE32(d32), wc2 = d32
# из RELOAD2) -> вердец -> отчёт -> SEAL/END ('nb 7 wo' — плейс-
# холдер, loader пишет токенов потока: слой T3×T4 = 7 токенов)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
TERM1 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (TERM, хвост T3-te)
CHAIN2 = ['nb 5', 'em', 'nb 3 0 8', 'sc',     # U8 5  (TERM)
          'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (LOAD 0x15)
          'wc', '2', 'ow']                    # BE32(d32)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 7', 'wo',                                    # Token = 7 (слой
                                                          # T3×T4-te: 7
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
       + CHAIN2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe77\pos_wc14v3t34te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t34te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
