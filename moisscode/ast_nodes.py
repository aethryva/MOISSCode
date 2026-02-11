from typing import List, Optional, Union, Any
from dataclasses import dataclass, field

@dataclass
class ASTNode:
    pass

# ─── Top Level ─────────────────────────────────────────────
@dataclass
class Program(ASTNode):
    imports: List['ImportStmt'] = field(default_factory=list)
    type_defs: List['TypeDef'] = field(default_factory=list)
    function_defs: List['FunctionDef'] = field(default_factory=list)
    protocols: List['ProtocolDef'] = field(default_factory=list)

@dataclass
class ImportStmt(ASTNode):
    """import med.biochem;"""
    module_path: str

@dataclass
class TypeDef(ASTNode):
    """type Bacteria { name: str; mic: float; }"""
    name: str
    parent: Optional[str]  # extends clause
    fields: List['FieldDecl']

@dataclass
class FieldDecl(ASTNode):
    name: str
    type_name: str
    default_value: Optional['Expression'] = None

@dataclass
class FunctionDef(ASTNode):
    """function calculate_dose(weight, drug) { ... return result; }"""
    name: str
    params: List['ParamDecl']
    body: List['Statement']
    return_type: Optional[str] = None

@dataclass
class ParamDecl(ASTNode):
    name: str
    type_name: Optional[str] = None

@dataclass
class ProtocolDef(ASTNode):
    name: str
    inputs: List['VariableDecl']
    body: List['Statement']

@dataclass
class VariableDecl(ASTNode):
    name: str
    type_name: str
    initial_value: Optional['Expression'] = None

# ─── Statements ────────────────────────────────────────────
class Statement(ASTNode):
    pass

@dataclass
class TrackStmt(Statement):
    target: str
    using_kae: bool

@dataclass
class AdministerStmt(Statement):
    drug_name: str
    dose_amount: float
    dose_unit: str

@dataclass
class IfStmt(Statement):
    condition: 'Expression'
    then_block: List[Statement]
    else_block: Optional[List[Statement]] = None

@dataclass
class LetStmt(Statement):
    """let score = med.scores.qsofa(p);"""
    name: str
    type_name: Optional[str]
    value: 'Expression'

@dataclass
class WhileStmt(Statement):
    """while p.lactate > 2.0 { ... }"""
    condition: 'Expression'
    body: List[Statement]

@dataclass
class ForEachStmt(Statement):
    """for patient in ward.patients { ... }"""
    var_name: str
    iterable: 'Expression'
    body: List[Statement]

@dataclass
class AssessStmt(Statement):
    """assess p for sepsis;"""
    target: str
    condition: str

@dataclass
class AlertStmt(Statement):
    """alert "Sepsis detected" severity: high;"""
    message: 'Expression'
    severity: Optional[str] = "info"

@dataclass
class ReturnStmt(Statement):
    """return value;"""
    value: Optional['Expression'] = None

@dataclass
class ExpressionStmt(Statement):
    expr: 'Expression'

# ─── Expressions ───────────────────────────────────────────
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class Literal(Expression):
    value: Any
    unit: Optional[str] = None

@dataclass
class StringLiteral(Expression):
    value: str

@dataclass
class ListLiteral(Expression):
    """[1, 2, 3] or ["a", "b", "c"]"""
    elements: List[Expression]

@dataclass
class MapLiteral(Expression):
    """{ "key": value, "key2": value2 }"""
    pairs: List[tuple]  # List of (key_expr, value_expr)

@dataclass
class IndexAccess(Expression):
    """list[0] or map["key"]"""
    object: Expression
    index: Expression

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class MemberAccess(Expression):
    object_name: str
    member_name: str

@dataclass
class FunctionCall(Expression):
    function_name: str
    arguments: List[Expression]

@dataclass
class ConstructorCall(Expression):
    """Bacteria { name: "E.coli", mic: 0.5 }"""
    type_name: str
    field_values: List[tuple]  # List of (field_name, expression)
