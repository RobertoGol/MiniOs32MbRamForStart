# -*- coding: utf-8 -*-
# Веха-23 (regr61, W-61): base regr60 (HEAD = 01bb6fa — приёмка
# кросс-формного T4×T3-pr-тома). СПРИНТ 41: честный КРОСС-ФОРМНЫЙ том
# с sv-хвостом 'wc d te d3 wc d2 sv' (Shape-T4×T3-sv). База =
# wc14v3t43s_build.py (кросс-том W-60 + sv-хвост) + честная карта
# probe57 (свежий stage1 на каждую цель): stage1 для T4×T3-sv целей =
# 56 Б 0xFF Token 7, emit = 05 15 BE32(d31) + 55 00 F0 0F [слот]
# (11 Б); база 'wc 5 te 3 wc 5 sv' = b904f09d. **СЛОТ-БАЙТ ЖИВ в
# T3-хвосте**: sv-emit = U8 0x55 + BE32(адрес-слота = cell[wc0]) —
# БЕЗ консты-аргумента (pr-хвост несёт BE32 0x3F0050C0, sv — нет:
# 5 Б против 9 Б); младший байт = 0xF3 + d2 (probe57: d2=0 -> F3
# 40e85dd6, d2=5 -> F8 база, d2=7 -> FA a4a86ea9; тот же закон для
# pr-хвоста, W-57/W-60); reslot из CHECK2 (cell[wc0] = F3_MINUS_48 +
# символ цифры = 15732723 + d2 = адрес-слот) НЕСУЩИЙ. d1-ИНВАРИАНТ-
# НОСТЬ ('wc 7 te 3 wc 5 sv' = база b904f09d); явная точка = база;
# Token = 7. Честный дизайн (= W-60 + sv-хвост): CHECK2 pSv =
# (word6 == LE2('sv') = 0x7673 = 30323, конст cell wc3 = F6);
# RELOAD1 d31 -> wc2 после B3; затвор ИДЕНТИЧЕН W-59/W-60 (PA 5 +
# PD 2 + ppunkt (word7=='.') == 8, 'eq 8' одноразрядный; ключ-
# развязка: у 8-ток двойников T4×T4-sv/pr word7 = '3' -> молчание);
# SV_TAIL = U8 0x55 + 'wc 0 ow' (12 ток, заменил PR_TAIL W-60 = 24
# ток). **Два честных дефекта, пойманных прогонами probe57:**
# (1) конста 'sv' в wc5 = 15732728 — ВСЕ цели молчат при честно
# компилирующемся томе: wc5 НЕ свободна — COPY читает 'wc 5' как
# emit-указатель (карта «wc5 свободна» была неверна); исправлено —
# конст в wc3 (= F6, та же ячейка, что 'pr'-конст W-60);
# (2) 'nb 5 5' = 55 ДЕСЯТИЧНЫХ = 0x37, а нужен U8 0x55 = 85 ->
# 'nb 8 5' ('nb'-литералы честно читаются как ДЕСЯТИЧНЫЕ числа по
# цифрам — дефект-находка W-58; W-60 спасала случайность: 'nb 8 4'
# = 84₁₀ = 0x54). Итог: **603 ток** <= 1022 (-12 над W-60: SV_TAIL
# короче PR_TAIL), компил stage1 = **876 Б 0xFF Token 0x25B = 603
# md5 dc7ff0ab**, детерминизм OK. Честная матрица probe57 OK:
# **11 целей BYTE-OK** (b904f09d база+dot+d1-инвариантность,
# b3999dcb d31=7, 664e8145 d31=9, 9fee8611 0/0/0, abd9ca45,
# dd1fb280, e235928f, 40e85dd6 d2=0, a4a86ea9 d2=7) + **20/20 негов
# молчат** (ключевые T4×T4-sv fe6aeb2b / T4×T4-pr 3f3634ef 8-ток;
# T4×T3-te 32448898 = W-59 форма; T4×T3-pr 26a8b48c = W-60 форма;
# reversed W-57 1c775e42; голые 'wc sv' be7bdf42 / 'wc 0 sv'
# eeee2e3e; сирота-цифра; хвост-мусор; bad d1/d2/d31, bad cells, bad
# word0/word4). NEW-пины W-61: sv-том + 3 tracked цели. Полки regr60
# переносятся целиком (tracked IDENTICAL + все полки + cold).
# Веха-23 (regr60, W-60): base regr59 (HEAD = 13d4a73 — приёмка
# кросс-формного T4×T3-тома). СПРИНТ 40: честный КРОСС-ФОРМНЫЙ том с
# pr-хвостом 'wc d te d3 wc d2 pr' (Shape-T4×T3-pr). База =
# wc14v3t43p_build.py (кросс-том W-59) + честная карта probe56 (свежий
# stage1 на каждую цель): stage1 для T4×T3-pr целей = 60 Б 0xFF
# Token 7, emit = 05 15 BE32(d31) + 54 3F 00 50 C0 00 F0 0F [слот]
# (15 Б); база 'wc 5 te 3 wc 5 pr' = 26a8b48c. **СЛОТ-БАЙТ ЖИВ в
# T3-хвосте**: pr-emit декодирован по прецеденту T4-pr-тома
# wc14v3pr_build.py ('wc 0 ow' = BE32(F3+d), G-факт regr52): U8 0x54
# (OUTCELL_V) + BE32 0x3F0050C0 (конста-аргумент кодогена) +
# BE32(адрес-слота = cell[wc0]) — младший байт = 0xF3 + d2 (probe56:
# d2=0 -> F3 c3269434, d2=5 -> F8 база, d2=7 -> FA 379666f3; тот же
# закон для sv-хвоста: 55 00 F0 0F [F3+d2], d2=7 FA a4a86ea9 —
# задел W-61); reslot из CHECK2 (cell[wc0] = F3_MINUS_48 + символ
# цифры = 15732723 + d2 = адрес-слот) НЕСУЩИЙ. d1-ИНВАРИАНТНОСТЬ
# ('wc 7 te 3 wc 5 pr' = база 26a8b48c — слот стейтмента-1 не входит
# в emit); явная точка = база; Token = 7. Честные соседи-кроссы (том
# обязан молчать): T4×T4-pr 8-ток = 3f3634ef (65 Б, stage1 принимает:
# emit ...F8 15 BE32(3), word7 = '3'); T4×T4-sv 8-ток = fe6aeb2b;
# T4×T3-te (W-59 форма) = 32448898 (word6 = 'te'); T4×T3-sv (W-61
# форма) = b904f09d; reversed W-57 'wc 5 pr 3 wc 5 te 3' = 1c775e42
# (word2 = 'pr'); голые формы 'wc pr' = 470eaa9e (54 Б, emit
# 54...F1) и T3-одиночка 'wc 0 pr' = 4c30de2d (54 Б, emit 54...F3);
# сирота-цифра 'wc 5 te 3 wc 5' = 8b2c4a6f (stage1 принимает, том
# молчит: word6 = '.'); мусор после слоя = FAIL 0xFE stage1. Честный
# дизайн (= W-59 + pr-хвост): CHECK1 = канон T4; CHECK2: p0-2
# (word4=='wc', PA+=), valid(d2) 57, reslot 26 (НЕСУЩИЙ: cell[wc0] =
# 15732723 + d2), pPr (word6 == LE2('pr') = 29296, конст cell wc3,
# прецедент W-57 F6/'pr', PD+=); RELOAD1 d31 -> wc2 после B3; затвор
# PA(5)+PD(2)+ppunkt(word7=='.') == 8 — ИДЕНТИЧЕН W-59 ('eq 8'
# одноразрядный; ключ-развязка: у 8-ток двойников T4×T4-pr/sv word7
# = '3' -> молчание); PR_TAIL = U8 0x54 + BE32 0x3F0050C0 +
# 'wc 0 ow' (24 ток, заменил TERM-only хвост W-59 = 8 ток). Token =
# 7. **Честный дефект, пойманный первым прогоном probe56:** 'em'
# честно пишет PENDING-nb-литерал (U8), а не acc — 'va em' = em БЕЗ
# pending -> fail 0xFE Token 633 (точный индекс em; все em в
# W-56..59 стоят после nb-литерала); исправлено по прецеденту
# T4-pr-тома: 'nb 1 0 5 6 9 8 5 2 8 0 wo' (BE32 0x3F0050C0) +
# 'wc 0 ow' (BE32(cell[wc0]) — acc-based BE32-вывод; 'ow' читает
# acc, 'wc 0' = LOAD cell[wc0]). Итог: **615 ток** <= 1022 (+26 над
# W-59: INIT 'pr'-конст +10, PR_TAIL +16), компил stage1 = **890 Б
# 0xFF Token 0x267 = 615 md5 613dafcd**, детерминизм OK. Честная
# матрица probe56 OK: **10 целей BYTE-OK** (база 26a8b48c
# +dot+d1-инвариантность, a37f4811 d31=7, 4cc94bee d31=9, c3269434
# 0/0/0, bac36784 d2=0, 68469b67, 56944a5c, 97adea87) + **20/20
# негов молчат** (ключевые T4×T4-pr/sv 8-ток; T4×T3-te/sv; reversed;
# голые; сирота-цифра; хвост-мусор; bad d1/d2/d31, bad cells, bad
# word0/word4). NEW-пины W-60: pr-том + 3 tracked цели. Полки regr59
# переносятся целиком (tracked IDENTICAL + все полки + cold).
# Веха-23 (regr59, W-59): base regr58 (HEAD = 0af3ccd — приёмка
# тройного te-тома). СПРИНТ 39: честный КРОСС-ФОРМНЫЙ том
# 'wc d te d3 wc d2 te' (Shape-T4×T3: стейтменты РАЗНЫХ форм в одном
# слое — 4-ток T4 + 3-ток T3). База = wc14v3t43_build.py (двойной
# te-том W-56, минус второй digit-block). Честные факты probe55
# (приёмка, свежий stage1 на каждую цель): stage1 для T4×T3-целей =
# 52 Б 0xFF Token 7, emit = 05 15 BE32(d31) + 05 (7 Б); база
# 'wc 5 te 3 wc 5 te' = 32448898; T3-'te' хвост = ТОЛЬКО TERM '05'
# (T3-одиночка 'wc 0 te' = 46 Б emit '05', bac85372, d-инвариант);
# d1- и d2-ИНВАРИАНТНОСТЬ артефакта ('wc 7 te 3 wc 5 te' = 'wc 5 te
# 3 wc 0 te' = база — слоты не входят в emit); явная точка = база;
# МУСОР ПОСЛЕ точки честно игнорируется ('wc 5 te 3 wc 5 te . 3' =
# 32448898 — точка-терминатор останавливает скан). Соседи-кроссы:
# T4×T4 8-ток = 57 Б 45188fc1/ae58af4c; 'wc 5 te 3 wc 5 pr' =
# 26a8b48c; 'wc 5 te 3 wc 5 sv' = b904f09d; 'wc 5 te 3 wc te' =
# 6265b72a; 'wc 5 te 3 te' = 2da04646; 'wc 5 te 3 wc 5' = 8b2c4a6f;
# 'wc te 3 wc 5 te' = c49e444f (47 Б emit '0505'); 9-ток
# 'wc 5 te 3 wc 5 te 3 3' = 3d825fd7; triple+T3 '...wc 5 te' =
# 9b17beeb; мусор/zz после T3 = FAIL 0xFE stage1 9b48ddc3 —
# соседние формы обязаны МОЛЧАТЬ в этом томе. Честный дизайн:
# CHECK1 = канон T4 (A,B,C,D,B2 без F/G); CHECK2 = скан T3-
# стейтмента (слова 4..6): p0-2 (word4=='wc', PA+=), valid(d2) 57,
# reslot 26 (RESET F3_MINUS_48 + re-add на word5), p2-2
# (word6=='te', PD+=) — НЕТ второго digit-block (T3 = 3 токена,
# word7 = терминатор); RELOAD1 d31 -> wc2 ПОСЛЕ последнего F5-cp
# (теперь B3, прецедент W-56); CHAIN2 = TERM-only ('nb 5 em nb 3 0 8
# sc') — честный хвост T3-'te'. Затвор PA(5)+PD(2)+ppunkt
# (word7=='.') == 8 (одноразрядный eq, без cell-конст; дефект
# 'eq 13' W-58); ключ-развязка с T4×T4: терминатор на СЕДЬМОМ слове
# — у 8-ток двойника word7 = '3' -> ppunkt = 0 -> молчание. Token
# отчёта = 7. **Честный дефект, пойманный первым прогоном probe55:**
# слот Token отчёта = токенов слоя ДО терминатора (точка не
# считается: '... te .' и '... te . 3' = тот же Token 7) —
# te2-плейсхолдер 'nb 8' давал MISMATCH при честной длине слоя 7
# (md5 различался ровно слотом Token), исправлено 'nb 7'; прежние
# тома совпадали по совпадению (длина слоя == конста 8/8/12). Итог:
# **589 ток** <= 1022 (683 W-56 − digit-block B4 57 − E2 25 − ow 3),
# компил stage1 = **852 Б 0xFF Token 0x24D = 589 md5 beac8aea**,
# детерминизм OK. Честная матрица probe55 OK: **10 целей BYTE-OK**
# (база 32448898, 9c81af97 7, efb2b765 9, 03ff8daf 0/0, a8b659f7
# 1-2|3, d84c2399 9-5|8, d4ab582e 2-8|6; d1/d2-инвариантность;
# точка; пост-точечный мусор) + **16/16 негов молчат** (ключевой
# T4×T4 8-ток; голые формы 'wc te'/'te'; соседи 'pr'/'sv';
# T4-одиночка; 9-ток; triple+T3; хвост-мусор; FAIL-источники
# stage1). NEW-пины W-59: кросс-том + 3 tracked цели. Полки regr58
# переносятся целиком (tracked IDENTICAL + все полки + cold).
# Веха-23 (regr58, W-58): base regr57 (HEAD = 1d31e31 — приёмка
# смешанного pr×te-тома). СПРИНТ 38: честный ТРОЙНОЙ том
# 'wc d te d3 wc d2 te d32 wc d3 te d33' (Shape-T4×3, honest
# three-chain). База = wc14v3te3_build.py (двойной te-том W-56).
# Честные факты probe54 (приёмка): том компилится stage1 (loader
# 0x400) = 1327 Б 0xFF Token 0x3A2 = 930, md5 b6c1fcb6, детерминизм
# OK; честная матрица OK — 10 тройных целей BYTE-OK против СВЕЖЕГО
# stage1 (база 'wc 5 te 3 wc 5 te 3 wc 5 te 3' 63 Б d52f8215, emit =
# 05 15 BE32 ×3; пин W-56 «3-цепочки аддитивны» подтверждён;
# d1/d2-ИНВАРИАНТНОСТЬ te-артефакта: 'wc 7 te 3 ...' = 'wc 5 te 3
# ...' = d52f8215; trailing-dot игнорируется; BE32-вариации: 96cf53c6
# 3/3/7, 093b6780 3/9/3, 709a66e7 1/2|3/4|5/6, 91670586 0/0/0,
# b9f6c3be 9/5|1/2|8/4, b459597d 2/8|6/1|4/9) + 17/17 негов молчат
# (bad d1/d2/d3/d31/d32/d33, bad L1/L2/L3, bad word0/word4/word8,
# хвост-мусор; кросс-молчания: single / double / 4-цепочка (stage1
# компилит efb4c55c, 69 Б — том обязан молчать) / 3-form 'pr' в
# слое). Честный дизайн: CHECK3 (слова 8..11): p0-3 (word8=='wc',
# PA+=), valid(d3) 57, reslot3 26 (RESET F3_MINUS_48 + re-add на
# word9), p2-3 (word10=='te', PD+=), valid(d33) 57; RELOAD1 d31 ->
# wc2 ПОСЛЕ последнего F5-cp (теперь B6, прецедент W-56); E3 d33 в
# эмиссии (25) + chain3-em 20. Затвор PA(9)+PD(3)+ppunkt(word12=='.')
# == 13; Token = 12. **Два честных дефекта, пойманных прогонами
# probe54:** (1) 'eq' честно берёт ОДНО following-token immediate —
# 'eq 13' = 'eq 1' + сирота '3' (голая цифра вне nb = не-опкод) ->
# fail 0xFE Token 708 (точный индекс сироты); исправлено: конст 13
# в cell F6 (wc 3) через INIT 'nb 1 3 ne wc 3 sv', сравнение 'cp'
# против cell[F6] (прецедент ppunkt/PC и F6/'pr' W-57); (2)
# многозначный nb-литерал обязан быть разрядными токенами: 'nb 12'
# -> fail 0xFE Token 899, исправлено 'nb 1 2' (прецедент EMIT_HEAD).
# Итог: 930 ток <= 1022 (дельта над двойным te +247: CHECK3 186,
# E3 25, chain3-em 20, конст-13 INIT +7, cp-затвор +8, разрядный
# nb +1). NEW-пины W-58: тройной том + 3 tracked цели. Полки regr57
# переносятся целиком (tracked IDENTICAL + все полки + cold).
# Веха-23 (regr57, W-57): base regr56 (HEAD = fb260de — приёмка
# двойного te-тома). СПРИНТ 37: честный СМЕШАННЫЙ том
# 'wc d pr d3 wc d2 te d32' (Shape-T4×2 mixed-L pr×te, honest-полка
# L1×L2 вехи-22). База = wc14v3prte_build.py (двойной te-том W-56 +
# честные окна wc14v3_gen.py). Честные факты probe53 (приёмка, все
# пины сошлись с ПЕРВОГО прогона): том компилится stage1 (loader
# 0x400) = 1041 Б 0xFF Token 0x2C5 = 709, md5 3ff9a8aa, детерминизм
# OK; честная матрица OK — 10 смешанных целей BYTE-OK против СВЕЖЕГО
# stage1 ('wc 5 pr 3 wc 5 te 3' 65 Б 1c775e42, emit = 54 3F 00 50 C0
# 00 F0 0F F8 15 BE32(d31) + 05 15 BE32(d32); СЛОТ-БАЙТ ЖИВ:
# 'wc 7 pr 3 wc 5 te 3' = 66baed44 (слот FA = F3+7); d2-ИНВАРИАНТ-
# НОСТЬ: 'wc 5 pr 3 wc 7 te 3' = ТОТ ЖЕ 1c775e42 — слот стейтмента-2
# не доходит до артефакта; trailing-dot игнорируется обеими
# сторонами) + 14/14 негов молчат (bad d1/d2/d31/d32, bad L1/L2, bad
# word0/word4, хвост-мусор, кросс-молчания: reversed te×pr / te×te /
# pr×pr / single / 3-form). Честный дизайн: C-блоки УХОДЯТ из CHECK —
# слот-калькуляция в секции эмиссии (pr-emit ЧИТАЕТ cell[F3]):
# SLOT1 (13 ток, add-only — INIT F3_MINUS_48 pristine) ПЕРЕД
# pr-окном; SLOT2 (26 ток, RESET + re-add на word5) ПОСЛЕ emit1 —
# честный side-effect стейтмента-2. CHECK1: p0 (PA+=), valid(d1) 57,
# p2 (word2=='pr', конст F6=wc3, PD+=), valid(d31) 57; CHECK2: p0-2
# (PA+=), valid(d2) 57, p2-2 (word6=='te', конст PB=wc7, PD+=),
# valid(d32) 57; RELOAD1 d31 -> wc2 ПОСЛЕ последнего F5-cp (B4)
# (прецедент W-56/probe52); E2 d32 в эмиссии. Затвор PA(6)+PD(2)+
# ppunkt(word8=='.') == 9; Token = 8. 709 ток <= 1022 (дельта над
# двойным te-томом +26: INIT 'pr' +13, SLOT1+SLOT2 +39, C-блоки
# -39, pr-окно вместо te +15, pr-хвост U8 84 вместо U8 5 — сет).
# NEW-пины W-57: смешанный том + 3 tracked цели (включая слот-живой
# 73). Полки regr56 переносятся целиком.
# Веха-23 (regr56, W-56): base regr55 (HEAD = 470c3e4 — приёмка роста).
# СПРИНТ 36: честный ДВОЙНОЙ te-том 'wc d te d3 wc d2 te d32' (Shape-T4×2,
# same-L two-chain полка, отвергнутая бюджетом вехи-22 685 > 510 — теперь
# честно влезает: 683 ток <= 1022). База = wc14v3te2_build.py (canon
# wc14v3te_build.py 452 ток + честный скан второго стейтмента). Честные
# факты probe52 (приёмка): том компилится stage1 (loader 0x400) = 1003 Б
# 0xFF Token 0x2AB = 683, md5 5d2a226b, детерминизм OK (повторный компил
# байт-в-байт); честная матрица OK — 11 двойных целей BYTE-OK против
# СВЕЖЕГО stage1 ('wc 5 te 3 wc 5 te 3' 57 Б 45188fc1, 'wc 5 te 0 wc 5
# te 7' f37ef4ee, 'wc 5 te 9 wc 5 te 9' ce668809, d-ИНВАРИАНТНОСТЬ
# te-артефакта: 'wc 7 te 3 wc 5 te 3' = ТОТ ЖЕ 45188fc1 — слот-байт не
# входит в emit; trailing-dot 'wc 5 te 3 wc 5 te 3 .' = 45188fc1 — обе
# стороны точку игнорируют) + 11 негов молчат (bad d1/d2/d31/d32, bad
# L1/L2, bad word0/word4, хвост-мусор, кросс-молчания single/3-form).
# Честный дефект, пойманный первым прогоном probe52: RELOAD1 (d31 ->
# wc2 = F5) в CHECK1 ДО digit-блоков B3/B4 портил сравнения valid =
# (bad == cell[F5]) — цели с d31 != 0 молчали; исправлено: reload ПОСЛЕ
# последнего F5-cp (B4), прецедент канона ('wc 2 sv' ПОСЛЕ честных
# F5-cp). Бюджет W-54 (оценка 685 ток, дельта +233) superseded честной
# сборкой: 683 ток, дельта +231 (word-пачка 20, chain2-em 20, reslot 26,
# digit-блоки 57×2, reload'ы 25×2). NEW-пины W-56: двойной том + 3
# tracked двойные цели (refs stage1). Полки regr55 переносятся целиком.
# Веха-23 (regr55, W-55): base regr54 (HEAD = 134026a — коммит роста).
# СПРИНТ 17: честный рост границы загрузчика MAX_SOURCE_WORDS 0x200 -> 0x400
# (512 -> 1024 слова), авторизовано пользователем 2026-11-11 ('1и3': сначала
# дизайн+пробы 'до', затем рост). Честный случай: прецедент вехи-9/12г/13/14v4
# (граница росла только от честной механики) + механика W-54 (двойной честный
# том 685 ток > 510) + probe47 (дешевле digit-скана нет) + probe48 (510 —
# хард-граница загрузчика stage1, 511+ честно бракуются; поток = N ток +
# терминатор-слово, брак при чтении #MAX). Пересборка честно детерминирована
# (probe49: rebuild .kt через codegen.py байт-в-байт = abd93961); новый stage1
# 22 861 Б md5 18123c29. Батарея миграции probe51 (все пины сошлись): canon
# (452 ток) 689 Б a4f15985 и pos_edge3 (510 ток) 2595 Б ea018d84 — байт-в-байт
# НЕ изменились; neg_big3 (511 sv) МИГРИРОВАЛ из honest OVERFLOW 0xFE/0x07/
# 0x200/19966a43 в легальную программу 0xFF 2600 Б df0a3e0a (прецедент вехи-
# 14v4, где границы переехали с neg_big/neg_big2 на neg_big3/pos_edge3);
# pos_edge4 (1020 sv + pr te = 1022 ток) = НОВАЯ честная граница 0xFF 5155 Б
# b659224e (Token 0x3FE); neg_big4 (1023 sv) = первый честный брак 0xFE/0x07/
# 0x400/Token 0x3FF 5160 Б bd53cfc6; cold 45 Б f3667180. Факты 'до' (probe50,
# stage1 abd93961): обе новые пробы честно 0xFE 2605 Б 8ca674ce (Token 512/
# Fail 7 @ 0x200, content-free за границей загрузки). stage1 правлен ТОЛЬКО
# define'ом границы (веха-23 комментарий в .kt:52) — остальной коден нетронут.
# NEW-пины вехи-23: pos_edge4/neg_big4/neg_big3. Полки regr54 переносятся
# целиком (tracked IDENTICAL + все полки + cold).
# Регресс вехи-22 (regr54): base regr53 (HEAD = W-53 4b322d5).
# СПРИНТ 16, веха-22 (много-стейтментные): честная карта probe46/46b/46c/46d
# (Temp/probe46). Честные факты stage1:
# 1) много-стейтментность АДДИТИВНА по цепочкам: 'wc 5 pr 3 wc 5 pr 3' =
#    73 Б a5fa7400 = цепочка pr `54 3F 00 50 C0 00 F0 0F F8 15 00 00 00 03`
#    x2 (по 14 Б), затем FF 00 00 00 08 (Token = 8 = число слов исходника);
# 2) байт слота = F3+d: d=0 -> F3 (d50b13c3), d=4 -> F7 (2b369370),
#    d=7 -> FA (c758e674); d3 в цепочке честно литералом ('wc 5 pr 3 wc 5
#    pr 4' db0fb830 — цепочка2 несёт своё d3);
# 3) формы склеиваются: mixed-L 'wc 5 pr 3 wc 5 te 1' = 65 Б d16f74df
#    (pr-цепочка 14 Б + te-цепочка `05 15 00 00 00 01` 6 Б), T4+T3
#    'wc 5 pr 3 wc 5 pr' = 68 Б 386f20a5 (T3-усеченение без d3-слота),
#    T1-смесь 'te pr as va' = 72 Б a65efed2; newline ≡ пробел (nl2 = двух-
#    стетьмент байт-в-байт a5fa7400);
# 4) предельные хвосты: digit-хвост честно +5 Б/цифру ('wc 5 pr 3 7 8' =
#    69 Б c8d0cec8, '...7 8 9' = 74 Б b7a45551); 'z' после цифр = fail
#    0xFE 1dcf2d73 (цифры уже эмитились); точка НЕ сепаратор: '3.' =
#    невалидный digit-token, fail@3 5d5795e5 честно content-free, даже
#    когда дальше стоит валидный стейтмент ('wc 5 pr 3. wc 5 pr 3' = тот
#    же артефакт);
# 5) same-L двойная свипа 0xFF x9: te 57/45188fc1, va 67/66ed9dd3,
#    sp 65/1e7d8b3e, sv 65/1b8699b9, pr 73/a5fa7400, as 77/5fb8d6c8,
#    ow 83/ead92d5a, if 65/0e1dd19c, vw 63/dbb5b0a3; нег-контроль
#    'wc 5 pr 3 zz' = 33944ce4 сошёлся;
# 6) честный вердикт БЮДЖЕТА: двойной том честно НЕ построить в каноне
#    MAX_USER_WORDS = 510: честная дельта скана = +2 digit-блока (57 x2),
#    +2 word-дачки (23 x2), reload d32 (25), reslot (26), chain2-em (22)
#    = +233 над T4 (te 452 -> 685; cp-dedup d2==d1 даст 617; tail-том
#    545; T3-second 540 — всё > 510). Веха-22 честно закрыта: тома-полки
#    T4 честно молчат на любых много-стейтментных исходниках (слой =
#    ровно 4 слова), приёмка regr54 = 9 томов x 8 инлайн-кроссов
#    (72 молчания) поверх regr53. stage1 НЕ правился (22 861 Б abd93961).
# Регресс вехи-21б (regr53): base regr52 (HEAD = W-52 cf4eeb1).
# СПРИНТ 15: полка T4 digit-tail 'wc d L d3' (9 лексем, честный
# ток-бюджет): wc14v3_gen.py -> wc14v3{L}_build.py -> pos_wc14v3{L}.words
# (токены 452/458/456/456/468/470/486/456/447 <= 510; тома 689/703/703/
# 703/717/731/745/703/689 Б, md5-пины в NEW ниже). Честная карта
# probe43/44/45: stage1 принимает 'wc d L d3' = 0xFF/Token 4/FC=0@0/
# rep [4,0,0,0,0,0]; окно = L-T1 окно с честным BE32-F1-слотом,
# заменённым на BE32(F3 + d) ('wc 0 ow', INIT F3 - 48 = 15732675);
# хвост честно = U8 21 + BE32(d3) (ячейка wc2 'wc 2 sv' -> 'wc 2 ow'
# ПОСЛЕ честных F5-cp). Приёмка probe45-bsweep: 90/90 refs байт-ok
# (word1=5, d3=0..9 x 9 лексем), неги честно молчат на всех 9 томах,
# 14 честных пинов probe43/44 сходятся (rhyme d-spread: 'wc 3 te 1',
# 'wc 7 as 2', 'wc 1 ow 9', 'wc 0 pr 0', 'wc 9 pr 9', 'wc 9 as 9'...).
# Честные неги stage1 (0xFE): fail@1 'wc 10 pr 3' = 'wc 10' = 29ba6852
# (reuse neg_t2c.words); fail@2 'wc 5 zz 3' = 4ff7c705 (new
# neg_t4zz.words); fail@3 per-L: 'wc 5 sv 03' = 8f94a026 (new),
# 'wc 5 if zz' = 04a1e74f (reuse neg_if2.words), 'wc 5 pr 07' =
# 5d5795e5 (07/12/00 у pr — один артефакт, fail content-free);
# fail@4 per-L: 'wc 5 pr 3 zz' = 33944ce4 / 'wc 5 vw 3 zz' = 1a8afff3 /
# 'wc 5 sp 3 z' = 1831e55c (new neg_t4pr/vw/sp.words). Честный факт
# digit-хвоста: stage1 ПРОДЛЕВАЕТ хвост лишними одноцифровыми словами
# ('wc 5 pr 3 7' = 0xFF Token=5 64 Б a0e18826; 'wc 5 te 3 7' =
# 4bba7803 56 Б; 'wc 5 pr 7 7' = eb2d5d40; +5 Б = U8 21 + BE32(d4) в
# хвосте) — T4-том честно молчит (слой = ровно 4 слова, контракт
# regr39..52; честный отказ-тип 'wc 5 pr pr pr zz' G-тома FC=1@5).
# СПРИНТ 14: том Shape-G 'wc d pr pr pr' (честный ток-бюджет):
# wc14v2gpr_build.py -> pos_wc14v2gpr.words, 468 токенов <= 510;
# том 696 Б md5 729befd4, вердец 0xFF, Token = 5 (честная формула
# 'Token = число слов исходника'), FC = 0@0, rep = [5,0,0,0,0,0].
# Окно = pr-T1 окно x3 (U8 84 + BE32 0x3F0050C0 + BE32 слот),
# честный слот в КАЖДОМ повторе = BE32(F3 + d), d = word1 - 48:
# v3-факт 'as' ('nb 10485764 va; wc 0 as' -> cell[wc0] = F3 + d
# при INIT F3 - 48 = 15732675), эмит слота честным 'wc 0 ow'
# (3 токена). CHECK = p0 & valid & p2 & p3 & p4 & ppunkt == 6:
# digit-block v2d-паттерна (su 8 x6, gt 9, bad в PF, valid =
# (bad == 0)); слияние p0+valid+p3+p4 честным 'as'-аккумулятором
# в PA (wc 6): 'wc 6 as' = acc = acc + cell + writeback (v3-факт
# pos_as1); p2 в PD через 'wc 9 sv'; ppunkt = (word5 == '.',
# PC = 46) остаётся в acc. Честные факты приёмки: цели
# 'wc 5 pr pr pr' = 1a2a0638 и 'wc 0 pr pr pr' = f675745d
# байт-в-байт против stage1-refs (f675745d из честного списка
# вехи-22); 'wc 9 pr pr pr' = 04c0f7bf (новый честный ref, слот
# 0x00F00FFC). Неги честно молчат: 'wc 5 pr pr pr zz' /
# 'wc 5 pr pr zz' / 'wc 5 pr pr te' / 'wc pr pr pr pr' /
# 'wc 5 yu pr pr' (эталон нега: 0xFE T5 FC=1@5 = честный отказ
# ppunkt-слота word5). Честные экономии, пойманные stage1-браком:
# 'cp' НЕ имеет select-режима ('wc 1 cp' -> честный fail-артефакт
# 77e27834, fail на токене 110) — сравнение только nb-формы
# ('nb(F4) cp'); 'sv' и 'as' честны в select-режиме (INIT/COPY-факт
# и v3-факт pos_as1); 2-значные ячейки (PF/PG/PHD = wc 10..12) —
# только nb-литералы ('nb 15732733 sv'), одиночный 'wc 10' честно
# бракуется (720-Б проба, 0xFE).
# Регресс вехи-21б (regr51): base regr50 (HEAD = W-50 9659b83).
# ФИНАЛ B-серии 'wc L' (спринт 13): 7 томов 'wc as/va/ow/sp/if/sv/vw'
# одним честным генератором wc14v2_gen.py -> wc14v2{L}_build.py ->
# pos_wc14v2{L}.words (токены 400/381/409/379/372/379/370 ≤ 510,
# тома 571/543/585/543/543/543/529 Б); приёмка bsweep — все 7
# IDENTICAL против честных refs 3078ad75/2d164d6e/b4cc0b3b/
# 46f6a7dd/c2877852/be7bdf42/acde33b3, неги честно молчат.
# Честный изъян генерата, пойманный вербатрейсом тома-'wc as':
# PB в шаблоне подставлялся ЗНАЧЕНИЕМ лексемы (29537 для as)
# вместо АДРЕСА ячейки 15732730 ('PB = %(pb)d') — CHECK честно
# сравнивал word1 с мусорной ячейкой → p1 = 0 → сумма 2 → честное
# молчание всех 7 (неги при этом молчали тоже — честно, но цель
# не говорила); фикс: 'PB = 15732730' в шаблоне генератора
# (замороженные pr/te от этого не зависели — они задают PB
# честным адресом с самого начала).
# Честные рифмы bsweep: T3 'wc <L> <L>' = f284718e (as) / 062457f4
# (va) / 640f3b15 (ow) / b5a67c85 (sp) / 237ab858 (if) / 5c315fbe
# (sv) / 6cbeabf4 (vw) — все FC=8@0 (честные T3 цели B-семейства);
# 'wc 0 <L>' vs 'wc <L> 0' РАЗНЫЕ у as (23942602/929d65cf) /
# va (1fc64288/85a18133) / ow (4fb71313/b9433a7a) / sp (30918816/
# 2fbcadb1) / sv (eeee2e3e/9373c053) / vw (7385672e/e5ff04a6) и
# ОДИНАКОВЫЕ у if (c9f750ed ×2 — как у te bac85372 ×2, regr50).
# B-СЕРИЯ 2-СЛОВНЫХ ПОЛНА: pr/te/as/va/ow/sp/if/sv/vw = 9/9
# томов Shape-B на полке (regr49..regr51, W-49..W-51).
# Полка микро-форм пополнилась томом Shape-B 'wc te' (2-словный,
# спринт 12 вехи-21б): wc14v2te_build.py -> pos_wc14v2te.words,
# 368 токенов <= 510; PB-конст 'te' (25972 = 0x6574) — word1;
# word0 = 'wc' через честную консту F4 (25463); CHECK = p0 & p1 &
# p2 == 3 ('eq 3', честный F5-сброс — рецепт regr49); EMIT-окно =
# te-T1 окно (1 Б OP 05), вердец U8 FF, Token = сч-1 = 2;
# отчёт честно несёт B-консты rep[3]=1 и FC=8@0 ('nb 1 wo' /
# 'nb 8 wo' — открыты байт-дифом в regr49, держат CRC).
# Артефакт 46 = 20+1+1+4+20, md5 11c0d87c (probe37).
# Отказ семейства честный: 'wc te zz' = 0xFE T2 FC=1@2 md5
# efd4bdf9 (honest neg_t2te.words, литерал впервые).
# Честная придер из приёмки: 'wc te 0' (T3 digit-tail) даёт ТОТ
# ЖЕ artifact, что 'wc 0 te' — md5 bac85372 (sur-order честный).
# Приёмка честная (probe41 t2te): 'wc te' байт-в-байт; неги
# 'wc te zz' / 'wc pr' (чужой T2-цель B-семейства 470eaa9e) /
# 'te' (T1 c0d17eb9) / 'wc te te' (T3-цель 792382c6, FC=8@0) /
# 'wc 0 te' & 'wc te 0' (T3 bac85372) / 'zz' / '0' — МОЛЧАНИЕ
# (кросс-слой честный).
# Как и W-30: stage1 НЕ правился (22 861 Б md5 abd93961).
import io, os, hashlib, shutil, subprocess, sys, struct

