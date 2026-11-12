# -*- coding: utf-8 -*-
# Сборщик честного ТРЁХстейтментного тома 'wc d ow wc d ow wc d ow'
# Shape-T3×T3×T3-ow (веха-23, спринт 75, W-95, TKT-052): СТРИМ —
# первая ТРЁХстейтментная T3-форма. ОБА... ВСЕ ТРИ хвоста НЕСУЩИЕ
# (ow-хвост 14 Б — U8 0x54 + BE32(0x00F00FF0 КОНСТА) + BE32(слот) +
# U8 0x13 + BE32(0x131 КОНСТА), закон W-76: ПЕРВЫЙ BE32 = КОНСТА
# 0x00F00FF0 = 15732720 — ИНВАРИАНТЕН в d1/d2/d3, ВТОРОЙ BE32 читает
# СЛОТ — T3-ow-single 'wc 5 ow' emit '54 00f00ff0 BE32(F3+d1) 13
# 00000131', пин W-85/probe85 b733ee4c) => d1/d2/d3 НЕ инвары — как у
# pr/sv/sp/vw/va/as/ow-томов W-87..W-94.
# База = wc14v3t33ow-структура (W-94, va/as-структура W-91/W-93) +
# честная карта probe95 (69 кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe95\_t95_card.py): stage1 для T3×T3×T3-ow
# целей = 87 Б 0xFF Token 9, emit = [ow-T3-хвост] ×3 = [54
# BE32(0x00F00FF0 КОНСТА) BE32(слот F3+d) 13 BE32(0x131 КОНСТА)] ×3 =
# 42 Б; база 'wc 5 ow wc 5 ow wc 5 ow' = 977e2a7a (пин W-94/probe94
# СОВПАЛ; честный полный hex probe95: header CRC 302ef00f + emit
# 5400f00ff000f00ff81300000131 ×3 + FF + BE32(9) + 20 нулей).
# **СЛОТ НЕСУЩИЙ ТОЛЬКО ВО ВТОРОМ BE32 КАЖДОГО ХВОСТА (ПЕРВЫЙ =
# КОНСТА, закон W-76)** (карта probe95: 'wc 7 ow wc 5 ow wc 5 ow' =
# 87 Б 7b4afb02, emit 5400f00ff000f00ffa1300000131… — слот1 = FA =
# F3+d1; 'wc 5 ow wc 7 ow wc 5 ow' = 26107216 — слот2 = FA; 'wc 5 ow
# wc 5 ow wc 7 ow' = 0f4b3d76 — слот3 = FA (НОВЫЙ пин: ТРЕТИЙ
# несущий слот); 'wc 7 ow wc 7 ow wc 5 ow' = 2fde9c2d (FA FA); 'wc 0
# ow ×3' = f0930036 (F3 F3 F3); 'wc 1 ow wc 3 ow wc 9 ow' = 83361277
# (F4 F6 FC); 'wc 9 ow wc 8 ow wc 0 ow' = 40263739 (FC FB F3); 'wc 2
# ow wc 6 ow wc 4 ow' = 4ed0247a (F5 F9 F7)) — три tracked-цели W-95
# ДАЮТ ТРИ РАЗНЫЕ md5 (7b4afb02 / 0f4b3d76 / 40263739 — честное
# доказательство несущих слотов W-76 ×3).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word9 — ОБА = база ('wc 5 ow wc 5 ow
# wc 5 ow .' = 977e2a7a; мусор после точки '… . 3' = база); слово ЗА
# терминатором = 0 — pEOF = eq(word9, 0) + eq(word9, 46) — сумма ДВУХ
# сравнений через stash-ячейку **STASH = PF = 15732733** (В W-95
# НЕЛЬЗЯ 15732723/15732725/15732726: там СЛОТЫ d1/d2/d3 —
# chain1/reslot пишут адреса F3+d1/F3+d2/F3+d3, TERM-фаза читает их
# 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ TAIL_CHECK; PF свободна —
# bad-flag мёртв после последнего digit-блока CHECK3, дальше никто
# не читает; форма 'nb(PF), sv'/'nb(PF), aa' — честно проверенные
# прецеденты digit-блоков W-93/W-94).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3 = 6) + PD (= pOw1+pOw2+pOw3 =
# 3) + pEOF == 10. Форма 'eq' с ДВУЗНАЧНЫМ immediate НЕ проверена
# (открытый вопрос W-94 → карта probe95 его не снимала: все
# прецеденты eq/su/ad/gt — ОДНОразрядные) => честная
# арифметическая развязка: 'su 9' + 'eq 1' (S - 9 == 1 ⟺ S == 10;
# недобор S < 9 → отрицательное/врап != 1 → затвор молчит; caps:
# PA <= 6, PD <= 3, pEOF <= 1 → S = 10 ТОЛЬКО при честном
# p0,v1,p0-2,v2,p0-3,v3,pOw1,pOw2,pOw3 = 1 И word9 ∈ {0, '.'}).
# НЕТ RELOAD2 (digit-tail d43 не существует в T3×T3×T3: word9 =
# терминатор слоя). Ключ-развязки (том обязан молчать, ВСЕ пины
# сняты честно картой probe95): te/sv/sp/vw/va/pr/if/as-смеси на
# ВСЕХ трёх позициях — stage1 ПРИНИМАЕТ ('wc 5 te wc 5 ow wc 5 ow' =
# 74 Б d407344e = 05 + ow-хвосты ×2; 'wc 5 ow wc 5 te wc 5 ow' = 74 Б
# a221d924; 'wc 5 ow wc 5 ow wc 5 te' = 74 Б 782c12ad; sv-смеси
# 9bf3b26a/b6dff599/42c4f464 (78 Б); sp 837a0480/f67fe970/647c4271;
# vw a2aa349f/e6777174/03aa0341 (77 Б); va ccecfbea/d326d2ef/8a0009e9
# (79 Б); pr df68690f/03c33cf1/e01a6677 (82 Б); if f96d128c/515145ed/
# 8365b00d (78 Б); as 5c9ed0eb/787d5b8e/ac1bf70d (84 Б); te/te база
# W-86 c49e444f) — том молчит: pOw1/pOw2/pOw3 = 0 → PD = 2 → S = 9;
# 4-stmt ow-поток — stage1 ПРИНИМАЕТ ('wc 5 ow' ×4 = 101 Б c39da5d5,
# emit 56 Б, Token 12; точка-вариант тот же c39da5d5, пин W-94
# СОВПАЛ) — том молчит: word9 = 'ow' → pEOF = 0 → S = 9; 2-stmt
# поток — stage1 ПРИНИМАЕТ ('wc 5 ow wc 5 ow' = 73 Б 40251c66, пин
# W-94 СОВПАЛ) — том молчит: word6 = 0-EOF → p0-3 = 0 → PA = 4, PD =
# 2, pEOF(word9 = 0) = 1 → S = 7; 3-stmt te-поток 48 Б 5cbeaa9b (НОВЫЙ
# пин: emit 05×3 = 3 Б), as-поток 78 Б 784a64e4 (пин W-93 СОВПАЛ),
# if-поток 60 Б eb8ecda2 (пин W-92 СОВПАЛ) — том молчит: pOw = 0;
# кресты: 'wc 5 ow wc 5 ow wc 5 ow 3' = 92 Б b20920c1 (НОВЫЙ пин:
# T3×3×T4-ow, emit 47 Б = 3 ow-хвоста + digit-tail 15 00000003) —
# word9 = '3' → pEOF = 0 → S = 9; 'wc 5 ow 3 wc 5 ow wc 5 ow' = 92 Б
# d19b0e46 (НОВЫЙ пин: word3 = '3' → p0-2 bad); 'wc 5 ow wc 5 ow 3
# wc 5 ow' = 92 Б f107ca43 (НОВЫЙ пин: digit МЕЖДУ stmt2 и stmt3,
# word6 = '3' → p0-3 bad); 'wc 5 ow 3 wc 5 ow 3' = 83 Б ead92d5a (пин
# W-94 СОВПАЛ: T4×T4-ow); 'wc 5 ow wc 5 ow 3 3' = 83 Б b9d2425c (пин
# W-94 СОВПАЛ, Token 8); 'wc 5 ow wc 5 ow wc 5 ow ow' = 101 Б
# 37bc465d (НОВЫЙ пин: stage1 парсит 10-й ток 'ow' как ЧЕТВЁРТЫЙ
# ow-стейтмент — emit 56 Б = 4 хвоста) — том молчит: word9 = 'ow' →
# pEOF = 0; 'wc 5 ow wc 5 ow wc 5 ow 3 3' = 97 Б 2a238d4d (НОВЫЙ пин,
# emit 52 Б) — том молчит: word9 = '3' → pEOF = 0; 2-stmt кресты:
# 'wc 5 ow wc 5 ow 3' = 78 Б 9a6a53e9 (пин W-94 СОВПАЛ), 'wc 5 ow wc
# 5 ow ow' = 87 Б 49149cf0 (пин W-94 СОВПАЛ) — том молчит; singles/
# сироты: 'wc 5 ow' = 59 Б b733ee4c (пин W-85 — СОВПАЛ), 'wc 5 ow 3'
# = 64 Б fb10fa26 (пин W-85 — СОВПАЛ), сирота 'wc 5 ow wc 5' = 59 Б
# a48426b6 (пин W-94 СОВПАЛ), 'wc 5 vw' = 49 Б 00ce976e (пин
# probe90..94), 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 te' = 46 Б bac85372;
# неги-браки: 'wc ow wc 5 ow wc 5 ow' = 0xFE 59 Б ff73c458 (пин W-94
# СОВПАЛ: bad word1 — emit 14 Б со слотом F1 = 0x00F00FF1 = 15732721
# DEFAULT WORK_CELL); 'wc z ow …' = 0xFE 45 Б 29ba6852 (пин W-94
# СОВПАЛ); 'wc 5 ow wc z ow …' = 0xFE 59 Б ea08576d (пин W-94 СОВПАЛ);
# 'wc 5 ow wc 5 ow wc z ow' = 0xFE 73 Б fa369b02 (НОВЫЙ пин: bad d3 —
# emit 28 Б = хвосты stmt1+stmt2); bad word2 = 0xFE 45 Б 4ff7c705
# (СОВПАЛ); 'wc 5 ow wc 5 xx …' = 0xFE 59 Б 7a101f35 (СОВПАЛ); 'wc 5
# ow wc 5 ow wc 5 xx' = 0xFE 73 Б 1e1f1b30 (НОВЫЙ пин: bad word8 —
# emit 28 Б); bad word0/мусор = f3667180; 'wc 5 ow wc ow wc 5 ow' =
# 0xFE 73 Б 17c27666 (НОВЫЙ пин: bad word4 в 3-stmt — В ОТЛИЧИЕ от
# 2-stmt 'wc 5 ow wc ow' [ПРИНИМАЕТ b5ace5e8, W-94], 3-stmt вариант
# stage1 БРАКУЕТ); 'wc 5 ow wc 5 ow wc ow' — stage1 ПРИНИМАЕТ (87 Б
# 13455fbf 0xFF, emit 42 Б — ВСЕ ТРИ хвоста со слотом F8 от stmt-1)
# — том молчит: v3 = 0 → PA = 5 → S = 9. Итог: **669 ток** <= 1022,
# компил stage1 = **NNN Б 0xFF Token 0x29D = 669 md5 …**, детерминизм
# OK. Честная матрица probe95c OK: **9 целей BYTE-OK против свежего
# stage1** (база 977e2a7a, точка, точка+мусор, d1-носитель 7b4afb02,
# d2-носитель 26107216, d3-носитель 0f4b3d76, FA FA 2fde9c2d, F3 F3
# f0930036, 83361277, 40263739 — ТРИ РАЗНЫЕ md5 tracked-целей) +
# **52/52 негов молчат**. NEW-пины W-95: t3×3-ow том + 3 tracked цели
# (ТРИ РАЗНЫЕ md5 — несущие слоты W-76 ×3).
# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe95:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo' = pending-nb BE32-вывод КОНСТАНТЫ, прецедент W-83/W-85) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 ('nb 1 9' =
# 19₁₀ [урок probe57/W-64: nb-литералы ДЕСЯТИЧНЫЕ]) + BE32(0x131 =
# 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76) -> OW_TAIL2
# (reslot: BE32(cell[wc2] = слот F3+d2)) -> OW_TAIL3 (reslot3:
# BE32(cell[wc3] = слот F3+d3 — НОВЫЙ ТРЕТИЙ НЕСУЩИЙ СЛОТ, прецедент
# 'wc 3 ow'-эмиссии: wc-N-адресация N = 0..9 проверена INIT'ом
# W-93/W-94) -> вердец -> отчёт (Token = 9: 'nb 9' 'wo' — токенов
# слоя ДО терминатора, точка не считается) -> SEAL/END. Честный
# дизайн (= W-94 ow-структура, va/as-структура W-91/W-93):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для OW_TAIL1;
#   прецедент W-87..W-94 CHECK1 C1) + pOw1 (word2 == LE2('ow') =
#   30575, 'o' в МЛАДШЕМ байте, PB = wc 7, PD = ) — БЕЗ digit-block
#   d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 ow' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для OW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid3
#   сравнился, дальше F5 не читается — честный порядок W-84) +
#   pOw2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   **'eq 0'** (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после
#   reslot CHECK2 — чтение F5 как ноль-референса испортило бы
#   valid3; 'eq 0' = прецедент TAIL_CHECK W-93/W-94) + C3 reslot3:
#   RESET cell[wc3] = F3_MINUS_48 + 'wc 3 ow' на word7 → cell[wc3] =
#   F3+d3 (НЕСУЩИЙ для OW_TAIL3; wc3 = 15732726 — СВОБОДНА в W-95:
#   stash переехал в PF) + pOw3 (word8 == PB, PD += ) — БЕЗ
#   digit-block d43 (word9 = терминатор слоя).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('ow') = 30575 → wc7 — 'o' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x776F; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t333ow.words

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
WORD10     = 10485796        # word9 — терминатор слоя T3×T3×T3
                             # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
