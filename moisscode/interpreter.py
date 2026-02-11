"""MOISSCode Interpreter  - executes parsed AST programs."""

from typing import Any, Dict, List, Optional
from moisscode.ast_nodes import *
from moisscode.typesystem import TypeChecker, Patient
from moisscode.stdlib import StandardLibrary, KAE_Estimator, MOISS_Classifier


class ReturnException(Exception):
    """Control flow exception for function return statements."""
    def __init__(self, value=None):
        self.value = value


class MOISSCodeInterpreter:
    """Walks the MOISSCode AST and produces runtime events."""

    MAX_LOOP_ITERATIONS = 1000
    LIBRARY_PREFIX = "med"

    def __init__(self):
        self.scope: Dict[str, Any] = {}
        self.kae_instances: Dict[str, KAE_Estimator] = {}
        self.moiss = MOISS_Classifier()
        self.type_checker = TypeChecker()
        self.runtime_events: List[Dict] = []
        self.user_types: Dict[str, TypeDef] = {}
        self.user_functions: Dict[str, FunctionDef] = {}
        self.call_stack: List[Dict] = []
        self.scope[self.LIBRARY_PREFIX] = {'type': 'Library', 'value': StandardLibrary()}

    # ─── Execute Program ───────────────────────────────────────
    def execute(self, program: Program):
        """Top-level entry point: register types/functions, execute protocols."""
        self.runtime_events = []

        for imp in program.imports:
            self.log(f"[Import] {imp.module_path}")

        for td in program.type_defs:
            self.user_types[td.name] = td
            self.log(f"[Type] Registered: {td.name}" +
                     (f" extends {td.parent}" if td.parent else "") +
                     f" ({len(td.fields)} fields)")

        for fd in program.function_defs:
            self.user_functions[fd.name] = fd
            self.log(f"[Function] Registered: {fd.name}({', '.join(p.name for p in fd.params)})")

        for proto in program.protocols:
            self.execute_protocol(proto)

        return self.runtime_events

    # ─── Protocol ──────────────────────────────────────────────
    def execute_protocol(self, proto: ProtocolDef):
        """Execute a single protocol block, binding inputs and running statements."""
        self.log(f"[Protocol] Executing: {proto.name}")

        for inp in proto.inputs:
            if inp.type_name == "Patient":
                if inp.name not in self.scope:
                    self.scope[inp.name] = {
                        'type': 'Patient',
                        'value': Patient(bp=85, hr=110, rr=24, temp=38.5, spo2=94,
                                         weight=70, age=55, gcs=14, lactate=3.2, sex='M')
                    }
            elif inp.type_name in self.user_types:
                self.scope[inp.name] = {
                    'type': inp.type_name,
                    'value': self._create_instance(inp.type_name)
                }

        for stmt in proto.body:
            self.execute_statement(stmt)

    # ─── Execute Statement ─────────────────────────────────────
    def execute_statement(self, stmt: Statement):
        if isinstance(stmt, TrackStmt):
            self.execute_track(stmt)
        elif isinstance(stmt, AdministerStmt):
            self.execute_administer(stmt)
        elif isinstance(stmt, IfStmt):
            self.execute_if(stmt)
        elif isinstance(stmt, LetStmt):
            self.execute_let(stmt)
        elif isinstance(stmt, WhileStmt):
            self.execute_while(stmt)
        elif isinstance(stmt, ForEachStmt):
            self.execute_for_each(stmt)
        elif isinstance(stmt, AssessStmt):
            self.execute_assess(stmt)
        elif isinstance(stmt, AlertStmt):
            self.execute_alert(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.execute_return(stmt)
        elif isinstance(stmt, ExpressionStmt):
            self.evaluate_expr(stmt.expr)

    # ─── Track ─────────────────────────────────────────────────
    def execute_track(self, stmt: TrackStmt):
        value = self.resolve_member(stmt.target)
        if stmt.using_kae:
            if stmt.target not in self.kae_instances:
                self.kae_instances[stmt.target] = KAE_Estimator()
            est = self.kae_instances[stmt.target].update(value)
            event = {'type': 'TRACK', 'target': stmt.target, 'raw': value,
                     'kae_pos': round(est['pos'], 2), 'kae_vel': round(est['vel'], 4)}
        else:
            event = {'type': 'TRACK', 'target': stmt.target, 'value': value}

        self.log(f"[Track] {stmt.target} = {value}" +
                 (f" (KAE: pos={event.get('kae_pos')}, vel={event.get('kae_vel')})" if stmt.using_kae else ""))
        self.runtime_events.append(event)

    # ─── Administer ────────────────────────────────────────────
    def execute_administer(self, stmt: AdministerStmt):
        moiss_class = self.moiss.classify(5.0, stmt.drug_name)
        event = {
            'type': 'ADMINISTER',
            'drug': stmt.drug_name,
            'dose': f"{stmt.dose_amount} {stmt.dose_unit}",
            'moiss_class': moiss_class
        }
        self.log(f"[Administer] {stmt.drug_name} {stmt.dose_amount} {stmt.dose_unit} | MOISS: {moiss_class}")
        self.runtime_events.append(event)

    # ─── If/Else ───────────────────────────────────────────────
    def execute_if(self, stmt: IfStmt):
        result = self.evaluate_expr(stmt.condition)
        self.log(f"[If] condition -> {result}")
        if result:
            for s in stmt.then_block:
                self.execute_statement(s)
        elif stmt.else_block:
            for s in stmt.else_block:
                self.execute_statement(s)

    # ─── Let ───────────────────────────────────────────────────
    def execute_let(self, stmt: LetStmt):
        value = self.evaluate_expr(stmt.value)
        self.scope[stmt.name] = {'type': stmt.type_name or 'auto', 'value': value}
        self.log(f"[Let] {stmt.name} = {value}")
        self.runtime_events.append({'type': 'LET', 'name': stmt.name, 'value': value})

    # ─── While ─────────────────────────────────────────────────
    def execute_while(self, stmt: WhileStmt):
        iterations = 0
        while self.evaluate_expr(stmt.condition):
            if iterations >= self.MAX_LOOP_ITERATIONS:
                self.log(f"[While] Safety limit: loop exceeded {self.MAX_LOOP_ITERATIONS} iterations")
                break
            for s in stmt.body:
                self.execute_statement(s)
            iterations += 1
        self.log(f"[While] Completed after {iterations} iterations")

    # ─── For-Each ──────────────────────────────────────────────
    def execute_for_each(self, stmt: ForEachStmt):
        iterable = self.evaluate_expr(stmt.iterable)
        if not hasattr(iterable, '__iter__'):
            self.log(f"[ForEach] Error: expression is not iterable")
            return

        count = 0
        for item in iterable:
            if count >= self.MAX_LOOP_ITERATIONS:
                self.log("[ForEach] Safety limit reached")
                break
            self.scope[stmt.var_name] = {'type': 'auto', 'value': item}
            for s in stmt.body:
                self.execute_statement(s)
            count += 1

        self.log(f"[ForEach] Iterated {count} items")
        self.runtime_events.append({'type': 'FOR_EACH', 'var': stmt.var_name, 'count': count})

    # ─── Assess ────────────────────────────────────────────────
    def execute_assess(self, stmt: AssessStmt):
        target_val = self.resolve_member(stmt.target)
        condition = stmt.condition
        self.log(f"[Assess] Evaluating {stmt.target} for {condition}...")

        if condition == "sepsis" and hasattr(target_val, 'rr'):
            lib = self.scope[self.LIBRARY_PREFIX]['value']
            score = lib.scores.qsofa(target_val)
            risk = "HIGH" if score >= 2 else ("MODERATE" if score == 1 else "LOW")
            result = {'type': 'ASSESS', 'condition': condition,
                      'score': score, 'scoring': 'qSOFA', 'risk': risk}
        else:
            result = {'type': 'ASSESS', 'condition': condition, 'status': 'evaluated'}

        self.log(f"[Assess] Result: {result}")
        self.runtime_events.append(result)

    # ─── Alert ─────────────────────────────────────────────────
    def execute_alert(self, stmt: AlertStmt):
        message = self.evaluate_expr(stmt.message)
        severity = stmt.severity
        icons = {'critical': '🚨', 'warning': '⚠️', 'info': 'ℹ️'}
        icon = icons.get(severity, '🔔')

        event = {'type': 'ALERT', 'message': message, 'severity': severity}
        self.log(f"[Alert] {icon} [{severity.upper()}] {message}")
        self.runtime_events.append(event)

    # ─── Return ────────────────────────────────────────────────
    def execute_return(self, stmt: ReturnStmt):
        value = self.evaluate_expr(stmt.value) if stmt.value else None
        raise ReturnException(value)

    # ─── Expression Evaluation ─────────────────────────────────
    def evaluate_expr(self, expr) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, ListLiteral):
            return [self.evaluate_expr(e) for e in expr.elements]
        elif isinstance(expr, ConstructorCall):
            return self._construct_instance(expr)
        elif isinstance(expr, IndexAccess):
            obj = self.evaluate_expr(expr.object)
            idx = self.evaluate_expr(expr.index)
            if isinstance(obj, list):
                return obj[int(idx)]
            elif isinstance(obj, dict):
                return obj[idx]
            return None
        elif isinstance(expr, UnaryOp):
            val = self.evaluate_expr(expr.operand)
            if expr.op == '-':
                return -val
            elif expr.op == 'not':
                return not val
            return val
        elif isinstance(expr, Identifier):
            name = expr.name
            if '.' in name:
                return self.resolve_member(name)
            if name in self.scope:
                return self.scope[name]['value']
            return name
        elif isinstance(expr, FunctionCall):
            return self.execute_function_call(expr)
        elif isinstance(expr, BinaryOp):
            left = self.evaluate_expr(expr.left)
            right = self.evaluate_expr(expr.right)
            return self._eval_binary(left, expr.op, right)
        return None

    def _eval_binary(self, left, op, right):
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else 0,
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '<=': lambda a, b: a <= b,
            '>=': lambda a, b: a >= b,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b,
        }
        fn = ops.get(op)
        if fn:
            try:
                return fn(left, right)
            except TypeError:
                return False
        return False

    # ─── Function Calls ────────────────────────────────────────
    def execute_function_call(self, call: FunctionCall) -> Any:
        name = call.function_name
        args = [self.evaluate_expr(a) for a in call.arguments]

        if name in self.user_functions:
            return self._call_user_function(name, args)
        if '.' in name:
            return self._call_dotted(name, args)
        return None

    def _call_user_function(self, name: str, args: List) -> Any:
        func_def = self.user_functions[name]
        saved_scope = dict(self.scope)

        for i, param in enumerate(func_def.params):
            if i < len(args):
                self.scope[param.name] = {'type': param.type_name or 'auto', 'value': args[i]}

        result = None
        try:
            for stmt in func_def.body:
                self.execute_statement(stmt)
        except ReturnException as ret:
            result = ret.value

        for param in func_def.params:
            if param.name in saved_scope:
                self.scope[param.name] = saved_scope[param.name]
            elif param.name in self.scope:
                del self.scope[param.name]

        return result

    def _call_dotted(self, name: str, args: List) -> Any:
        parts = name.split('.')
        if len(parts) < 2:
            return None

        obj_name = parts[0]
        if obj_name not in self.scope:
            return None

        current = self.scope[obj_name]['value']
        for part in parts[1:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        method_name = parts[-1]
        if hasattr(current, method_name):
            method = getattr(current, method_name)
            if callable(method):
                result = method(*args)
                event = {'type': f'{obj_name.upper()}_CALL', 'method': name, 'result': result}
                self.runtime_events.append(event)
                return result
            return method
        return None

    # ─── Custom Type Instance Creation ─────────────────────────
    def _create_instance(self, type_name: str) -> Dict:
        """Create a default instance of a registered custom type."""
        if type_name not in self.user_types:
            return {}

        type_def = self.user_types[type_name]
        instance = {'__type__': type_name}

        if type_def.parent and type_def.parent in self.user_types:
            parent_instance = self._create_instance(type_def.parent)
            instance.update(parent_instance)

        for field in type_def.fields:
            if field.default_value:
                instance[field.name] = self.evaluate_expr(field.default_value)
            else:
                instance[field.name] = None

        instance['__type__'] = type_name
        return instance

    def _construct_instance(self, expr: ConstructorCall) -> Dict:
        """Create an instance from a constructor call with field values."""
        instance = self._create_instance(expr.type_name)
        for field_name, value_expr in expr.field_values:
            instance[field_name] = self.evaluate_expr(value_expr)
        self.log(f"[Constructor] Created {expr.type_name}: {instance}")
        return instance

    # ─── Member Resolution ─────────────────────────────────────
    def resolve_member(self, path: str):
        """Resolve a dotted path (e.g. p.hr) against the current scope."""
        parts = path.split('.')
        obj_name = parts[0]

        if obj_name not in self.scope:
            return 0

        current_obj = self.scope[obj_name]['value']
        for part in parts[1:]:
            if isinstance(current_obj, dict) and part in current_obj:
                current_obj = current_obj[part]
            elif hasattr(current_obj, part):
                current_obj = getattr(current_obj, part)
            else:
                return 0
        return current_obj

    # ─── Logging ───────────────────────────────────────────────
    def log(self, message: str):
        idx = len(self.runtime_events) + 1
        print(f"  [{idx}] LOG: {message}")
        self.runtime_events.append({'type': 'LOG', 'message': message})
