# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d pr wc d pr wc d pr wc d pr wc d pr'
# Shape-T3×5-pr (веха-23, спринт 87, W-107, TKT-052): СТРИМ — ЧЕТВЁРТАЯ
# ПЯТИстейтментная T3-форма (после ow W-104, te W-105, as W-106). ВСЕ
# ПЯТЬ хвостов НЕСУЩИЕ (pr-хвост 9 Б — U8 0x54 + BE32(0x3F0050C0
# КОНСТА) + BE32(слот F3+d), закон W-78: ЕДИНСТВЕННЫЙ BE32 хвоста
# читает СЛОТ — В ОТЛИЧИЕ от as W-75 [ОБА BE32 НЕСУЩИЕ], прецедент
# W-99 T3×4-pr: T3-pr-single 'wc 5 pr' emit '54 3f 00 50 c0 BE32(F3+d)',
# карта probe99 'wc 7 pr' → BE32(0x00F00FFA), пин probe96 34f4a890)
# => d1..d5 НЕ инвары — как у as-тома W-106 (но В ОТЛИЧИЕ от него
# ТОЛЬКО ВТОРОЙ BE32-слот — ПЕРВЫЕ 5 Б КОНСТА).
# База = wc14v3t33333as-структура (W-106, as-структура = W-98 + CHECK5
# + RESLOT5) + честная карта probe107 (102 кейса, свежий stage1 на
# каждую цель, G:\...\Temp\opencode\probe107\_t107_card.py): stage1
# для T3×5-pr целей = 90 Б 0xFF Token 15, emit = [pr-T3-хвост] ×5 =
# [54 3f 00 50 c0 BE32(слот F3+d)] ×5 = 45 Б; база 'wc 5 pr' ×5 =
# 65b3dd01 (пин W-99-карты СОВПАЛ — снята как «5-stmt pr-поток»; честный
# полный hex probe107: header CRC 8e327ec6 + emit 543f0050c000f00ff8 ×5
# + FF + BE32(15) + 20 нулей).
# **9 НОСИТЕЛЕЙ = 9 РАЗНЫХ md5 (честное доказательство несущих слотов
# W-78 ×5)**: 'wc 7 pr' на каждой из ПЯТИ позиций = 41185c1e (слот1 =
# FA)/d078943d (слот2)/ce9c5b9a (слот3)/e13a4ce3 (слот4 = RESLOT4)/
# 92e624bf (слот5 = RESLOT5 — ПЯТЫЙ несущий НОВЫЙ KEY, прецедент
# W-104 ow 0bfc66a5/W-106 as 0bec2c13); 'wc 7 pr' ×4 + 'wc 5 pr' =
# 4df1cf7b (FA FA FA FA F8); 'wc 0 pr' ×5 = 0a4b1e4e (F3 ×5); 'wc 1 pr
# wc 3 pr wc 5 pr wc 9 pr wc 5 pr' = a8228cf2 (F4 F6 F8 FC F8); 'wc 9
# pr wc 8 pr wc 0 pr wc 1 pr wc 5 pr' = 75e0a51f (FC FB F3 F4 F8) —
# tracked-цели W-107 ДАЮТ ТРИ РАЗНЫЕ md5 (несущие слоты).
# ПЯТЬ reslot'ов — chain1 d1→wc0 (CHECK1) + reslot d2→wc2 (CHECK2) +
# reslot3 d3→wc3 (CHECK3) + RESLOT4 d4→wc0 (переиспользование wc0,
# W-96/W-98/W-106) + RESLOT5 d5→wc2 (переиспользование wc2 — W-104/
# W-106); свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ d1/d2/d3, wc1 =
# INIT F4, wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA, wc7 =
# PB, wc8 = PC, wc9 = PD; ЕДИНСТВЕННЫЙ BE32 читает ОДНУ ячейку —
# переиспользование после чтения слота PR_TAIL1 (emit-порядок TAIL1 →
# TAIL2 → TAIL3 → RESLOT4 → TAIL4 → RESLOT5 → TAIL5), CHECK-фазы
# завершены ДО затвора — безопасно (ИДЕОМ W-96/W-98/W-99/W-106).
# ЧЕСТНОЕ СЖАТИЕ W-104: CHECK1/CHECK2 — валид через 'gt 9' + stash PF +
# cp F5 (F5 = wc2 чист ДО reslot CHECK2); CHECK3/CHECK4/CHECK5 —
# 'gt 9' + 'eq 0' НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0'
# сравнивает acc, sv/va acc не портят — снято с CtOs-Emu/ctos_vm.py,
# доказано regr104; F5 отравлен reslot CHECK2 — 'eq 0', а не cp).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база (карта probe107 кейсы 1/2 = 65b3dd01; мусор после точки '… . 3'
# = база кейс 2); pEOF = eq(word15, 0) + eq(word15, 46) через stash-
# ячейку STASH = PF = 15732733 (bad-flag МЁРТВ после CHECK5;
# 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их
# 'wc 0 pr'/'wc 2 pr'/'wc 3 pr' ПОСЛЕ TAIL_CHECK).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pPr1+pPr2+pPr3+pPr4+pPr5 = 5) + pEOF == 16. Форма W-104/W-106: 'su 9'
# + 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; недобор S < 15 →
# затвор молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 → S = 16 ТОЛЬКО
# при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,pPr1..pPr5 = 1 И
# word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не существует в
# T3×5: word15 = терминатор слоя). Ключ-развязки (том обязан молчать,
# ВСЕ пины сняты честно картой probe107): ow/sv/sp/vw/va/if/te/as-
# смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ, ВСЕ 40 НОВЫЕ пины
# pr-роли (ow f1641925/7bf0da4d/1ec9b29a/2fdb37d3/4b5848e8; sv
# 84c7f89c/c240f3f8/175a2a7b/f647655f/9ceba69a; sp d9d35d1e/c097ae1e/
# b5072e94/d94ff536/47adbee5; vw 74228a41/776e840f/a68f839f/cc76b17a/
# 737e7695; va 14c55791/5f024b76/6a926994/ff81985f/a46a5580; if
# bce4db4b/c84b5bd6/f0264c1e/ad5bcf3e/c9a6d960; te 267b7ec5/f4598b69/
# 28b42ac8/3a8b1d38/563f809d; as 4c7db5d3/22a54774/ba161d59/2f25b099/
# 33619320) — том молчит: pPrX = 0 → PD = 4 → S <= 15; 4/3/2-стейтмент
# ные pr-потоки — stage1 ПРИНИМАЕТ (pr ×4 = 81 Б 34f4a890, пин W-99
# СОВПАЛ, emit 36 Б; pr ×3 = 72 Б ca3af6f2, пин W-99 СОВПАЛ; pr ×2 =
# 63 Б 93d24c79, пин W-99 СОВПАЛ) — том молчит: PD = 0; потоки других
# kinds ×4 — stage1 ПРИНИМАЕТ (as ×4 = 89 Б 3f6d8893 [W-98]; te ×4 =
# 49 Б 40dc0e48 [W-97]; sv ×4 = 65 Б 05df0915; sp ×4 = 65 Б c02a9b43;
# vw ×4 = 61 Б 8669285e; va ×4 = 69 Б 917128ff; ow ×4 = 101 Б
# c39da5d5 [W-96]; 3/2-stmt ow = 977e2a7a/40251c66 СОВПАЛИ W-95/W-94)
# — том молчит: word15 = 'pr'/'as'/'te'/'ow' → pEOF = 0 (PD = 0 у
# чужих); if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ)
# — том молчит; 6-stmt pr-поток — stage1 ПРИНИМАЕТ ('wc 5 pr' ×6 =
# 99 Б 78022c3a [пин W-99 СОВПАЛ], emit 54 Б = 6 хвостов, Token 18;
# точка-вариант тот же) — том молчит: word15 = 'wc' → pEOF = 0 →
# S = 15; 7-stmt = 108 Б f4d5575a (НОВЫЙ пин, emit 63 Б, Token 21) —
# S = 15; кресты: 'wc 5 pr' ×5 + '3' = 95 Б d16efb25 (НОВЫЙ пин: emit
# 50 Б = 5 pr-хвостов + digit-tail 15 00000003, Token 16) — word15 =
# '3' → pEOF = 0; 'wc 5 pr 3 …' = 95 Б 177ccbb0 (НОВЫЙ пин: digit-tail
# ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad); '… wc 5 pr 3 …' = 95 Б
# b8c3b4ed (word6), '… 3 …' = 95 Б 45b7d0f1 (word9), '… wc 5 pr 3 wc 5
# pr' = 95 Б de233af3 (word12) — НОВЫЕ пины: digit МЕЖДУ стейтментами
# → p0-X bad; 'wc 5 pr' ×5 + 'pr' = 99 Б 73dedc1f (НОВЫЙ KEY-пин:
# stage1 парсит 16-й ток 'pr' как ШЕСТОЙ pr-стейтмент — emit 54 Б,
# Token 16 ≠ 6-stmt Token 18) — том молчит: word15 = 'pr' → pEOF = 0;
# 'wc 5 pr' ×5 + '3 3' = 100 Б d613aac0 (НОВЫЙ пин, emit 55 Б = 5
# pr-хвостов + digit-tail ×2); 2-stmt кресты СОВПАЛИ W-99: 'wc 5 pr 3
# wc 5 pr 3' = 73 Б a5fa7400, 'wc 5 pr wc 5 pr 3 3' = 73 Б 89aa4c61,
# 'wc 5 pr wc 5 pr 3' = 68 Б 3396f4ac, 'wc 5 pr wc 5 pr pr' = 72 Б
# 42545e00 (7-й ток 'pr' — stage1 эмитит 3 хвоста) — том молчит;
# singles/сироты: 'wc 5 pr' = 54 Б 61957c4c (пин W-99 СОВПАЛ, emit
# 9 Б), 'wc 5 pr 3' = 59 Б 40bf2183 (пин W-99 СОВПАЛ, emit 14 Б),
# сирота 'wc 5 pr wc 5' = 54 Б 2d2ebfbf (пин W-99 СОВПАЛ), 'wc 5 vw'
# = 49 Б 00ce976e, 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 ow' = 59 Б
# b733ee4c (пин W-85 СОВПАЛ); неги-браки: 'wc pr wc 5 pr …' = 0xFE
# 54 Б bd98dd90 (НОВЫЙ пин: bad word1 — emit 9 Б = pr-хвост1 со
# слотом F1); 'wc z pr …' = 0xFE 45 Б 29ba6852 (СОВПАЛ); 'wc 5 pr wc
# z pr …' = 0xFE 54 Б 53097fac (СОВПАЛ W-99: emit 9 Б); '… wc z pr
# …' = 0xFE 63 Б ca46e635 (СОВПАЛ W-99: emit 18 Б); '… wc z pr …' =
# 0xFE 72 Б fa187979 (СОВПАЛ W-99: emit 27 Б); 'wc 5 pr' ×4 + 'wc z
# pr' = 0xFE 81 Б **a2891e37** (НОВЫЙ пин: bad d5 — emit 36 Б = 4
# pr-хвоста до брака); bad word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad
# word5 = 0xFE 54 Б ddb5b70d (СОВПАЛ W-99); bad word8 = 0xFE 63 Б
# 603df1f9 (СОВПАЛ W-99); bad word11 = 0xFE 72 Б e7fb9fa7 (СОВПАЛ
# W-99); 'wc 5 pr' ×4 + 'wc 5 xx' = 0xFE 81 Б **2810612c** (НОВЫЙ
# пин: bad word14 — emit 36 Б); bad word0/мусор = f3667180 (СОВПАЛ
# ×2); bad word4 'pr' = 0xFE 63 Б 9f0eb716 (НОВЫЙ пин: emit 18 Б);
# bad word7 'pr' = 0xFE 72 Б 80bc6552 (НОВЫЙ пин: emit 27 Б); bad
# word10 'pr' в СЕРЕДИНЕ = 0xFE 81 Б 9746f264 (НОВЫЙ пин: emit 36 Б —
# брак в середине подтверждён); 'wc 5 pr' ×4 + 'wc pr' — stage1
# ПРИНИМАЕТ (90 Б 0xFF **f1b0d964**, НОВЫЙ KEY-пин: emit 45 Б = 5
# pr-хвостов, 5-й со слотом-ДЕФОЛТОМ 0x00F00FF8 [прецедент W-106 as
# 49a13420/W-98 dd6dec99: bad word10 'ow' → слот дефолт; word13 =
# 'pr' НЕ цифра → слот дефолт], Token 14 ≠ база Token 15) — том
# молчит: v5 = 0 → PA = 9 → S = 15.
# Итог приёмки (probe107c, accept107.txt, С ПЕРВОГО ПРОГОНА): **941
# ток** <= 1022, компил stage1 = **1338 Б 0xFF md5 610cace9** (Token
# 0x3AD = 941 = ток-счёт; реп 000003ad). ЗАПИСЬ «986 ток = W-106» и
# «as-хвост 24 ток» в ожидании была НЕВЕРНА: as-хвост W-106 = **33
# ток** (11 Б = U8 0x12 + U8 0x15 + BE32(слот) + U8 0x55 + BE32(слот)),
# pr-хвост = **24 ток** (9 Б) — МЕНЬШЕ на 9 ток ×5 = 45: 941 = 986 −
# 45 (дифф ток-потоков W-106/W-107 — ТОЛЬКО INIT-константа и хвосты);
# компил тома 1338 Б против as-тома 1478 Б (−140 Б — честный итог
# более короткого pr-хвоста в теле компилятора). Детерминизм OK (2
# прогона 1338 Б 610cace9). Честная матрица probe107c: **15 целей
# BYTE-OK против свежего stage1** (база 65b3dd01 = пин W-99-карт ×3,
# точка, точка+мусор; 9 носителей = 9 РАЗНЫХ md5 — несущие слоты
# W-78 ×5; tracked _33 = c81e7555, _37 = f6d91c3c, _90 = 75e0a51f =
# карта-кейс 11 СОВПАЛ) + **90/90 негов молчат**.
# EMIT: PR_TAIL1 (честный хвост T3-'pr' стейтмента 1, карта probe107:
# U8 0x54 ('nb 8 4' = 84₁₀) + BE32(0x3F0050C0 КОНСТА = 1056985280 —
# 'nb 1 0 5 6 9 8 5 2 8 0' 'wo' = 4 Б) + BE32(cell[wc0] = слот F3+d1
# НЕСУЩИЙ — chain1, закон W-78: ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d;
# УРОК W-98: КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc' [sc = syscall
# FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; 'em' ТОЛЬКО кладёт
# константу в ячейку, без 'sc' байта НЕТ; nb-литералы ДЕСЯТИЧНЫЕ —
# урок probe57/W-64], 9 Б) -> PR_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2)) -> PR_TAIL3 (тот же хвост с reslot3:
# BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование wc0:
# RESET cell[wc0] = F3_MINUS_48 + 'wc 0 pr' на word10 → cell[wc0] =
# F3+d4 — слот1 УЖЕ прочитан PR_TAIL1, CHECK-фазы завершены; ИДЕОМ =
# INIT + CHECK1 C1) -> PR_TAIL4 (BE32(cell[wc0] = слот F3+d4) —
# ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ; честный emit базы probe107
# 543f0050c000f00ff8 ×5) -> RESLOT5 (переиспользование wc2 — W-104/
# W-106: RESET cell[wc2] = F3_MINUS_48 + 'wc 2 pr' на word13 →
# cell[wc2] = F3+d5 — слот2 УЖЕ прочитан PR_TAIL2) -> PR_TAIL5
# (BE32(cell[wc2] = слот F3+d5) — ПЯТЫЙ НЕСУЩИЙ) -> вердец -> отчёт
# (Token = 15: 'nb 1 5' 'wo' — токенов слоя ДО терминатора, точка не
# считается) -> SEAL/END. Честный дизайн (= W-106 as-структура,
# хвосты pr):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для PR_TAIL1)
#   + pPr1 (word2 == LE2('pr') = 29296, 'p' в МЛАДШЕМ байте, PB =
#   wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 pr' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для PR_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок W-84/W-96) +
#   pPr2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' НАПРЯМУЮ (сжатие W-104; НЕ через 'nb(F5), cp': F5 = wc2 =
#   СЛОТ d2 после reslot CHECK2; 'eq 0' = прецедент TAIL_CHECK
#   W-93/W-94/W-96) + C3 reslot3: RESET cell[wc3] = F3_MINUS_48 +
#   'wc 3 pr' на word7 → cell[wc3] = F3+d3 (НЕСУЩИЙ для PR_TAIL3;
#   wc3 = 15732726 СВОБОДНА: stash в PF) + pPr3 (word8 == PB, PD += )
#   — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pPr4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pPr5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('pr') = 29296 → wc7 — 'p' в МЛАДШЕМ байте
# [урок W-65/W-67], 0x7270; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333pr.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('pr' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('pr' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('pr' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('pr' stmt-4)
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('pr' stmt-5)
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
                             # 'wc 0 pr'/'wc 2 pr'/'wc 3 pr' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('pr') = 29296 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-107
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
          'wc', '6', 'as',
          # C1: честный слот chain1: cell[wc0] = F3_MINUS_48 + word1
          # = 15732723 + d1 — НЕСУЩИЙ для PR_TAIL1 (карта probe107:
          # 'wc 7 pr …' → BE32(FA); 'wc 0 pr …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pPr1 = (word2 == LE2('pr'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pPr1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (pr-аккумулятор)
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
          # затем 'wc 2 pr' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для PR_TAIL2 (карта probe107: '… wc 7 pr …' →
          # BE32(FA) во ВТОРОМ хвосте; '… wc 0 pr …' → BE32(F3)).
          # wc2 = F5 — ПОСЛЕ последнего F5-cp (valid3 сравнился выше;
          # дальше F5 не читается CHECK1/CHECK2 — честный порядок
          # RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pPr2 = (word5 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (pr-аккумулятор)
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
          # затем 'wc 3 pr' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для PR_TAIL3 (карта probe107: '… wc 7 pr …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-95..W-106 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pPr3 = (word8 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (pr-аккумулятор)
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
          # wc0 ПОСЛЕ PR_TAIL3)
          # D4: pPr4 = (word11 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr4
          # БЕЗ digit-block d44: word12 = 'wc' stmt-5

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (pr-аккумулятор)
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
          # W-96/W-104/W-106/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ PR_TAIL4)
          # D5: pPr5 = (word14 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr5
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
# W-100/W-101/W-102/W-103/W-104/W-106): RESET cell[wc0] = F3_MINUS_48,
# затем 'wc 0 pr' на word10 (d4) → cell[wc0] = 15732723 + d4. НЕСУЩИЙ
# для PR_TAIL4 (карта probe107: '… wc 5 pr wc 7 pr' → BE32(FA) в
# ЧЕТВЁРТОМ хвосте — пин e13a4ce3; '… wc 0 pr' → BE32(F3) ×2).
# Слот1 уже прочитан PR_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (W-104/W-106, идеом =
# RESLOT4 W-96): RESET cell[wc2] = F3_MINUS_48, затем 'wc 2 pr' на
# word13 (d5) → cell[wc2] = 15732723 + d5. НЕСУЩИЙ для PR_TAIL5
# (карта probe107: '… wc 5 pr wc 7 pr' → BE32(FA) в ПЯТОМ хвосте —
# НОВЫЙ пин 92e624bf: ПЯТЫЙ несущий слот; '… wc 0 pr' → BE32(F3)).
# Слот2 уже прочитан PR_TAIL2 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: PR_TAIL = честный хвост T3-'pr' стейтмента (закон W-78: U8
# 0x54 = 84₁₀ + BE32(0x3F0050C0 КОНСТА) ('nb … wo') + BE32(слот)
# ('wc N ow') — ЕДИНСТВЕННЫЙ BE32 читает СЛОТ, 9 Б, 24 ток)
PR_TAIL1 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '0', 'ow']                          # BE32(слот F3+d1 — chain1)
PR_TAIL2 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '2', 'ow']                          # BE32(слот F3+d2 — reslot)
PR_TAIL3 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '3', 'ow']                          # BE32(слот F3+d3 — reslot3)
PR_TAIL4 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — RESLOT4)
PR_TAIL5 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
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
       + PR_TAIL1 + PR_TAIL2 + PR_TAIL3 + RESLOT4 + PR_TAIL4 \
       + RESLOT5 + PR_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe107\pos_wc14v3t33333pr.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333pr tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
