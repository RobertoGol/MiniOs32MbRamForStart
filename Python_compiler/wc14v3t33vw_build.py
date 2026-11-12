# -*- coding: utf-8 -*-
# Сборщик честного МНОГОстейтментного тома 'wc d vw wc d vw'
# Shape-T3×T3-vw (веха-23, спринт 70, W-90, TKT-052): СТРИМ — пятый
# вид многостейтментного тома, оба хвоста НЕСУЩИЕ (слоты d1/d2 входят
# в emit) => d1/d2 НЕТ инваров — как у pr/sv/sp-томов W-87/W-88/W-89
# (vw-хвост БЕЗ ведущего U8, 4 Б — уникальный вид W-72).
# База = wc14v3t33sp-структура (W-89) + честная карта probe90 (39
# кейсов, свежий stage1 на каждую цель): stage1 для T3×T3-vw целей =
# 53 Б 0xFF Token 6, emit = [vw-T3-хвост] ×2 = [BE32(слот F3+d)] ×2
# = 8 Б; база 'wc 5 vw wc 5 vw' = ab92cdf6 (честный полный hex
# probe90: header CRC f5326e9b + emit 00f00ff800f00ff8 + FF +
# BE32(6) + 20 нулей). **СЛОТ НЕСУЩИЙ В ОБОИХ ХВОСТАХ** (карта
# probe90: 'wc 7 vw wc 5 vw' = 53 Б debec05a, emit
# 00f00ffa00f00ff8 — слот1 = FA = F3+d1; 'wc 5 vw wc 7 vw' = b94e9805
# — слот2 = FA = F3+d2; 'wc 7 vw wc 7 vw' = 1b52f57f — FA FA; 'wc 0
# vw wc 0 vw' = e885bcd7 — F3 F3; 'wc 1 vw wc 3 vw' = bfd24d86 — F4
# F6; 'wc 9 vw wc 8 vw' = b12eb84d — FC FB) — три tracked-цели W-90
# ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство несущих слотов).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word6 — ОБА = база ('wc 5 vw wc 5 vw .'
# = ab92cdf6; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word6, 0) + eq(word6, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = 15732726 (wc3)** (В W-90
# НЕЛЬЗЯ 15732723/15732725: там СЛОТЫ d1/d2 — chain1/reslot пишут
# адреса слотов F3+d1/F3+d2, TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'
# ПОСЛЕ TAIL_CHECK; wc3 свободна — в W-87/W-88/W-89 тоже stash; формы
# 'nb(STASH), sv'/'nb(STASH), aa' — честно проверенные
# 'nb(PF), sv'/'nb(PA), aa').
# G-затвор: PA (= p0+v1+p0-2+v2 = 4) + PD (= pVw1+pVw2 = 2) + pEOF ==
# 7 ('eq 7' — одноразрядный immediate); НЕТ RELOAD2 (digit-tail d32
# не существует в T3×T3: word6 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): te/pr/sv/sp/vw-смеси —
# stage1 ПРИНИМАЕТ ('wc 5 vw wc 5 te' = 50 Б 100e1e86 = BE32 + 05;
# 'wc 5 te wc 5 vw' = 50 Б 0b3dbc7a = 05 + BE32; 'wc 5 vw wc 5 sv' =
# 54 Б 4129034c = BE32 + 55; 'wc 5 sv wc 5 vw' = 54 Б 393c306e = 55 +
# BE32; 'wc 5 vw wc 5 sp' = 54 Б 1a4c8569 = BE32 + 53; 'wc 5 sp wc 5
# vw' = 54 Б 8dfc9673 = 53 + BE32; 'wc 5 vw wc 5 pr' = 58 Б 2d610dec
# = BE32 + pr-хвост; 'wc 5 pr wc 5 vw' = 58 Б f82af1d8 = pr-хвост +
# BE32; 'wc 5 te wc 5 te' = 47 Б c49e444f база W-86) — том молчит:
# pVw2/pVw1/обе = 0; 3/4-stmt vw-потоки — stage1 ПРИНИМАЕТ ('wc 5 vw
# wc 5 vw wc 5 vw' = 57 Б 14a07fc1 Token 9, emit 12 Б = 3 BE32,
# точка-вариант тот же 14a07fc1; 4-stmt = 61 Б 8669285e, emit 16 Б) —
# том молчит: word6 = 'wc' → pEOF = 0; 'wc 5 vw wc 5 vw 3' = 58 Б
# 0bce683b (НОВЫЙ пин: T3-vw×T4-vw, emit 13 Б = BE32×2 + digit-tail
# 15 00000003) — word6 = '3' → pEOF = 0; 'wc 5 vw 3 wc 5 vw' = 58 Б
# e595289e (НОВЫЙ пин: T4-vw×T3-vw, emit 13 Б) — word3 = '3' → p0-2
# bad; 'wc 5 vw 3 wc 5 vw 3' = 63 Б dbb5b0a3 (НОВЫЙ пин: T4×T4-vw,
# emit 18 Б; точка-вариант тот же dbb5b0a3); 'wc 5 vw wc 5 vw 3 3' =
# 63 Б 0c35ee83 (НОВЫЙ пин, Token 8, emit 18 Б); 'wc 5 vw wc 5 vw
# vw' = 57 Б d9eabc11 (НОВЫЙ пин: word6 = 'vw', emit 12 Б = 3 BE32) —
# том молчит: pEOF = 0; singles/сироты 'wc 5 vw' = 49 Б 00ce976e
# (НОВЫЙ пин: emit 4 Б БЕЗ ведущего U8 — уникальный вид W-72), сирота
# 'wc 5 vw wc 5' = 49 Б 0ddf9034 (НОВЫЙ пин: emit 4 Б), 'wc 5 sv' =
# 50 Б 6a16ae85 (пин probe88/89), 'wc 5 te' = 46 Б bac85372; неги-
# браки: 'wc vw wc 5 vw' = 0xFE 49 Б ff595de2 (НОВЫЙ пин: bad word1 —
# emit 4 Б со слотом F1 = 0x00F00FF1 = 15732721 DEFAULT WORK_CELL,
# W_Current не сменился); 'wc 5 vw wc vw' — stage1 ПРИНИМАЕТ (53 Б
# 21c2bad7 0xFF, emit 8 Б — ОБА хвоста со слотом F8 от stmt-1) — том
# молчит: v2 = 0 → PA = 3; bad d1 = 0xFE 45 Б 29ba6852 (=
# W-86/87/88/89); bad d2 = 0xFE 49 Б c4165c69 (НОВЫЙ пин); bad word2
# = 0xFE 45 Б 4ff7c705 (= W-86/87/88/89); bad word5 = 0xFE 49 Б
# 95856a78 (НОВЫЙ пин); bad word0/мусор = f3667180.
# EMIT: VW_TAIL1 (BE32(cell[wc0] = слот F3+d1, НЕСУЩИЙ — chain1
# CHECK1)) -> VW_TAIL2 (BE32(cell[wc2] = слот F3+d2, НЕСУЩИЙ —
# reslot CHECK2)) — по 3 ток ('wc N' 'ow') — vw-хвост БЕЗ ведущего
# U8 (уникальный вид W-72; в отличие от sv/sp 12 ток) -> вердец ->
# отчёт (Token = 6: 'nb 6' 'wo' — токенов слоя ДО терминатора, точка
# не считается) -> SEAL/END. Честный дизайн:
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для VW_TAIL1;
#   прецедент W-87/W-88/W-89 CHECK1 C1) + pVw1 (word2 == LE2('vw') =
#   30582, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для VW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84 RELOAD2) +
#   pVw2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('vw') = 30582 → wc7 — 'v' в МЛАДШЕМ байте
# [урок W-65/W-67/W-72], 0x7776; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33vw.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('vw' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('vw' stmt-2)
WORD7      = 10485784        # word6 — терминатор слоя T3×T3
                            # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-block'ов (VM-память = 0);
                             # в C2 reslot ПЕРЕЗАПИСЫВАЕТСЯ слотом F3+d2 —
                             # ПОСЛЕ последнего F5-cp (честный порядок)
