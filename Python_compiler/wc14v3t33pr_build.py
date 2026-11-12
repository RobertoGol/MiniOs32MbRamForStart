# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d pr wc d pr'
# Shape-T3×T3-pr (веха-23, спринт 67, W-87, TKT-052): СТРИМ ОТКРЫТ —
# второй вид многостейтментного тома, оба хвоста НЕСУЩИЕ (слоты d1/d2
# входят в emit) => d1/d2 НЕТ инваров — в отличие от te-тома W-86.
# База = wc14v3t33te-структура (W-86) + честная карта probe87 (32
# кейса, свежий stage1 на каждую цель): stage1 для T3×T3-pr целей =
# 63 Б 0xFF Token 6, emit = [pr-T3-хвост] ×2 = [54 BE32(0x3F0050C0 =
# 1056985280 КОНСТА) + BE32(слот F3+d)] ×2 = 18 Б; база 'wc 5 pr wc 5
# pr' = 93d24c79 (пин probe86; честный полный hex probe87: header CRC
# 45879e04 + emit 543f0050c000f00ff8543f0050c000f00ff8 + FF + BE32(6)
# + 20 нулей). **СЛОТ НЕСУЩИЙ В ОБОИХ ХВОСТАХ** (карта probe87:
# 'wc 7 pr wc 5 pr' = 63 Б 02089644, emit 543f0050c000f00ffa…f8 —
# слот1 = FA = F3+d1; 'wc 5 pr wc 7 pr' = 9707345d — слот2 = FA =
# F3+d2; 'wc 7 pr wc 7 pr' = 0144dd04 — FA FA; 'wc 0 pr wc 0 pr' =
# c0d5c83c — F3 F3; 'wc 1 pr wc 3 pr' = 4f47a406 — F4 F6; 'wc 9 pr wc
# 8 pr' = 76d751a5 — FC FB) — три tracked-цели W-87 ДАЮТ ТРИ РАЗНЫЕ
# md5 (честное доказательство несущих слотов; в W-86 все три были
# c49e444f — инвары). ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база
# ('wc 5 pr wc 5 pr .' = 93d24c79; мусор после точки '… . 3' = база);
# слово ЗА терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) —
# сумма ДВУХ сравнений через stash-ячейку **STASH = 15732726 (wc3)**
# (В W-87 НЕЛЬЗЯ 15732723: там СЛОТ — chain1/reslot пишут адреса
# слотов F3+d1/F3+d2, TERM1/TERM2 читают их 'wc 0 ow'/'wc 2 ow' в
# EMIT-фазе ПОСЛЕ TAIL_CHECK; wc3 свободна — в W-84 там был 'as'-
# конст F6, в W-87 оба вида 'pr' → конста одна PB; формы 'nb(STASH),
# sv' / 'nb(STASH), aa' — честно проверенные 'nb(PF), sv'/'nb(PA),
# aa'). G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pPr1+pPr2 = 2) +
# pEOF == 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-
# tail d32 не существует в T3×T3: word6 = терминатор слоя). Ключ-
# развязки (том обязан молчать, ВСЕ пины сняты честно): te/pr-смеси —
# stage1 ПРИНИМАЕТ ('wc 5 pr wc 5 te' = 55 Б 9ae11899 = pr-хвост + 05,
# пин probe86; 'wc 5 te wc 5 pr' = 55 Б c0596f7a = 05 + pr-хвост;
# 'wc 5 te wc 5 te' = 47 Б c49e444f база W-86) — том молчит: pPr2/1/обе
# = 0; 3/4-stmt pr-потоки — stage1 ПРИНИМАЕТ ('wc 5 pr wc 5 pr wc 5
# pr' = 72 Б ca3af6f2 Token 9, emit 27 Б = 3 pr-хвоста, точка-вариант
# тот же ca3af6f2; 4-stmt = 81 Б 34f4a890, emit 36 Б) — том молчит:
# word6 = 'wc' → pEOF = 0; 'wc 5 pr wc 5 pr 3' = 68 Б 3396f4ac (НОВЫЙ
# пин: T3-pr×T3pr+digit, emit 23 Б) — word6 = '3' → pEOF = 0; 'wc 5 pr
# 3 wc 5 pr' = 68 Б 386f20a5 (НОВЫЙ пин: T4-pr×T3-pr, emit 23 Б) —
# word3 = '3' → p0-2 bad; 'wc 5 pr 3 wc 5 pr 3' = 73 Б a5fa7400 (НОВЫЙ
# пин: T4×T4-pr, emit 28 Б; точка-вариант тот же a5fa7400); 'wc 5 pr
# wc 5 pr 3 3' = 73 Б 89aa4c61 (НОВЫЙ пин, Token 8) — word6 = '3';
# 'wc 5 pr wc 5 pr pr' = 72 Б 42545e00 (НОВЫЙ пин: word6 = 'pr', emit
# 27 Б = 3 pr-хвоста) — том молчит: pEOF = 0; singles/сироты 'wc 5 pr'
# = 54 Б 61957c4c (пин probe86), 'wc 5 pr wc 5' = 54 Б 2d2ebfbf (НОВЫЙ
# пин: сирота-цифра, emit 9 Б), 'wc 5 te' = 46 Б bac85372; неги-браки:
# 'wc pr wc 5 pr' = 0xFE 54 Б bd98dd90 (НОВЫЙ пин: bad word1 — emit
# 9 Б со слотом F1 = 0x00F00FF1 = 15732721 DEFAULT WORK_CELL, W_Current
# не сменился); 'wc 5 pr wc pr' — stage1 ПРИНИМАЕТ (63 Б e60ab79f
# 0xFF, emit 18 Б — ОБА хвоста со слотом F8 от stmt-1) — том молчит:
# v2 = 0 → PA = 3; bad d1 = 0xFE 45 Б 29ba6852 (= W-86/te); bad d2 =
# 0xFE 54 Б 53097fac (НОВЫЙ пин); bad word2 = 0xFE 45 Б 4ff7c705 (=
# W-86); bad word5 = 0xFE 54 Б ddb5b70d (НОВЫЙ пин); bad word0/мусор
# = f3667180.
# EMIT: PR_TAIL1 (54 + BE32(порт-КОНСТА) + BE32(cell[wc0] = F3+d1,
# НЕСУЩИЙ — chain1 CHECK1) -> PR_TAIL2 (54 + BE32(порт-КОНСТА) +
# BE32(cell[wc2] = F3+d2, НЕСУЩИЙ — reslot CHECK2)) — по 26 ток ('nb
# 8 4' 'em' 'nb 3 0 8' 'sc' 'nb 1 0 5 6 9 8 5 2 8 0' 'wo' 'wc N ow')
# -> вердец -> отчёт (Token = 6: 'nb 6' 'wo' — токенов слоя ДО
# терминатора, точка не считается) -> SEAL/END. Честный дизайн:
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для PR_TAIL1;
#   прецедент W-84 CHECK1 C1 — там не несущий, тут несущий) + pPr1
#   (word2 == LE2('pr') = 29296, PB = wc 7, PD = ) — БЕЗ digit-block
#   d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для PR_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2) +
#   pPr2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('pr') = 29296 → wc7 — 'p' = 0x70 в МЛАДШЕМ
# байте [урок W-65/W-67], 0x7270; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33pr.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('pr' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('pr' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-84 'as'-конст F6;
                             # в W-87 оба вида 'pr'): stash pEOF-ветки
                             # (в W-86 stash был 15732723/wc0 — тут ЗАПРЕЩЕНО:
                             # wc0 = слот d1)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('pr') = 29296 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29296), 'ne', 'wc', '7', 'sv',           # 'pr' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для PR_TAIL1 (карта probe87:
          # 'wc 7 pr …' → BE32(FA); 'wc 0 pr …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pPr1 = (word2 == LE2('pr'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pPr1

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
          # НЕСУЩИЙ для PR_TAIL2 (карта probe87: '… wc 7 pr' → BE32(FA);
          # '… wc 0 pr' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pPr2 = (word5 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr2
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

