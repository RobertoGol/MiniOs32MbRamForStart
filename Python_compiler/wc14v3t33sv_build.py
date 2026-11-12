# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d sv wc d sv'
# Shape-T3×T3-sv (веха-23, спринт 68, W-88, TKT-052): СТРИМ — третий
# вид многостейтментного тома, оба хвоста НЕСУЩИЕ (слоты d1/d2 входят
# в emit) => d1/d2 НЕТ инваров — как у pr-тома W-87 (sv-хвост БЕЗ
# консты, 5 Б, в отличие от pr — урок W-79).
# База = wc14v3t33pr-структура (W-87) + честная карта probe88 (35
# кейсов, свежий stage1 на каждую цель): stage1 для T3×T3-sv целей =
# 55 Б 0xFF Token 6, emit = [sv-T3-хвост] ×2 = [55 BE32(слот F3+d)] ×2
# = 10 Б; база 'wc 5 sv wc 5 sv' = cd1086b0 (честный полный hex
# probe88: header CRC a2b4e40a + emit 5500f00ff85500f00ff8 + FF +
# BE32(6) + 20 нулей). **СЛОТ НЕСУЩИЙ В ОБОИХ ХВОСТАХ** (карта
# probe88: 'wc 7 sv wc 5 sv' = 55 Б bdd718db, emit
# 5500f00ffa5500f00ff8 — слот1 = FA = F3+d1; 'wc 5 sv wc 7 sv' =
# 8435c2f4 — слот2 = FA = F3+d2; 'wc 7 sv wc 7 sv' = d43e9f7f — FA FA;
# 'wc 0 sv wc 0 sv' = 5daa2d4e — F3 F3; 'wc 1 sv wc 3 sv' = d44710ba —
# F4 F6; 'wc 9 sv wc 8 sv' = c2951982 — FC FB) — три tracked-цели
# W-88 ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство несущих слотов).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 sv wc 5 sv .'
# = cd1086b0; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = 15732726 (wc3)** (В W-88
# НЕЛЬЗЯ 15732723: там СЛОТ — chain1/reslot пишут адреса слотов
# F3+d1/F3+d2, TERM-фаза читает их 'wc 0 ow'/'wc 2 ow' ПОСЛЕ
# TAIL_CHECK; wc3 свободна — в W-87 тоже stash; формы 'nb(STASH), sv'
# / 'nb(STASH), aa' — честно проверенные 'nb(PF), sv'/'nb(PA), aa').
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pSv1+pSv2 = 2) + pEOF ==
# 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-tail d32
# не существует в T3×T3: word6 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): te/pr/sv-смеси — stage1
# ПРИНИМАЕТ ('wc 5 sv wc 5 te' = 51 Б 13d1cb2a = sv-хвост + 05; 'wc 5
# te wc 5 sv' = 51 Б 3de2d640 = 05 + sv-хвост; 'wc 5 sv wc 5 pr' = 59
# Б 5cb6140b = sv-хвост + pr-хвост; 'wc 5 pr wc 5 sv' = 59 Б 8c6455be
# = pr-хвост + sv-хвост; 'wc 5 te wc 5 te' = 47 Б c49e444f база W-86)
# — том молчит: pSv2/pSv1/обе = 0; 3/4-stmt sv-потоки — stage1
# ПРИНИМАЕТ ('wc 5 sv wc 5 sv wc 5 sv' = 60 Б c23cf6ec Token 9, emit
# 15 Б = 3 sv-хвоста, точка-вариант тот же c23cf6ec; 4-stmt = 65 Б
# 05df0915, emit 20 Б) — том молчит: word6 = 'wc' → pEOF = 0; 'wc 5 sv
# wc 5 sv 3' = 60 Б b2939d7c (НОВЫЙ пин: T3-sv×T4-sv, emit 15 Б = 55×2
# + digit-tail 15 00000003) — word6 = '3' → pEOF = 0; 'wc 5 sv 3 wc 5
# sv' = 60 Б 7340522f (НОВЫЙ пин: T4-sv×T3-sv, emit 15 Б) — word3 =
# '3' → p0-2 bad; 'wc 5 sv 3 wc 5 sv 3' = 65 Б 1b8699b9 (НОВЫЙ пин:
# T4×T4-sv, emit 20 Б; точка-вариант тот же 1b8699b9); 'wc 5 sv wc 5
# sv 3 3' = 65 Б 19832dd4 (НОВЫЙ пин, Token 8, emit 20 Б); 'wc 5 sv wc
# 5 sv sv' = 60 Б f9f9c9af (НОВЫЙ пин: word6 = 'sv', emit 15 Б = 3
# sv-хвоста) — том молчит: pEOF = 0; singles/сироты 'wc 5 sv' = 50 Б
# 6a16ae85 (НОВЫЙ пин: emit 5 Б), сирота 'wc 5 sv wc 5' = 50 Б
# 46e2f69b (НОВЫЙ пин: emit 5 Б), 'wc 5 sp' = 50 Б 87817a4b (НОВЫЙ
# пин: sp-хвост 53 00f00ff8 — 0x53 = 83₁₀, урок W-80), 'wc 5 te' = 46
# Б bac85372; неги-браки: 'wc sv wc 5 sv' = 0xFE 50 Б 643ff46e (НОВЫЙ
# пин: bad word1 — emit 5 Б со слотом F1 = 0x00F00FF1 = 15732721
# DEFAULT WORK_CELL, W_Current не сменился); 'wc 5 sv wc sv' — stage1
# ПРИНИМАЕТ (55 Б ba8e42a3 0xFF, emit 10 Б — ОБА хвоста со слотом F8
# от stmt-1) — том молчит: v2 = 0 → PA = 3; bad d1 = 0xFE 45 Б
# 29ba6852 (= W-86/87); bad d2 = 0xFE 50 Б e8906fca (НОВЫЙ пин); bad
# word2 = 0xFE 45 Б 4ff7c705 (= W-86/87); bad word5 = 0xFE 50 Б
# e8afe9c6 (НОВЫЙ пин); bad word0/мусор = f3667180.
# EMIT: SV_TAIL1 (55 + BE32(cell[wc0] = слот F3+d1, НЕСУЩИЙ — chain1
# CHECK1)) -> SV_TAIL2 (55 + BE32(cell[wc2] = слот F3+d2, НЕСУЩИЙ —
# reslot CHECK2)) — по 12 ток ('nb 8 5' 'em' 'nb 3 0 8' 'sc' 'wc N'
# 'ow') — sv-хвост БЕЗ консты (в отличие от pr 24 ток) -> вердец ->
# отчёт (Token = 6: 'nb 6' 'wo' — токенов слоя ДО терминатора, точка
# не считается) -> SEAL/END. Честный дизайн:
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для SV_TAIL1;
#   прецедент W-87 CHECK1 C1) + pSv1 (word2 == LE2('sv') = 30323, PB =
#   wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для SV_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2) +
#   pSv2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('sv') = 30323 → wc7 — 's' = 0x73 в МЛАДШЕМ
# байте [урок W-65/W-79], 0x7673; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33sv.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('sv' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('sv' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-87 stash; в W-88 оба
                             # вида 'sv'): stash pEOF-ветки
                             # (15732723 = СЛОТ d1, 15732725 = СЛОТ d2 —
                             # трогать НЕЛЬЗЯ: TERM-фаза читает их после
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('sv') = 30323 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(30323), 'ne', 'wc', '7', 'sv',           # 'sv' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для SV_TAIL1 (карта probe88:
          # 'wc 7 sv …' → BE32(FA); 'wc 0 sv …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pSv1 = (word2 == LE2('sv'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pSv1

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
          # НЕСУЩИЙ для SV_TAIL2 (карта probe88: '… wc 7 sv' → BE32(FA);
          # '… wc 0 sv' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pSv2 = (word5 == LE2('sv'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSv2
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