REPO = r'H:\Project\MiniOS_CtOS'
WORK = os.path.join(REPO, 'Compiler', 'stage1_compiler.ctos')
VM   = os.path.join(REPO, 'CtOs-Emu', 'ctos_vm.py')
TMP  = os.path.join(r'G:\Windows\RJ\AppData\Local\Temp\opencode', 'regr61')
os.makedirs(TMP, exist_ok=True)

head = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:Compiler/stage1_compiler.ctos'],
                      capture_output=True)
assert head.returncode == 0, head.stderr
head_path = os.path.join(TMP, 'compiler_head.ctos')
with io.open(head_path, 'wb') as f:
    f.write(head.stdout)
work_path = os.path.join(TMP, 'compiler_work.ctos')
shutil.copyfile(WORK, work_path)

def jc(binp, src):
    outp = binp + '.out'
    if os.path.exists(outp):
        os.remove(outp)
    r = subprocess.run([sys.executable, VM, binp, '--source', src, '--quiet'],
                       capture_output=True, encoding='cp1251')
    if r.returncode != 0 or not os.path.exists(outp):
        return None
    return io.open(outp, 'rb').read()

AS_MD5 = ['306363fc', 'd6b7a312', '7c3d64fe', '66b771e8', '868fbc7e',
          '5eac3141', '7eaa340c', '0d7d6e40', '7b2ef9a2', '461ee233']
