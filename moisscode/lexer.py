import re
from typing import NamedTuple, List, Optional

class Token(NamedTuple):
    type: str
    value: str
    line: int
    column: int

class MOISSCodeLexer:
    TOKENS = [
        ('COMMENT',     r'//.*'),

        # Keywords
        ('PROTOCOL',    r'\bprotocol\b'),
        ('FUNCTION',    r'\bfunction\b'),
        ('IMPORT',      r'\bimport\b'),
        ('INPUT',       r'\binput\b'),
        ('TYPE',        r'\btype\b'),
        ('EXTENDS',     r'\bextends\b'),
        ('TRACK',       r'\btrack\b'),
        ('USING',       r'\busing\b'),
        ('KAE',         r'\bKAE\b'),
        ('ASSESS',      r'\bassess\b'),
        ('FOR',         r'\bfor\b'),
        ('IN',          r'\bin\b'),
        ('ADMINISTER',  r'\badminister\b'),
        ('DOSE',        r'\bdose\b'),
        ('RULE',        r'\brule\b'),
        ('IF',          r'\bif\b'),
        ('ELSE',        r'\belse\b'),
        ('WHILE',       r'\bwhile\b'),
        ('RETURN',      r'\breturn\b'),
        ('LET',         r'\blet\b'),
        ('ALERT',       r'\balert\b'),
        ('SEVERITY',    r'\bseverity\b'),
        ('AND',         r'\band\b'),
        ('OR',          r'\bor\b'),
        ('NOT',         r'\bnot\b'),
        ('TRUE',        r'\btrue\b'),
        ('FALSE',       r'\bfalse\b'),
        ('NULL',        r'\bnull\b'),

        # Medical units
        ('UNIT',        r'\b(mg|mcg|g|kg|L|mL|mmHg|mmol|mol|IU)\b(?:/(?:min|hr|kg|L|mL))*'),

        # Numeric literals
        ('FLOAT',       r'\d+\.\d+'),
        ('INT',         r'\d+'),

        # Identifiers
        ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),

        # String literals
        ('STRING',      r'"[^"]*"'),

        # Symbols (multi-char first)
        ('LBRACKET',    r'\['),
        ('RBRACKET',    r'\]'),
        ('LBRACE',      r'\{'),
        ('RBRACE',      r'\}'),
        ('LPAREN',      r'\('),
        ('RPAREN',      r'\)'),
        ('SEMI',        r';'),
        ('COLON',       r':'),
        ('COMMA',       r','),
        ('DOT',         r'\.'),
        ('ARROW',       r'->'),
        ('GE',          r'>='),
        ('LE',          r'<='),
        ('NE',          r'!='),
        ('EQ',          r'=='),
        ('ASSIGN',      r'='),
        ('GT',          r'>'),
        ('LT',          r'<'),
        ('PLUS',        r'\+'),
        ('MINUS',       r'-'),
        ('MUL',         r'\*'),
        ('DIV',         r'/'),

        ('NEWLINE',     r'\n'),
        ('SKIP',        r'[ \t]+'),
        ('MISMATCH',    r'.'),
    ]

    def __init__(self):
        self.regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKENS))

    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        line_num = 1
        line_start = 0

        for mo in self.regex.finditer(code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'COMMENT':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')

            tokens.append(Token(kind, value, line_num, column))

        return tokens
