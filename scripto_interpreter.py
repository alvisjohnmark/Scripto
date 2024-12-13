import re  # Import regular expressions for tokenizing the input code

# **Lexer**: Converts raw code into tokens
def lexer(code):
    token_spec = [
        ('KEYWORD', r'start|display|use'),       # Keywords: start, display, use
        ('DATATYPE', r'int|float|string'),       # Data types: int, float, string
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Variable names
        ('ASSIGN', r'=>' ),                     # Assignment operator
        ('NUMBER', r'\d+(\.\d+)?'),             # Numbers (integer or float)
        ('STRING', r'\".*?\"'),                 # Strings enclosed in quotes
        ('OP', r'[+\-*/]'),                     # Arithmetic operators
        ('OPEN_BRACE', r'\{'),                  # Opening brace
        ('CLOSE_BRACE', r'\}'),                 # Closing brace
        ('COLON', r':'),                        # Colon
        ('DOT', r'\.'),                         # Dot for "use.variable"
        ('SKIP', r'[ \t]+'),                    # Whitespace to skip
        ('NEWLINE', r'\n'),                     # Newline to detect line breaks
    ]

    # Combine token definitions into one regex pattern
    token_regex = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_spec)
    tokens = []  # To store extracted tokens

    # Use regex to find tokens in the input code
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup  # Token type (e.g., KEYWORD, NUMBER)
        value = mo.group()   # Matched value
        if kind == 'SKIP':   # Skip whitespace
            continue
        tokens.append((kind, value))  # Append the token to the list
    return tokens  # Return the list of tokens

#Converts tokens into an Abstract Syntax Tree (AST)
def parser(tokens):
    ast = []  # To store the structure of the program
    i = 0     # Index to iterate through the tokens

    while i < len(tokens):
        token, value = tokens[i]

        if token == 'DATATYPE':  # Handle variable declarations
            data_type = value  # Capture the data type
            if tokens[i + 1][0] == 'COLON' and tokens[i + 2][0] == 'IDENTIFIER':
                var_name = tokens[i + 2][1]  # Variable name
                i += 3
                if tokens[i][0] == 'ASSIGN':  # Assignment operator found
                    i += 1
                    expr = []  # Collect the assigned expression
                    while i < len(tokens) and tokens[i][0] not in ('NEWLINE', 'CLOSE_BRACE'):
                        expr.append(tokens[i])
                        i += 1
                    # Add a variable declaration node to the AST
                    ast.append({'type': 'VariableDeclaration', 'dataType': data_type, 'name': var_name, 'value': expr})

        elif token == 'KEYWORD' and value == 'display':  # Handle display statements
            i += 1
            expr = []  # Collect the expression to be displayed
            while i < len(tokens) and tokens[i][0] not in ('NEWLINE', 'CLOSE_BRACE'):
                expr.append(tokens[i])
                i += 1
            # Add a display node to the AST
            ast.append({'type': 'Display', 'expression': expr})

        elif token == 'KEYWORD' and value == 'start':  # Handle start block
            i += 1
            if tokens[i][0] == 'OPEN_BRACE':  # Check for opening brace
                i += 1
                start_body = []  # Collect body tokens
                while i < len(tokens) and tokens[i][0] != 'CLOSE_BRACE':
                    start_body.append(tokens[i])
                    i += 1
                # Parse the block and add it as a node in the AST
                ast.append({'type': 'Start', 'body': parser(start_body)})
        i += 1
    return ast  # Return the generated AST

# **Interpreter**: Executes the AST
def interpreter(ast):
    variables = {}  # Store variable names and their values

    # Evaluate expressions recursively
    def evaluate_expression(expr):
        if len(expr) == 1:  # Single token case
            kind, value = expr[0]
            if kind == 'NUMBER':  # Convert numbers to int or float
                return float(value) if '.' in value else int(value)
            elif kind == 'STRING':  # Strip quotes from strings
                return value.strip('"')
            elif kind == 'IDENTIFIER':  # Lookup variable value
                if value in variables:
                    return variables[value]
                else:
                    raise ValueError(f"Undefined variable: {value}")

        elif len(expr) >= 3:  # Composite expressions with operators
            if expr[0][0] == 'KEYWORD' and expr[0][1] == 'use' and expr[1][0] == 'DOT':
                var_name = expr[2][1]  # Variable after "use."
                if var_name not in variables:
                    raise ValueError(f"Undefined variable in 'use.': {var_name}")
                left = variables[var_name]
                if len(expr) > 3:  # Handle operations
                    op = expr[3][1]
                    right = evaluate_expression(expr[4:])
                    if op == '+': return left + right
                    elif op == '-': return left - right
                    elif op == '*': return left * right
                    elif op == '/': return left / right
                return left

            # Standard composite expression
            left = evaluate_expression([expr[0]])
            op = expr[1][1]
            right = evaluate_expression(expr[2:])
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == '/': return left / right
        return None

    # Execute each block in the AST
    def execute_block(body):
        for node in body:
            if node['type'] == 'VariableDeclaration':  # Variable declaration
                value = evaluate_expression(node['value'])
                if node['dataType'] == 'string' and not isinstance(value, str):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected a string but got {type(value).__name__}")
                elif node['dataType'] == 'int' and not isinstance(value, int):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected an integer but got {type(value).__name__}")
                elif node['dataType'] == 'float' and not isinstance(value, (int, float)):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected a float but got {type(value).__name__}")
                variables[node['name']] = value  # Store the variable value
            elif node['type'] == 'Display':  # Display statement
                result = evaluate_expression(node['expression'])
                if result is not None:
                    print(result)  # Print the evaluated result

    # Start interpreting the AST
    for node in ast:
        if node['type'] == 'Start':  # Execute the start block
            execute_block(node['body'])

# Read the source code file
with open("scripto.scr", "r") as file:
    code = file.read()

# Tokenize the code
tokens = lexer(code)
print("Tokens:", tokens)

# Parse tokens into an AST
ast = parser(tokens)
print("AST:", ast)

# Interpret the AST
interpreter(ast)
