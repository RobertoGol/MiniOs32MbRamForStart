import sys
import os

class KitiiLexer:
    def __init__(self):
        self.keywords = {
            'function': 'TOKEN_KEY_FUNCTION',
            'pub entry': 'TOKEN_KEY_PUBENTRY',
            'run': 'TOKEN_KEY_RUN',
            'if': 'TOKEN_KEY_IF',
            'else': 'TOKEN_KEY_ELSE',
            'terminate': 'TOKEN_KEY_TERMINATE',
            'cell': 'TOKEN_TYPE_CELL',
            'raw': 'TOKEN_RAW_MODIFIER',
            'set': 'TOKEN_KEY_SET',
            'static': 'TOKEN_MOD_STATIC',
            'sys_call': 'TOKEN_OP_SYSCALL',
            'in_cell': 'TOKEN_OP_INCELL',
            'out_cell': 'TOKEN_OP_OUTCELL',
            'store_ind': 'TOKEN_OP_STOREIND',   # запись по адресу из ячейки-указателя
            'log_cell': 'TOKEN_OP_LOGCELL',     # вывод значения переменной в порт
            'net_all': 'TOKEN_LITE_NETALL',
            'net_up': 'TOKEN_LITE_NETUP',
            'net_down': 'TOKEN_LITE_NETDOWN',
            'net_flush': 'TOKEN_LITE_NETFLUSH',
            'net_arp': 'TOKEN_LITE_NETARP',
            'go': 'TOKEN_LITE_PING',
            'trace': 'TOKEN_LITE_TRACERT',
            'music_find': 'TOKEN_LITE_MSFIND',
            'music_get': 'TOKEN_LITE_MSGET',
            'pinup_install': 'TOKEN_LITE_PININSTALL',
            'pinup_download': 'TOKEN_LITE_PINDOWNLOAD',
            'pinup_web': 'TOKEN_LITE_PINWEB',
            'pinup_dir': 'TOKEN_LITE_PINDIR',
            'pinup_lit': 'TOKEN_LITE_PINLIT',
            'pinup_fin': 'TOKEN_LITE_PINFIN',
        }
        self.directives = {
            '#core:': 'TOKEN_SYS_CORE',
            '#target:': 'TOKEN_SYS_TARGET',
            '#firmware:': 'TOKEN_SYS_FIRMWARE',
            '#include:': 'TOKEN_SYS_INCLUDE',
            '#define:': 'TOKEN_SYS_DEFINE'
        }
        self.symbols = {
            '=': 'TOKEN_OP_ASSIGN',
            '{': 'TOKEN_SYM_LBRACE',
            '}': 'TOKEN_SYM_RBRACE',
            '(': 'TOKEN_SYM_LPAREN',
            ')': 'TOKEN_SYM_RPAREN',
            ';': 'TOKEN_SYM_SEMICOLON',
            ',': 'TOKEN_SYM_COMMA',
            ':': 'TOKEN_SYM_COLON',
            '+': 'TOKEN_OP_PLUS',
            '-': 'TOKEN_OP_MINUS',
            '<': 'TOKEN_OP_LT',
            '>': 'TOKEN_OP_GT'
        }

    def tokenize(self, source_code):
        tokens = []
        line_num = 1
        current_pos = 0
        code_len = len(source_code)
        
        while current_pos < code_len:
            char = source_code[current_pos]
            remaining_code = source_code[current_pos:]
            
            if char == '\r':
                current_pos += 1
                continue
            if char == '\n':
                line_num += 1
                current_pos += 1
                continue
            if char in ' \t':
                current_pos += 1
                continue
                
            if remaining_code.startswith('//'):
                end_of_line = source_code.find('\n', current_pos)
                if end_of_line == -1:
                    break
                current_pos = end_of_line
                continue

            if char == '#':
                end_of_line = source_code.find('\n', current_pos)
                if end_of_line == -1:
                    end_of_line = code_len
                full_directive = source_code[current_pos:end_of_line].strip()
                
                if full_directive.startswith('#core:'):
                    tokens.append({'type': 'TOKEN_SYS_CORE', 'value': full_directive[6:].strip(), 'line': line_num})
                elif full_directive.startswith('#target:'):
                    tokens.append({'type': 'TOKEN_SYS_TARGET', 'value': full_directive[8:].strip(), 'line': line_num})
                elif full_directive.startswith('#firmware:'):
                    tokens.append({'type': 'TOKEN_SYS_FIRMWARE', 'value': full_directive[10:].strip(), 'line': line_num})
                elif full_directive.startswith('#include:'):
                    tokens.append({'type': 'TOKEN_SYS_INCLUDE', 'value': full_directive[9:].strip(), 'line': line_num})
                elif full_directive.startswith('#define:'):
                    raw_def = full_directive[8:].strip()
                    if '//' in raw_def:
                        raw_def = raw_def.split('//', 1)[0].strip()
                    parts = raw_def.split(None, 1)
                    macro_name = parts[0].strip() if len(parts) > 0 else ''
                    macro_val = parts[1].strip() if len(parts) > 1 else ''
                    tokens.append({
                        'type': 'TOKEN_SYS_DEFINE', 
                        'value': f"{macro_name} {macro_val}", 
                        'line': line_num,
                        'macro_name': macro_name,
                        'macro_val': macro_val
                    })
                else:
                    print(f"[PREPROCESSOR ERROR]: Unknown directive '{full_directive}' at line {line_num}")
                    sys.exit(1)
                current_pos = end_of_line
                continue

            if remaining_code.startswith('__asm__'):
                tokens.append({'type': 'TOKEN_OP_ASMBLOCK', 'value': '__asm__', 'line': line_num})
                current_pos += 7
                while current_pos < code_len and source_code[current_pos] in ' \t\r\n':
                    if source_code[current_pos] == '\n':
                        line_num += 1
                    current_pos += 1
                if current_pos < code_len and source_code[current_pos] == '{':
                    tokens.append({'type': 'TOKEN_SYM_LBRACE', 'value': '{', 'line': line_num})
                    current_pos += 1
                    start_asm = current_pos
                    brace_balance = 1
                    while current_pos < code_len and brace_balance > 0:
                        if source_code[current_pos] == '{':
                            brace_balance += 1
                        elif source_code[current_pos] == '}':
                            brace_balance -= 1
                            if brace_balance == 0:
                                break
                        elif source_code[current_pos] == '\n':
                            line_num += 1
                        current_pos += 1
                    tokens.append({'type': 'TOKEN_ASM_BODY', 'value': source_code[start_asm:current_pos].strip(), 'line': line_num})
                    if current_pos < code_len and source_code[current_pos] == '}':
                        tokens.append({'type': 'TOKEN_SYM_RBRACE', 'value': '}', 'line': line_num})
                        current_pos += 1
                    continue

            if remaining_code.startswith('&- import'):
                tokens.append({'type': 'TOKEN_OP_HARDLINK', 'value': '&- import', 'line': line_num})
                current_pos += 9
                continue

            if char == '"':
                end_quotes = source_code.find('"', current_pos + 1)
                if end_quotes == -1:
                    print(f"[LEXER ERROR]: Unterminated string literal at line {line_num}")
                    sys.exit(1)
                tokens.append({'type': 'TOKEN_LIT_STRING', 'value': source_code[current_pos:end_quotes + 1], 'line': line_num})
                current_pos = end_quotes + 1
                continue

            if remaining_code.startswith('0x'):
                end_hex = current_pos + 2
                while end_hex < code_len and source_code[end_hex] in '0123456789abcdefABCDEF':
                    end_hex += 1
                tokens.append({'type': 'TOKEN_LIT_HEX', 'value': source_code[current_pos:end_hex], 'line': line_num})
                current_pos = end_hex
                continue

            if char.isalnum() or char == '_':
                if remaining_code.startswith('pub entry'):
                    word = 'pub entry'
                    end_word = current_pos + 9
                else:
                    end_word = current_pos
                    while end_word < code_len and (source_code[end_word].isalnum() or source_code[end_word] == '_'):
                        end_word += 1
                    word = source_code[current_pos:end_word]
                
                if word in self.keywords:
                    tokens.append({'type': self.keywords[word], 'value': word, 'line': line_num})
                else:
                    if word.isdigit():
                        tokens.append({'type': 'TOKEN_LIT_NUMBER', 'value': word, 'line': line_num})
                    else:
                        tokens.append({'type': 'TOKEN_IDENTIFIER', 'value': word, 'line': line_num})
                current_pos = end_word
                continue

            if char == '=' and remaining_code.startswith('=='):
                # Оператор равенства обязан разбираться ДО одиночного '='
                tokens.append({'type': 'TOKEN_OP_EQ', 'value': '==', 'line': line_num})
                current_pos += 2
                continue

            if char in self.symbols:
                tokens.append({'type': self.symbols[char], 'value': char, 'line': line_num})
                current_pos += 1
                continue

            print(f"[LEXER ERROR]: Illegal sequence '{char}' at line {line_num}")
            sys.exit(1)
        return tokens

def print_kernel_boot():
    print("="*75)
    print("[0.000000] CTOS KERNEL BOOTLOADER INIT ENGINE ACTIVATED...")
    print("[0.003114] HOST HARDWARE ARCHITECTURE MATRIX PROFILE VERIFICATION... OK")
    print("[0.009452] MEMORY ALLOCATOR CORE INITIALIZATION POOL SYSTEM: 32MB FIXED... OK")
    print("[0.021084] SYSTEM CORE HARDWARE INTERFACE BUS INITIALIZATION DETECTED... OK")
    print("[0.035912] COMPILER DIRECTIVES AND OPCODES SPECIFICATION MATRIX PARSED... OK")
    print("="*75 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[STAGE-0 ERROR]: Compilation input source file target path parameter required.")
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"[STAGE-0 ERROR]: File path '{file_path}' not found.")
        sys.exit(1)
    with open(file_path, 'r', encoding='utf-8') as f:
        source_bytes = f.read()
    print_kernel_boot()
    lexer = KitiiLexer()
    token_stream = lexer.tokenize(source_bytes)
    print(f"[CTOS CORE]: Tokens mapped: {len(token_stream)}")