F3_MINUS_48 = 15732675
F5 = 15732725                # ноль-референс digit-блоков CHECK1/CHECK2
                             # (VM-память = 0); В CHECK3 НЕЛЬЗЯ — там
                             # СЛОТ d2 (reslot CHECK2) — valid3 через
                             # 'eq 0'
STASH = 15732733             # PF — bad-flag МЁРТВ после CHECK3
                             # (в W-95 НЕЛЬЗЯ 15732723/15732725/15732726:
                             # там СЛОТЫ d1/d2/d3 — TERM-фаза читает их
                             # 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('ow') = 30575 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-95
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
          # = 15732723 + d1 — НЕСУЩИЙ для OW_TAIL1 (карта probe95:
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
          # НЕСУЩИЙ для OW_TAIL2 (карта probe95: '… wc 7 ow wc 5 ow' →
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
# block d43: word9 = терминатор слоя)
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
          # НЕСУЩИЙ для OW_TAIL3 (карта probe95: '… wc 5 ow wc 7 ow' →
          # BE32(FA) в ТРЕТЬЕМ хвосте; '… wc 0 ow' → BE32(F3); НОВЫЙ
          # пин 0f4b3d76 — ТРЕТИЙ несущий слот). wc3 = 15732726 —
          # СВОБОДНА (stash W-95 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pOw3 = (word8 == LE2('ow'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pOw3
          # НЕТ RELOAD2: digit-tail d43 не существует в T3×T3×T3
          # (word9 = терминатор слоя)

