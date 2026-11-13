# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d te wc d te wc d te wc d te wc d te'
# Shape-T3×5-te (веха-23, спринт 85, W-105, TKT-052): СТРИМ — вторая
# ПЯТИстейтментная T3-форма (после ow W-104). ВСЕ ПЯТЬ хвостов
# КОНСТАНТНЫ (te-хвост = ГОЛЫЙ U8 05 — 1 Б, прецедент W-86 T3×T3-te
# [emit 05+05, d1/d2 ИНВАРЫ] и W-97 te ×4; d НЕ читается хвостом) =>
# d1/d2/d3/d4/d5 — честные ИНВАРЫ. Слот/chain/reslot/RELOAD2 НЕ нужны
# вовсе — НЕТ ни одного слота (свободны wc0/wc2 = F5/wc3).
# База = wc14v3t3333te-структура (W-97, te-структура W-86) + честная
# карта probe105 (100 кейсов, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe105\_t105_card.py): stage1 для T3×5-te
# целей = 50 Б 0xFF Token 15, emit = 05×5 = 5 Б; база 'wc 5 te' ×5 =
# 511f2235 (пин probe97-карты СОВПАЛ — снята как «5-stmt te-поток»;
# честный полный hex probe105: header CRC 8580d86c + emit 0505050505 +
# FF + BE32(15) + 20 нулей).
# **d1..d5 ИНВАРЫ ×5 — ВСЕ 9 d-вариантов = ОДИН md5 511f2235 (честный
# инвариант, НЕ ошибка; прецедент W-86/W-92/W-97)**: 'wc 7 te' на
# каждой из ПЯТИ позиций = 'wc 7 te' ×4 + 'wc 5 te' = 'wc 0 te' ×5 =
# 'wc 1 te wc 3 te wc 5 te wc 9 te wc 5 te' = 'wc 9 te wc 8 te wc 0 te
# wc 1 te wc 5 te' = база 511f2235 (emit 0505050505 во ВСЕХ) — tracked-
# цели W-105 ДАЮТ ТОТ ЖЕ md5 (инвариант ×5).
# БЕЗ chain1/reslot/reslot3/RESLOT4/RESLOT5 (слотов нет вовсе —
# ИДЕОМ W-97); ЧЕСТНОЕ СЖАТИЕ W-104: stash-пересылка nb(PF) sv/va
# после 'gt 9' ИЗБЫТОЧНА — VM OP_LOAD 0x1A оставляет bad в acc,
# 'eq 0' (mode 0x16) сравнивает acc, sv/va acc не портят (снято с
# CtOs-Emu/ctos_vm.py, доказано regr104 CHECK3/4/5) — применено ко
# ВСЕМ ПЯТИ digit-блокам: 'gt 9' + 'eq 0' НАПРЯМУЮ; F5 НЕ НУЖЕН
# (нет ни одного F5-cp), PF НЕ хранит bad (только pEOF-stash
# TAIL_CHECK).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база ('wc 5 te' ×5 + ' .' = 511f2235 =БАЗА карта-кейс 1; мусор после
# точки '… . 3' = база кейс 2); pEOF = eq(word15, 0) + eq(word15, 46)
# через stash-ячейку STASH = PF = 15732733 (bad-flag МЁРТВ — digit-
# блоки сравниваются 'eq 0' без PF).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pTe1+pTe2+pTe3+pTe4+pTe5 = 5) + pEOF == 16. Форма W-104: 'su 9' +
# 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; недобор S < 15 →
# затвор молчит; caps: PA <= 10, PD <= 5, pEOF <= 1 → S = 16 ТОЛЬКО
# при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,p0-5,v5,pTe1..pTe5 = 1 И
# word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail d55 не существует в
# T3×5: word15 = терминатор слоя). Ключ-развязки (том обязан молчать,
# ВСЕ пины сняты честно картой probe105): ow/sv/sp/vw/va/pr/if/as-
# смеси на ВСЕХ ПЯТИ позициях — stage1 ПРИНИМАЕТ (ow eec87bcb/
# d8c5a8a8/e64b5c84/794a4ef6/1f8a444f; sv 2c1f58da/17a2118c/93142ef6/
# bd1666a0/f76fd057; sp c137d645/77a6b7a4/0e08033d/f413c399/908f0589;
# vw 399110f1/df54ea9b/ec5f16f6/3a4a6adb/f41cb9a1; va 11b9cba3/
# 3f24dc9f/d655c4f9/35629d11/00d4a509; pr 15463c76/a0114fa2/7d2d883f/
# 4909ec22/ef98ffb4; if 0437a13c/40fa1997/57ed8d29/9ee3a759/fbda68f6;
# as c51ee56a/f4984663/e4436631/7218b6cc/49dc0c7f) — том молчит:
# pTeX = 0 → PD <= 4 → S <= 15; 4-стейтментные потоки других kinds —
# stage1 ПРИНИМАЕТ ('wc 5 te' ×4 = 49 Б 40dc0e48, пин W-97 СОВПАЛ,
# emit 05×4 = 4 Б; as ×4 = 89 Б 3f6d8893; sv ×4 = 65 Б 05df0915;
# sp ×4 = 65 Б c02a9b43; vw ×4 = 61 Б 8669285e; va ×4 = 69 Б 917128ff;
# pr ×4 = 81 Б 34f4a890; ow ×4 = 101 Б c39da5d5, пин W-96 СОВПАЛ) —
# том молчит: word12 = 'te'/'wc'/'ow' → pEOF = 0 (PD = 0 у чужих);
# if ×4 — stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92 СОВПАЛ) — том
# молчит; 6-stmt te-поток — stage1 ПРИНИМАЕТ ('wc 5 te' ×6 = 51 Б
# e1bf059a [пин W-97 СОВПАЛ], emit 05×6 = 6 Б, Token 18; точка-вариант
# тот же) — том молчит: word15 = 'wc' → pEOF = 0 → S = 15; 7-stmt =
# 52 Б 46f1f382 (НОВЫЙ пин, emit 7 Б) — S = 15; 4-stmt ow-поток = 101
# Б c39da5d5 (пин W-96 СОВПАЛ) — том молчит; 3-stmt = 87 Б 977e2a7a
# (пин W-95 СОВПАЛ) — S = 10; 2-stmt = 73 Б 40251c66 (пин W-94
# СОВПАЛ) — S = 7; кресты: 'wc 5 te' ×5 + '3' = 55 Б 74aaf2f7 (НОВЫЙ
# пин: emit 10 Б = 05×5 + digit-tail 15 00000003) — word15 = '3' →
# pEOF = 0; 'wc 5 te 3 …' = 55 Б a28dd0ca (НОВЫЙ пин: digit-tail
# ПОСЛЕ хвоста 1 — word3 = '3' → p0-2 bad); '… wc 5 te 3 …' = 55 Б
# 3e1342c4 (word6), '… 3 …' = 55 Б d8b33465 (word9), '… wc 5 te 3
# wc 5 te' = 55 Б ca0aabe2 (word12) — НОВЫЕ пины: digit МЕЖДУ
# стейтментами → p0-X bad; 'wc 5 te' ×5 + 'te' = 51 Б 4a40a459 (НОВЫЙ
# KEY-пин: stage1 парсит 16-й ток 'te' как ШЕСТОЙ te-стейтмент —
# emit 05×6, Token 16 ≠ 6-stmt Token 18) — том молчит: word15 =
# 'te' → pEOF = 0; 'wc 5 te' ×5 + '3 3' = 60 Б fb80be63 (НОВЫЙ пин,
# emit 15 Б = 05×5 + digit-tail ×2); 2-stmt кресты 'wc 5 te 3 wc 5 te
# 3' = 57 Б 45188fc1 (= T4×T4-te база W-68), 'wc 5 te wc 5 te 3 3' =
# 57 Б 6a6f0a94 (пин W-86 СОВПАЛ), 'wc 5 te wc 5 te 3' = 52 Б
# df520cf9 (пин W-77 СОВПАЛ), 'wc 5 te wc 5 te te' = 48 Б 3dacb5b7
# (пин W-97 СОВПАЛ) — том молчит; singles/сироты: 'wc 5 te' = 46 Б
# bac85372 (пин W-97 СОВПАЛ), 'wc 5 te 3' = 51 Б 495e8056 (пин W-97
# СОВПАЛ), сирота 'wc 5 te wc 5' = 46 Б a3bac192 (пин W-86 СОВПАЛ),
# 'wc 5 vw' = 49 Б 00ce976e, 'wc 5 sv' = 50 Б 6a16ae85, 'wc 5 ow' =
# 59 Б b733ee4c (пин W-85 СОВПАЛ); неги-браки: 'wc te wc 5 te …' =
# 0xFE 46 Б 03928005 (НОВЫЙ пин: bad word1 — emit 1 Б 05); 'wc z te
# …' = 0xFE 45 Б 29ba6852 (СОВПАЛ); 'wc 5 te wc z te …' = 0xFE 46 Б
# 06448daf (СОВПАЛ W-86); '… wc z te …' = 0xFE 47 Б dcf812e7
# (СОВПАЛ W-97); '… wc z te …' = 0xFE 48 Б c9b55156 (СОВПАЛ W-97);
# 'wc 5 te' ×4 + 'wc z te' = 0xFE 49 Б **f40cae08** (НОВЫЙ пин: bad
# d5 — emit 4 Б = 05×4 до брака); bad word2 = 0xFE 45 Б 4ff7c705
# (СОВПАЛ); bad word5 = 0xFE 46 Б d0059999 (СОВПАЛ W-86); bad word8 =
# 0xFE 47 Б d692bb98 (СОВПАЛ W-97); bad word11 = 0xFE 48 Б c1ccc2a5
# (СОВПАЛ W-97); 'wc 5 te' ×4 + 'wc 5 xx' = 0xFE 49 Б **0d6e4524**
# (НОВЫЙ пин: bad word14 — emit 4 Б); bad word0/мусор = f3667180
# (СОВПАЛ ×2); 'wc 5 te wc te …' = 0xFE 47 Б 30331574 (НОВЫЙ пин:
# bad word4 'te' — emit 2 Б = 05×2); '… wc te …' = 0xFE 48 Б
# d5beb267 (НОВЫЙ пин: bad word7 — emit 3 Б); '… wc te wc 5 te' =
# 0xFE 49 Б c333b5ad (НОВЫЙ пин: bad word10 'te' в СЕРЕДИНЕ —
# stage1 БРАКУЕТ, emit 4 Б — брак в середине подтверждён); 'wc 5 te'
# ×4 + 'wc te' — stage1 ПРИНИМАЕТ (50 Б 0xFF **d5b76114**, НОВЫЙ
# KEY-пин: emit 05×5 — te-хвост КОНСТАНТЕН, bad digit на последней
# позиции НЕ меняет emit, Token 14 ≠ база Token 15) — том молчит:
# v5 = 0 → PA = 9 → S = 15.
# ИТОГ приёмки (probe105c, accept105.txt): том ТРЕБУЕТСЯ ток <= 1022,
# собран = вердец 0xFF (двойной компил — детерминизм OK); 15 целей
# BYTE-OK против свежего stage1 (база 511f2235; ВСЕ 9 d-вариантов =
# ТОТ ЖЕ md5 — честный инвариант d1..d5 ×5; tracked _33/_37/_90 = ТОТ
# ЖЕ md5); неги 88/88 молчат.
# EMIT: TERM1 (честный хвост T3-'te' стейтмента 1, карта probe105:
# U8 0x05 = 5₁₀ — 'nb 5' 'em' [урок probe57/W-64: nb-литералы
# ДЕСЯТИЧНЫЕ], 1 Б — d1-ИНВАР: хвост не читает слот) -> TERM2 ->
# TERM3 -> TERM4 -> TERM5 -> вердец -> отчёт (Token = 15: 'nb 1 5'
# 'wo' — токенов слоя ДО терминатора, точка не считается) -> SEAL/
# END. Честный дизайн (= W-97 te-структура + CHECK5, БЕЗ chain/
# reslot/RESLOT4/RESLOT5, pTe вместо pOw, eq-0-сжатие W-104):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + pTe1 (word2 == LE2('te')
#   = 25972, 't' в МЛАДШЕМ байте, PB = wc 7, PD = ) — БЕЗ chain1
#   (d1-ИНВАР: te-хвост константен, слот не нужен) — БЕЗ digit-block
#   d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + pTe2 (word5 == PB,
#   PD += ) — БЕЗ reslot (слот не нужен) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) + pTe3 (word8 == PB,
#   PD += ) — БЕЗ reslot3 — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) + pTe4 (word11 == PB,
#   PD += ) — БЕЗ digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ
#   RESLOT4 (слотов нет вовсе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) + pTe5 (word14 ==
#   PB, PD += ) — БЕЗ digit-block d55 (word15 = терминатор слоя) —
#   БЕЗ RESLOT5 (слотов нет вовсе).
# INIT = 4 группы (F4 LE2('wc') = 25463 → wc1; SRC_BUFFER → wc4; PB
# LE2('te') = 25972 → wc7 — 't' в МЛАДШЕМ байте [урок W-65/W-67,
# 0x6574 = 25972]; PC '.' = 46 → wc8). F3_MINUS_48-группа НЕ нужна:
# слотов нет вовсе (d-ИНВАРЫ ×5; wc0/wc2 = F5/wc3 СВОБОДНЫ в W-105).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333te.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('te' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('te' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('te' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('te' stmt-4)
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('te' stmt-5)
WORD16     = 10485820        # word15 — терминатор слоя T3×5
                             # (EOF: VM допишет '.', либо '.' в файле)
