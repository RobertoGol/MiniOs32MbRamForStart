# -*- coding: utf-8 -*-
# Сборщик честного ПЯТИстейтментного тома
# 'wc d va wc d va wc d va wc d va wc d va'
# Shape-T3×5-va (веха-23, спринт 91, W-111, TKT-052): СТРИМ — ВОСЬМАЯ
# (ПОСЛЕДНЯЯ) ПЯТИстейтментная T3-форма (после ow W-104, te W-105, as
# W-106, pr W-107, sv W-108, sp W-109, vw W-110). ВСЕ ПЯТЬ хвостов
# НЕСУЩИЕ (va-хвост 6 Б = U8 0x12 = 18₁₀ [урок probe57/W-64: nb-литералы
# ДЕСЯТИЧНЫЕ] + U8 0x19 = 25₁₀ + BE32(слот F3+d) — закон W-73: BE32
# хвоста читает СЛОТ, U8-пары по уроку W-98; прецеденты va-закона:
# T3×T3-va W-91 `89d4c4` 8479bb87, T3×4-va W-103 69 Б 917128ff,
# T3-va-single 'wc 5 va' = 51 Б d4766ef5; 5-stmt va-поток (карта
# probe103) = 75 Б 26da57b5, emit 121900f00ff8 ×5 = 30 Б, 6-stmt = 81 Б
# c3276c5e) => d1..d5 НЕ инвары — как у vw-тома W-110 (те же ПЯТЬ
# reslot'ов; хвост 6 Б = 21 ток против 4 Б = 3 ток у vw — U8-пары
# ['nb 1 8','em','nb 3 0 8','sc'] + ['nb 2 5','em','nb 3 0 8','sc']).
# База = wc14v3t33333vw-структура (W-110) + va-хвосты (закон W-73) +
# честная карта probe111 (102 кейса, свежий stage1 на каждую цель,
# G:\...\Temp\opencode\probe111\_t111_card.py).
# stage1 для T3×5-va целей = 75 Б 0xFF Token 15, emit = [va-T3-хвост]
# ×5 = 30 Б; база 'wc 5 va' ×5 = 26da57b5 (пин probe103-карты — снята
# как «5-stmt va-поток»; СОВПАЛ картой probe111 (кейс 0, свежий
# stage1); полный hex: header CRC a39ef25e + emit 121900f00ff8 ×5 +
# FF + BE32(15) + 20 нулей). 6-stmt va-поток = 81 Б c3276c5e (пин
# probe103 СОВПАЛ probe111). 7-stmt va-поток = 87 Б d311ba02 (НОВЫЙ
# пин probe111, emit 42 Б, Token 21).
# **СЛОТ НЕСУЩИЙ В КАЖДОМ ХВОСТЕ (закон W-73 ×5)** — носители дают
# РАЗНЫЕ md5 (карта probe111: слот1 = 078a9f5b/слот2 = f7871fc7/
# слот3 = 817a08a2/слот4 = 603ffe99/слот5 = 6bd7342a; прецедент:
# 4 носителя T3×4-va probe103 af188fa8/783d6eaf/823ae74d/e5e8021e).
# --- ЧЕСТНАЯ КАРТА + ПРИЁМКА probe111 (снята и принята) ---
# КАРТА probe111 (card111.txt): stage1 для T3×5-va целей = 75 Б
# 0xFF Token 15; база 'wc 5 va' ×5 = 26da57b5 (пин probe103 СОВПАЛ;
# полный hex: header CRC a39ef25e + emit 121900f00ff8 ×5 + FF +
# BE32(15) + 20 нулей); точка/точка+мусор = база. **9 НОСИТЕЛЕЙ = 9
# РАЗНЫХ md5**: слот1 = 078a9f5b (FA)/слот2 = f7871fc7/слот3 =
# 817a08a2/слот4 = 603ffe99 (RESLOT4)/слот5 = 6bd7342a (RESLOT5 —
# ПЯТЫЙ несущий НОВЫЙ KEY для va, прецедент W-110 vw 24569b25)/
# FA FA FA FA F8 = f4eedd96/F3 ×5 = f254bbd0/F4 F6 F8 FC F8 =
# 0eecd51a/FC FB F3 F4 F8 = 01cb385e. 6-stmt = 81 Б c3276c5e (пин
# probe103 СОВПАЛ); 7-stmt = 87 Б d311ba02 (НОВЫЙ, emit 42 Б, Token
# 21). Смеси 8 kinds × 5 позиций = 40 НОВЫХ пинов va-роли (том
# молчит: pVaX = 0 → PD = 4 → S <= 15; полный список —
# card111.txt/accept111.txt). Кресты 5-stmt: word15 = '3' = 80 Б
# 29d71c11 (НОВЫЙ: emit 35 Б = 5 va-хвостов + digit-tail 15
# 00000003, Token 16), word3/6/9/12 = '3' = c5b4305f/68a43f01/
# d6b76f1e/9ef95675 (НОВЫЕ), word15 = 'va' = 81 Б c1f077dd (НОВЫЙ
# KEY: stage1 парсит 16-й ток 'va' как ШЕСТОЙ va-стейтмент, Token 16
# ≠ 6-stmt Token 18), '3 3' = 85 Б f9a20498 (НОВЫЙ, emit 40 Б);
# 2-stmt кресты СОВПАЛИ W-91/probe103 (66ed9dd3/f2174453/223e6120/
# 8db7af23); singles/сироты СОВПАЛИ (d4766ef5, a6f09ea2, 7b987a13,
# 87817a4b, 61957c4c, b733ee4c); неги: bad word1 'va' = 0xFE 51 Б
# cdb8c657 (НОВЫЙ: emit 6 Б 121900f00ff1 = va-хвост1 со слотом F1);
# bad d1 = 0xFE 45 Б 29ba6852 (СОВПАЛ, kind-independent); bad
# d2..d5 = 0xFE 51/57/63/69 Б f5435378/d435afca/9c13c8b0/ab8098fc
# (НОВЫЕ: emit 6/12/18/24 Б); bad word2 = 45 Б 4ff7c705 (СОВПАЛ);
# bad word5/8/11/14 = 0xFE 51/57/63/69 Б 69f882df/2610c7d5/
# d25f3217/6de0160a (НОВЫЕ: emit 6/12/18/24 Б); bad word0/мусор =
# f3667180 (СОВПАЛ ×2); bad word4/7/10 'va' = 0xFE 57/63/69 Б
# 0b3d714e/855fe60e/b14dce57 (НОВЫЕ: emit 12/18/24 Б — брак в
# середине подтверждён); **KEY bad word13 'va' — stage1 ПРИНИМАЕТ =
# 75 Б 0xFF 695766e4** (НОВЫЙ KEY-пин: emit 30 Б = 5 va-хвостов, 5-й
# со слотом-ДЕФОЛТОМ 0x00F00FF8 в BE32-части, Token 14 ≠ база
# Token 15; прецедент W-110 vw 94de01cd/W-109 sp 0db85b07/W-108 sv
# ab45118d/W-107 pr f1b0d964/W-106 as 49a13420) — том молчит: v5 = 0
# → PA = 9 → S <= 15.
# ЧЕСТНЫЙ ИТОГ ПРИЁМКИ W-111 (probe111c, accept111.txt): том собран
# **926 ток** <= 1022; компил тома свежим stage1 ×2 = **1338 Б 0xFF
# md5 aa59659c** (реп 0000039E = 926), детерминизм OK. Честная
# матрица probe111c: **15/15 целей BYTE-OK против свежего stage1**
# (база 26da57b5 = пин probe103-карт СОВПАЛ, точка, точка+мусор; 9
# носителей = 9 РАЗНЫХ md5 — несущие слоты W-73 ×5; tracked _33 =
# b90aea10, _37 = 2faf8f22, _90 = 01cb385e = карта-кейс 11 СОВПАЛ) +
# **90/90 негов молчат**. Прогон №1 драйвера прервался багом печати
# emit() в САМОМ драйвере — UnicodeEncodeError ('×' не кодируется в
# cp1251-консоль) ДО сборки/компила; правка скрипта, НЕ тома; все
# пины выше — прогон №2.
# --- КОНЕЦ блока карта+приёмка probe111 ---
# ПЯТЬ reslot'ов — chain1 d1→wc0 (CHECK1) + reslot d2→wc2 (CHECK2) +
# reslot3 d3→wc3 (CHECK3) + RESLOT4 d4→wc0 (переиспользование wc0,
# W-96/W-98/W-102/W-103/W-106/W-107/W-108/W-109/W-110) + RESLOT5 d5→wc2
# (переиспользование wc2 — W-102/W-104/W-106/W-107/W-108/W-109/W-110);
# свободных wc-ячеек НЕТ: wc0/wc2/wc3 = СЛОТЫ d1/d2/d3, wc1 = INIT F4,
# wc4 = INIT SRC_BUFFER, wc5 = COPY-счётчик, wc6 = PA, wc7 = PB, wc8 =
# PC, wc9 = PD; ЕДИНСТВЕННЫЙ BE32 читает ОДНУ ячейку —
# переиспользование после чтения слота VA_TAIL1 (emit-порядок TAIL1 →
# TAIL2 → TAIL3 → RESLOT4 → TAIL4 → RESLOT5 → TAIL5), CHECK-фазы
# завершены до затвора — безопасно (ИДЕОМ W-96/W-98/W-99/W-102/W-103/
# W-106/W-107/W-108/W-109/W-110).
# ЧЕСТНОЕ СЖАТИЕ W-104: CHECK1/CHECK2 — валид через 'gt 9' + stash PF +
# cp F5 (F5 = wc2 чист ДО reslot CHECK2); CHECK3/CHECK4/CHECK5 —
# 'gt 9' + 'eq 0' НАПРЯМУЮ (VM OP_LOAD 0x1A оставляет bad в acc, 'eq 0'
# сравнивает acc, va acc не портят — снято с CtOs-Emu/ctos_vm.py,
# доказано regr104; F5 отравлен reslot CHECK2 — 'eq 0', а не cp).
# ТЕРМИНАЦИЯ: EOF ИЛИ точка на word15 (ШЕСТНАДЦАТОЕ слово) — ОБА =
# база (карта probe111: точка, точка+мусор = база; прецедент probe103
# кейсы 1/2 для T3×4-va); pEOF = eq(word15, 0) +
# eq(word15, 46) через stash-ячейку STASH = PF = 15732733 (bad-flag
# МЁРТВ после CHECK5; 15732723/15732725/15732726 = СЛОТЫ d1/d2/d3 —
# TERM-фаза читает их 'wc 0 ow'/'wc 2 ow'/'wc 3 ow' ПОСЛЕ TAIL_CHECK).
# G-затвор: PA (= p0+v1+p0-2+v2+p0-3+v3+p0-4+v4+p0-5+v5 = 10) + PD (=
# pVa1+pVa2+pVa3+pVa4+pVa5 = 5) + pEOF == 16. Форма W-104/W-106/W-107/
# W-108/W-109/W-110: 'su 9' + 'su 3' + 'su 3' + 'eq 1' (S - 15 == 1
# ⟺ S == 16; недобор S < 15 → затвор молчит; caps: PA <= 10, PD <= 5,
# pEOF <= 1 → S = 16 ТОЛЬКО при честном p0,v1,p0-2,v2,p0-3,v3,p0-4,v4,
# p0-5,v5, pVa1..pVa5 = 1 И word15 ∈ {0, '.'}). НЕТ RELOAD2 (digit-tail
# d55 не существует в T3×5: word15 = терминатор слоя). Ключ-развязки
# (том обязан молчать, ВСЕ пины сняты честно): смеси 8 kinds на ВСЕХ
# ПЯТИ позициях — stage1 ПРИНИМАЕТ, том молчит: pVaX = 0 → PD = 4 →
# S <= 15 (пины probe111, analog vw-роли W-110: 40 пинов); 4/3/2-стейтментные va-потоки — stage1 ПРИНИМАЕТ
# (va ×4 = 69 Б 917128ff [пин W-103], va ×3 = 63 Б 61c72bef, va ×2 =
# 57 Б 8479bb87 [пины W-91/probe103]) — том молчит: PD = 0; потоки
# других kinds ×4 — stage1 ПРИНИМАЕТ (pr ×4 = 81 Б 34f4a890 [W-99];
# as ×4 = 89 Б 3f6d8893 [W-98]; te ×4 = 49 Б 40dc0e48 [W-97]; sv ×4 =
# 65 Б 05df0915 [W-100]; sp ×4 = 65 Б c02a9b43 [W-101]; vw ×4 = 61 Б
# 8669285e [W-102]; ow ×4 = 101 Б c39da5d5 [W-96]; ow ×3/×2 =
# 977e2a7a/40251c66 СОВПАЛИ W-95/W-94) — том молчит: word15 =
# 'va'/'pr'/'as'/'te'/'ow' → pEOF = 0 (PD = 0 у чужих); if ×4 —
# stage1 БРАКУЕТ (0xFE 60 Б ebe049f9, пин W-92) — том молчит; 6-stmt
# va-поток — stage1 ПРИНИМАЕТ ('wc 5 va' ×6 = 81 Б c3276c5e [пин
# probe103], emit 36 Б = 6 хвостов; точка-вариант тот же) — том
# молчит: word15 = 'wc' → pEOF = 0 → S = 15; 7-stmt = 87 Б d311ba02
# (НОВЫЙ пин probe111) — S = 15; кресты: digit-tails и 'va' на
# word15 — пины probe111 (word15 = '3' = 80 Б 29d71c11 [Token 16];
# word3/6/9/12 = '3' = c5b4305f/68a43f01/d6b76f1e/9ef95675; 'va' на
# word15 = 81 Б c1f077dd [6-й parse, Token 16 ≠ 6-stmt Token 18];
# '3 3' = 85 Б f9a20498; том молчит: pEOF = 0 / PA < 10); singles/
# сироты:
# 'wc 5 va' = 51 Б d4766ef5 (пин probe103), 'wc 5 va 3' = 56 Б
# a6f09ea2 (пин probe103), сирота 'wc 5 va wc 5' = 51 Б 7b987a13
# (пин probe103), 'wc 5 sp' = 50 Б 87817a4b (пин W-101), 'wc 5 pr' =
# 54 Б 61957c4c (пин W-99), 'wc 5 ow' = 59 Б b733ee4c (пин W-85); неги-
# браки 0xFE: bad d1 / bad word2 / bad word0/мусор — СОВПАЛИ probe102/
# probe110 (29ba6852, 4ff7c705, f3667180 ×2 — kind-independent);
# bad d2..d5 = 0xFE 51/57/63/69 Б f5435378/d435afca/9c13c8b0/
# ab8098fc (НОВЫЕ: emit 6/12/18/24 Б); bad word1 'va' = 0xFE 51 Б
# cdb8c657 (НОВЫЙ: emit 6 Б 121900f00ff1 = va-хвост1 со слотом F1);
# bad word5/8/11/14 = 0xFE 51/57/63/69 Б 69f882df/2610c7d5/
# d25f3217/6de0160a (НОВЫЕ); bad word4/7/10 'va' = 0xFE 57/63/69 Б
# 0b3d714e/855fe60e/b14dce57 (НОВЫЕ: emit 12/18/24 Б); **KEY: bad
# word13 'va' — stage1 ПРИНИМАЕТ (75 Б 0xFF 695766e4, НОВЫЙ
# KEY-пин: emit 30 Б = 5 va-хвостов, 5-й со слотом-ДЕФОЛТОМ
# 0x00F00FF8 в BE32-части [прецедент as W-106 49a13420 / pr W-107
# f1b0d964 / sv W-108 ab45118d / sp W-109 0db85b07 / vw W-110
# 94de01cd: word НЕ цифра → слот дефолт], Token 14 ≠ база
# Token 15)** — том молчит: valid6 = 0 → PA = 9 → S <= 15.
# EMIT: VA_TAIL = честный хвост T3-'va' стейтмента (закон W-73: U8
# 0x12 = 18₁₀ + U8 0x19 = 25₁₀ + BE32(слот) ('wc N ow') — U8-пары
# ['nb 1 8','em','nb 3 0 8','sc'] + ['nb 2 5','em','nb 3 0 8','sc'],
# 6 Б, 21 ток; BE32(cell[wcX] = слот F3+d НЕСУЩИЙ — карта probe103:
# 'wc 7 va …' → BE32(FA) = 00f00ffa; 'wc 0 va …' → BE32(F3))
# -> VA_TAIL1 (chain1) -> VA_TAIL2 (reslot) -> VA_TAIL3 (reslot3)
# -> RESLOT4 (переиспользование wc0: RESET cell[wc0] = F3_MINUS_48 +
# 'wc 0 sv' на word10 → cell[wc0] = F3+d4 — слот1 УЖЕ прочитан
# VA_TAIL1, CHECK-фазы завершены; ИДЕОМ = INIT + CHECK1 C1) ->
# VA_TAIL4 (BE32(cell[wc0] = слот F3+d4) — ЧЕТВЁРТЫЙ НЕСУЩИЙ СЛОТ;
# честный emit базы probe103: 121900f00ff8 ×5) -> RESLOT5
# (переиспользование wc2 — W-102/W-104/W-106/W-107/W-108/W-109/W-110:
# RESET cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word13 → cell[wc2] =
# F3+d5 — слот2 УЖЕ прочитан VA_TAIL2) -> VA_TAIL5 (BE32(cell[wc2] =
# слот F3+d5) — ПЯТЫЙ НЕСУЩИЙ) -> вердец -> отчёт (Token = 15: 'nb 1 5'
# 'wo' — токенов слоя ДО терминатора, точка не считается) -> SEAL/END.
# Честный дизайн (= W-110 vw-структура, хвосты va):
#   CHECK1 = скан T3-стейтмента 1 (слова 0..2): p0 (word0 == 'wc',
#   PA = ) + valid(d1) digit-block (word1) + C1 chain1: cell[wc0] =
#   F3_MINUS_48 + word1-символ = 15732723 + d1 (НЕСУЩИЙ для VA_TAIL1)
#   + pVa1 (word2 == LE2('va') = 24950 = 0x6176, 'v' в МЛАДШЕМ байте,
#   PB = wc 7, PD = ) — БЕЗ digit-block d31 (word3 = 'wc' stmt-2).
#   CHECK2 = скан T3-стейтмента 2 (слова 3..5): p0-2 (word3 == 'wc',
#   PA += ) + valid(d2) digit-block (word4) + C2 reslot: RESET
#   cell[wc2] = F3_MINUS_48 + 'wc 2 sv' на word4 → cell[wc2] = F3+d2
#   (НЕСУЩИЙ для VA_TAIL2; wc2 = F5 — ПОСЛЕ последнего F5-cp: valid2
#   сравнился, дальше F5 не читается — честный порядок W-84/W-96) +
#   pVa2 (word5 == PB, PD += ) — БЕЗ digit-block d32.
#   CHECK3 = скан T3-стейтмента 3 (слова 6..8): p0-3 (word6 == 'wc',
#   PA += ) + valid(d3) digit-block (word7) — валид-сравнение через
#   'eq 0' НАПРЯМУЮ (сжатие W-104; НЕ через 'nb(F5), cp': F5 = wc2 =
#   СЛОТ d2 после reslot CHECK2; 'eq 0' = прецедент TAIL_CHECK
#   W-93/W-94/W-96) + C3 reslot3: RESET cell[wc3] = F3_MINUS_48 +
#   'wc 3 sv' на word7 → cell[wc3] = F3+d3 (НЕСУЩИЙ для VA_TAIL3;
#   wc3 = 15732726 СВОБОДНА: stash в PF) + pVa3 (word8 == PB, PD += )
#   — БЕЗ digit-block d33.
#   CHECK4 = скан T3-стейтмента 4 (слова 9..11): p0-4 (word9 == 'wc',
#   PA += ) + valid(d4) digit-block (word10) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pVa4 (word11 == PB, PD += ) — БЕЗ
#   digit-block d44 (word12 = 'wc' stmt-5) — БЕЗ reslot4 (слот4
#   материализуется RESLOT4 в EMIT-фазе).
#   CHECK5 = скан T3-стейтмента 5 (слова 12..14): p0-5 (word12 ==
#   'wc', PA += ) + valid(d5) digit-block (word13) — 'eq 0' НАПРЯМУЮ
#   (сжатие W-104; F5 отравлен) + pVa5 (word14 == PB, PD += ) — БЕЗ
#   digit-block d55 (word15 = терминатор слоя) — БЕЗ reslot5 (слот5
#   материализуется RESLOT5 в EMIT-фазе).
# INIT = 5 групп (F3_MINUS_48 → wc0; F4 LE2('wc') = 25463 → wc1;
# SRC_BUFFER → wc4; PB LE2('va') = 24950 = 0x6176 → wc7 — 'v' в
# МЛАДШЕМ байте [урок W-65/W-67]; PC '.' = 46 → wc8).
# Лимит честного тома вехи-23 = 1022 ток.
# pos_wc14v3t33333va.words

