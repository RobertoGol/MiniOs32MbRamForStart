# -*- coding: utf-8 -*-
# Сборщик честного ЧЕТЫРЁХстейтментного тома
# 'wc d ow wc d ow wc d ow wc d ow'
# Shape-T3×T3×T3×T3-ow (веха-23, спринт 76, W-96, TKT-052): СТРИМ —
# первая ЧЕТЫРЁХстейтментная T3-форма. ВСЕ ЧЕТЫРЕ хвоста НЕСУЩИЕ
# (ow-хвост 14 Б — U8 0x54 + BE32(0x00F00FF0 КОНСТА) + BE32(слот) +
# U8 0x13 + BE32(0x131 КОНСТА), закон W-76: ПЕРВЫЙ BE32 = КОНСТА
# 0x00F00FF0 = 15732720 — ИНВАРИАНТЕН в d1/d2/d3/d4, ВТОРОЙ BE32
# читает СЛОТ — T3-ow-single 'wc 5 ow' emit '54 00f00ff0 BE32(F3+d1)
# 13 00000131', пин W-85/probe85 b733ee4c) => d1/d2/d3/d4 НЕ инвары —
# как у pr/sv/sp/vw/va/as/ow-томов W-87..W-95.
# База = wc14v3t333ow-структура (W-95, va/as/ow-структура
# W-91/W-93/W-94) + честная карта probe96 (86 кейсов, свежий stage1
# на каждую цель, G:\...\Temp\opencode\probe96\_t96_card.py):
# stage1 для T3×T3×T3×T3-ow целей = 101 Б 0xFF Token 12, emit =
# [ow-T3-хвост] ×4 = [54 BE32(0x00F00FF0 КОНСТА) BE32(слот F3+d) 13
# BE32(0x131 КОНСТА)] ×4 = 56 Б; база 'wc 5 ow wc 5 ow wc 5 ow wc 5
# ow' = c39da5d5 (пин W-94/probe94 СОВПАЛ; честный полный hex
# probe96: header CRC a9f0ef2d + emit 5400f00ff000f00ff81300000131 ×4
# + FF + BE32(12) + 20 нулей).
# **СЛОТ НЕСУЩИЙ ТОЛЬКО ВО ВТОРОМ BE32 КАЖДОГО ХВОСТА (ПЕРВЫЙ =
# КОНСТА, закон W-76)** (карта probe96: 'wc 7 ow …' = 101 Б
# 3c51223a, слот1 = FA; '… wc 7 ow …' = 62418a1c, слот2 = FA; '… wc 7
# ow …' = 6307fb05, слот3 = FA; '… wc 5 ow wc 7 ow' = **358aae69 —
# НОВЫЙ пин: ЧЕТВЁРТЫЙ несущий слот (слот4 = FA)**; 'wc 7 ow' ×3 +
# 'wc 5 ow' = b4c825b6 (FA FA FA); 'wc 0 ow' ×4 = 9093fbf5 (F3 F3 F3
# F3); 'wc 1 ow wc 3 ow wc 5 ow wc 9 ow' = 2dfe3a78 (F4 F6 F8 FC);
# 'wc 9 ow wc 8 ow wc 0 ow wc 1 ow' = 41a1116d (FC FB F3 F4); 'wc 2
# ow wc 6 ow wc 4 ow wc 8 ow' = 4476e8aa (F5 F9 F7 FB)) — три
# tracked-цели W-96 ДАЮТ ТРИ РАЗНЫЕ md5 (3c51223a / 358aae69 /
# 41a1116d — честное доказательство несущих слотов W-76 ×4).
# ТРИ reslot'а в CHECK-фазе: chain1 d1→wc0 (CHECK1) + reslot d2→wc2
# (CHECK2) + reslot3 d3→wc3 (CHECK3, W-95); **СЛОТ4 = НОВОЕ РЕШЕНИЕ —
# переиспользование wc0 в EMIT-фазе** (свободных wc-ячеек НЕТ:
# wc0/wc2/wc3 = СЛОТЫ d1/d2/d3, wc1 = INIT F4, wc4 = INIT
# SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA, wc7 = PB, wc8 = PC,
# wc9 = PD): RESLOT4 между OW_TAIL3 и OW_TAIL4 — RESET cell[wc0] =
# F3_MINUS_48 + 'wc 0 as' на word10 (d4) → cell[wc0] = F3+d4
# (НЕСУЩИЙ для OW_TAIL4; ИДЕОМ = INIT 'nb(F3_MINUS_48) ne wc 0 sv' +
# CHECK1 C1 'nb(SRC_WORD2) va wc 0 as' — оба честно проверены);
# слот1 УЖЕ ПРОЧИТАН OW_TAIL1 (emit-порядок TAIL1 → TAIL2 → TAIL3 →
# RESLOT4 → TAIL4), CHECK-фазы завершены ДО затвора —
# переиспользование безопасно.
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word12 (ТРИНАДЦАТОЕ слово) — ОБА =
# база ('wc 5 ow' ×4 + ' .' = c39da5d5; мусор после точки '… . 3' =
# база); pEOF = eq(word12, 0) + eq(word12, 46) через stash-ячейку
# STASH = PF = 15732733 (В W-96 НЕЛЬЗЯ 15732723/25/26: там СЛОТЫ
# d1/d2/d3 — TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
# TAIL_CHECK; PF = bad-flag stash W-95 — мёртв после последнего
# digit-блока CHECK4).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4 = 8) + PD (=
# pOw1+pOw2+pOw3+pOw4 = 4) + pEOF == 13. Форма 'eq' с ДВУЗНАЧНЫМ
# immediate НЕ проверена (все прецеденты eq/su/ad/gt —
# ОДНОразрядные) => честная арифметическая развязка: 'su 9' + 'su 3'
# + 'eq 1' (S - 12 == 1 ⟺ S == 13; недобор S < 12 → затвор молчит;
# caps: PA <= 8, PD <= 4, pEOF <= 1 → S = 13 ТОЛЬКО при честном
# p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,pOw1,pOw2,pOw3,pOw4 = 1 И word12 ∈
# {0, '.'}). НЕТ RELOAD2 (digit-tail d44 не существует в T3×T3×T3×T3:
# word12 = терминатор слоя). Ключ-развязки (том обязан молчать, ВСЕ
# пины сняты честно картой probe96): te/sv/sp/vw/va/pr/if/as-смеси
# на ВСЕХ ЧЕТЫРЁХ позициях — stage1 ПРИНИМАЕТ ('wc 5 te wc 5 ow wc 5
# ow wc 5 ow' = 88 Б e402fe19 = 05 + ow-хвосты ×3; sv 45ab5714/sp
# 967c513c/vw c2d5c76d/va 146d0482/pr 16d77715/if 98891826/as
# bd9a813e; позиция 2: te 1e4548d5/sv 5d98991c/sp fa152967/vw
# bcb82435/va ce45976e/pr 867eecc0/if 7e958cad/as 6f02bb6d; позиция
# 3: te 92ba0d21/sv e99dcfff/sp b98e4df7/vw 4f9841d8/va 3d6e741a/pr
# 62ff60da/if 4c03fa0f/as c5994480; позиция 4: te 1891b369/sv
# 1ebb8c4e/sp d942b704/vw 1808885d/va a0dee23f/pr 7f911a05/if
# 90e96ed8/as 0a2e27ea) — том молчит: pOwX = 0 → PD = 3 → S = 12;
# 4-стейтментные потоки других kinds — stage1 ПРИНИМАЕТ ('wc 5 te' ×4
# = 49 Б 40dc0e48, emit 05×4 = 4 Б; as ×4 = 89 Б 3f6d8893, emit 44 Б;
# sv ×4 = 65 Б 05df0915, emit 20 Б; sp ×4 = c02a9b43; vw ×4 = 61 Б
# 8669285e, emit 16 Б; va ×4 = 69 Б 917128ff, emit 24 Б; pr ×4 = 81 Б
# 34f4a890, emit 36 Б) — том молчит: PD = 0; if ×4 — stage1 БРАКУЕТ
# (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ) — том молчит; 5-stmt
# ow-поток — stage1 ПРИНИМАЕТ ('wc 5 ow' ×5 = 115 Б 26a30702, emit 70
# Б = 5 хвостов, Token 15; точка-вариант тот же) — том молчит:
# word12 = 'wc' → pEOF = 0 → S = 12; 6-stmt = 129 Б 9fbdc31e, emit 84
# Б — том молчит: word12 = 'wc' → S = 12; 3-stmt поток = 87 Б
# 977e2a7a (пин W-95 СОВПАЛ) — том молчит: word9 = 'ow' → p0-4 = 0 →
# PA = 6, PD = 3, pEOF(word12 = 0) = 1 → S = 10; 2-stmt = 73 Б
# 40251c66 (пин W-94 СОВПАЛ) — S = 7; кресты: 'wc 5 ow' ×4 + '3' =
# 106 Б b8ca1c4c (НОВЫЙ пин: emit 61 Б = 4 ow-хвоста + digit-tail 15
# 00000003) — word12 = '3' → pEOF = 0; 'wc 5 ow 3 wc 5 ow wc 5 ow wc
# 5 ow' = 106 Б f0658743 (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 —
# word3 = '3' → p0-2 bad); 'wc 5 ow wc 5 ow 3 wc 5 ow wc 5 ow' = 106
# Б e2a0ec2a (НОВЫЙ пин: digit-tail после хвоста 2 — word6 = '3' →
# p0-3 bad); 'wc 5 ow wc 5 ow wc 5 ow 3 wc 5 ow' = 106 Б 32b1908e
# (НОВЫЙ пин: digit МЕЖДУ stmt3 и stmt4, word9 = '3' → p0-4 bad);
# 'wc 5 ow' ×4 + 'ow' = 115 Б 5dabe5cb (НОВЫЙ пин: stage1 парсит
# 13-й ток 'ow' как ПЯТЫЙ ow-стейтмент — emit 70 Б = 5 хвостов) — том
# молчит: word12 = 'ow' → pEOF = 0; 'wc 5 ow' ×4 + '3 3' = 111 Б
# 8901e0f5 (НОВЫЙ пин, emit 66 Б = 4 хвоста + digit-tail ×2); 2-stmt
# кресты 'wc 5 ow 3 wc 5 ow 3' = 83 Б ead92d5a (пин W-94 СОВПАЛ),
# 'wc 5 ow wc 5 ow 3 3' = 83 Б b9d2425c (СОВПАЛ), 'wc 5 ow wc 5 ow 3'
# = 78 Б 9a6a53e9 (СОВПАЛ), 'wc 5 ow wc 5 ow ow' = 87 Б 49149cf0
# (СОВПАЛ) — том молчит; singles/сироты: 'wc 5 ow' = 59 Б b733ee4c
# (пин W-85 СОВПАЛ), 'wc 5 ow 3' = 64 Б fb10fa26 (СОВПАЛ), сирота
# 'wc 5 ow wc 5' = 59 Б a48426b6 (пин W-94 СОВПАЛ), 'wc 5 vw' = 49 Б
# 00ce976e, 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 te' = 46 Б bac85372;
# неги-браки: 'wc ow wc 5 ow wc 5 ow wc 5 ow' = 0xFE 59 Б ff73c458
# (пин W-95 СОВПАЛ: bad word1); 'wc z ow …' = 0xFE 45 Б 29ba6852
# (СОВПАЛ); 'wc 5 ow wc z ow …' = 0xFE 59 Б ea08576d (СОВПАЛ); 'wc 5
# ow wc 5 ow wc z ow …' = 0xFE 73 Б fa369b02 (СОВПАЛ); 'wc 5 ow wc 5
# ow wc 5 ow wc z ow' = 0xFE 87 Б cf830e57 (НОВЫЙ пин: bad d4 — emit
# 42 Б = 3 хвоста); bad word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad
# word5 = 0xFE 59 Б 7a101f35 (СОВПАЛ); bad word8 = 0xFE 73 Б
# 1e1f1b30 (СОВПАЛ); 'wc 5 ow wc 5 ow wc 5 ow wc 5 xx' = 0xFE 87 Б
# 6ea111bd (НОВЫЙ пин: bad word11 — emit 42 Б); bad word0/мусор =
# f3667180; 'wc 5 ow wc ow wc 5 ow wc 5 ow' = 0xFE 73 Б 17c27666
# (пин W-95 СОВПАЛ); 'wc 5 ow wc 5 ow wc ow wc 5 ow' = 0xFE 87 Б
# 39437968 (НОВЫЙ пин: bad word7 в 4-stmt — stage1 БРАКУЕТ, В
# ОТЛИЧИЕ от 3-stmt аналога [ПРИНИМАЕТ 13455fbf, W-95]); 'wc 5 ow wc
# 5 ow wc 5 ow wc ow' — stage1 ПРИНИМАЕТ (101 Б 68d64e5f 0xFF, emit
# 56 Б — ВСЕ ЧЕТЫРЕ хвоста со слотом F8 от stmt-1) — том молчит: v4 =
# 0 → PA = 7 → S = 12. Итог: **902 ток** <= 1022, компил stage1 =
# **1286 Б 0xFF Token 0x386 = 902 md5 e1c6ceba**, детерминизм OK. Честная
# матрица probe96c OK: **12 целей BYTE-OK против свежего stage1**
# (база c39da5d5, точка, точка+мусор, 9 носителей — ТРИ РАЗНЫЕ md5
# tracked-целей) + **75/75 негов молчат**. NEW-пины W-96: t3×3×3×3-ow
# том + 3 tracked цели (ТРИ РАЗНЫЕ md5 — несущие слоты W-76 ×4).
# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe96:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo' = pending-nb BE32-вывод КОНСТАНТЫ, прецедент W-83/W-85) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 ('nb 1 9' =
# 19₁₀ [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ]) + BE32(0x131 =
# 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76) -> OW_TAIL2
# (reslot: BE32(cell[wc2] = слот F3+d2)) -> OW_TAIL3 (reslot3:
# BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (НОВОЕ: RESET cell[wc0] =
# F3_MINUS_48 + 'wc 0 as' на word10 → cell[wc0] = F3+d4 —
# переиспользование wc0, слот1 уже прочитан OW_TAIL1) -> OW_TAIL4
# (BE32(cell[wc0] = слот F3+d4 — ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ) -> вердец ->
# отчёт (Token = 12: 'nb 1 2' 'wo' — токенов слоя ДО терминатора,
# точка не считается) -> SEAL/END. Честный дизайн (= W-95
# ow-структура + CHECK4):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для
#   OW_TAIL1) + pOw1 (word2 == LE2('ow') = 30575, 'o' в МЛАДШЕМ
#   байте, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для OW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84) + pOw2
#   (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после reslot
#   CHECK2; 'eq 0' = прецедент TAIL_CHECK W-93/W-94) + C3 reslot3:
#   RESET cell[wc3] = F3_MINUS_48 + 'wc 3 as' на word7 → cell[wc3] =
#   F3+d3 (НЕСУЩИЙ для OW_TAIL3; wc3 = 15732726 СВОБОДНА в W-95/W-96:
#   stash в PF) + pOw3 (word8 == PB, PD += ) — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — валид-сравнение через
#   'eq 0' (F5 отравлен) + pOw4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = терминатор слоя) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('ow') = 30575 → wc7 — 'o' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x776F; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t3333ow.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('ow' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('ow' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('ow' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('ow' stmt-4)
WORD13     = 10485808        # word12 — терминатор слоя T3×T3×T3×T3
                             # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-блоков CHECK1/CHECK2
                             # (VM-память = 0); В CHECK3/CHECK4 НЕЛЬЗЯ —
                             # там СЛОТ d2 (reslot CHECK2) — valid через
                             # 'eq 0'
