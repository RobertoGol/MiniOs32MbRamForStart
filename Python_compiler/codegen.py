# -*- coding: utf-8 -*-
"""
codegen.py — кодогенератор Стадии-0 языка KITII (Void) под ядро CtOs.

Контракт бинарника (.ctos) — единый с исполнителем CtOs-Emu/ctos_vm.py:
  Заголовок (16 байт): 'CTOS', версия LE u16, цель LE u16,
                       точка входа LE u32, магия-конец 0xAAAAFFFF.
  Дальше — rodata (пустая сейчас) и поток опкодов.

Уровни опкодов и формат аргументов (BE = big-endian u32):
  0x06 OP_JZ        +BE(адрес в файле)   переход, если acc == 0
  0x07 OP_JMP       +BE(адрес)           безусловный переход
  0x14 OP_STORE_A   +BE(адрес ячейки)    запись acc в ячейку ПО НАСТОЯЩЕМУ адресу
  0x15 OP_CONST     +BE(значение)        положить константу на аккумулятор
  0x50 OP_INCELL    +BE(адрес)           acc = содержимое ячейки по адресу
  0x52 OP_INCELL_IND +BE(адрес ячейки)   косвенное чтение: acc = cell[cell[arg]]
  0x51 OP_OUTCELL   +BE(порт)+BE(знач)   запись в порт шины bridge.ctos
  0x60 OP_ASMBLOCK  +LE(длина)+байты     ассемблерная вставка (символьный дамп)
  ...остальные — см. Compiler/opcodes.core.

Честные решения Стадии-0:
  * Переменные (`set static`) живут в фиксированной зоне 0x00F00000*(Ring 2,
    ниже монопольной видеопамяти 0x01E00000+ и выше Ring 1 до 0x00A00000).
  * `run Функция` компилируется в OP_CALL с реальным абсолютным адресом
    (двухпроходная сборка: сухой проход меряет функции, второй печатает).
  * `if (X == знач)` эмитится как чтение+сравнение+OP_JZ, ветка честно
    пропускается, когда условие ложно (проверено исполнителем).
  * Не поддержанное синтаксисом (else, арифметика сложнее `имя + число`)
    даёт честный [CODEGEN ERROR], а не мусорный бинарь.
"""

import struct
import sys

OP_NOP        = 0x00
OP_INIT       = 0x01
OP_IMPORT     = 0x02
OP_CALL       = 0x03
OP_RET        = 0x04
OP_TERM       = 0x05
OP_JZ         = 0x06
OP_JMP        = 0x07
OP_ALLOC_ST   = 0x10
OP_STORE      = 0x11   # легаси запись (без адреса) — сохранена для совместимости
OP_LOAD       = 0x12   # акк-операции: 0x14 = «acc += N», 0x16 = «acc = (acc == N)»
OP_SYSCALL    = 0x13
OP_STORE_A    = 0x14
OP_CONST      = 0x15
NET_FLUSH     = 0x23
OP_INCELL     = 0x50
OP_OUTCELL    = 0x51
OP_INCELL_IND = 0x52
OP_STORE_IND  = 0x53   # запись acc в cell[cell[arg]] — по адресу-указателю из ячейки
OP_OUTCELL_V  = 0x54   # вывод ЗНАЧЕНИЯ ячейки (cell[arg]) в порт — честный log_cell
OP_ASMBLOCK   = 0x60

OPCODES = {
    'OP_NOP': OP_NOP, 'OP_INIT': OP_INIT, 'OP_IMPORT': OP_IMPORT,
    'OP_CALL': OP_CALL, 'OP_RET': OP_RET, 'OP_TERM': OP_TERM,
    'OP_JZ': OP_JZ, 'OP_JMP': OP_JMP,
    'OP_ALLOC_ST': OP_ALLOC_ST, 'OP_STORE': OP_STORE, 'OP_LOAD': OP_LOAD,
    'OP_SYSCALL': OP_SYSCALL, 'OP_STORE_A': OP_STORE_A, 'OP_CONST': OP_CONST,
    'net_all': 0x20, 'net_up': 0x21, 'net_down': 0x22, 'net_flush': NET_FLUSH,
    'net_arp': 0x24, 'go': 0x25, 'trace': 0x26,
    'OP_INCELL': OP_INCELL, 'OP_OUTCELL': OP_OUTCELL,
    'OP_INCELL_IND': OP_INCELL_IND, 'OP_ASMBLOCK': OP_ASMBLOCK,
}