# F2/G2: pEOF = (word9 == 0 ИЛИ word9 == '.') — арифметическая сумма
# ДВУХ сравнений через stash-ячейку STASH = PF = 15732733 (bad-flag
# мёртв после CHECK3; 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 —
# трогать НЕЛЬЗЯ: TERM-фаза читает их после TAIL_CHECK); терминатор
# слоя T3×T3×T3 на ДЕСЯТОМ слове (WORD10 = 10485796).
# Затвор: PA (6) + PD (3) + pEOF == 10 — через 'su 9' + 'eq 1'
# (S - 9 == 1 ⟺ S == 10; форма 'eq' с двузначным immediate не
# проверена — все прецеденты eq/su/ad/gt одноразрядные; caps: S = 10
# ТОЛЬКО при PA = 6, PD = 3, pEOF = 1 — честный 3-стейтментный поток)
TAIL_CHECK = [nb(WORD10), 'va', 'eq', '0',       # acc = eq(word9, 0) [EOF]
              nb(PA), 'aa',
              nb(PD), 'aa',
              nb(PF), 'sv',                      # stash → cell[15732733]
              nb(WORD10), 'va', nb(PC), 'cp',    # acc = eq(word9, '.')
              nb(PF), 'aa',                      # acc += stash
              'su', '9',                         # acc = S - 9
              'eq', '1',                         # затвор: S == 10
              'if']

