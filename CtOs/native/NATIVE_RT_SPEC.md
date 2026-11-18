# A1/A2/A3 — нативный интерпретатор (bring-up Ф2)

Статус: ✅ A1, A2, A3а приняты; A3b, A4a, A5 и A5b приняты **в QEMU как эмуляционная контрольная точка**, 2026-11-18/19. Связано: `CtOs/BRINGUP_SPEC.md` (Ф2/Ф3, вариант A), `CtOs/native/boot/BOOT_SPEC.md`, TKT-056 / TKT-055 / TKT-052.

## A1 — подмножество ядра (принято ранее)

`CtOs/native/native_rt.c` (C11) исполнял ровно те опкоды, что реально использует ядро:
`NOP INIT ALLOC_ST CALL RET TERM JZ JMP CONST LOAD(0x14/0x15/0x16/0x17/0x18/0x19/0x1A/0x1B) STORE_A STORE_AT INCELL INCELL_IND STORE_IND OUTCELL OUTCELL_V`.
CRC-32 заголовка v1.1, строго 32-битные ячейки, `FATAL` на нулевой `STORE_IND`. Сверка с `ctos_vm.py`: `memmgr` 13 портов / 1395 опкодов / 73 ячейки; `kernel_sched` 12 портов / 132552 опкода / 313 ячеек.

## A2 — NID-слой и полная самосборка (этот шаг)

Добавлено честно, без тихих заглушек:

- **Файлы:** `0x130 FILE_BEGIN`, `0x131 FILE_PUT` (BE32), `0x132 FILE_U16` (BE16), `0x133 FILE_END`, `0x134 FILE_U8`, `0x135 FILE_SEAL` (CRC-32 тела, zlib-совместимый), `0x136 FILE_SEEK`, `0x137 FILE_GET` (поток слов исходника, EOF в `0x00F00FF2`).
  - Важный контракт, найденный сверкой: `FILE_SEAL` обязан читать **весь** файл (`fseek END` → `ftell`), а не до текущей позиции записи — после `FILE_SEEK` позиция может быть меньше хвоста. Иначе CRC расходится ровно на 4 байта при полностью совпадающем теле.
- **Контекст (TKT-055):** `0x150 SAVE`, `0x151 RESTORE`, `0x152 YIELD`; блок `CTX1` (магия `0x43545831`), per-epoch переустановка ядерного контекста на каждом `RESTORE`, окно статиков `+166`, лимиты `rts ≤ 0x80`, статиков `≤ 0x50`.
- **Таймер (TKT-055):** `0x153 TIMER_ARM`, `0x154 TIMER_RET`, кадр `TCK1` (`0x54434B31`), статик-окно `+132`, тик доставляется **между** инструкциями до инкремента `op_count` — ровно как в эталонной VM (проверено по исходнику `ctos_vm.py`, stray off-by-one исключён).
- **Опкоды полной самосборки:** `0x11 STORE` (адрес = смещение опкода, стадия-0), `0x20..0x26 NET_OPS` (1-байтные маркеры etalon VM), `0x60 ASMBLOCK` (`+LE u32` длина + байты).
- `RTS_MAX` поднят до `65536`: VM держит стек возвратов без лимита, а кольцевой компилятор при чтении потока исходника делает глубокие вложенные `CALL`. Это честный запас, не маскировка расхождения.

## A3а — загрузка `.ctos`-модулей ядра (этот шаг)

Контейнер **CTMD v1** (`CtOs/native/build_modules_image.py`, детерминированный; образ `*.ctmd` не отслеживается VCS, а создаётся сборщиком по требованию):
заголовок `CTMD` + версия + число модулей, каталог по 48 Б (имя ASCIIZ[32],
LE32 смещение, LE32 длина, LE32 CRC-32 тела, LE32 reserved), тела выровнены по 16 Б.

`native_rt.exe --module <name> <image.ctmd> <events> [source.words]`:

