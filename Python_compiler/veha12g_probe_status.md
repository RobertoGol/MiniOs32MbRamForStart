# W-122 / 24д (ad/gt/lt + честный подъём границы) — статус после переноса в tracked

Дата: 2026-11-18. Ветка `feature/ctos-kernel`, база `1522e0c` (приёмка W-121/24г).
Fresh stage1: `Compiler/stage1_compiler.ctos`, **22861 Б, md5 `984d90d4ab327d67d9f194809a399926`**
(пересобран из `Compiler/stage1_compiler.kt` после подъёма `MAX_SOURCE_WORDS` 0x1000 → 0x2000;
эмиссия байт-в-байт неизменна против `de5079df`: probe125 `_stage1_sem.py` 20/20 SAME).

## Принято в tracked (24д, частично)

- `Compiler/stage1_compiler.kt` / `.ctos` — `MAX_SOURCE_WORDS` 0x1000 → 0x2000
  (4096 → 8192 слов; `MAX_USER_WORDS` в билдере 4094 → 8190). Причина — budget-приговор:
  24д-том 4375 ток > 4094, прецедент W-120 (0x800 → 0x1000).
- `Python_compiler/wc14v3ring_build.py` — `ad/gt/lt` через обобщённую pending-машину `su/eq`.
- `Python_compiler/pos_wc14v3ring.words` — **4375 ток ≤ 8190**, 10663 Б.
- `Python_compiler/regr120.py` — пин `cc678b3e`, полка расширена 12 кейсами 24д.

Сборка: `[SUCCESS] … 1061656 опкодов, ячеек 4446`; артефакт
`Compiler/stage1_compiler.ctos.out` = **10674 Б md5 `cc678b3e180781d05dad0c7de6c0cf3d`**, вердец `0xFF`.

## Приёмка byte-exact (probe125, 25 кейсов)

`_w122_verify.py`: **BYTE-OK 21/25**. Новые слова:
`ad 0/1/5`, `gt 0/9`, `lt 0/2`, `nb 6 1 va gt 9 eq 0`, `nb 6 5 aa su 1 lt 2`,
`ad 5 ad 3`, `gt 0 lt 2 ad 5` — все BYTE-OK. Прежние `su/eq/wc/pr/te` без регресса.
Честные SILENT (4): `ml 2`, `nb 0 em`, `nb 0 wo` (ещё не реализованы),
`nb 3 ad 7 ne` (stage1 печатает 0xFE-артефакт, кольцо честно молчит — tracked-DIV).

`regr120.py`: **REGRESS OK / rc=0** — **188/188 positives BYTE-OK + 25/25 honest-silence
+ 35/35 diverg-silence + 2/2 ddiv-tracked**, cold IDENTICAL. Артефакт 10674 Б `cc678b3e`.

## Устройство `ad/gt/lt` (честно)

Детекция по `cell[8]` = текущее слово исходника (внутренние `gt/ad` кольца — просто
арифметика и не конфликтуют). Тег цифры-операнда:
`TAGTAB[8] = 4628 + 2·EQOA + 3·SUPA + 6·GTUA + 7·LTOA`, что даёт
`eq 0x1216 / su 0x1217 / ad 0x1214 / gt 0x121A / lt 0x121B`.
Sticky-флаги `EQOA/ADOA/GTUA/LTOA` по формуле `(2·PDG + X_old + is_X) == 1`
(аналог `SUPA` из 24г); `EQSG` — «чистый» is_eq до OR с остальными.
`ml` в сумме тега жжёт слот S — S стешится в `SSAV=198` и сразу восстанавливается.

## Фиксепоинт `T(S_T) == T` — НЕ достигнут (честный блокер)

`selfhost_check.py`:
- `T = S(S_T)` — свежий stage1 собирает S_T в 10674 Б `cc678b3e`;
- `T(S_T)` — кольцо на своём же исходнике **молчит** `rc=0`, 5 375 889 опкодов, 761 ячейка;
- бисект: первый отказ сдвинулся **1263 → 1424-й токен**, контекст
  `… 7 sv nb 1 9 1 va ml 2 nb 1 9 …` — первое неподдерживаемое слово **`ml`**.

Остаток неподдерживаемых слов в S_T: `ml` (50), `wo` (7), `em` (1).
`ml` — главная стена: 92-Б runtime-кольцо с тремя вычисляемыми целями прыжков
(`L0 = base+25`, `JZ→L0+22`, `JMP exit→L0+61`, `JMP body→L0`).
Все байты кольца выразимы через record-эмиттер `[X][TAG16]`:
`[0x55][BE32]` (STORE_AT), `[0x15][BE32]` (CONST), `[0x12][0x19|0x16|0x17][BE32]` (LOAD),
`[0x06][BE32]` (JZ), `[0x07][BE32]` (JMP). Реализация — отдельный фронт (24д-б).
`em` = `OP_OUTCELL + BE32(STREAM_EMIT_CELL) + BE32(N)` (9 Б), `wo` добавляет
`OP_SYSCALL(FILE_PUT)` (14 Б всего) — поглотители `nb`-числа, дешевле `ml`.

Это **не** регрессия: фиксепоинт не сходился и на W-121 по тем же причинам.

## Воспроизведение

```
python -X utf8 Python_compiler/codegen.py Compiler/stage1_compiler.kt
python -X utf8 Python_compiler/wc14v3ring_build.py
python -X utf8 CtOs-Emu/ctos_vm.py Compiler/stage1_compiler.ctos \
  --source Python_compiler/pos_wc14v3ring.words --quiet
python -X utf8 Python_compiler/regr120.py
python -X utf8 Python_compiler/selfhost_check.py   # ожидаемо rc=1 (BLOCKED at ml)
```

## Итог спринта 101 (W-122, 24д-а)

- `ad/gt/lt`: **принято**, byte-exact 21/25 (новые 11 кейсов BYTE-OK), regr120 REGRESS OK.
- Граница 0x1000 → 0x2000: **принята**, эмиссия stage1 byte-exact неизменна.
- 24д-б (`ml/em/wo` → фиксепоинт): **не принято**, честно блокируется на `ml` (токен 1424).

---

## Архив: W-121 / 24г (if/es/mk/jb + su)

Дата: 2026-11-18. База `534d678`. Fresh stage1 тогда: 22861 Б md5 `de5079df`.
Том 4065 ток, артефакт 9955 Б `22896d3f`, probe124 53/16/0, regr120 177/177 + 24/24 +
35/35 + 2/2, cold IDENTICAL. Первый refusal фиксепоинта — 1263-й токен (`gt`).
Подробности — в git-истории (`1522e0c`) и комментариях `wc14v3ring_build.py`.