STASH = 15732726             # wc3 — свободна (в W-87/W-88/W-89 stash;
                             # в W-90 оба вида 'vw'): stash pEOF-ветки
                             # (15732723 = СЛОТ d1, 15732725 = СЛОТ d2 —
                             # трогать НЕЛЬЗЯ: TERM-фаза читает их после
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('vw') = 30582 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно)
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(30582), 'ne', 'wc', '7', 'sv',           # 'vw' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для VW_TAIL1 (карта probe90:
          # 'wc 7 vw …' → BE32(FA); 'wc 0 vw …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pVw1 = (word2 == LE2('vw'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pVw1

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
          # НЕСУЩИЙ для VW_TAIL2 (карта probe90: '… wc 7 vw' → BE32(FA);
          # '… wc 0 vw' → BE32(F3)). wc2 = F5 — ПОСЛЕ последнего F5-cp
          # (valid3 сравнился выше; дальше F5 не читается — честный
          # порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pVw2 = (word5 == LE2('vw'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVw2
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

# EMIT: VW_TAIL1 (честный хвост T3-'vw' стейтмента 1, карта probe90:
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ), 4 Б — БЕЗ ведущего U8,
# уникальный вид W-72) -> VW_TAIL2 (честный хвост T3-'vw' стейтмента
# 2: BE32(cell[wc2] = слот F3+d2 НЕСУЩИЙ), 4 Б; честный emit базы
# probe90 00f00ff800f00ff8) -> вердец -> отчёт (Token = 6) -> SEAL/END
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
# VW_TAIL = честный хвост T3-'vw' стейтмента (закон probe90/probe81:
# BE32(слот), 4 Б — БЕЗ ведущего U8, уникальный вид W-72): ТОЛЬКО
# BE32(слот) ('wc N ow') — ни одного U8
VW_TAIL1 = ['wc', '0', 'ow']                        # BE32(слот F3+d1 — chain1)
VW_TAIL2 = ['wc', '2', 'ow']                        # BE32(слот F3+d2 — reslot)
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

MAIN = CHECK1 + CHECK2 + TAIL_CHECK + EMIT_HEAD + VW_TAIL1 \
       + VW_TAIL2 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe90\pos_wc14v3t33vw.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33vw tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