# EMIT: SV_TAIL1 (честный хвост T3-'sv' стейтмента 1, карта probe88:
# 55 BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ), 5 Б — БЕЗ консты, урок
# W-79) -> SV_TAIL2 (честный хвост T3-'sv' стейтмента 2: 55 +
# BE32(cell[wc2] = слот F3+d2 НЕСУЩИЙ), 5 Б; честный emit базы probe88
# 5500f00ff85500f00ff8) -> вердец -> отчёт (Token = 6) -> SEAL/END
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
# SV_TAIL = честный хвост T3-'sv' стейтмента (закон probe88/probe79:
# 55 BE32(слот), 5 Б — БЕЗ консты): U8 0x55 ('nb 8 5' = 85₁₀ = 0x55
# [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ, 'nb 5 5' = 55₁₀ = 0x37
# НЕВЕРНО]) + BE32(слот) ('wc N ow') — sv = STORE 0x55; sp-хвост = 53
# BE32(слот) (0x53 = 83₁₀, урок W-80)
SV_TAIL1 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 0x55 (= 85 десят.)
            'wc', '0', 'ow']                    # BE32(слот F3+d1 — chain1)
SV_TAIL2 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',   # U8 0x55 (= 85 десят.)
            'wc', '2', 'ow']                    # BE32(слот F3+d2 — reslot)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + SV_TAIL1 \
       + SV_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe88\pos_wc14v3t33sv.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33sv tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