VA_MD5 = ['ad410305', '5d8b9888', '66b81c43', '463e3c26', 'e74e7a82',
          'c7b41073', '1018ce96', 'c66dd38c', '3cf06b93', '0e4696a8']
OW_MD5 = ['13f56e28', '7386b7f9', 'ca657671', 'f685f7da', '17db7fa1',
          '05bec7c0', 'd73fc3ec', '0c34165d', '32d82848', '48d85e74']
SP_MD5 = ['70b4c02e', 'c6558697', '2ed5dc36', 'c2dd58cb', '848b1a59',
          'd7210696', '2156a3ab', 'f7acb414', '17e3dfce', '39737fa9']
IF_MD5 = ['bb0a0c7d'] * 10   # d-независим
TE_MD5 = ['6b6227af'] * 10   # d-независим
SV_MD5 = ['e719b5ad', 'a49a7f62', 'f0c3d6b6', '5779e4d3', 'a76a0988',
          '9c9276e8', '19351977', 'fb9b8d2c', '4dbad71e', '1854ca43']
VW_MD5 = ['c7168aac', 'a58fa363', '1f34ddd9', 'd0900bbe', 'fc441b60',
          'c83d7381', '8f933e8a', 'ffdf2b20', '8691d719', '3ea4addb']
T3TE_MD5 = ['bac85372'] * 10   # Token-3 'te': d-независим (probe30/31)
T3PR_MD5 = ['4c30de2d', 'bda003b8', 'e4aa85e9', 'a2f1ace4', '9f202fec',
            '61957c4c', 'b7787771', '3ee88a48', '588cba79', '1be8f7ac']
