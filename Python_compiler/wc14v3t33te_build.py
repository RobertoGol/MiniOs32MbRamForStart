# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d te wc d te'
# Shape-T3×T3-te (веха-23, спринт 66, W-86, TKT-052): ПЕРВЫЙ
# многостейтментный том word-компилятора — прорыв барьера «один
# стейтмент на том», первый шаг к стриму и истинной самосборке.
# База = wc14v3t34as-структура (кросс T3×T4-as, W-84) минус chain1/
# reslot/RELOAD2/AS_TAIL2 и минус F6-группы INIT; EMIT = TERM1 +
# TERM2. Честная карта probe86 (32 кейса, свежий stage1 на каждую
# цель): stage1 для T3×T3-te целей = 47 Б 0xFF Token 6, emit = 05 +
# 05 (2 Б); база 'wc 5 te wc 5 te' = c49e444f (пин probe77..probe85;
# честный полный hex probe86: header CRC dfbb6632 + emit 0505 + FF +
# BE32(6) + 20 нулей). ЕДИНЫЙ ЗАКОН ЭМИССИИ (карты probe77..probe86):
# каждый стейтмент эмитит [tail(kind)] + ([15 BE32(digit)] если есть
# digit-tail); T3×T3-te: ОБА хвоста константны (te = 05) => d1/d2
# ИНВАРЫ (карта probe86: 'wc 7 te wc 5 te' = 'wc 5 te wc 7 te' =
# 'wc 0 te wc 0 te' = 'wc 1 te wc 3 te' = 'wc 9 te wc 8 te' = база
# c49e444f) — слот/chain/reslot/RELOAD2 НЕ нужны вовсе.
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 te wc 5 te
# .' = c49e444f; мусор после точки честно игнорируется '… . 3' =
# c49e444f); VM допишет '.' на слово за концом потока (прецедент
# v9te/t3-shelf: гейт p4 = eq(word3, '.') на EOF-терминированных
# 'wc d te' — 10/10 в regr), слово ЗА терминатором = 0 — pEOF тома
# накрывает ОБА варианта: pEOF = eq(word6, 0) + eq(word6, 46) —
# арифметическая сумма ДВУХ сравнений через stash-ячейку 15732723
# ('wc 0'/F3 — СВОБОДНА в W-86: слота нет, F6-группа писала 'wc 3'
# = 15732726; полные адреса 'nb(PF), sv' и 'nb(PA), aa' честно
# проверены).
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pTe1+pTe2 = 2) + pEOF
# == 7 ('eq 7' — одноразрядный immediate); терминатор на ШЕСТОМ
# слове (ячейка WORD7 = 10485784 = word6). Ключ-развязки (том
# обязан молчать): T3×T4-te 'wc 5 te wc 5 te 3' = 52 Б df520cf9
# (W-77) — word6 = '3' → pEOF = 0; 3-stmt 'wc 5 te wc 5 te wc 5 te'
# = 48 Б 5cbeaa9b Token 9 — stage1 ПРИНИМАЕТ многостейтментные
# потоки (точка-вариант тот же 5cbeaa9b), том молчит: word6 = 'wc'
# → pEOF = 0; 4-stmt = 49 Б 40dc0e48 Token 12; T4×T3-te 'wc 5 te 3
# wc 5 te' = 52 Б 32448898 (НОВЫЙ пин) — word3 = '3' → p0-2 bad.
# НОВЫЕ пины probe86: pr-T3-хвост = 54 BE32(0x3F0050C0 КОНСТА) +
# BE32(слот F3+d1) 9 Б ('wc 5 pr wc 5 te' = 55 Б 9ae11899, emit
# 543f0050c000f00ff805; T3-pr-single 'wc 5 pr' = 54 Б 61957c4c —
# pr-хвост и в одиночке; 'wc 5 te wc 5 pr' = 55 Б c0596f7a = 05 +
# pr-хвост; 'wc 5 pr wc 5 pr' = 63 Б 93d24c79); T4×T3-pr 'wc 5 te 3
# wc 5 pr' = 60 Б 26a8b48c; T3+T4+сирота 'wc 5 te wc 5 te 3 3' = 57
# Б 6a6f0a94 (Token 8); T4×T4+точка 'wc 5 te 3 wc 5 te 3 .' =
# 45188fc1 (= T4×T4-te база W-68); 'wc 5 te wc te' — stage1
# ПРИНИМАЕТ (47 Б c6ac37a7 0xFF, emit 0505) — том молчит: v2 = 0 →
# PA = 3; старые пины совпали: T3×T4-pr 8f5455db, T4×T4-te
# 45188fc1, T3-single bac85372, сирота a3bac192, bad d1 29ba6852,
# bad d2 06448daf (= W-85), bad word2 4ff7c705, bad word0/мусор
# f3667180; 'wc te wc 5 te' = 0xFE 46 Б 03928005 (НОВЫЙ пин); 'wc 5
# te wc 5 xx' = 0xFE 46 Б d0059999 (= W-85).
# EMIT: TERM1 (05) -> TERM2 (05) — по 4 list-entries ('nb 5', 'em',
# 'nb 3 0 8', 'sc') -> вердец -> отчёт (Token = 6: 'nb 6' 'wo' —
# токенов слоя ДО терминатора, точка не считается) -> SEAL/END.
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('te' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс (VM-память = 0 изначально)
WC3 = 15732723               # 'wc 0'/F3 — СВОБОДНА в W-86 (слота нет):
                             # stash pEOF-ветки EOF (eq word6 == 0)
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
        nb(46), 'ne', 'wc', '8', 'sv']              # '.' (терминатор)
        # F6-группа ('ow' = 30575) НЕ нужна: в T3×T3-te НЕТ ow-хвоста

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
          # D1: pTe1 = (word2 == LE2('te'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pTe1
          # НЕТ chain1 (d1-ИНВАР: te-хвост константен, слот не нужен)

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (as-аккумулятор)
          nb(WORD4), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word4 (d2): bad3 в PF.
          # d2-ИНВАР: te-хвост stmt-2 константен — слот НЕ читается
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # D2: pTe2 = (word5 == LE2('te'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe2
          # НЕТ reslot (слот не нужен), НЕТ digit-block d32

