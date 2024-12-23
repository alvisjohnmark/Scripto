import re  # Import regular expressions for tokenizing the input code

# **Lexer**: Converts raw code into tokens
def lexer(code):
    token_spec = [
        ('KEYWORD', r'start|display|use|whatIf|alsoWhatIf|else'),       # Keywords: start, display, use, conditionals
        ('DATATYPE', r'int|float|string|boolean'), # Data types: int, float, string, boolean
        ('BOOLEAN', r'true|false'),              # Boolean values: true, false
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # Variable names
        ('ASSIGN', r'=>' ),                     # Assignment operator
        ('NUMBER', r'\d+(\.\d+)?'),             # Numbers (integer or float)
        ('STRING', r'\".*?\"'),                 # Strings enclosed in quotes
        ('OP', r'==|!=|>=|<=|[+\-*/><=!]'),                # Arithmetic and comparison operators
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
        if kind == 'SKIP':  # Skip whitespace
            continue
        tokens.append((kind, value))  # Append the token to the list
    return tokens  # Return the list of tokens

# Converts tokens into an Abstract Syntax Tree (AST)
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

def interpreter(ast):
    variables = {}  # Store variable names and their values

    def evaluate_expression(expr):
    #"""Evaluate arithmetic expressions."""
        if not expr:
            raise ValueError("Empty expression cannot be evaluated.")

        # Ensure that the expression does not start or end with an operator
        if expr[0][0] == 'OP' or expr[-1][0] == 'OP':
            raise SyntaxError("Expression cannot start or end with an operator.")

        # Start with the first value in the expression
        result = None
        operator = None

        # Process tokens one by one
        for i, (kind, value) in enumerate(expr):
            if kind == 'NUMBER':  # Convert numbers to int or float
                value = float(value) if '.' in value else int(value)
                if result is None:
                    result = value
                elif operator:
                    result = apply_operator(result, operator, value)
                    operator = None  # Reset the operator
                elif i > 0 and expr[i-1][0] == 'NUMBER':
                # This checks if two numbers are adjacent without an operator between them
                    raise SyntaxError(f"Syntax error: Two numbers cannot appear consecutively without an operator. Found: {expr[i-1][1]} and {value}")

            elif kind == 'IDENTIFIER':  # Lookup variable value
                if value in variables:
                    value = variables[value]
                    if result is None:
                        result = value
                    elif operator:
                        result = apply_operator(result, operator, value)
                        operator = None  # Reset the operator
                else:
                    raise ValueError(f"Undefined variable: {value}")

            elif kind == 'OP':  # Save the operator for the next operation
                if operator is not None:
                    raise SyntaxError(f"Consecutive operators are not allowed: {expr[i-1][1]} and {value}")
                operator = value

            else:
                raise ValueError(f"Invalid token in expression: {kind} ({value})")

        return result


    def apply_operator(left, operator, right):
        #"""Applies an arithmetic operator between two operands."""
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            return left / right
        elif operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        else:
            raise ValueError(f"Unknown operator: {operator}")




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
                elif node['dataType'] == 'boolean' and not isinstance(value, bool):
                    raise TypeError(f"Type error: Variable '{node['name']}' expected a boolean but got {type(value).__name__}")
                variables[node['name']] = value  # Assign the value to the variable

            elif node['type'] == 'Display':  # Display statement
                result = evaluate_expression(node['expression'])
                print(result)  # Print the evaluated result to the consol

            elif node['type'] == 'Start':  # Start block
                execute_block(node['body'])  # Execute the start block's body


    # Start execution with the root AST body
    execute_block(ast)


with open("scripto.scr", "r") as file:
    code = file.read()
    
tokens = lexer(code)  # Lexical analysis
ast = parser(tokens)  # Parse into AST
interpreter(ast)  # Interpret and execute