STASH = 15732733             # PF — bad-flag МЁРТВ после CHECK4
                             # (В W-96 НЕЛЬЗЯ 15732723/15732725/15732726:
                             # там СЛОТЫ d1/d2/d3 — TERM-фаза читает их
                             # 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('ow') = 30575 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-96
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
          # = 15732723 + d1 — НЕСУЩИЙ для OW_TAIL1 (карта probe96:
          # 'wc 7 ow …' → BE32(FA); 'wc 0 ow …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pOw1 = (word2 == LE2('ow'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pOw1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
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
          # НЕСУЩИЙ для OW_TAIL2 (карта probe96: '… wc 7 ow …' →
          # BE32(FA); '… wc 0 ow …' → BE32(F3)). wc2 = F5 — ПОСЛЕ
          # последнего F5-cp (valid3 сравнился выше; дальше F5 не
          # читается CHECK1/CHECK2 — честный порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pOw2 = (word5 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw2

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
          # valid4 = (bad4 == 0) через 'eq 0' — НЕ через 'nb(F5), cp':
          # F5 = wc2 = СЛОТ d2 после reslot CHECK2 ('eq 0' = прецедент
          # TAIL_CHECK W-93/W-94)
          nb(PF), 'va', 'eq', '0',
          'wc', '6', 'as',              # PA += valid4
          # C3: честный reslot chain3: RESET cell[wc3] = F3 минус 48,
          # затем 'wc 3 as' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для OW_TAIL3 (карта probe96: '… wc 7 ow …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-95/W-96 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pOw3 = (word8 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

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
          # valid5 = (bad5 == 0) через 'eq 0' — НЕ через 'nb(F5), cp':
          # F5 = wc2 = СЛОТ d2 (отравлен reslot CHECK2; 'eq 0' =
          # прецедент CHECK3 W-95/TAIL_CHECK)
          nb(PF), 'va', 'eq', '0',
          'wc', '6', 'as',              # PA += valid5
          # БЕЗ reslot4: свободных wc-ячеек НЕТ — слот4
          # материализуется RESLOT4 в EMIT-фазе (переиспользование
          # wc0 ПОСЛЕ OW_TAIL3)
          # D4: pOw4 = (word11 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw4
          # БЕЗ digit-block d44: word12 = терминатор слоя

