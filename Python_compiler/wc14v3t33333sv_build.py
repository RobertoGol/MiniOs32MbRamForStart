# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d sv wc d sv wc d sv wc d sv wc d sv'
# Shape-T3×5-sv (веха-23, спринт 88, W-108, TKT-052): СТРИМ — ПЯТАЯ
# ПЯТИстейтментная T3-форма (после ow W-104, te W-105, as W-106, pr
# W-107). ВСЕ ПЯТЬ хвостов НЕСУЩИЕ (sv-хвост 5 Б — U8 0x55 + BE32(слот
# F3+d), БЕЗ консты, закон W-79: ЕДИНСТВЕННЫЙ BE32 хвоста читает СЛОТ —
# В ОТЛИЧИЕ от pr W-78 [U8 0x54 + BE32(КОНСТА) + BE32(слот), 24 ток] и
# as W-75 [ОБА BE32]; прецедент W-100 T3×4-sv: T3-sv-single 'wc 5 sv' =
# 50 Б 6a16ae85, emit '55 BE32(F3+d)' → 'wc 7 sv' → BE32(0x00F00FFA),
# пин W-88/probe100-полки 6a16ae85) => d1..d5 НЕ инвары — как у
# pr-тома W-107 (но В ОТЛИЧИЕ от него хвост БЕЗ консты-BE32 — 12 ток/
# хвост против 24).
# База = wc14v3t33333sv-структура (W-100, sv-структура = W-99/W-106 +
# CHECK5 + RESLOT5) + честная карта probe108 (102 кейса, свежий stage1
# на каждую цель, G:\...\Temp\opencode\probe108\_t108_card.py): stage1
# для T3×5-sv целей = 70 Б 0xFF Token 15, emit = [sv-T3-хвост] ×5 =
# [55 BE32(слот F3+d)] ×5 = 25 Б; база 'wc 5 sv' ×5 = 99c1c4ef (пин
# W-100-карты СОВПАЛ — снята как «5-stmt sv-поток»; честный полный hex
# probe108: header CRC 4a18a55c + emit 5500f00ff8 ×5 + FF + BE32(15) +
# 20 нулей).
# **9 НОСИТЕЛЕЙ = 9 РАЗНЫХ md5 (честное доказательство несущих слотов
# W-79 ×5)**: 'wc 7 sv' на каждой из ПЯТИ позиций = 97a1849e (слот1 =
# FA)/5a5684ec (слот2)/f159ffc7 (слот3)/905fd5a9 (слот4 = RESLOT4)/
# 9c3e5183 (слот5 = RESLOT5 — ПЯТЫЙ несущий НОВЫЙ KEY, прецедент
# W-104 ow 0bfc66a5/W-106 as 0bec2c13/W-107 pr 92e624bf); 'wc 7 sv' ×4
# + 'wc 5 sv' = be3115b2 (FA FA FA FA F8); 'wc 0 sv' ×5 = c93dab7c
# (F3 ×5); 'wc 1 sv wc 3 sv wc 5 sv wc 9 sv wc 5 sv' = a253f27d (F4
# F6 F8 FC F8); 'wc 9 sv wc 8 sv wc 0 sv wc 1 sv wc 5 sv' = 47f27f4d
# (FC FB F3 F4 F8) — tracked-цели W-108 ДАЮТ ТРИ РАЗНЫЕ md5 (несущие
# слоты).
# ПЯТЬ reslot'ов — chain1 d1→wc0 (CHECK1) + reslot d2→wc2 (CHECK2) +
# reslot3 d3→wc3 (CHECK3) + RESLOT4 d4→wc0 (переиспользование wc0,
# W-96/W-98/W-106/W-107) + RESLOT5 d5→wc2 (переиспользование wc2 —
# W-104/W-106/W-107); свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ
# d1/d2/d3, wc1 = INIT F4, wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик,
# wc6 = PA, wc7 = PB, wc8 = PC, wc9 = PD; ЕДИНСТВЕННЫЙ BE32 читает
# ОДНУ ячейку — переиспользование после чтения слота SV_TAIL1
# (emit-порядок TAIL1 → TAIL2 → TAIL3 → RESLOT4 → TAIL4 → RESLOT5 →
# TAIL5), CHECK-фазы завершены до затвора — безопасно (ИДЕОМ
# W-96/W-98/W-99/W-106/W-107).
# ЧЕСТНОЕ СЖАТИЕ W-104: CHECK1/CHECK2 — валид через 'gt 9' + stash PF +
# cp F5 (F5 = wc2 чист ДО reslot CHECK2); CHECK3/CHECK4/CHECK5 —
# 'gt 9' + 'eq 0' НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0'
# сравнивает acc, sv/va acc не портят — снято с CtOs-Emu/ctos_vm.py,
# доказано regr104; F5 отравлен reslot CHECK2 — 'eq 0', а не cp).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база (карта probe108 кейсы 1/2 = 99c1c4ef; мусор после точки '… . 3'
# = база кейс 2); pEOF = eq(word15, 0) + eq(word15, 46) через stash-
# ячейку STASH = PF = 15732733 (bad-flag МЁРТВ после CHECK5;
# 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их
# 'wc 0 sv'/'wc 2 sv'/'wc 3 sv' ПОСЛЕ TAIL_CHECK).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pSv1+pSv2+pSv3+pSv4+pSv5 = 5) + pEOF == 16. Форма W-104/W-106/W-107:
# 'su 9' + 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; недобор
# S < 15 → затвор молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 → S = 16
# ТОЛЬКО при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,pSv1..pSv5
# = 1 И word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не существует
# в T3×5: word15 = терминатор слоя). Ключ-развязки (том обязан молчать,
# ВСЕ пины сняты честно картой probe108): ow/sv/sp/vw/va/if/te/as/pr-
# смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ, ВСЕ 40 НОВЫЕ пины
# sv-роли (ow 38adb29a/79c0b056/b4f5d8b9/498278f3/a56b4682; sp
# 3f37535b/a688a978/566137cb/25232be5/a1634f5e; vw 7fc2fecc/e130bf07/
# 1c59ff97/c95f6214/19a5e9a8; va 76b6e674/3af24b7f/4315785b/5c36cfa5/
# 57132854; if d713ddb9/16fc3897/0d408e04/d11cb917/19a69b65; te
# fcd2fec9/d522e750/4b9341bf/14c52f91/eb960c14; as e341f832/94d099ba/
# e451cb8c/64c7b68e/d01f6c4f; pr a5ac95a9/5c07dab3/530ed511/c337ae13/
# cbe76fc1) — том молчит: pSvX = 0 → PD = 4 → S <= 15; 4/3/2-стейтмент
# ные sv-потоки — stage1 ПРИНИМАЕТ (sv ×4 = 65 Б 05df0915, пин W-100
# СОВПАЛ, emit 20 Б; sv ×3 = 60 Б c23cf6ec, пин W-100 СОВПАЛ; sv ×2 =
# 55 Б cd1086b0, пин W-100 СОВПАЛ) — том молчит: PD = 0; потоки других
# kinds ×4 — stage1 ПРИНИМАЕТ (pr ×4 = 81 Б 34f4a890 [W-99]; as ×4 = 89
# Б 3f6d8893 [W-98]; te ×4 = 49 Б 40dc0e48 [W-97]; sp ×4 = 65 Б
# c02a9b43; vw ×4 = 61 Б 8669285e; va ×4 = 69 Б 917128ff; ow ×4 = 101 Б
# c39da5d5 [W-96]; 3/2-stmt ow = 977e2a7a/40251c66 СОВПАЛИ W-95/W-94) —
# том молчит: word15 = 'sv'/'pr'/'as'/'te'/'ow' → pEOF = 0 (PD = 0 у
# чужих); if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ)
# — том молчит; 6-stmt sv-поток — stage1 ПРИНИМАЕТ ('wc 5 sv' ×6 = 75
# Б 0a9576bb [пин W-100 СОВПАЛ], emit 30 Б = 6 хвостов, Token 18;
# точка-вариант тот же) — том молчит: word15 = 'wc' → pEOF = 0 →
# S = 15; 7-stmt = 80 Б 9a1b6b85 (НОВЫЙ пин, emit 35 Б, Token 21) —
# S = 15; кресты: 'wc 5 sv' ×5 + '3' = 75 Б 240e111e (НОВЫЙ пин: emit
# 30 Б = 5 sv-хвостов + digit-tail 15 00000003, Token 16) — word15 =
# '3' → pEOF = 0; 'wc 5 sv 3 …' = 75 Б 2142fc19 (НОВЫЙ пин: digit-tail
# ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad); '… wc 5 sv 3 …' = 75 Б
# b5dfb28d (word6), '… 3 …' = 75 Б 42cf6c02 (word9), '… wc 5 sv 3 wc 5
# sv' = 75 Б 3f667884 (word12) — НОВЫЕ пины: digit МЕЖДУ стейтментами
# → p0-X bad; 'wc 5 sv' ×5 + 'sv' = 75 Б 53c81ebb (НОВЫЙ KEY-пин:
# stage1 парсит 16-й ток 'sv' как ШЕСТОЙ sv-стейтмент — emit 30 Б,
# Token 16 ≠ 6-stmt Token 18) — том молчит: word15 = 'sv' → pEOF = 0;
# 'wc 5 sv' ×5 + '3 3' = 80 Б 61c180fa (НОВЫЙ пин, emit 35 Б = 5
# sv-хвостов + digit-tail ×2); 2-stmt кресты СОВПАЛИ W-100: 'wc 5 sv 3
# wc 5 sv 3' = 65 Б 1b8699b9, 'wc 5 sv wc 5 sv 3 3' = 65 Б 19832dd4,
# 'wc 5 sv wc 5 sv 3' = 60 Б b2939d7c, 'wc 5 sv wc 5 sv sv' = 60 Б
# f9f9c9af (7-й ток 'sv' — stage1 эмитит 3 хвоста) — том молчит;
# singles/сироты: 'wc 5 sv' = 50 Б 6a16ae85 (пин W-100 СОВПАЛ, emit
# 5 Б), 'wc 5 sv 3' = 55 Б d0efc383 (пин W-100 СОВПАЛ, emit 10 Б),
# сирота 'wc 5 sv wc 5' = 50 Б 46e2f69b (пин W-100 СОВПАЛ), 'wc 5 vw'
# = 49 Б 00ce976e, 'wc 5 pr' = 54 Б 61957c4c (пин W-99 СОВПАЛ), 'wc 5
# ow' = 59 Б b733ee4c (пин W-85 СОВПАЛ); неги-браки: 'wc sv wc 5 sv …'
# = 0xFE 50 Б 643ff46e (НОВЫЙ пин: bad word1 — emit 5 Б 5500f00ff1 =
# sv-хвост1 со слотом F1, Token 2); 'wc z sv …' = 0xFE 45 Б 29ba6852
# (СОВПАЛ); 'wc 5 sv wc z sv …' = 0xFE 50 Б e8906fca (СОВПАЛ W-100:
# emit 5 Б); '… wc z sv …' = 0xFE 55 Б a74228cb (СОВПАЛ W-100: emit
# 10 Б); '… wc z sv …' = 0xFE 60 Б 3b9d8a9b (СОВПАЛ W-100: emit 15 Б);
# 'wc 5 sv' ×4 + 'wc z sv' = 0xFE 65 Б **3c4ab640** (НОВЫЙ пин: bad
# d5 — emit 20 Б = 4 sv-хвоста до брака); bad word2 = 0xFE 45 Б
# 4ff7c705 (СОВПАЛ); bad word5 = 0xFE 50 Б e8afe9c6 (СОВПАЛ W-100);
# bad word8 = 0xFE 55 Б dc976f7c (СОВПАЛ W-100); bad word11 = 0xFE
# 60 Б fd74d8ee (СОВПАЛ W-100); 'wc 5 sv' ×4 + 'wc 5 xx' = 0xFE 65 Б
# **d41dfe04** (НОВЫЙ пин: bad word14 — emit 20 Б); bad word0/мусор =
# f3667180 (СОВПАЛ ×2); bad word4 'sv' = 0xFE 55 Б d43a612a (НОВЫЙ
# пин: emit 10 Б); bad word7 'sv' = 0xFE 60 Б 52cef2c2 (НОВЫЙ пин:
# emit 15 Б); bad word10 'sv' в СЕРЕДИНЕ = 0xFE 65 Б 97a98683 (НОВЫЙ
# пин: emit 20 Б — брак в середине подтверждён); 'wc 5 sv' ×4 +
# 'wc sv' — stage1 ПРИНИМАЕТ (70 Б 0xFF **ab45118d**, НОВЫЙ KEY-пин:
# emit 25 Б = 5 sv-хвостов, 5-й со слотом-ДЕФОЛТОМ 0x00F00FF8
# [прецедент W-107 pr f1b0d964/W-106 as 49a13420: word НЕ цифра →
# слот дефолт], Token 14 ≠ база Token 15) — том молчит: v5 = 0 →
# PA = 9 → S = 15.
# ЧЕСТНАЯ ПОПРАВКА W-108 (приёмка probe108c, accept108.txt): первый
# прогон билдера дал 15/15 MISMATCH — sv-хвост писался 'nb 5 5' (55
# десят. = 0x37, hex прочтён как десят.) вместо 'nb 8 5' (85 десят. =
# 0x55); CRC-поле не трогалось (заполнитель 'nb 0' — VM пересчитывает
# CRC на закрытии файла, содержание зависело только от U8). Исправлено
# на 'nb 8 5' → probe108c OK. Итог приёмки: том собран **881 ток** <=
# 1022 (sv-хвост 12 ток против pr-хвоста 24 ток ×5 = −60 от W-107
# [941]); компил тома свежим stage1 ×2 = **1268 Б 0xFF md5 143e6c5f**
# (реп 00000371 = 881), детерминизм OK. Честная матрица probe108c:
# **15/15 целей BYTE-OK против свежего stage1** (база 99c1c4ef = пин
# W-100-карт СОВПАЛ, точка, точка+мусор; 9 носителей = 9 РАЗНЫХ md5 —
# несущие слоты W-79 ×5: 97a1849e/5a5684ec/f159ffc7/905fd5a9/9c3e5183/
# be3115b2/c93dab7c/a253f27d/47f27f4d — ВСЕ совпали с картой probe108;
# tracked _33 = ba606896, _37 = 2b81502c, _90 = 47f27f4d) + **90/90
# негов молчат**.
# EMIT: SV_TAIL1 (честный хвост T3-'sv' стейтмента 1, карта probe108:
# U8 0x55 ('nb 8 5' = 85₁₀) + BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ —
# chain1; закон W-79: ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d, хвост БЕЗ
# консты; УРОК W-98: КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc' [sc =
# syscall FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; 'em' ТОЛЬКО
# кладёт константу в ячейку, без 'sc' байта НЕТ; nb-литералы
# ДЕСЯТИЧНЫЕ — урок probe57/W-64], 5 Б) -> SV_TAIL2 (тот же хвост с
# reslot: BE32(cell[wc2] = слот F3+d2)) -> SV_TAIL3 (тот же хвост с
# reslot3: BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование
# wc0: RESET cell[wc0] = F3_MINUS_48 + 'wc 0 sv' на word10 →
# cell[wc0] = F3+d4 — слот1 УЖЕ прочитан SV_TAIL1, CHECK-фазы
# завершены; ИДЕОМ = INIT + CHECK1 C1) -> SV_TAIL4 (BE32(cell[wc0] =
# слот F3+d4) — ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ; честный emit базы probe108
# 5500f00ff8 ×5) -> RESLOT5 (переиспользование wc2 — W-104/W-106/
# W-107: RESET cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word13 →
# cell[wc2] = F3+d5 — слот2 УЖЕ прочитан SV_TAIL2) -> SV_TAIL5
# (BE32(cell[wc2] = слот F3+d5) — ПЯТЫЙ НЕСУЩИЙ) -> вердец -> отчёт
# (Token = 15: 'nb 1 5' 'wo' — токенов слоя ДО терминатора, точка не
# считается) -> SEAL/END. Честный дизайн (= W-107 pr-структура /
# W-106 as-структура, хвосты sv):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для SV_TAIL1)
#   + pSv1 (word2 == LE2('sv') = 30323, 's' в МЛАДШЕМ байте, PB =
#   wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для SV_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок W-84/W-96) +
#   pSv2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' НАПРЯМУЮ (сжатие W-104; НЕ через 'nb(F5), cp': F5 = wc2 =
#   СЛОТ d2 после reslot CHECK2; 'eq 0' = прецедент TAIL_CHECK
#   W-93/W-94/W-96) + C3 reslot3: RESET cell[wc3] = F3_MINUS_48 +
#   'wc 3 sv' на word7 → cell[wc3] = F3+d3 (НЕСУЩИЙ для SV_TAIL3;
#   wc3 = 15732726 СВОБОДНА: stash в PF) + pSv3 (word8 == PB, PD += )
#   — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pSv4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 == 'wc',
#   PA += ) + valid(d5) digit-block (word13) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pSv5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('sv') = 30323 → wc7 — 's' в МЛАДШЕМ байте
# [урок W-65/W-67], 0x7673; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333sv.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('sv' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('sv' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('sv' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('sv' stmt-4)
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('sv' stmt-5)
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
PB = 15732730                # АДРЕС-конст LE2('sv') = 30323 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-108
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(30323), 'ne', 'wc', '7', 'sv',           # 'sv' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для SV_TAIL1 (карта probe108:
          # 'wc 7 sv …' → BE32(FA); 'wc 0 sv …' → BE32(F3))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pSv1 = (word2 == LE2('sv'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pSv1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (sv-аккумулятор)
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
          # НЕСУЩИЙ для SV_TAIL2 (карта probe108: '… wc 7 sv …' →
          # BE32(FA) во ВТОРОМ хвосте; '… wc 0 sv …' → BE32(F3)).
          # wc2 = F5 — ПОСЛЕ последнего F5-cp (valid3 сравнился выше;
          # дальше F5 не читается CHECK1/CHECK2 — честный порядок
          # RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pSv2 = (word5 == LE2('sv'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSv2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (sv-аккумулятор)
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
          # НЕСУЩИЙ для SV_TAIL3 (карта probe108: '… wc 7 sv …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-95..W-107 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pSv3 = (word8 == LE2('sv'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSv3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (sv-аккумулятор)
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
          # wc0 ПОСЛЕ SV_TAIL3)
          # D4: pSv4 = (word11 == LE2('sv'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSv4
          # БЕЗ digit-block d44: word12 = 'wc' stmt-5

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (sv-аккумулятор)
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
          # W-96/W-104/W-106/W-107/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ SV_TAIL4)
          # D5: pSv5 = (word14 == LE2('sv'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pSv5
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
# W-100/W-101/W-102/W-103/W-104/W-106/W-107): RESET cell[wc0] =
# F3_MINUS_48, затем 'wc 0 sv' на word10 (d4) → cell[wc0] = 15732723 +
# d4. НЕСУЩИЙ для SV_TAIL4 (карта probe108: '… wc 5 sv wc 7 sv' →
# BE32(FA) в ЧЕТВЁРТОМ хвосте — пин 905fd5a9; '… wc 0 sv' → BE32(F3)
# ×2). Слот1 уже прочитан SV_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (W-104/W-106/W-107,
# идеом = RESLOT4 W-96): RESET cell[wc2] = F3_MINUS_48, затем
# 'wc 2 sv' на word13 (d5) → cell[wc2] = 15732723 + d5. НЕСУЩИЙ для
# SV_TAIL5 (карта probe108: '… wc 5 sv wc 7 sv' → BE32(FA) в ПЯТОМ
# хвосте — НОВЫЙ пин 9c3e5183: ПЯТЫЙ несущий слот; '… wc 0 sv' →
# BE32(F3)). Слот2 уже прочитан SV_TAIL2 (emit-порядок TAIL1→TAIL2→
# TAIL3→RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: SV_TAIL = честный хвост T3-'sv' стейтмента (закон W-79: U8
# 0x55 = 85₁₀ + BE32(слот) ('wc N ow') — ЕДИНСТВЕННЫЙ BE32 читает
# СЛОТ, БЕЗ консты, 5 Б, 12 ток)
SV_TAIL1 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 0x55 (85 десят.)
            'wc', '0', 'ow']                          # BE32(слот F3+d1 — chain1)
SV_TAIL2 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 0x55 (85 десят.)
            'wc', '2', 'ow']                          # BE32(слот F3+d2 — reslot)
SV_TAIL3 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 0x55 (85 десят.)
            'wc', '3', 'ow']                          # BE32(слот F3+d3 — reslot3)
SV_TAIL4 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 0x55 (85 десят.)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — RESLOT4)
SV_TAIL5 = ['nb 8 5', 'em', 'nb 3 0 8', 'sc',         # U8 0x55 (85 десят.)
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
       + SV_TAIL1 + SV_TAIL2 + SV_TAIL3 + RESLOT4 + SV_TAIL4 \
       + RESLOT5 + SV_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe108\pos_wc14v3t33333sv.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333sv tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