# EMIT: PR_TAIL1 (честный хвост T3-'pr' стейтмента 1, карта probe87:
# 54 BE32(0x3F0050C0 КОНСТА) + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ),
# 9 Б) -> PR_TAIL2 (честный хвост T3-'pr' стейтмента 2: 54 +
# BE32(0x3F0050C0 КОНСТА) + BE32(cell[wc2] = слот F3+d2 НЕСУЩИЙ), 9 Б;
# честный emit базы probe87 543f0050c000f00ff8543f0050c000f00ff8) ->
# вердец -> отчёт (Token = 6) -> SEAL/END
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
# PR_TAIL = честный хвост T3-'pr' стейтмента (закон probe87/probe86/
# probe78: 54 BE32(0x3F0050C0 КОНСТА) + BE32(слот), 9 Б): U8 0x54
# ('nb 8 4' = 84₁₀ = 0x54 [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ,
# 'nb 5 4' = 54₁₀ = 0x36 НЕВЕРНО]) + BE32(0x3F0050C0 = 1056985280
# КОНСТА) ('nb 1 0 5 6 9 8 5 2 8 0' 'wo') + BE32(слот) ('wc N ow')
PR_TAIL1 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',   # U8 0x54 (= 84 десят.)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',     # BE32(0x3F0050C0 КОНСТА)
            'wc', '0', 'ow']                    # BE32(слот F3+d1 — chain1)
PR_TAIL2 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',   # U8 0x54 (= 84 десят.)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',     # BE32(0x3F0050C0 КОНСТА)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + PR_TAIL1 \
       + PR_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe87\pos_wc14v3t33pr.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33pr tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
