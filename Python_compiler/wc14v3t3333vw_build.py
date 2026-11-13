# -*- coding: utf-8 -*-
# Сборщик честного ЧЕТЫРЁХстейтментного тома
# 'wc d vw wc d vw wc d vw wc d vw'
# Shape-T3×T3×T3×T3-vw (веха-23, спринт 82, W-102, TKT-052): СТРИМ —
# седьмая ЧЕТЫРЁХстейтментная T3-форма. ВСЕ ЧЕТЫРЕ хвоста НЕСУЩИЕ
# (vw-хвост 4 Б — ТОЛЬКО BE32(слот), БЕЗ ведущего U8 — уникальный вид
# W-72: ЕДИНСТВЕННЫЙ BE32 хвоста читает СЛОТ F3+d — T3×T3-vw W-90
# `89d4c4` ab92cdf6, T3×T4-vw W-81 `918ac0` 0bde646b) => d1/d2/d3/d4
# НЕ инвары — как у sp/sv-томов W-100/W-101 (те же ТРИ reslot'а +
# RESLOT4, хвосты 4 Б вместо 5 Б).
# База = wc14v3t3333sp-структура (W-101) + честная карта probe102 (86
# кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe102\_t102_card.py):
# stage1 для T3×T3×T3×T3-vw целей = 61 Б 0xFF Token 12, emit =
# [vw-T3-хвост] ×4 = [BE32(слот F3+d)] ×4 = 16 Б; база
# 'wc 5 vw wc 5 vw wc 5 vw wc 5 vw' = 8669285e (пин probe96..101-карт
# СОВПАЛ — снята в probe101 как «vw ×4»; честный полный hex probe102:
# header CRC f5a80f3c + emit 00f00ff8 ×4 + FF + BE32(12) + 20 нулей).
# **BE32 НЕСУЩИЙ В КАЖДОМ ХВОСТЕ (закон W-72 ×4)** — 9 носителей
# РАЗНЫЕ md5: 'wc 7 vw …' = d24f6fbe (слот1 = FA), '… wc 7 vw …' =
# 753b2b6f (слот2 = FA), '… wc 7 vw …' = 4fe2453e (слот3 = FA),
# '… wc 5 vw wc 7 vw' = 16763076 (НОВЫЙ пин: слот4 = FA), 'wc 7 vw' ×3
# + 'wc 5 vw' = cc0290fb (FA FA FA), 'wc 0 vw' ×4 = 574b06eb (F3 F3 F3
# F3), 'wc 1 vw wc 3 vw wc 5 vw wc 9 vw' = c50d4cc2 (F4 F6 F8 FC),
# 'wc 9 vw wc 8 vw wc 0 vw wc 1 vw' = 0ae99a72 (FC FB F3 F4), 'wc 2 vw
# wc 6 vw wc 4 vw wc 8 vw' = c5fc65e0 (F5 F9 F7 FB) — tracked-цели
# ДАЮТ ТРИ РАЗНЫЕ md5. Точка/точка+мусор = база. 5-stmt vw-поток = 65
# Б 44b4ed8e (Token 15; точка-вариант тот же) — том молчит: word12 =
# 'wc' → pEOF = 0 → S = 12; 6-stmt = 69 Б 95cce12e — S = 12; 3-stmt =
# 57 Б 14a07fc1 (СОВПАЛ W-90) — том молчит: word9 = 'vw' → p0-4 = 0 →
# PA = 6, PD = 3, pEOF(word12 = 0) = 1 → S = 10; 2-stmt = 53 Б
# ab92cdf6 (СОВПАЛ W-90 = tracked T3-vw-полки) — S = 7.
# Ключ-смеси (том обязан молчать, ВСЕ пины сняты честно): te/pr/sv/sp/
# va/if/ow/as-смеси на ВСЕХ ЧЕТЫРЁХ позициях — stage1 ПРИНИМАЕТ (te
# ea88f9cd/44260b7f/e72f9781/5c31cec3; pr 5eb0d628/d6941700/ac6e78e1/
# ced7c9ba; sv b66e8470/97a24c7e/bf4969f9/d2329bdf; sp e851a742/
# e6344f84/6643aac9/03106f64; va 9fa6abab/daa7abdb/d9fd0b0e/a6060cd1;
# ow f656109c/9a1c9643/c002cfcd/28cbf333; if d55f1af7/29da45ef/
# b3aef29e/80c9462a; as 871daf47/34a3e161/a5c9dd53/7afe99d3) — том
# молчит: pVwX = 0 → PD = 3 → S = 12; 4-стейтментные потоки других
# kinds (пины probe96..101 СОВПАЛИ: te ×4 = 49 Б 40dc0e48, emit 05×4 =
# 4 Б; as ×4 = 89 Б 3f6d8893, 44 Б; pr ×4 = 81 Б 34f4a890, 36 Б; sv ×4
# = 65 Б 05df0915 = W-100, 20 Б; sp ×4 = 65 Б c02a9b43 = W-101, 20 Б;
# va ×4 = 69 Б 917128ff, 24 Б; ow ×4 = 101 Б c39da5d5, 56 Б) — том
# молчит: PD = 0; if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92
# СОВПАЛ) — том молчит; кресты: 'wc 5 vw' ×4 + '3' = 66 Б 99c6ba85
# (НОВЫЙ пин: emit 21 Б = 4 vw-хвоста + digit-tail 15 00000003) —
# word12 = '3' → pEOF = 0; 'wc 5 vw 3 wc 5 vw wc 5 vw wc 5 vw' = 66 Б
# 10194aa8 (НОВЫЙ пин: digit-tail ПОСЛЕ хвоста 1 — word3 = '3' →
# p0-2 bad); 'wc 5 vw wc 5 vw 3 wc 5 vw wc 5 vw' = 66 Б b2e2e257
# (НОВЫЙ пин: digit-tail после хвоста 2 — word6 = '3' → p0-3 bad);
# 'wc 5 vw wc 5 vw wc 5 vw 3 wc 5 vw' = 66 Б b3dc5d38 (НОВЫЙ пин:
# digit МЕЖДУ stmt3 и stmt4, word9 = '3' → p0-4 bad); 'wc 5 vw' ×4 +
# 'vw' = 65 Б e8b78dcd (НОВЫЙ пин: stage1 парсит 13-й ток 'vw' как
# ПЯТЫЙ vw-стейтмент — emit 20 Б) — том молчит: word12 = 'vw' →
# pEOF = 0; 'wc 5 vw' ×4 + '3 3' = 71 Б fec63912 (НОВЫЙ пин, emit 26 Б
# = 4 хвоста + digit-tail ×2); 2-stmt кресты СОВПАЛИ W-90: 'wc 5 vw 3
# wc 5 vw 3' = 63 Б dbb5b0a3, 'wc 5 vw wc 5 vw 3 3' = 63 Б 0c35ee83,
# 'wc 5 vw wc 5 vw 3' = 58 Б 0bce683b, 'wc 5 vw wc 5 vw vw' = 57 Б
# d9eabc11 (7-й ток 'vw' — stage1 эмитит 3 хвоста) — том молчит:
# word5 = 'vw' → pVw2 = 1, но p0-3 = 0, pVw3 = 0 → PA = 4, PD = 2,
# pEOF = 1 → S = 7; singles/сироты: 'wc 5 vw' = 49 Б 00ce976e (СОВПАЛ
# T3-vw-single, пин probe90/W-90-полки: emit 4 Б БЕЗ ведущего U8),
# 'wc 5 vw 3' = 54 Б 77e58387 (НОВЫЙ пин: emit 9 Б = vw-хвост +
# digit-tail), сирота 'wc 5 vw wc 5' = 49 Б 0ddf9034 (СОВПАЛ W-90:
# emit 4 Б), 'wc 5 sp' = 50 Б 87817a4b (пин W-89), 'wc 5 pr' = 54 Б
# 61957c4c (пин); неги-браки: 'wc ow wc 5 vw wc 5 vw wc 5 vw' = 0xFE
# 59 Б ff73c458 (СОВПАЛ: bad word1 — emit 14 Б = ow-хвост со слотом
# F1 = 0x00F00FF1 = 15732721 DEFAULT WORK_CELL, W_Current не
# сменился); bad d1 = 0xFE 45 Б 29ba6852 (СОВПАЛ, emit 0); bad d2 =
# 0xFE 49 Б c4165c69 (СОВПАЛ пин W-90: emit = vw-tail1 4 Б); bad d3 =
# 0xFE 53 Б 9700c6d4 (НОВЫЙ пин, emit 8 Б); bad d4 = 0xFE 57 Б
# 34b360e8 (НОВЫЙ пин, emit 12 Б); bad word2 = 0xFE 45 Б 4ff7c705
# (СОВПАЛ); bad word5 = 0xFE 49 Б 95856a78 (СОВПАЛ пин W-90); bad
# word8 = 0xFE 53 Б da1f9de7 (НОВЫЙ пин); bad word11 = 0xFE 57 Б
# e94de9b1 (НОВЫЙ пин); bad word0/мусор = f3667180 (СОВПАЛ ×2); 'wc 5
# vw wc ow wc 5 vw wc 5 vw' = 0xFE 63 Б 4684f2f1 (НОВЫЙ пин: bad
# word4 'ow' — emit 18 Б = vw-хвост1 + ow-хвост 14 Б — stage1
# БРАКУЕТ); 'wc 5 vw wc 5 vw wc ow wc 5 vw' = 0xFE 67 Б 0d22dfbf
# (НОВЫЙ пин: bad word7 — emit 22 Б); 'wc 5 vw wc 5 vw wc 5 vw wc ow'
# — stage1 ПРИНИМАЕТ (71 Б 0xFF 07151ce6, НОВЫЙ KEY-пин: emit 26 Б =
# 3 vw-хвоста (12 Б) + ow-хвост 14 Б — ЕДИНСТВЕННЫЙ несущий BE32
# ow-хвоста = 0x00F00FF8 DEFAULT WORK_CELL, word10 = 'ow' НЕ цифра →
# слот дефолт) — том молчит: v4 = 0 → PA = 7, pVw4 = 0 → S = 11.
# Итог: **770 ток** <= 1022, компил stage1 =
# **1062 Б 0xFF Token 0x302 = 770 md5 2a47c028**, детерминизм OK.
# Честная матрица probe102c OK С ПЕРВОГО ПРОГОНА (хвост БЕЗ U8-пары —
# 3 ток/хвост): **15 целей BYTE-OK против свежего stage1** (база
# 8669285e = пин probe96..101-карт, точка, точка+мусор, 9 носителей —
# РАЗНЫЕ md5 несущих слотов W-72 ×4; + 3 tracked-цели
# c1679afd/6ea2be4c/0ae99a72) + **74/74 негов молчат**. NEW-пины
# W-102: t3×3×3×3-vw том + 3 tracked цели (РАЗНЫЕ md5 — несущие
# слоты W-72 ×4; _90 = 0ae99a72 СОВПАЛ карта-кейс 10).
# EMIT: VW_TAIL1 (честный хвост T3-'vw' стейтмента 1, карта probe102:
# ТОЛЬКО BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1; закон W-72:
# ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d, хвост БЕЗ ведущего U8 —
# 3 ток/хвост; урок W-98 (U8-пара 'nb X em' + 'nb 3 0 8 sc') НЕ
# применяется — хвосту НЕЧЕГО писать U8'ом) ->
# VW_TAIL2 (тот же хвост с reslot: BE32(cell[wc2] = слот F3+d2)) ->
# VW_TAIL3 (тот же хвост с reslot3: BE32(cell[wc3] = слот F3+d3)) ->
# RESLOT4 (переиспользование wc0: RESET cell[wc0] = F3_MINUS_48 +
# 'wc 0 vw' на word10 → cell[wc0] = F3+d4 — слот1 УЖЕ прочитан
# VW_TAIL1, CHECK-фазы завершены; ИДЕОМ = INIT + CHECK1 C1) ->
# VW_TAIL4 (тот же хвост с переиспользованным wc0: BE32(cell[wc0] =
# слот F3+d4) — честный emit базы probe102 00f00ff8 ×4) -> вердец ->
# отчёт (Token = 12: 'nb 1 2' 'wo' — токенов слоя ДО терминатора,
# точка не считается) -> SEAL/END. Честный дизайн (= W-101
# sp-структура, хвосты vw):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для VW_TAIL1)
#   + pVw1 (word2 == LE2('vw') = 30582, 'v' в МЛАДШЕМ байте, 0x7776,
#   PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 vw' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для VW_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок RELOAD2 W-84)
#   + pVw2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' (НЕ через 'nb(F5), cp': F5 = wc2 = СЛОТ d2 после reslot
#   CHECK2; 'eq 0' = прецедент TAIL_CHECK W-93/W-94/W-96) + C3
#   reslot3: RESET cell[wc3] = F3_MINUS_48 + 'wc 3 vw' на word7 →
#   cell[wc3] = F3+d3 (НЕСУЩИЙ для VW_TAIL3; wc3 = 15732726 СВОБОДНА:
#   stash в PF) + pVw3 (word8 == PB, PD += ) — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — валид-сравнение через
#   'eq 0' (F5 отравлен) + pVw4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = терминатор слоя) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('vw') = 30582 → wc7 — 'v' в МЛАДШЕМ байте
# [урок W-65/W-79/W-90], 0x7776; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t3333vw.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('vw' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('vw' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('vw' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('vw' stmt-4)
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
                             # 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ
                             # TAIL_CHECK)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('vw') = 30582 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH W-102
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(30582), 'ne', 'wc', '7', 'sv',           # 'vw' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для VW_TAIL1 (карта probe102:
          # 'wc 7 vw …' → BE32(FA))
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pVw1 = (word2 == LE2('vw'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pVw1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (vw-аккумулятор)
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
          # затем 'wc 2 vw' на word4 -> cell[wc2] = 15732723 + d2.
          # НЕСУЩИЙ для VW_TAIL2 (карта probe102: '… wc 7 vw …' →
          # BE32(FA) во ВТОРОМ хвосте). wc2 = F5 — ПОСЛЕ последнего
          # F5-cp (valid2 сравнился выше; дальше F5 не читается
          # CHECK1/CHECK2 — честный порядок RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pVw2 = (word5 == LE2('vw'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVw2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (vw-аккумулятор)
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
          # затем 'wc 3 vw' на word7 -> cell[wc3] = 15732723 + d3.
          # НЕСУЩИЙ для VW_TAIL3 (карта probe102: '… wc 7 vw …' →
          # BE32(FA) в ТРЕТЬЕМ хвосте). wc3 = 15732726 — СВОБОДНА
          # (stash W-96/W-98/W-99/W-100/W-101/W-102 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pVw3 = (word8 == LE2('vw'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVw3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = терминатор слоя)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (vw-аккумулятор)
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
          # wc0 ПОСЛЕ VW_TAIL3)
          # D4: pVw4 = (word11 == LE2('vw'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVw4
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

# RESLOT4 = переиспользование wc0 для слота d4 (ИДЕОМ W-96/W-98/W-99/
# W-100/W-101): RESET cell[wc0] = F3_MINUS_48, затем 'wc 0 vw' на
# word10 (d4) → cell[wc0] = 15732723 + d4. НЕСУЩИЙ для VW_TAIL4
# (карта probe102: '… wc 5 vw wc 7 vw' → BE32(FA) в ЧЕТВЁРТОМ хвосте —
# НОВЫЙ пин 16763076: ЧЕТВЁРТЫЙ несущий слот; '… wc 0 vw' →
# BE32(F3)).
# Слот1 уже прочитан VW_TAIL1 (emit-порядок TAIL1→TAIL2→TAIL3→
# RESLOT4→TAIL4); CHECK-фазы завершены до затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']

# EMIT: VW_TAIL1 (честный хвост T3-'vw' стейтмента 1, карта probe102:
# ТОЛЬКО BE32(cell[wc0] = слот F3+d1 НЕСУЩИЙ — chain1; закон W-72:
# ЕДИНСТВЕННЫЙ BE32 хвоста читает F3+d, хвост БЕЗ ведущего U8 —
# 3 ток/хвост) -> VW_TAIL2 (тот же хвост с reslot: BE32(cell[wc2] =
# слот F3+d2)) -> VW_TAIL3 (тот же хвост с reslot3: BE32(cell[wc3] =
# слот F3+d3)) -> RESLOT4 (переиспользование wc0: RESET cell[wc0] =
# F3_MINUS_48 + 'wc 0 vw' на word10 → cell[wc0] = F3+d4 — слот1 УЖЕ
# прочитан VW_TAIL1, CHECK-фазы завершены; ИДЕОМ = INIT + CHECK1 C1)
# -> VW_TAIL4 (тот же хвост с переиспользованным wc0: BE32(cell[wc0]
# = слот F3+d4) — честный emit базы probe102 00f00ff8 ×4) -> вердец
# -> отчёт (Token = 12)
VW_TAIL1 = ['wc', '0', 'ow']                        # BE32(слот F3+d1 — chain1)
VW_TAIL2 = ['wc', '2', 'ow']                        # BE32(слот F3+d2 — reslot)
VW_TAIL3 = ['wc', '3', 'ow']                        # BE32(слот F3+d3 — reslot3)
VW_TAIL4 = ['wc', '0', 'ow']                        # BE32(слот F3+d4 — RESLOT4)
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
       + VW_TAIL1 + VW_TAIL2 + VW_TAIL3 + RESLOT4 + VW_TAIL4 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe102\pos_wc14v3t3333vw.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t3333vw tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