def nb(value):
    assert isinstance(value, int) and 0 <= value <= 4294929951
    return 'nb ' + ' '.join(str(value))

SRC_BUFFER = 10485760        # word0 ('wc' stmt-1)
SRC_WORD2  = 10485764        # word1 (d1)
WORD3      = 10485768        # word2 ('va' stmt-1)
WORD4      = 10485772        # word3 ('wc' stmt-2)
WORD5      = 10485776        # word4 (d2)
WORD6      = 10485780        # word5 ('va' stmt-2)
WORD7      = 10485784        # word6 ('wc' stmt-3)
WORD8      = 10485788        # word7 (d3)
WORD9      = 10485792        # word8 ('va' stmt-3)
WORD10     = 10485796        # word9 ('wc' stmt-4)
WORD11     = 10485800        # word10 (d4)
WORD12     = 10485804        # word11 ('va' stmt-4)
WORD13     = 10485808        # word12 ('wc' stmt-5)
WORD14     = 10485812        # word13 (d5)
WORD15     = 10485816        # word14 ('va' stmt-5)
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
PB = 15732730                # АДРЕС-конст LE2('va') = 24950 (через INIT)
PC = 15732731                # АДРЕС-конст '.' = 46 (через INIT)
PD = 15732732
PF = 15732733                # bad-flag (том-C честно) = STASH
F4 = 15732724                # АДРЕС-конст LE2('wc') = 25463 (через INIT)

