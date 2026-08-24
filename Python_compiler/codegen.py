import sys
import os
import struct

OPCODES = {
    'OP_NOP':       0x00, 
    'OP_INIT':      0x01, 
    'OP_IMPORT':    0x02, 
    'OP_CALL':      0x03, 
    'OP_RET':       0x04, 
    'OP_TERM':      0x05,
    'OP_ALLOC_ST':  0x10, 
    'OP_STORE':     0x11, 
    'OP_LOAD':      0x12, 
    'OP_SYSCALL':   0x13, 
    'OP_INCELL':    0x50, 
    'OP_OUTCELL':   0x51, 
    'OP_ASMBLOCK':  0x60,
    'net_all':      0x20, 
    'net_up':       0x21, 
    'net_down':     0x22, 
    'net_flush':    0x23, 
    'net_arp':      0x24, 
    'go':           0x25, 
    'trace':        0x26,
}

class KitiiCodegen:
    def __init__(self, ast_root):
        self.ast = ast_root
        self.rodata_section = bytearray()
        self.text_section = bytearray()
        self.macro_table = {}

    def generate(self, target_profile="ARM32"):
        target_id = 0x01 if target_profile == "ARM32" else 0x02
        
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

        for function in self.ast.functions:
            self.compile_function(function)
            
        header = bytearray(b"CTOS")
        header.extend(struct.pack("<H", 0x0100))
        header.extend(struct.pack("<H", target_id))
        header.extend(struct.pack("<I", 0x00000010))
        header.extend(struct.pack("<I", 0xAAAAFFFF))
        return header + self.rodata_section + self.text_section

    def compile_function(self, func_node):
        from parser import CommandNode, AssignmentNode, IfNode
        
        for stmt in func_node.body:
            if isinstance(stmt, CommandNode):
                if stmt.name == 'terminate':
                    self.text_section.append(OPCODES['OP_TERM'])
                elif stmt.name == 'net_flush':
                    self.text_section.append(OPCODES['net_flush'])
                elif stmt.name == 'run':
                    self.text_section.append(OPCODES['OP_CALL'])
                    self.text_section.extend(struct.pack(">I", 0x00000000))
                elif stmt.name == 'out_cell':
                    self.text_section.append(OPCODES['OP_OUTCELL'])
                    port_arg = stmt.args[0].strip() if len(stmt.args) > 0 else "0"
                    val_arg = stmt.args[1].strip() if len(stmt.args) > 1 else "0"
                    
                    if port_arg in self.macro_table:
                        port_addr = self.macro_table[port_arg]
                    else:
                        port_addr = int(port_arg, 16) if port_arg.startswith('0x') else int(port_arg)
                        
                    if val_arg in self.macro_table:
                        val_num = self.macro_table[val_arg]
                    else:
                        val_num = int(val_arg, 16) if val_arg.startswith('0x') else int(val_arg)
                        
                    self.text_section.extend(struct.pack(">I", port_addr))
                    self.text_section.extend(struct.pack(">I", val_num))
                elif stmt.name == 'in_cell':
                    self.text_section.append(OPCODES['OP_INCELL'])
                    port_arg = stmt.args[0].strip() if len(stmt.args) > 0 else "0"
                    if port_arg in self.macro_table:
                        port_addr = self.macro_table[port_arg]
                    else:
                        port_addr = int(port_arg, 16) if port_arg.startswith('0x') else int(port_arg)
                    self.text_section.extend(struct.pack(">I", port_addr))
                elif stmt.name == '__asm__':
                    self.text_section.append(OPCODES['OP_ASMBLOCK'])
                    encoded_asm = stmt.args[0].encode('utf-8')
                    self.text_section.extend(struct.pack("<I", len(encoded_asm)))
                    self.text_section.extend(encoded_asm)
                    
            elif isinstance(stmt, AssignmentNode):
                val_expr = stmt.value_expr.strip()
                if val_expr.startswith('in_cell'):
                    self.text_section.append(OPCODES['OP_INCELL'])
                    inside = val_expr[val_expr.find('(')+1 : val_expr.find(')')].strip()
                    addr = self.macro_table.get(inside, int(inside, 16) if inside.startswith('0x') else 0x00)
                    self.text_section.extend(struct.pack(">I", addr))
                elif '+' in val_expr:
                    parts = val_expr.split('+')
                    right_op = parts[1].strip()
                    self.text_section.append(OPCODES['OP_LOAD'])
                    self.text_section.append(0x14)
                    self.text_section.extend(struct.pack(">I", int(right_op) if right_op.isdigit() else 0x00))
                else:
                    num_val = self.macro_table.get(val_expr, int(val_expr, 16) if val_expr.startswith('0x') else (int(val_expr) if val_expr.isdigit() else 0x00))
                    self.text_section.append(0x15)
                    self.text_section.extend(struct.pack(">I", num_val))
                self.text_section.append(OPCODES['OP_STORE'])
                
            elif isinstance(stmt, IfNode):
                cond = stmt.condition.strip()
                if '==' in cond:
                    parts = cond.split('==')
                    right_side = parts[1].strip()
                    self.text_section.append(OPCODES['OP_LOAD'])
                    self.text_section.append(0x16)
                    target_val = self.macro_table.get(right_side, int(right_side, 16) if right_side.startswith('0x') else int(right_side))
                    self.text_section.extend(struct.pack(">I", target_val))
                for sub_stmt in stmt.body:
                    class Container: pass
                    c = Container()
                    c.body = [sub_stmt]
                    self.compile_function(c)

if __name__ == "__main__":
    from parser import KitiiParser
    from lexer import KitiiLexer
    
    if len(sys.argv) < 2:
        sys.exit(1)
        
    file_path = sys.argv[1]
    output_path = os.path.splitext(file_path)[0] + ".ctos"
    
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
