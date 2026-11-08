#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ctos_vm.py — хост-исполнитель бинарников CtOs (.ctos), Этап 4.

Честная VM формата кодогенератора Стадии-0 (Python_compiler/codegen.py):
  Заголовок v1.0 (16 байт) / v1.1 (20 байт, TKT-040 веха-1):
    [0..4)  'CTOS'               магия
    [4..6)  версия (LE u16)      0x0100 (v1.0) / 0x0101 (v1.1, с контролем)
    [6..8)  цель (LE u16)        0x01 = ARM32, 0x02 = прочее
    [8..12) точка входа (LE u32) смещение в файле
    [12..16) магия-конец 0xAAAAFFFF
    v1.1: [16..20) контрольное слово тела (LE u32) — CRC-32 (zlib, честная
          открытая реализация stdlib) по всем байтам после заголовка;
          порча файлов ловится честным KERNEL PANIC на загрузке.
  Дальше — поток опкодов (формат аргументов смотри в __init__).

ЧЕСТНОЕ СЛОВО (B-13, 2026-11-01): память и арифметика стадии-0 — строго
32 бита. Результат `+`/`-` и любая запись в ячейку маскируются `& 0xFFFFFFFF`
(перенос за 32 бита теряется, как на настоящем железе); раньше VM могла
положить в ячейку 36-битное значение — нарушение контракта TKT-009.

Запуск:
    python ctos_vm.py <файл.ctos> [файл2.ctos ...] [--quiet]
      [--steps N]       честный лимит шагов VM (по умолчанию 10 млн)
      [--trace FILE]    честная трасса в файл (консоль остаётся чистой)
      [--source FILE]   честный поток исходника слово-языка стадии-1 для
                        сисколла FILE_GET 0x137 (самосборка, TKT-052 веха-2):
                        слова через пробел, максимум 2 символа ASCII на
                        слово ('5' -> 0x35, 'sv' -> 0x7673, где второй символ
                        в старшем байте); терминатор '.' дописывается честно;
                        СЛОВА В БУФЕР 0x00A00000 КЛАДЁТ САМ КОМПИЛЯТОР через
                        FILE_GET + store_ind (честная граница 16 слов —
                        MAX_SOURCE_WORDS, контракт TKT-009); без --source
                        поток честно пуст (первый FILE_GET = EOF)

Флаги честно совместимы со старым поведением: без флагов — как раньше.