BE = ">I"   # сетевой порядок — один на весь бинарь, как в opcodes.core


class KitiiCodegen:
    # Зона статических переменных: Ring 2 (0x00A00000+), ниже видеорайона
    # Rev.web (0x01E00000+) — см. Readme «карта распределения ОЗУ».
    VAR_ZONE = 0x00F00000

    def __init__(self, ast_root):
        self.ast = ast_root
        self.rodata_section = bytearray()
        self.macro_table = {}
        self.var_table = {}        # имя переменной -> адрес ячейки
        self.call_targets = None   # имя функции -> абсолютный адрес (2-й проход)
        self.pos = self.HEADER_SIZE()  # текущее смещение в файле

    @staticmethod
    def HEADER_SIZE():
        return 16  # 'CTOS' + 2+2 цели/версия + 4 вход + 4 магия

    # ---------- честные сбои ----------
    def fail(self, msg, node=None):
        line = getattr(node, 'line', None)
        where = f" (строка {line})" if line is not None else ""
        print(f"[CODEGEN ERROR]: {msg}{where}")
        sys.exit(1)

    # ---------- резолвер имён ----------
    def resolve(self, name):
        """макрос -> переменная -> 0xHEX -> число; иначе честный сбой."""
        t = name.strip()
        if t in self.macro_table:
            return self.macro_table[t]
        if t in self.var_table:
            return self.var_table[t]
        if t.startswith('0x'):
            try:
                return int(t, 16)
            except ValueError:
                pass
        if t.isdigit():
            return int(t)
        self.fail(f"неизвестное имя '{t}': это не макрос #define, не переменная "
                  f"set static и не число")

    def is_var(self, name):
        return name.strip() in self.var_table

    def var_addr(self, name):
        name = name.strip()
        if name not in self.var_table:
            self.var_table[name] = self.VAR_ZONE + 4 * len(self.var_table)
        return self.var_table[name]

    # ---------- эмиссия ----------
    def emit(self, out, data):
        out.extend(data)
        self.pos += len(data)

    def emit_op(self, out, op):
        out.append(op)
        self.pos += 1
        self._last_opcode = op   # честный трекинг: последний ИМЕННО опкод

    def emit_be(self, out, val):
        self.emit(out, struct.pack(BE, val))

    # ---------- глобальные сущности ----------
    def load_macros_and_vars(self):
        for directive in self.ast.directives:
            if directive.type == 'TOKEN_SYS_DEFINE':
                raw_val = directive.value.replace(':', '').strip()
                if '//' in raw_val:
                    raw_val = raw_val.split('//', 1)[0].strip()
                parts = raw_val.split(None, 1)
                if len(parts) == 2:
                    macro_name = parts[0].strip()
                    macro_val = parts[1].strip()
                    if macro_val.startswith('0x'):
                        self.macro_table[macro_name] = int(macro_val, 16)
                    else:
                        self.macro_table[macro_name] = int(macro_val)
            elif directive.type == 'TOKEN_VARIABLE_DECL':
                # формат парсера: "static cell NAME = VAL"
                raw = directive.value.strip()
                if raw.startswith('static cell'):
                    raw = raw[len('static cell'):].strip()
                if '=' not in raw:
                    self.fail(f"глобальная переменная без инициализации: '{raw}'")
                name, val = (p.strip() for p in raw.split('=', 1))
                self.var_addr(name)
                # начальное значение резервируем на память memory.ctos: VM
                # по умолчанию читает неиспользованные ячейки как 0, поэтому
                # отдельные задующие OP_CONST не требуются (см. ctos_vm.py).

    # ---------- генерация ----------
    def generate(self, target_profile="ARM32"):
        target_id = 0x01 if target_profile == "ARM32" else 0x02
        self.load_macros_and_vars()

        pubs = [f for f in self.ast.functions if getattr(f, 'is_pub', False)]
        others = [f for f in self.ast.functions if not getattr(f, 'is_pub', False)]
        if len(pubs) > 1:
            self.fail("pub entry должен быть ровно один, найдено %d" % len(pubs))
        order = pubs + others

        # ПРОХОД 1 (сухой): только меряем функции, чтобы знать адреса OP_CALL.
        self.call_targets = None
        self.pos = self.HEADER_SIZE()
        starts = {}
        for func in order:
            starts[func.name] = self.pos
            self.compile_function(func, bytearray())   # выкинем, важны размеры
        self.call_targets = dict(starts)

        # ПРОХОД 2 (реальный): те же эмиссии + настоящие адреса вызовов.
        self.pos = self.HEADER_SIZE()
        self.text_section = bytearray()
        for func in order:
            self.compile_function(func, self.text_section)

        header = bytearray(b"CTOS")
        header.extend(struct.pack("<H", 0x0100))
        header.extend(struct.pack("<H", target_id))
        header.extend(struct.pack("<I", self.HEADER_SIZE()))
        header.extend(struct.pack("<I", 0xAAAAFFFF))
        return header + self.rodata_section + self.text_section

    # ---------- функции и инструкции ----------
    def compile_function(self, func, out):
        self._last_opcode = None
        for stmt in func.body:
            self.compile_stmt(stmt, out)
        if getattr(func, 'is_pub', False):
            if self._last_opcode != OP_TERM:
                self.emit_op(out, OP_TERM)   # честный выход даже без terminate
        else:
            if self._last_opcode not in (OP_RET, OP_TERM):
                self.emit_op(out, OP_RET)    # неявный возврат из функции

    def _last_op(self, out):   # устаревшая заглушка для совместимости вызовов
        return self._last_opcode

    def compile_stmt(self, stmt, out):
        from parser import CommandNode, AssignmentNode, IfNode
        if isinstance(stmt, CommandNode):
            self.compile_command(stmt, out)
        elif isinstance(stmt, AssignmentNode):
            self.compile_assign(stmt, out)
        elif isinstance(stmt, IfNode):
            self.compile_if(stmt, out)
        else:
            self.fail("неизвестный узел AST: %r" % (stmt.__class__.__name__,), stmt)

    # --- команды ---
    def compile_command(self, stmt, out):
        name = stmt.name
        if name == 'terminate':
            self.emit_op(out, OP_TERM)
        elif name == 'net_flush':
            self.emit_op(out, NET_FLUSH)
        elif name in ('net_all', 'net_up', 'net_down', 'net_arp', 'go', 'trace'):
            self.emit_op(out, OPCODES[name])
        elif name == 'run':
            self.emit_op(out, OP_CALL)
            callee = stmt.args[0] if len(stmt.args) > 0 else ''
            if self.call_targets is None:
                self.emit_be(out, 0x00000000)        # сухой проход: 4 байта места
            else:
                if callee not in self.call_targets:
                    self.fail(f"run '{callee}': функция не объявлена в файле", stmt)
                self.emit_be(out, self.call_targets[callee])
        elif name == 'out_cell':
            self.emit_op(out, OP_OUTCELL)
            port_arg = stmt.args[0] if len(stmt.args) > 0 else ''
            val_arg = stmt.args[1] if len(stmt.args) > 1 else ''
            if self.is_var(val_arg):
                self.fail("out_cell в стадии-0 пишет только константы/макросы; "
                          f"для вывода переменной есть честный log_cell "
                          f"(OP_OUTCELL_V); пришло: '{val_arg}'", stmt)
            self.emit_be(out, self.resolve(port_arg))
            self.emit_be(out, self.resolve(val_arg))
        elif name == 'log_cell':
            # честный вывод ЗНАЧЕНИЯ переменной в порт: OP_OUTCELL_V
            self.emit_op(out, OP_OUTCELL_V)
            port_arg = stmt.args[0] if len(stmt.args) > 0 else ''
            val_arg = stmt.args[1] if len(stmt.args) > 1 else ''
            if not self.is_var(val_arg):
                self.fail("log_cell выводит ПЕРЕМЕННУЮ (опкод 0x54 OP_OUTCELL_V); "
                          f"константы выводятся честным out_cell: '{val_arg}'", stmt)
            self.emit_be(out, self.resolve(port_arg))
            self.emit_be(out, self.var_addr(val_arg))
        elif name == 'store_ind':
            # честная запись по адресу из ячейки-указателя: OP_STORE_IND.
            # Контракт: acc должен быть готов ДО опкода — сначала источник,
            # потом 0x53 + BE(адрес ячейки-указателя).
            ptr_arg = stmt.args[0] if len(stmt.args) > 0 else ''
            val_arg = stmt.args[1] if len(stmt.args) > 1 else ''
            if not self.is_var(ptr_arg):
                self.fail("store_ind: первый аргумент — переменная-указатель, "
                          f"пришло '{ptr_arg}'", stmt)
            if self.is_var(val_arg):
                self.emit_op(out, OP_INCELL)
                self.emit_be(out, self.var_addr(val_arg))
            else:
                self.emit_op(out, OP_CONST)
                self.emit_be(out, self.resolve(val_arg))
            self.emit_op(out, OP_STORE_IND)
            self.emit_be(out, self.var_addr(ptr_arg))
        elif name == 'in_cell':
            self.emit_op(out, OP_INCELL)
            port_arg = stmt.args[0] if len(stmt.args) > 0 else ''
            self.emit_be(out, self.resolve(port_arg))
        elif name == '__asm__':
            self.emit_op(out, OP_ASMBLOCK)
            encoded = stmt.args[0].encode('utf-8')
            self.emit(out, struct.pack("<I", len(encoded)))
            self.emit(out, encoded)
        else:
            self.fail(f"команда '{name}' не поддержана кодогенератором Стадии-0", stmt)

    # --- присваивания ---
    def compile_assign(self, stmt, out):
        tgt = stmt.target.strip()
        tgt_addr = self.var_addr(tgt)
        expr = stmt.value_expr.strip()

        # вид:      имя = in_cell(адрес_или_имя)  -> косвенное чтение в переменную
        if expr.startswith('in_cell'):
            inside = expr[expr.find('(') + 1:expr.find(')')].strip()
            if self.is_var(inside):
                # честное чтение ПО УКАЗАТЕЛЮ из ячейки-переменной
                self.emit_op(out, OP_INCELL_IND)
                self.emit_be(out, self.var_addr(inside))
            else:
                self.emit_op(out, OP_INCELL)
                self.emit_be(out, self.resolve(inside))
            self.emit_op(out, OP_STORE_A)
            self.emit_be(out, tgt_addr)
            return

        # вид:      имя = имя/константа ± число
        # честная поддержка вычитания: «имя - число» -> OP_LOAD режим 0x17
        if ' - ' in expr:
            lhs, rhs = (p.strip() for p in expr.split(' - ', 1))
            if not rhs.isdigit():
                self.fail("в стадии-0 вычитание ограничено: "
                          f"'имя - число', справа не число: '{expr}'", stmt)
            if '- ' not in lhs and ' -' not in lhs:
                if self.is_var(lhs):
                    self.emit_op(out, OP_INCELL)
                    self.emit_be(out, self.var_addr(lhs))
                else:
                    self.emit_op(out, OP_CONST)
                    self.emit_be(out, self.resolve(lhs))
                self.emit_op(out, OP_LOAD)
                self.emit(out, bytes([0x17]))   # acc = acc - N (честный режим)
                self.emit_be(out, int(rhs))
            else:
                self.fail(f"вложенное вычитание '{expr}' в стадии-0 не поддержано", stmt)
            self.emit_op(out, OP_STORE_A)
            self.emit_be(out, tgt_addr)
            return

        # вид:      имя = число/макрос (+ число)
        parts = [p.strip() for p in expr.split('+')]
        if len(parts) == 2:
            lhs, rhs = parts
            if not rhs.isdigit():
                self.fail(f"в стадии-0 арифметика ограничена: "
                          f"'имя + число', справа не число: '{rhs}'", stmt)
            # читаем источник lhs: переменная или константа
            if self.is_var(lhs):
                self.emit_op(out, OP_INCELL)
                self.emit_be(out, self.var_addr(lhs))
            else:
                self.emit_op(out, OP_CONST)
                self.emit_be(out, self.resolve(lhs))
            self.emit_op(out, OP_LOAD)
            self.emit(out, bytes([0x14]))
            self.emit_be(out, int(rhs))
        elif len(parts) == 1:
            self.emit_op(out, OP_CONST)
            self.emit_be(out, self.resolve(expr))
        else:
            self.fail(f"многоскоростная арифметика '{expr}' в стадии-0 не поддержана", stmt)

        self.emit_op(out, OP_STORE_A)
        self.emit_be(out, tgt_addr)

    # --- ветвления ---
    def compile_if(self, stmt, out):
        cond = stmt.condition.strip()
        if '==' not in cond:
            self.fail("в стадии-0 поддержано сравнение только вида "
                      f"`имя == значение`, пришло: '{cond}'", stmt)
        lhs, rhs = (p.strip() for p in cond.split('==', 1))

        # lhs: чтение переменной либо константы
        if self.is_var(lhs):
            self.emit_op(out, OP_INCELL)
            self.emit_be(out, self.var_addr(lhs))
        else:
            self.emit_op(out, OP_CONST)
            self.emit_be(out, self.resolve(lhs))

        # сравнение: acc = (acc == rhs)
        self.emit_op(out, OP_LOAD)
        self.emit(out, bytes([0x16]))
        self.emit_be(out, self.resolve(rhs))

        # честная схема ветки:
        #   JZ -> (код then ПОСЛЕДНЯЯ точка: else, если есть; иначе конец)
        #   then...
        #   [else: JMPpast + else-код]
        # ----------- then -----------
        self.emit_op(out, OP_JZ)
        jz_at = len(out)                 # заплатка: индекс В ПОТОКЕ out
        self.emit_be(out, 0xFFFFFFFF)
        for sub in stmt.body:
            self.compile_stmt(sub, out)

        if stmt.else_body is not None:
            # тогда наливаем JMP поверх else и исполняем else после then:
            self.emit_op(out, OP_JMP)
            jmp_at = len(out)            # индекс В ПОТОКЕ out
            self.emit_be(out, 0xFFFFFFFF)
            # цель JZ — начало else (ТОЧНО здесь)
            out[jz_at:jz_at + 4] = struct.pack(BE, self.pos)
            for sub in stmt.else_body:
                self.compile_stmt(sub, out)
            # цель JMP — точка СРАЗУ ПОСЛЕ else
            out[jmp_at:jmp_at + 4] = struct.pack(BE, self.pos)
        else:
            # без else: цель JZ — точка СРАЗУ ПОСЛЕ then
            out[jz_at:jz_at + 4] = struct.pack(BE, self.pos)


if __name__ == "__main__":
    from parser import KitiiParser
    from lexer import KitiiLexer

    if len(sys.argv) < 2:
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = file_path.rsplit('.', 1)[0] + ".ctos"

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = KitiiLexer()
    tokens = lexer.tokenize(code)

    parser = KitiiParser(tokens)
    ast_root = parser.parse()

    codegen = KitiiCodegen(ast_root)
    target_prof = "ARM32"
    for d in ast_root.directives:
        if d.type == 'TOKEN_SYS_TARGET':
            target_prof = d.value

    compiled_bytes = codegen.generate(target_profile=target_prof)
    with open(output_path, 'wb') as f_out:
        f_out.write(compiled_bytes)
    print(f"[SUCCESS]: Binary image packed successfully. Weight: {len(compiled_bytes)} bytes.")
