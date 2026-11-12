# -*- coding: utf-8 -*-
# Сборщик честного ЧЕТЫРЁХстейтментного тома
# 'wc d as wc d as wc d as wc d as'
# Shape-T3×T3×T3×T3-as (веха-23, спринт 78, W-98, TKT-052): СТРИМ —
# третья ЧЕТЫРЁХстейтментная T3-форма. ВСЕ ЧЕТЫРЕ хвоста НЕСУЩИЕ
# (as-хвост 11 Б — U8 0x12 + U8 0x15 + BE32(слот) + U8 0x55 +
# BE32(слот), закон W-75: ОБА BE32 читают СЛОТ F3+d — T3-as-single
# 'wc 5 as' emit '12 15 BE32(F3+d) 55 BE32(F3+d)', карта probe98:
# 'wc 7 as' → BE32(0x00F00FFA) В ОБОИХ BE32, пин probe96/W-93
# 1176c0df/probe98 3f6d8893) => d1/d2/d3/d4 НЕ инвары — как у
# ow-тома W-96 (но В ОТЛИЧИЕ от него ОБА BE32 — не только второй).
# База = wc14v3t3333ow-структура (W-96) + честная карта probe98 (86
# кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe98\_t98_card.py):
# stage1 для T3×T3×T3×T3-as целей = 89 Б 0xFF Token 12, emit =
# [as-T3-хвост] ×4 = [12 15 BE32(слот F3+d) 55 BE32(слот F3+d)] ×4 =
# 44 Б; база 'wc 5 as wc 5 as wc 5 as wc 5 as' = 3f6d8893 (пин
# probe96 СОВПАЛ; честный полный hex probe98: header CRC d5004ce8 +
# emit 121500f00ff85500f00ff8 ×4 + FF + BE32(12) + 20 нулей).
# **ОБА BE32 НЕСУЩИЕ В КАЖДОМ ХВОСТЕ (закон W-75 ×4 ×2 BE32)** (карта
# probe98: 'wc 7 as …' = 89 Б c694b1d8, слот1 = FA В ОБОИХ BE32; '… wc
# 7 as …' = 1d8684fa, слот2 = FA; '… wc 7 as …' = ffef3074, слот3 =
# FA; '… wc 5 as wc 7 as' = 9fa48f7f — НОВЫЙ пин: слот4 = FA; 'wc 7
# as' ×3 + 'wc 5 as' = 568057c3 (FA FA FA); 'wc 0 as' ×4 = d9d1f1fa
# (F3 F3 F3 F3); 'wc 1 as wc 3 as wc 5 as wc 9 as' = 343768e9 (F4 F6
# F8 FC); 'wc 9 as wc 8 as wc 0 as wc 1 as' = 421dd1d2 (FC FB F3 F4);
# 'wc 2 as wc 6 as wc 4 as wc 8 as' = 703fbf1e (F5 F9 F7 FB)) —
# три tracked-цели W-98 ДАЮТ ТРИ РАЗНЫЕ md5 (честное доказательство
# несущих слотов W-75 ×4 ×2 BE32).
# ТРИ reslot'а в CHECK-фазе (структура W-96): chain1 d1→wc0 (CHECK1) +
# reslot d2→wc2 (CHECK2) + reslot3 d3→wc3 (CHECK3); **СЛОТ4 =
# переиспользование wc0 в EMIT-фазе (RESLOT4 между AS_TAIL3 и
# AS_TAIL4)** — свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ d1/d2/d3,
# wc1 = INIT F4, wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA,
# wc7 = PB, wc8 = PC, wc9 = PD; ОБА BE32 читают ОДНУ ячейку —
# переиспользование после чтения слота1 AS_TAIL1 (emit-порядок TAIL1
# → TAIL2 → TAIL3 → RESLOT4 → TAIL4), CHECK-фазы завершены ДО
# затвора — безопасно (ИДЕОМ W-96, прецедент снят).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word12 (ТРИНАДЦАТОЕ слово) — ОБА =
# база (карта probe98 кейсы 1/2 = 3f6d8893); pEOF = eq(word12, 0) +
# eq(word12, 46) через stash-ячейку STASH = PF = 15732733 (15732723/
# 15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их 'wc 0
# as'/'wc 2 as'/'wc 3 as' ПОСЛЕ TAIL_CHECK; PF = bad-flag stash
# W-95/W-96 — мёртв после последнего digit-блока CHECK4).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4 = 8) + PD (=
# pAs1+pAs2+pAs3+pAs4 = 4) + pEOF == 13 — 'su 9' + 'su 3' + 'eq 1'
# (S − 12 == 1 ⟺ S == 13; все immediate ОДНОразрядные; caps: S = 13
# ТОЛЬКО при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,pAs1,pAs2,pAs3,
# pAs4 = 1 И word12 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d44 не
# существует в T3×T3×T3×T3: word12 = терминатор слоя).
# Ключ-развязки (том обязан молчать, ВСЕ пины сняты честно картой
# probe98): te/sv/sp/vw/va/pr/if/ow-смеси на ВСЕХ ЧЕТЫРЁХ позициях —
# stage1 ПРИНИМАЕТ (pr c4af4ef1/61844980/686b5def/25f5573e; sv
# aaec62e2/af3216fe/a4006ddb/94ec66dd; sp 24db195e/ea2f9efe/
# b8d8c2b6/67bb1104; vw f638580c/ca410512/ac04e8f3/997d8b82; va
# 905e39c4/2e800850/e0c7bb65/e1f08a8d; ow 9fdb77c0/fe16a134/
# 1dc38b48/9016c376; if 96db1ea3/078dc270/c0822d40/dc008ec0; te
# 9dde2834/d370ac58/410eb76d/efedc9af) — том молчит: pAsX = 0 →
# PD = 3 → S = 12; 4-стейтментные потоки других kinds — stage1
# ПРИНИМАЕТ (te ×4 = 49 Б 40dc0e48, emit 05×4 = 4 Б — пин W-97; sv ×4
# = 65 Б 05df0915, 20 Б; sp ×4 = c02a9b43; vw ×4 = 61 Б 8669285e,
# 16 Б; va ×4 = 69 Б 917128ff, 24 Б; pr ×4 = 81 Б 34f4a890, 36 Б; ow
# ×4 = 101 Б c39da5d5, 56 Б — пин W-94) — том молчит: PD = 0; if ×4 —
# stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ) — том молчит;
# 5-stmt as-поток — stage1 ПРИНИМАЕТ ('wc 5 as' ×5 = 100 Б 334d2504,
# emit 55 Б = 5 хвостов, Token 15; точка-вариант тот же) — том
# молчит: word12 = 'wc' → pEOF = 0 → S = 12; 6-stmt = 111 Б
# 868904cb, emit 66 Б — S = 12; 3-stmt поток = 78 Б 784a64e4 (НОВЫЙ
# пин) — том молчит: word9 = 'as' → p0-4 = 0 → PA = 6, PD = 3,
# pEOF(word12 = 0) = 1 → S = 10; 2-stmt = 67 Б 80a53bb1 (НОВЫЙ пин) —
# S = 7; кресты: 'wc 5 as' ×4 + '3' = 94 Б f650c264 (НОВЫЙ пин: emit
# 49 Б = 4 as-хвоста + digit-tail 15 00000003) — word12 = '3' →
# pEOF = 0; 'wc 5 as 3 wc 5 as wc 5 as wc 5 as' = 94 Б d972ac1b
# (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad);
# 'wc 5 as wc 5 as 3 wc 5 as wc 5 as' = 94 Б 3eda1b21 (НОВЫЙ пин:
# digit-tail после хвоста 2 — word6 = '3' → p0-3 bad); 'wc 5 as wc 5
# as wc 5 as 3 wc 5 as' = 94 Б cbd55167 (НОВЫЙ пин: digit МЕЖДУ
# stmt3 и stmt4, word9 = '3' → p0-4 bad); 'wc 5 as' ×4 + 'as' = 100 Б
# ad71415d (НОВЫЙ пин: stage1 парсит 13-й ток 'as' как ПЯТЫЙ
# as-стейтмент — emit 55 Б) — том молчит: word12 = 'as' → pEOF = 0;
# 'wc 5 as' ×4 + '3 3' = 99 Б aa1b62f9 (НОВЫЙ пин, emit 54 Б =
# 4 хвоста + digit-tail ×2); 2-stmt кресты 'wc 5 as 3 wc 5 as 3' =
# 77 Б 5fb8d6c8 (НОВЫЙ пин), 'wc 5 as wc 5 as 3 3' = 77 Б 76767951
# (НОВЫЙ пин), 'wc 5 as wc 5 as 3' = 72 Б d0814e42 (НОВЫЙ пин),
# 'wc 5 as wc 5 as as' = 78 Б 52eb2ae5 (НОВЫЙ пин: 7-й ток 'as' —
# stage1 эмитит 3 хвоста) — том молчит: word5 = 'as' → pAs2 = 1, но
# p0-3 = 0, pAs3 = 0 → PA = 4, PD = 2, pEOF = 1 → S = 7;
# singles/сироты: 'wc 5 as' = 56 Б 1176c0df (пин W-93 СОВПАЛ), 'wc 5
# as 3' = 61 Б cbb9ba26 (НОВЫЙ пин: emit 16 Б = as-хвост +
# digit-tail), сирота 'wc 5 as wc 5' = 56 Б 59a9f18d (НОВЫЙ пин:
# emit 11 Б), 'wc 5 vw' = 49 Б 00ce976e (пин), 'wc 5 sv' = 50 Б
# 6a16ae85 (пин); неги-браки: 'wc ow wc 5 as wc 5 as wc 5 as' = 0xFE
# 59 Б ff73c458 (пин СОВПАЛ: bad word1); bad d1 = 0xFE 45 Б
# 29ba6852 (СОВПАЛ); bad d2 = 0xFE 56 Б 26811567 (НОВЫЙ пин: emit
# 11 Б = as-хвост1); bad d3 = 0xFE 67 Б 0c157e0c (НОВЫЙ пин: emit
# 22 Б); bad d4 = 0xFE 78 Б 6ff548fa (НОВЫЙ пин: emit 33 Б); bad
# word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad word5 = 0xFE 56 Б
# a1b1f926 (НОВЫЙ пин); bad word8 = 0xFE 67 Б 88af7b15 (НОВЫЙ пин);
# bad word11 = 0xFE 78 Б 71e766e1 (НОВЫЙ пин); bad word0/мусор =
# f3667180 (СОВПАЛ); 'wc 5 as wc ow wc 5 as wc 5 as' = 0xFE 70 Б
# 2577775d (НОВЫЙ пин: bad word4 'ow' — emit 25 Б = as-хвост1 +
# ow-хвост F8 — stage1 БРАКУЕТ); 'wc 5 as wc 5 as wc ow wc 5 as' =
# 0xFE 81 Б dd5bec0f (НОВЫЙ пин: bad word7 — emit 36 Б); 'wc 5 as wc
# 5 as wc 5 as wc ow' — stage1 ПРИНИМАЕТ (92 Б 0xFF dd6dec99, НОВЫЙ
# KEY-пин: emit 47 Б = 3 as-хвоста + ow-хвост со слотами F8 =
# 0x00F00FF8 DEFAULT WORK_CELL — word10 = 'ow' НЕ цифра → слот
# дефолт) — том молчит: v4 = 0 → PA = 7, pAs4 = 0 → S = 11.
# Итог: **890 ток** <= 1022, компил stage1 =
# **1286 Б 0xFF Token 0x37A = 890 md5 e9d085da**, детерминизм OK. Честная
# матрица probe98c OK: **15 целей BYTE-OK против свежего stage1**
# (база 3f6d8893 = пин probe96, точка, точка+мусор, 9 носителей —
# РАЗНЫЕ md5 несущих слотов W-75 ×4 ×2 BE32; + 3 tracked-цели) +
# **74/74 негов молчат**. NEW-пины W-98: t3×3×3×3-as том + 3 tracked
# цели (РАЗНЫЕ md5 — несущие слоты W-75 ×4 ×2 BE32).
# EMIT: AS_TAIL1 (честный хвост T3-'as' стейтмента 1, карта probe98:
# U8 0x12 ('nb 1 2' = 18₁₀) + U8 0x15 ('nb 1 5' = 21₁₀) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x55 ('nb 5 5' =
# 85₁₀) + BE32(cell[wc0] = ТОТ ЖЕ СЛОТ — второй BE32, закон W-75:
# ОБА BE32 читают F3+d), 11 Б) -> AS_TAIL2 (reslot: BE32(cell[wc2] =
# слот F3+d2) ОБА) -> AS_TAIL3 (reslot3: BE32(cell[wc3] = слот
# F3+d3) ОБА) -> RESLOT4 (переиспользование wc0: RESET cell[wc0] =
# F3_MINUS_48 + 'wc 0 as' на word10 → cell[wc0] = F3+d4) ->
# AS_TAIL4 (BE32(cell[wc0] = слот F3+d4) ОБА — ЧЕТВЁРТЫЙ НЕСУЩИЙ
# СЛОТ В ОБОИХ BE32; честный emit базы probe98
# 121500f00ff85500f00ff8 ×4) -> вердец -> отчёт (Token = 12: 'nb 1 2'
# 'wo' — токенов слоя ДО терминатора, точка не считается) -> SEAL/
# END. Честный дизайн (= W-96 ow-структура, хвосты as):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для AS_TAIL1
#   В ОБОИХ BE32) + pAs1 (word2 == LE2('as') = 29537, 'a' в МЛАДШЕМ
#   байте, PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc'
#   stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для AS_TAIL2 В ОБОИХ BE32; wc2 = F5 — ПОСЛЕ последнего
#   F5-cp: valid2 сравнился, дальше F5 не читается — честный порядок
#   W-84/W-96) + pAs2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после reslot
#   CHECK2; 'eq 0' = прецедент TAIL_CHECK W-93/W-94/W-96) + C3
#   reslot3: RESET cell[wc3] = F3_MINUS_48 + 'wc 3 as' на word7 →
#   cell[wc3] = F3+d3 (НЕСУЩИЙ для AS_TAIL3 В ОБОИХ BE32; wc3 =
#   15732726 СВОБОДНА: stash в PF) + pAs3 (word8 == PB, PD += ) —
#   БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — валид-сравнение через
#   'eq 0' (F5 отравлен) + pAs4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = терминатор слоя) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('as') = 29537 → wc7 — 'a' в МЛАДШЕМ
# байте [урок W-65/W-67], 0x6173; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t3333as.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('as' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('as' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('as' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('as' stmt-4)
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
                             # (НЕЛЬЗЯ 15732723/15732725/15732726: там
                             # СЛОТЫ d1/d2/d3 — TERM-фаза читает их
                             # 'wc 0 as'/'wc 2 as'/'wc 3 as' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('as') = 29537 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-98
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(29537), 'ne', 'wc', '7', 'sv',           # 'as' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для AS_TAIL1 В ОБОИХ BE32
          # (карта probe98: 'wc 7 as …' → BE32(FA) ×2)
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pAs1 = (word2 == LE2('as'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pAs1

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
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid2 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid2
          # C2: честный reslot chain2: RESET cell[wc2] = F3 минус 48,
          # затем 'wc 2 as' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для AS_TAIL2 В ОБОИХ BE32 (карта probe98: '… wc 7
          # as …' → BE32(FA) ×2 во ВТОРОМ хвосте). wc2 = F5 — ПОСЛЕ
          # последнего F5-cp (valid2 сравнился выше; дальше F5 не
          # читается CHECK1/CHECK2 — честный порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pAs2 = (word5 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs2

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
          # valid3 = (bad4 == 0) через 'eq 0' — НЕ через 'nb(F5), cp':
          # F5 = wc2 = СЛОТ d2 после reslot CHECK2 ('eq 0' = прецедент
          # TAIL_CHECK W-93/W-94/W-96)
          nb(PF), 'va', 'eq', '0',
          'wc', '6', 'as',              # PA += valid3
          # C3: честный reslot chain3: RESET cell[wc3] = F3 минус 48,
          # затем 'wc 3 as' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для AS_TAIL3 В ОБОИХ BE32 (карта probe98: '… wc 7
          # as …' → BE32(FA) ×2 в ТРЕТЬЕМ хвосте). wc3 = 15732726 —
          # СВОБОДНА (stash W-96/W-98 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pAs3 = (word8 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs3
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
          # valid4 = (bad5 == 0) через 'eq 0' — НЕ через 'nb(F5), cp':
          # F5 = wc2 = СЛОТ d2 (отравлен reslot CHECK2; 'eq 0' =
          # прецедент CHECK3 W-95/W-96/TAIL_CHECK)
          nb(PF), 'va', 'eq', '0',
          'wc', '6', 'as',              # PA += valid4
          # БЕЗ reslot4: свободных wc-ячеек НЕТ — слот4
          # материализуется RESLOT4 в EMIT-фазе (переиспользование
          # wc0 ПОСЛЕ AS_TAIL3)
          # D4: pAs4 = (word11 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs4
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

# EMIT: AS_TAIL1 (честный хвост T3-'as' стейтмента 1, карта probe98:
# U8 0x12 ('nb 1 8' = 18₁₀) + U8 0x15 ('nb 2 1' = 21₁₀) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x55 ('nb 8 5' =
# 85₁₀) + BE32(cell[wc0] = ТОТ ЖЕ СЛОТ — второй BE32, закон W-75:
# ОБА BE32 читают F3+d; КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc'
# [sc = syscall FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; урок
# W-96: 'em' ТОЛЬКО кладёт константу в ячейку, без 'sc' байта НЕТ;
# nb-литералы ДЕСЯТИЧНЫЕ — урок probe57/W-64]) -> AS_TAIL2 (тот же
# хвост с reslot: BE32(cell[wc2] = слот F3+d2) ОБА) -> AS_TAIL3 (тот
# же хвост с reslot3: BE32(cell[wc3] = слот F3+d3) ОБА) -> RESLOT4
# (переиспользование wc0: RESET cell[wc0] = F3_MINUS_48 + 'wc 0 as'
# на word10 → cell[wc0] = F3+d4 — слот1 УЖЕ прочитан AS_TAIL1 (ОБА
# BE32), CHECK-фазы завершены; ИДЕОМ = INIT + CHECK1 C1) -> AS_TAIL4
# (тот же хвост с переиспользованным wc0: BE32(cell[wc0] = слот
# F3+d4) ОБА — честный emit базы probe98 121500f00ff85500f00ff8 ×4)
# -> вердец -> отчёт (Token = 12)
AS_TAIL1 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '0', 'ow',                          # BE32(слот F3+d1 — chain1)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '0', 'ow']                          # BE32(слот F3+d1 — ВТОРОЙ BE32)
AS_TAIL2 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '2', 'ow',                          # BE32(слот F3+d2 — reslot)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '2', 'ow']                          # BE32(слот F3+d2 — ВТОРОЙ BE32)
AS_TAIL3 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '3', 'ow',                          # BE32(слот F3+d3 — reslot3)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '3', 'ow']                          # BE32(слот F3+d3 — ВТОРОЙ BE32)
# RESLOT4 = переиспользование wc0 для слота d4 (ИДЕОМ W-96):
# RESET cell[wc0] = F3_MINUS_48, затем 'wc 0 as' на word10 (d4)
# → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для AS_TAIL4 В ОБОИХ BE32
# (карта probe98: '… wc 5 as wc 7 as' → BE32(FA) ×2 в ЧЕТВЁРТОМ
# хвосте — НОВЫЙ пин 9fa48f7f: ЧЕТВЁРТЫЙ несущий слот; '… wc 0 as'
# → BE32(F3) ×2).
# Слот1 уже прочитан AS_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
AS_TAIL4 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '0', 'ow',                          # BE32(слот F3+d4 — RESLOT4)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — ВТОРОЙ BE32)
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
       + AS_TAIL1 + AS_TAIL2 + AS_TAIL3 + RESLOT4 + AS_TAIL4 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe98\pos_wc14v3t3333as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t3333as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
