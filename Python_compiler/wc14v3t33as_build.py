# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d as wc d as'
# Shape-T3×T3-as (веха-23, спринт 73, W-93, TKT-052): СТРИМ — восьмой
# вид многостейтментного тома, ОБА хвоста НЕСУЩИЕ (as-хвост 11 Б —
# U8 0x12 + U8 0x15 + BE32(слот) + U8 0x55 + BE32(слот), закон W-75:
# ОБА BE32 читают СЛОТ — T3-as-single 'wc 5 as' emit '12 15
# BE32(F3+d1) 55 BE32(F3+d1)', пин W-84/probe84) => d1/d2 НЕТ инваров —
# как у pr/sv/sp/vw/va-томов W-87..W-91.
# База = wc14v3t33va-структура (W-91) + честная карта probe93 (47
# кейсов, свежий stage1 на каждую цель): stage1 для T3×T3-as целей =
# 67 Б 0xFF Token 6, emit = [as-T3-хвост] ×2 = [12 15 BE32(слот F3+d)
# 55 BE32(слот F3+d)] ×2 = 22 Б; база 'wc 5 as wc 5 as' = 80a53bb1
# (честный полный hex probe93: header CRC 5f5195b0 + emit
# 121500f00ff85500f00ff8121500f00ff85500f00ff8 + FF + BE32(6) + 20
# нулей). **СЛОТ НЕСУЩИЙ В ОБОИХ ХВОСТАХ (ОБА BE32)** (карта probe93:
# 'wc 7 as wc 5 as' = 67 Б 9fcda3d2, emit 121500f00ffa5500f00ffa… —
# слот1 = FA = F3+d1; 'wc 5 as wc 7 as' = a614afd1 — слот2 = FA;
# 'wc 7 as wc 7 as' = 0c496533 — FA FA; 'wc 0 as wc 0 as' = 69f39501
# — F3 F3; 'wc 1 as wc 3 as' = a72fb2c0 — F4 F6; 'wc 9 as wc 8 as' =
# 980d5ae7 — FC FB) — три tracked-цели W-93 ДАЮТ ТРИ РАЗНЫЕ md5
# (честное доказательство несущих слотов).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 as wc 5 as .'
# = 80a53bb1; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = 15732726 (wc3)** (В W-93
# НЕЛЬЗЯ 15732723/15732725: там СЛОТЫ d1/d2 — chain1/reslot пишут
# адреса слотов F3+d1/F3+d2, TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'
# ПОСЛЕ TAIL_CHECK; wc3 свободна — как в W-87..W-91; формы
# 'nb(STASH), sv'/'nb(STASH), aa' — честно проверенные
# 'nb(PF), sv'/'nb(PA), aa').
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pAs1+pAs2 = 2) + pEOF ==
# 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-tail d32
# не существует в T3×T3: word6 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): te/pr/sv/sp/vw/va/if-
# смеси — stage1 ПРИНИМАЕТ ('wc 5 as wc 5 te' = 57 Б 640ebe97 =
# as-хвост + 05; 'wc 5 te wc 5 as' = 57 Б 3a7cc82f = 05 + as-хвост;
# 'wc 5 as wc 5 sv' = 61 Б 4d5be862 = as-хвост + 55BE32; 'wc 5 sv wc
# 5 as' = 61 Б bb7fa2d2; 'wc 5 as wc 5 sp' = 61 Б 97191149 = as-хвост
# + 53BE32; 'wc 5 sp wc 5 as' = 61 Б 338ce940; 'wc 5 as wc 5 vw' = 60
# Б 5f3f3c87 = as-хвост + BE32; 'wc 5 vw wc 5 as' = 60 Б bc9d255f;
# 'wc 5 as wc 5 va' = 62 Б bc19bcfc = as-хвост + 1219BE32; 'wc 5 va
# wc 5 as' = 62 Б 63cc01fa; 'wc 5 as wc 5 pr' = 65 Б 404b13d2 =
# as-хвост + pr-хвост; 'wc 5 pr wc 5 as' = 65 Б 9a255d54; 'wc 5 as wc
# 5 if' = 61 Б 5151411a = as-хвост + 06BE32(0x14); 'wc 5 if wc 5 as'
# = 61 Б 740e64e3; 'wc 5 te wc 5 te' = 47 Б c49e444f база W-86) — том
# молчит: pAs2/pAs1/обе = 0; 3/4-stmt as-потоки — stage1 ПРИНИМАЕТ
# ('wc 5 as wc 5 as wc 5 as' = 78 Б 784a64e4 Token 9, emit 33 Б = 3
# as-хвоста, точка-вариант тот же 784a64e4; 4-stmt = 89 Б 3f6d8893,
# emit 44 Б = 4 as-хвоста — В ОТЛИЧИЕ от if: 4 if-стейтмента stage1
# бракует [0xFE ebe049f9, W-92], 4 as-стейтмента ПРИНИМАЕТ [НОВЫЙ пин
# W-93]) — том молчит: word6 = 'wc' → pEOF = 0; 'wc 5 as wc 5 as 3' =
# 72 Б d0814e42 (НОВЫЙ пин: T3-as×T4-as, emit 27 Б = as-хвосты ×2 +
# digit-tail 15 00000003) — word6 = '3' → pEOF = 0; 'wc 5 as 3 wc 5
# as' = 72 Б 2f06bb3b (НОВЫЙ пин: T4-as×T3-as, digit-tail МЕЖДУ
# хвостами, emit 27 Б) — word3 = '3' → p0-2 bad; 'wc 5 as 3 wc 5 as
# 3' = 77 Б 5fb8d6c8 (НОВЫЙ пин: T4×T4-as, emit 32 Б; точка-вариант
# тот же 5fb8d6c8); 'wc 5 as wc 5 as 3 3' = 77 Б 76767951 (НОВЫЙ пин,
# Token 8, emit 32 Б); 'wc 5 as wc 5 as as' = 78 Б 52eb2ae5 (НОВЫЙ
# пин: word6 = 'as', emit 33 Б = 3 as-хвоста) — том молчит: pEOF = 0;
# singles/сироты 'wc 5 as' = 56 Б 1176c0df (пин W-84/probe84 —
# СОВПАЛ, emit 11 Б), 'wc 5 as 3' = 61 Б cbb9ba26 (пин W-84 — СОВПАЛ,
# emit 16 Б), сирота 'wc 5 as wc 5' = 56 Б 59a9f18d (НОВЫЙ пин: emit
# 11 Б), 'wc 5 vw' = 49 Б 00ce976e (пин probe90..92), 'wc 5 sv' = 50
# Б 6a16ae85 (пин probe88..92), 'wc 5 te' = 46 Б bac85372; неги-браки:
# 'wc as wc 5 as' = 0xFE 56 Б 9300cf34 (НОВЫЙ пин: bad word1 — emit
# 11 Б со слотом F1 = 0x00F00FF1 = 15732721 DEFAULT WORK_CELL,
# W_Current не сменился); 'wc 5 as wc as' — stage1 ПРИНИМАЕТ (67 Б
# c6cdaa69 0xFF, emit 22 Б — ОБА хвоста со слотом F8 от stmt-1) — том
# молчит: v2 = 0 → PA = 3; bad d1 = 0xFE 45 Б 29ba6852 (= W-86..92);
# bad d2 = 0xFE 56 Б 26811567 (НОВЫЙ пин: emit 11 Б — хвост stmt-1);
# bad word2 = 0xFE 45 Б 4ff7c705 (= W-86..92); bad word5 = 0xFE 56 Б
# a1b1f926 (НОВЫЙ пин: emit 11 Б); bad word0/мусор = f3667180.
# EMIT: AS_TAIL1 (честный хвост T3-'as' стейтмента 1, карта probe93:
# 12 15 + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ) + 55 + BE32(cell[wc0]),
# 11 Б — закон W-75) -> AS_TAIL2 (честный хвост T3-'as' стейтмента 2:
# 12 15 + BE32(cell[wc2] = слот F3+d2 НЕСУЩИЙ) + 55 + BE32(cell[wc2]),
# 11 Б; честный emit базы probe93 121500f00ff85500f00ff8… ×2) ->
# вердец -> отчёт (Token = 6: 'nb 6' 'wo' — токенов слоя ДО
# терминатора, точка не считается) -> SEAL/END. Честный дизайн (=
# W-91 va-структура):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для AS_TAIL1;
#   прецедент W-87..W-91 CHECK1 C1) + pAs1 (word2 == LE2('as') =
#   29537, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для AS_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2)
#   + pAs2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('as') = 29537 → wc7 — 'a' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x7361; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33as.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('as' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('as' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-87..W-91 stash; в W-93
                             # оба вида 'as'): stash pEOF-ветки
                             # (15732723 = СЛОТ d1, 15732725 = СЛОТ d2 —
                             # трогать НЕЛЬЗЯ: TERM-фаза читает их после
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('as') = 29537 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29537), 'ne', 'wc', '7', 'sv',           # 'as' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv']              # '.' (терминатор)

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = скан T3-стейтмента 1 (слова 0..2; 3 токена — БЕЗ digit-
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
          # C1: честный слот chain1: cell[wc0] = F3_MINUS_48 + word1
          # = 15732723 + d1 — НЕСУЩИЙ для AS_TAIL1 (карта probe93:
          # 'wc 7 as …' → BE32(FA); 'wc 0 as …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pAs1 = (word2 == LE2('as'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pAs1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (as-аккумулятор)
          nb(WORD4), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word4 (d2): bad3 в PF.
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: честный reslot chain2: RESET cell[wc2] = F3 минус 48,
          # затем 'wc 2 as' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для AS_TAIL2 (карта probe93: '… wc 7 as' → BE32(FA);
          # '… wc 0 as' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pAs2 = (word5 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs2
          # НЕТ RELOAD2: digit-tail d32 не существует в T3×T3 (word6 =
          # терминатор слоя)

# F2/G2: pEOF = (word6 == 0 ИЛИ word6 == '.') — арифметическая сумма
# ДВУХ сравнений через stash-ячейку STASH = 15732726 (wc3 — свободна;
# 15732723 = СЛОТ d1, 15732725 = СЛОТ d2 — трогать НЕЛЬЗЯ: TERM-фаза
# читает их после TAIL_CHECK); терминатор слоя T3×T3 на ШЕСТОМ слове
# (WORD7 = 10485784). Затвор: PA (4) + PD (2) + pEOF == 7 ('eq 7')
TAIL_CHECK = [nb(WORD7), 'va', 'eq', '0',       # acc = eq(word6, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(STASH), 'sv',                  # stash → cell[15732726]
              nb(WORD7), 'va', nb(PC), 'cp',    # acc = eq(word6, '.')
              nb(STASH), 'aa',                  # acc += stash
              'eq', '7',
              'if']

# EMIT: AS_TAIL1 (честный хвост T3-'as' стейтмента 1, карта probe93:
# 12 15 + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1 CHECK1) + 55 +
# BE32(cell[wc0]), 11 Б — закон W-75: U8 0x12 = 18₁₀ (LOAD-адрес) +
# U8 0x15 = 21₁₀ (ADD) + BE32(слот) + U8 0x55 = 85₁₀ (STORE-конста;
# урок probe57/W-75: 'nb 8 5' = 85₁₀ = 0x55, 'nb 5 5' = 55₁₀ = 0x37
# НЕВЕРНО) + BE32(слот)) -> AS_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2) ×2) -> вердец -> отчёт (Token = 6)
AS_TAIL1 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12, LOAD)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (0x15, ADD)
            'wc', '0', 'ow',                    # BE32(слот F3+d1 — chain1)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 85 (0x55, STORE)
            'wc', '0', 'ow']                    # BE32(слот F3+d1 — chain1)
AS_TAIL2 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12, LOAD)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',   # U8 21 (0x15, ADD)
            'wc', '2', 'ow',                    # BE32(слот F3+d2 — reslot)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 85 (0x55, STORE)
            'wc', '2', 'ow']                    # BE32(слот F3+d2 — reslot)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 6', 'wo',                                    # Token = 6 (6
                                                          # токенов слоя
                                                          # ДО
                                                          # терминатора;
                                                          # точка не
                                                          # считается)
        'nb 0', 'wo',                                    # wr2 = 0 (конст)
        'nb 0', 'wo',                                    # wr3 = 0
        'nb 0', 'wo',                                    # rep[3] = 0
        'nb 0', 'wo',                                    # FC = 0@0
        'nb 0', 'wo',                                    # pos = 0
        'nb 3 0 9', 'sc', 'nb 3 0 7', 'sc']

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + AS_TAIL1 \
       + AS_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe93\pos_wc14v3t33as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
