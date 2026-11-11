# -*- coding: utf-8 -*-
# Сборщик честного КРОСС-ФОРМНОГО тома 'wc d te d3 wc d2 sv'
# Shape-T4×T3-sv (веха-23, спринт 41, W-61, TKT-052). База =
# wc14v3t43p_build.py (кросс-формный T4×T3-pr 615 ток, W-60) + честная
# карта probe56 (свежий stage1 на каждую цель): stage1 для T4×T3-sv
# целей = 56 Б 0xFF Token 7, emit = 05 15 BE32(d31) + 55 00 F0 0F
# [слот-байт] (11 Б); база 'wc 5 te 3 wc 5 sv' = b904f09d.
# **СЛОТ-БАЙТ ЖИВ в T3-хвосте**: последний байт sv-emit = младший байт
# адреса слота = (wc0 + d2) & 0xFF = 0xF3 + d2 (probe56: d2=5 -> F8
# b904f09d, d2=7 -> FA a4a86ea9; тот же закон для pr-хвоста
# 54 3F 00 50 C0 00 F0 0F [F3+d2], прецедент W-57/W-60); sv-emit
# декодирован честно: U8 0x55 + BE32(адрес-слота = cell[wc0]) —
# БЕЗ консты-аргумента (pr-хвост несёт BE32 0x3F0050C0, sv — нет:
# 5 Б против 9 Б); reslot из CHECK2 (cell[wc0] = F3_MINUS_48 + символ
# цифры = 15732723 + d2 = адрес-слот) НЕСУЩИЙ: слот-байт честно
# берётся прямо из cell[wc0] ('wc 0 ow' — acc-based BE32-вывод);
# d1-ИНВАРИАНТНОСТЬ ('wc 7 te 3 wc 5 sv' = база b904f09d — слот
# стейтмента-1 не входит в emit); явная точка = база; Token отчёта =
# 7 (слой до терминатора, дефект-находка W-59). Честные соседи-
# кроссы (том обязан молчать): T4×T4-sv 8-ток = fe6aeb2b (61 Б, emit
# ...F8 15 BE32(3), stage1 принимает, word7 = '3'); T4×T4-pr 8-ток =
# 3f3634ef; T4×T3-te (W-59 форма) = 32448898 (word6 = 'te', не 'sv');
# T4×T3-pr (W-60 форма) = 26a8b48c (word6 = 'pr'); reversed W-57
# 'wc 5 pr 3 wc 5 te 3' = 1c775e42 (word2 = 'pr'); голые формы
# 'wc sv' = be7bdf42 (50 Б, emit 55...F1) / T3-одиночка 'wc 0 sv' =
# eeee2e3e (50 Б, emit 55...F3); сирота-цифра 'wc 5 te 3 wc 5' =
# 8b2c4a6f (stage1 принимает, том молчит: word6 = '.'); мусор после
# слоя = FAIL 0xFE stage1 — том молчит.
# Честный дизайн (= W-60 + sv-хвост):
#   CHECK1 = канон T4 (A,B,C,D,B2 без F/G)          203 ток
#   CHECK2 = скан T3-стейтмента (слова 4..6):
#     p0-2 (word4 == 'wc', PA += )                  23 ток
#     valid(d2) digit-block (word5)                 57 ток
#     reslot: RESET cell[wc0] = F3_MINUS_48 (13) +
#             'wc 0 as' на word5 (13) — НЕСУЩИЙ:
#             cell[wc0] = 15732723 + d2 = адрес-слот  26 ток
#     pSv (word6 == LE2('sv'), PD += )              23 ток
#     (LE2('sv') = 0x7673 = 30323 — конст cell wc3 =
#     F6 — ТА ЖЕ ячейка, что 'pr'-конст W-60. Честная
#     находка probe57: wc5 = 15732728 НЕ свободна —
#     COPY читает 'wc 5' как emit-указатель, конст в
#     cell[wc5] = ВСЕ цели молчат при честно
#     компилирующемся томе; карта «wc5 свободна»
#     была неверна);
#     T3 = 3 токена: НЕТ второго digit-block — word7 =
#     терминатор)
#   RELOAD1: d31 -> wc2 (= F5) ПОСЛЕ последнего F5-cp
#   G-затвор: PA (5) + PD (2) + ppunkt == 8 — ИДЕНТИЧЕН W-59/W-60
#   ('eq 8' одноразрядный); терминатор на word7 — ключ-развязка:
#   у 8-ток двойников (T4×T4-sv/pr) word7 = '3' -> молчание.
#   SV_TAIL (заменяет PR_TAIL W-60): U8 0x55 + BE32(адрес-слота =
#   cell[wc0]) — 'ow' = acc-based BE32-вывод ('em' = pending-U8,
#   дефект-находка probe56). Token = 7. Лимит честного тома
#   вехи-23 = 1022 ток.
#   Честные дефекты, пойманные прогонами probe57:
#   (1) конста 'sv' в wc5 = 15732728 — ВСЕ цели молчат при честно
#   компилирующемся томе: wc5 НЕ свободна, COPY читает 'wc 5' как
#   emit-указатель; исправлено — конст в wc3 (= F6, та же ячейка,
#   что 'pr'-конст W-60);
#   (2) 'nb 5 5' = 55 ДЕСЯТИЧНЫХ = 0x37, а нужен U8 0x55 = 85 →
#   'nb 8 5' ('nb'-литералы — десятичные по цифрам; W-60 спасала
#   случайность 'nb 8 4' = 84₁₀ = 0x54).
# pos_wc14v3t43s.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te')
WORD4      = 10485772        # word3 (d31)
WORD5      = 10485776        # word4 ('wc' stmt-2)
WORD6      = 10485780        # word5 (d2)
WORD7      = 10485784        # word6 ('sv' stmt-2)
WORD8      = 10485788        # word7 ('.' терминатор слоя T4×T3-sv)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
WC0 = 15732723               # адрес слота: cell[wc0] = F3 + d (reslot)
F5 = 15732725
F6 = 15732726                # wc 3 - конст LE2('sv') = 30323 (INIT)
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
        nb(30323), 'ne', 'wc', '3', 'sv']            # 'sv' (LE2)

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
          # НЕСУЩИЙ: слот-байт SV_TAIL честно берётся из cell[wc0]
          nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
          nb(WORD6), 'va',
          'wc', '0', 'as',
          # D2: pSv = (word6 == LE2('sv')), PD += (конст F6 = wc 3 —
          # ТА ЖЕ ячейка, что 'pr'-конст W-60; wc5 ЗАНЯТА: COPY читает
          # 'wc 5' как emit-указатель — честная находка probe57: конст
          # в cell[wc5] = ВСЕ цели молчат, карта «wc5 свободна» была
          # неверна)
          nb(WORD7), 'va', nb(F6), 'cp',
          'wc', '9', 'as']

