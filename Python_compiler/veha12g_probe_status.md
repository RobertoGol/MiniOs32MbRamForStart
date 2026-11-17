# W-121 / 24г (if/es/mk/jb + su) — статус после переноса в tracked

Дата: 2026-11-18. Ветка `feature/ctos-kernel`, база `534d678` (промежуточный статус W-121).
Fresh stage1: `Compiler/stage1_compiler.ctos`, 22861 Б, md5 `de5079df0067dd4ae39802fa815c5511` — не менялся.

## Принято в tracked (24г)

- `Python_compiler/wc14v3ring_build.py` — билдер 24г (if/es/mk/jb/su + Stage2-патч TAIL).
- `Python_compiler/pos_wc14v3ring.words` — пересобранный том: **4065 ток ≤ 4094**, 9917 Б.
- `Python_compiler/regr120.py` — регрессия на базе `regr119.py` с пином 24г и полкой 69 кейсов.
- `Python_compiler/selfhost_check.py` — честная проверка фиксепоинта `T(S_T) == T`.

Сборка: `[SUCCESS] … 985769 опкодов, ячеек 4136`; артефакт `Compiler/stage1_compiler.ctos.out`
= **9955 Б md5 `22896d3ffa1cf2e7f2a69967d3b9f10a`**, вердец `0xFF`.

## Приёмка byte-exact (probe124, 69 кейсов)

`_t124_smoke.py`: **BYTE-OK=53, OK-DIV=16, DIFF=0**.
16 OK-DIV = честные stage1-неги (`0xFE`), на которых кольцо молчит `rc=0` без `.out`
(sticky `BADIF/BADEJ/BADJB`, 4-й if/es, jb без живой метки, открытый `nb`).
Полный отчёт: `probe124/probe124_smoke.txt`.

`regr120.py` (base regr119): **REGRESS OK / rc=0** — все прежние полки перенесены;
ring-полка расширена 24г-кейсами: **177/177 positives BYTE-OK + 24/24 honest-silence
+ 35/35 diverg-silence + 2/2 ddiv-tracked**, cold IDENTICAL. Артефакт 9955 Б `22896d3f`.
При первом прогоне regr120 честно поймал регрессию `eq 3 eq 4` (см. урок 5), после
фикса `SUPA` — FAIL=0. Лог: `probe124/regr120.log`.

## Ключевые уроки 24г (честно)

1. `site_store`: база `392` (`CSDP=251`), EJ-сайты 409..411, `adj=-1` для третьего;
   пары селекторов через `SITE_FACTORS {401:(9,), 404:(3,4), 409:(2,9)}` — закрыло кейс 25
   (`if te if te if te es es es`): if#1 target `0x2B`, es#3 target `0`.
2. `mk`/`jb`: `MARKP:=20` — сигнал «нет живой метки»; `cstore(MARKP, JBFA, N(20))`;
   sticky отказ записывается сразу после каждого члена; PS-gate `+ABS(BADJB,'aa')`.
3. `te`: цепь `X_te` читает предыдущую реальную запись `[PTR-2]`, не `cell[149]`.
4. `su` (`KW_SUB 0x7573`): self-конста в `SUWC=57`, флаг `SUFL=58`, pending `SUPA=59`,
   тег цифры `0x1217` вместо `0x1216` (`N(TAGEQ)+ABS(SUPA,'aa')` в `TAGTAB[8]`).
5. `SUPA' = (2·PDG + SUPA_old + is_su) == 1` — цифра закрывает pending. Старая формула
   `(su+SUPA+PDG)==1` ставила su-тег на второй `eq` (`eq 3 eq 4`: ring `508c1429` против
   stage1 `dd23d731`) — поймано regr120, исправлено; после правки smoke остался 53/16/0.
6. Forecast размера: `pr/ow` дают **9 Б всего** = 5 Б базы + 4 Б хвоста; было `ml·9`
   сверх базы — все if/es/jb-цели ехали вперёд (кейс 68). Исправлено на `ml·4`.
7. Бюджет сэкономлен группировкой INIT-констант (один `N(0)/N(1)/N(2)/N(16)/N(20)/N(ARR)`
   на группу ADC-независимых записей): 4092 → 3990 → 4065 с учётом su/SUPA и фиксов.

## Фиксепоинт `T(S_T) == T` — НЕ достигнут (честный блокер)

`selfhost_check.py`:
- `T = S(S_T)` — свежий stage1 собирает S_T в 9955 Б `22896d3f`;
- `T(S_T)` — кольцо на своём же исходнике **молчит** `rc=0`, 4 420 780 опкодов, 677 ячеек;
- бисект: первый отказ на **1263-м токене**, контекст `… nb 6 1 va gt 9 eq 0 nb …` —
  первое неподдерживаемое исходное слово **`gt`** (`KW_GT 0x00007467`).

Всего в S_T неподдерживаемых кольцом слов: `ml` (50), `ad` (9), `wo` (7), `gt` (5),
`em` (1), `lt` (1). Для фиксепоинта кольцо обязано эмитировать их байт-в-байт против
stage1: `ad/gt/lt` — pending-опы OP_LOAD[0x14/0x1A/0x1B] (аналог `eq/su`, но новые
теги/веса), `ml` — 92-Байтовый runtime-кольцевой множитель (`Emit_Ml_Ring`), `em/wo` —
output-системные syscall-формы. Текущий запас бюджета — 29 токенов (4065/4094), этого недостаточно.

Это **не** регрессия 24г: W-120-кольцо тоже молчит на своём S_T по тем же причинам.
24г закрывает управляющие слова; 24д (фиксепоинт) — отдельный фронт W-122.

## Воспроизведение

```
python -X utf8 Python_compiler/wc14v3ring_build.py
python -X utf8 CtOs-Emu/ctos_vm.py Compiler/stage1_compiler.ctos \
  --source Python_compiler/pos_wc14v3ring.words --quiet
python -X utf8 Python_compiler/regr120.py
python -X utf8 Python_compiler/selfhost_check.py   # ожидаемо rc=1 (BLOCKED)
```

## Итог спринта 100 (W-121)

- 24г: **принято**, byte-exact 53/16/0, regr120 REGRESS OK, cold IDENTICAL.
- 24д: **не принято**, фиксепоинт честно не сходится; требуется расширение набора source-words.
