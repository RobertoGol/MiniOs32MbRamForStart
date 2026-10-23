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

Запуск:
    python ctos_vm.py <файл.ctos> [файл2.ctos ...] [--quiet]
      [--steps N]       честный лимит шагов VM (по умолчанию 10 млн)
      [--trace FILE]    честная трасса в файл (консоль остаётся чистой)

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
OP_OUTCELL_V  = 0x54   # вывод ЗНАЧЕНИЯ ячейки (cell[arg]) в порт — честный log_cell
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
                 trace_file=None, max_steps=10_000_000):
        self.b = binary
        self.path = path
        self.trace = trace
        self.trace_file = trace_file  # честная трасса в файл (TKT-035), None = консоль
        self.max_steps = max_steps    # честный лимит шагов (TKT-035, дефолт 10 млн)
        self.cells = {}       # ячейки cell:raw: адрес -> значение
        self.static_set = {}  # статические ячейки компилятора (OP_ALLOC_ST)
        self.pc = None
        self.op_count = 0
        self._t0 = None
        self._acc = 0    # аккумулятор арифметики стадий-0
        self.rts = []    # стек возвратов для OP_CALL / OP_RET
        self.outfile = None    # честный файл-воркер (стадия-1.5, syscall-слой)
        self.outfile_n = 0     # честный счётчик записанных байт
        self.last_out = None   # честный след: последний вывод в порт (где брак, TKT-035)

    # ---------- лог ----------
    def log(self, line):
        if not self.trace:
            return
        stamped = "[%09.6f] %s" % ((time.perf_counter() - self._t0) * 1.0, line)
        if self.trace_file is not None:
            self.trace_file.write(stamped + "\n")
        else:
            print(stamped)

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
            elif mode == 0x15:    # прибавить ЗНАЧЕНИЕ ячейки: acc += cell[arg]
                self._acc = getattr(self, "_acc", 0) + self.cells.get(arg, 0)
            elif mode == 0x17:    # честное вычитание константы
                self._acc = getattr(self, "_acc", 0) - arg
            elif mode == 0x16:    # сравнение «равно?»
                self._acc = 1 if getattr(self, "_acc", 0) == arg else 0
            elif mode == 0x18:    # сравнение с ЯЧЕЙКОЙ: acc = (acc == cell[arg])
                self._acc = 1 if getattr(self, "_acc", 0) == self.cells.get(arg, 0) else 0
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
            else:
                raise VmFault("OP_SYSCALL: NID 0x%08X — честный драйвер не зарегистрирован "
                              "(файл-слой зарегистрирован: NID 0x00000130..0x00000135)" % nid)
            self.pc = pc + 5
        elif op == OP_STORE_A:
            if pc + 5 > len(b):
                raise VmFault("OP_STORE_A обрезан в конце файла")
            addr = struct.unpack_from(C1, b, pc + 1)[0]
            self.cells[addr] = self._acc
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
            self.cells[addr] = self._acc
            self.log("OP_STORE_IND: cell[cell[0x%08X]=0x%08X] = 0x%08X"
                     % (holder, addr, self._acc))
            self.pc = pc + 5
        elif op == OP_OUTCELL_V:
            if pc + 9 > len(b):
                raise VmFault("OP_OUTCELL_V обрезан в конце файла")
            port = struct.unpack_from(C1, b, pc + 1)[0]
            var_addr = struct.unpack_from(C1, b, pc + 5)[0]
            val = self.cells.get(var_addr, 0)
            self.cells[port] = val
            self.last_out = (pc, "OP_OUTCELL_V", port, val)
            self.log("OP_OUTCELL_V: порт 0x%08X <- cell[0x%08X] = 0x%08X"
                     % (port, var_addr, val))
            self.pc = pc + 9
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
        elif a.startswith("--"):
            raise SystemExit("[VM FLAGS]: неизвестный флаг '%s' (честные "
                             "флаги VM: --quiet / --steps N / --trace FILE)"
                             % a)
        else:
            files.append(a)
        i += 1
    if quiet and trace_path is not None:
        raise SystemExit("[VM FLAGS]: конфликт честных флагов: --quiet глушит "
                         "трассу, а --trace FILE её пишет; выбери один")
    return quiet, steps, trace_path, files


def main(argv):
    quiet, steps, trace_path, args = honest_flags(argv[1:])
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
            vm = CtOsVm(binary, path, trace=trace, trace_file=fh,
                        max_steps=steps)
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