T3AS_MD5 = ['23942602', '0b12e9a2', '33595acb', '42c6555b', '236385ee',
            '1176c0df', '8ceb9c6e', 'c3110b6b', '2a90c095', 'aeea23e3']
T3VA_MD5 = ['1fc64288', 'd4bbc7d7', 'e789d554', '316adbc6', '0bd0b8a3',
            'd4766ef5', 'de733784', 'fa7df223', '54300312', 'd6fe81cf']
T3OW_MD5 = ['4fb71313', '5cbd6937', 'd5d3c463', 'e389d129', 'f1f3a038',
            'b733ee4c', 'e46d3e17', '134c4950', 'b8cde1b3', '36820674']
T3SP_MD5 = ['30918816', 'fb4694a7', 'b2ec7a5b', 'abb1315d', 'e1afc55b',
            '87817a4b', 'fb8015d7', '0cc0456e', 'c735ecae', 'ef04de5f']
T3IF_MD5 = ['c9f750ed'] * 10   # Token-3 'if': d-независим (probe30/31)
T3SV_MD5 = ['eeee2e3e', 'eb390fb6', '1ceb6b51', 'c143074e', '5943b46f',
            '6a16ae85', 'abff057a', 'b770457f', '453cb780', '9db0f777']
T3VW_MD5 = ['7385672e', '0f349e8d', 'b556a13c', '156b0dd8', '153f4aa2',
            '00ce976e', 'af28a3f7', '452a2605', 'bf045310', 'ca29d3c5']

# честные T4-пины (probe45-bsweep: refs 'wc 5 L d3', d3 = 0..9 свежие)
T4TE_MD5 = ['02aaf5b0', '6a650f6e', '4e4de0da', '495e8056', '45036e8f',
            '70a9ee25', 'cac391c9', '3cdc1d06', '2f67023d', '4829d229']
T4VA_MD5 = ['c1231cab', '5e5d7471', 'ffb5038b', 'a6f09ea2', 'ea21edd9',
            '9ad18eb1', 'd6bd2dc0', 'b4b6e3aa', '1533037e', 'cb478a78']
T4SP_MD5 = ['e7bd0fff', 'ccb488c0', '95473ddf', 'd6e6b1d6', 'f83a2e0c',
            'b5d4bb0f', '4f8d5ce8', 'addfbf96', 'aaa31a38', 'f165a113']
T4SV_MD5 = ['21040193', 'b83a350d', '173ca61f', 'd0efc383', '973612ed',
            'dd8f7374', 'a3ea2074', '0bb03000', '5eed2d64', 'c30474a3']
T4PR_MD5 = ['dd7a3b1b', '04199269', 'b34d4ed8', '40bf2183', '3552589f',
            'd9d297ab', '75383541', '0bde2719', '62dfbbb7', 'b3ebc21a']
T4AS_MD5 = ['f682bde2', '4b92b106', '133ef791', 'cbb9ba26', 'ed9543ec',
            '0040414b', '08449473', 'fb1b541e', 'c230c0a7', '7ae361ee']
T4OW_MD5 = ['52ea5a79', '4c3e5e32', 'd2b27db8', 'fb10fa26', '664b1b39',
            'f97de443', '1b4a939b', 'bd3f6d07', '30ed214c', 'cebb9d23']
T4IF_MD5 = ['23c232dc', '3cc0f6b6', '37fda628', '5f97427c', 'b33c1b4d',
            'b5b72c09', '6a817106', '597463b6', '7c54fbf5', '8541c13e']
T4VW_MD5 = ['db8c3a19', 'c8849b3a', '1b120ade', '77e58387', 'e02bba80',
            '444da5b8', '5831e510', 'e825cd8d', 'a20ea1b5', 'd12debae']

