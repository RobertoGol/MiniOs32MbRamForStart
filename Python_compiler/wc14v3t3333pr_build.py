# -*- coding: utf-8 -*-
# Сборщик честного ЧЕТЫРЁХстейтментного тома
# 'wc d pr wc d pr wc d pr wc d pr'
# Shape-T3×T3×T3×T3-pr (веха-23, спринт 79, W-99, TKT-052): СТРИМ —
# четвёртая ЧЕТЫРЁХстейтментная T3-форма. ВСЕ ЧЕТЫРЕ хвоста НЕСУЩИЕ
# (pr-хвост 9 Б — U8 0x54 + BE32(0x3F0050C0 КОНСТА) + BE32(слот),
# закон W-78: ЕДИНСТВЕННЫЙ BE32 хвоста читает СЛОТ F3+d —
# T3-pr-single 'wc 5 pr' emit '54 3f 00 50 c0 BE32(F3+d)', карта
# probe99: 'wc 7 pr' → BE32(0x00F00FFA), пин probe96/W-96-полки
# 34f4a890) => d1/d2/d3/d4 НЕ инвары — как у as-тома W-98 (но В
# ОТЛИЧИЕ от него ТОЛЬКО ВТОРОЙ BE32-слот — ПЕРВЫЕ 5 Б КОНСТА).
# База = wc14v3t3333as-структура (W-98) + честная карта probe99 (86
# кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe99\_t99_card.py):
# stage1 для T3×T3×T3×T3-pr целей = 81 Б 0xFF Token 12, emit =
# [pr-T3-хвост] ×4 = [54 3f 00 50 c0 BE32(слот F3+d)] ×4 = 36 Б; база
# 'wc 5 pr wc 5 pr wc 5 pr wc 5 pr' = 34f4a890 (пин СОВПАЛ; честный
# полный hex probe99: header CRC cfe10619 + emit 543f0050c000f00ff8
# ×4 + FF + BE32(12) + 20 нулей).
# **BE32 НЕСУЩИЙ В КАЖДОМ ХВОСТЕ (закон W-78 ×4)** (карта probe99:
# 'wc 7 pr …' = 81 Б c1e8223d, слот1 = FA; '… wc 7 pr …' = 68ef4e9e,
# слот2 = FA; '… wc 7 pr …' = 8217bb1c, слот3 = FA; '… wc 5 pr wc 7
# pr' = 1815b443 — НОВЫЙ пин: слот4 = FA; 'wc 7 pr' ×3 + 'wc 5 pr' =
# 7fdafacb (FA FA FA); 'wc 0 pr' ×4 = f90e5788 (F3 F3 F3 F3); 'wc 1
# pr wc 3 pr wc 5 pr wc 9 pr' = c073b562 (F4 F6 F8 FC); 'wc 9 pr wc 8
# pr wc 0 pr wc 1 pr' = 6167d479 (FC FB F3 F4); 'wc 2 pr wc 6 pr wc 4
# pr wc 8 pr' = a17b1ff9 (F5 F9 F7 FB)) — три tracked-цели W-99 ДАЮТ
# ТРИ РАЗНЫЕ md5 (честное доказательство несущих слотов W-78 ×4).
# ТРИ reslot'а в CHECK-фазе (структура W-96/W-98): chain1 d1→wc0
# (CHECK1) + reslot d2→wc2 (CHECK2) + reslot3 d3→wc3 (CHECK3); СЛОТ4
# = переиспользование wc0 в EMIT-фазе (RESLOT4 между PR_TAIL3 и
# PR_TAIL4) — свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ d1/d2/d3,
# wc1 = INIT F4, wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA,
# wc7 = PB, wc8 = PC, wc9 = PD; ЕДИНСТВЕННЫЙ BE32 читает ОДНУ ячейку
# — переиспользование после чтения слота1 PR_TAIL1 (emit-порядок
# TAIL1 → TAIL2 → TAIL3 → RESLOT4 → TAIL4), CHECK-фазы завершены ДО
# затвора — безопасно (ИДЕОМ W-96/W-98, прецедент снят).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word12 (ТРИНАДЦАТОЕ слово) — ОБА =
# база (карта probe99 кейсы 1/2 = 34f4a890); pEOF = eq(word12, 0) +
# eq(word12, 46) через stash-ячейку STASH = PF = 15732733 (15732723/
# 15732725/15732726 = СЛОТЫ d1/d2/d3 — TERM-фаза читает их 'wc 0
# pr'/'wc 2 pr'/'wc 3 pr' ПОСЛЕ TAIL_CHECK; PF = bad-flag stash
# W-95/W-96/W-98 — мёртв после последнего digit-блока CHECK4).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4 = 8) + PD (=
# pPr1+pPr2+pPr3+pPr4 = 4) + pEOF == 13 — 'su 9' + 'su 3' + 'eq 1'
# (S − 12 == 1 ⟺ S == 13; все immediate ОДНОразрядные; caps: S = 13
# ТОЛЬКО при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,pPr1,pPr2,pPr3,
# pPr4 = 1 И word12 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d44 не
# существует в T3×T3×T3×T3: word12 = терминатор слоя).
# Ключ-развязки (том обязан молчать, ВСЕ пины сняты честно картой
# probe99): te/sv/sp/vw/va/ow/if/as-смеси на ВСЕХ ЧЕТЫРЁХ позициях —
# stage1 ПРИНИМАЕТ (te e46b73ed/5beb6fd9/2d494f6c/45b66ac5; sv
# 6e693e7b/ad8222a4/fe558d17/19e8479b; sp fd89429e/7df9ab4c/
# 01cb1d7a/2e3dc0d8; vw 257c07cc/de6207e0/900c84e2/48c149cc; va
# 561e7395/38d8a8fe/10da9736/c86b6cac; ow fc60d5fa/bee64418/
# e973db71/e1d960d7; if 904586c2/de435575/397e8cce/32425f91; as
# fe55a1ed/485abdfd/955b39cf/ef046ca0) — том молчит: pPrX = 0 →
# PD = 3 → S = 12; 4-стейтментные потоки других kinds — stage1
# ПРИНИМАЕТ (te ×4 = 49 Б 40dc0e48, emit 05×4 = 4 Б — пин W-97; as ×4
# = 89 Б 3f6d8893, 44 Б — пин W-98; sv ×4 = 65 Б 05df0915, 20 Б; sp
# ×4 = c02a9b43; vw ×4 = 61 Б 8669285e, 16 Б; va ×4 = 69 Б 917128ff,
# 24 Б; ow ×4 = 101 Б c39da5d5, 56 Б — пин W-94) — том молчит:
# PD = 0; if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92
# СОВПАЛ) — том молчит; 5-stmt pr-поток — stage1 ПРИНИМАЕТ ('wc 5
# pr' ×5 = 90 Б 65b3dd01, emit 45 Б = 5 хвостов, Token 15;
# точка-вариант тот же) — том молчит: word12 = 'wc' → pEOF = 0 →
# S = 12; 6-stmt = 99 Б 78022c3a, emit 54 Б — S = 12; 3-stmt поток =
# 72 Б ca3af6f2 (НОВЫЙ пин) — том молчит: word9 = 'pr' → p0-4 = 0 →
# PA = 6, PD = 3, pEOF(word12 = 0) = 1 → S = 10; 2-stmt = 63 Б
# 93d24c79 (НОВЫЙ пин) — S = 7; кресты: 'wc 5 pr' ×4 + '3' = 86 Б
# 30a80c6f (НОВЫЙ пин: emit 41 Б = 4 pr-хвоста + digit-tail 15
# 00000003) — word12 = '3' → pEOF = 0; 'wc 5 pr 3 wc 5 pr wc 5 pr wc
# 5 pr' = 86 Б 283e49da (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 —
# word3 = '3' → p0-2 bad); 'wc 5 pr wc 5 pr 3 wc 5 pr wc 5 pr' = 86 Б
# 21988639 (НОВЫЙ пин: digit-tail после хвоста 2 — word6 = '3' →
# p0-3 bad); 'wc 5 pr wc 5 pr wc 5 pr 3 wc 5 pr' = 86 Б af0f8111
# (НОВЫЙ пин: digit МЕЖДУ stmt3 и stmt4, word9 = '3' → p0-4 bad);
# 'wc 5 pr' ×4 + 'pr' = 90 Б e24ca597 (НОВЫЙ пин: stage1 парсит 13-й
# ток 'pr' как ПЯТЫЙ pr-стейтмент — emit 45 Б) — том молчит: word12
# = 'pr' → pEOF = 0; 'wc 5 pr' ×4 + '3 3' = 91 Б 2c6de67b (НОВЫЙ пин,
# emit 46 Б = 4 хвоста + digit-tail ×2); 2-stmt кресты 'wc 5 pr 3 wc
# 5 pr 3' = 73 Б a5fa7400 (НОВЫЙ пин), 'wc 5 pr wc 5 pr 3 3' = 73 Б
# 89aa4c61 (НОВЫЙ пин), 'wc 5 pr wc 5 pr 3' = 68 Б 3396f4ac (НОВЫЙ
# пин), 'wc 5 pr wc 5 pr pr' = 72 Б 42545e00 (НОВЫЙ пин: 7-й ток
# 'pr' — stage1 эмитит 3 хвоста) — том молчит: word5 = 'pr' → pPr2 =
# 1, но p0-3 = 0, pPr3 = 0 → PA = 4, PD = 2, pEOF = 1 → S = 7;
# singles/сироты: 'wc 5 pr' = 54 Б 61957c4c (НОВЫЙ пин T3-pr-single:
# emit 9 Б), 'wc 5 pr 3' = 59 Б 40bf2183 (НОВЫЙ пин: emit 14 Б =
# pr-хвост + digit-tail), сирота 'wc 5 pr wc 5' = 54 Б 2d2ebfbf
# (НОВЫЙ пин: emit 9 Б), 'wc 5 vw' = 49 Б 00ce976e (пин), 'wc 5 sv' =
# 50 Б 6a16ae85 (пин); неги-браки: 'wc ow wc 5 pr wc 5 pr wc 5 pr' =
# 0xFE 59 Б ff73c458 (пин СОВПАЛ: bad word1); bad d1 = 0xFE 45 Б
# 29ba6852 (СОВПАЛ); bad d2 = 0xFE 54 Б 53097fac (НОВЫЙ пин: emit
# 9 Б = pr-хвост1); bad d3 = 0xFE 63 Б ca46e635 (НОВЫЙ пин: emit
# 18 Б); bad d4 = 0xFE 72 Б fa187979 (НОВЫЙ пин: emit 27 Б); bad
# word2 = 0xFE 45 Б 4ff7c705 (СОВПАЛ); bad word5 = 0xFE 54 Б
# ddb5b70d (НОВЫЙ пин); bad word8 = 0xFE 63 Б 603df1f9 (НОВЫЙ пин);
# bad word11 = 0xFE 72 Б e7fb9fa7 (НОВЫЙ пин); bad word0/мусор =
# f3667180 (СОВПАЛ); 'wc 5 pr wc ow wc 5 pr wc 5 pr' = 0xFE 68 Б
# 4e5de7d8 (НОВЫЙ пин: bad word4 'ow' — emit 23 Б = pr-хвост1 +
# ow-хвост 14 Б ['54' + BE32(0x00F00FF0 КОНСТА = EMIT_CELL) +
# BE32(несущий слот; word НЕ цифра → дефолт 0x00F00FF8 DEFAULT
# WORK_CELL) + '13' + BE32(305)] — stage1 БРАКУЕТ); 'wc 5 pr wc 5 pr
# wc ow wc 5 pr' = 0xFE 77 Б db2bdbe3 (НОВЫЙ пин: bad word7 — emit
# 32 Б); 'wc 5 pr wc 5 pr wc 5 pr wc ow' — stage1 ПРИНИМАЕТ (86 Б
# 0xFF 08fffa85, НОВЫЙ KEY-пин: emit 41 Б = 3 pr-хвоста (27 Б) +
# ow-хвост 14 Б — ЕДИНСТВЕННЫЙ несущий BE32 ow-хвоста = 0x00F00FF8
# DEFAULT WORK_CELL, word10 = 'ow' НЕ цифра → слот дефолт; первая
# BE32 = 0x00F00FF0 КОНСТА) — том молчит: v4 = 0 → PA = 7, pPr4 = 0 →
# S = 11.
# Итог: **854 ток** <= 1022, компил stage1 =
# **1174 Б 0xFF Token 0x356 = 854 md5 9cb4ff72**, детерминизм OK.
# Честная матрица probe99c OK С ПЕРВОГО ПРОГОНА (урок W-98 применён
# ДО прогона: 'nb 8 4' = 84₁₀ — U8 0x54): **15 целей BYTE-OK против
# свежего stage1** (база 34f4a890 = пин probe96, точка, точка+мусор,
# 9 носителей — РАЗНЫЕ md5 несущих слотов W-78 ×4; + 3 tracked-цели
# 2229ff03/56475806/6167d479) + **74/74 негов молчат**. NEW-пины
# W-99: t3×3×3×3-pr том + 3 tracked цели (РАЗНЫЕ md5 — несущие
# слоты W-78 ×4).
# EMIT: PR_TAIL1 (честный хвост T3-'pr' стейтмента 1, карта probe99:
# U8 0x54 ('nb 8 4' = 84₁₀) + BE32(0x3F0050C0 КОНСТА = 1056985280 —
# 'nb 1 0 5 6 9 8 5 2 8 0' 'wo' = 4 Б) + BE32(cell[wc0] = слот F3+d1
# НЕСУЩИЙ — chain1, закон W-78: ЕДИНСТВЕННЫЙ BE32 хвоста читает
# F3+d; УРОК W-98: КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc' [sc =
# syscall FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; 'em' ТОЛЬКО
# кладёт константу в ячейку, без 'sc' байта НЕТ; nb-литералы
# ДЕСЯТИЧНЫЕ — урок probe57/W-64]) -> PR_TAIL2 (тот же хвост с
# reslot: BE32(cell[wc2] = слот F3+d2)) -> PR_TAIL3 (тот же хвост с
# reslot3: BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование
# wc0: RESET cell[wc0] = F3_MINUS_48 + 'wc 0 pr' на word10 →
# cell[wc0] = F3+d4 — слот1 УЖЕ прочитан PR_TAIL1, CHECK-фазы
# завершены; ИДЕОМ = INIT + CHECK1 C1) -> PR_TAIL4 (тот же хвост с
# переиспользованным wc0: BE32(cell[wc0] = слот F3+d4) — честный emit
# базы probe99 543f0050c000f00ff8 ×4) -> вердец -> отчёт (Token = 12:
# 'nb 1 2' 'wo' — токенов слоя ДО терминатора, точка не считается)
# -> SEAL/END. Честный дизайн (= W-98 as-структура, хвосты pr):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для PR_TAIL1)
#   + pPr1 (word2 == LE2('pr') = 29296, 'p' в МЛАДШЕМ байте, PB =
#   wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 pr' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для PR_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок RELOAD2 W-84)
#   + pPr2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после reslot
#   CHECK2; 'eq 0' = прецедент TAIL_CHECK W-93/W-94/W-96) + C3
#   reslot3: RESET cell[wc3] = F3_MINUS_48 + 'wc 3 pr' на word7 →
#   cell[wc3] = F3+d3 (НЕСУЩИЙ для PR_TAIL3; wc3 = 15732726 СВОБОДНА:
#   stash в PF) + pPr3 (word8 == PB, PD += ) — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — валид-сравнение через
#   'eq 0' (F5 отравлен) + pPr4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = терминатор слоя) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('pr') = 29296 → wc7 — 'p' в МЛАДШЕМ байте
# [урок W-65/W-67], 0x7270; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t3333pr.words

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
                             # 'wc 0 pr'/'wc 2 pr'/'wc 3 pr' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('pr') = 29296 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-99
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
          # = 15732723 + d1 — НЕСУЩИЙ для PR_TAIL1 (карта probe99:
          # 'wc 7 pr …' → BE32(FA))
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
          nb(PF), 'va', nb(F5), 'cp',   # acc = valid2 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid2
          # C2: честный reslot chain2: RESET cell[wc2] = F3 минус 48,
          # затем 'wc 2 pr' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для PR_TAIL2 (карта probe99: '… wc 7 pr …' →
          # BE32(FA) во ВТОРОМ хвосте). wc2 = F5 — ПОСЛЕ последнего
          # F5-cp (valid2 сравнился выше; дальше F5 не читается
          # CHECK1/CHECK2 — честный порядок RELOAD2 W-84)
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
          nb(PF), 'sv',
          # valid3 = (bad4 == 0) через 'eq 0' — НЕ через 'nb(F5), cp':
          # F5 = wc2 = СЛОТ d2 после reslot CHECK2 ('eq 0' = прецедент
          # TAIL_CHECK W-93/W-94/W-96)
          nb(PF), 'va', 'eq', '0',
          'wc', '6', 'as',              # PA += valid3
          # C3: честный reslot chain3: RESET cell[wc3] = F3 минус 48,
          # затем 'wc 3 pr' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для PR_TAIL3 (карта probe99: '… wc 7 pr …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-96/W-98/W-99 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pPr3 = (word8 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = терминатор слоя)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (pr-аккумулятор)
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
          # wc0 ПОСЛЕ PR_TAIL3)
          # D4: pPr4 = (word11 == LE2('pr'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pPr4
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

