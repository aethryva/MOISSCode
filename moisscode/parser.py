from typing import List, Optional
from moisscode.lexer import Token, MOISSCodeLexer
from moisscode.ast_nodes import *

class MOISSCodeParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0) -> Optional[Token]:
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type: str = None) -> Token:
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected end of file")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {token.type} ('{token.value}') at line {token.line}")
        self.pos += 1
        return token

    # ─── Top Level ─────────────────────────────────────────────
    def parse_program(self) -> Program:
        imports = []
        type_defs = []
        function_defs = []
        protocols = []

        while self.peek():
            token = self.peek()
            if token.type == 'IMPORT':
                imports.append(self.parse_import())
            elif token.type == 'TYPE':
                type_defs.append(self.parse_type_def())
            elif token.type == 'FUNCTION':
                function_defs.append(self.parse_function_def())
            elif token.type == 'PROTOCOL':
                protocols.append(self.parse_protocol())
            else:
                self.consume()  # Skip unknown top-level tokens

        return Program(imports, type_defs, function_defs, protocols)

    # ─── Import ────────────────────────────────────────────────
    def parse_import(self) -> ImportStmt:
        self.consume('IMPORT')
        path = self.parse_dotted_name()
        self.consume('SEMI')
        return ImportStmt(path)

    # ─── Type Definition ──────────────────────────────────────
    def parse_type_def(self) -> TypeDef:
        self.consume('TYPE')
        name = self.consume('ID').value

        parent = None
        if self.peek() and self.peek().type == 'EXTENDS':
            self.consume('EXTENDS')
            parent = self.consume('ID').value

        self.consume('LBRACE')
        fields = []
        while self.peek() and self.peek().type != 'RBRACE':
            field_name = self.consume('ID').value
            self.consume('COLON')
            field_type = self.consume('ID').value

            default = None
            if self.peek() and self.peek().type == 'ASSIGN':
                self.consume('ASSIGN')
                default = self.parse_expression()

            self.consume('SEMI')
            fields.append(FieldDecl(field_name, field_type, default))

        self.consume('RBRACE')
        return TypeDef(name, parent, fields)

    # ─── Function Definition ──────────────────────────────────
    def parse_function_def(self) -> FunctionDef:
        self.consume('FUNCTION')
        name = self.consume('ID').value
        self.consume('LPAREN')

        params = []
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                param_name = self.consume('ID').value
                param_type = None
                if self.peek() and self.peek().type == 'COLON':
                    self.consume('COLON')
                    param_type = self.consume('ID').value
                params.append(ParamDecl(param_name, param_type))
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break

        self.consume('RPAREN')

        # Optional return type
        return_type = None
        if self.peek() and self.peek().type == 'ARROW':
            self.consume('ARROW')
            return_type = self.consume('ID').value

        self.consume('LBRACE')
        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')

        return FunctionDef(name, params, body, return_type)

    # ─── Protocol ──────────────────────────────────────────────
    def parse_protocol(self) -> ProtocolDef:
        self.consume('PROTOCOL')
        name = self.consume('ID').value
        self.consume('LBRACE')

        inputs = []
        body = []

        while self.peek() and self.peek().type != 'RBRACE':
            token = self.peek()
            if token.type == 'INPUT':
                inputs.append(self.parse_input())
            else:
                body.append(self.parse_statement())

        self.consume('RBRACE')
        return ProtocolDef(name, inputs, body)

    # ─── Statement Dispatch ────────────────────────────────────
    def parse_statement(self) -> Statement:
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected end of file while parsing statement")

        if token.type == 'TRACK':
            return self.parse_track()
        elif token.type == 'ADMINISTER':
            return self.parse_administer()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'LET':
            return self.parse_let()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'FOR':
            return self.parse_for_each()
        elif token.type == 'ASSESS':
            return self.parse_assess()
        elif token.type == 'ALERT':
            return self.parse_alert()
        elif token.type == 'RETURN':
            return self.parse_return()
        elif token.type == 'ID':
            return self.parse_expression_statement()
        else:
            raise SyntaxError(f"Unknown statement starting with '{token.value}' ({token.type}) at line {token.line}")

    # ─── Input ─────────────────────────────────────────────────
    def parse_input(self) -> VariableDecl:
        self.consume('INPUT')
        self.consume('COLON')
        type_name = self.consume('ID').value
        var_name = self.consume('ID').value
        self.consume('SEMI')
        return VariableDecl(var_name, type_name)

    # ─── Track ─────────────────────────────────────────────────
    def parse_track(self) -> TrackStmt:
        self.consume('TRACK')
        target = self.parse_dotted_name()
        using_kae = False
        if self.peek() and self.peek().type == 'USING':
            self.consume('USING')
            self.consume('KAE')
            using_kae = True
        self.consume('SEMI')
        return TrackStmt(target, using_kae)

    # ─── Administer ────────────────────────────────────────────
    def parse_administer(self) -> AdministerStmt:
        self.consume('ADMINISTER')
        drug = self.consume('ID').value
        self.consume('DOSE')
        self.consume('COLON')
        amount = float(self.consume().value)
        unit = self.consume('UNIT').value
        self.consume('SEMI')
        return AdministerStmt(drug, amount, unit)

    # ─── If / Else ─────────────────────────────────────────────
    def parse_if(self) -> IfStmt:
        self.consume('IF')
        condition = self.parse_expression()
        self.consume('LBRACE')

        then_block = []
        while self.peek() and self.peek().type != 'RBRACE':
            then_block.append(self.parse_statement())
        self.consume('RBRACE')

        else_block = None
        if self.peek() and self.peek().type == 'ELSE':
            self.consume('ELSE')
            self.consume('LBRACE')
            else_block = []
            while self.peek() and self.peek().type != 'RBRACE':
                else_block.append(self.parse_statement())
            self.consume('RBRACE')

        return IfStmt(condition, then_block, else_block)

    # ─── Let ───────────────────────────────────────────────────
    def parse_let(self) -> LetStmt:
        self.consume('LET')
        var_name = self.consume('ID').value

        type_name = None
        if self.peek() and self.peek().type == 'COLON':
            self.consume('COLON')
            type_name = self.consume('ID').value

        self.consume('ASSIGN')
        value = self.parse_expression()
        self.consume('SEMI')
        return LetStmt(var_name, type_name, value)

    # ─── While ─────────────────────────────────────────────────
    def parse_while(self) -> WhileStmt:
        self.consume('WHILE')
        condition = self.parse_expression()
        self.consume('LBRACE')

        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')

        return WhileStmt(condition, body)

    # ─── For-Each ──────────────────────────────────────────────
    def parse_for_each(self) -> ForEachStmt:
        self.consume('FOR')
        var_name = self.consume('ID').value
        self.consume('IN')
        iterable = self.parse_expression()
        self.consume('LBRACE')

        body = []
        while self.peek() and self.peek().type != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')

        return ForEachStmt(var_name, iterable, body)

    # ─── Assess ────────────────────────────────────────────────
    def parse_assess(self) -> AssessStmt:
        self.consume('ASSESS')
        target = self.parse_dotted_name()
        self.consume('FOR')
        condition = self.consume('ID').value
        self.consume('SEMI')
        return AssessStmt(target, condition)

    # ─── Alert ─────────────────────────────────────────────────
    def parse_alert(self) -> AlertStmt:
        self.consume('ALERT')
        message = self.parse_expression()

        severity = "info"
        if self.peek() and self.peek().type == 'SEVERITY':
            self.consume('SEVERITY')
            self.consume('COLON')
            severity = self.consume('ID').value

        self.consume('SEMI')
        return AlertStmt(message, severity)

    # ─── Return ────────────────────────────────────────────────
    def parse_return(self) -> ReturnStmt:
        self.consume('RETURN')
        value = None
        if self.peek() and self.peek().type != 'SEMI':
            value = self.parse_expression()
        self.consume('SEMI')
        return ReturnStmt(value)

    # ─── Expression Statement ──────────────────────────────────
    def parse_expression_statement(self) -> ExpressionStmt:
        expr = self.parse_expression()
        self.consume('SEMI')
        return ExpressionStmt(expr)

    # ─── Expression Parsing (Precedence Climbing) ──────────────
    def parse_expression(self) -> Expression:
        return self.parse_or()

    def parse_or(self) -> Expression:
        left = self.parse_and()
        while self.peek() and self.peek().type == 'OR':
            op = self.consume().value
            right = self.parse_and()
            left = BinaryOp(left, op, right)
        return left

    def parse_and(self) -> Expression:
        left = self.parse_not()
        while self.peek() and self.peek().type == 'AND':
            op = self.consume().value
            right = self.parse_not()
            left = BinaryOp(left, op, right)
        return left

    def parse_not(self) -> Expression:
        if self.peek() and self.peek().type == 'NOT':
            op = self.consume().value
            operand = self.parse_not()
            return UnaryOp(op, operand)
        return self.parse_comparison()

    def parse_comparison(self) -> Expression:
        left = self.parse_term()
        if self.peek() and self.peek().type in ['GT', 'LT', 'GE', 'LE', 'EQ', 'NE']:
            op = self.consume().value
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        return left

    def parse_term(self) -> Expression:
        left = self.parse_factor()
        while self.peek() and self.peek().type in ['PLUS', 'MINUS']:
            op = self.consume().value
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        return left

    def parse_factor(self) -> Expression:
        left = self.parse_unary()
        while self.peek() and self.peek().type in ['MUL', 'DIV']:
            op = self.consume().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def parse_unary(self) -> Expression:
        if self.peek() and self.peek().type == 'MINUS':
            self.consume()
            operand = self.parse_postfix()
            return UnaryOp('-', operand)
        return self.parse_postfix()

    def parse_postfix(self) -> Expression:
        expr = self.parse_primary()

        # Handle index access: expr[index]
        while self.peek() and self.peek().type == 'LBRACKET':
            self.consume('LBRACKET')
            index = self.parse_expression()
            self.consume('RBRACKET')
            expr = IndexAccess(expr, index)

        return expr

    def parse_primary(self):
        token = self.peek()

        if token.type in ['INT', 'FLOAT']:
            return self.parse_literal()
        elif token.type == 'STRING':
            return self.parse_string()
        elif token.type == 'TRUE':
            self.consume()
            return Literal(True)
        elif token.type == 'FALSE':
            self.consume()
            return Literal(False)
        elif token.type == 'NULL':
            self.consume()
            return Literal(None)
        elif token.type == 'LBRACKET':
            return self.parse_list_literal()
        elif token.type == 'ID':
            return self.parse_id_or_call()
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'MINUS':
            return self.parse_unary()
        else:
            raise SyntaxError(f"Unexpected token '{token.value}' ({token.type}) at line {token.line}")

    def parse_id_or_call(self):
        name = self.consume('ID').value

        # Check if this is a constructor: TypeName { field: val }
        if self.peek() and self.peek().type == 'LBRACE':
            # Look ahead to distinguish constructor vs block
            # Constructor pattern: ID { ID : expr ... }
            saved_pos = self.pos
            try:
                self.consume('LBRACE')
                if self.peek() and self.peek().type == 'ID':
                    next_next = self.peek(1)
                    if next_next and next_next.type == 'COLON':
                        # This is a constructor
                        self.pos = saved_pos
                        return self.parse_constructor(name)
                self.pos = saved_pos
            except:
                self.pos = saved_pos

        # Dotted access
        while self.peek() and self.peek().type == 'DOT':
            self.consume('DOT')
            if self.peek() and self.peek().type == 'ID':
                name += "." + self.consume('ID').value
            else:
                raise SyntaxError(f"Expected identifier after '.'")

        # Function call
        if self.peek() and self.peek().type == 'LPAREN':
            return self.parse_function_call(name)

        return Identifier(name)

    def parse_constructor(self, type_name: str) -> ConstructorCall:
        self.consume('LBRACE')
        field_values = []
        while self.peek() and self.peek().type != 'RBRACE':
            field_name = self.consume('ID').value
            self.consume('COLON')
            value = self.parse_expression()
            field_values.append((field_name, value))
            if self.peek() and self.peek().type == 'COMMA':
                self.consume('COMMA')
        self.consume('RBRACE')
        return ConstructorCall(type_name, field_values)

    def parse_function_call(self, func_name: str):
        self.consume('LPAREN')
        args = []
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        self.consume('RPAREN')
        return FunctionCall(func_name, args)

    def parse_list_literal(self) -> ListLiteral:
        self.consume('LBRACKET')
        elements = []
        if self.peek() and self.peek().type != 'RBRACKET':
            while True:
                elements.append(self.parse_expression())
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        self.consume('RBRACKET')
        return ListLiteral(elements)

    def parse_literal(self):
        val = float(self.consume().value)
        unit = None
        if self.peek() and self.peek().type == 'UNIT':
            unit = self.consume('UNIT').value
        return Literal(val, unit)

    def parse_string(self):
        token = self.consume('STRING')
        val = token.value[1:-1]
        return Literal(val, None)

    def parse_dotted_name(self) -> str:
        name = self.consume('ID').value
        while self.peek() and self.peek().type == 'DOT':
            self.consume('DOT')
            name += "." + self.consume('ID').value
        return name
