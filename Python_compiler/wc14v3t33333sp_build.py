# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d sp wc d sp wc d sp wc d sp wc d sp'
# Shape-T3×5-sp (веха-23, спринт 89, W-109, TKT-052): СТРИМ — ШЕСТАЯ
# ПЯТИстейтментная T3-форма (после ow W-104, te W-105, as W-106, pr
# W-107, sv W-108). ВСЕ ПЯТЬ хвостов НЕСУЩИЕ (sp-хвост 5 Б — U8 0x53 +
# BE32(слот F3+d), БЕЗ консты, закон W-80: ЕДИНСТВЕННЫЙ BE32 хвоста
# читает СЛОТ — В ОТЛИЧИЕ от pr W-78 [U8 0x54 + BE32(КОНСТА) +
# BE32(слот), 24 ток] и as W-75 [ОБА BE32]; прецеденты sp-закона:
# T3×T4-sp W-80 d19276d, T3×T3-sp W-89 003aed4; прецедент W-101
# T3×4-sp: T3-sp-single 'wc 5 sp' = 50 Б 87817a4b, emit '53 BE32(F3+d)'
# → 'wc 7 sp' → BE32(0x00F00FFA)) => d1..d5 НЕ инвары — как у
# sv-тома W-108 (тот же размер хвоста 5 Б, 12 ток/хвост).
# База = wc14v3t3333sp-структура (W-101, sp-структура = W-89/закон
# W-80 + CHECK5 + RESLOT5) + честная карта probe109 (102 кейса, свежий
# stage1 на каждую цель, G:\...\Temp\opencode\probe109\_t109_card.py):
# stage1 для T3×5-sp целей = 70 Б 0xFF Token 15, emit = [sp-T3-хвост]
# ×5 = [53 BE32(слот F3+d)] ×5 = 25 Б; база 'wc 5 sp' ×5 = 832bf061
# (пин W-101-карты СОВПАЛ — снята как «5-stmt sp-поток»; честный
# полный hex probe109: header CRC 97ec9b9d + emit 5300f00ff8 ×5 + FF +
# BE32(15) + 20 нулей).
# **9 НОСИТЕЛЕЙ = 9 РАЗНЫХ md5 (честное доказательство несущих слотов
# W-80 ×5)**: 'wc 7 sp' на каждой из ПЯТИ позиций = 3ff760a9 (слот1 =
# FA)/57605a0f (слот2)/07894fd3 (слот3)/111f68ff (слот4 = RESLOT4)/
# 1dd91a00 (слот5 = RESLOT5 — ПЯТЫЙ несущий НОВЫЙ KEY, прецедент
# W-104 ow 0bfc66a5/W-106 as 0bec2c13/W-107 pr 92e624bf/W-108 sv
# 9c3e5183); 'wc 7 sp' ×4 + 'wc 5 sp' = 80f450f0 (FA FA FA FA F8);
# 'wc 0 sp' ×5 = 00455654 (F3 ×5); 'wc 1 sp wc 3 sp wc 5 sp wc 9 sp
# wc 5 sp' = 41277933 (F4 F6 F8 FC F8); 'wc 9 sp wc 8 sp wc 0 sp wc 1
# sp wc 5 sp' = b94ff318 (FC FB F3 F4 F8) — tracked-цели W-109 =
# РАЗНЫЕ md5 (несущие слоты; _90 = b94ff318 = этот кейс).
# ПЯТЬ reslot'ов — chain1 d1→wc0 (CHECK1) + reslot d2→wc2 (CHECK2) +
# reslot3 d3→wc3 (CHECK3) + RESLOT4 d4→wc0 (переиспользование wc0,
# W-96/W-98/W-106/W-107/W-108) + RESLOT5 d5→wc2 (переиспользование
# wc2 — W-104/W-106/W-107/W-108); свободных wc-ячеек НЕТ: wc0/wc2/wc3
# = СЛОТЫ d1/d2/d3, wc1 = INIT F4, wc4 = INIT SRC_BUFFER, wc5 =
# COPY-счётчик, wc6 = PA, wc7 = PB, wc8 = PC, wc9 = PD; ЕДИНСТВЕННЫЙ
# BE32 читает ОДНУ ячейку — переиспользование после чтения слота
# SP_TAIL1 (emit-порядок TAIL1 → TAIL2 → TAIL3 → RESLOT4 → TAIL4 →
# RESLOT5 → TAIL5), CHECK-фазы завершены до затвора — безопасно (ИДЕОМ
# W-96/W-98/W-99/W-106/W-107/W-108).
# ЧЕСТНОЕ СЖАТИЕ W-104: CHECK1/CHECK2 — валид через 'gt 9' + stash PF +
# cp F5 (F5 = wc2 чист ДО reslot CHECK2); CHECK3/CHECK4/CHECK5 —
# 'gt 9' + 'eq 0' НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0'
# сравнивает acc, sv/va acc не портят — снято с CtOs-Emu/ctos_vm.py,
# доказано regr104; F5 отравлен reslot CHECK2 — 'eq 0', а не cp).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база (карта probe109 кейсы 1/2 = 832bf061; мусор после точки '… . 3'
# = база кейс 2); pEOF = eq(word15, 0) + eq(word15, 46) через stash-
# ячейку STASH = PF = 15732733 (bad-flag МЁРТВ после CHECK5;
# 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их
# 'wc 0 sv'/'wc 2 sv'/'wc 3 sv' ПОСЛЕ TAIL_CHECK).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pSp1+pSp2+pSp3+pSp4+pSp5 = 5) + pEOF == 16. Форма W-104/W-106/W-107/
# W-108: 'su 9' + 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16;
# недобор S < 15 → затвор молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 →
# S = 16 ТОЛЬКО при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,
# pSp1..pSp5 = 1 И word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не
# существует в T3×5: word15 = терминатор слоя). Ключ-развязки (том
# обязан молчать, ВСЕ пины сняты честно картой probe109): ow/sv/sp/vw/
# va/if/te/as/pr-смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ, ВСЕ
# 40 НОВЫЕ пины sp-роли (ow ce719ad9/88214be2/8a7770eb/0b35b664/
# 8c4cc576; sv eb44c27e/53d45bb7/0eaf9766/88f0b9b3/76ab1861; vw
# ac57cf38/fc68e529/a3fe7a17/cb3825ca/e3b44373; va 38191517/38154b7f/
# b74e6bbe/ea52ea70/be91d527; if 8a94e104/67f3ef67/989c15c2/2f19f877/
# 13a90682; te 7036f771/6a8fb101/4e2f9f4f/414c3b11/8725555e; as
# b5c32e31/712d4abe/3be23ea9/66b4548f/a6d3ce12; pr e789492c/b98ae53a/
# 63d54cea/13ddf511/694eba82) — том молчит: pSpX = 0 → PD = 4 →
# S <= 15; 4/3/2-стейтментные sp-потоки — stage1 ПРИНИМАЕТ (sp ×4 = 65
# Б c02a9b43, пин W-101 СОВПАЛ, emit 20 Б; sp ×3 = 60 Б 0f03bdf1, пин
# W-101 СОВПАЛ; sp ×2 = 55 Б 413c7817, пин W-101 СОВПАЛ) — том молчит:
# PD = 0; потоки других kinds ×4 — stage1 ПРИНИМАЕТ (pr ×4 = 81 Б
# 34f4a890 [W-99]; as ×4 = 89 Б 3f6d8893 [W-98]; te ×4 = 49 Б 40dc0e48
# [W-97]; sv ×4 = 65 Б 05df0915 [W-100]; vw ×4 = 61 Б 8669285e
# [W-102]; va ×4 = 69 Б 917128ff [W-103]; ow ×4 = 101 Б c39da5d5
# [W-96]; ow ×3/×2 = 977e2a7a/40251c66 СОВПАЛИ W-95/W-94) — том
# молчит: word15 = 'sp'/'pr'/'as'/'te'/'ow' → pEOF = 0 (PD = 0 у
# чужих); if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ)
# — том молчит; 6-stmt sp-поток — stage1 ПРИНИМАЕТ ('wc 5 sp' ×6 = 75
# Б 87d5427a [пин W-101 СОВПАЛ], emit 30 Б = 6 хвостов, Token 18;
# точка-вариант тот же) — том молчит: word15 = 'wc' → pEOF = 0 →
# S = 15; 7-stmt = 80 Б ff36a960 (НОВЫЙ пин, emit 35 Б, Token 21) —
# S = 15; кресты: 'wc 5 sp' ×5 + '3' = 75 Б 2017376e (НОВЫЙ пин: emit
# 30 Б = 5 sp-хвостов + digit-tail 15 00000003, Token 16) — word15 =
# '3' → pEOF = 0; 'wc 5 sp 3 …' = 75 Б 4f8c304c (НОВЫЙ пин: digit-tail
# ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad); '… wc 5 sp 3 …' = 75 Б
# b779f112 (word6), '… 3 …' = 75 Б ac74ddeb (word9), '… wc 5 sp 3 wc 5
# sp' = 75 Б f7eee731 (word12) — НОВЫЕ пины: digit МЕЖДУ стейтментами
# → p0-X bad; 'wc 5 sp' ×5 + 'sp' = 75 Б a3961e99 (НОВЫЙ KEY-пин:
# stage1 парсит 16-й ток 'sp' как ШЕСТОЙ sp-стейтмент — emit 30 Б,
# Token 16 ≠ 6-stmt Token 18) — том молчит: word15 = 'sp' → pEOF = 0;
# 'wc 5 sp' ×5 + '3 3' = 80 Б 5b4f0b20 (НОВЫЙ пин, emit 35 Б = 5
# sp-хвостов + digit-tail ×2); 2-stmt кресты СОВПАЛИ W-101: 'wc 5 sp 3
# wc 5 sp 3' = 65 Б 1e7d8b3e, 'wc 5 sp wc 5 sp 3 3' = 65 Б e95fd4ab,
# 'wc 5 sp wc 5 sp 3' = 60 Б 6296b751, 'wc 5 sp wc 5 sp sp' = 60 Б
# 87420d50 (7-й ток 'sp' — stage1 эмитит 3 хвоста) — том молчит;
# singles/сироты: 'wc 5 sp' = 50 Б 87817a4b (пин W-101 СОВПАЛ, emit
# 5 Б), 'wc 5 sp 3' = 55 Б d6e6b1d6 (пин W-101 СОВПАЛ, emit 10 Б),
# сирота 'wc 5 sp wc 5' = 50 Б a88f6c3a (пин W-101 СОВПАЛ), 'wc 5 vw'
# = 49 Б 00ce976e, 'wc 5 pr' = 54 Б 61957c4c (пин W-99 СОВПАЛ), 'wc 5
# ow' = 59 Б b733ee4c (пин W-85 СОВПАЛ); неги-браки: 'wc sp wc 5 sp …'
# = 0xFE 50 Б f27847f5 (НОВЫЙ пин: bad word1 — emit 5 Б 5300f00ff1 =
# sp-хвост1 со слотом F1, Token 2); 'wc z sp …' = 0xFE 45 Б 29ba6852
# (СОВПАЛ); 'wc 5 sp wc z sp …' = 0xFE 50 Б a915cf6e (СОВПАЛ W-101:
# emit 5 Б); '… wc z sp …' = 0xFE 55 Б f19410b0 (СОВПАЛ W-101: emit
# 10 Б); '… wc z sp …' = 0xFE 60 Б 3bd3e41a (СОВПАЛ W-101: emit 15 Б);
# 'wc 5 sp' ×4 + 'wc z sp' = 0xFE 65 Б **bbcf46e9** (НОВЫЙ пин: bad
# d5 — emit 20 Б = 4 sp-хвоста до брака); bad word2 = 0xFE 45 Б
# 4ff7c705 (СОВПАЛ); bad word5 = 0xFE 50 Б bd775853 (СОВПАЛ W-101);
# bad word8 = 0xFE 55 Б 10b37188 (СОВПАЛ W-101); bad word11 = 0xFE
# 60 Б 0ae22675 (СОВПАЛ W-101); 'wc 5 sp' ×4 + 'wc 5 xx' = 0xFE 65 Б
# **7481d70d** (НОВЫЙ пин: bad word14 — emit 20 Б); bad word0/мусор =
# f3667180 (СОВПАЛ ×2); bad word4 'sp' = 0xFE 55 Б b8b19698 (НОВЫЙ
# пин: emit 10 Б); bad word7 'sp' = 0xFE 60 Б 105f4837 (НОВЫЙ пин:
# emit 15 Б); bad word10 'sp' в СЕРЕДИНЕ = 0xFE 65 Б 7bb6d7b7 (НОВЫЙ
# пин: emit 20 Б — брак в середине подтверждён); 'wc 5 sp' ×4 + 'wc
# sp' — stage1 ПРИНИМАЕТ (70 Б 0xFF **0db85b07**, НОВЫЙ KEY-пин: emit
# 25 Б = 5 sp-хвостов, 5-й со слотом-ДЕФОЛТОМ 0x00F00FF8 [прецедент
# W-108 sv ab45118d/W-107 pr f1b0d964/W-106 as 49a13420: word НЕ цифра
# → слот дефолт], Token 14 ≠ база Token 15) — том молчит: v5 = 0 →
# PA = 9 → S = 15.
# ЧЕСТНЫЙ ИТОГ ПРИЁМКИ W-109 (probe109c, accept109.txt): том собран
# **881 ток** <= 1022 (sp-хвост 12 ток — как sv-хвост W-108; против
# pr-хвоста 24 ток ×5 = −60 от W-107 [941]); компил тома свежим
# stage1 ×2 = **1268 Б 0xFF md5 57ad3a87** (реп 00000371 = 881),
# детерминизм OK. Честная матрица probe109c: **15/15 целей BYTE-OK
# против свежего stage1** (база 832bf061 = пин W-101-карт СОВПАЛ,
# точка, точка+мусор; 9 носителей = 9 РАЗНЫХ md5 — несущие слоты
# W-80 ×5: 3ff760a9/57605a0f/07894fd3/111f68ff/1dd91a00/80f450f0/
# 00455654/41277933/b94ff318 — ВСЕ совпали с картой probe109; tracked
# _33 = 74bb672c, _37 = d79e0cf0, _90 = b94ff318 = карта-кейс 11
# СОВПАЛ) + **90/90 негов молчат**.
# EMIT: SP_TAIL1 (честный хвост T3-'sp' стейтмента 1, карта probe109:
# U8 0x53 ('nb 8 3' = 83₁₀) + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ —
# chain1; закон W-80: ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d, хвост БЕЗ
# консты; УРОК W-98: КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc' [sc =
# syscall FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; 'em' ТОЛЬКО
# кладёт константу в ячейку, без 'sc' байта НЕТ; nb-литералы
# ДЕСЯТИЧНЫЕ — урок probe57/W-64], 5 Б) -> SP_TAIL2 (тот же хвост с
# reslot: BE32(cell[wc2] = слот F3+d2)) -> SP_TAIL3 (тот же хвост с
# reslot3: BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование
# wc0: RESET cell[wc0] = F3_MINUS_48 + 'wc 0 sv' на word10 →
# cell[wc0] = F3+d4 — слот1 УЖЕ прочитан SP_TAIL1, CHECK-фазы
# завершены; ИДЕОМ = INIT + CHECK1 C1) -> SP_TAIL4 (BE32(cell[wc0] =
# слот F3+d4) — ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ; честный emit базы probe109
# 5300f00ff8 ×5) -> RESLOT5 (переиспользование wc2 — W-104/W-106/
# W-107/W-108: RESET cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word13 →
# cell[wc2] = F3+d5 — слот2 УЖЕ прочитан SP_TAIL2) -> SP_TAIL5
# (BE32(cell[wc2] = слот F3+d5) — ПЯТЫЙ НЕСУЩИЙ) -> вердец -> отчёт
# (Token = 15: 'nb 1 5' 'wo' — токенов слоя ДО терминатора, точка не
# считается) -> SEAL/END. Честный дизайн (= W-108 sv-структура /
# W-107 pr-структура, хвосты sp):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для SP_TAIL1)
#   + pSp1 (word2 == LE2('sp') = 28787, 's' в МЛАДШЕМ байте, PB =
#   wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для SP_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок W-84/W-96) +
#   pSp2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' НАПРЯМУЮ (сжатие W-104; НЕ через 'nb(F5), cp': F5 = wc2 =
#   СЛОТ d2 после reslot CHECK2; 'eq 0' = прецедент TAIL_CHECK
#   W-93/W-94/W-96) + C3 reslot3: RESET cell[wc3] = F3_MINUS_48 +
#   'wc 3 sv' на word7 → cell[wc3] = F3+d3 (НЕСУЩИЙ для SP_TAIL3;
#   wc3 = 15732726 СВОБОДНА: stash в PF) + pSp3 (word8 == PB, PD += )
#   — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pSp4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pSp5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('sp') = 28787 → wc7 — 's' в МЛАДШЕМ байте
# [урок W-65/W-67], 0x7073; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333sp.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('sp' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('sp' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('sp' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('sp' stmt-4)
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('sp' stmt-5)
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
                             # 'wc 0 sv'/'wc 2 sv'/'wc 3 sv' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('sp') = 28787 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-109
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(28787), 'ne', 'wc', '7', 'sv',           # 'sp' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для SP_TAIL1 (карта probe109:
          # 'wc 7 sp …' → BE32(FA); 'wc 0 sp …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pSp1 = (word2 == LE2('sp'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pSp1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (sp-аккумулятор)
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
          # затем 'wc 2 sv' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для SP_TAIL2 (карта probe109: '… wc 7 sp …' →
          # BE32(FA) во ВТОРОМ хвосте; '… wc 0 sp …' → BE32(F3)).
          # wc2 = F5 — ПОСЛЕ последнего F5-cp (valid3 сравнился выше;
          # дальше F5 не читается CHECK1/CHECK2 — честный порядок
          # RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pSp2 = (word5 == LE2('sp'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSp2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (sp-аккумулятор)
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
          # затем 'wc 3 sv' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для SP_TAIL3 (карта probe109: '… wc 7 sp …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-95..W-108 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pSp3 = (word8 == LE2('sp'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSp3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (sp-аккумулятор)
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
          # wc0 ПОСЛЕ SP_TAIL3)
          # D4: pSp4 = (word11 == LE2('sp'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSp4
          # БЕЗ digit-block d44: word12 = 'wc' stmt-5

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (sp-аккумулятор)
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
          # W-96/W-104/W-106/W-107/W-108/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ SP_TAIL4)
          # D5: pSp5 = (word14 == LE2('sp'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSp5
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
# W-100/W-101/W-102/W-103/W-104/W-106/W-107/W-108): RESET cell[wc0] =
# F3_MINUS_48, затем 'wc 0 sv' на word10 (d4) → cell[wc0] = 15732723 +
# d4. НЕСУЩИЙ для SP_TAIL4 (карта probe109: '… wc 5 sp wc 7 sp' →
# BE32(FA) в ЧЕТВЁРТОМ хвосте — пин 111f68ff; '… wc 0 sp' → BE32(F3)
# ×2). Слот1 уже прочитан SP_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (W-104/W-106/W-107/
# W-108, идеом = RESLOT4 W-96): RESET cell[wc2] = F3_MINUS_48, затем
# 'wc 2 sv' на word13 (d5) → cell[wc2] = 15732723 + d5. НЕСУЩИЙ для
# SP_TAIL5 (карта probe109: '… wc 5 sp wc 7 sp' → BE32(FA) в ПЯТОМ
# хвосте — НОВЫЙ пин 1dd91a00: ПЯТЫЙ несущий слот; '… wc 0 sp' →
# BE32(F3)). Слот2 уже прочитан SP_TAIL2 (emit-порядок TAIL1→TAIL2→
# TAIL3→RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: SP_TAIL = честный хвост T3-'sp' стейтмента (закон W-80: U8
# 0x53 = 83₁₀ + BE32(слот) ('wc N ow') — ЕДИНСТВЕННЫЙ BE32 читает
# СЛОТ, БЕЗ консты, 5 Б, 12 ток)
SP_TAIL1 = ['nb 8 3', 'em', 'nb 3 0 8', 'sc',         # U8 0x53 (83 десят.)
            'wc', '0', 'ow']                          # BE32(слот F3+d1 — chain1)
SP_TAIL2 = ['nb 8 3', 'em', 'nb 3 0 8', 'sc',         # U8 0x53 (83 десят.)
            'wc', '2', 'ow']                          # BE32(слот F3+d2 — reslot)
SP_TAIL3 = ['nb 8 3', 'em', 'nb 3 0 8', 'sc',         # U8 0x53 (83 десят.)
            'wc', '3', 'ow']                          # BE32(слот F3+d3 — reslot3)
SP_TAIL4 = ['nb 8 3', 'em', 'nb 3 0 8', 'sc',         # U8 0x53 (83 десят.)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — RESLOT4)
SP_TAIL5 = ['nb 8 3', 'em', 'nb 3 0 8', 'sc',         # U8 0x53 (83 десят.)
            'wc', '2', 'ow']                          # BE32(слот F3+d5 — RESLOT5)
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
       + SP_TAIL1 + SP_TAIL2 + SP_TAIL3 + RESLOT4 + SP_TAIL4 \
       + RESLOT5 + SP_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe109\pos_wc14v3t33333sp.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333sp tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
