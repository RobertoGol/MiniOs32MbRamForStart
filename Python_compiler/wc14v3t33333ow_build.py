# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d ow wc d ow wc d ow wc d ow wc d ow'
# Shape-T3×5-ow (веха-23, спринт 84, W-104, TKT-052): СТРИМ — первая
# ПЯТИстейтментная T3-форма. ВСЕ ПЯТЬ хвостов НЕСУЩИЕ (ow-хвост 14 Б —
# U8 0x54 + BE32(0x00F00FF0 КОНСТА) + BE32(слот) + U8 0x13 +
# BE32(0x131 КОНСТА), закон W-76: ПЕРВЫЙ BE32 = КОНСТА 0x00F00FF0 =
# 15732720 — ИНВАРИАНТЕН в d1..d5, ВТОРОЙ BE32 читает СЛОТ —
# T3-ow-single 'wc 5 ow' emit '54 00f00ff0 BE32(F3+d1) 13 00000131',
# пин W-85/probe85 b733ee4c) => d1..d5 НЕ инвары — как у
# pr/sv/sp/vw/va/as/ow-томов W-87..W-103.
# База = wc14v3t3333ow-структура (W-96, va/as/ow-структура
# W-91/W-93/W-94/W-95) + честная карта probe104 (100 кейсов, свежий
# stage1 на каждую цель, G:\...\Temp\opencode\probe104\_t104_card.py):
# stage1 для T3×5-ow целей = 115 Б 0xFF Token 15, emit =
# [ow-T3-хвост] ×5 = [54 BE32(0x00F00FF0 КОНСТА) BE32(слот F3+d) 13
# BE32(0x131 КОНСТА)] ×5 = 70 Б; база 'wc 5 ow' ×5 = 26a30702 (пин
# probe96-карты СОВПАЛ — снята как «5-stmt ow-поток»; честный полный
# hex probe104: header CRC a34018a9 + emit 5400f00ff000f00ff81300000131
# ×5 + FF + BE32(15) + 20 нулей).
# **СЛОТ НЕСУЩИЙ ТОЛЬКО ВО ВТОРОМ BE32 КАЖДОГО ХВОСТА (ПЕРВЫЙ =
# КОНСТА, закон W-76)** (карта probe104: 'wc 7 ow …' = 115 Б
# 8f75f479, слот1 = FA; '… wc 7 ow …' = ab0f360f, слот2 = FA; '… wc 7
# ow …' = c83817ff, слот3 = FA; '… wc 7 ow …' = 313f9f8d, слот4 = FA;
# '… wc 5 ow wc 7 ow' = **0bfc66a5 — НОВЫЙ пин: ПЯТЫЙ несущий слот
# (слот5 = FA)**; 'wc 7 ow' ×4 + 'wc 5 ow' = 67493493 (FA FA FA FA);
# 'wc 0 ow' ×5 = ddb539c4 (F3 F3 F3 F3 F3); 'wc 1 ow wc 3 ow wc 5 ow
# wc 9 ow wc 5 ow' = 904542d0 (F4 F6 F8 FC F8); 'wc 9 ow wc 8 ow wc 0
# ow wc 1 ow wc 5 ow' = 46ff2c50 (FC FB F3 F4 F8)) — tracked-цели
# W-104 ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство несущих слотов
# W-76 ×5).
# ТРИ reslot'а в CHECK-фазе: chain1 d1→wc0 (CHECK1) + reslot d2→wc2
# (CHECK2) + reslot3 d3→wc3 (CHECK3, W-95); СЛОТ4 = переиспользование
# wc0 в EMIT-фазе (RESLOT4, W-96); **СЛОТ5 = НОВОЕ РЕШЕНИЕ —
# переиспользование wc2 в EMIT-фазе** (свободных wc-ячеек НЕТ:
# wc0/wc2/wc3 = СЛОТЫ d1/d2/d3, wc1 = INIT F4, wc4 = INIT
# SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA, wc7 = PB, wc8 = PC,
# wc9 = PD): RESLOT5 между OW_TAIL4 и OW_TAIL5 — RESET cell[wc2] =
# F3_MINUS_48 + 'wc 2 as' на word13 (d5) → cell[wc2] = F3+d5
# (НЕСУЩИЙ для OW_TAIL5; ИДЕОМ = RESLOT4 W-96); слот2 УЖЕ ПРОЧИТАН
# OW_TAIL2 (emit-порядок TAIL1 → TAIL2 → TAIL3 → RESLOT4 → TAIL4 →
# RESLOT5 → TAIL5), CHECK-фазы завершены ДО затвора —
# переиспользование безопасно.
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база ('wc 5 ow' ×5 + ' .' = 26a30702; мусор после точки '… . 3' =
# база); pEOF = eq(word15, 0) + eq(word15, 46) через stash-ячейку
# STASH = PF = 15732733 (НЕЛЬЗЯ 15732723/25/26: там СЛОТЫ d1/d2/d3 —
# TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
# TAIL_CHECK; PF = bad-flag stash W-95..W-103 — мёртв после
# последнего digit-блока CHECK5).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pOw1+pOw2+pOw3+pOw4+pOw5 = 5) + pEOF == 16. Форма 'eq' с ДВУЗНАЧНЫМ
# immediate НЕ проверена (все прецеденты eq/su/ad/gt —
# ОДНОразрядные) => честная арифметическая развязка: 'su 9' + 'su 3'
# + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; недобор S < 15 → затвор
# молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 → S = 16 ТОЛЬКО при
# честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,pOw1..pOw5 = 1 И
# word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не существует в
# T3×5: word15 = терминатор слоя). Ключ-развязки (том обязан молчать,
# ВСЕ пины сняты честно картой probe104): te/sv/sp/vw/va/pr/if/as-
# смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ (te baa87fe5/
# 1a069fba/e3c82105/f4d3a898/3e4cf09e; sv cd66b728/9516cabd/269fd7ec/
# 05bf3df8/41b7bcf0; sp 535b8042/21c35785/247177f3/5a37a839/
# 22c982b6; vw e9546d13/2cb5beb0/fbab134e/5d58b460/28bdbea6; va
# 6393ca84/e2f2e870/d90dadab/afa40b8f/4ea850a8; pr 955d85e9/
# e0d45686/1bb278e1/2980a561/48d456e1; if 6dfaec44/48f0275a/57bdf245/
# 3505fe7e/c768ace5; as 775d9794/de79ee7a/9a0cddcd/7277a478/
# ededfc63) — том молчит: pOwX = 0 → PD = 4 → S = 15; 4-стейтментные
# потоки других kinds — stage1 ПРИНИМАЕТ ('wc 5 te' ×4 = 49 Б
# 40dc0e48, emit 05×4 = 4 Б; as ×4 = 89 Б 3f6d8893, emit 44 Б; sv ×4 =
# 65 Б 05df0915, emit 20 Б; sp ×4 = 65 Б c02a9b43; vw ×4 = 61 Б
# 8669285e, emit 16 Б; va ×4 = 69 Б 917128ff, emit 24 Б; pr ×4 = 81 Б
# 34f4a890, emit 36 Б) — том молчит: PD = 0; if ×4 — stage1 БРАКУЕТ
# (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ) — том молчит; 6-stmt
# ow-поток — stage1 ПРИНИМАЕТ ('wc 5 ow' ×6 = 129 Б 9fbdc31e [пин
# probe96 СОВПАЛ], emit 84 Б = 6 хвостов, Token 18; точка-вариант тот
# же) — том молчит: word15 = 'wc' → pEOF = 0 → S = 15; 7-stmt = 143 Б
# 9d1bf1da (НОВЫЙ пин, emit 98 Б) — S = 15; 4-stmt поток = 101 Б
# c39da5d5 (пин W-96 СОВПАЛ) — том молчит: word12 = 'ow' → p0-5 = 0 →
# PA = 8, PD = 4, pEOF(word15 = 0) = 1 → S = 13; 3-stmt поток = 87 Б
# 977e2a7a (пин W-95 СОВПАЛ) — S = 10; 2-stmt = 73 Б 40251c66 (пин
# W-94 СОВПАЛ) — S = 7; кресты: 'wc 5 ow' ×5 + '3' = 120 Б bc954986
# (НОВЫЙ пин: emit 75 Б = 5 ow-хвостов + digit-tail 15 00000003) —
# word15 = '3' → pEOF = 0; 'wc 5 ow 3 wc 5 ow wc 5 ow wc 5 ow wc 5
# ow' = 120 Б b195554c (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 —
# word3 = '3' → p0-2 bad); 'wc 5 ow wc 5 ow 3 …' = 120 Б 1b051a9c
# (НОВЫЙ пин: digit-tail после хвоста 2 — word6 = '3' → p0-3 bad);
# 'wc 5 ow wc 5 ow wc 5 ow 3 …' = 120 Б a3824c4c (НОВЫЙ пин: digit
# МЕЖДУ stmt3 и stmt4, word9 = '3' → p0-4 bad); 'wc 5 ow wc 5 ow wc 5
# ow wc 5 ow 3 …' = 120 Б 6535dff2 (НОВЫЙ пин: digit МЕЖДУ stmt4 и
# stmt5, word12 = '3' → p0-5 bad); 'wc 5 ow' ×5 + 'ow' = 129 Б
# e126d9d4 (НОВЫЙ пин: stage1 парсит 16-й ток 'ow' как ШЕСТОЙ
# ow-стейтмент — emit 84 Б, Token 16 ≠ 6-stmt Token 18) — том молчит:
# word15 = 'ow' → pEOF = 0; 'wc 5 ow' ×5 + '3 3' = 125 Б 5308e196
# (НОВЫЙ пин, emit 80 Б = 5 хвостов + digit-tail ×2); 2-stmt кресты
# 'wc 5 ow 3 wc 5 ow 3' = 83 Б ead92d5a (пин W-94 СОВПАЛ), 'wc 5 ow
# wc 5 ow 3 3' = 83 Б b9d2425c (СОВПАЛ), 'wc 5 ow wc 5 ow 3' = 78 Б
# 9a6a53e9 (СОВПАЛ), 'wc 5 ow wc 5 ow ow' = 87 Б 49149cf0 (СОВПАЛ) —
# том молчит; singles/сироты: 'wc 5 ow' = 59 Б b733ee4c (пин W-85
# СОВПАЛ), 'wc 5 ow 3' = 64 Б fb10fa26 (СОВПАЛ), сирота 'wc 5 ow wc
# 5' = 59 Б a48426b6 (пин W-94 СОВПАЛ), 'wc 5 vw' = 49 Б 00ce976e,
# 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 te' = 46 Б bac85372; неги-браки:
# 'wc ow wc 5 ow wc 5 ow wc 5 ow wc 5 ow' = 0xFE 59 Б ff73c458 (пин
# W-95 СОВПАЛ: bad word1 — emit 14 Б со слотом F1 = 0x00F00FF1 =
# 15732721 DEFAULT WORK_CELL); 'wc z ow …' = 0xFE 45 Б 29ba6852
# (СОВПАЛ); 'wc 5 ow wc z ow …' = 0xFE 59 Б ea08576d (СОВПАЛ); 'wc 5
# ow wc 5 ow wc z ow …' = 0xFE 73 Б fa369b02 (СОВПАЛ); 'wc 5 ow wc 5
# ow wc 5 ow wc z ow …' = 0xFE 87 Б cf830e57 (СОВПАЛ); 'wc 5 ow' ×4 +
# 'wc z ow' = 0xFE 101 Б **7485bf10** (НОВЫЙ пин: bad d5 — emit 56 Б
# = 4 хвоста); bad word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad word5 =
# 0xFE 59 Б 7a101f35 (СОВПАЛ); bad word8 = 0xFE 73 Б 1e1f1b30
# (СОВПАЛ); bad word11 = 0xFE 87 Б 6ea111bd (СОВПАЛ); 'wc 5 ow' ×4 +
# 'wc 5 xx' = 0xFE 101 Б **40263471** (НОВЫЙ пин: bad word14 — emit
# 56 Б); bad word0/мусор = f3667180 (СОВПАЛ ×2); 'wc 5 ow wc ow wc 5
# ow wc 5 ow wc 5 ow' = 0xFE 73 Б 17c27666 (пин W-95 СОВПАЛ); 'wc 5
# ow wc 5 ow wc ow wc 5 ow wc 5 ow' = 0xFE 87 Б 39437968 (пин W-96
# СОВПАЛ); 'wc 5 ow wc 5 ow wc 5 ow wc ow wc 5 ow' = 0xFE 101 Б
# **5777b5bd** (НОВЫЙ пин: bad word10 в СЕРЕДИНЕ 5-stmt — stage1
# БРАКУЕТ, emit 56 Б = 4 хвоста); 'wc 5 ow' ×4 + 'wc ow' — stage1
# ПРИНИМАЕТ (115 Б 0xFF **565c1b63**, НОВЫЙ KEY-пин: emit 70 Б — ВСЕ
# ПЯТЬ хвостов со слотом F8 от stmt-1, Token 14) — том молчит: v5 = 0
# → PA = 9 → S = 15.
# ИТОГ приёмки (probe104c, accept104.txt): том 1001 ток (лимит 1022),
# собран = 1478 B вердец 0xFF md5 3672ed6245b479d181340a15d4bbe0de
# (двойной компил — детерминизм OK); 15 целей BYTE-OK против свежего
# stage1 (база 26a30702; носители 8f75f479/ab0f360f/c83817ff/313f9f8d/
# 0bfc66a5/67493493/ddb539c4/904542d0/46ff2c50; tracked _33 7da9d5eb,
# _37 71c96dd5, _90 46ff2c50); неги 88/88 молчат. 1001 ток = честное
# сжатие −60: stash-пересылка nb(PF) sv/va после 'gt 9' ИЗБЫТОЧНА —
# VM OP_LOAD mode 0x1A оставляет bad в acc, 'eq 0' (mode 0x16)
# сравнивает acc, sv/va acc не портят (снято с CtOs-Emu/ctos_vm.py);
# digit-block 'su 8'×6, 'eq 0', reslot-идиомы ЦЕЛЫ.
# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe104:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo' = pending-nb BE32-вывод КОНСТАНТЫ, прецедент W-83/W-85) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 ('nb 1 9' =
# 19₁₀ [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ]) + BE32(0x131 =
# 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76) -> OW_TAIL2
# (reslot: BE32(cell[wc2] = слот F3+d2)) -> OW_TAIL3 (reslot3:
# BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование wc0:
# RESET cell[wc0] = F3_MINUS_48 + 'wc 0 as' на word10 → cell[wc0] =
# F3+d4 — слот1 уже прочитан OW_TAIL1) -> OW_TAIL4 (BE32(cell[wc0] =
# слот F3+d4)) -> RESLOT5 (НОВОЕ: переиспользование wc2: RESET
# cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word13 → cell[wc2] = F3+d5 —
# слот2 уже прочитан OW_TAIL2) -> OW_TAIL5 (BE32(cell[wc2] = слот
# F3+d5 — ПЯТЫЙ НЕСУЩИЙ СЛОТ)) -> вердец -> отчёт (Token = 15: 'nb 1
# 5' 'wo' — токенов слоя ДО терминатора, точка не считается) ->
# SEAL/END. Честный дизайн (= W-96 ow-структура + CHECK5 + RESLOT5):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для
#   OW_TAIL1) + pOw1 (word2 == LE2('ow') = 30575, 'o' в МЛАДШЕМ
#   байте, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для OW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок W-84) + pOw2
#   (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после reslot
#   CHECK2; 'eq 0' = прецедент TAIL_CHECK W-93/W-94) + C3 reslot3:
#   RESET cell[wc3] = F3_MINUS_48 + 'wc 3 as' на word7 → cell[wc3] =
#   F3+d3 (НЕСУЩИЙ для OW_TAIL3; wc3 = 15732726 СВОБОДНА в
#   W-95..W-104: stash в PF) + pOw3 (word8 == PB, PD += ) — БЕЗ
#   digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — валид-сравнение через
#   'eq 0' (F5 отравлен) + pOw4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 — БЕЗ reslot4 (слот4 материализуется RESLOT4 в
#   EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) — валид-сравнение
#   через 'eq 0' (F5 отравлен) + pOw5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('ow') = 30575 → wc7 — 'o' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x776F; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333ow.words

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
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('ow' stmt-5)
WORD16     = 10485820        # word15 — терминатор слоя T3×5
                             # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-блоков CHECK1/CHECK2
                             # (VM-память = 0); В CHECK3/CHECK4/CHECK5
                             # НЕЛЬЗЯ — там СЛОТ d2 (reslot CHECK2) —
                             # valid через 'eq 0'
STASH = 15732733             # PF — bad-flag МЁРТВ после CHECK5
                             # (НЕЛЬЗЯ 15732723/15732725/15732726: там
                             # СЛОТЫ d1/d2/d3 — TERM-фаза читает их
                             # 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('ow') = 30575 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-104
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
          # = 15732723 + d1 — НЕСУЩИЙ для OW_TAIL1 (карта probe104:
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
          # НЕСУЩИЙ для OW_TAIL2 (карта probe104: '… wc 7 ow …' →
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
          # valid4 = (bad4 == 0) через 'eq 0' НАПРЯМУЮ: 'gt 9' оставляет
          # bad4 в acc (VM OP_LOAD mode 0x1A — результат в acc; 'eq 0' =
          # mode 0x16 сравнивает acc; stash-пересылка nb(PF) sv/va
          # ИЗБЫТОЧНА — sv/va acc не портят, снято с CtOs-Emu/ctos_vm.py;
          # F5 = wc2 = СЛОТ d2 после reslot CHECK2 — потому 'eq 0', а не
          # 'nb(F5), cp'; прецедент TAIL_CHECK W-93/W-94)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid4
          # C3: честный reslot chain3: RESET cell[wc3] = F3 минус 48,
          # затем 'wc 3 as' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для OW_TAIL3 (карта probe104: '… wc 7 ow …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-95..W-104 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pOw3 = (word8 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (as-аккумулятор)
          nb(WORD10), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B5: честный digit-block на word10 (d4): bad5 в PF.
          nb(WORD11), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          # valid5 = (bad5 == 0) через 'eq 0' НАПРЯМУЮ: 'gt 9' оставляет
          # bad5 в acc (VM OP_LOAD mode 0x1A; 'eq 0' = mode 0x16 на acc;
          # stash-пересылка nb(PF) sv/va ИЗБЫТОЧНА — sv/va acc не портят,
          # снято с CtOs-Emu/ctos_vm.py). НЕ через 'nb(F5), cp': F5 = wc2
          # = СЛОТ d2 (отравлен reslot CHECK2; прецедент CHECK3 W-95/
          # TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid5
          # БЕЗ reslot4: свободных wc-ячеек НЕТ — слот4
          # материализуется RESLOT4 в EMIT-фазе (переиспользование
          # wc0 ПОСЛЕ OW_TAIL3)
          # D4: pOw4 = (word11 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw4
          # БЕЗ digit-block d44: word12 = 'wc' stmt-5

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (as-аккумулятор)
          nb(WORD13), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B6: честный digit-block на word13 (d5): bad6 в PF.
          nb(WORD14), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          # valid6 = (bad6 == 0) через 'eq 0' НАПРЯМУЮ: 'gt 9' оставляет
          # bad6 в acc (VM OP_LOAD mode 0x1A; 'eq 0' = mode 0x16 на acc;
          # stash-пересылка nb(PF) sv/va ИЗБЫТОЧНА — sv/va acc не портят,
          # снято с CtOs-Emu/ctos_vm.py). НЕ через 'nb(F5), cp': F5 = wc2
          # = СЛОТ d2 (отравлен reslot CHECK2; прецедент CHECK3 W-95/
          # W-96/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ OW_TAIL4)
          # D5: pOw5 = (word14 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw5
          # БЕЗ digit-block d55: word15 = терминатор слоя

# F2/G2: pEOF = (word15 == 0 ИЛИ word15 == '.') — арифметическая
# сумма ДВУХ сравнений через stash-ячейку STASH = PF = 15732733
# (bad-flag мёртв после CHECK5; 15732723/15732725/15732726 = СЛОТЫ
# d1/d2/d3 — трогать НЕЛЬЗЯ: TERM-фаза читает их после TAIL_CHECK);
# терминатор слоя T3×5 на ШЕСТНАДЦАТОМ слове (WORD16 = 10485820).
# Затвор: PA (10) + PD (5) + pEOF == 16 — через 'su 9' + 'su 3' +
# 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; форма 'eq' с двузначным
# immediate не проверена — все прецеденты eq/su/ad/gt одноразрядные;
# caps: S = 16 ТОЛЬКО при PA = 10, PD = 5, pEOF = 1 — честный
# 5-стейтментный поток)
TAIL_CHECK = [nb(WORD16), 'va', 'eq', '0',       # acc = eq(word15, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(PF), 'sv',                      # stash → cell[15732733]
              nb(WORD16), 'va', nb(PC), 'cp',    # acc = eq(word15, '.')
              nb(PF), 'aa',                      # acc += stash
              'su', '9',                         # acc = S - 9
              'su', '3',                         # acc = S - 12
              'su', '3',                         # acc = S - 15
              'eq', '1',                         # затвор: S == 16
              'if']

# RESLOT4 = переиспользование wc0 для слота d4 (ИДЕОМ W-96/W-98/W-99/
# W-100/W-101/W-102/W-103): RESET cell[wc0] = F3_MINUS_48, затем
# 'wc 0 as' на word10 (d4) → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для
# OW_TAIL4 (карта probe104: '… wc 5 ow wc 7 ow' → BE32(FA) в
# ЧЕТВЁРТОМ хвосте — пин 313f9f8d; '… wc 0 ow' → BE32(F3)).
# Слот1 уже прочитан OW_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (НОВОЕ W-104, идеом =
# RESLOT4 W-96): RESET cell[wc2] = F3_MINUS_48, затем 'wc 2 as' на
# word13 (d5) → cell[wc2] = 15732723 + d5. НЕСУЩИЙ для OW_TAIL5
# (карта probe104: '… wc 5 ow wc 7 ow' → BE32(FA) в ПЯТОМ хвосте —
# НОВЫЙ пин 0bfc66a5: ПЯТЫЙ несущий слот; '… wc 0 ow' → BE32(F3)).
# Слот2 уже прочитан OW_TAIL2 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: OW_TAIL = честный хвост T3-'ow' стейтмента (закон W-76: U8
# 0x54 = 84₁₀ = 0x54 [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ] +
# BE32(0x00F00FF0 = 15732720 КОНСТА) + BE32(слот) ('wc N ow') + U8
# 0x13 = 19₁₀ + BE32(0x131 = 305 КОНСТА), 14 Б, 36 ток)
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
OW_TAIL4 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '0', 'ow',                         # BE32(слот F3+d4 — RESLOT4)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
OW_TAIL5 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',        # U8 84 (0x54)
            'nb 1 5 7 3 2 7 2 0', 'wo',              # BE32(0x00F00FF0 КОНСТА)
            'wc', '2', 'ow',                         # BE32(слот F3+d5 — RESLOT5)
            'nb 1 9', 'em', 'nb 3 0 8', 'sc',        # U8 19 (0x13)
            'nb 3 0 5', 'wo']                        # BE32(0x131 = 305 КОНСТА)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 1 5', 'wo',                                  # Token = 15 (15
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

MAIN = CHECK1 + CHECK2 + CHECK3 + CHECK4 + CHECK5 + TAIL_CHECK + EMIT_HEAD \
       + OW_TAIL1 + OW_TAIL2 + OW_TAIL3 + RESLOT4 + OW_TAIL4 \
       + RESLOT5 + OW_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe104\pos_wc14v3t33333ow.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333ow tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