Выход: код возврата 0 — все бинарники отработали до OP_TERM; 1 — сбой VM.
"""

import struct
import sys
import time
import zlib  # честная метка источника: CRC-32 из stdlib (open-source zlib)

HEADER_SIZE = 16   # наименьший честный заголовок (v1.0 legacy)
HEADER_SIZE_V11 = 20  # v1.1: + контрольное слово тела (TKT-040 веха-1)
VER_BASE  = 0x0100  # v1.0 — без контрольного слова (legacy, работает, честный лог)
VER_CHECK = 0x0101  # v1.1 — с контрольным словом, VM честно проверяет
MAGIC = b"CTOS"
TAIL_MAGIC = 0xAAAAFFFF

TARGETS = {0x01: "ARM32", 0x02: "X86_HOST"}

# Опкоды — ровно тот же словарь, что в Python_compiler/codegen.py (единый контракт).
OP_NOP       = 0x00
OP_INIT      = 0x01
OP_IMPORT    = 0x02
OP_CALL      = 0x03
OP_RET       = 0x04
OP_TERM      = 0x05
OP_ALLOC_ST  = 0x10
OP_STORE     = 0x11
OP_LOAD      = 0x12
OP_SYSCALL   = 0x13
OP_INCELL    = 0x50
OP_OUTCELL   = 0x51
OP_INCELL_IND = 0x52
OP_STORE_IND  = 0x53   # запись acc в cell[cell[arg]] — по адресу-указателю из ячейки
OP_OUTCELL_V  = 0x54
OP_STORE_AT  = 0x55   # запись acc в cell[arg] — честная память по адресу (TKT-050 веха-2)   # вывод ЗНАЧЕНИЯ ячейки (cell[arg]) в порт — честный log_cell
OP_ASMBLOCK  = 0x60
OP_JZ        = 0x06
OP_JMP       = 0x07
OP_STORE_A   = 0x14
OP_CONST     = 0x15   # «положить константу на акк» — эмитится как 0x15 + BE u32
NET_OPS = {
    0x20: "net_all", 0x21: "net_up", 0x22: "net_down",
    0x23: "net_flush", 0x24: "net_arp", 0x25: "go", 0x26: "trace",
}

C1 = ">I"  # сетевой порядок для адресов/значений в потоке


class VmFault(Exception):
    """Честный сбой VM: недокументированный opcode, обрыв потока и т.п."""


class CtOsVm:
    def __init__(self, binary, path, trace=True, clock_scale=1,
                 trace_file=None, max_steps=10_000_000, source_words=None):
        self.b = binary
        self.path = path
        self.trace = trace
        self.trace_file = trace_file  # честная трасса в файл (TKT-035), None = консоль
        self.max_steps = max_steps    # честный лимит шагов (TKT-035, дефолт 10 млн)
        self.cells = {}       # ячейки cell:raw: адрес -> значение
        self.static_set = {}  # статические ячейки компилятора (OP_ALLOC_ST)
        self.pc = None
        self.op_count = 0
        self._t0 = time.perf_counter()  # честная точка отсчёта лога: и до run() (TKT-052)
        self._acc = 0    # аккумулятор арифметики стадий-0
        self.rts = []    # стек возвратов для OP_CALL / OP_RET
        self.outfile = None    # честный файл-воркер (стадия-1.5, syscall-слой)
        self.outfile_n = 0     # честный счётчик записанных байт
        self.last_out = None   # честный след: последний вывод в порт (где брак, TKT-035)
        # честный поток исходника для FILE_GET (TKT-052 веха-2): список слов,
        # упакованных из текста инструментом; без --source честно пуст
        self.src_words = list(source_words) if source_words else []
        self.src_pos = 0       # честная позиция чтения потока исходника
        # честный контекст задач (TKT-055 спринт А, NID 0x150-0x152):
        # снимок состояния ЯДРА (планировщика) на момент RESTORE — точка возврата
        # для честного WORK_CTX_YIELD; None = ядерный контекст не установлен
        self.kernel_ctx = None
        # честный вытесняющий таймер (TKT-055 спринт Б, NID 0x153/0x154):
        # источник тиков — честный счётчик шагов VM (аналог аппаратного
        # таймера); механика тика в VM, политика планирования — в ядре
        self.tick_armed = False       # честный таймер заведён (TIMER_ARM)
        self.tick_quantum = 0         # честный интервал между тиками, в шагах
        self.tick_next = 0            # честный порог следующего тика (op_count)
        self.tick_trap_block = 0      # честный блок 'TCK1' для IRQ-кадра
        self.tick_trap_entry = 0      # честный вход обработчика тика в ядре
        self.tick_pending = False     # честный флаг: тик доставлен, TIMER_RET не было
        # честное окно статик-ячеек стадии-0 (TKT-055 спринт Б): общая память
        # "регистров" задач, объявляется ядром в блоке 'TMR1' (+4 base, +5 count).
        # Честный ABI: тик сохраняет окно в кадр 'TCK1', ядро переносит в
        # блок 'CTX1' (+166 count +167 base +170.. ячейки), RESTORE восстанавливает.
        # Без этого handler честно затирает общие ячейки прерванной задачи.
        self.tick_st_base = 0         # честная база окна статиков (VAR_ZONE)
        self.tick_st_count = 0        # честный размер окна (ячеек, 0 = нет статики)

    # ---------- лог ----------
    def log(self, line):
        if not self.trace:
            return
        stamped = "[%09.6f] %s" % ((time.perf_counter() - self._t0) * 1.0, line)
        if self.trace_file is not None:
            self.trace_file.write(stamped + "\n")
        else:
            print(stamped)

    # ---------- честный контекст задач: блок сохранения в ячейках (TKT-055) ----------
    # Раскладка блока по честному указателю (адрес из Stream_Emit):
    #   +0 magic +1 pc +2 acc +3 rts_len +4.. rts-слова.
    # rts хранится снизу вверх (как в списке VM) — порядок честно восстанавливается.
    WORK_CTX_MAGIC = 0x43545831   # 'CTX1' BE — блок контекста задачи
    TIMER_FRAME_MAGIC = 0x54434B31  # 'TCK1' BE — честный кадр тика (IRQ trap frame)
    WORK_CTX_RTS_MAX = 0x80       # честная глубина стека в блоке (128 слов)

    def _ctx_write(self, ptr, save_pc, magic):
        """Честный снимок контекста (pc+acc+rts) по указателю; magic выбирает
        смысл блока: 'CTX1' — контекст задачи, 'TCK1' — честный IRQ-кадр."""
        if len(self.rts) > self.WORK_CTX_RTS_MAX:
            raise VmFault("WORK_CTX: честный брак — глубина стека вызовов %d "
                          "сверх честного лимита %d (снимок перезаписал бы "
                          "соседние слова блока)"
                          % (len(self.rts), self.WORK_CTX_RTS_MAX))
        self.cells[ptr] = magic
        self.cells[ptr + 1] = save_pc & 0xFFFFFFFF
        self.cells[ptr + 2] = self._acc & 0xFFFFFFFF
        self.cells[ptr + 3] = len(self.rts) & 0xFFFFFFFF
        base = ptr + 4
        for i, ret in enumerate(self.rts):
            self.cells[base + i] = ret & 0xFFFFFFFF

    def _work_ctx_write(self, ptr, save_pc):
        self._ctx_write(ptr, save_pc, self.WORK_CTX_MAGIC)

    def _ctx_read(self, ptr, magic):
        found = self.cells.get(ptr, 0) & 0xFFFFFFFF
        if found != magic:
            raise VmFault("WORK_CTX: честный брак — блок 0x%08X имеет магию "
                          "0x%08X, а ожидалась %s (контекст не инициализирован "
                          "/ испорчен)" % (ptr, found,
                                           "'CTX1'" if magic == self.WORK_CTX_MAGIC
                                           else "'TCK1'"))
        save_pc = self.cells.get(ptr + 1, 0) & 0xFFFFFFFF
        acc = self.cells.get(ptr + 2, 0) & 0xFFFFFFFF
        rts_len = self.cells.get(ptr + 3, 0) & 0xFFFFFFFF
        if rts_len > self.WORK_CTX_RTS_MAX:
            raise VmFault("WORK_CTX: честный брак — rts_len %d сверх лимита %d "
                          "(контекст вне честного блока ячеек)"
                          % (rts_len, self.WORK_CTX_RTS_MAX))
        if save_pc < self.pc_entry or save_pc >= len(self.b):
            raise VmFault("WORK_CTX: честный брак — pc 0x%08X вне потока опкодов"
                          % save_pc)
        base = ptr + 4
        rts = []
        for i in range(rts_len):
            rts.append(self.cells.get(base + i, 0) & 0xFFFFFFFF)
        return save_pc, acc, rts

    def _work_ctx_read(self, ptr):
        return self._ctx_read(ptr, self.WORK_CTX_MAGIC)

    # ---------- честное окно статик-ячеек (TKT-055 спринт Б) ----------
    # Стадия-0 держит "регистры" задач в ОБЩИХ ячейках (VAR_ZONE..): обработчик
    # тика и ядро честно их затирают. Честный ABI callee-saved: окно (base/count
    # из блока 'TMR1' +4/+5) снимается в блок формата:
    #   [off] count, [off+1] base, [off+4 .. off+3+count] ячейки окна;
    # для кадра 'TCK1' off=132 (после rts-части 4..131): +132 count, +133 base,
    # +134/135 резерв, ячейки окна честно с +136; для 'CTX1' off=166
    # (meta: +160..165 заняты, ячейки окна честно в 170.. до 255).
    STATICS_COUNT_MAX = 0x50      # честный лимит окна (80 ячеек, влезает в ctx)
    # Честная зона статиков стадии-0 — обязана соответствовать VAR_ZONE кодгена
    # (Python_compiler/codegen.py: единая раскладка ячеек бирепозитория).
    STATIC_ZONE = 0x00F00000

    def _statics_save(self, ptr, off):
        """Честный снимок окна статиков в блок по указателю (armed-режим)."""
        n = self.tick_st_count
        if not n:
            return
        self.cells[ptr + off] = n & 0xFFFFFFFF
        self.cells[ptr + off + 1] = self.tick_st_base & 0xFFFFFFFF
        for i in range(n):
            v = self.cells.get(self.tick_st_base + i * 4, 0) & 0xFFFFFFFF
            self.cells[ptr + off + 4 + i] = v
        self.log("SCHED-STSAVE: честный снимок окна -> блок 0x%08X off=%d "
                 "(n=%d, base=0x%08X) окна: %s"
                 % (ptr, off, n, self.tick_st_base,
                    " ".join("%08X" % (self.cells.get(
                        ptr + off + 4 + i, 0) & 0xFFFFFFFF)
                        for i in range(n))))

    def _statics_load(self, ptr, off):
        """Честное восстановление окна статиков из блока; честный брак —
        count сверх лимита или base без count."""
        n = self.cells.get(ptr + off, 0) & 0xFFFFFFFF
        if not n:
            return
        if n > self.STATICS_COUNT_MAX:
            raise VmFault("статик-окно: честный брак — count %d сверх честного "
                          "лимита %d (блок 0x%08X испорчен/подменён)"
                          % (n, self.STATICS_COUNT_MAX, ptr))
        base = self.cells.get(ptr + off + 1, 0) & 0xFFFFFFFF
        if not base:
            raise VmFault("статик-окно: честный брак — count %d без базы "
                          "(блок 0x%08X испорчен/подменён)" % (n, ptr))
        for i in range(n):
            self.cells[base + i * 4] = self.cells.get(
                ptr + off + 4 + i, 0) & 0xFFFFFFFF

    def _timer_tick(self, at_pc):
        """Честная механика IRQ-тика (спринт Б): сохранить кадр прерванной
        задачи в блок 'TCK1' и прыгнуть на вход обработчика ядра. Выбор задач
        и возврат (TIMER_RET или RESTORE) — честно в коде ядра."""
        if self.tick_pending:
            raise VmFault("честный тик: предыдущий тик не завершён "
                          "(нет TIMER_RET) — nested IRQ не является частью "
                          "честного контракта спринта Б")
        self.tick_pending = True
        self._ctx_write(self.tick_trap_block, at_pc, self.TIMER_FRAME_MAGIC)
        self._statics_save(self.tick_trap_block, 132)
        self.pc = self.jump_target(self.tick_trap_entry)
        self.log("SCHED-TICK: честный IRQ-тик: кадр задачи -> блок 0x%08X "
                 "(pc=0x%08X, rts=%d, st=%d), вход в обработчик ядра pc=0x%08X "
                 "окно: %s"
                 % (self.tick_trap_block, at_pc, len(self.rts),
                    self.tick_st_count, self.pc,
                    " ".join("%08X" % (self.cells.get(
                        self.tick_st_base + i * 4, 0) & 0xFFFFFFFF)
                        for i in range(self.tick_st_count))))

    # ---------- разбор заголовка ----------
    def read_header(self):
        if len(self.b) < HEADER_SIZE:
            raise VmFault("файл меньше 16 байт — не может быть CTOS-бинарником")
        if self.b[:4] != MAGIC:
            raise VmFault("нет магии 'CTOS' в начале файла — это не бинарь CtOs")
        ver, target_id = struct.unpack_from("<HH", self.b, 4)
        entry, tail = struct.unpack_from("<II", self.b, 8)
        if tail != TAIL_MAGIC:
            raise VmFault("хвостовая магия заголовка испорчена: 0x%08X" % tail)
        if ver == VER_CHECK:
            # честное Контрольное слово тела (TKT-040 веха-1, контракт v1.1)
            if len(self.b) < HEADER_SIZE_V11:
                raise VmFault("файл заявлен как v1.1 (с контролем), но меньше "
                              "%d байт — не может быть CTOS-бинарником" % HEADER_SIZE_V11)
            stored = struct.unpack_from("<I", self.b, 16)[0]
            real = zlib.crc32(self.b[HEADER_SIZE_V11:]) & 0xFFFFFFFF
            if stored != real:
                raise VmFault("[TKT-040] честный брак целостности: контрольное "
                              "слово в файле 0x%08X, а честный CRC-32 тела "
                              "0x%08X — бинарь подменён/испорчен" % (stored, real))
            self.log("целостность: контрольное слово 0x%08X сошлось (CRC-32 тела, "
                     "байт %d)" % (stored, len(self.b) - HEADER_SIZE_V11))
        else:
            self.log("заголовок v1.0 (legacy): контрольного слова нет — "
                     "проверка целостности не производилась")
        if entry < HEADER_SIZE or entry >= len(self.b):
            raise VmFault("точка входа %d вне файла (0..%d): пустой поток опкодов "
                          "или бинарь без кода — честный брак" % (entry, len(self.b)))
        self.pc_entry = entry
        self.log("заголовок: v%d.%d, цель %s, вход 0x%08X" %
                 ((ver >> 8) & 0xFF, ver & 0xFF,
                  TARGETS.get(target_id, "0x%04X" % target_id), entry))
        self.pc = entry

    # ---------- шаг VM ----------
    def jump_target(self, addr):
        """Честная проверка адреса перехода: строго внутрь потока опкодов."""
        if addr <= self.pc_entry or addr >= len(self.b):
            raise VmFault("переход по адресу 0x%08X вне потока опкодов "
                          "(файл 0x%08X байт)" % (addr, len(self.b)))
        return addr

    def step(self):
        """Исполняет один опкод; возвращает False, когда поток закончен (OP_TERM/RET)."""
        b = self.b
        pc = self.pc
        if pc >= len(b):
            # честная страховка на границе: после честного байта опкодов
            # осуществление по формуле OP_TERM уже вернуло False; сюда попадаем
            # только на битом бинаре (jump обошёл TERM) или пустом потоке.
            raise VmFault("честная граница: поток опкодов кончился на смещении "
                          "0x%08X (файл 0x%08X байт) — OP_TERM не встретился"
                          % (pc, len(b)))
        op = b[pc]

        # честный IRQ-тик (TKT-055 спринт Б): доставляется МЕЖДУ инструкциями
        # (текущий pc ещё не исполнен), только после первого RESTORE эпохи
        # (kernel_ctx установлен = исполняется задача; ядерный код честно
        # без тика); счётчик шагов VM = честный аналог аппаратного таймера.
        if (self.tick_armed and self.kernel_ctx is not None
                and self.op_count >= self.tick_next
                and not self.tick_pending):
            self._timer_tick(pc)
            self.tick_next = self.op_count + self.tick_quantum
            return True   # честный тик занимает шаг VM (честная накладка IRQ)
        self.op_count += 1

        # 1) тривиальные без аргументов
        if op == OP_NOP:
            self.pc = pc + 1
        elif op == OP_INIT:
            self.log("OP_INIT: инициализация модуля")
            self.pc = pc + 1
        elif op == OP_ALLOC_ST:
            # TKT-047: стадия-1 эмитит 'se'/'st' как голый 0x10 (без операнда) —
            # связь имени статики с ячейкой живёт на стороне стадии-1;
            # на исполнении это честный маркер объявления: поток идёт дальше,
            # статики этапа компиляции не создаются молча (лог виден).
            self.log("OP_ALLOC_ST: объявление статики (стадия-1, без операнда)")
            self.pc = pc + 1
        elif op in (OP_JZ, OP_JMP):
            if pc + 5 > len(b):
                raise VmFault("переходной опкод обрезан в конце файла")
            target = struct.unpack_from(C1, b, pc + 1)[0]
            if op == OP_JZ and self._acc != 0:
                self.log("OP_JZ: acc=%d — условие ложно не сработало, идём дальше"
                         % self._acc)
                self.pc = pc + 5
            else:
                self.log("%s: [%s] -> 0x%08X"
                         % ("OP_JZ" if op == OP_JZ else "OP_JMP", "acc=0" if op == OP_JZ else "всегда", target))
                self.pc = self.jump_target(target)
        elif op == OP_TERM:
            self.log("OP_TERM: завершение контекста, зачистка ячеек стека")
            return False
        elif op == OP_RET:
            if not self.rts:
                raise VmFault("OP_RET: возврат вне вызова функции — "
                              "стек вызовов пуст в точке 0x%08X" % pc)
            self.pc = self.rts.pop()
            self.log("OP_RET: возврат из функции, pc = 0x%08X" % self.pc)
        elif op in NET_OPS:
            self.log("сеть: %s" % NET_OPS[op])
            self.pc = pc + 1

        # 2) константа и работа с ячейками
        elif op == OP_CONST:
            if pc + 5 > len(b):
                raise VmFault("OP_CONST обрезан в конце файла")
            val = struct.unpack_from(C1, b, pc + 1)[0]
            self._acc = val
            self.log("OP_CONST: acc = 0x%08X" % val)
            self.pc = pc + 5
        elif op == OP_STORE:
            # Честно: стадия-0 пока не кодирует целевой адрес переменной,
            # поэтому «ячейка» временно адресуется смещением опкода в файле.
            # Когда стадия-0 начнёт писать адрес (OP_ALLOC_ST + привязка),
            # эта строка будет читать по настоящему адресу из компилятора.
            self.cells[pc] = getattr(self, "_acc", 0) & 0xFFFFFFFF
            self.log("OP_STORE: acc -> ячейка@0x%08X (стадия-0: адрес-заглушка)"
                     % pc)
            self.pc = pc + 1
        elif op == OP_LOAD:
            if pc + 6 > len(b):
                raise VmFault("OP_LOAD обрезан в конце файла")
            mode, arg = b[pc + 1], struct.unpack_from(C1, b, pc + 2)[0]
            if mode == 0x14:      # склейка «прибавить»
                self._acc = (getattr(self, "_acc", 0) + arg) & 0xFFFFFFFF
            elif mode == 0x15:    # прибавить ЗНАЧЕНИЕ ячейки: acc += cell[arg]
                self._acc = (getattr(self, "_acc", 0) + self.cells.get(arg, 0)) & 0xFFFFFFFF
            elif mode == 0x17:    # честное вычитание константы
                self._acc = (getattr(self, "_acc", 0) - arg) & 0xFFFFFFFF
            elif mode == 0x16:    # сравнение «равно?»
                self._acc = 1 if getattr(self, "_acc", 0) == arg else 0
            elif mode == 0x18:    # сравнение с ЯЧЕЙКОЙ: acc = (acc == cell[arg])
                self._acc = 1 if getattr(self, "_acc", 0) == self.cells.get(arg, 0) else 0
            elif mode == 0x19:    # честная загрузка ЯЧЕЙКИ: acc = cell[arg] (TKT-050 веха-2)
                self._acc = self.cells.get(arg, 0)
            elif mode == 0x1A:    # честное сравнение «больше»: acc = (acc > arg) (TKT-050 веха-3)
                self._acc = 1 if getattr(self, "_acc", 0) > arg else 0
            elif mode == 0x1B:    # честное сравнение «меньше»: acc = (acc < arg) (TKT-050 веха-3)
                self._acc = 1 if getattr(self, "_acc", 0) < arg else 0
            else:
                raise VmFault("OP_LOAD: недокументированный режим 0x%02X" % mode)
            self.log("OP_LOAD[0x%02X]: acc = 0x%08X" % (mode, self._acc))
            self.pc = pc + 6
        elif op == OP_INCELL:
            if pc + 5 > len(b):
                raise VmFault("OP_INCELL обрезан в конце файла")
            addr = struct.unpack_from(C1, b, pc + 1)[0]
            self._acc = self.cells.get(addr, 0)
            self.log("OP_INCELL: acc = cell[0x%08X] = 0x%08X" % (addr, self._acc))
            self.pc = pc + 5
        elif op == OP_OUTCELL:
            if pc + 9 > len(b):
                raise VmFault("OP_OUTCELL обрезан в конце файла")
            port = struct.unpack_from(C1, b, pc + 1)[0]
            val = struct.unpack_from(C1, b, pc + 5)[0]
            self.cells[port] = val & 0xFFFFFFFF
            self.last_out = (self.pc, "OP_OUTCELL", port, val)
            self.log("OP_OUTCELL: порт 0x%08X <- 0x%08X" % (port, val))
            self.pc = pc + 9

        # 3) вызовы, syscall, ассемблерный блок
        elif op == OP_CALL:
            if pc + 5 > len(b):
                raise VmFault("OP_CALL обрезан в конце файла")
            addr = struct.unpack_from(C1, b, pc + 1)[0]
            if addr == 0:
                self.log("OP_CALL: адрес 0 — старые бинари стадий-0 без таблицы "
                         "вызовов, пропускаю")
                self.pc = pc + 5
            else:
                self.rts.append(pc + 5)
                self.log("OP_CALL: стек возврата <- 0x%08X, вход в 0x%08X"
                         % (pc + 5, addr))
                self.pc = self.jump_target(addr)
        elif op == OP_SYSCALL:
            if pc + 5 > len(b):
                raise VmFault("OP_SYSCALL обрезан в конце файла")
            nid = struct.unpack_from(C1, b, pc + 1)[0]
            stream_cell = 0x00F00FF0  # честная ячейка-аргумент syscall (Stream_Emit)
            # честный флаг: контекстные NID (0x150-0x152) сами выставляют pc,
            # общий хвост pc+5 применяется только к syscall без переключения
            ctx_jump = False
            if nid == 0x00000130:     # FILE_BEGIN — честный файл-воркер: открыть артефакт
                if self.outfile is not None:
                    raise VmFault("FILE_BEGIN: честный артефакт уже открыт")
                self.outfile = open(self.path + ".out", "w+b")
                self.outfile_n = 0
                self.log("OP_SYSCALL[FILE_BEGIN]: честный артефакт открыт")
            elif nid == 0x00000131:   # FILE_PUT — честное слово из Stream_Emit → 4 байта BE
                if self.outfile is None:
                    raise VmFault("FILE_PUT до FILE_BEGIN — честный брак порядка syscall")
                val = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                self.outfile.write(struct.pack(C1, val))
                self.outfile_n += 4
                self.log("OP_SYSCALL[FILE_PUT]: честное слово 0x%08X -> 4 байта BE (всего %d)"
                         % (val, self.outfile_n))
            elif nid == 0x00000132:   # FILE_U16 — честные младшие 16 бит → 2 байта BE
                if self.outfile is None:
                    raise VmFault("FILE_U16 до FILE_BEGIN — честный брак порядка syscall")
                val = self.cells.get(stream_cell, 0) & 0xFFFF
                self.outfile.write(struct.pack(">H", val))
                self.outfile_n += 2
                self.log("OP_SYSCALL[FILE_U16]: честные 16 бит 0x%04X -> 2 байта BE (всего %d)"
                         % (val, self.outfile_n))
            elif nid == 0x00000133:   # FILE_END — честное закрытие артефакта
                if self.outfile is None:
                    raise VmFault("FILE_END без FILE_BEGIN — честный брак порядка syscall")
                self.outfile.close()
                self.outfile = None
                self.log("OP_SYSCALL[FILE_END]: честный артефакт закрыт (%d байт)"
                         % self.outfile_n)
            elif nid == 0x00000134:   # FILE_U8 — честный байт → 1 байт (TKT-047)
                if self.outfile is None:
                    raise VmFault("FILE_U8 до FILE_BEGIN — честный брак порядка syscall")
                val = self.cells.get(stream_cell, 0) & 0xFF
                self.outfile.write(struct.pack(">B", val))
                self.outfile_n += 1
                self.log("OP_SYSCALL[FILE_U8]: честный байт 0x%02X -> 1 байт (всего %d)"
                         % (val, self.outfile_n))
            elif nid == 0x00000135:   # FILE_SEAL — честное контрольное слово артефакта (TKT-040)
                if self.outfile is None:
                    raise VmFault("FILE_SEAL до FILE_BEGIN — честный брак порядка syscall")
                self.outfile.flush()
                self.outfile.seek(0)
                blob = self.outfile.read()
                if len(blob) < HEADER_SIZE_V11:
                    raise VmFault("FILE_SEAL: в артефакте меньше %d байт — честное "
                                  "контрольное слово некуда вписывать" % HEADER_SIZE_V11)
                crc = zlib.crc32(blob[HEADER_SIZE_V11:]) & 0xFFFFFFFF
                self.outfile.seek(16)
                self.outfile.write(struct.pack("<I", crc))
                self.outfile.seek(0, 2)   # честный хвост: продолжаем писать в конец
                self.log("OP_SYSCALL[FILE_SEAL]: контрольное слово артефакта 0x%08X "
                         "(CRC-32 тела, байт %d)" % (crc, len(blob) - HEADER_SIZE_V11))
            elif nid == 0x00000136:   # FILE_SEEK — честная позиция записи в артефакте (TKT-048)
                if self.outfile is None:
                    raise VmFault("FILE_SEEK до FILE_BEGIN — честный брак порядка syscall")
                pos = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                # честная граница: проверяется ОЧНО по факту Ok записи ниже
                # (запись за конец файла поднять честный IOError, не тишину —
                # обёртка честного OSError даст [VM ERROR])
                try:
                    self.outfile.flush()
                    self.outfile.seek(pos)
                except OSError as exc:
                    raise VmFault("FILE_SEEK: честная позиция 0x%08X вне артефакта — "
                                  "честный брак (%s)" % (pos, exc))
                self.log("OP_SYSCALL[FILE_SEEK]: честная позиция записи 0x%08X" % pos)
            elif nid == 0x00000137:   # FILE_GET — честное чтение слова исходника
                # (TKT-052 веха-2): 4 байта BE из потока исходника -> ячейка
                # Stream_Emit 0x00F00FF0; статус конца — в File_Eof 0x00F00FF2
                # (0 = слово есть, 1 = честный конец). Без --source поток
                # честно пуст: первый же FILE_GET даст EOF, тишины нет.
                if self.src_pos < len(self.src_words):
                    val = self.src_words[self.src_pos] & 0xFFFFFFFF
                    self.src_pos += 1
                    self.cells[stream_cell] = val
                    self.cells[0x00F00FF2] = 0
                    self.log("OP_SYSCALL[FILE_GET]: честное слово 0x%08X <- "
                             "исходник (%d из %d)" % (val, self.src_pos,
                                                      len(self.src_words)))
                else:
                    self.cells[0x00F00FF2] = 1
                    self.log("OP_SYSCALL[FILE_GET]: честный конец исходника (EOF)")
            elif nid == 0x00000150:   # WORK_CTX_SAVE — сохранить контекст (TKT-055)
                # Аргумент — АДРЕС блока контекста через Stream_Emit (0x00F00FF0).
                # Сохраняются pc (после syscall), acc и стек rts. Состояние VM
                # не меняется — SAVE это честный снимок.
                ptr = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                if ptr == 0:
                    raise VmFault("WORK_CTX_SAVE: честный брак — нет открытого "
                                  "протокола аргумента (Stream_Emit пуст)")
                self._work_ctx_write(ptr, pc + 5)
                self._statics_save(ptr, 166)
                self.log("OP_SYSCALL[WORK_CTX_SAVE]: контекст -> блок 0x%08X "
                         "(pc=0x%08X, acc, rts=%d)" % (ptr, pc + 5, len(self.rts)))
            elif nid == 0x00000151:   # WORK_CTX_RESTORE — загрузить контекст и продолжить
                ptr = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                if ptr == 0:
                    raise VmFault("WORK_CTX_RESTORE: честный брак — нет открытого "
                                  "протокола аргумента (Stream_Emit пуст)")
                new_pc, new_acc, new_rts = self._work_ctx_read(ptr)
                # честная переустановка ядерного контекста КАЖДУЮ эпоху: RESTORE
                # всегда фиксирует точку планировщика после syscall как честную
                # точку возврата WORK_CTX_YIELD (per-epoch контракт TKT-055)
                self.kernel_ctx = (pc + 5,
                                   self._acc & 0xFFFFFFFF,
                                   list(self.rts))
                self.rts = new_rts
                self._acc = new_acc
                self.pc = self.jump_target(new_pc)
                self._statics_load(ptr, 166)
                ctx_jump = True
                self.log("OP_SYSCALL[WORK_CTX_RESTORE]: переключение c блока 0x%08X "
                         "-> pc=0x%08X (rts=%d, st=%d, ядерный контекст переустановлен)"
                         % (ptr, self.pc, len(self.rts),
                            self.cells.get(ptr + 166, 0) & 0xFFFFFFFF))
            elif nid == 0x00000152:   # WORK_CTX_YIELD — вернуть управление ядру (TKT-055)
                ptr = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                if ptr == 0:
                    raise VmFault("WORK_CTX_YIELD: честный брак — нет открытого "
                                  "протокола аргумента (Stream_Emit пуст)")
                if self.kernel_ctx is None:
                    # честный первый вход из свежего OP_CALL-старта задачи:
                    # контекст задачи сохраняется ПОЛНОСТЬЮ (включая кадр вызова),
                    # а кадр снимается — возврат в точку после run-вызова ядра
                    self._work_ctx_write(ptr, pc + 5)
                    self._statics_save(ptr, 166)
                    ret_pc = self.rts.pop()
                    self._acc = 0
                    self.pc = self.jump_target(ret_pc)
                    ctx_jump = True
                    self.log("OP_SYSCALL[WORK_CTX_YIELD]: свежая задача -> блок "
                             "0x%08X, возврат в точку вызова ядра pc=0x%08X"
                             % (ptr, self.pc))
                else:
                    old_pc, old_acc, old_rts = self.kernel_ctx
                    self.kernel_ctx = None
                    self._work_ctx_write(ptr, pc + 5)
                    self._statics_save(ptr, 166)
                    self.rts = old_rts
                    self._acc = old_acc
                    self.pc = self.jump_target(old_pc)
                    ctx_jump = True
                    self.log("OP_SYSCALL[WORK_CTX_YIELD]: задача -> блок 0x%08X, "
                             "возврат в ядро pc=0x%08X" % (ptr, self.pc))
            elif nid == 0x00000153:   # TIMER_ARM — честный вытесняющий таймер (спринт Б)
                # Аргумент-блок через Stream_Emit ('TMR1'):
                #   +0 magic 'TMR1' 0x544D5231, +1 квант (шаги VM между тиками),
                #   +2 trap-блок 'TCK1' (кадр прерванной задачи),
                #   +3 trap_entry (адрес входа обработчика тика в ядре).
                # Механика тика в VM, политика планирования — честно в ядре.
                ptr = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                if ptr == 0:
                    raise VmFault("TIMER_ARM: честный брак — нет открытого "
                                  "протокола аргумента (Stream_Emit пуст)")
                if self.cells.get(ptr, 0) & 0xFFFFFFFF != 0x544D5231:
                    raise VmFault("TIMER_ARM: честный брак — блок 0x%08X не имеет "
                                  "магии 'TMR1'" % ptr)
                quant = self.cells.get(ptr + 1, 0) & 0xFFFFFFFF
                trap_block = self.cells.get(ptr + 2, 0) & 0xFFFFFFFF
                trap_entry = self.cells.get(ptr + 3, 0) & 0xFFFFFFFF
                st_base = self.cells.get(ptr + 4, 0) & 0xFFFFFFFF
                st_count = self.cells.get(ptr + 5, 0) & 0xFFFFFFFF
                if quant == 0:
                    raise VmFault("TIMER_ARM: честный брак — квант 0 "
                                  "(таймер без интервала)")
                if trap_block == 0:
                    raise VmFault("TIMER_ARM: честный брак — trap-блок не указан")
                if st_count and st_base != self.STATIC_ZONE:
                    raise VmFault("TIMER_ARM: честный брак — база статик-окна "
                                  "0x%08X вне честной зоны статиков "
                                  "STATIC_ZONE (0x%08X)" % (st_base, self.STATIC_ZONE))
                if st_count > self.STATICS_COUNT_MAX:
                    raise VmFault("TIMER_ARM: честный брак — окно статиков %d "
                                  "сверх честного лимита %d"
                                  % (st_count, self.STATICS_COUNT_MAX))
                if st_count:
                    st_hi = st_base + st_count * 4
                    tb_hi = trap_block + 136 + st_count
                    if st_base < tb_hi and trap_block < st_hi:
                        raise VmFault("TIMER_ARM: честный брак — окно статики "
                                      "[0x%08X..0x%08X) перекрывает trap-блок "
                                      "[0x%08X..0x%08X)"
                                      % (st_base, st_hi, trap_block, tb_hi))
                self.jump_target(trap_entry)   # честная проверка входа обработчика
                if self.tick_pending:
                    raise VmFault("TIMER_ARM: честный брак — тик ещё не завершён "
                                  "(нет TIMER_RET), перевзвод запрещён")
                self.tick_armed = True
                self.tick_quantum = quant
                self.tick_next = self.op_count + quant
                self.tick_trap_block = trap_block
                self.tick_trap_entry = trap_entry
                self.tick_st_base = st_base
                self.tick_st_count = st_count
                self.log("OP_SYSCALL[TIMER_ARM]: честный таймер заведён "
                         "(квант %d шагов VM, trap-блок 0x%08X, обработчик "
                         "0x%08X, статик-окно base=0x%08X count=%d)"
                         % (quant, trap_block, trap_entry, st_base, st_count))
            elif nid == 0x00000154:   # TIMER_RET — честный IRET из обработчика тика
                ptr = self.cells.get(stream_cell, 0) & 0xFFFFFFFF
                if not self.tick_pending:
                    raise VmFault("TIMER_RET: честный брак — открытого тика нет "
                                  "(соответствует IRET без IRQ)")
                if ptr == 0:
                    raise VmFault("TIMER_RET: честный брак — нет открытого "
                                  "протокола аргумента (Stream_Emit пуст)")
                new_pc, new_acc, new_rts = self._ctx_read(
                    ptr, self.TIMER_FRAME_MAGIC)
                self._acc = new_acc
                self.rts = new_rts
                self.pc = self.jump_target(new_pc)
                self._statics_load(ptr, 132)
                self.tick_pending = False
                ctx_jump = True
                self.log("OP_SYSCALL[TIMER_RET]: честный IRET: возобновление "
                         "прерванной задачи pc=0x%08X (rts=%d)"
                         % (self.pc, len(self.rts)))
            else:
                raise VmFault("OP_SYSCALL: NID 0x%08X — честный драйвер не зарегистрирован "
                              "(файл-слой зарегистрирован: NID 0x00000130..0x00000137, "
                              "контекстный слой: NID 0x00000150..0x00000152)" % nid)
            if not ctx_jump:
                self.pc = pc + 5
        elif op == OP_STORE_A:
            if pc + 5 > len(b):
                raise VmFault("OP_STORE_A обрезан в конце файла")
            addr = struct.unpack_from(C1, b, pc + 1)[0]
            self.cells[addr] = self._acc & 0xFFFFFFFF
            self.log("OP_STORE_A: cell[0x%08X] = 0x%08X" % (addr, self._acc))
            self.pc = pc + 5
        elif op == OP_INCELL_IND:
            if pc + 5 > len(b):
                raise VmFault("OP_INCELL_IND обрезан в конце файла")
            holder = struct.unpack_from(C1, b, pc + 1)[0]
            addr = self.cells.get(holder, 0)
            self._acc = self.cells.get(addr, 0)
            self.log("OP_INCELL_IND: acc = cell[cell[0x%08X]=0x%08X] = 0x%08X"
                     % (holder, addr, self._acc))
            self.pc = pc + 5
        elif op == OP_STORE_IND:
            if pc + 5 > len(b):
                raise VmFault("OP_STORE_IND обрезан в конце файла")
            holder = struct.unpack_from(C1, b, pc + 1)[0]
            addr = self.cells.get(holder, 0)
            # честная защита: запись по адресу ноль — подмена мастер-ячейки
            if addr == 0:
                raise VmFault("OP_STORE_IND: запись по адресу 0 из ячейки "
                              "0x%08X — указатель не инициализирован" % holder)
            self.cells[addr] = self._acc & 0xFFFFFFFF
            self.log("OP_STORE_IND: cell[cell[0x%08X]=0x%08X] = 0x%08X"
                     % (holder, addr, self._acc))
            self.pc = pc + 5
        elif op == OP_OUTCELL_V:
            if pc + 9 > len(b):
                raise VmFault("OP_OUTCELL_V обрезан в конце файла")
            port = struct.unpack_from(C1, b, pc + 1)[0]
            var_addr = struct.unpack_from(C1, b, pc + 5)[0]
            val = self.cells.get(var_addr, 0)
            self.cells[port] = val & 0xFFFFFFFF
            self.last_out = (pc, "OP_OUTCELL_V", port, val)
            self.log("OP_OUTCELL_V: порт 0x%08X <- cell[0x%08X] = 0x%08X"
                     % (port, var_addr, val))
            self.pc = pc + 9
        elif op == OP_STORE_AT:
            # TKT-050 веха-2: честная память стадии-1 — cell[arg] = acc,
            # адрес берётся из честного операнда BE32 (не заглушка pc)
            if pc + 5 > len(b):
                raise VmFault("OP_STORE_AT обрезан в конце файла")
            arg = struct.unpack_from(C1, b, pc + 1)[0]
            self.cells[arg] = getattr(self, "_acc", 0) & 0xFFFFFFFF
            self.log("OP_STORE_AT: cell[0x%08X] <- acc = 0x%08X"
                     % (arg, self._acc))
            self.pc = pc + 5
        elif op == OP_ASMBLOCK:
            if pc + 5 > len(b):
                raise VmFault("OP_ASMBLOCK обрезан в конце файла")
            ln = struct.unpack_from("<I", self.b, pc + 1)[0]
            if pc + 5 + ln > len(b):
                raise VmFault("OP_ASMBLOCK: длина %d выходит за файл" % ln)
            code = b[pc + 5: pc + 5 + ln]
            self.log("OP_ASMBLOCK (%d байт): %s" % (ln, code.decode("utf-8", "replace")))
            self.pc = pc + 5 + ln

        else:
            dump = " ".join("%02X" % x for x in b[pc:pc + 8])
            raise VmFault("недокументированный опкод 0x%02X на смещении 0x%08X (байты: %s)"
                          % (op, pc, dump))

        # честная страховка от бесконечного потока
        if self.pc >= len(b):
            raise VmFault("поток опкодов кончился раньше OP_TERM — бинарь усечён")
        return True

    def run(self):
        self._t0 = time.perf_counter()
        self.log("CtOs VM: запуск '%s'" % self.path)
        self.read_header()
        self._acc = 0
        while self.step():
            # честный предохранитель от неконечного цикла в бинаре
            # (лимит честно настраиваемый: --steps, дефолт 10 млн — TKT-035)
            if self.op_count > self.max_steps:
                raise VmFault("VM крутится дольше %d опкодов (фактически "
                              "исполнено %d, наступило на шаге pc=0x%08X) — "
                              "бинарь испорчен (нет OP_TERM/OP_RET)"
                              % (self.max_steps, self.op_count, self.pc))
        # честная страховка 1.5: артефакт остался открытым — FILE_END не был вызван
        if self.outfile is not None:
            raise VmFault("честный артефакт не закрыт — FILE_END не вызвался "
                          "(бинарь честно бракован: файл-вывод оборван)")
        return 0


def honest_flags(args_in):
    """Честный разбор флагов VM (TKT-035) в argparse-стиле; поведение без
    флагов честно прежнее — бэккомпат."""
    quiet = False
    steps = 10_000_000
    trace_path = None
    source_path = None
    files = []
    i = 0
    while i < len(args_in):
        a = args_in[i]
        if a == "--quiet":
            quiet = True
        elif a == "--steps":
            i += 1
            if i >= len(args_in):
                raise SystemExit("[VM FLAGS]: --steps требует честное число "
                                 "шагов (например --steps 500000)")
            try:
                steps = int(args_in[i])
            except ValueError:
                raise SystemExit("[VM FLAGS]: --steps: '%s' не число "
                                 "(честный лимит шагов)" % args_in[i])
            if steps <= 0:
                raise SystemExit("[VM FLAGS]: --steps должен быть > 0 "
                                 "(честно)")
        elif a == "--trace":
            i += 1
            if i >= len(args_in):
                raise SystemExit("[VM FLAGS]: --trace требует честный путь "
                                 "к файлу трассы (например --trace out.log)")
            trace_path = args_in[i]
        elif a == "--source":
            i += 1
            if i >= len(args_in):
                raise SystemExit("[VM FLAGS]: --source требует честный путь "
                                 "к файлу исходника слово-языка (TKT-052)")
            source_path = args_in[i]
        elif a.startswith("--"):
            raise SystemExit("[VM FLAGS]: неизвестный флаг '%s' (честные "
                             "флаги VM: --quiet / --steps N / --trace FILE / "
                             "--source FILE)" % a)
        else:
            files.append(a)
        i += 1
    if quiet and trace_path is not None:
        raise SystemExit("[VM FLAGS]: конфликт честных флагов: --quiet глушит "
                         "трассу, а --trace FILE её пишет; выбери один")
    return quiet, steps, trace_path, source_path, files


# ---------- честный поток исходника для FILE_GET (TKT-052 веха-2) ----------
# Границу длины (MAX_SOURCE_WORDS = 16 слов) честно держит сам компилятор
# (брак BRK_SRC_OVERFLOW в отчёте артефакта) — инструмент только упаковывает.


def build_source_words(path):
    """Честная упаковка текстового исходника в поток слов для FILE_GET
    (TKT-052 веха-2; в вехе-1 --source прекэргружал ячейки буфера — с вехи-2
    честно кормит сисколл чтения, а слова в буфер кладёт САМ компилятор).

    Текст = слова через пробел; слово максимум 2 символа ASCII:
      1 символ  -> слово = ord(c)                ('5' -> 0x35, '.' -> 0x2E)
      2 символа -> слово = ord(c1) | ord(c2)<<8  ('sv' -> 0x7673: второй
                   символ честно в старшем байте — тот же порядок, что у
                   загрузчиков стенда и констант KW_* компилятора)
    Терминатор '.' (CH_WORD_END 0x2E) дописывается честно в конец потока.
    Границу длины честно держит САМ компилятор (MAX_SOURCE_WORDS, брак
    BRK_SRC_OVERFLOW в отчёте артефакта) — инструмент только упаковывает.
    Длиннее 2 символов / не-ASCII / пустой файл — честный отказ
    инструмента, тишины нет.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise SystemExit("[VM SOURCE]: исходник не открыт — %s" % e)
    tokens = text.split()
    if not tokens:
        raise SystemExit("[VM SOURCE]: файл '%s' пуст — компилировать "
                         "нечего (честный отказ)" % path)
    words = []
    for tok in tokens:
        if len(tok) > 2:
            raise SystemExit("[VM SOURCE]: токен '%s' длиннее 2 символов — "
                             "слово-язык стадии-1 честно двухсимвольный"
                             % tok)
        codes = [ord(ch) for ch in tok]
        if any(c > 0xFF for c in codes):
            raise SystemExit("[VM SOURCE]: токен '%s' не ASCII — честный "
                             "отказ упаковки" % tok)
        w = codes[0] if len(codes) == 1 else (codes[0] | (codes[1] << 8))
        words.append(w & 0xFFFFFFFF)
    words.append(0x2E)  # честный терминатор '.' (CH_WORD_END)
    return words


