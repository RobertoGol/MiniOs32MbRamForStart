# A1/A2 — нативный интерпретатор (bring-up Ф2)

Статус: ✅ A1 и A2 приняты, 2026-11-18. Связано: `CtOs/BRINGUP_SPEC.md` (Ф2, вариант A), TKT-056 / TKT-055 / TKT-052.

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

## Честные границы (НЕ сделано)

- Boot shim под **legacy BIOS моноблока** (сырой MBR, real mode → защищённый режим, INT 13h, VGA text/COM1) / QEMU — нет. На R3700 только очень старый BIOS-аналог; UEFI/GRUB не подтверждены. QEMU в окружении отсутствует, поэтому «работает на железе» **не заявляется**. A1/A2 — хостовый нативный рантайм для сверки семантики.
- Неизвестный NID/опкод даёт `FATAL`, а не тихое пропускание. Нативная периферия, HAL физической памяти, реальные прерывания — шаги A3/Ф3.

## Приёмка

`python -X utf8 Python_compiler/verify_native_rt.py` — автобилд в TEMP, дерево не засоряется.

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
python -X utf8 Python_compiler/verify_native_rt.py   # автобилд в TEMP, дерево не засоряется
```