INIT = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
        nb(25463), 'ne', 'wc', '1', 'sv',
        nb(SRC_BUFFER), 'ne', 'wc', '4', 'sv',
        nb(24950), 'ne', 'wc', '7', 'sv',           # 'va' (PB, LE2)
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
          # = 15732723 + d1 — НЕСУЩИЙ для VA_TAIL1 (закон W-73; карта
          # probe111: 'wc 7 va …' → BE32(FA) = 078a9f5b; 'wc 0 va …'
          # → BE32(F3) = f254bbd0)
          nb(SRC_WORD2), 'va',
          'wc', '0', 'as',
          # D1: pVa1 = (word2 == LE2('va'), const PB = wc 7)
          nb(WORD3), 'va', nb(PB), 'cp',
          'wc', '9', 'sv']              # PD = pVa1

# CHECK2 = скан T3-стейтмента 2 (слова 3..5; 3 токена — БЕЗ digit-
# block d32: word6 = 'wc' третьего стейтмента)
CHECK2 = [
          # A2: p0-2 = (word3 == 'wc'), PA += (va-аккумулятор)
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
          # НЕСУЩИЙ для VA_TAIL2 (закон W-73; карта probe111:
          # '… wc 7 va …' → BE32(FA) во ВТОРОМ хвосте = f7871fc7;
          # '… wc 0 va …' → BE32(F3) = f254bbd0 [F3 ×5]).
          # wc2 = F5 — ПОСЛЕ последнего F5-cp (valid3 сравнился выше;
          # дальше F5 не читается CHECK1/CHECK2 — честный порядок
          # RELOAD2 W-84)
          nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
          nb(WORD5), 'va',
          'wc', '2', 'as',
          # D2: pVa2 = (word5 == LE2('va'), const PB = wc 7), PD +=
          nb(WORD6), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVa2

# CHECK3 = скан T3-стейтмента 3 (слова 6..8; 3 токена — БЕЗ digit-
# block d33: word9 = 'wc' четвёртого стейтмента)
CHECK3 = [
          # A3: p0-3 = (word6 == 'wc'), PA += (va-аккумулятор)
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
          # НЕСУЩИЙ для VA_TAIL3 (закон W-73; карта probe111:
          # '… wc 7 va …' → BE32(FA) в ТРЕТЬЕМ хвосте = 817a08a2).
          # wc3 = 15732726 — СВОБОДНА (stash W-95..W-110 = PF)
          nb(F3_MINUS_48), 'ne', 'wc', '3', 'sv',
          nb(WORD8), 'va',
          'wc', '3', 'as',
          # D3: pVa3 = (word8 == LE2('va'), const PB = wc 7), PD +=
          nb(WORD9), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVa3
          # БЕЗ digit-block d33: word9 = 'wc' stmt-4

# CHECK4 = скан T3-стейтмента 4 (слова 9..11; 3 токена — БЕЗ digit-
# block d44: word12 = 'wc' пятого стейтмента)
CHECK4 = [
          # A4: p0-4 = (word9 == 'wc'), PA += (va-аккумулятор)
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
          # wc0 ПОСЛЕ VA_TAIL3)
          # D4: pVa4 = (word11 == LE2('va'), const PB = wc 7), PD +=
          nb(WORD12), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVa4
          # БЕЗ digit-block d44: word12 = 'wc' stmt-5

# CHECK5 = скан T3-стейтмента 5 (слова 12..14; 3 токена — БЕЗ digit-
# block d55: word15 = терминатор слоя)
CHECK5 = [
          # A5: p0-5 = (word12 == 'wc'), PA += (va-аккумулятор)
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
          # W-96/W-104/W-106/W-107/W-108/W-109/W-110/TAIL_CHECK)
          'eq', '0',
          'wc', '6', 'as',              # PA += valid6
          # БЕЗ reslot5: свободных wc-ячеек НЕТ — слот5
          # материализуется RESLOT5 в EMIT-фазе (переиспользование
          # wc2 ПОСЛЕ VA_TAIL4)
          # D5: pVa5 = (word14 == LE2('va'), const PB = wc 7), PD +=
          nb(WORD15), 'va', nb(PB), 'cp',
          'wc', '9', 'as']              # PD += pVa5
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
# W-100/W-101/W-102/W-103/W-104/W-106/W-107/W-108/W-109/W-110): RESET
# cell[wc0] = F3_MINUS_48, затем 'wc 0 sv' на word10 (d4) → cell[wc0] =
# 15732723 + d4. НЕСУЩИЙ для VA_TAIL4 (закон W-73; карта probe111:
# '… wc 7 va' (слот4) = 603ffe99 — ЧЕТВЁРТЫЙ несущий; '… wc 0 va' →
# BE32(F3) = f254bbd0 [F3 ×5]; прецедент probe103 RESLOT4 T3×4-va:
# '… wc 5 va wc 7 va' → BE32(FA) в ЧЕТВЁРТОМ хвосте e5e8021e). Слот1
# уже прочитан VA_TAIL1 (emit-порядок TAIL1→
# TAIL2→TAIL3→RESLOT4→TAIL4→RESLOT5→TAIL5); CHECK-фазы завершены до
# затвора.
RESLOT4 = [nb(F3_MINUS_48), 'ne', 'wc', '0', 'sv',
           nb(WORD11), 'va',
           'wc', '0', 'as']
# RESLOT5 = переиспользование wc2 для слота d5 (W-102/W-104/W-106/
# W-107/W-108/W-109/W-110, идеом = RESLOT4 W-96): RESET cell[wc2] =
# F3_MINUS_48, затем 'wc 2 sv' на word13 (d5) → cell[wc2] = 15732723 +
# d5. НЕСУЩИЙ для VA_TAIL5 (закон W-73; ПЯТЫЙ несущий НОВЫЙ KEY для
# va — W-103 = T3×4 без RESLOT5; прецедент RESLOT5 = W-104 ow/W-106
# as/W-107 pr/W-108 sv/W-109 sp/W-110 vw; карта probe111: '… wc 7 va'
# (слот5) = 6bd7342a). Слот2 уже
# прочитан VA_TAIL2 (emit-порядок TAIL1→TAIL2→TAIL3→RESLOT4→TAIL4→
# RESLOT5→TAIL5); CHECK-фазы завершены до затвора.
RESLOT5 = [nb(F3_MINUS_48), 'ne', 'wc', '2', 'sv',
           nb(WORD14), 'va',
           'wc', '2', 'as']

# EMIT: VA_TAIL = честный хвост T3-'va' стейтмента (закон W-73: U8
# 0x12 = 18₁₀ + U8 0x19 = 25₁₀ + BE32(слот) ('wc N ow') — U8-пары по
# уроку W-98, 6 Б, 21 ток)
VA_TAIL1 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '0', 'ow']                    # BE32(слот F3+d1 — chain1)
VA_TAIL2 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '2', 'ow']                    # BE32(слот F3+d2 — reslot)
VA_TAIL3 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '3', 'ow']                    # BE32(слот F3+d3 — reslot3)
VA_TAIL4 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '0', 'ow']                    # BE32(слот F3+d4 — RESLOT4)
VA_TAIL5 = ['nb 1 8', 'em', 'nb 3 0 8', 'sc',   # U8 18 (0x12)
            'nb 2 5', 'em', 'nb 3 0 8', 'sc',   # U8 25 (0x19)
            'wc', '2', 'ow']                    # BE32(слот F3+d5 — RESLOT5)
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
       + VA_TAIL1 + VA_TAIL2 + VA_TAIL3 + RESLOT4 + VA_TAIL4 \
       + RESLOT5 + VA_TAIL5 \
       + EMIT_TAIL + ['te', 'es', 'te']

PROGRAM = INIT + ['mk', nb(311), 'sc', nb(EOF_CELL), 'va', 'eq', '0', 'if',
                  ] + COPY + ['jb', 'es'] + MAIN

MAX_USER_WORDS = 1022   # честная граница вехи-23: 1024 чтения потока =
                        # 1022 ток + терминатор-слово (regr55)

TOKENS = len(' '.join(PROGRAM).split())
POS_PATH = r'G:\Windows\RJ\AppData\Local\Temp\opencode\probe111\pos_wc14v3t33333va.words'
assert TOKENS <= MAX_USER_WORDS, ('отказ: токенов %d > %d'
                                  % (TOKENS, MAX_USER_WORDS))
with open(POS_PATH, 'w', encoding='ascii') as f:
    f.write(' '.join(PROGRAM) + '\n')
print('pos_wc14v3t33333va tokens:', TOKENS, 'limit:', MAX_USER_WORDS)