- ищет имя в каталоге, проверяет границы тела и CRC-32 против каталога;
- грузит тело в interpreter как обычный `.ctos` (общая проверка `verify_code`);
- пишет в events честный след `MODULE <name> <len> <crc>`;
- артефакт `FILE_*` модуля — `<image>.<name>.out`, чтобы не затирать прямой запуск.

Приёмка (`verify_native_rt.py`, все сверки с эталонной VM):

| Модуль из CTMD | EVENT'ы VM/NAT | Опкоды/ячейки | Артефакт |
|---|---:|---:|---|
| `memmgr` | 13/13 | 1395 / 73 | — |
| `sched` | 12/12 | 132552 / 313 | — |
| `syscall_test` | 10/10 | 23 / 1 | 20 Б md5 совпал |
| `stage1` | 17295/17295 | 1348680 / 5657 | T 13084 Б md5 `30a90f3f…` совпал |

Честные негативы загрузчика: неизвестное имя ⇒ `FATAL … не найден` (rc=1),
подмена тела с неверным CRC ⇒ `FATAL CTMD: честный брак целостности модуля` (rc=1).

## A3b — сырой legacy-BIOS загрузчик (принят в QEMU)

`CtOs/native/boot/`: `mbr.S` (LBA 0, `0x7C00`, EDD `INT 13h AH=41h` + `AH=42h`), `stage2.S` (LBA 1..4, `0x1000:0000`, CTMD с LBA 8 в `0x2000:0000`, проверка magic/каталога/CRC-32, VGA text + COM1, защищённый режим), `build_boot_image.py` (детерминированный образ 65536 Б). Плоский код-сегмент требует 32-битный far jump с линейным смещением `0x1019A`; 16-битная форма давала `#UD` по физическому `0x19A` — найдено трассой `-d in_asm,int` и исправлено.

`python -X utf8 Python_compiler/verify_boot_image.py`: холодная сборка дважды в разных TEMP ⇒ `IDENTICAL`, образ 65536 Б md5 `2b8847fc192c3c7595e9240d9091730a`; QEMU positive `rc=33` с полным логом до `CTOS A3b PM OK`; негативы (подмена магии `CTMD`→`XXXX`, порча тела `memmgr`) ⇒ `rc=35` с диагностикой без `PM OK`. Детали — `CtOs/native/boot/BOOT_SPEC.md`.

## A4a — нативный интерпретатор в защищённом режиме (принят в QEMU)

Рантайм в PM — **тот же `CtOs/native/native_rt.c`**, собранный в flat 32-bit код. Меняется только окружение: `CtOs/native/boot/pm/` даёт freestanding-заголовки, `pm_start.S` (BSS-clear, `argc=5`, argv `native_rt --module memmgr CTMD:image events:com1`) и `shim.c` (COM1 вместо event-файла, in-memory `FILE` для CTMD/артефакта, bump-allocator, свой `fprintf`/`snprintf`). ctmd физически лежит по `0x20000`, PM-код грузится с LBA 72 по `0x40000`, BSS по `0x01000000`, стек `0x90000`.

Флаги сборки включают `-mno-mmx -mno-sse -mno-sse2`: иначе GCC выдаёт `pcmpeqd %xmm3,%xmm3`, а при `CR4=0` это `#UD`. `nm -u` PM-рантайма пуст — builder падает, если остался неразрешённый символ.

`verify_boot_image.py` теперь проверяет:

- холодную сборку ×2: образ 69632 Б md5 `dc90a080710efb03b3ccbfe640cebb9e` (stage2 1720 Б);
- positive QEMU: `rc=39` (`AX=0x13`), 24 линии COM1, из них 15 event'ов **байт-в-байт** совпадают с хост-запуском `native_rt.exe --module memmgr` (`MODULE`, 13 × `PORT`, `OPS 1395 CELLS 73`);
- негативы stage2: `rc=35`;
- негатив рантайма: порча тела `memmgr` с пересчётом CRC в каталоге CTMD проходит stage2, но `verify_code()` ловит внутренний CRC v1.1 ⇒ `FATAL: [TKT-040]`, `rc=41` (`AX=0x14`).