# EMIT: PR_TAIL1 (честный хвост T3-'pr' стейтмента 1, карта probe99:
# U8 0x54 ('nb 8 4' = 84₁₀) + BE32(0x3F0050C0 КОНСТА = 1056985280 —
# 'nb 1 0 5 6 9 8 5 2 8 0' 'wo' = 4 Б) + BE32(cell[wc0] = слот F3+d1
# НЕСУЩИЙ — chain1; закон W-78: ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d;
# УРОК W-98: КАЖДЫЙ U8 = пара 'nb X em' + 'nb 3 0 8 sc' [sc = syscall
# FILE_U8 308 — пишет 1 Б из STREAM_EMIT_CELL; 'em' ТОЛЬКО кладёт
# константу в ячейку, без 'sc' байта НЕТ; nb-литералы ДЕСЯТИЧНЫЕ —
# урок probe57/W-64]) -> PR_TAIL2 (тот же хвост с reslot:
# BE32(cell[wc2] = слот F3+d2)) -> PR_TAIL3 (тот же хвост с reslot3:
# BE32(cell[wc3] = слот F3+d3)) -> RESLOT4 (переиспользование wc0:
# RESET cell[wc0] = F3_MINUS_48 + 'wc 0 pr' на word10 → cell[wc0] =
# F3+d4 — слот1 УЖЕ прочитан PR_TAIL1, CHECK-фазы завершены; ИДЕОМ =
# INIT + CHECK1 C1) -> PR_TAIL4 (тот же хвост с переиспользованным
# wc0: BE32(cell[wc0] = слот F3+d4) — честный emit базы probe99
# 543f0050c000f00ff8 ×4) -> вердец -> отчёт (Token = 12)
PR_TAIL1 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '0', 'ow']                          # BE32(слот F3+d1 — chain1)
PR_TAIL2 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '2', 'ow']                          # BE32(слот F3+d2 — reslot)
PR_TAIL3 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '3', 'ow']                          # BE32(слот F3+d3 — reslot3)
# RESLOT4 = переиспользование wc0 для слота d4 (ИДЕОМ W-96/W-98):
# RESET cell[wc0] = F3_MINUS_48, затем 'wc 0 pr' на word10 (d4)
# → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для PR_TAIL4 (карта probe99:
# '… wc 5 pr wc 7 pr' → BE32(FA) в ЧЕТВЁРТОМ хвосте — НОВЫЙ пин
# 1815b443: ЧЕТВЁРТЫЙ несущий слот; '… wc 0 pr' → BE32(F3)).
# Слот1 уже прочитан PR_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
PR_TAIL4 = ['nb 8 4', 'em', 'nb 3 0 8', 'sc',         # U8 0x54 (84₁₀)
            'nb 1 0 5 6 9 8 5 2 8 0', 'wo',           # BE32(0x3F0050C0 КОНСТА)
            'wc', '0', 'ow']                          # BE32(слот F3+d4 — RESLOT4)
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
       + PR_TAIL1 + PR_TAIL2 + PR_TAIL3 + RESLOT4 + PR_TAIL4 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe99\pos_wc14v3t3333pr.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t3333pr tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