# НЕТ RELOAD2: digit-tail d32 не существует в T3×T3 (word6 =
# терминатор слоя)

# F2/G2: pEOF = (word6 == 0 ИЛИ word6 == '.') — арифметическая сумма
# ДВУХ сравнений через stash-ячейку WC3 = 15732723 ('nb(WC3), sv' и
# 'nb(WC3), aa' — честно проверенные формы 'nb(PF), sv'/'nb(PA),
# aa'); терминатор слоя T3×T3 на ШЕСТОМ слове (WORD7 = 10485784):
# ключ-развязка — у T3×T4-te word6 = '3' → pEOF = 0; у 3/4-stmt
# word6 = 'wc' → pEOF = 0; у T4×T3 word6 = 'te'. Затвор: PA (4) + PD
# (2) + pEOF == 7 ('eq 7')
TAIL_CHECK = [nb(WORD7), 'va', 'eq', '0',       # acc = eq(word6, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(WC3), 'sv',                    # stash → cell[15732723]
              nb(WORD7), 'va', nb(PC), 'cp',    # acc = eq(word6, '.')
              nb(WC3), 'aa',                    # acc += stash
              'eq', '7',
              'if']

# EMIT: TERM1 (05 — честный хвост T3-'te' стейтмента 1) -> TERM2 (05
# — честный хвост T3-'te' стейтмента 2; карта probe86: emit = 0505,
# ОБА хвоста константны, d1/d2 инвары) -> вердец -> отчёт (Token = 6)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
TERM1 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-1 te)
TERM2 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-2 te)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + TERM1 \
       + TERM2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe86\pos_wc14v3t33te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