# RELOAD1: d31 в ячейку wc2 (= F5) для BE32 chain1. Честный порядок
# (прецедент W-56/probe52): reload обязан стоять ПОСЛЕ последнего
# F5-cp (теперь B3) — иначе cell[F5] = d31 портит сравнение valid3
# (d31 != 0 -> цели молчат).
RELOAD1 = [nb(WORD4), 'va',
           'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
           'wc', '2', 'sv']              # cell[wc2] = d31

# F2/G2: ppunkt = (word7 == '.' — терминатор слоя T4×T3-sv: ровно 7
# токенов; ключ-развязка с T4×T4-sv/pr: word7 = '3' -> ppunkt = 0);
# затвор: PA (5) + PD (2) + ppunkt == 8 ('eq 8' — одноразрядный
# immediate, без cell-конст; дефект 'eq 13' W-58) — ИДЕНТИЧЕН W-59
TAIL_CHECK = [nb(WORD8), 'va', nb(PC), 'cp',
              nb(PA), 'aa',
              nb(PD), 'aa',
              'eq', '8',
              'if']

# EMIT: chain1 (05 15 BE32(d31), wc2 = d31 из RELOAD1) -> SV_TAIL
# (55 00 F0 0F + слот-байт из cell[wc0]) -> вердец -> отчёт -> SEAL/END.
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
# SV_TAIL = честный хвост T3-'sv' (probe56, прецедент 'wc 0 ow' =
# BE32(F3+d) W-57/W-60): U8 0x55 + BE32(cell[wc0]) = адрес-слот
# 00 F0 0F [F3+d2] — 'ow' = acc-based BE32-вывод ('em' = pending-U8,
# дефект 'va em' probe56: em без pending -> fail 0xFE Token 633);
# БЕЗ консты-аргумента 0x3F0050C0 (pr-хвост несёт её, sv — нет).
# Reslot CHECK2 несущий.
SV_TAIL = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 0x55 (= 85 десятичных;
                                               # честная находка probe57:
                                               # 'nb'-литералы читаются как
                                               # ДЕСЯТИЧНЫЕ числа по цифрам —
                                               # 'nb 5 5' = 55₁₀ = 0x37!
                                               # W-60 спасала случайность:
                                               # 'nb 8 4' = 84₁₀ = 0x54)
           'wc', '0', 'ow']                    # BE32(адрес-слота)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 7', 'wo',                                    # Token = 7 (слой
                                                         # T4×T3-sv: 7
                                                         # токенов до
                                                         # терминатора)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + RELOAD1 + TAIL_CHECK + EMIT_HEAD + CHAIN1 \
       + SV_TAIL + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\pos_wc14v3t43s.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t43s tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
