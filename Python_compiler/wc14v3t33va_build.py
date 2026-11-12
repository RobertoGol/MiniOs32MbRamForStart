# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d va wc d va'
# Shape-T3×T3-va (веха-23, спринт 71, W-91, TKT-052): СТРИМ — шестой
# вид многостейтментного тома, оба хвоста НЕСУЩИЕ (слоты d1/d2 входят
# в emit) => d1/d2 НЕТ инваров — как у pr/sv/sp/vw-томов
# W-87/W-88/W-89/W-90 (va-хвост 6 Б — U8 0x12 + U8 0x19 + BE32(слот),
# закон W-73).
# База = wc14v3t33vw-структура (W-90) + честная карта probe91 (42
# кейса, свежий stage1 на каждую цель): stage1 для T3×T3-va целей =
# 57 Б 0xFF Token 6, emit = [va-T3-хвост] ×2 = [12 19 BE32(слот
# F3+d)] ×2 = 12 Б; база 'wc 5 va wc 5 va' = 8479bb87 (честный
# полный hex probe91: header CRC 87c5d320 + emit 121900f00ff8121900
# f00ff8 + FF + BE32(6) + 20 нулей). **СЛОТ НЕСУЩИЙ В ОБОИХ ХВОСТАХ**
# (карта probe91: 'wc 7 va wc 5 va' = 57 Б 7cc588d2, emit
# 121900f00ffa121900f00ff8 — слот1 = FA = F3+d1; 'wc 5 va wc 7 va' =
# a4423b7a — слот2 = FA = F3+d2; 'wc 7 va wc 7 va' = 07f2c382 — FA
# FA; 'wc 0 va wc 0 va' = e745eee0 — F3 F3; 'wc 1 va wc 3 va' =
# aaa10b55 — F4 F6; 'wc 9 va wc 8 va' = 6f76eaca — FC FB) — три
# tracked-цели W-91 ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство
# несущих слотов).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 va wc 5 va .'
# = 8479bb87; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = 15732726 (wc3)** (В W-91
# НЕЛЬЗЯ 15732723/15732725: там СЛОТЫ d1/d2 — chain1/reslot пишут
# адреса слотов F3+d1/F3+d2, TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'
# ПОСЛЕ TAIL_CHECK; wc3 свободна — в W-87..W-90 тоже stash; формы
# 'nb(STASH), sv'/'nb(STASH), aa' — честно проверенные
# 'nb(PF), sv'/'nb(PA), aa').
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pVa1+pVa2 = 2) + pEOF ==
# 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-tail d32
# не существует в T3×T3: word6 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): te/pr/sv/sp/vw/va-
# смеси — stage1 ПРИНИМАЕТ ('wc 5 va wc 5 te' = 52 Б b58c86d8 =
# 1219BE32 + 05; 'wc 5 te wc 5 va' = 52 Б 1eb39153 = 05 + 1219BE32;
# 'wc 5 va wc 5 sv' = 56 Б 4822f462 = 1219BE32 + 55; 'wc 5 sv wc 5
# va' = 56 Б 3ab771dd = 55 + 1219BE32; 'wc 5 va wc 5 sp' = 56 Б
# d9166287 = 1219BE32 + 53; 'wc 5 sp wc 5 va' = 56 Б 1f4468e8 = 53 +
# 1219BE32; 'wc 5 va wc 5 vw' = 55 Б 7c27ea4d = 1219BE32 + BE32; 'wc
# 5 vw wc 5 va' = 55 Б e1c55c5c = BE32 + 1219BE32; 'wc 5 va wc 5 pr'
# = 60 Б 5bc7a283 = 1219BE32 + pr-хвост; 'wc 5 pr wc 5 va' = 60 Б
# 76abd04d = pr-хвост + 1219BE32; 'wc 5 te wc 5 te' = 47 Б c49e444f
# база W-86) — том молчит: pVa2/pVa1/обе = 0; 3/4-stmt va-потоки —
# stage1 ПРИНИМАЕТ ('wc 5 va wc 5 va wc 5 va' = 63 Б 61c72bef Token
# 9, emit 18 Б = 3 va-хвоста, точка-вариант тот же 61c72bef; 4-stmt =
# 69 Б 917128ff, emit 24 Б) — том молчит: word6 = 'wc' → pEOF = 0;
# 'wc 5 va wc 5 va 3' = 62 Б 223e6120 (НОВЫЙ пин: T3-va×T4-va, emit
# 17 Б = 1219BE32×2 + digit-tail 15 00000003) — word6 = '3' → pEOF =
# 0; 'wc 5 va 3 wc 5 va' = 62 Б a6cf502c (НОВЫЙ пин: T4-va×T3-va,
# emit 17 Б) — word3 = '3' → p0-2 bad; 'wc 5 va 3 wc 5 va 3' = 67 Б
# 66ed9dd3 (НОВЫЙ пин: T4×T4-va, emit 22 Б; точка-вариант тот же
# 66ed9dd3); 'wc 5 va wc 5 va 3 3' = 67 Б f2174453 (НОВЫЙ пин, Token
# 8, emit 22 Б); 'wc 5 va wc 5 va va' = 63 Б 8db7af23 (НОВЫЙ пин:
# word6 = 'va', emit 18 Б = 3 va-хвоста) — том молчит: pEOF = 0;
# singles/сироты 'wc 5 va' = 51 Б d4766ef5 (НОВЫЙ пин: emit 6 Б),
# сирота 'wc 5 va wc 5' = 51 Б 7b987a13 (НОВЫЙ пин: emit 6 Б), 'wc 5
# vw' = 49 Б 00ce976e (пин probe90), 'wc 5 sv' = 50 Б 6a16ae85 (пин
# probe88/89/90), 'wc 5 te' = 46 Б bac85372; неги-браки: 'wc va wc 5
# va' = 0xFE 51 Б cdb8c657 (НОВЫЙ пин: bad word1 — emit 6 Б со
# слотом F1 = 0x00F00FF1 = 15732721 DEFAULT WORK_CELL, W_Current не
# сменился); 'wc 5 va wc va' — stage1 ПРИНИМАЕТ (57 Б df212a2f 0xFF,
# emit 12 Б — ОБА хвоста со слотом F8 от stmt-1) — том молчит: v2 =
# 0 → PA = 3; bad d1 = 0xFE 45 Б 29ba6852 (= W-86..90); bad d2 =
# 0xFE 51 Б f5435378 (НОВЫЙ пин); bad word2 = 0xFE 45 Б 4ff7c705 (=
# W-86..90); bad word5 = 0xFE 51 Б 69f882df (НОВЫЙ пин); bad
# word0/мусор = f3667180.
# EMIT: VA_TAIL1 (12 19 + BE32(cell[wc0] = слот F3+d1, НЕСУЩИЙ —
# chain1 CHECK1)) -> VA_TAIL2 (12 19 + BE32(cell[wc2] = слот F3+d2,
# НЕСУЩИЙ — reslot CHECK2)) — по 11 ток ('nb 1 8' 'em' 'nb 3 0 8'
# 'sc' 'nb 2 5' 'em' 'nb 3 0 8' 'sc' 'wc N' 'ow') — va-хвост 6 Б
# (закон W-73: U8 0x12 = 18₁₀ + U8 0x19 = 25₁₀ + BE32(слот)) ->
# вердец -> отчёт (Token = 6: 'nb 6' 'wo' — токенов слоя ДО
# терминатора, точка не считается) -> SEAL/END. Честный дизайн:
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для
#   VA_TAIL1; прецедент W-87..W-90 CHECK1 C1) + pVa1 (word2 ==
#   LE2('va') = 24950, PB = wc 7, PD = ) — БЕЗ digit-block d31
#   (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для VA_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2)
#   + pVa2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('va') = 24950 → wc7 — 'v' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x6176; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33va.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('va' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('va' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-87..W-90 stash; в W-91
                             # оба вида 'va'): stash pEOF-ветки
                             # (15732723 = СЛОТ d1, 15732725 = СЛОТ d2 —
                             # трогать НЕЛЬЗЯ: TERM-фаза читает их после
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('va') = 24950 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(24950), 'ne', 'wc', '7', 'sv',           # 'va' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для VA_TAIL1 (карта probe91:
          # 'wc 7 va …' → BE32(FA); 'wc 0 va …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pVa1 = (word2 == LE2('va'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pVa1

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
          # НЕСУЩИЙ для VA_TAIL2 (карта probe91: '… wc 7 va' → BE32(FA);
          # '… wc 0 va' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pVa2 = (word5 == LE2('va'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVa2
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

# EMIT: VA_TAIL1 (честный хвост T3-'va' стейтмента 1, карта probe91:
# 12 19 + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ), 6 Б — закон W-73) ->
# VA_TAIL2 (честный хвост T3-'va' стейтмента 2: 12 19 + BE32(cell[wc2]
# = слот F3+d2 НЕСУЩИЙ), 6 Б; честный emit базы probe91
# 121900f00ff8121900f00ff8) -> вердец -> отчёт (Token = 6) -> SEAL/END
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
# VA_TAIL = честный хвост T3-'va' стейтмента (закон probe91/probe82:
# 12 19 + BE32(слот), 6 Б): U8 0x12 ('nb 1 8' = 18₁₀ = 0x12 [урок
# probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ]) + U8 0x19 ('nb 2 5' = 25₁₀ =
# 0x19) + BE32(слот) ('wc N ow')
VA_TAIL1 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '0', 'ow']                    # BE32(слот F3+d1 — chain1)
VA_TAIL2 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + VA_TAIL1 \
       + VA_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe91\pos_wc14v3t33va.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33va tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
