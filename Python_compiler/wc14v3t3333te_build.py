# -*- coding: utf-8 -*-
# Сборщик честного ЧЕТЫРЁХстейтментного тома
# 'wc d te wc d te wc d te wc d te'
# Shape-T3×T3×T3×T3-te (веха-23, спринт 77, W-97, TKT-052): СТРИМ —
# вторая ЧЕТЫРЁХстейтментная T3-форма (после ow W-96). ВСЕ ЧЕТЫРЕ
# хвоста КОНСТАНТНЫ (te-хвост = ГОЛЫЙ U8 05 — 1 Б, d НЕ читается
# хвостом) => d1/d2/d3/d4 — честные ИНВАРЫ (прецедент W-86 T3×T3-te
# [emit 05+05, d1/d2 ИНВАРЫ] и W-92 if; tracked-цели ДАЮТ ОДИН md5 —
# честный инвариант, НЕ ошибка). Слот/chain/reslot/RELOAD2 НЕ нужны
# вовсе — НЕТ ни одного слота (свободны wc0/wc2=F5/wc3).
# База = wc14v3t33te-структура (W-86) + ЧЕТЫРЕ TERM-хвоста; честная
# карта probe97 (86 кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe97\_t97_card.py): stage1 для
# T3×T3×T3×T3-te целей = 49 Б 0xFF Token 12, emit = 05×4 = 4 Б; база
# 'wc 5 te' ×4 = 40dc0e48 (пин probe96 СОВПАЛ; честный полный hex:
# header CRC dd9675d1 + emit 05050505 + FF + BE32(12) + 20 нулей).
# **ВСЕ 9 НОСИТЕЛЕЙ = БАЗА (d1/d2/d3/d4 ИНВАРЫ ×4 — честный
# инвариант)**: 'wc 7 te wc 5 te wc 5 te wc 5 te' = 'wc 5 te wc 7 te
# …' = '… wc 7 te wc 5 te' = '… wc 5 te wc 7 te' = 'wc 7 te' ×3 +
# 'wc 5 te' = 'wc 0 te' ×4 = 'wc 1 te wc 3 te wc 5 te wc 9 te' = 'wc
# 9 te wc 8 te wc 0 te wc 1 te' = 'wc 2 te wc 6 te wc 4 te wc 8 te' =
# база 40dc0e48. 5-stmt te-поток = 50 Б 511f2235 (emit 05×5 = 5 Б,
# Token 15; точка-вариант тот же) — том молчит: word12 = 'wc' →
# pEOF = 0 → S = 12; 6-stmt = 51 Б e1bf059a (6 Б); 3-stmt = 48 Б
# 5cbeaa9b (пин W-95 СОВПАЛ) — том молчит: word9 = 'te' → p0-4 = 0 →
# PA = 6, PD = 3, pEOF(word12 = 0) = 1 → S = 10; 2-stmt = 47 Б
# c49e444f (пин W-86 СОВПАЛ) — S = 7. Ключ-смеси (том обязан молчать,
# ВСЕ пины сняты честно): pr/sv/sp/vw/va/ow/if/as-смеси на ВСЕХ
# ЧЕТЫРЁХ позициях — stage1 ПРИНИМАЕТ (pr 4ad3258e/ce672405/473c6395/
# cea92743; sv 97360089/26b08f21/9eceeb93/3af52223; sp 2de26709/
# 0dd0e143/f79e9b66/fbcfbf27; vw f62f6e90/ecd3ee2f/a2f6a2e1/e66f62b4;
# va ca919bd8/28ea27af/4851b498/8a6398f8; ow 6615e19c/4efd4f5f/
# a64e8431/811cb617; if 348b0254/6cac7ee5/63fe7a59/e0857428; as
# 35f64e31/854c3716/91bf6936/e9136641) — том молчит: pTeX = 0 →
# PD = 3 → S = 12; 4-стейтментные потоки других kinds (пины probe96
# СОВПАЛИ: as ×4 = 89 Б 3f6d8893, emit 44 Б; sv ×4 = 65 Б 05df0915,
# 20 Б; sp ×4 = c02a9b43; vw ×4 = 61 Б 8669285e, 16 Б; va ×4 = 69 Б
# 917128ff, 24 Б; pr ×4 = 81 Б 34f4a890, 36 Б; ow ×4 = 101 Б c39da5d5,
# 56 Б; if ×4 = 0xFE 60 Б ebe049f9 — stage1 БРАКУЕТ, пин W-92
# СОВПАЛ) — том молчит: PD = 0; кресты: 'wc 5 te' ×4 + '3' = 54 Б
# 1760d9ca (НОВЫЙ пин: emit 9 Б = 05×4 + digit-tail 15 00000003) —
# word12 = '3' → pEOF = 0; 'wc 5 te 3 wc 5 te wc 5 te wc 5 te' = 54 Б
# 137c8370 (НОВЫЙ пин: word3 = '3' → p0-2 bad); 'wc 5 te wc 5 te 3 wc
# 5 te wc 5 te' = 54 Б 7b74d3db (НОВЫЙ пин: word6 = '3' → p0-3 bad);
# 'wc 5 te wc 5 te wc 5 te 3 wc 5 te' = 54 Б 38f2c4b8 (НОВЫЙ пин:
# digit МЕЖДУ stmt3 и stmt4, word9 = '3' → p0-4 bad); 'wc 5 te' ×4 +
# 'te' = 50 Б 81728d12 (НОВЫЙ пин: stage1 парсит 13-й ток 'te' как
# ПЯТЫЙ te-стейтмент — emit 05×5) — том молчит: word12 = 'te' →
# pEOF = 0; 'wc 5 te' ×4 + '3 3' = 59 Б faa6bede (НОВЫЙ пин, emit 14
# Б); 2-stmt кресты 'wc 5 te 3 wc 5 te 3' = 57 Б 45188fc1 (= T4×T4-te
# база W-68), 'wc 5 te wc 5 te 3 3' = 57 Б 6a6f0a94 (пин W-86
# СОВПАЛ), 'wc 5 te wc 5 te 3' = 52 Б df520cf9 (пин W-77 СОВПАЛ),
# 'wc 5 te wc 5 te te' = 48 Б 3dacb5b7 (НОВЫЙ пин: 7-й ток 'te' —
# stage1 эмитит 05×3) — том молчит: word5 = 'te' → pTe2 = 1, но
# p0-3 = 0, pTe3 = 0 → PA = 4, PD = 2, pEOF = 1 → S = 7; singles/
# сироты: 'wc 5 te' = 46 Б bac85372 (пин СОВПАЛ), 'wc 5 te 3' = 51 Б
# 495e8056 (НОВЫЙ пин: emit 6 Б = 05 + digit-tail), сирота 'wc 5 te
# wc 5' = 46 Б a3bac192 (пин W-86 СОВПАЛ: emit 1 Б), 'wc 5 vw' = 49 Б
# 00ce976e (пин), 'wc 5 sv' = 50 Б 6a16ae85 (пин); неги-браки: 'wc ow
# wc 5 te wc 5 te wc 5 te' = 0xFE 59 Б ff73c458 (пин СОВПАЛ); bad d1
# = 0xFE 45 Б 29ba6852 (СОВПАЛ); bad d2 = 0xFE 46 Б 06448daf (пин
# W-86 СОВПАЛ, emit 1 Б); bad d3 = 0xFE 47 Б dcf812e7 (НОВЫЙ пин:
# emit 2 Б); bad d4 = 0xFE 48 Б c9b55156 (НОВЫЙ пин: emit 3 Б); bad
# word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad word5 = 0xFE 46 Б
# d0059999 (пин W-86 СОВПАЛ); bad word8 = 0xFE 47 Б d692bb98 (НОВЫЙ
# пин); bad word11 = 0xFE 48 Б c1ccc2a5 (НОВЫЙ пин); bad word0/мусор
# = f3667180 (СОВПАЛ); 'wc 5 te wc ow wc 5 te wc 5 te' = 0xFE 60 Б
# 2e31251b (НОВЫЙ пин: bad word4 'ow' — emit 15 Б = 05 + ow-хвост F8
# — stage1 БРАКУЕТ, В ОТЛИЧИЕ от ow-аналога [ПРИНИМАЕТ 68d64e5f,
# W-96]); 'wc 5 te wc 5 te wc ow wc 5 te' = 0xFE 61 Б b7079cc7
# (НОВЫЙ пин: bad word7 — emit 16 Б); 'wc 5 te wc 5 te wc 5 te wc
# ow' — stage1 ПРИНИМАЕТ (62 Б 0xFF a374540c, НОВЫЙ KEY-пин: emit 17
# Б = 05×3 + ow-хвост со слотом F8 = 0x00F00FF8 DEFAULT WORK_CELL —
# word10 = 'ow' НЕ цифра → слот дефолт) — том молчит: v4 = 0 → PA =
# 7, pTe4 = 0 → S = 11. Итог: **702 ток** <= 1022, компил stage1 =
# **954 Б 0xFF Token 0x2BE = 702 md5 090a6bec**, детерминизм OK. Честная
# матрица probe97c OK: **15 целей BYTE-OK против свежего stage1**
# (база 40dc0e48 = пин probe96, точка, точка+мусор, 9 носителей —
# ВСЕ = ОДИН md5 40dc0e48 — честный инвариант d-ИНВАРОВ ×4,
# прецедент W-86/W-92; + 3 tracked-цели = ТОТ ЖЕ md5) + **74/74
# негов молчат**. NEW-пины W-97: t3×3×3×3-te том + 3 tracked цели
# (ОДИН md5 — честный инвариант, НЕ ошибка).
# EMIT: TERM1..TERM4 (честные хвосты T3-'te' стейтментов 1..4 — карта
# probe97: emit = 05050505, ОБА..ВСЕ ЧЕТЫРЕ хвоста константны, d1..d4
# инвары) -> вердец -> отчёт (Token = 12: 'nb 1 2' 'wo' — токенов
# слоя ДО терминатора, точка не считается) -> SEAL/END. Честный
# дизайн (= W-96-структура минус chain1/reslot/reslot3/RESLOT4, pTe
# вместо pOw):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + pTe1 (word2 == LE2('te')
#   = 25972, 't' в МЛАДШЕМ байте, PB = wc 7, PD = ) — БЕЗ chain1 (d1-
#   ИНВАР: te-хвост константен, слот не нужен).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + pTe2 (word5 == PB,
#   PD += ) — БЕЗ reslot.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) + pTe3 (word8 == PB,
#   PD += ) — БЕЗ reslot3.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) + pTe4 (word11 == PB,
#   PD += ) — БЕЗ digit-block d44 (word12 = терминатор слоя) и БЕЗ
#   RESLOT4 (слотов нет вовсе).
# INIT = 4 группы (F4 LE2('wc') = 25463 → wc1; SRC_BUFFER → wc4; PB
# LE2('te') = 25972 → wc7 — 't' в МЛАДШЕМ байте [урок W-65/W-67,
# 0x6574 = 25972]; PC '.' = 46 → wc8). F3_MINUS_48-группа НЕ нужна:
# слотов нет вовсе (wc0/wc2 = F5/wc3 СВОБОДНЫ в W-97).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4 = 8) + PD (=
# pTe1+pTe2+pTe3+pTe4 = 4) + pEOF == 13. Форма та же, что W-96:
# 'su 9' + 'su 3' + 'eq 1' (S − 12 == 1 ⟺ S == 13; все immediate
# ОДНОразрядные; caps: PA <= 8, PD <= 4, pEOF <= 1 → S = 13 ТОЛЬКО
# при честном 4-стейтментном te-потоке И word12 ∈ {0, '.'}).
# TAIL_CHECK: pEOF = eq(word12, 0) + eq(word12, 46) через stash-ячейку
# STASH = PF = 15732733 (bad-flag МЁРТВ после последнего digit-блока
# CHECK4, дальше никто не читает; В W-97 ВСЕ ячейки 15732723/25/26
# СВОБОДНЫ — слотов нет, но PF-форма = прецедент W-95/W-96). НЕТ
# RELOAD2 (digit-tail d44 не существует в T3×T3×T3×T3: word12 =
# терминатор слоя). Урок nb-литералов учтён ЗАРАНЕЕ (probe57/W-64,
# W-93/W-94): nb-литералы ДЕСЯТИЧНЫЕ — 'nb 5' = 5₁₀ = 0x05, 'nb 3 0
# 8' = 308 = syscall-канал, 'nb 1 2' = 12.
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t3333te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('te' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('te' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('te' stmt-4)
WORD13     = 10485808        # word12 — терминатор слоя T3×T3×T3×T3
                             # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F5 = 15732725                # ноль-референс digit-блоков (VM-память =
                             # 0; В W-97 СВОБОДНА — слотов нет вовсе)
PF = 15732733                # bad-flag + pEOF-stash (том-C честно,
                             # прецедент W-95/W-96; 15732723/25/26
                             # СВОБОДНЫ, но PF-форма честнее)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('te') = 25972 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv']              # '.' (терминатор)
        # F3_MINUS_48-группа НЕ нужна: слотов нет вовсе (d-ИНВАРЫ ×4)
        # F6-группа ('ow' = 30575) НЕ нужна: te-хвост не читает слот

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
          # НЕТ chain1 (d1-ИНВАР: te-хвост константен, слот не нужен)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pTe1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
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
          # НЕТ reslot (слот не нужен)
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (as-аккумулятор)
          nb(WORD7), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B4: честный digit-block на word7 (d3): bad4 в PF.
          nb(WORD8), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as',              # PA += valid4
          # D3: pTe3 = (word8 == LE2('te'), const PB = wc 7), PD +=
          # НЕТ reslot3 (слот не нужен)
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe3

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = терминатор слоя)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (as-аккумулятор)
          nb(WORD10), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B5: честный digit-block на word10 (d4): bad5 в PF.
          nb(WORD11), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          nb(PF), 'sv',
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid5 = (bad5 == 0)
          'wc', '6', 'as',              # PA += valid5
          # БЕЗ RESLOT4: слотов нет вовсе (d-ИНВАРЫ ×4)
          # D4: pTe4 = (word11 == LE2('te'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe4
          # БЕЗ digit-block d44: word12 = терминатор слоя

# F2/G2: pEOF = (word12 == 0 ИЛИ word12 == '.') — арифметическая
# сумма ДВУХ сравнений через stash-ячейку STASH = PF = 15732733
# (bad-flag МЁРТВ после CHECK4); терминатор слоя T3×T3×T3×T3 на
# ТРИНАДЦАТОМ слове (WORD13 = 10485808).
# Затвор: PA (8) + PD (4) + pEOF == 13 — через 'su 9' + 'su 3' +
# 'eq 1' (S - 12 == 1 ⟺ S == 13; форма та же, что W-96 — прецедент
# снят; все immediate ОДНОразрядные; caps: S = 13 ТОЛЬКО при PA = 8,
# PD = 4, pEOF = 1 — честный 4-стейтментный te-поток)
TAIL_CHECK = [nb(WORD13), 'va', 'eq', '0',       # acc = eq(word12, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(PF), 'sv',                      # stash → cell[15732733]
              nb(WORD13), 'va', nb(PC), 'cp',    # acc = eq(word12, '.')
              nb(PF), 'aa',                      # acc += stash
              'su', '9',                         # acc = S - 9
              'su', '3',                         # acc = S - 12
              'eq', '1',                         # затвор: S == 13
              'if']

# EMIT: TERM1..TERM4 (честные хвосты T3-'te' стейтментов 1..4 — карта
# probe97: emit = 05050505, ВСЕ ЧЕТЫРЕ хвоста константны, d1..d4
# инвары) -> вердец -> отчёт (Token = 12)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
TERM1 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-1 te)
TERM2 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-2 te)
TERM3 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-3 te)
TERM4 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-4 te)
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 1 2', 'wo',                                  # Token = 12 (12
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

MAIN = CHECK1 + CHECK2 + CHECK3 + CHECK4 + TAIL_CHECK + EMIT_HEAD \
       + TERM1 + TERM2 + TERM3 + TERM4 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe97\pos_wc14v3t3333te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t3333te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
