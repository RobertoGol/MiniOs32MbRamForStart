# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d ow wc d ow'
# Shape-T3×T3-ow (веха-23, спринт 74, W-94, TKT-052): СТРИМ — девятый
# (последний) вид многостейтментного тома, ОБА хвоста НЕСУЩИЕ (ow-
# хвост 14 Б — U8 0x54 + BE32(0x00F00FF0 КОНСТА) + BE32(слот) + U8
# 0x13 + BE32(0x131 КОНСТА), закон W-76: ПЕРВЫЙ BE32 = КОНСТА
# 0x00F00FF0 = 15732720 — ИНВАРИАНТЕН в d1/d2, ВТОРОЙ BE32 читает
# СЛОТ — T3-ow-single 'wc 5 ow' emit '54 00f00ff0 BE32(F3+d1) 13
# 00000131', пин W-85/probe85 b733ee4c) => d1/d2 НЕ инвары — как у
# pr/sv/sp/vw/va/as-томов W-87..W-93.
# База = wc14v3t33as-структура (W-93, va-структура W-91) + честная
# карта probe94 (49 кейсов, свежий stage1 на каждую цель): stage1 для
# T3×T3-ow целей = 73 Б 0xFF Token 6, emit = [ow-T3-хвост] ×2 = [54
# BE32(0x00F00FF0 КОНСТА) BE32(слот F3+d) 13 BE32(0x131 КОНСТА)] ×2 =
# 28 Б; база 'wc 5 ow wc 5 ow' = 40251c66 (честный полный hex
# probe94: header CRC 00374d17 + emit 5400f00ff000f00ff81300000131
# 5400f00ff000f00ff81300000131 + FF + BE32(6) + 20 нулей). **СЛОТ
# НЕСУЩИЙ ТОЛЬКО ВО ВТОРОМ BE32 (ПЕРВЫЙ = КОНСТА, закон W-76)**
# (карта probe94: 'wc 7 ow wc 5 ow' = 73 Б 2075a2c0, emit
# 5400f00ff000f00ffa1300000131… — слот1 = FA = F3+d1; 'wc 5 ow wc 7
# ow' = a54d118c — слот2 = FA; 'wc 7 ow wc 7 ow' = 8f5a977f — FA FA;
# 'wc 0 ow wc 0 ow' = ffe4420a — F3 F3; 'wc 1 ow wc 3 ow' = d18547fa
# — F4 F6; 'wc 9 ow wc 8 ow' = 66b2cb8f — FC FB) — три tracked-цели
# W-94 ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство несущего слота
# W-76).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 ow wc 5 ow .'
# = 40251c66; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = 15732726 (wc3)** (В W-94
# НЕЛЬЗЯ 15732723/15732725: там СЛОТЫ d1/d2 — chain1/reslot пишут
# адреса слотов F3+d1/F3+d2, TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'
# ПОСЛЕ TAIL_CHECK; wc3 свободна — как в W-87..W-93; формы
# 'nb(STASH), sv'/'nb(STASH), aa' — честно проверенные
# 'nb(PF), sv'/'nb(PA), aa').
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pOw1+pOw2 = 2) + pEOF ==
# 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-tail d32
# не существует в T3×T3: word6 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): te/sv/sp/vw/va/pr/if/
# as-смеси — stage1 ПРИНИМАЕТ ('wc 5 ow wc 5 te' = 60 Б 491b8dc9 =
# ow-хвост + 05; 'wc 5 te wc 5 ow' = 60 Б 7b3b9765 = 05 + ow-хвост;
# 'wc 5 ow wc 5 sv' = 64 Б 923d7c8b = ow-хвост + 55BE32; 'wc 5 sv wc
# 5 ow' = 64 Б 43d21d5f; 'wc 5 ow wc 5 sp' = 64 Б be75d926 = ow-хвост
# + 53BE32; 'wc 5 sp wc 5 ow' = 64 Б 849430f1; 'wc 5 ow wc 5 vw' = 63
# Б ab0c69ed = ow-хвост + BE32; 'wc 5 vw wc 5 ow' = 63 Б b5959eb9;
# 'wc 5 ow wc 5 va' = 65 Б 7ea79c72 = ow-хвост + 1219BE32; 'wc 5 va
# wc 5 ow' = 65 Б 0c6acb61; 'wc 5 ow wc 5 pr' = 68 Б 3d35c2e1 =
# ow-хвост + pr-хвост; 'wc 5 pr wc 5 ow' = 68 Б 4cb250c3; 'wc 5 ow wc
# 5 if' = 64 Б a46abe3a = ow-хвост + 06BE32(0x14); 'wc 5 if wc 5 ow'
# = 64 Б ca685a47; 'wc 5 ow wc 5 as' = 70 Б 7b9fd1f7 = ow-хвост +
# as-хвост; 'wc 5 as wc 5 ow' = 70 Б 81bacbfe; 'wc 5 te wc 5 te' = 47
# Б c49e444f база W-86) — том молчит: pOw2/pOw1/обе = 0; 3/4-stmt
# ow-потоки — stage1 ПРИНИМАЕТ ('wc 5 ow wc 5 ow wc 5 ow' = 87 Б
# 977e2a7a Token 9, emit 42 Б = 3 ow-хвоста, точка-вариант тот же
# 977e2a7a; 4-stmt = 101 Б c39da5d5, emit 56 Б = 4 ow-хвоста — В
# ОТЛИЧИЕ от if: 4 if-стейтмента stage1 бракует [0xFE ebe049f9,
# W-92], 4 ow-стейтмента ПРИНИМАЕТ [НОВЫЙ пин W-94]) — том молчит:
# word6 = 'wc' → pEOF = 0; 'wc 5 ow wc 5 ow 3' = 78 Б 9a6a53e9 (НОВЫЙ
# пин: T3-ow×T4-ow, emit 33 Б = ow-хвосты ×2 + digit-tail 15
# 00000003) — word6 = '3' → pEOF = 0; 'wc 5 ow 3 wc 5 ow' = 78 Б
# 691890f6 (НОВЫЙ пин: T4-ow×T3-ow, digit-tail МЕЖДУ хвостами, emit
# 33 Б) — word3 = '3' → p0-2 bad; 'wc 5 ow 3 wc 5 ow 3' = 83 Б
# ead92d5a (НОВЫЙ пин: T4×T4-ow, emit 38 Б; точка-вариант тот же
# ead92d5a); 'wc 5 ow wc 5 ow 3 3' = 83 Б b9d2425c (НОВЫЙ пин, Token
# 8, emit 38 Б); 'wc 5 ow wc 5 ow ow' = 87 Б 49149cf0 (НОВЫЙ пин:
# word6 = 'ow', emit 42 Б = 3 ow-хвоста) — том молчит: pEOF = 0;
# singles/сироты 'wc 5 ow' = 59 Б b733ee4c (пин W-85/probe85 —
# СОВПАЛ, emit 14 Б), 'wc 5 ow 3' = 64 Б fb10fa26 (пин W-85 —
# СОВПАЛ, emit 19 Б), сирота 'wc 5 ow wc 5' = 59 Б a48426b6 (НОВЫЙ
# пин: emit 14 Б), 'wc 5 vw' = 49 Б 00ce976e (пин probe90..93), 'wc
# 5 sv' = 50 Б 6a16ae85 (пин probe88..93), 'wc 5 te' = 46 Б
# bac85372; неги-браки: 'wc ow wc 5 ow' = 0xFE 59 Б ff73c458 (НОВЫЙ
# пин: bad word1 — emit 14 Б со слотом F1 = 0x00F00FF1 = 15732721
# DEFAULT WORK_CELL, W_Current не сменился); 'wc 5 ow wc ow' —
# stage1 ПРИНИМАЕТ (73 Б b5ace5e8 0xFF, emit 28 Б — ОБА хвоста со
# слотом F8 от stmt-1) — том молчит: v2 = 0 → PA = 3; bad d1 = 0xFE
# 45 Б 29ba6852 (= W-86..93); bad d2 = 0xFE 59 Б ea08576d (НОВЫЙ
# пин: emit 14 Б — хвост stmt-1); bad word2 = 0xFE 45 Б 4ff7c705
# (= W-86..93); bad word5 = 0xFE 59 Б 7a101f35 (НОВЫЙ пин: emit 14
# Б); bad word0/мусор = f3667180.
# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe94:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo' = pending-nb BE32-вывод КОНСТАНТЫ, прецедент W-83/W-85) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 ('nb 1 9' =
# 19₁₀ [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ]) + BE32(0x131 =
# 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76: ПЕРВЫЙ BE32 =
# КОНСТА (инвариантен), ВТОРОЙ BE32 = СЛОТ) -> OW_TAIL2 (тот же хвост
# с reslot: BE32(cell[wc2] = слот F3+d2)) -> вердец -> отчёт (Token =
# 6: 'nb 6' 'wo' — токенов слоя ДО терминатора, точка не считается)
# -> SEAL/END. Честный дизайн (= W-93 as-структура, va-структура
# W-91):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для OW_TAIL1;
#   прецедент W-87..W-93 CHECK1 C1) + pOw1 (word2 == LE2('ow') =
#   30575, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 ow' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для OW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2)
#   + pOw2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('ow') = 30575 → wc7 — 'o' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x776F; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33ow.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('ow' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('ow' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-87..W-93 stash; в W-94
                             # оба вида 'ow'): stash pEOF-ветки
                             # (15732723 = СЛОТ d1, 15732725 = СЛОТ d2 —
                             # трогать НЕЛЬЗЯ: TERM-фаза читает их после
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('ow') = 30575 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(30575), 'ne', 'wc', '7', 'sv',           # 'ow' (PB, LE2)
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
          'wc', '6', 'as',
          # C1: честный слот chain1: cell[wc0] = F3_MINUS_48 + word1
          # = 15732723 + d1 — НЕСУЩИЙ для OW_TAIL1 (карта probe94:
          # 'wc 7 ow …' → BE32(FA); 'wc 0 ow …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pOw1 = (word2 == LE2('ow'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pOw1

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
          # НЕСУЩИЙ для OW_TAIL2 (карта probe94: '… wc 7 ow' → BE32(FA);
          # '… wc 0 ow' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pOw2 = (word5 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw2
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

# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe94:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo') + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 +
# BE32(0x131 = 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76:
# ПЕРВЫЙ BE32 = КОНСТА (инвариантен в d1/d2), ВТОРОЙ BE32 = СЛОТ;
# 'nb 8 4' = 84₁₀ = 0x54, 'nb 1 9' = 19₁₀ = 0x13 [урок probe57/W-64:
# nb-литералы ДЕСЯТИЧНЫЕ]) -> OW_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2) — честный emit базы probe94
# 5400f00ff000f00ff81300000131 ×2) -> вердец -> отчёт (Token = 6)
OW_TAIL1 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '0', 'ow',                         # BE32(слот F3+d1 — chain1)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
OW_TAIL2 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '2', 'ow',                         # BE32(слот F3+d2 — reslot)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + OW_TAIL1 \
       + OW_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe94\pos_wc14v3t33ow.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33ow tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