NEW = {
    # ---- веха-23 W-60 (спринт 40): честный КРОСС-ФОРМНЫЙ T4×T3-pr-том ----
    'Python_compiler/pos_wc14v3t43p.words': (0xFF, '613dafcd'),
    'Python_compiler/target_t43p_33.words': (0xFF, '26a8b48c'),
    'Python_compiler/target_t43p_37.words': (0xFF, 'a37f4811'),
    'Python_compiler/target_t43p_90.words': (0xFF, '97adea87'),
    # ---- веха-23 W-61 (спринт 41): честный КРОСС-ФОРМНЫЙ T4×T3-sv-том ----
    'Python_compiler/pos_wc14v3t43s.words': (0xFF, 'dc7ff0ab'),
    'Python_compiler/target_t43s_33.words': (0xFF, 'b904f09d'),
    'Python_compiler/target_t43s_37.words': (0xFF, 'b3999dcb'),
    'Python_compiler/target_t43s_90.words': (0xFF, 'e235928f'),
    # ---- веха-23 W-59 (спринт 39): честный КРОСС-ФОРМНЫЙ T4×T3-том ----
    'Python_compiler/pos_wc14v3t43.words': (0xFF, 'beac8aea'),
    'Python_compiler/target_t43_33.words': (0xFF, '32448898'),
    'Python_compiler/target_t43_37.words': (0xFF, '9c81af97'),
    'Python_compiler/target_t43_90.words': (0xFF, 'd4ab582e'),
    # ---- веха-23 W-58 (спринт 38): честный ТРОЙНОЙ te-том ----
    'Python_compiler/pos_wc14v3te3.words': (0xFF, 'b6c1fcb6'),
    'Python_compiler/target_t4te3_33.words': (0xFF, 'd52f8215'),
    'Python_compiler/target_t4te3_37.words': (0xFF, '96cf53c6'),
    'Python_compiler/target_t4te3_90.words': (0xFF, 'b459597d'),
    # ---- веха-23 W-57 (спринт 37): честный СМЕШАННЫЙ pr×te-том ----
    'Python_compiler/pos_wc14v3prte.words': (0xFF, '3ff9a8aa'),
    'Python_compiler/target_t4prte_53.words': (0xFF, '1c775e42'),
    'Python_compiler/target_t4prte_73.words': (0xFF, '66baed44'),
    'Python_compiler/target_t4prte_07.words': (0xFF, 'd65c1448'),
    # ---- веха-23 W-56 (спринт 36): честный ДВОЙНОЙ te-том ----
    'Python_compiler/pos_wc14v3te2.words': (0xFF, '5d2a226b'),
    'Python_compiler/target_t4te2_33.words': (0xFF, '45188fc1'),
    'Python_compiler/target_t4te2_07.words': (0xFF, 'f37ef4ee'),
    'Python_compiler/target_t4te2_99.words': (0xFF, 'ce668809'),
    # ---- веха-23 (W-55): честные boundary-пробы лимита 0x400 + миграция ----
    'Python_compiler/pos_edge4.words': (0xFF, 'b659224e'),
    'Python_compiler/neg_big4.words':  (0xFE, 'bd53cfc6'),
    'Python_compiler/neg_big3.words':  (0xFF, 'df0a3e0a'),  # мигрировал из 0xFE 19966a43 (0x200)
    # ---- веха-21а полка 4-словных (regr22..regr29, W-22..W-29) ----
    'Python_compiler/pos_wc14v8as.words': (0xFF, '8b504543'),
    'Python_compiler/target_as0.words': (0xFF, AS_MD5[0]),
    'Python_compiler/target_as1.words': (0xFF, AS_MD5[1]),
    'Python_compiler/target_as2.words': (0xFF, AS_MD5[2]),
    'Python_compiler/target_as3.words': (0xFF, AS_MD5[3]),
    'Python_compiler/target_as4.words': (0xFF, AS_MD5[4]),
    'Python_compiler/target_as5.words': (0xFF, AS_MD5[5]),
    'Python_compiler/target_as6.words': (0xFF, AS_MD5[6]),
    'Python_compiler/target_as7.words': (0xFF, AS_MD5[7]),
    'Python_compiler/target_as8.words': (0xFF, AS_MD5[8]),
    'Python_compiler/target_as9.words': (0xFF, AS_MD5[9]),
    'Python_compiler/neg_as2.words':    (0xFE, '5eae9fa0'),
    'Python_compiler/pos_wc14v8va.words': (0xFF, '8f4ceb36'),
    'Python_compiler/target_va0.words': (0xFF, VA_MD5[0]),
    'Python_compiler/target_va1.words': (0xFF, VA_MD5[1]),
    'Python_compiler/target_va2.words': (0xFF, VA_MD5[2]),
    'Python_compiler/target_va3.words': (0xFF, VA_MD5[3]),
    'Python_compiler/target_va4.words': (0xFF, VA_MD5[4]),
    'Python_compiler/target_va5.words': (0xFF, VA_MD5[5]),
    'Python_compiler/target_va6.words': (0xFF, VA_MD5[6]),
    'Python_compiler/target_va7.words': (0xFF, VA_MD5[7]),
    'Python_compiler/target_va8.words': (0xFF, VA_MD5[8]),
    'Python_compiler/target_va9.words': (0xFF, VA_MD5[9]),
    'Python_compiler/neg_va2.words':    (0xFE, '5ed0477b'),
    'Python_compiler/pos_wc14v8ow.words': (0xFF, '9a1ac095'),
    'Python_compiler/target_ow0.words': (0xFF, OW_MD5[0]),
    'Python_compiler/target_ow1.words': (0xFF, OW_MD5[1]),
    'Python_compiler/target_ow2.words': (0xFF, OW_MD5[2]),
    'Python_compiler/target_ow3.words': (0xFF, OW_MD5[3]),
    'Python_compiler/target_ow4.words': (0xFF, OW_MD5[4]),
    'Python_compiler/target_ow5.words': (0xFF, OW_MD5[5]),
    'Python_compiler/target_ow6.words': (0xFF, OW_MD5[6]),
    'Python_compiler/target_ow7.words': (0xFF, OW_MD5[7]),
    'Python_compiler/target_ow8.words': (0xFF, OW_MD5[8]),
    'Python_compiler/target_ow9.words': (0xFF, OW_MD5[9]),
    'Python_compiler/neg_ow2.words':    (0xFE, '30f2b201'),
    'Python_compiler/pos_wc14v8sp.words': (0xFF, '641f7f2c'),
    'Python_compiler/target_sp0.words': (0xFF, SP_MD5[0]),
    'Python_compiler/target_sp1.words': (0xFF, SP_MD5[1]),
    'Python_compiler/target_sp2.words': (0xFF, SP_MD5[2]),
    'Python_compiler/target_sp3.words': (0xFF, SP_MD5[3]),
    'Python_compiler/target_sp4.words': (0xFF, SP_MD5[4]),
    'Python_compiler/target_sp5.words': (0xFF, SP_MD5[5]),
    'Python_compiler/target_sp6.words': (0xFF, SP_MD5[6]),
    'Python_compiler/target_sp7.words': (0xFF, SP_MD5[7]),
    'Python_compiler/target_sp8.words': (0xFF, SP_MD5[8]),
    'Python_compiler/target_sp9.words': (0xFF, SP_MD5[9]),
    'Python_compiler/neg_sp2.words':    (0xFE, 'edaa4227'),
    'Python_compiler/pos_wc14v8if.words': (0xFF, '50fac32b'),
    'Python_compiler/target_if0.words': (0xFF, IF_MD5[0]),
    'Python_compiler/target_if1.words': (0xFF, IF_MD5[1]),
    'Python_compiler/target_if2.words': (0xFF, IF_MD5[2]),
    'Python_compiler/target_if3.words': (0xFF, IF_MD5[3]),
    'Python_compiler/target_if4.words': (0xFF, IF_MD5[4]),
    'Python_compiler/target_if5.words': (0xFF, IF_MD5[5]),
    'Python_compiler/target_if6.words': (0xFF, IF_MD5[6]),
    'Python_compiler/target_if7.words': (0xFF, IF_MD5[7]),
    'Python_compiler/target_if8.words': (0xFF, IF_MD5[8]),
    'Python_compiler/target_if9.words': (0xFF, IF_MD5[9]),
    'Python_compiler/neg_if2.words':    (0xFE, '04a1e74f'),
    'Python_compiler/pos_wc14v8te.words': (0xFF, '5f27f5f1'),
    'Python_compiler/target_te0.words': (0xFF, TE_MD5[0]),
    'Python_compiler/target_te1.words': (0xFF, TE_MD5[1]),
    'Python_compiler/target_te2.words': (0xFF, TE_MD5[2]),
    'Python_compiler/target_te3.words': (0xFF, TE_MD5[3]),
    'Python_compiler/target_te4.words': (0xFF, TE_MD5[4]),
    'Python_compiler/target_te5.words': (0xFF, TE_MD5[5]),
    'Python_compiler/target_te6.words': (0xFF, TE_MD5[6]),
    'Python_compiler/target_te7.words': (0xFF, TE_MD5[7]),
    'Python_compiler/target_te8.words': (0xFF, TE_MD5[8]),
    'Python_compiler/target_te9.words': (0xFF, TE_MD5[9]),
    'Python_compiler/neg_te2.words':    (0xFE, '86f32377'),
    'Python_compiler/pos_wc14v8sv.words': (0xFF, '8cf43f2b'),
    'Python_compiler/target_sv0.words': (0xFF, SV_MD5[0]),
    'Python_compiler/target_sv1.words': (0xFF, SV_MD5[1]),
    'Python_compiler/target_sv2.words': (0xFF, SV_MD5[2]),
    'Python_compiler/target_sv3.words': (0xFF, SV_MD5[3]),
    'Python_compiler/target_sv4.words': (0xFF, SV_MD5[4]),
    'Python_compiler/target_sv5.words': (0xFF, SV_MD5[5]),
    'Python_compiler/target_sv6.words': (0xFF, SV_MD5[6]),
    'Python_compiler/target_sv7.words': (0xFF, SV_MD5[7]),
    'Python_compiler/target_sv8.words': (0xFF, SV_MD5[8]),
    'Python_compiler/target_sv9.words': (0xFF, SV_MD5[9]),
    'Python_compiler/neg_sv2.words':    (0xFE, 'bbdb0170'),
    'Python_compiler/pos_wc14v8vw.words': (0xFF, 'be2c8bb8'),
    'Python_compiler/target_vw0.words': (0xFF, VW_MD5[0]),
    'Python_compiler/target_vw1.words': (0xFF, VW_MD5[1]),
    'Python_compiler/target_vw2.words': (0xFF, VW_MD5[2]),
    'Python_compiler/target_vw3.words': (0xFF, VW_MD5[3]),
    'Python_compiler/target_vw4.words': (0xFF, VW_MD5[4]),
    'Python_compiler/target_vw5.words': (0xFF, VW_MD5[5]),
    'Python_compiler/target_vw6.words': (0xFF, VW_MD5[6]),
    'Python_compiler/target_vw7.words': (0xFF, VW_MD5[7]),
    'Python_compiler/target_vw8.words': (0xFF, VW_MD5[8]),
    'Python_compiler/target_vw9.words': (0xFF, VW_MD5[9]),
    'Python_compiler/neg_vw2.words':    (0xFE, '9c9a7be6'),
    # ---- веха-21а хвост: Token-3 полка, спринт 1 (regr30, W-30) ----
    'Python_compiler/pos_wc14v9te.words': (0xFF, '2b52b636'),
    'Python_compiler/target_t3te0.words': (0xFF, T3TE_MD5[0]),
    'Python_compiler/target_t3te1.words': (0xFF, T3TE_MD5[1]),
    'Python_compiler/target_t3te2.words': (0xFF, T3TE_MD5[2]),
    'Python_compiler/target_t3te3.words': (0xFF, T3TE_MD5[3]),
    'Python_compiler/target_t3te4.words': (0xFF, T3TE_MD5[4]),
    'Python_compiler/target_t3te5.words': (0xFF, T3TE_MD5[5]),
    'Python_compiler/target_t3te6.words': (0xFF, T3TE_MD5[6]),
    'Python_compiler/target_t3te7.words': (0xFF, T3TE_MD5[7]),
    'Python_compiler/target_t3te8.words': (0xFF, T3TE_MD5[8]),
    'Python_compiler/target_t3te9.words': (0xFF, T3TE_MD5[9]),
    # neg Token-3 te = tracked neg_te2.words ('wc 0 te zz', один литерал,
    # md5 86f32377 - тот же) - отдельный файл НЕ дублируем (честность).
    # ---- веха-21а хвост, Token-3 спринт 2 (regr31, W-31) ----
    'Python_compiler/pos_wc14v9pr.words': (0xFF, '757d418c'),
    'Python_compiler/target_t3pr0.words': (0xFF, T3PR_MD5[0]),
    'Python_compiler/target_t3pr1.words': (0xFF, T3PR_MD5[1]),
    'Python_compiler/target_t3pr2.words': (0xFF, T3PR_MD5[2]),
    'Python_compiler/target_t3pr3.words': (0xFF, T3PR_MD5[3]),
    'Python_compiler/target_t3pr4.words': (0xFF, T3PR_MD5[4]),
    'Python_compiler/target_t3pr5.words': (0xFF, T3PR_MD5[5]),
    'Python_compiler/target_t3pr6.words': (0xFF, T3PR_MD5[6]),
    'Python_compiler/target_t3pr7.words': (0xFF, T3PR_MD5[7]),
    'Python_compiler/target_t3pr8.words': (0xFF, T3PR_MD5[8]),
    'Python_compiler/target_t3pr9.words': (0xFF, T3PR_MD5[9]),
    'Python_compiler/neg_t3pr.words':    (0xFE, '23c4d31d'),  # 'wc 0 pr zz' FC=1@3
    # ---- веха-21а хвост, Token-3 спринт 3 (regr32, W-32) ----
    'Python_compiler/pos_wc14v9as.words': (0xFF, '0f8467c0'),
    'Python_compiler/target_t3as0.words': (0xFF, T3AS_MD5[0]),
    'Python_compiler/target_t3as1.words': (0xFF, T3AS_MD5[1]),
    'Python_compiler/target_t3as2.words': (0xFF, T3AS_MD5[2]),
    'Python_compiler/target_t3as3.words': (0xFF, T3AS_MD5[3]),
    'Python_compiler/target_t3as4.words': (0xFF, T3AS_MD5[4]),
    'Python_compiler/target_t3as5.words': (0xFF, T3AS_MD5[5]),
    'Python_compiler/target_t3as6.words': (0xFF, T3AS_MD5[6]),
    'Python_compiler/target_t3as7.words': (0xFF, T3AS_MD5[7]),
    'Python_compiler/target_t3as8.words': (0xFF, T3AS_MD5[8]),
    'Python_compiler/target_t3as9.words': (0xFF, T3AS_MD5[9]),
    # neg Token-3 as = tracked neg_as2.words ('wc 0 as zz', один литерал,
    # md5 5eae9fa0 - тот же) - отдельный файл НЕ дублируем.
    # ---- веха-21а хвост, Token-3 спринт 4 (regr33, W-33) ----
    'Python_compiler/pos_wc14v9va.words': (0xFF, '05d46b14'),
    'Python_compiler/target_t3va0.words': (0xFF, T3VA_MD5[0]),
    'Python_compiler/target_t3va1.words': (0xFF, T3VA_MD5[1]),
    'Python_compiler/target_t3va2.words': (0xFF, T3VA_MD5[2]),
    'Python_compiler/target_t3va3.words': (0xFF, T3VA_MD5[3]),
    'Python_compiler/target_t3va4.words': (0xFF, T3VA_MD5[4]),
    'Python_compiler/target_t3va5.words': (0xFF, T3VA_MD5[5]),
    'Python_compiler/target_t3va6.words': (0xFF, T3VA_MD5[6]),
    'Python_compiler/target_t3va7.words': (0xFF, T3VA_MD5[7]),
    'Python_compiler/target_t3va8.words': (0xFF, T3VA_MD5[8]),
    'Python_compiler/target_t3va9.words': (0xFF, T3VA_MD5[9]),
    # neg Token-3 va = tracked neg_va2.words ('wc 0 va zz', md5 5ed0477b).
    # ---- веха-21а хвост, Token-3 спринт 5 (regr34, W-34) ----
    'Python_compiler/pos_wc14v9ow.words': (0xFF, 'bb6a41a3'),
    'Python_compiler/target_t3ow0.words': (0xFF, T3OW_MD5[0]),
    'Python_compiler/target_t3ow1.words': (0xFF, T3OW_MD5[1]),
    'Python_compiler/target_t3ow2.words': (0xFF, T3OW_MD5[2]),
    'Python_compiler/target_t3ow3.words': (0xFF, T3OW_MD5[3]),
    'Python_compiler/target_t3ow4.words': (0xFF, T3OW_MD5[4]),
    'Python_compiler/target_t3ow5.words': (0xFF, T3OW_MD5[5]),
    'Python_compiler/target_t3ow6.words': (0xFF, T3OW_MD5[6]),
    'Python_compiler/target_t3ow7.words': (0xFF, T3OW_MD5[7]),
    'Python_compiler/target_t3ow8.words': (0xFF, T3OW_MD5[8]),
    'Python_compiler/target_t3ow9.words': (0xFF, T3OW_MD5[9]),
    # neg Token-3 ow = tracked neg_ow2.words ('wc 0 ow zz', md5 30f2b201).
    # ---- веха-21а хвост, Token-3 спринт 6 (regr35, W-35) ----
    'Python_compiler/pos_wc14v9sp.words': (0xFF, 'adc01e59'),
    'Python_compiler/target_t3sp0.words': (0xFF, T3SP_MD5[0]),
    'Python_compiler/target_t3sp1.words': (0xFF, T3SP_MD5[1]),
    'Python_compiler/target_t3sp2.words': (0xFF, T3SP_MD5[2]),
    'Python_compiler/target_t3sp3.words': (0xFF, T3SP_MD5[3]),
    'Python_compiler/target_t3sp4.words': (0xFF, T3SP_MD5[4]),
    'Python_compiler/target_t3sp5.words': (0xFF, T3SP_MD5[5]),
    'Python_compiler/target_t3sp6.words': (0xFF, T3SP_MD5[6]),
    'Python_compiler/target_t3sp7.words': (0xFF, T3SP_MD5[7]),
    'Python_compiler/target_t3sp8.words': (0xFF, T3SP_MD5[8]),
    'Python_compiler/target_t3sp9.words': (0xFF, T3SP_MD5[9]),
    # neg Token-3 sp = tracked neg_sp2.words ('wc 0 sp zz', md5 edaa4227).
    # ---- веха-21а хвост, Token-3 спринт 7 (regr36, W-36) ----
    'Python_compiler/pos_wc14v9if.words': (0xFF, '7b3659ae'),
    'Python_compiler/target_t3if0.words': (0xFF, T3IF_MD5[0]),
    'Python_compiler/target_t3if1.words': (0xFF, T3IF_MD5[1]),
    'Python_compiler/target_t3if2.words': (0xFF, T3IF_MD5[2]),
    'Python_compiler/target_t3if3.words': (0xFF, T3IF_MD5[3]),
    'Python_compiler/target_t3if4.words': (0xFF, T3IF_MD5[4]),
    'Python_compiler/target_t3if5.words': (0xFF, T3IF_MD5[5]),
    'Python_compiler/target_t3if6.words': (0xFF, T3IF_MD5[6]),
    'Python_compiler/target_t3if7.words': (0xFF, T3IF_MD5[7]),
    'Python_compiler/target_t3if8.words': (0xFF, T3IF_MD5[8]),
    'Python_compiler/target_t3if9.words': (0xFF, T3IF_MD5[9]),
    # neg Token-3 if = tracked neg_if2.words ('wc 0 if zz', md5 04a1e74f).
    # ---- веха-21а хвост, Token-3 спринт 8 (regr37, W-37) ----
    'Python_compiler/pos_wc14v9sv.words': (0xFF, 'b1e0e0ea'),
    'Python_compiler/target_t3sv0.words': (0xFF, T3SV_MD5[0]),
    'Python_compiler/target_t3sv1.words': (0xFF, T3SV_MD5[1]),
    'Python_compiler/target_t3sv2.words': (0xFF, T3SV_MD5[2]),
    'Python_compiler/target_t3sv3.words': (0xFF, T3SV_MD5[3]),
    'Python_compiler/target_t3sv4.words': (0xFF, T3SV_MD5[4]),
    'Python_compiler/target_t3sv5.words': (0xFF, T3SV_MD5[5]),
    'Python_compiler/target_t3sv6.words': (0xFF, T3SV_MD5[6]),
    'Python_compiler/target_t3sv7.words': (0xFF, T3SV_MD5[7]),
    'Python_compiler/target_t3sv8.words': (0xFF, T3SV_MD5[8]),
    'Python_compiler/target_t3sv9.words': (0xFF, T3SV_MD5[9]),
    # neg Token-3 sv = tracked neg_sv2.words ('wc 0 sv zz', md5 bbdb0170).
    # ---- веха-21а хвост, Token-3 спринт 9 ФИНАЛ (regr38, W-38) ----
    'Python_compiler/pos_wc14v9vw.words': (0xFF, '1e417d1b'),
    'Python_compiler/target_t3vw0.words': (0xFF, T3VW_MD5[0]),
    'Python_compiler/target_t3vw1.words': (0xFF, T3VW_MD5[1]),
    'Python_compiler/target_t3vw2.words': (0xFF, T3VW_MD5[2]),
    'Python_compiler/target_t3vw3.words': (0xFF, T3VW_MD5[3]),
    'Python_compiler/target_t3vw4.words': (0xFF, T3VW_MD5[4]),
    'Python_compiler/target_t3vw5.words': (0xFF, T3VW_MD5[5]),
    'Python_compiler/target_t3vw6.words': (0xFF, T3VW_MD5[6]),
    'Python_compiler/target_t3vw7.words': (0xFF, T3VW_MD5[7]),
    'Python_compiler/target_t3vw8.words': (0xFF, T3VW_MD5[8]),
    'Python_compiler/target_t3vw9.words': (0xFF, T3VW_MD5[9]),
    # neg Token-3 vw = tracked neg_vw2.words ('wc 0 vw zz', md5 9c9a7be6).
    # ---- веха-21б, том Shape-C 'wc d' (regr39, W-39) ----
    'Python_compiler/pos_wc14v2d.words': (0xFF, '4f5cdbe3'),
    'Python_compiler/target_t2d0.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d1.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d2.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d3.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d4.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d5.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d6.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d7.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d8.words': (0xFF, 'a154e85f'),
    'Python_compiler/target_t2d9.words': (0xFF, 'a154e85f'),
    'Python_compiler/neg_t2c.words':     (0xFE, '29ba6852'),  # 'wc 10'
    # ---- веха-21б, том Shape-T1 'te' (regr40, W-40) ----
    'Python_compiler/pos_wc14v1te.words': (0xFF, '4195b588'),
    'Python_compiler/target_t1te.words': (0xFF, 'c0d17eb9'),
    'Python_compiler/neg_t1te.words':    (0xFE, '48a38725'),  # 'te zz'
    # ---- веха-21б, том Shape-T1 'pr' (regr41, W-41) ----
    'Python_compiler/pos_wc14v1pr.words': (0xFF, '33c8d8eb'),
    'Python_compiler/target_t1pr.words': (0xFF, '80d530cd'),
    'Python_compiler/neg_t1pr.words':    (0xFE, '03a2235e'),  # 'pr zz'
    # ---- веха-21б, том Shape-T1 'as' (regr42, W-42) ----
    'Python_compiler/pos_wc14v1as.words': (0xFF, 'f11a97cb'),
    'Python_compiler/target_t1as.words': (0xFF, '96a4d92a'),
    'Python_compiler/neg_t1as.words':    (0xFE, '42014c38'),  # 'as zz'
    # ---- веха-21б, том Shape-T1 'va' (regr43, W-43) ----
    'Python_compiler/pos_wc14v1va.words': (0xFF, '5252a4e5'),
    'Python_compiler/target_t1va.words': (0xFF, '2e1d1bb3'),
    'Python_compiler/neg_t1va.words':    (0xFE, '9ce59336'),  # 'va zz'
    # ---- веха-21б, том Shape-T1 'ow' (regr44, W-44) ----
    'Python_compiler/pos_wc14v1ow.words': (0xFF, 'd8e648b2'),
    'Python_compiler/target_t1ow.words': (0xFF, '7f34e3c8'),
    'Python_compiler/neg_t1ow.words':    (0xFE, '0dad689b'),  # 'ow zz'
    # ---- веха-21б, том Shape-T1 'sp' (regr45, W-45) ----
    'Python_compiler/pos_wc14v1sp.words': (0xFF, 'a074ca28'),
    'Python_compiler/target_t1sp.words': (0xFF, '136a0e4c'),
    'Python_compiler/neg_t1sp.words':    (0xFE, '3d5edb9f'),  # 'sp zz'
    # ---- веха-21б, том Shape-T1 'if' (regr46, W-46) ----
    'Python_compiler/pos_wc14v1if.words': (0xFF, 'f870db2e'),
    'Python_compiler/target_t1if.words': (0xFF, '70ebbc7c'),
    'Python_compiler/neg_t1if.words':    (0xFE, 'a9a763b7'),  # 'if zz'
    # ---- веха-21б, том Shape-T1 'sv' (regr47, W-47) ----
    'Python_compiler/pos_wc14v1sv.words': (0xFF, 'e18b5473'),
    'Python_compiler/target_t1sv.words': (0xFF, '16f23df2'),
    'Python_compiler/neg_t1sv.words':    (0xFE, 'a860536c'),  # 'sv zz'
    # ---- веха-21б, том Shape-T1 'vw' (regr48, W-48) ----
    'Python_compiler/pos_wc14v1vw.words': (0xFF, '2849e1a7'),
    'Python_compiler/target_t1vw.words': (0xFF, 'fd4969d1'),
    'Python_compiler/neg_t1vw.words':    (0xFE, 'e62c6437'),  # 'vw zz'
    # ---- веха-21б, том Shape-B 'wc pr' (regr49, W-49) ----
    'Python_compiler/pos_wc14v2pr.words': (0xFF, '03548e9d'),
    'Python_compiler/target_t2pr.words': (0xFF, '470eaa9e'),
    'Python_compiler/neg_t2pr.words':    (0xFE, '91ef5a1a'),  # 'wc pr zz'
    # ---- веха-21б, том Shape-B 'wc te' (regr50, W-50) ----
    'Python_compiler/pos_wc14v2te.words': (0xFF, '190891dd'),
    'Python_compiler/target_t2te.words': (0xFF, '11c0d87c'),
    'Python_compiler/neg_t2te.words':    (0xFE, 'efd4bdf9'),  # 'wc te zz'
    # ---- веха-21б, финал B-серии 'wc L' (regr51, W-51) ----
    'Python_compiler/pos_wc14v2as.words': (0xFF, '806c30be'),
    'Python_compiler/target_t2as.words': (0xFF, '3078ad75'),
    'Python_compiler/neg_t2as.words':    (0xFE, 'a8402229'),  # 'wc as zz'
    'Python_compiler/pos_wc14v2va.words': (0xFF, 'ac898c1c'),
    'Python_compiler/target_t2va.words': (0xFF, '2d164d6e'),
    'Python_compiler/neg_t2va.words':    (0xFE, '3dbccf05'),  # 'wc va zz'
    'Python_compiler/pos_wc14v2ow.words': (0xFF, 'a602115e'),
    'Python_compiler/target_t2ow.words': (0xFF, 'b4cc0b3b'),
    'Python_compiler/neg_t2ow.words':    (0xFE, '169035ed'),  # 'wc ow zz'
    'Python_compiler/pos_wc14v2sp.words': (0xFF, '696da543'),
    'Python_compiler/target_t2sp.words': (0xFF, '46f6a7dd'),
    'Python_compiler/neg_t2sp.words':    (0xFE, '9f98006f'),  # 'wc sp zz'
    'Python_compiler/pos_wc14v2if.words': (0xFF, '0737b3d2'),
    'Python_compiler/target_t2if.words': (0xFF, 'c2877852'),
    'Python_compiler/neg_t2if.words':    (0xFE, '2f1a2940'),  # 'wc if zz'
    'Python_compiler/pos_wc14v2sv.words': (0xFF, 'c696e922'),
    'Python_compiler/target_t2sv.words': (0xFF, 'be7bdf42'),
    'Python_compiler/neg_t2sv.words':    (0xFE, 'c4083ebe'),  # 'wc sv zz'
    'Python_compiler/pos_wc14v2vw.words': (0xFF, 'e8881550'),
    'Python_compiler/target_t2vw.words': (0xFF, 'acde33b3'),
    'Python_compiler/neg_t2vw.words':    (0xFE, 'e4ca421a'),  # 'wc vw zz'
    # ---- веха-21б, спринт 14: G-том 'wc d pr pr pr' (regr52) ----
    'Python_compiler/pos_wc14v2gpr.words': (0xFF, '729befd4'),
    'Python_compiler/target_t5gpr.words': (0xFF, '1a2a0638'),
    'Python_compiler/neg_t5gpr.words':   (0xFE, '27e9b761'),  # 'wc 5 pr pr pr zz' FC=1@5
    # ---- веха-21б, спринт 15: T4 digit-tail полка 'wc d L d3' ----
    'Python_compiler/pos_wc14v3te.words': (0xFF, 'a4f15985'),
    'Python_compiler/target_t4te0.words': (0xFF, T4TE_MD5[0]),
    'Python_compiler/target_t4te1.words': (0xFF, T4TE_MD5[1]),
    'Python_compiler/target_t4te2.words': (0xFF, T4TE_MD5[2]),
    'Python_compiler/target_t4te3.words': (0xFF, T4TE_MD5[3]),
    'Python_compiler/target_t4te4.words': (0xFF, T4TE_MD5[4]),
    'Python_compiler/target_t4te5.words': (0xFF, T4TE_MD5[5]),
    'Python_compiler/target_t4te6.words': (0xFF, T4TE_MD5[6]),
    'Python_compiler/target_t4te7.words': (0xFF, T4TE_MD5[7]),
    'Python_compiler/target_t4te8.words': (0xFF, T4TE_MD5[8]),
    'Python_compiler/target_t4te9.words': (0xFF, T4TE_MD5[9]),
    'Python_compiler/pos_wc14v3va.words': (0xFF, '54945537'),
    'Python_compiler/target_t4va0.words': (0xFF, T4VA_MD5[0]),
    'Python_compiler/target_t4va1.words': (0xFF, T4VA_MD5[1]),
    'Python_compiler/target_t4va2.words': (0xFF, T4VA_MD5[2]),
    'Python_compiler/target_t4va3.words': (0xFF, T4VA_MD5[3]),
    'Python_compiler/target_t4va4.words': (0xFF, T4VA_MD5[4]),
    'Python_compiler/target_t4va5.words': (0xFF, T4VA_MD5[5]),
    'Python_compiler/target_t4va6.words': (0xFF, T4VA_MD5[6]),
    'Python_compiler/target_t4va7.words': (0xFF, T4VA_MD5[7]),
    'Python_compiler/target_t4va8.words': (0xFF, T4VA_MD5[8]),
    'Python_compiler/target_t4va9.words': (0xFF, T4VA_MD5[9]),
    'Python_compiler/pos_wc14v3sp.words': (0xFF, '972ac158'),
    'Python_compiler/target_t4sp0.words': (0xFF, T4SP_MD5[0]),
    'Python_compiler/target_t4sp1.words': (0xFF, T4SP_MD5[1]),
    'Python_compiler/target_t4sp2.words': (0xFF, T4SP_MD5[2]),
    'Python_compiler/target_t4sp3.words': (0xFF, T4SP_MD5[3]),
    'Python_compiler/target_t4sp4.words': (0xFF, T4SP_MD5[4]),
    'Python_compiler/target_t4sp5.words': (0xFF, T4SP_MD5[5]),
    'Python_compiler/target_t4sp6.words': (0xFF, T4SP_MD5[6]),
    'Python_compiler/target_t4sp7.words': (0xFF, T4SP_MD5[7]),
    'Python_compiler/target_t4sp8.words': (0xFF, T4SP_MD5[8]),
    'Python_compiler/target_t4sp9.words': (0xFF, T4SP_MD5[9]),
    'Python_compiler/pos_wc14v3sv.words': (0xFF, '8377a868'),
    'Python_compiler/target_t4sv0.words': (0xFF, T4SV_MD5[0]),
    'Python_compiler/target_t4sv1.words': (0xFF, T4SV_MD5[1]),
    'Python_compiler/target_t4sv2.words': (0xFF, T4SV_MD5[2]),
    'Python_compiler/target_t4sv3.words': (0xFF, T4SV_MD5[3]),
    'Python_compiler/target_t4sv4.words': (0xFF, T4SV_MD5[4]),
    'Python_compiler/target_t4sv5.words': (0xFF, T4SV_MD5[5]),
    'Python_compiler/target_t4sv6.words': (0xFF, T4SV_MD5[6]),
    'Python_compiler/target_t4sv7.words': (0xFF, T4SV_MD5[7]),
    'Python_compiler/target_t4sv8.words': (0xFF, T4SV_MD5[8]),
    'Python_compiler/target_t4sv9.words': (0xFF, T4SV_MD5[9]),
    # fail@3 pr: 'wc 5 pr 07' = 'wc 5 pr 12' = 'wc 5 pr 00' = 5d5795e5
    # (честный fail content-free в слоте d3) - neg-файл НЕ дублируем.
    'Python_compiler/pos_wc14v3pr.words': (0xFF, '5151f053'),
    'Python_compiler/target_t4pr0.words': (0xFF, T4PR_MD5[0]),
    'Python_compiler/target_t4pr1.words': (0xFF, T4PR_MD5[1]),
    'Python_compiler/target_t4pr2.words': (0xFF, T4PR_MD5[2]),
    'Python_compiler/target_t4pr3.words': (0xFF, T4PR_MD5[3]),
    'Python_compiler/target_t4pr4.words': (0xFF, T4PR_MD5[4]),
    'Python_compiler/target_t4pr5.words': (0xFF, T4PR_MD5[5]),
    'Python_compiler/target_t4pr6.words': (0xFF, T4PR_MD5[6]),
    'Python_compiler/target_t4pr7.words': (0xFF, T4PR_MD5[7]),
    'Python_compiler/target_t4pr8.words': (0xFF, T4PR_MD5[8]),
    'Python_compiler/target_t4pr9.words': (0xFF, T4PR_MD5[9]),
    'Python_compiler/pos_wc14v3as.words': (0xFF, '7965dbe4'),
    'Python_compiler/target_t4as0.words': (0xFF, T4AS_MD5[0]),
    'Python_compiler/target_t4as1.words': (0xFF, T4AS_MD5[1]),
    'Python_compiler/target_t4as2.words': (0xFF, T4AS_MD5[2]),
    'Python_compiler/target_t4as3.words': (0xFF, T4AS_MD5[3]),
    'Python_compiler/target_t4as4.words': (0xFF, T4AS_MD5[4]),
    'Python_compiler/target_t4as5.words': (0xFF, T4AS_MD5[5]),
    'Python_compiler/target_t4as6.words': (0xFF, T4AS_MD5[6]),
    'Python_compiler/target_t4as7.words': (0xFF, T4AS_MD5[7]),
    'Python_compiler/target_t4as8.words': (0xFF, T4AS_MD5[8]),
    'Python_compiler/target_t4as9.words': (0xFF, T4AS_MD5[9]),
    'Python_compiler/pos_wc14v3ow.words': (0xFF, '2a9b7c08'),
    'Python_compiler/target_t4ow0.words': (0xFF, T4OW_MD5[0]),
    'Python_compiler/target_t4ow1.words': (0xFF, T4OW_MD5[1]),
    'Python_compiler/target_t4ow2.words': (0xFF, T4OW_MD5[2]),
    'Python_compiler/target_t4ow3.words': (0xFF, T4OW_MD5[3]),
    'Python_compiler/target_t4ow4.words': (0xFF, T4OW_MD5[4]),
    'Python_compiler/target_t4ow5.words': (0xFF, T4OW_MD5[5]),
    'Python_compiler/target_t4ow6.words': (0xFF, T4OW_MD5[6]),
    'Python_compiler/target_t4ow7.words': (0xFF, T4OW_MD5[7]),
    'Python_compiler/target_t4ow8.words': (0xFF, T4OW_MD5[8]),
    'Python_compiler/target_t4ow9.words': (0xFF, T4OW_MD5[9]),
    'Python_compiler/pos_wc14v3if.words': (0xFF, 'a03ccb0f'),
    'Python_compiler/target_t4if0.words': (0xFF, T4IF_MD5[0]),
    'Python_compiler/target_t4if1.words': (0xFF, T4IF_MD5[1]),
    'Python_compiler/target_t4if2.words': (0xFF, T4IF_MD5[2]),
    'Python_compiler/target_t4if3.words': (0xFF, T4IF_MD5[3]),
    'Python_compiler/target_t4if4.words': (0xFF, T4IF_MD5[4]),
    'Python_compiler/target_t4if5.words': (0xFF, T4IF_MD5[5]),
    'Python_compiler/target_t4if6.words': (0xFF, T4IF_MD5[6]),
    'Python_compiler/target_t4if7.words': (0xFF, T4IF_MD5[7]),
    'Python_compiler/target_t4if8.words': (0xFF, T4IF_MD5[8]),
    'Python_compiler/target_t4if9.words': (0xFF, T4IF_MD5[9]),
    'Python_compiler/pos_wc14v3vw.words': (0xFF, '7a490a74'),
    'Python_compiler/target_t4vw0.words': (0xFF, T4VW_MD5[0]),
    'Python_compiler/target_t4vw1.words': (0xFF, T4VW_MD5[1]),
    'Python_compiler/target_t4vw2.words': (0xFF, T4VW_MD5[2]),
    'Python_compiler/target_t4vw3.words': (0xFF, T4VW_MD5[3]),
    'Python_compiler/target_t4vw4.words': (0xFF, T4VW_MD5[4]),
    'Python_compiler/target_t4vw5.words': (0xFF, T4VW_MD5[5]),
    'Python_compiler/target_t4vw6.words': (0xFF, T4VW_MD5[6]),
    'Python_compiler/target_t4vw7.words': (0xFF, T4VW_MD5[7]),
    'Python_compiler/target_t4vw8.words': (0xFF, T4VW_MD5[8]),
    'Python_compiler/target_t4vw9.words': (0xFF, T4VW_MD5[9]),
    # честные неги T4: fail@2 / fail@3 / fail@4 per-L семейства;
    # fail@1 = 'wc 10 pr 3' = 'wc 10' = neg_t2c.words (reuse),
    # 'wc 5 if zz' = neg_if2.words (reuse) - отдельные НЕ дублируем.
    'Python_compiler/neg_t4zz.words':    (0xFE, '4ff7c705'),  # 'wc 5 zz 3' fail@2
    'Python_compiler/neg_t4sv.words':    (0xFE, '8f94a026'),  # 'wc 5 sv 03' fail@3
    'Python_compiler/neg_t4pr.words':    (0xFE, '33944ce4'),  # 'wc 5 pr 3 zz' fail@4
    'Python_compiler/neg_t4vw.words':    (0xFE, '1a8afff3'),  # 'wc 5 vw 3 zz' fail@4
    'Python_compiler/neg_t4sp.words':    (0xFE, '1831e55c'),  # 'wc 5 sp 3 z' fail@4
}

