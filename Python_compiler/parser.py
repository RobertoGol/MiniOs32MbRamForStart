import sys

class ASTNode: pass
class ProgramNode(ASTNode):
    def __init__(self, directives, functions):
        self.directives = directives
        self.functions = functions
class DirectiveNode(ASTNode):
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
class FunctionNode(ASTNode):
    def __init__(self, name, body, is_pub=False):
        self.name = name
        self.body = body
        self.is_pub = is_pub
class CommandNode(ASTNode):
    def __init__(self, name, args, line):
        self.name = name
        self.args = args
        self.line = line
class AssignmentNode(ASTNode):
    def __init__(self, target, value_expr, line):
        self.target = target
        self.value_expr = value_expr
        self.line = line
class IfNode(ASTNode):
    def __init__(self, condition, body, line, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body   # честная else-ветка стадии-0 (может быть None)
        self.line = line

class KitiiParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.total_tokens = len(tokens)

    def current_token(self):
        if self.pos < self.total_tokens: return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        token = self.current_token()
        if not token:
            print(f"[PARSER ERROR]: Unexpected end of file.")
            sys.exit(1)
        if expected_type and token['type'] != expected_type:
            print(f"[PARSER ERROR]: Boundary verification fault! Expected '{expected_type}', found '{token['type']}' ('{token['value']}') at line {token['line']}")
            sys.exit(1)
        self.pos += 1
        return token

    def parse(self):
        directives = []
        functions = []
        while self.pos < self.total_tokens:
            token = self.current_token()
            if token['type'] in ['TOKEN_SYS_CORE', 'TOKEN_SYS_TARGET', 'TOKEN_SYS_FIRMWARE', 'TOKEN_SYS_INCLUDE', 'TOKEN_SYS_DEFINE']:
                directives.append(DirectiveNode(token['type'], token['value']))
                self.consume()
            else: break
        while self.pos < self.total_tokens:
            token = self.current_token()
            if token['type'] == 'TOKEN_KEY_SET':
                self.consume('TOKEN_KEY_SET')
                self.consume('TOKEN_MOD_STATIC')
                name = self.consume('TOKEN_IDENTIFIER')['value']
                self.consume('TOKEN_OP_ASSIGN')
                val = self.consume()['value']
                self.consume('TOKEN_SYM_SEMICOLON')
                directives.append(DirectiveNode('TOKEN_VARIABLE_DECL', f"static cell {name} = {val}"))
            elif token['type'] == 'TOKEN_KEY_FUNCTION':
                functions.append(self.parse_function())
            elif token['type'] == 'TOKEN_KEY_PUBENTRY':
                functions.append(self.parse_function(is_pub=True))
            else:
                print(f"[PARSER ERROR]: Illegal global frame instruction '{token['value']}' at line {token['line']}")
                sys.exit(1)
        return ProgramNode(directives, functions)

    def parse_function(self, is_pub=False):
        if is_pub: self.consume('TOKEN_KEY_PUBENTRY')
        else: self.consume('TOKEN_KEY_FUNCTION')
        name_token = self.consume('TOKEN_IDENTIFIER')
        self.consume('TOKEN_SYM_LPAREN')
        while self.current_token() and self.current_token()['type'] != 'TOKEN_SYM_RPAREN':
            self.consume()
            if self.current_token() and self.current_token()['type'] == 'TOKEN_SYM_COMMA':
                self.consume('TOKEN_SYM_COMMA')
        self.consume('TOKEN_SYM_RPAREN')
        self.consume('TOKEN_SYM_LBRACE')
        body = []
        while self.pos < self.total_tokens:
            token = self.current_token()
            if token['type'] == 'TOKEN_SYM_RBRACE': break
            body.append(self.parse_statement())
        self.consume('TOKEN_SYM_RBRACE')
        return FunctionNode(name_token['value'], body)

    def parse_statement(self):
        token = self.current_token()
        if token['type'] == 'TOKEN_KEY_IF':
            line_num = token['line']
            self.consume('TOKEN_KEY_IF')
            self.consume('TOKEN_SYM_LPAREN')
            cond_expr = []
            while self.pos < self.total_tokens and self.current_token()['type'] != 'TOKEN_SYM_RPAREN':
                cond_expr.append(self.consume()['value'])
            self.consume('TOKEN_SYM_RPAREN')
            self.consume('TOKEN_SYM_LBRACE')
            if_body = []
            while self.pos < self.total_tokens and self.current_token()['type'] != 'TOKEN_SYM_RBRACE':
                if_body.append(self.parse_statement())
            self.consume('TOKEN_SYM_RBRACE')
            # честная else-ветка: лексер даёт TOKEN_KEY_ELSE, парсер обязан съесть
            else_body = None
            if self.current_token() and self.current_token()['type'] == 'TOKEN_KEY_ELSE':
                self.consume('TOKEN_KEY_ELSE')
                self.consume('TOKEN_SYM_LBRACE')
                else_body = []
                while self.pos < self.total_tokens and self.current_token()['type'] != 'TOKEN_SYM_RBRACE':
                    else_body.append(self.parse_statement())
                self.consume('TOKEN_SYM_RBRACE')
            return IfNode(" ".join(cond_expr), if_body, line_num, else_body)
        if token['type'] == 'TOKEN_KEY_SET':
            line_num = token['line']
            self.consume('TOKEN_KEY_SET')
            self.consume('TOKEN_MOD_STATIC')
            name = self.consume('TOKEN_IDENTIFIER')['value']
            self.consume('TOKEN_OP_ASSIGN')
            expr_tokens = []
            while self.pos < self.total_tokens and self.current_token()['type'] != 'TOKEN_SYM_SEMICOLON':
                expr_tokens.append(self.consume()['value'])
            self.consume('TOKEN_SYM_SEMICOLON')
            return AssignmentNode(name, " ".join(expr_tokens), line_num)
        if token['type'] == 'TOKEN_IDENTIFIER' and self.pos + 1 < self.total_tokens and self.tokens[self.pos + 1]['type'] == 'TOKEN_OP_ASSIGN':
            line_num = token['line']
            target_var = self.consume('TOKEN_IDENTIFIER')['value']
            self.consume('TOKEN_OP_ASSIGN')
            expr_tokens = []
            while self.pos < self.total_tokens and self.current_token()['type'] != 'TOKEN_SYM_SEMICOLON':
                expr_tokens.append(self.consume()['value'])
            self.consume('TOKEN_SYM_SEMICOLON')
            return AssignmentNode(target_var, " ".join(expr_tokens), line_num)
        if token['type'].startswith('TOKEN_LITE_') or token['type'] in ['TOKEN_KEY_TERMINATE', 'TOKEN_OP_OUTCELL', 'TOKEN_OP_INCELL', 'TOKEN_OP_SYSCALL', 'TOKEN_KEY_RUN', 'TOKEN_OP_STOREIND', 'TOKEN_OP_LOGCELL']:
            cmd_val = token['value']
            line_num = token['line']
            self.consume()
            args = []
            if cmd_val == 'run':
                args.append(self.consume('TOKEN_IDENTIFIER')['value'])
            if self.current_token() and self.current_token()['type'] == 'TOKEN_SYM_LPAREN':
                self.consume('TOKEN_SYM_LPAREN')
                while self.pos < self.total_tokens:
                    arg_token = self.current_token()
                    if arg_token['type'] == 'TOKEN_SYM_RPAREN': break
                    if arg_token['type'] in ['TOKEN_IDENTIFIER', 'TOKEN_LIT_HEX', 'TOKEN_LIT_NUMBER', 'TOKEN_LIT_STRING', 'TOKEN_TYPE_CELL', 'TOKEN_RAW_MODIFIER', 'TOKEN_SYM_COLON']:
                        args.append(arg_token['value'])
                        self.consume()
                    if self.current_token() and self.current_token()['type'] == 'TOKEN_SYM_COMMA':
                        self.consume('TOKEN_SYM_COMMA')
                self.consume('TOKEN_SYM_RPAREN')
            else:
                while self.current_token() and self.current_token()['type'] in ['TOKEN_IDENTIFIER', 'TOKEN_LIT_STRING', 'TOKEN_LIT_NUMBER']:
                    args.append(self.consume()['value'])
            self.consume('TOKEN_SYM_SEMICOLON')
            return CommandNode(cmd_val, args, line_num)
        print(f"[PARSER ERROR]: Illegal instruction sequence '{token['value']}' inside function context loop layer boundary context wrapper context tracking nodes at line {token['line']}")
        sys.exit(1)

if __name__ == "__main__":
    from lexer import KitiiLexer
    if len(sys.argv) < 2: sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f: code = f.read()
    lexer = KitiiLexer()
    tokens = lexer.tokenize(code)
    parser = KitiiParser(tokens)
    ast_root = parser.parse()
    print("[PARSER SUCCESS]: AST built successfully.")
