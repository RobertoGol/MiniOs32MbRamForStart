#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ctos_vm.py — хост-исполнитель бинарников CtOs (.ctos), Этап 4.

Честная VM формата кодогенератора Стадии-0 (Python_compiler/codegen.py):
  Заголовок (16 байт):
    [0..4)  'CTOS'               магия
    [4..6)  версия (LE u16)      сейчас 0x0100
    [6..8)  цель (LE u16)        0x01 = ARM32, 0x02 = прочее
    [8..12) точка входа (LE u32) смещение в файле
    [12..16) магия-конец 0xAAAAFFFF
  Дальше — поток опкодов (формат аргументов смотри в __init__).

Запуск:
    python ctos_vm.py <файл.ctos> [файл2.ctos ...] [--quiet]

Выход: код возврата 0 — все бинарники отработали до OP_TERM; 1 — сбой VM.
"""

import struct
import sys
import time

HEADER_SIZE = 16
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
OP_ASMBLOCK  = 0x60
OP_CONST     = 0x15   # «положить константу на акк» — эмитится как 0x15 + BE u32
NET_OPS = {
    0x20: "net_all", 0x21: "net_up", 0x22: "net_down",
    0x23: "net_flush", 0x24: "net_arp", 0x25: "go", 0x26: "trace",
}

C1 = ">I"  # сетевой порядок для адресов/значений в потоке


class VmFault(Exception):
    """Честный сбой VM: недокументированный opcode, обрыв потока и т.п."""


class CtOsVm:
    def __init__(self, binary, path, trace=True, clock_scale=1):
        self.b = binary
        self.path = path
        self.trace = trace
        self.cells = {}       # ячейки cell:raw: адрес -> значение
        self.static_set = {}  # статические ячейки компилятора (OP_ALLOC_ST)
        self.pc = None
        self.op_count = 0
        self._t0 = None

    # ---------- лог ----------
    def log(self, line):
        if self.trace:
            print("[%09.6f] %s" % ((time.perf_counter() - self._t0) * 1.0, line))

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
        if entry < HEADER_SIZE or entry > len(self.b):
            raise VmFault("точка входа %d вне файла (0..%d)" % (entry, len(self.b)))
        self.log("заголовок: v%d.%d, цель %s, вход 0x%08X" %
                 ((ver >> 8) & 0xFF, ver & 0xFF,
                  TARGETS.get(target_id, "0x%04X" % target_id), entry))
        self.pc = entry

    # ---------- шаг VM ----------
    def step(self):
        """Исполняет один опкод; возвращает False, когда поток закончен (OP_TERM/RET)."""
        b = self.b
        pc = self.pc
        op = b[pc]
        self.op_count += 1

        # 1) тривиальные без аргументов
        if op == OP_NOP:
            self.pc = pc + 1
        elif op == OP_INIT:
            self.log("OP_INIT: инициализация модуля")
            self.pc = pc + 1
        elif op == OP_TERM:
            self.log("OP_TERM: завершение контекста, зачистка ячеек стека")
            return False
        elif op == OP_RET:
            self.log("OP_RET: возврат из функции")
            return False
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
            self.cells[pc] = getattr(self, "_acc", 0)
            self.log("OP_STORE: acc -> ячейка@0x%08X (стадия-0: адрес-заглушка)"
                     % pc)
            self.pc = pc + 1
        elif op == OP_LOAD:
            if pc + 6 > len(b):
                raise VmFault("OP_LOAD обрезан в конце файла")
            mode, arg = b[pc + 1], struct.unpack_from(C1, b, pc + 2)[0]
            if mode == 0x14:      # склейка «прибавить»
                self._acc = getattr(self, "_acc", 0) + arg
            elif mode == 0x16:    # сравнение «равно?»
                self._acc = 1 if getattr(self, "_acc", 0) == arg else 0
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
            self.cells[port] = val
            self.log("OP_OUTCELL: порт 0x%08X <- 0x%08X" % (port, val))
            self.pc = pc + 9

        # 3) вызовы, syscall, ассемблерный блок
        elif op == OP_CALL:
            if pc + 5 > len(b):
                raise VmFault("OP_CALL обрезан в конце файла")
            addr = struct.unpack_from(C1, b, pc + 1)[0]
            if addr == 0:
                self.log("OP_CALL: адрес не выставлен стадией-0 (заглушка) — пропускаю")
            else:
                raise VmFault("OP_CALL: таблица адресов функций ещё не встроена "
                              "в бинарь стадий-0 (адрес 0x%08X)" % addr)
            self.pc = pc + 5
        elif op == OP_SYSCALL:
            if pc + 5 > len(b):
                raise VmFault("OP_SYSCALL обрезан в конце файла")
            nid = struct.unpack_from(C1, b, pc + 1)[0]
            raise VmFault("OP_SYSCALL: NID 0x%08X — на хосте нет драйвера с "
                          "таким адресом (эмуляция шины пока не встроена)" % nid)
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
            pass
        return 0


def main(argv):
    quiet = "--quiet" in argv[1:]
    trace = not quiet
    args = [a for a in argv[1:] if a != "--quiet"]
    if not args:
        print(__doc__)
        return 1
    rc = 0
    for path in args:
        try:
            with open(path, "rb") as f:
                binary = f.read()
            vm = CtOsVm(binary, path, trace=trace)
            vm.run()
            print("[SUCCESS]: %s — %d опкодов(а), ячеек: %d" %
                  (path, vm.op_count, len(vm.cells)))
        except VmFault as e:
            print("[KERNEL PANIC]: %s" % e)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
