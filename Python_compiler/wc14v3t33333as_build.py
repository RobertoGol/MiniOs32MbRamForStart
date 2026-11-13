# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d as wc d as wc d as wc d as wc d as'
# Shape-T3×5-as (веха-23, спринт 86, W-106, TKT-052): СТРИМ — ТРЕТЬЯ
# ПЯТИстейтментная T3-форма (после ow W-104, te W-105). ВСЕ ПЯТЬ
# хвостов НЕСУЩИЕ (as-хвост 11 Б — U8 0x12 + U8 0x15 + BE32(слот
# F3+d) + U8 0x55 + BE32(слот F3+d), закон W-75: ОБА BE32 читают СЛОТ
# — В ОТЛИЧИЕ от ow W-76 [несущий только ВТОРОЙ BE32]; T3-as-single
# 'wc 5 as' emit '12 15 BE32(F3+d) 55 BE32(F3+d)', пин W-93 1176c0df)
# => d1..d5 НЕ инвары — как у ow-тома W-104 (но В ОТЛИЧИЕ от него ОБА
# BE32 — не только второй).
# База = wc14v3t3333as-структура (W-98, as-структура = ow-структура
# W-96 с хвостами as) + честная карта probe106 (100 кейсов, свежий
# stage1 на каждую цель,
# G:\...\Temp\opencode\probe106\_t106_card.py): stage1 для T3×5-as
# целей = 100 Б 0xFF Token 15, emit = [as-T3-хвост] ×5 =
# [12 15 BE32(слот F3+d) 55 BE32(слот F3+d)] ×5 = 55 Б; база 'wc 5 as'
# ×5 = 334d2504 (пин probe98-карты СОВПАЛ — снята как «5-stmt as-поток»;
# честный полный hex probe106: header CRC 7f1a7522 + emit
# 121500f00ff85500f00ff8 ×5 + FF + BE32(15) + 20 нулей).
# **9 НОСИТЕЛЕЙ = 9 РАЗНЫХ md5 (честное доказательство несущих слотов
# W-75 ×5 ×2 BE32)**: 'wc 7 as' на каждой из ПЯТИ позиций = c73a0429
# (слот1 = FA В ОБОИХ BE32)/9de57133 (слот2)/6febf14c (слот3)/295c98d6
# (слот4 = RESLOT4)/0bec2c13 (слот5 = RESLOT5 — ПЯТЫЙ несущий НОВЫЙ
# KEY, прецедент W-104 ow 0bfc66a5); 'wc 7 as' ×4 + 'wc 5 as' =
# 47ccf02d (FA FA FA FA F8); 'wc 0 as' ×5 = cda40d67 (F3 ×5); 'wc 1 as
# wc 3 as wc 5 as wc 9 as wc 5 as' = dc71522a (F4 F6 F8 FC F8); 'wc 9
# as wc 8 as wc 0 as wc 1 as wc 5 as' = e16eb462 (FC FB F3 F4 F8) —
# tracked-цели W-106 ДАЮТ ТРИ РАЗНЫЕ md5 (несущие слоты).
# ПЯТЬ reslot'ов — chain1 d1→wc0 (CHECK1) + reslot d2→wc2 (CHECK2) +
# reslot3 d3→wc3 (CHECK3) + RESLOT4 d4→wc0 (переиспользование wc0,
# W-96/W-98) + RESLOT5 d5→wc2 (переиспользование wc2 — W-104);
# свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ d1/d2/d3, wc1 = INIT F4,
# wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA, wc7 = PB,
# wc8 = PC, wc9 = PD; ОБА BE32 читают ОДНУ ячейку — переиспользование
# после чтения слота AS_TAIL1 (ОБА BE32; emit-порядок TAIL1 → TAIL2 →
# TAIL3 → RESLOT4 → TAIL4 → RESLOT5 → TAIL5), CHECK-фазы завершены ДО
# затвора — безопасно (ИДЕОМ W-96/W-98/W-104, прецедент снят).
# ЧЕСТНОЕ СЖАТИЕ W-104: CHECK1/CHECK2 — валид через 'gt 9' + stash PF +
# cp F5 (F5 = wc2 чист ДО reslot CHECK2); CHECK3/CHECK4/CHECK5 —
# 'gt 9' + 'eq 0' НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0'
# сравнивает acc, sv/va acc не портят — снято с CtOs-Emu/ctos_vm.py,
# доказано regr104; F5 отравлен reslot CHECK2 — 'eq 0', а не cp).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база (карта probe106 кейсы 1/2 = 334d2504; мусор после точки '… . 3'
# = база кейс 2); pEOF = eq(word15, 0) + eq(word15, 46) через stash-
# ячейку STASH = PF = 15732733 (bad-flag МЁРТВ после CHECK5;
# 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их
# 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ TAIL_CHECK).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pAs1+pAs2+pAs3+pAs4+pAs5 = 5) + pEOF == 16. Форма W-104: 'su 9' +
# 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; недобор S < 15 →
# затвор молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 → S = 16 ТОЛЬКО
# при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,pAs1..pAs5 = 1 И
# word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не существует в
# T3×5: word15 = терминатор слоя). Ключ-развязки (том обязан молчать,
# ВСЕ пины сняты честно картой probe106): ow/sv/sp/vw/va/pr/if/te-
# смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ, ВСЕ 40 НОВЫЕ пины
# as-роли (ow e0ac2307/4ad89f14/4c62d21a/b311ce14/80695b83; sv
# 81699771/2e5c5581/671490f2/d6910b7d/f20123ae; sp c7810996/eed220ff/
# 18d9d6a7/d28b422c/5a748b61; vw e5b6ea9d/e86e17af/3e968d59/98b664de/
# 80655b58; va 47ed436e/3832dbe8/ca03b0d4/d8fe4ff8/961b9d30; pr
# a622273c/99f9e3c5/a357f53b/bb6bbc62/05de93d4; if 53fdfaf7/32e34a2c/
# 14ad34e5/01ffe299/b515181f; te be6593c7/5b852876/78ca42ec/350650b2/
# b9944a6d) — том молчит: pAsX = 0 → PD = 4 → S <= 15; 4-стейтментные
# потоки других kinds — stage1 ПРИНИМАЕТ (as ×4 = 89 Б 3f6d8893, пин
# W-98 СОВПАЛ, emit 44 Б; te ×4 = 49 Б 40dc0e48, пин W-97 СОВПАЛ,
# emit 05×4; sv ×4 = 65 Б 05df0915; sp ×4 = 65 Б c02a9b43; vw ×4 = 61
# Б 8669285e; va ×4 = 69 Б 917128ff; pr ×4 = 81 Б 34f4a890; ow ×4 =
# 101 Б c39da5d5, пин W-96 СОВПАЛ) — том молчит: word12 = 'as'/'te'/
# 'ow' → pEOF = 0 (PD = 0 у чужих); if ×4 — stage1 БРАКУЕТ (0xFE 60 Б
# ebe049f9, пин W-92 СОВПАЛ) — том молчит; 6-stmt as-поток — stage1
# ПРИНИМАЕТ ('wc 5 as' ×6 = 111 Б 868904cb [пин W-98 СОВПАЛ], emit
# 66 Б = 6 хвостов, Token 18; точка-вариант тот же) — том молчит:
# word15 = 'wc' → pEOF = 0 → S = 15; 7-stmt = 122 Б fdd1c882 (НОВЫЙ
# пин, emit 77 Б, Token 21) — S = 15; 4-stmt ow-поток = 101 Б
# c39da5d5 (пин W-96 СОВПАЛ) — том молчит; 3-stmt = 87 Б 977e2a7a
# (пин W-95 СОВПАЛ) — S = 10; 2-stmt = 73 Б 40251c66 (пин W-94
# СОВПАЛ) — S = 7; кресты: 'wc 5 as' ×5 + '3' = 105 Б 233bd8ca
# (НОВЫЙ пин: emit 60 Б = 5 as-хвостов + digit-tail 15 00000003,
# Token 16) — word15 = '3' → pEOF = 0; 'wc 5 as 3 …' = 105 Б f082606d
# (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad);
# '… wc 5 as 3 …' = 105 Б bda1645b (word6), '… 3 …' = 105 Б 908a3735
# (word9), '… wc 5 as 3 wc 5 as' = 105 Б ce7aabbf (word12) — НОВЫЕ
# пины: digit МЕЖДУ стейтментами → p0-X bad; 'wc 5 as' ×5 + 'as' =
# 111 Б 73d3534f (НОВЫЙ KEY-пин: stage1 парсит 16-й ток 'as' как
# ШЕСТОЙ as-стейтмент — emit 66 Б, Token 16 ≠ 6-stmt Token 18) — том
# молчит: word15 = 'as' → pEOF = 0; 'wc 5 as' ×5 + '3 3' = 110 Б
# acb587ba (НОВЫЙ пин, emit 65 Б = 5 as-хвостов + digit-tail ×2);
# 2-stmt кресты 'wc 5 as 3 wc 5 as 3' = 77 Б 5fb8d6c8 (= T4×T4-as
# база W-70), 'wc 5 as wc 5 as 3 3' = 77 Б 76767951 (пин W-98 СОВПАЛ),
# 'wc 5 as wc 5 as 3' = 72 Б d0814e42 (СОВПАЛ W-98), 'wc 5 as wc 5 as
# as' = 78 Б 52eb2ae5 (СОВПАЛ W-98: 7-й ток 'as' — stage1 эмитит
# 3 хвоста) — том молчит; singles/сироты: 'wc 5 as' = 56 Б 1176c0df
# (пин W-93 СОВПАЛ), 'wc 5 as 3' = 61 Б cbb9ba26 (пин W-98 СОВПАЛ),
# сирота 'wc 5 as wc 5' = 56 Б 59a9f18d (пин W-98 СОВПАЛ), 'wc 5 vw'
# = 49 Б 00ce976e, 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 ow' = 59 Б
# b733ee4c (пин W-85 СОВПАЛ); неги-браки: 'wc as wc 5 as …' = 0xFE
# 56 Б 9300cf34 (НОВЫЙ пин: bad word1 — emit 11 Б = as-хвост1 со
# слотом F1); 'wc z as …' = 0xFE 45 Б 29ba6852 (СОВПАЛ); 'wc 5 as wc
# z as …' = 0xFE 56 Б 26811567 (СОВПАЛ W-98: emit 11 Б); '… wc z as
# …' = 0xFE 67 Б 0c157e0c (СОВПАЛ W-98: emit 22 Б); '… wc z as …' =
# 0xFE 78 Б 6ff548fa (СОВПАЛ W-98: emit 33 Б); 'wc 5 as' ×4 + 'wc z
# as' = 0xFE 89 Б **ba71109d** (НОВЫЙ пин: bad d5 — emit 44 Б = 4
# as-хвоста до брака); bad word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad
# word5 = 0xFE 56 Б a1b1f926 (СОВПАЛ W-98); bad word8 = 0xFE 67 Б
# 88af7b15 (СОВПАЛ W-98); bad word11 = 0xFE 78 Б 71e766e1 (СОВПАЛ
# W-98); 'wc 5 as' ×4 + 'wc 5 xx' = 0xFE 89 Б **ff1e1721** (НОВЫЙ
# пин: bad word14 — emit 44 Б); bad word0/мусор = f3667180 (СОВПАЛ
# ×2); bad word4 'as' = 0xFE 67 Б 67a96a73 (НОВЫЙ пин: emit 22 Б);
# bad word7 'as' = 0xFE 78 Б b0863a07 (НОВЫЙ пин: emit 33 Б); bad
# word10 'as' в СЕРЕДИНЕ = 0xFE 89 Б 79eed8fb (НОВЫЙ пин: emit 44 Б —
# брак в середине подтверждён); 'wc 5 as' ×4 + 'wc as' — stage1
# ПРИНИМАЕТ (100 Б 0xFF **49a13420**, НОВЫЙ KEY-пин: emit 55 Б = 5
# as-хвостов, 5-й со слотом-ДЕФОЛТОМ 0x00F00FF8 [прецедент W-98
# dd6dec99: bad word10 'ow' → слот дефолт; word13 = 'as' НЕ цифра →
# слот дефолт], Token 14 ≠ база Token 15) — том молчит: v5 = 0 →
# PA = 9 → S = 15.
# Итог приёмки (probe106c, accept106.txt): **986 ток** <= 1022, компил
# stage1 = **1478 Б 0xFF md5 907e028e** (Token 0x3DA = 986; размер
# СОВПАЛ с ow-томом W-104 [1478 Б] — честное совпадение, md5 РАЗНЫЙ:
# 907e028e против 3672ed62), детерминизм OK. Честная матрица probe106c
# OK С ПЕРВОГО ПРОГОНА: **15 целей BYTE-OK против свежего stage1**
# (база 334d2504 = пин probe98-карт, точка, точка+мусор; 9 носителей =
# 9 РАЗНЫХ md5 — несущие слоты W-75 ×5 ×2 BE32; tracked _33 =
# 62443dfc, _37 = 281cce2e, _90 = e16eb462 = карта-кейс 11) + **88/88
# негов молчат**.
# EMIT: AS_TAIL1 (честный хвост T3-'as' стейтмента 1, карта probe106:
# U8 0x12 ('nb 1 8' = 18₁₀) + U8 0x15 ('nb 2 1' = 21₁₀) +
# BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1) + U8 0x55 ('nb 8 5' =
# 85₁₀) + BE32(cell[wc0] = ТОТ ЖЕ СЛОТ — второй BE32, закон W-75: ОБА
# BE32 читают F3+d; КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc'
# [sc = syscall FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; урок
# W-96: 'em' ТОЛЬКО кладёт константу в ячейку, без 'sc' байта НЕТ;
# nb-литералы ДЕСЯТИЧНЫЕ — урок probe57/W-64], 11 Б) -> AS_TAIL2
# (reslot: BE32(cell[wc2] = слот F3+d2) ОБА) -> AS_TAIL3 (reslot3:
# BE32(cell[wc3] = слот F3+d3) ОБА) -> RESLOT4 (переиспользование
# wc0: RESET cell[wc0] = F3_MINUS_48 + 'wc 0 as' на word10 →
# cell[wc0] = F3+d4) -> AS_TAIL4 (BE32(cell[wc0] = слот F3+d4) ОБА —
# ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ В ОБОИХ BE32; честный emit базы probe106
# 121500f00ff85500f00ff8 ×5) -> RESLOT5 (переиспользование wc2 —
# W-104: RESET cell[wc2] = F3_MINUS_48 + 'wc 2 as' на word13 →
# cell[wc2] = F3+d5 — слот2 УЖЕ прочитан AS_TAIL2) -> AS_TAIL5
# (BE32(cell[wc2] = слот F3+d5) ОБА — ПЯТЫЙ НЕСУЩИЙ В ОБОИХ BE32) ->
# вердец -> отчёт (Token = 15: 'nb 1 5' 'wo' — токенов слоя ДО
# терминатора, точка не считается) -> SEAL/END. Честный дизайн
# (= W-104 ow-структура, хвосты as):
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
#   'eq 0' НАПРЯМУЮ (сжатие W-104; НЕ через 'nb(F5), cp': F5 = wc2 =
#   СЛОТ d2 после reslot CHECK2; 'eq 0' = прецедент TAIL_CHECK
#   W-93/W-94/W-96) + C3 reslot3: RESET cell[wc3] = F3_MINUS_48 +
#   'wc 3 as' на word7 → cell[wc3] = F3+d3 (НЕСУЩИЙ для AS_TAIL3 В
#   ОБОИХ BE32; wc3 = 15732726 СВОБОДНА: stash в PF) + pAs3 (word8 ==
#   PB, PD += ) — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pAs4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pAs5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('as') = 29537 → wc7 — 'a' в МЛАДШЕМ байте
# [урок W-65/W-67], 0x6173; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333as.words

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
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('as' stmt-5)
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
PB = 15732730                # АДРЕС-конст LE2('as') = 29537 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-106
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
          # = 15732723 + d1 — НЕСУЩИЙ для AS_TAIL1 В ОБОИХ BE32 (карта
          # probe106: 'wc 7 as …' → BE32(FA) ×2; 'wc 0 as …' →
          # BE32(F3) ×2)
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
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # C2: честный reslot chain2: RESET cell[wc2] = F3 минус 48,
          # затем 'wc 2 as' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для AS_TAIL2 В ОБОИХ BE32 (карта probe106: '… wc 7
          # as …' → BE32(FA) ×2 во ВТОРОМ хвосте; '… wc 0 as …' →
          # BE32(F3) ×2). wc2 = F5 — ПОСЛЕ последнего F5-cp (valid3
          # сравнился выше; дальше F5 не читается CHECK1/CHECK2 —
          # честный порядок RELOAD2 W-84)
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
          # valid4 = (bad4 == 0) через 'eq 0' НАПРЯМУЮ: 'gt 9' оставляет
          # bad4 в acc (VM OP_LOAD mode 0x1A — результат в acc; 'eq 0' =
          # mode 0x16 сравнивает acc; stash-пересылка nb(PF) sv/va
          # ИЗБЫТОЧНА — sv/va acc не портят, снято с CtOs-Emu/ctos_vm.py;
          # F5 = wc2 = СЛОТ d2 после reslot CHECK2 — потому 'eq 0', а не
          # 'nb(F5), cp'; прецедент TAIL_CHECK W-93/W-94/W-96)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid4
          # C3: честный reslot chain3: RESET cell[wc3] = F3 минус 48,
          # затем 'wc 3 as' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для AS_TAIL3 В ОБОИХ BE32 (карта probe106: '… wc 7
          # as …' → BE32(FA) ×2 в ТРЕТЬЕМ хвосте). wc3 = 15732726 —
          # СВОБОДНА (stash W-95..W-104 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pAs3 = (word8 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs3
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
          # W-96/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid5
          # БЕЗ reslot4: свободных wc-ячеек НЕТ — слот4
          # материализуется RESLOT4 в EMIT-фазе (переиспользование
          # wc0 ПОСЛЕ AS_TAIL3)
          # D4: pAs4 = (word11 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs4
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
          # W-96/W-104/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ AS_TAIL4)
          # D5: pAs5 = (word14 == LE2('as'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pAs5
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
# W-100/W-101/W-102/W-103/W-104): RESET cell[wc0] = F3_MINUS_48, затем
# 'wc 0 as' на word10 (d4) → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для
# AS_TAIL4 В ОБОИХ BE32 (карта probe106: '… wc 5 as wc 7 as' → BE32(FA)
# ×2 в ЧЕТВЁРТОМ хвосте — пин 295c98d6; '… wc 0 as' → BE32(F3) ×2).
# Слот1 уже прочитан AS_TAIL1 В ОБОИХ BE32 (emit-порядок TAIL1→TAIL2→
# TAIL3→RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (W-104, идеом =
# RESLOT4 W-96): RESET cell[wc2] = F3_MINUS_48, затем 'wc 2 as' на
# word13 (d5) → cell[wc2] = 15732723 + d5. НЕСУЩИЙ для AS_TAIL5 В
# ОБОИХ BE32 (карта probe106: '… wc 5 as wc 7 as' → BE32(FA) ×2 в
# ПЯТОМ хвосте — НОВЫЙ пин 0bec2c13: ПЯТЫЙ несущий слот; '… wc 0 as'
# → BE32(F3) ×2).
# Слот2 уже прочитан AS_TAIL2 В ОБОИХ BE32 (emit-порядок TAIL1→TAIL2→
# TAIL3→RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: AS_TAIL = честный хвост T3-'as' стейтмента (закон W-75: U8
# 0x12 = 18₁₀ + U8 0x15 = 21₁₀ + BE32(слот) ('wc N ow') + U8 0x55 =
# 85₁₀ + BE32(слот) ('wc N ow') — ОБА BE32 читают СЛОТ, 11 Б, 18 ток)
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
AS_TAIL4 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '0', 'ow',                          # BE32(слот F3+d4 — RESLOT4)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — ВТОРОЙ BE32)
AS_TAIL5 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',         # U8 18 (0x12)
            'nb 2 1', 'em', 'nb 3 0 8', 'sc',         # U8 21 (0x15)
            'wc', '2', 'ow',                          # BE32(слот F3+d5 — RESLOT5)
            'nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 85 (0x55)
            'wc', '2', 'ow']                          # BE32(слот F3+d5 — ВТОРОЙ BE32)
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
       + AS_TAIL1 + AS_TAIL2 + AS_TAIL3 + RESLOT4 + AS_TAIL4 \
       + RESLOT5 + AS_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe106\pos_wc14v3t33333as.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333as tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
