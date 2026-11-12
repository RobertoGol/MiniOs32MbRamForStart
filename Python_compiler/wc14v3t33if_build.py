# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d if wc d if'
# Shape-T3×T3-if (веха-23, спринт 72, W-92, TKT-052): СТРИМ — седьмой
# вид многостейтментного тома, ОБА хвоста КОНСТАНТНЫ (if-хвост 5 Б —
# U8 0x06 + BE32(0x14 = 20 КОНСТАНТА), закон W-74) => d1/d2 ИНВАРЫ —
# слот НЕ несущий (особый случай W-74: BE32 патча = 0x14 НЕ зависит
# ни от d1, ни от d2) — как у te-тома W-86.
# База = wc14v3t33te-структура (W-86) + честная карта probe92 (44
# кейса, свежий stage1 на каждую цель): stage1 для T3×T3-if целей =
# 55 Б 0xFF Token 6, emit = [if-T3-хвост] ×2 = [06 BE32(0x14 = 20
# КОНСТАНТА)] ×2 = 10 Б; база 'wc 5 if wc 5 if' = 98a0ab23 (честный
# полный hex probe92: header CRC a72d12f3 + emit 06000000140600000014
# + FF + BE32(6) + 20 нулей). ЕДИНЫЙ ЗАКОН ЭМИССИИ (карты
# probe77..probe92): каждый стейтмент эмитит [tail(kind)] + ([15
# BE32(digit)] если есть digit-tail); T3×T3-if: ОБА хвоста константны
# => d1/d2 ИНВАРЫ (карта probe92: 'wc 7 if wc 5 if' = 'wc 5 if wc 7
# if' = 'wc 7 if wc 7 if' = 'wc 0 if wc 0 if' = 'wc 1 if wc 3 if' =
# 'wc 9 if wc 8 if' = точка = мусор-после-точки = база 98a0ab23 — ВСЕ
# 8 носителей = база, честное доказательство инваров W-74) — слот/
# chain/reslot/RELOAD2 НЕ нужны вовсе; tracked-цели W-92 дают ОДИН
# md5 (честный инвариант W-74 — НЕ ошибка, прецедент W-86: все три
# c49e444f).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 if wc 5 if .'
# = 98a0ab23; мусор после точки честно игнорируется '… . 3' =
# 98a0ab23); VM допишет '.' на слово за концом потока (прецедент
# v9te/t3-shelf: гейт p4 = eq(word3, '.') на EOF-терминированных
# 'wc d te' — 10/10 в regr), слово ЗА терминатором = 0 — pEOF тома
# накрывает ОБА варианта: pEOF = eq(word6, 0) + eq(word6, 46) —
# арифметическая сумма ДВУХ сравнений через stash-ячейку 15732723
# ('wc 0'/F3 — СВОБОДНА в W-92: слота нет, как в W-86; полные адреса
# 'nb(PF), sv' и 'nb(PA), aa' честно проверены).
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pIf1+pIf2 = 2) + pEOF
# == 7 ('eq 7' — одноразрядный immediate); терминатор на ШЕСТОМ
# слове (ячейка WORD7 = 10485784 = word6). Ключ-развязки (том
# обязан молчать, ВСЕ пины сняты честно): te/sv/sp/vw/va/pr-смеси —
# stage1 ПРИНИМАЕТ ('wc 5 if wc 5 te' = 51 Б 9b975402 — НОВЫЙ пин:
# if-хвост с te-соседом даёт BE32(0x19 = 25) ВМЕСТО 0x14!; 'wc 5 te
# wc 5 if' = 51 Б 8f0cfe17 = 05 + 0600000014; 'wc 5 if wc 5 sv' = 55
# Б a8a01a4a = 0600000014 + 55BE32; 'wc 5 sv wc 5 if' = 55 Б
# 0680d9a0; 'wc 5 if wc 5 sp' = 55 Б 167ac2a6; 'wc 5 sp wc 5 if' = 55
# Б 3785e6ce; 'wc 5 if wc 5 vw' = 54 Б ddc6c78a = 0600000014 + BE32;
# 'wc 5 vw wc 5 if' = 54 Б bc3c67cf; 'wc 5 if wc 5 va' = 56 Б
# bb34f87f = 0600000014 + 1219BE32; 'wc 5 va wc 5 if' = 56 Б
# 9d91f860; 'wc 5 if wc 5 pr' = 59 Б f5a7aa0b = 0600000014 + pr-
# хвост; 'wc 5 pr wc 5 if' = 59 Б 422e46b5; 'wc 5 te wc 5 te' = 47 Б
# c49e444f база W-86) — том молчит: pIf2/pIf1/обе = 0; 3-stmt
# if-поток 'wc 5 if wc 5 if wc 5 if' = 60 Б eb8ecda2 Token 9 (emit
# 15 Б = 3 if-хвоста 0600000014×3; точка-вариант тот же eb8ecda2) —
# том молчит: word6 = 'wc' → pEOF = 0; 4-stmt if-поток — stage1 САМ
# БРАКУЕТ (0xFE 60 Б ebe049f9, emit 15 Б = 3 хвоста, rep Token 0x0b
# — НОВЫЙ пин W-92: 4 va-стейтмента stage1 принимает [917128ff], 4
# if-стейтмента НЕТ; точка-вариант тот же ebe049f9) — том молчит;
# T3-if×T4-if 'wc 5 if wc 5 if 3' = 60 Б 8b4670f1 (НОВЫЙ пин: emit
# 15 Б = 0600000014×2 + 15 BE32(3)) — word6 = '3' → pEOF = 0;
# T4-if×T3-if 'wc 5 if 3 wc 5 if' = 60 Б 0f083900 (НОВЫЙ пин, emit
# 15 Б) — word3 = '3' → p0-2 bad; T4×T4-if 'wc 5 if 3 wc 5 if 3' =
# 65 Б 0e1dd19c (НОВЫЙ пин, emit 20 Б; точка-вариант тот же
# 0e1dd19c); 'wc 5 if wc 5 if 3 3' = 65 Б 87cd838d (НОВЫЙ пин, Token
# 8, emit 20 Б = 0600000014×2 + 15 BE32(3)×2); 'wc 5 if wc 5 if if'
# = 60 Б 8af5aa63 (НОВЫЙ пин: word6 = 'if', emit 15 Б = 3 if-хвоста)
# — том молчит: pEOF = 0; singles/сироты: 'wc 5 if' = 50 Б c9f750ed
# (пин W-83/probe83 — СОВПАЛ, emit 5 Б), сирота 'wc 5 if wc 5' = 50
# Б 87b4ae50 (НОВЫЙ пин: emit 5 Б), 'wc 5 vw' = 49 Б 00ce976e (пин
# probe90/91), 'wc 5 sv' = 50 Б 6a16ae85 (пин probe88..91), 'wc 5
# te' = 46 Б bac85372; неги-браки: 'wc if wc 5 if' = 0xFE 50 Б
# 7b0a5de7 (НОВЫЙ пин: bad word1 — emit 5 Б КОНСТАНТЕН и в браке,
# слота нет); 'wc 5 if wc if' — stage1 ПРИНИМАЕТ (55 Б d41440c5 0xFF,
# emit 0600000014×2 — ОБА хвоста константны) — том молчит: v2 = 0 →
# PA = 3; bad d1 = 0xFE 45 Б 29ba6852 (= W-86..91); bad d2 = 0xFE 50
# Б 84001270 (НОВЫЙ пин); bad word2 = 0xFE 45 Б 4ff7c705 (= W-86..91);
# bad word5 = 0xFE 50 Б 98def804 (НОВЫЙ пин); bad word0/мусор =
# f3667180. Мини-карта probe92b (18 кейсов, te-структуры, свежий
# stage1 на каждую цель): 'wc 7 if wc 5 te' = 'wc 5 if wc 7 te' = 'wc
# 5 if wc 0 te' = 51 Б 9b975402 (BE32 0x19 НЕ зависит от d1/d2), 'wc
# 5 if wc 5 te 3' = 56 Б aba7ebb2 (0x19, emit 11 Б), 'wc 5 if 3 wc 5
# te' = 56 Б 6b3321f3 (НОВЫЙ пин: T4-if с te-соседом даёт BE32(0x1e =
# 30)!, emit 060000001e1500000003 05), 'wc 5 if 3 wc 5 te 3' = 61 Б
# 99d2e93a (0x1e), 'wc 5 te wc 5 if 3' = 56 Б 1d69a38a (пин probe83 —
# СОВПАЛ, emit 05 0600000014 15BE32(3) — if ПОСЛЕДНИЙ → 0x14), 'wc 5
# if wc 5 te .' = 9b975402 (точка = та же), 'wc 5 if wc 5 te wc 5 te'
# = 52 Б 53c58520 (НОВЫЙ пин: 0x1a = 26), 'wc 5 if wc 5 te wc 5 if' =
# 56 Б 0e9c55d2 (НОВЫЙ пин: 0x19 ОБА if-хвоста), 'wc 5 if wc 5 sv wc
# 5 te' = 56 Б 8e0adf7f (НОВЫЙ пин: 0x1e), 'wc 5 if wc 5 if wc 5 if .'
# = eb8ecda2 (контроль), 'wc 5 if wc 5 if wc 5 if 3' = 65 Б 4c98f613
# (НОВЫЙ пин: Token 10, emit 20 Б = 0600000014×3 + 15 BE32(3)), 4-stmt
# + точка = ebe049f9 (тот же FAIL), 'wc 5 if wc 5 if wc 5 te' = 56 Б
# f83a4186 (НОВЫЙ пин: 0x1e ОБА if-хвоста), 'wc 5 if wc 5 if wc 5 va'
# = 61 Б d0403724 (НОВЫЙ пин: 0x14 ОБА — НЕ te-сосед!), 'wc 5 if wc 5
# pr' = f5a7aa0b (контроль 0x14) — ВСЕ te-структуры = неги (том
# молчит: pIf2/pIf3-структуры не проходят затвор). ИТОГ ЧЕСТНОЙ
# КАРТЫ: в ЧИСТОМ if-контексте BE32 = 0x14 КОНСТА всегда (все 9
# целей, 3-stmt, T4×T3, T4×T4, single, сирота); te-сосед в потоке
# меняет BE32 stage1 (0x19/0x1a/0x1e — НОВЫЙ факт W-92) — эти формы
# НЕ входят в приёмный класс тома (все неги, том молчит).
# EMIT: IF_TAIL1 (06 + BE32(0x14 = 20 КОНСТАНТА) — 'nb 2 0' 'wo' =
# pending-nb BE32-вывод КОНСТАНТЫ [прецедент W-83]) -> IF_TAIL2 (тот
# же константный хвост) — по 6 ток ('nb 6' 'em' 'nb 3 0 8' 'sc' 'nb 2
# 0' 'wo') — if-хвост 5 Б (закон W-74) -> вердец -> отчёт (Token = 6:
# 'nb 6' 'wo' — токенов слоя ДО терминатора, точка не считается) ->
# SEAL/END. Честный дизайн (= W-86 te-структура, слот не нужен):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1, значение СБРАСЫВАЕТСЯ —
#   d1-ИНВАР) + pIf1 (word2 == LE2('if') = 26217, PB = wc 7, PD = ) —
#   БЕЗ digit-block d31 (word3 = 'wc' stmt-2) — НЕТ chain1.
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4, значение СБРАСЫВАЕТСЯ —
#   d2-ИНВАР) + pIf2 (word5 == PB, PD += ) — БЕЗ digit-block d32 —
#   НЕТ reslot (слот не нужен).
#   НЕТ RELOAD2: digit-tail d32 не существует в T3×T3 (word6 =
#   терминатор слоя).
# INIT = 5 групп (F3_MINUS_48 → wc0 [группа-наследник W-86-структуры,
# ячейка далее не читается]; F4 LE2('wc') = 25463 → wc1; SRC_BUFFER →
# wc4; PB LE2('if') = 26217 → wc7 — 'i' в МЛАДШЕМ байте [урок
# W-65/W-67], 0x6669; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33if.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('if' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('if' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0)
WC3 = 15732723               # 'wc 0'/F3 — СВОБОДНА в W-92 (слота нет,
                             # как в W-86): stash pEOF-ветки EOF
                             # (eq word6 == 0)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('if') = 26217 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(26217), 'ne', 'wc', '7', 'sv',           # 'if' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv']              # '.' (терминатор)
        # F6-группа ('ow' = 30575) НЕ нужна: в T3×T3-if НЕТ ow-хвоста
        # (BE32(0x14) константен — 'nb 2 0' 'wo', не 'wc N ow')

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = скан T3-стейтмента 1 (слова 0..2; 3 токена — БЕЗ digit-
# block d31: word3 = 'wc' второго стейтмента)
CHECK1 = [nb(SRC_BUFFER), 'va',
          nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
          'wc', '6', 'sv',              # PA = p0
          # B1: честный digit-block (v2d, без правок): bad в PF.
          # d1-ИНВАР: if-хвост stmt-1 константен — значение СБРАСЫВАЕТСЯ
          nb(SRC_WORD2), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid1 = (bad == F5=0)
          'wc', '6', 'as',              # PA += valid1
          # D1: pIf1 = (word2 == LE2('if'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pIf1
          # НЕТ chain1 (d1-ИНВАР: if-хвост константен, слот не нужен)

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = терминатор слоя)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (as-аккумулятор)
          nb(WORD4), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word4 (d2): bad3 в PF.
          # d2-ИНВАР: if-хвост stmt-2 константен — значение СБРАСЫВАЕТСЯ
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # D2: pIf2 = (word5 == LE2('if'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pIf2
          # НЕТ reslot (слот не нужен), НЕТ digit-block d32

# НЕТ RELOAD2: digit-tail d32 не существует в T3×T3 (word6 =
# терминатор слоя)

# F2/G2: pEOF = (word6 == 0 ИЛИ word6 == '.') — арифметическая сумма
# ДВУХ сравнений через stash-ячейку WC3 = 15732723 ('nb(WC3), sv' и
# 'nb(WC3), aa' — честно проверенные формы 'nb(PF), sv'/'nb(PA),
# aa'); терминатор слоя T3×T3 на ШЕСТОМ слове (WORD7 = 10485784):
# ключ-развязка — у T3×T4-if word6 = '3' → pEOF = 0; у 3/4-stmt
# word6 = 'wc' → pEOF = 0; у T4×T3 word6 = 'if'. Затвор: PA (4) + PD
# (2) + pEOF == 7 ('eq 7')
TAIL_CHECK = [nb(WORD7), 'va', 'eq', '0',       # acc = eq(word6, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(WC3), 'sv',                    # stash → cell[15732723]
              nb(WORD7), 'va', nb(PC), 'cp',    # acc = eq(word6, '.')
              nb(WC3), 'aa',                    # acc += stash
              'eq', '7',
              'if']

# EMIT: IF_TAIL1 (06 + BE32(0x14 = 20 КОНСТАНТА) — честный хвост
# T3-'if' стейтмента 1, карта probe92: emit = 06000000140600000014,
# ОБА хвоста константны, d1/d2 инвары) -> IF_TAIL2 (тот же
# константный хвост T3-'if' стейтмента 2) -> вердец -> отчёт (Token
# = 6)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
# IF_TAIL = честный хвост T3-'if' стейтмента (закон W-74: 06 +
# BE32(0x14 = 20 КОНСТАНТА), 5 Б): U8 0x06 ('nb 6' [nb-литералы
# ДЕСЯТИЧНЫЕ — урок probe57/W-64]) + BE32(20 КОНСТА) ('nb 2 0' 'wo' =
# pending-nb BE32-вывод КОНСТАНТЫ — прецедент W-83)
IF_TAIL1 = ['nb 6', 'em', 'nb 3 0 8', 'sc',     # U8 6 (0x06)
            'nb 2 0', 'wo']                     # BE32(0x14 = 20 КОНСТА)
IF_TAIL2 = ['nb 6', 'em', 'nb 3 0 8', 'sc',     # U8 6 (0x06)
            'nb 2 0', 'wo']                     # BE32(0x14 = 20 КОНСТА)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + IF_TAIL1 \
       + IF_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe92\pos_wc14v3t33if.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33if tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
