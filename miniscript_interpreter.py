import re

def lexer(code):
    token_spec = [
        ('KEYWORD', r'start|display|use'),
        ('DATATYPE', r'int|float|string'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('ASSIGN', r'=>' ),
        ('NUMBER', r'\d+(\.\d+)?'),
        ('STRING', r'\".*?\"'),
        ('OP', r'[+\-*/]'),
        ('OPEN_BRACE', r'\{'),
        ('CLOSE_BRACE', r'\}'),
        ('COLON', r':'),
        ('DOT', r'\.'),
        ('SKIP', r'[ \t]+'),
        ('NEWLINE', r'\n'),
    ]

    token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_spec)
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        tokens.append((kind, value))
    return tokens

def parser(tokens):
    ast = []
    i = 0
    while i < len(tokens):
        token, value = tokens[i]

        if token == 'DATATYPE':
            data_type = value
            if tokens[i + 1][0] == 'COLON' and tokens[i + 2][0] == 'IDENTIFIER':
                var_name = tokens[i + 2][1]
                i += 3
                if tokens[i][0] == 'ASSIGN':
                    i += 1
                    expr = []
                    while i < len(tokens) and tokens[i][0] not in ('NEWLINE', 'CLOSE_BRACE'):
                        expr.append(tokens[i])
                        i += 1
                    ast.append({'type': 'VariableDeclaration', 'dataType': data_type, 'name': var_name, 'value': expr})

        elif token == 'KEYWORD' and value == 'display':
            i += 1
            expr = []
            while i < len(tokens) and tokens[i][0] not in ('NEWLINE', 'CLOSE_BRACE'):
                expr.append(tokens[i])
                i += 1
            ast.append({'type': 'Display', 'expression': expr})

        elif token == 'KEYWORD' and value == 'start':
            i += 1
            if tokens[i][0] == 'OPEN_BRACE':
                i += 1
                start_body = []
                while i < len(tokens) and tokens[i][0] != 'CLOSE_BRACE':
                    start_body.append(tokens[i])
                    i += 1
                ast.append({'type': 'Start', 'body': parser(start_body)})
        i += 1
    return ast

def interpreter(ast):
    variables = {}

    def evaluate_expression(expr):
        if len(expr) == 1:
            kind, value = expr[0]
            if kind == 'NUMBER':
                return float(value) if '.' in value else int(value)
            elif kind == 'STRING':
                return value.strip('"')
            elif kind == 'IDENTIFIER':
                if value in variables:
                    return variables[value]
                else:
                    raise ValueError(f"Undefined variable: {value}")
        elif len(expr) == 3 and expr[0][0] == 'KEYWORD' and expr[0][1] == 'use':
            if expr[1][0] == 'DOT' and expr[2][0] == 'IDENTIFIER':
                var_name = expr[2][1]
            if var_name in variables:
                return variables[var_name]
            else:
                raise ValueError(f"Undefined variable: {var_name}")
        elif len(expr) == 3:
            left = evaluate_expression([expr[0]])
            op = expr[1][1]
            right = evaluate_expression([expr[2]])
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
        return None


    def execute_block(body):
        for node in body:
            if node['type'] == 'VariableDeclaration':
                value = evaluate_expression(node['value'])
                if node['dataType'] == 'string' and not isinstance(value, str):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected a string but got {type(value).__name__}")
                elif node['dataType'] == 'int' and not isinstance(value, int):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected an integer but got {type(value).__name__}")
                elif node['dataType'] == 'float' and not isinstance(value, (int, float)):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected a float but got {type(value).__name__}")
                variables[node['name']] = value
            elif node['type'] == 'Display':
                result = evaluate_expression(node['expression'])
                if result is not None:
                    print(result)


    for node in ast:
        if node['type'] == 'Start':
            execute_block(node['body'])

with open("miniscript.msp", "r") as file:
    code = file.read()

tokens = lexer(code)
ast = parser(tokens)
interpreter(ast)