## A5 — самоадаптивная установка принятой базы (принят в QEMU)

Отдельный 16-битный этап `CtOs/native/boot/install.S` лежит в LBA 5..7 и грузится в `0x5000:0000`. Он **не меняет** ни `native_rt.c`, ни PM-рантайм: задача — найти целевой диск, перенести на него уже принятую A4a-базу, закрепить загрузку, удалить себя (самоудаление установщика) и оставить автозапуск проверенного `memmgr`.

Контракт честный, без угадывания:

- источник помечен `CTOS-INST-A5` в MBR+`0x180`; без маркера установщик **молча** возвращает `AL=0` (это уже рабочая система, печать ей не нужна);
- цель ищется сканированием `0x80..0xEF` через EDD (`AH=41h`, бит0 в `CX`), маркер `CTOS-TGT-A5!` в MBR+`0x180`, диск источника пропускается; нет цели ⇒ `AL=2`;
- 136 секторов образа копируются порциями по 64 сектора через `0x6000:0000` с **перечиткой и `repe cmpsb`** перед закреплением; сбой ⇒ `AL=2`, честная диагностика;
- закрепление: `ACTIVE=0x80` в MBR+`0x1BE`, sentinel `CTOS-LOCK-A5` в LBA136 (версия=1, `image_sectors=136`, 32-битная сумма dword LBA0..135, флаги=0), снятие обоих маркеров и затирание LBA5..7. Шифрование **отклонено**: на R3700 нет TPM/надёжного ключа;
- `AL=1` — установлено. Stage2 вызывает установщик только при маркере на своём диске (после самоудаления LBA5..7 — нули, звать их нельзя), печатает `CTOS A5 INSTALL OK` / `CTOS A5 AUTORUN memmgr`, при отказе — `CTOS A5 REFUSED` и `AX=0x12` (rc=37).

`python -X utf8 Python_compiler/verify_a5_install.py`: два raw-диска в QEMU, холодная сборка ×2 IDENTICAL, md5 образа совпадает с A4a-гейтом, установка даёт `rc=39` и 7 A5-строк, sentinel и состояние обоих дисков проверены побайтово, перезагрузка с цели — `rc=39`, 24 строки COM1, **ни одной A5-строки**, негатив без маркера цели — `rc=37`. На R3700 не принято.

## A5b — закрепление загрузки стало двусторонним (принят в QEMU)

A5 писал sentinel, но сам загрузчик его не читал. В A5b `stage2.S` проверяет закрепление **до** EDD/CTMD/перехода в PM:

- LBA0 с `ACTIVE != 0x80` — чистая установочная система, проверка молча пропускается, чтобы A4a-лог остался байт-в-байт прежним;
- `ACTIVE == 0x80` — читается LBA136: магия `CTOS-LOCK-A5` + 4 нуля, версия 1 (`+0x10`), `image_sectors=136` (`+0x14`), контрольная сумма (`+0x18`), флаги 0 (`+0x1C`);
- сумма dword по LBA0..135 пересчитывается тремя порциями 64/64/8 секторов (`INT 13h AH=42h`, буфер `0x6000:0000`) и сравнивается с записанной установщиком;
- любое расхождение — `CTOS A5 PIN FAIL`, `AX=0x11` (rc=35), **без** `CTMD ALL OK` и `PM OK`; отказ чтения LBA136 — `CTOS A5 PIN READ FAIL`.

Исправлены два конкретных бага, найденных трассой: в `repe cmpsb` были перепутаны `DS:SI` и `ES:DI` (сравнивался код stage2 с областью за sentinel), а флаги читались по `+0x20` вместо `+0x1C`. Временная отладочная печать (`GOT`/`WANT`/`FIRST`/`PIN MAGIC`/`PIN VER`/`PIN SIZE`/`PIN FLAGS`) удалена; при успехе A5b не печатает ничего.

Верификатор добавлен к `verify_a5_install.py`: 7 честных негативов — подмена сектора PM внутри LBA0..135, подмена checksum/magic/version/size/flags sentinel и стёртый sentinel. Все дают `rc=35` + `CTOS A5 PIN FAIL` и не доходят до PM.