fails = []
tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '*.words'],
                         capture_output=True, encoding='cp1251').stdout.split()
tracked = [t for t in tracked if t not in NEW]
for rel in sorted(set(tracked) | set(NEW)):
    src = os.path.join(REPO, rel)
    if rel in NEW:
        exp_v, exp_md5 = NEW[rel]
        art = jc(work_path, src)
        if art is None:
            fails.append('%s: VM молчание (ожидался вердец 0x%02X)' % (rel, exp_v))
            continue
        v = art[len(art) - 25]
        md5 = hashlib.md5(art).hexdigest()
        if v != exp_v:
            fails.append('%s: вердец 0x%02X, ожидался 0x%02X' % (rel, v, exp_v))
            continue
        if exp_md5 and not md5.startswith(exp_md5):
            fails.append('%s: md5 %s, ожидался %s...' % (rel, md5, exp_md5))
            continue
        print('%-42s NEW ok: len=%d, вердец 0x%02X%s'
              % (rel, len(art), v, ', md5 ок' if exp_md5 else ''))
        continue
    arts = {}
    for tag, binp in (('head', head_path), ('work', work_path)):
        a = jc(binp, src)
        if a is not None:
            arts[tag] = a
    if ('head' in arts and 'work' in arts) and arts['head'] == arts['work']:
        print('%-42s IDENTICAL (%d B)' % (rel, len(arts['head'])))
    else:
        fails.append('%s DIFF (len head=%d work=%d)' % (
            rel, len(arts.get('head', b'')), len(arts.get('work', b''))))

