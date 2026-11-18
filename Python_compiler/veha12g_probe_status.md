# W-122 / 24д + 24д-б — фиксепоинт `T(S_T)==T` достигнут

Дата: 2026-11-18. Ветка `feature/ctos-kernel`, база `26c00f4` (приёмка W-122/24д-а).
Fresh stage1: `Compiler/stage1_compiler.ctos`, **22861 Б, md5 `984d90d4ab327d67d9f194809a399926`**
(пересобран из `Compiler/stage1_compiler.kt` при подъёме `MAX_SOURCE_WORDS` 0x1000 → 0x2000;
эмиссия байт-в-байт неизменна против `de5079df`: probe125 `_stage1_sem.py` 20/20 SAME).

## Принято в tracked

- `Compiler/stage1_compiler.kt` / `.ctos` — `MAX_SOURCE_WORDS` 0x1000 → 0x2000
  (4096 → 8192 слов; `MAX_USER_WORDS` в билдере 4094 → 8190). Причина — budget-приговор:
  24д-том 4375 ток > 4094, прецедент W-120 (0x800 → 0x1000).
- `Python_compiler/wc14v3ring_build.py` — `ad/gt/lt` (обобщённая pending-машина
  `su/eq`) + `em/wo/ml` (спринт 102).
- `Python_compiler/pos_wc14v3ring.words` — **5586 ток ≤ 8190**, 13650 Б, md5 `4d12b7ee`.
- `Python_compiler/regr120.py` — пин `30a90f3f`, полка расширена 25 кейсами 24д-б;
  два старых div-пина (`nb 7 em`, `nb 7 wo`) переведены в `ok`.
- `Python_compiler/selfhost_check.py` — явный `--steps 50000000`.

Сборка: `[SUCCESS] Compiler/stage1_compiler.ctos — 1348680 опкодов(а), ячеек: 5657`;
артефакт `Compiler/stage1_compiler.ctos.out` =
**13084 Б md5 `30a90f3ff440ec249a132f58ee5a040a`**, вердец `0xFF`.

## Приёмка byte-exact

`regr120.py`: **REGRESS OK / rc=0** — **209/209 positives BYTE-OK + 30/30 honest-silence
+ 33/33 diverg-silence + 3/3 ddiv-tracked**, cold IDENTICAL.
Новый ddiv — `ml`: stage1 печатает 45-Б отчёт, кольцо — 137-Б ml-кольцо.

probe125 `_t24db.py`: 8/11 BYTE-OK + 3 честных SILENT (`nb 12 em`, `em 5`, `wo 5`).
probe125 `_acc24db.py`: **272/275 GOOD**, 3 BAD — устаревшие ожидания, которые стали
BYTE-OK (`nb 7 em`, `nb 7 wo`, `wc 5 ml 2`), не регрессии.

## Устройство `em/wo/ml` (честно)

Детекция `ad/gt/lt` — по `cell[8]` = текущее слово исходника; тег цифры-операнда
`TAGTAB[8] = 4628 + 2·EQOA + 3·SUPA + 6·GTUA + 7·LTOA`, что даёт
`eq 0x1216 / su 0x1217 / ad 0x1214 / gt 0x121A / lt 0x121B`. Sticky-флаги —
по формуле `(2·PDG + X_old + is_X) == 1`.

24д-б:
- `em` = `[STREAM][0x5100] + [NumAcc][0x00F0]` (`TAGTAB[14]=0x5100`, `cell[20736]=1`);
  `wo` добавляет `[305][0x1300]`. Оба — поглотители `nb`-числа: без `nb`
  кольцо честно молчит rc=0.
- `ml` — pending-слово + runtime-кольцо 17 рекордов / 92 Б. `ABS(v,'va')` загружает
  acc, `ABS(v,'aa')` добавляет; цели `rec08 JZ=P+47`, `rec09 JMP=P+86`,
  `rec16 JMP=P+25`. `ml` без цифры — tracked-DIV (оба печатают, байты разные).

Ключевой фикс прогноза: `ow` эмитит **14 Б** (`OP_OUTCELL_V` + `FILE_PUT`,
`stage1 KW_OW`), а не 9 Б как `pr`. Старый вклад `PGOF·4` недосчитывал 5 Б на
каждое `ow` ⇒ `FPOS` уезжал на −5 к `es#3` и на −50 к `TERM`, ломая patched-цели.
Добавлен отдельный вклад `OWFA·5`.

## Фиксепоинт `T(S_T) == T` — ДОСТИГНУТ

`python -X utf8 Python_compiler/selfhost_check.py`:

- `T = S(S_T)` — свежий stage1 собирает S_T в 13084 Б `30a90f3f`;
- `T(S_T)` — кольцо на своём же исходнике даёт 13084 Б `30a90f3f`;
- `SELFHOST IDENTICAL: T(S_T) == T`, rc=0.

Для самосборки лимит VM поднят явно: `--steps 50000000` (дефолтные 10 млн
опкодов честно падают `KERNEL PANIC` на ~25.8 млн); расхождения не маскируются.

История откатов (для честности): на W-121 первый отказ был 1263-й токен (`gt`),
на 24д-а — 1424-й (`ml`). Оба устранены в 24д/24д-б.

## Воспроизведение

```
python -X utf8 Python_compiler/codegen.py Compiler/stage1_compiler.kt
python -X utf8 Python_compiler/wc14v3ring_build.py
python -X utf8 CtOs-Emu/ctos_vm.py Compiler/stage1_compiler.ctos \
  --source Python_compiler/pos_wc14v3ring.words --quiet
python -X utf8 Python_compiler/regr120.py        # REGRESS OK / rc=0
python -X utf8 Python_compiler/selfhost_check.py  # SELFHOST IDENTICAL / rc=0
```

## Итог спринта 102 (W-122, 24д-б)

- `em/wo/ml`: **принято**, byte-exact; `regr120` 209/30/33/3, cold IDENTICAL.
- ВЕХА-24: **закрыта** — `T(S_T)==T`, 13084 Б `30a90f3f`, S_T 5586 ток ≤ 8190.
- Граница 0x1000 → 0x2000: **принята**, эмиссия stage1 byte-exact неизменна.

---

## Архив: W-122 / 24д-а (ad/gt/lt + честный подъём границы)

База `1522e0c`. BYTE-OK 21/25; новые `ad/gt/lt` работали, 4 SILENT = ml/em/wo +
`nb 3 ad 7 ne`. Том 4375 ток, артефакт 10674 Б `cc678b3e`, regr120 188/188 +
25/25 + 35/35 + 2/2, cold IDENTICAL. Первый refusal фиксепоинта — 1424-й токен (`ml`).

## Архив: W-121 / 24г (if/es/mk/jb + su)

База `534d678`. Fresh stage1 тогда: 22861 Б md5 `de5079df`.
Том 4065 ток, артефакт 9955 Б `22896d3f`, probe124 53/16/0, regr120 177/177 + 24/24 +
35/35 + 2/2, cold IDENTICAL. Первый refusal фиксепоинта — 1263-й токен (`gt`).
Подробности — в git-истории (`1522e0c`) и комментариях `wc14v3ring_build.py`.