## Честные границы (НЕ сделано)

- **A3b/A4a/A5/A5b на железе:** boot shim, PM-рантайм, самоустановка и проверка закрепления реально проходят в QEMU 11.1.0, но на **R3700 не приняты** — доступа к моноблоку нет, интернета на нём нет. На R3700 только очень старый BIOS-аналог; UEFI/GRUB не подтверждены. «Работает на железе» **не заявляется**, моноблок пока не трогаем. `isa-debug-exit` — тестовый хук QEMU, не честное завершение для реального стенда.
- A1/A2/A3а — хостовый нативный рантайм для сверки семантики и загрузки модулей; A4a — исполнение того же кода в PM, но пока только для модуля `memmgr`. `sched`, `syscall_test`, `stage1` в PM не запускались; полная самосборка `S(S_T)` остаётся хостовым гейтом.
- Неизвестный NID/опкод даёт `FATAL`, а не тихое пропускание. Нативная периферия, HAL физической памяти, реальные прерывания — шаги A4a/Ф3.

## Приёмка

`python -X utf8 Python_compiler/verify_native_rt.py` — автобилд в TEMP, дерево не засоряется.

Дополнительные гейты: `python -X utf8 Python_compiler/verify_boot_image.py` (A3b/A4a, образ в QEMU) и `python -X utf8 Python_compiler/verify_a5_install.py` (A5/A5b, самоустановка с двумя дисками и 7 подмен закрепления). Все три проходят на финальном коде; `python -X utf8 Python_compiler/regr120.py` зелёный.

| Случай | EVENT'ы VM/NAT | Опкоды/ячейки | Артефакт |
|---|---:|---:|---|
| `memmgr.ctos` | 13/13 | 1395 / 73 | — |
| `kernel_sched.ctos` | 12/12 | 132552 / 313 | — |
| `syscall_test.ctos` | 10/10 | 23 / 1 | 20 Б, md5 совпал |
| `schedF_test.ctos` | 44/44 | 15382 / 332 | — |
| `schedT_test.ctos` (1 тик) | 41/41 | 16434 / 443 | — |
| **полная самосборка S(S_T)** | **17295/17295** | **1348680 / 5657** | **13084 Б md5 `30a90f3ff440ec249a132f58ee5a040a` — IDENTICAL** |

Побайтовая сверка последовательностей `PORT` / `SYSCALL` / `TICK` / `NET` против трассы `ctos_vm.py --trace`, плюс счётчики, плюс байты артефакта. Честные негативы: `probe_seek` (FILE_SEEK до BEGIN), `neg_ctx1` (YIELD без аргумента), `syscall_test_endfail` (нет FILE_END), `syscall_test_orderfail` (FILE_PUT до BEGIN) — оба исполнителя отказываются с `rc=1` и одной диагностикой. CRC-негатив: порча байта тела ⇒ оба с `[TKT-040]` (`rc=1`).

## Сборка/запуск

```
gcc -O2 -std=c11 -Wall -Wextra -o CtOs/native/native_rt.exe CtOs/native/native_rt.c
CtOs/native/native_rt.exe CtOs/memmgr.ctos events.txt
CtOs/native/native_rt.exe Compiler/stage1_compiler.ctos events.txt Python_compiler/pos_wc14v3ring.words
python -X utf8 CtOs/native/build_modules_image.py /tmp/kernel.ctmd
CtOs/native/native_rt.exe --module memmgr /tmp/kernel.ctmd events.txt
python -X utf8 Python_compiler/verify_native_rt.py   # автобилд в TEMP, дерево не засоряется
python -X utf8 CtOs/native/boot/build_boot_image.py ctos_boot.img <TEMP>
python -X utf8 Python_compiler/verify_boot_image.py  # A3b + A4a в QEMU
python -X utf8 Python_compiler/verify_a5_install.py # A5/A5b: два диска в QEMU
```