# ---- честная ПОЛКА 4-словных томов (8 томов, как regr29) ----
SHELF = [
    ('as', 'pos_wc14v8as.words', 'target_as'),
    ('va', 'pos_wc14v8va.words', 'target_va'),
    ('ow', 'pos_wc14v8ow.words', 'target_ow'),
    ('sp', 'pos_wc14v8sp.words', 'target_sp'),
    ('if', 'pos_wc14v8if.words', 'target_if'),
    ('te', 'pos_wc14v8te.words', 'target_te'),
    ('sv', 'pos_wc14v8sv.words', 'target_sv'),
    ('vw', 'pos_wc14v8vw.words', 'target_vw'),
]
shelf_ok = True
vol_paths = {}
for lex, pos_rel, _tbase in SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('shelf: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr30_vol_%s.ctos' % lex)
    io.open(volp, 'wb').write(art)
    vol_paths[lex] = volp
    print('shelf vol-%s: %d B md5 %s' % (lex, len(art),
                                         hashlib.md5(art).hexdigest()[:8]))
for lex, _pos_rel, tbase in SHELF:
    volp = vol_paths.get(lex)
    if volp is None:
        continue
    ok10 = True
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', '%s%d.words' % (tbase, d))
        ref = jc(work_path, src)
        got = jc(volp, src)
        if ref is None or got is None:
            print('shelf %s%d: молчание тома/эталона' % (lex, d))
            ok10 = False
            continue
        if ref != got:
            print('shelf %s%d: MISMATCH' % (lex, d))
            ok10 = False
    print('shelf %s: %s' % (lex, '10/10 targets byte-ok' if ok10
                            else 'has mismatches above'))
    shelf_ok = shelf_ok and ok10
    # кросс-отказы: pr + первые цели чужих томов + Token-3-цель =
    # честное молчание (4-словный том требует p5, у Token-3 SRC5 за
    # терминатором == 0/EOF)
    for cross in ('target0.words', 'target_t3te0.words') + tuple(
            '%s0.words' % tb for _l, _p, tb in SHELF if tb != tbase):
        cx = os.path.join(REPO, 'Python_compiler', cross)
        g2 = jc(volp, cx)
        if g2 is None:
            print('shelf %s-vol on %s: молчание (честный отказ)' % (lex, cross))
        else:
            print('shelf %s-vol on %s: НЕ молчание (%d B)!!'
                  % (lex, cross, len(g2)))
            shelf_ok = False

# ---- ДОБАВЛЕНО: честная ПОЛКА Token-3 томов ----
# том te-T3: 10 / 10 на 'wc d te'; кросс-отказы на 4-словные цели и neg.
T3SHELF = [
    ('te', 'pos_wc14v9te.words', 'target_t3te'),
    ('pr', 'pos_wc14v9pr.words', 'target_t3pr'),
    ('as', 'pos_wc14v9as.words', 'target_t3as'),
    ('va', 'pos_wc14v9va.words', 'target_t3va'),
    ('ow', 'pos_wc14v9ow.words', 'target_t3ow'),
    ('sp', 'pos_wc14v9sp.words', 'target_t3sp'),
    ('if', 'pos_wc14v9if.words', 'target_t3if'),
    ('sv', 'pos_wc14v9sv.words', 'target_t3sv'),
    ('vw', 'pos_wc14v9vw.words', 'target_t3vw'),
]
for lex, pos_rel, tbase in T3SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('t3: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr30_t3_%s.ctos' % lex)
    io.open(volp, 'wb').write(art)
    print('t3 vol-%s: %d B md5 %s' % (lex, len(art),
                                      hashlib.md5(art).hexdigest()[:8]))
    ok10 = True
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', '%s%d.words' % (tbase, d))
        ref = jc(work_path, src)   # свежий честный эталон stage1
        got = jc(volp, src)
        if ref is None or got is None:
            print('t3 %s%d: молчание тома/эталона' % (lex, d))
            ok10 = False
            continue
        if ref != got:
            print('t3 %s%d: MISMATCH' % (lex, d))
            ok10 = False
    print('t3 %s: %s' % (lex, '10/10 targets byte-ok' if ok10
                         else 'has mismatches above'))
    shelf_ok = shelf_ok and ok10
    for cs in ('wc 0 %s %s' % (lex, lex), 'wc 0 pr te', 'wc 0 %s zz' % lex):
        cx = os.path.join(REPO, 'Python_compiler', 'neg_as2.words')
        # кросс-исходники Token-3: инлайн-случаи через temp-файл
        tmpsrc = os.path.join(TMP, 'regr30_t3_cx.words')
        with io.open(tmpsrc, 'w', encoding='ascii') as f:
            f.write(cs + '\n')
        g2 = jc(volp, tmpsrc)
        if g2 is None:
            print('t3 %s-vol on %r: молчание (честный отказ)' % (lex, cs))
        else:
            print('t3 %s-vol on %r: НЕ молчание (%d B)!!'
                  % (lex, cs, len(g2)))
            shelf_ok = False