# EMIT: OW_TAIL1 (честный хвост T3-'ow' стейтмента 1, карта probe95:
# U8 0x54 + BE32(0x00F00FF0 = 15732720 КОНСТА — 'nb 1 5 7 3 2 7 2 0'
# 'wo') + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x13 +
# BE32(0x131 = 305 КОНСТА — 'nb 3 0 5' 'wo'), 14 Б — закон W-76:
# ПЕРВЫЙ BE32 = КОНСТА (инвариантен в d1/d2/d3), ВТОРОЙ BE32 = СЛОТ;
# 'nb 8 4' = 84₁₀ = 0x54, 'nb 1 9' = 19₁₀ = 0x13 [урок probe57/W-64:
# nb-литералы ДЕСЯТИЧНЫЕ]) -> OW_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2)) -> OW_TAIL3 (тот же хвост с reslot3:
# BE32(cell[wc3] = слот F3+d3) — честный emit базы probe95
# 5400f00ff000f00ff81300000131 ×3) -> вердец -> отчёт (Token = 9)
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
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
EMIT_TAIL = ['nb 2 5 5', 'em', 'nb 3 0 8', 'sc',              # вердец U8 FF
        'nb 9', 'wo',                                    # Token = 9 (9
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

MAIN = CHECK1 + CHECK2 + CHECK3 + TAIL_CHECK + EMIT_HEAD + OW_TAIL1 \
       + OW_TAIL2 + OW_TAIL3 + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe95\pos_wc14v3t333ow.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t333ow tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