# F2/G2: pEOF = (word12 == 0 ИЛИ word12 == '.') — арифметическая
# сумма ДВУХ сравнений через stash-ячейку STASH = PF = 15732733
# (bad-flag мёртв после CHECK4; 15732723/15732725/15732726 = СЛОТЫ
# d1/d2/d3 — трогать НЕЛЬЗЯ: TERM-фаза читает их после TAIL_CHECK);
# терминатор слоя T3×T3×T3×T3 на ТРИНАДЦАТОМ слове (WORD13 =
# 10485808).
# Затвор: PA (8) + PD (4) + pEOF == 13 — через 'su 9' + 'su 3' +
# 'eq 1' (S - 12 == 1 ⟺ S == 13; форма 'eq' с двузначным immediate
# не проверена — все прецеденты eq/su/ad/gt одноразрядные; caps:
# S = 13 ТОЛЬКО при PA = 8, PD = 4, pEOF = 1 — честный
# 4-стейтментный поток)
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

# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe96:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo') + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 +
# BE32(0x131 = 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76:
# ПЕРВЫЙ BE32 = КОНСТА (инвариантен в d1..d4), ВТОРОЙ BE32 = СЛОТ;
# 'nb 8 4' = 84₁₀ = 0x54, 'nb 1 9' = 19₁₀ = 0x13 [урок probe57/W-64:
# nb-литералы ДЕСЯТИЧНЫЕ]) -> OW_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2)) -> OW_TAIL3 (тот же хвост с reslot3:
# BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (НОВОЕ: RESET cell[wc0] =
# F3_MINUS_48 + 'wc 0 as' на word10 → cell[wc0] = F3+d4 —
# переиспользование wc0: слот1 УЖЕ прочитан OW_TAIL1, CHECK-фазы
# завершены; ИДЕОМ = INIT + CHECK1 C1) -> OW_TAIL4 (тот же хвост с
# переиспользованным wc0: BE32(cell[wc0] = слот F3+d4) — честный emit
# базы probe96 5400f00ff000f00ff81300000131 ×4) -> вердец -> отчёт
# (Token = 12)
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
OW_TAIL3 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '3', 'ow',                         # BE32(слот F3+d3 — reslot3)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
# RESLOT4 = переиспользование wc0 для слота d4 (НОВОЕ W-96):
# RESET cell[wc0] = F3_MINUS_48, затем 'wc 0 as' на word10 (d4)
# → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для OW_TAIL4 (карта probe96:
# '… wc 5 ow wc 7 ow' → BE32(FA) в ЧЕТВЁРТОМ хвосте — НОВЫЙ пин
# 358aae69: ЧЕТВЁРТЫЙ несущий слот; '… wc 0 ow' → BE32(F3)).
# Слот1 уже прочитан OW_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
OW_TAIL4 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '0', 'ow',                         # BE32(слот F3+d4 — RESLOT4)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
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
       + OW_TAIL1 + OW_TAIL2 + OW_TAIL3 + RESLOT4 + OW_TAIL4 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe96\pos_wc14v3t3333ow.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t3333ow tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