# ---- веха-21б: честная ПОЛКА микро-форм (C + T1 старт) ----
# Каждое семейство = (флаг, pos, список target-файлов,
# список кросс-источников, сводный счётчик целей).
MSHELF = [
    ('t2d', 'pos_wc14v2d.words',
     ['target_t2d%d.words' % d for d in range(10)],
     ['wc 0 zz', 'wc 10', 'wc 0 te', 'wc']),
    ('t1te', 'pos_wc14v1te.words',
     ['target_t1te.words'],
     ['te zz', 'te te', 'te 5', 'te pr', 'zz', '0', 'wc 0 te']),
    ('t1pr', 'pos_wc14v1pr.words',
     ['target_t1pr.words'],
     ['pr zz', 'pr pr', 'pr 5', 'te', 'zz', '0', 'wc 0 pr']),
    ('t1as', 'pos_wc14v1as.words',
     ['target_t1as.words'],
     ['as zz', 'as as', 'as 5', 'te', 'pr', 'zz', '0', 'wc 0 as']),
    ('t1va', 'pos_wc14v1va.words',
     ['target_t1va.words'],
     ['va zz', 'va va', 'va 5', 'te', 'pr', 'as', 'zz', '0',
      'wc 0 va']),
    ('t1ow', 'pos_wc14v1ow.words',
     ['target_t1ow.words'],
     ['ow zz', 'ow ow', 'ow 5', 'te', 'pr', 'as', 'va', 'zz', '0',
      'wc 0 ow']),
    ('t1sp', 'pos_wc14v1sp.words',
     ['target_t1sp.words'],
     ['sp zz', 'sp sp', 'sp 5', 'te', 'pr', 'as', 'va', 'ow', 'zz',
      '0', 'wc 0 sp']),
    ('t1if', 'pos_wc14v1if.words',
     ['target_t1if.words'],
     ['if zz', 'if if', 'if 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'zz', '0', 'wc 0 if']),
    ('t1sv', 'pos_wc14v1sv.words',
     ['target_t1sv.words'],
     ['sv zz', 'sv sv', 'sv 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'if', 'zz', '0', 'wc 0 sv']),
    ('t1vw', 'pos_wc14v1vw.words',
     ['target_t1vw.words'],
     ['vw zz', 'vw vw', 'vw 5', 'te', 'pr', 'as', 'va', 'ow', 'sp',
      'if', 'sv', 'zz', '0', 'wc 0 vw']),
    ('t2pr', 'pos_wc14v2pr.words',
     ['target_t2pr.words'],
     ['wc pr zz', 'wc te', 'pr', 'wc pr pr', 'zz', '0', 'wc 0 pr',
      'wc pr 0']),
    ('t2te', 'pos_wc14v2te.words',
     ['target_t2te.words'],
     ['wc te zz', 'wc pr', 'te', 'wc te te', 'zz', '0', 'wc 0 te',
      'wc te 0']),
    ('t2as', 'pos_wc14v2as.words',
     ['target_t2as.words'],
     ['wc as zz', 'wc pr', 'wc te', 'as', 'wc as as', 'wc 0 as',
      'wc as 0', 'zz', '0', 'wc']),
    ('t2va', 'pos_wc14v2va.words',
     ['target_t2va.words'],
     ['wc va zz', 'wc pr', 'wc te', 'va', 'wc va va', 'wc 0 va',
      'wc va 0', 'zz', '0', 'wc']),
    ('t2ow', 'pos_wc14v2ow.words',
     ['target_t2ow.words'],
     ['wc ow zz', 'wc pr', 'wc te', 'ow', 'wc ow ow', 'wc 0 ow',
      'wc ow 0', 'zz', '0', 'wc']),
    ('t2sp', 'pos_wc14v2sp.words',
     ['target_t2sp.words'],
     ['wc sp zz', 'wc pr', 'wc te', 'sp', 'wc sp sp', 'wc 0 sp',
      'wc sp 0', 'zz', '0', 'wc']),
    ('t2if', 'pos_wc14v2if.words',
     ['target_t2if.words'],
     ['wc if zz', 'wc pr', 'wc te', 'if', 'wc if if', 'wc 0 if',
      'wc if 0', 'zz', '0', 'wc']),
    ('t2sv', 'pos_wc14v2sv.words',
     ['target_t2sv.words'],
     ['wc sv zz', 'wc pr', 'wc te', 'sv', 'wc sv sv', 'wc 0 sv',
      'wc sv 0', 'zz', '0', 'wc']),
    ('t2vw', 'pos_wc14v2vw.words',
     ['target_t2vw.words'],
     ['wc vw zz', 'wc pr', 'wc te', 'vw', 'wc vw vw', 'wc 0 vw',
      'wc vw 0', 'zz', '0', 'wc']),
    ('t5gpr', 'pos_wc14v2gpr.words',
     ['target_t5gpr.words'],
     ['wc 5 pr pr pr zz', 'wc 5 pr pr zz', 'wc 5 pr pr te',
      'wc pr pr pr pr', 'wc 5 yu pr pr', 'wc pr', 'wc te',
      'wc 5 te te te', 'zz', '0', 'wc']),
]
micro_total = 0
for ftag, pos_rel, tgt_list, cross_list in MSHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('micro: том %s не собрал бинарник' % ftag); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr40_micro_%s.ctos' % ftag)
    io.open(volp, 'wb').write(art)
    print('micro vol-%s: %d B md5 %s' % (ftag, len(art),
                                         hashlib.md5(art).hexdigest()[:8]))
    okn = True
    n_ok = 0
    for rel in tgt_list:
        src = os.path.join(REPO, 'Python_compiler', rel)
        ref = jc(work_path, src)
        got = jc(volp, src)
        if ref is None or got is None:
            print('micro %s %s: молчание тома/эталона' % (ftag, rel))
            okn = False
            continue
        if ref != got:
            print('micro %s %s: MISMATCH' % (ftag, rel))
            okn = False
        else:
            n_ok += 1
    print('micro %s: %d/%d targets byte-ok'
          % (ftag, n_ok, len(tgt_list)))
    micro_total += n_ok
    shelf_ok = shelf_ok and (n_ok == len(tgt_list))
    for cs in cross_list:
        tmpsrc = os.path.join(TMP, 'regr40_micro_cx.words')
        with io.open(tmpsrc, 'w', encoding='ascii') as f:
            f.write(cs + '\n')
        g2 = jc(volp, tmpsrc)
        if g2 is None:
            print('micro %s-vol on %r: молчание (честный отказ)' % (ftag, cs))
        else:
            print('micro %s-vol on %r: НЕ молчание (%d B)!!'
                  % (ftag, cs, len(g2)))
            shelf_ok = False

# ---- спринт 15: честная ПОЛКА T4 digit-tail 'wc d L d3' ----
T4SHELF = [
    ('te', 'pos_wc14v3te.words', 'target_t4te'),
    ('va', 'pos_wc14v3va.words', 'target_t4va'),
    ('sp', 'pos_wc14v3sp.words', 'target_t4sp'),
    ('sv', 'pos_wc14v3sv.words', 'target_t4sv'),
    ('pr', 'pos_wc14v3pr.words', 'target_t4pr'),
    ('as', 'pos_wc14v3as.words', 'target_t4as'),
    ('ow', 'pos_wc14v3ow.words', 'target_t4ow'),
    ('if', 'pos_wc14v3if.words', 'target_t4if'),
    ('vw', 'pos_wc14v3vw.words', 'target_t4vw'),
]
for lex, pos_rel, tbase in T4SHELF:
    art = jc(work_path, os.path.join(REPO, 'Python_compiler', pos_rel))
    if art is None:
        print('t4: том %s не собрал бинарник' % lex); shelf_ok = False
        continue
    volp = os.path.join(TMP, 'regr53_t4_%s.ctos' % lex)
    io.open(volp, 'wb').write(art)
    print('t4 vol-%s: %d B md5 %s' % (lex, len(art),
                                      hashlib.md5(art).hexdigest()[:8]))
    ok10 = True
    for d in range(10):
        src = os.path.join(REPO, 'Python_compiler', '%s%d.words' % (tbase, d))
        ref = jc(work_path, src)   # свежий честный эталон stage1
        got = jc(volp, src)
        if ref is None or got is None:
            print('t4 %s%d: молчание тома/эталона' % (lex, d))
            ok10 = False
            continue
        if ref != got:
            print('t4 %s%d: MISMATCH' % (lex, d))
            ok10 = False
    print('t4 %s: %s' % (lex, '10/10 targets byte-ok' if ok10
                         else 'has mismatches above'))
    shelf_ok = shelf_ok and ok10
    # честные отказы: чужие T4-цели (p2), Token-3 target, G target,
    # 5 negs (tracked 0xFE-артефакты stage1) — том честно молчит
    for cross in tuple('target_t4%s0.words' % _l2
                       for _l2, _p, _tb in T4SHELF if _l2 != lex) + (
            'target_t3te0.words', 'target_t5gpr.words',
            'neg_t4zz.words', 'neg_t4sv.words', 'neg_t4pr.words',
            'neg_t4vw.words', 'neg_t4sp.words'):
        cx = os.path.join(REPO, 'Python_compiler', cross)
        g2 = jc(volp, cx)
        if g2 is None:
            print('t4 %s-vol on %s: молчание (честный отказ)' % (lex, cross))
        else:
            print('t4 %s-vol on %s: НЕ молчание (%d Б)!!'
                  % (lex, cross, len(g2)))
            shelf_ok = False
    # инлайн-отказы: digit-продление хвоста ('wc 5 L 3 7' — stage1
    # эмитит 0xFF Token=5, том честно молчит: слой = 4 слова),
    # 2-значный d3 ('07'), fail@1/@2-слоты, чужой T3/G/B-слой
    # ---- веха-22 (W-54): честные много-стейтментные кросс-молчания
    # (probe46/46d: stage1 честно аддитивен, том честно молчит — слой
    # = ровно 4 слова; double/newline/mixed/T4T3/tail2/tailz/dot) ----
    for cs in ('wc 5 %s 3 7' % lex, 'wc 5 %s 07' % lex,
               'wc 10 %s 3' % lex, 'wc zz %s 3' % lex,
               'wc 5 %s' % lex, 'wc pr 3', 'wc 5 pr pr pr',
               'wc 5 pr pr pr zz',
               'wc 5 %s 3 wc 5 %s 3' % (lex, lex),
               'wc 5 %s 3\nwc 5 %s 3' % (lex, lex),
               ('wc 5 %s 3 wc 5 pr 1' % lex) if lex == 'te' else
               ('wc 5 %s 3 wc 5 te 1' % lex),
               'wc 5 %s 3 wc 5 %s' % (lex, lex),
               'wc 5 %s 3 7 8' % lex,
               'wc 5 %s 3 7 8 z' % lex,
               'wc 5 %s 3.' % lex):
        tmpsrc = os.path.join(TMP, 'regr53_t4_cx.words')
        with io.open(tmpsrc, 'w', encoding='ascii') as f:
            f.write(cs + '\n')
        g2 = jc(volp, tmpsrc)
        if g2 is None:
            print('t4 %s-vol on %r: молчание (честный отказ)' % (lex, cs))
        else:
            print('t4 %s-vol on %r: НЕ молчание (%d Б)!!'
                  % (lex, cs, len(g2)))
            shelf_ok = False

# холодный ход (нет --source)
cold = {}
for tag, binp in (('head', head_path), ('work', work_path)):
    outp = binp + '.out'
    if os.path.exists(outp):
        os.remove(outp)
    subprocess.run([sys.executable, VM, binp, '--quiet'], capture_output=True)
    cold[tag] = io.open(outp, 'rb').read()
print('cold: %s' % ('IDENTICAL' if cold['head'] == cold['work'] else 'DIFF'))
if cold['head'] != cold['work']:
    fails.append('cold DIFF')

print('')
if fails:
    print('FAILURES:')
    for f_ in fails:
        print(' ', f_)
    sys.exit(1)
print('REGRESS OK W-61 cross-shape t4×t3-sv-volume (603tok 876B dc7ff0ab; loader 0x400: tracked IDENTICAL + 4-word-shelf 80/80 + T3-shelf '
      '90/90 + micro-shelf t2d 10/10 + t1te 1/1 + t1pr 1/1 + t1as 1/1 '
      '+ t1va 1/1 + t1ow 1/1 + t1sp 1/1 + t1if 1/1 + t1sv 1/1 '
      '+ t1vw 1/1 + t2pr 1/1 + t2te 1/1 + t2as 1/1 + t2va 1/1 + '
      't2ow 1/1 + t2sp 1/1 + t2if 1/1 + t2sv 1/1 + t2vw 1/1 + t5gpr 1/1 + '
      'T4-shelf 90/90 + T4 multi-statement cross-silences (8x9) + '
      'T4 digit-tail cross-silences + cold)')