def main(argv):
    quiet, steps, trace_path, source_path, args = honest_flags(argv[1:])
    trace = not quiet
    if not args:
        print(__doc__)
        return 1
    rc = 0
    for path in args:
        fh = None
        vm = None
        try:
            # честная трасса в файл (TKT-035): консоль не тонет, аудит жив
            if trace_path is not None:
                fh = open(trace_path, "w", encoding="utf-8")
            with open(path, "rb") as f:
                binary = f.read()
            # честный поток исходника (TKT-052 веха-2): слова кормятся
            # сисколлом FILE_GET, в буфер их кладёт САМ компилятор
            src_words = build_source_words(source_path) \
                if source_path is not None else None
            vm = CtOsVm(binary, path, trace=trace, trace_file=fh,
                        max_steps=steps, source_words=src_words)
            try:
                vm.run()
            finally:
                if fh is not None:
                    fh.close()
            print("[SUCCESS]: %s — %d опкодов(а), ячеек: %d" %
                  (path, vm.op_count, len(vm.cells)))
        except VmFault as e:
            panic = "[KERNEL PANIC]: %s" % e
            # честные итоги паники: сколько шагов сделано и где последний
            # честный вывод в порт (по нему и сверяют трассу — TKT-035)
            if vm is not None:
                panic += " [итоги: шагов %d" % vm.op_count
                if vm.last_out is not None:
                    op_pc, op_name, port, val = vm.last_out
                    panic += (", последний честный вывод %s порт 0x%08X <- "
                              "0x%08X на смещении 0x%08X"
                              % (op_name, port, val, op_pc))
                else:
                    panic += ", честных выводов в порт не было"
                panic += "]"
            print(panic)
            rc = 1
        except OSError as e:
            print("[VM ERROR]: файл не открыт — %s" % e)
            rc = 1
        finally:
            if fh is not None:
                fh.close()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