EOF_CELL  = 15732722
EMIT_CELL = 15732720
PF = 15732733                # pEOF-stash (том-C честно, прецедент
                             # W-95..W-104; bad НЕ хранится — digit-
                             # блоки сравниваются 'eq 0' НАПРЯМУЮ,
                             # честное сжатие W-104)
PA = 15732729
PB = 15732730                # АДРЕС-конст LE2('te') = 25972 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(25972), 'ne', 'wc', '7', 'sv',           # 'te' (PB, LE2)
        nb(46), 'ne', 'wc', '8', 'sv']              # '.' (терминатор)
        # F3_MINUS_48-группа НЕ нужна: слотов нет вовсе (d-ИНВАРЫ ×5)

COPY = [nb(EMIT_CELL), 'va', 'wc', '4', 'sp', 'va', 'ad', '4', 'sv',
        'wc', '5', 'va', 'ad', '1', 'sv']

# CHECK1 = скан T3-стейтмента 1 (слова 0..2; 3 токена — БЕЗ digit-
# block d31: word3 = 'wc' второго стейтмента)
CHECK1 = [nb(SRC_BUFFER), 'va',
          nb(F4), 'cp',                 # acc = p0 = (word0 == 'wc')
          'wc', '6', 'sv',              # PA = p0
          # B1: честный digit-block (v1d): bad в acc — 'eq 0' сравнивает
          # acc НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0' =
          # mode 0x16; честное сжатие W-104 — stash-пересылка ИЗБЫТОЧНА)
          nb(SRC_WORD2), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          'eq', '0',                    # acc = valid1 = (bad == 0)
          'wc', '6', 'as',              # PA += valid1
          # D1: pTe1 = (word2 == LE2('te'), const PB = wc 7)
          # НЕТ chain1 (d1-ИНВАР: te-хвост константен, слот не нужен)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pTe1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (as-аккумулятор)
          nb(WORD4), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B2: честный digit-block на word4 (d2) — 'eq 0' НАПРЯМУЮ
          # (честное сжатие W-104). d2-ИНВАР: te-хвост stmt-2
          # константен — слот НЕ читается, БЕЗ reslot
          nb(WORD5), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          'eq', '0',                    # acc = valid2 = (bad2 == 0)
          'wc', '6', 'as',              # PA += valid2
          # D2: pTe2 = (word5 == LE2('te'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (as-аккумулятор)
          nb(WORD7), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B3: честный digit-block на word7 (d3) — 'eq 0' НАПРЯМУЮ
          nb(WORD8), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          'eq', '0',                    # acc = valid3 = (bad3 == 0)
          'wc', '6', 'as',              # PA += valid3
          # D3: pTe3 = (word8 == LE2('te'), const PB = wc 7), PD +=
          # НЕТ reslot3 (слот не нужен)
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe3

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (as-аккумулятор)
          nb(WORD10), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B4: честный digit-block на word10 (d4) — 'eq 0' НАПРЯМУЮ
          nb(WORD11), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          'eq', '0',                    # acc = valid4 = (bad4 == 0)
          'wc', '6', 'as',              # PA += valid4
          # БЕЗ RESLOT4: слотов нет вовсе (d-ИНВАРЫ ×5)
          # D4: pTe4 = (word11 == LE2('te'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe4

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (as-аккумулятор)
          nb(WORD13), 'va', nb(F4), 'cp',
          'wc', '6', 'as',
          # B5: честный digit-block на word13 (d5) — 'eq 0' НАПРЯМУЮ
          nb(WORD14), 'va',
          'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8', 'su', '8',
          'gt', '9',
          'eq', '0',                    # acc = valid5 = (bad5 == 0)
          'wc', '6', 'as',              # PA += valid5
          # БЕЗ RESLOT5: слотов нет вовсе (d-ИНВАРЫ ×5)
          # D5: pTe5 = (word14 == LE2('te'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pTe5
          # БЕЗ digit-block d55: word15 = терминатор слоя

# F2/G2: pEOF = (word15 == 0 ИЛИ word15 == '.') — арифметическая
# сумма ДВУХ сравнений через stash-ячейку STASH = PF = 15732733
# (bad НЕ хранится — digit-блоки сравниваются 'eq 0' НАПРЯМУЮ);
# терминатор слоя T3×5 на ШЕСТНАДЦАТОМ слове (WORD16 = 10485820).
# Затвор: PA (10) + PD (5) + pEOF == 16 — через 'su 9' + 'su 3' +
# 'su 3' + 'eq 1' (S - 15 == 1 ⟺ S == 16; форма W-104 — прецедент
# снят; все immediate ОДНОразрядные; caps: S = 16 ТОЛЬКО при PA = 10,
# PD = 5, pEOF = 1 — честный 5-стейтментный te-поток)
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

# EMIT: TERM1..TERM5 (честные хвосты T3-'te' стейтментов 1..5 — карта
# probe105: emit = 0505050505, ВСЕ ПЯТЬ хвостов константны, d1..d5
# инвары) -> вердец -> отчёт (Token = 15)
EMIT_HEAD = [nb(304), 'sc',
        'nb 1 1 2 9 5 9 8 8 0 3', 'wo',                  # 0x43544F53
        'nb 1 6 8 4 3 0 0 8', 'wo',                      # 0x01010100
        'nb 3 3 5 5 4 4 3 2 0', 'wo',                    # 0x14000000
        'nb 4 2 9 4 9 4 5 4 5 0', 'wo',                  # 0xFFFFAAAA
        'nb 0', 'wo']                                    # CRC-заполнитель
TERM1 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-1 te)
TERM2 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-2 te)
TERM3 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-3 te)
TERM4 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-4 te)
TERM5 = ['nb 5', 'em', 'nb 3 0 8', 'sc']      # U8 5 (хвост stmt-5 te)
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
       + TERM1 + TERM2 + TERM3 + TERM4 + TERM5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe105\pos_wc14v3t33333te.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333te tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
