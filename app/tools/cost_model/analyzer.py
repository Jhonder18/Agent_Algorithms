# app/tools/cost_model/analyzer.py
from typing import Dict, List, Tuple
import sympy as sp
from sympy import sympify, simplify

from app.tools.ast_parser.ast_nodes import (
    Program, Function, Block, Stmt,
    For, While, If, Assign, Return, ExprStmt,
    Expr, Var, Literal, BinOp, Compare, ArrayAccess
)


class CostExpr:
    def __init__(self, best: str = "0", avg: str = "0", worst: str = "0"):
        self.best = best
        self.avg = avg
        self.worst = worst


class NodeCost:
    def __init__(self, node_id: str, node_type: str, cost: CostExpr, own_cost: CostExpr = None,
                 line_start: int = None, line_end: int = None, code_snippet: str = None, loop_info=None):
        self.node_id = node_id
        self.node_type = node_type
        self.cost = cost
        self.own_cost = own_cost or CostExpr()
        self.line_start = line_start
        self.line_end = line_end
        self.code_snippet = code_snippet
        self.loop_info = loop_info


class LineCost:
    def __init__(self, line_number: int, code: str, operations: List[str], cost: CostExpr):
        self.line_number = line_number
        self.code = code
        self.operations = operations
        self.cost = cost


class LoopInfo:
    def __init__(self, var: str, start: str, end: str):
        self.var = var
        self.start = start
        self.end = end


class CostsOut:
    def __init__(self, per_node: List[NodeCost], per_line: List[LineCost], total: CostExpr):
        self.per_node = per_node
        self.per_line = per_line
        self.total = total
    
    def to_dict(self):
        return {
            "per_node": [
                {
                    "node_id": nc.node_id,
                    "node_type": nc.node_type,
                    "line_start": nc.line_start,
                    "line_end": nc.line_end,
                    "code_snippet": nc.code_snippet,
                    "cost": {"best": nc.cost.best, "avg": nc.cost.avg, "worst": nc.cost.worst},
                    "own_cost": {"best": nc.own_cost.best, "avg": nc.own_cost.avg, "worst": nc.own_cost.worst} if nc.own_cost else None,
                    "execution_count": None,
                    "loop_info": {"var": nc.loop_info.var, "start": nc.loop_info.start, "end": nc.loop_info.end} if nc.loop_info else None
                }
                for nc in self.per_node
            ],
            "per_line": [
                {
                    "line_number": lc.line_number,
                    "code": lc.code,
                    "operations": lc.operations,
                    "cost": {"best": lc.cost.best, "avg": lc.cost.avg, "worst": lc.cost.worst}
                }
                for lc in self.per_line
            ],
            "total": {"best": self.total.best, "avg": self.total.avg, "worst": self.total.worst}
        }


class CostContext:
    def __init__(self):
        self.node_counter = 0
        self.loop_depth = 0
        self.var_mapping: Dict[str, str] = {}
        self.execution_multipliers: List[str] = []

    def next_id(self, prefix: str = "N") -> str:
        self.node_counter += 1
        return f"{prefix}{self.node_counter}"

    def next_loop_var(self) -> str:
        vars_ = ['i', 'j', 'k', 'l', 'm', 'p', 'q', 'r']
        return vars_[self.loop_depth] if self.loop_depth < len(vars_) else f"v{self.loop_depth}"

    def replace_vars(self, expr: str) -> str:
        out = expr
        for orig, repl in self.var_mapping.items():
            out = out.replace(orig, repl)
        return out


class CostAnalyzer:
    COUNT_LOOP_CONTROL = False
    INCREMENT_STYLE = "unit"
    DEFAULT_P_TRUE = 0.5

    def __init__(self):
        self.context = CostContext()
        self.costs = []  # Mantener para compatibilidad con _generate_line_costs

    @staticmethod
    def _simplify_expr(expr_str: str) -> str:
        if not expr_str or expr_str in ("0", "1"):
            return expr_str
        try:
            return str(simplify(sympify(expr_str, evaluate=True)))
        except Exception:
            return expr_str

    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        self.context = CostContext()
        self.costs = []  # Resetear la lista de nodos
        _ = self._analyze_program(program)
        per_line = self._generate_line_costs(source_code) if source_code else []
        total = self._sum_from_lines(per_line) if per_line else CostExpr(best="0", avg="0", worst="0")
        return CostsOut(per_node=[], per_line=per_line, total=total)

    def _analyze_program(self, program: Program) -> CostExpr:
        fn_costs = [self._analyze_function(f) for f in program.functions]
        total = self._sum_costs(fn_costs) if fn_costs else CostExpr(best="0", avg="0", worst="0")
        return total

    def _analyze_function(self, func: Function) -> CostExpr:
        cost = self._analyze_block(func.body)
        return cost

    def _analyze_block(self, block: Block) -> CostExpr:
        if not block.statements:
            return CostExpr(best="0", avg="0", worst="0")
        return self._sum_costs([self._analyze_statement(s) for s in block.statements])

    def _analyze_statement(self, stmt: Stmt) -> CostExpr:
        if isinstance(stmt, For):    return self._analyze_for(stmt)
        if isinstance(stmt, While):  return self._analyze_while(stmt)
        if isinstance(stmt, If):     return self._analyze_if(stmt)
        if isinstance(stmt, Assign): return self._analyze_assign(stmt)
        if isinstance(stmt, Return): return CostExpr(best="1", avg="1", worst="1")
        if isinstance(stmt, ExprStmt): return self._analyze_expr_stmt(stmt)
        return CostExpr(best="1", avg="1", worst="1")

    def _analyze_for(self, for_stmt: For) -> CostExpr:
        iter_var = self.context.next_loop_var()
        self.context.var_mapping[for_stmt.var] = iter_var
        self.context.loop_depth += 1
        body_cost = self._analyze_block(for_stmt.body)
        self.context.loop_depth -= 1
        del self.context.var_mapping[for_stmt.var]

        start = self.context.replace_vars(self._expr_to_str(for_stmt.start))
        end   = self.context.replace_vars(self._expr_to_str(for_stmt.end))
        b, a, w = (self.context.replace_vars(body_cost.best),
                   self.context.replace_vars(body_cost.avg),
                   self.context.replace_vars(body_cost.worst))

        sum_best  = self._create_sum(b, iter_var, start, end)
        sum_avg   = self._create_sum(a, iter_var, start, end)
        sum_worst = self._create_sum(w, iter_var, start, end)

        if self.COUNT_LOOP_CONTROL:
            init_cost = "1"
            tests_cost = f"(({end}) - ({start}) + 2)"
            inc = f"(({end}) - ({start}) + 1)"
            if self.INCREMENT_STYLE != "unit":
                inc = f"2*{inc}"
            control = self._add_terms([init_cost, tests_cost, inc])
            sum_best  = self._add_terms([sum_best, control])
            sum_avg   = self._add_terms([sum_avg, control])
            sum_worst = self._add_terms([sum_worst, control])
            own_cost = CostExpr(best=control, avg=control, worst=control)
        else:
            own_cost = CostExpr(best="0", avg="0", worst="0")

        cost = CostExpr(best=sum_best, avg=sum_avg, worst=sum_worst)
        
        # Guardar nodo para _generate_line_costs
        loop_info = LoopInfo(var=iter_var, start=start, end=end)
        node = NodeCost(
            node_id=self.context.next_id("for"),
            node_type="For",
            cost=cost,
            own_cost=own_cost,
            line_start=getattr(for_stmt, 'line_start', None),
            line_end=getattr(for_stmt, 'line_end', None),
            loop_info=loop_info
        )
        self.costs.append(node)
        
        return cost

    def _analyze_while(self, while_stmt: While) -> CostExpr:
        guard = self._cost_of_expr(while_stmt.cond)
        is_nested = self.context.loop_depth > 0
        
        # Guardar la profundidad actual para obtener la variable del bucle padre
        parent_depth = self.context.loop_depth - 1 if is_nested else -1
        
        self.context.loop_depth += 1
        iter_var = self.context.next_loop_var()
        body = self._analyze_block(while_stmt.body)
        self.context.loop_depth -= 1

        # Determinar el límite superior del while basado en el contexto
        if is_nested and parent_depth >= 0:
            # Obtener la variable del bucle padre
            vars_ = ['i', 'j', 'k', 'l', 'm', 'p', 'q', 'r']
            parent_var = vars_[parent_depth] if parent_depth < len(vars_) else f"v{parent_depth}"
            # Para while anidado dentro de for, asumimos que itera hasta la variable del for padre
            M_avg = parent_var  # Caso promedio: toda la variable del for
            M_worst = parent_var  # Peor caso: toda la variable del for
        else:
            # While no anidado o anidado en estructura no reconocida
            M_avg, M_worst = "n/2", "n"

        # Costos de las guardas y cuerpo
        # MEJOR CASO: El while evalúa la guarda una vez y NO entra al cuerpo
        # - La guarda se evalúa: guard
        # - El cuerpo NO se ejecuta: 0
        guard_best = guard
        
        # CASO PROMEDIO/PEOR: El while itera M veces
        # - La guarda se evalúa M+1 veces (una vez más para salir)
        # - El cuerpo se ejecuta M veces
        guard_sum_avg   = self._create_sum(guard, iter_var, "1", M_avg)
        guard_sum_worst = self._create_sum(guard, iter_var, "1", M_worst)
        body_avg        = self._create_sum(body.avg,   iter_var, "1", M_avg)
        body_worst      = self._create_sum(body.worst, iter_var, "1", M_worst)

        # El costo total del while
        best  = guard_best  # Solo evalúa la guarda, no entra al cuerpo
        avg   = self._add_terms([guard_sum_avg,  body_avg])
        worst = self._add_terms([guard_sum_worst, body_worst])

        cost = CostExpr(best=best, avg=avg, worst=worst)
        
        # Guardar nodo para _generate_line_costs
        # El own_cost del while es el costo de evaluar la guarda
        loop_info = LoopInfo(var=iter_var, start="1", end=M_worst)
        node = NodeCost(
            node_id=self.context.next_id("while"),
            node_type="While",
            cost=cost,
            own_cost=CostExpr(best=guard_best, avg=guard_sum_avg, worst=guard_sum_worst),
            line_start=getattr(while_stmt, 'line_start', None),
            line_end=getattr(while_stmt, 'line_end', None),
            loop_info=loop_info
        )
        self.costs.append(node)
        
        return cost

    def _analyze_if(self, if_stmt: If) -> CostExpr:
        guard = self._cost_of_expr(if_stmt.cond)
        then_c = self._analyze_block(if_stmt.then_block)
        else_c = self._analyze_block(if_stmt.else_block) if if_stmt.else_block else CostExpr(best="0", avg="0", worst="0")

        best  = self._add_terms([guard, self._min_cost(then_c.best, else_c.best)])
        p = str(self.DEFAULT_P_TRUE); q = str(1 - self.DEFAULT_P_TRUE)
        avg   = self._add_terms([guard, self._multiply_terms(p, then_c.avg), self._multiply_terms(q, else_c.avg)])
        worst = self._add_terms([guard, self._max_cost(then_c.worst, else_c.worst)])

        cost = CostExpr(best=best, avg=avg, worst=worst)
        
        # Guardar nodo para _generate_line_costs
        node = NodeCost(
            node_id=self.context.next_id("if"),
            node_type="If",
            cost=cost,
            own_cost=CostExpr(best=guard, avg=guard, worst=guard),
            line_start=getattr(if_stmt, 'line_start', None),
            line_end=getattr(if_stmt, 'line_end', None)
        )
        self.costs.append(node)
        
        return cost

    def _analyze_assign(self, assign: Assign) -> CostExpr:
        rhs = self._cost_of_expr(assign.value)
        total = self._add_terms(["1", rhs])
        cost = CostExpr(best=total, avg=total, worst=total)
        
        # Guardar nodo para _generate_line_costs
        node = NodeCost(
            node_id=self.context.next_id("assign"),
            node_type="Assign",
            cost=cost,
            own_cost=cost,
            line_start=getattr(assign, 'line_start', None),
            line_end=getattr(assign, 'line_end', None)
        )
        self.costs.append(node)
        
        return cost

    def _analyze_expr_stmt(self, expr_stmt: ExprStmt) -> CostExpr:
        ec = self._cost_of_expr(expr_stmt.expr) or "0"
        cost = CostExpr(best=ec, avg=ec, worst=ec)
        return cost

    def _extract_line_info(self, stmt: Stmt) -> Tuple[int | None, int | None, str | None]:
        ls = getattr(stmt, 'line_start', None)
        le = getattr(stmt, 'line_end', None)
        snippet = None
        t = stmt.__class__.__name__
        if t == 'For' and hasattr(stmt, 'var'): snippet = f"for {stmt.var} ← ... to ..."
        elif t == 'While':  snippet = "while ..."
        elif t == 'If':     snippet = "if ..."
        elif t == 'Assign': snippet = f"{getattr(getattr(stmt, 'target', None), 'name', '...')} ← ..."
        elif t == 'Return': snippet = "return ..."
        return ls, le, snippet

    def _cost_of_expr(self, expr: Expr) -> str:
        if isinstance(expr, (Literal, Var)): return "0"
        if isinstance(expr, BinOp):
            return self._add_terms(["1", self._cost_of_expr(expr.left), self._cost_of_expr(expr.right)])
        if isinstance(expr, Compare):
            return self._add_terms(["1", self._cost_of_expr(expr.left), self._cost_of_expr(expr.right)])
        return "0"

    def _add_terms(self, terms: List[str]) -> str:
        nz = [t for t in terms if t and t != "0"]
        if not nz: return "0"
        if len(nz) == 1: return nz[0]
        return " + ".join(nz)

    def _multiply_terms(self, factor: str, expr: str) -> str:
        if factor == "0" or expr == "0": return "0"
        if factor == "1": return expr
        if expr == "1": return factor
        return f"{factor}*({expr})" if ("+" in expr or "-" in expr) else f"{factor}*{expr}"

    def _sum_costs(self, costs: List[CostExpr]) -> CostExpr:
        if not costs: return CostExpr(best="0", avg="0", worst="0")
        if len(costs) == 1: return costs[0]
        def join(xs):
            xs = [x for x in xs if x != "0"]
            return " + ".join(xs) if xs else "0"
        return CostExpr(
            best=join([c.best for c in costs]),
            avg=join([c.avg for c in costs]),
            worst=join([c.worst for c in costs]),
        )

    def _create_sum(self, inner: str, var: str, start: str, end: str) -> str:
        return "0" if inner == "0" else f"Sum({inner}, ({var}, {start}, {end}))"

    def _expr_to_str(self, expr: Expr) -> str:
        if isinstance(expr, Literal): return str(expr.value)
        if isinstance(expr, Var):     return expr.name
        if isinstance(expr, ArrayAccess):
            # Para A[i][j], extraer solo el índice más profundo (j)
            index_str = self._expr_to_str(expr.index)
            return index_str
        if isinstance(expr, BinOp):   return f"({self._expr_to_str(expr.left)} {expr.op} {self._expr_to_str(expr.right)})"
        if isinstance(expr, Compare): return f"({self._expr_to_str(expr.left)} {expr.op} {self._expr_to_str(expr.right)})"
        return "n"

    def _min_cost(self, a: str, b: str) -> str:
        if a == "0" or b == "0": return "0"
        return a if a == b else f"min({a}, {b})"

    def _max_cost(self, a: str, b: str) -> str:
        return a if a == b else f"max({a}, {b})"

    def _sum_from_lines(self, per_line: List[LineCost]) -> CostExpr:
        best_terms = [lc.cost.best  for lc in per_line if lc.cost.best  != "0"]
        avg_terms  = [lc.cost.avg   for lc in per_line if lc.cost.avg   != "0"]
        worst_terms= [lc.cost.worst for lc in per_line if lc.cost.worst != "0"]
        return CostExpr(
            best=self._add_terms(best_terms) if best_terms else "0",
            avg=self._add_terms(avg_terms) if avg_terms else "0",
            worst=self._add_terms(worst_terms) if worst_terms else "0",
        )

    def _generate_line_costs(self, source_code: str) -> List[LineCost]:
        if not source_code:
            return []
        lines = source_code.split('\n')

        for_nodes = [n for n in self.costs if n.node_type == "For" and n.loop_info and n.line_start and n.line_end]
        for_nodes.sort(key=lambda n: (n.line_start, -n.line_end))
        if_nodes = [n for n in self.costs if n.node_type == "If" and n.line_start and n.line_end]
        if_nodes.sort(key=lambda n: (n.line_start, -n.line_end))
        while_nodes = [n for n in self.costs if n.node_type == "While" and n.line_start and n.line_end]
        while_nodes.sort(key=lambda n: (n.line_start, -n.line_end))

        line_to_loops: Dict[int, List[Tuple[str, str, str]]] = {}
        for ln in range(1, len(lines) + 1):
            inside = []
            for fn in for_nodes:
                if fn.line_start < ln <= fn.line_end:
                    inside.append((fn.loop_info.var, fn.loop_info.start, fn.loop_info.end))
            if inside:
                line_to_loops[ln] = inside

        line_to_if_depth: Dict[int, int] = {}
        for ln in range(1, len(lines) + 1):
            d = sum(1 for inf in if_nodes if inf.line_start < ln <= inf.line_end)
            if d > 0: line_to_if_depth[ln] = d

        # Detectar líneas dentro del cuerpo de un while (no en la línea del while mismo)
        line_inside_while_body: Dict[int, bool] = {}
        for ln in range(1, len(lines) + 1):
            for wn in while_nodes:
                if wn.line_start < ln <= wn.line_end:
                    line_inside_while_body[ln] = True
                    break

        line_costs_map: Dict[int, Dict[str, List[str]]] = {}
        for node in self.costs:
            if not node.line_start or node.node_type in ['Function', 'Program']:
                continue
            ln = node.line_start

            if node.node_type == 'For':
                if node.loop_info:
                    start, end = node.loop_info.start, node.loop_info.end
                    evals = self._simplify_expr(f"({end}) - ({start}) + 2")
                    loops = line_to_loops.get(ln, [])
                    best = avg = worst = self._wrap_in_sums(evals, loops) if loops else evals
                else:
                    best = avg = worst = "1"

            elif node.node_type == 'While':
                if node.own_cost:
                    base_b, base_a, base_w = node.own_cost.best, node.own_cost.avg, node.own_cost.worst
                    loops = line_to_loops.get(ln, [])
                    if loops:
                        best  = self._wrap_in_sums(base_b, loops)
                        avg   = self._wrap_in_sums(base_a, loops)
                        worst = self._wrap_in_sums(base_w, loops)
                    else:
                        best, avg, worst = base_b, base_a, base_w
                else:
                    best = avg = worst = "0"

            else:
                if not node.own_cost:
                    continue
                loops = line_to_loops.get(ln, [])
                if_depth = line_to_if_depth.get(ln, 0)
                inside_while_body = line_inside_while_body.get(ln, False)
                base_b, base_a, base_w = node.own_cost.best, node.own_cost.avg, node.own_cost.worst
                
                # En el mejor caso: if no ejecuta su cuerpo, while no ejecuta su cuerpo
                if if_depth > 0:
                    base_b = "0"
                    prob = 0.5 ** if_depth
                    if base_a != "0": base_a = f"({prob} * ({base_a}))"
                if inside_while_body:
                    # Si está dentro del cuerpo de un while, en el mejor caso no se ejecuta
                    base_b = "0"
                
                if loops:
                    best = self._wrap_in_sums(base_b, loops)
                    avg  = self._wrap_in_sums(base_a, loops)
                    worst= self._wrap_in_sums(base_w, loops)
                else:
                    best, avg, worst = base_b, base_a, base_w

            line_costs_map.setdefault(ln, {"operations": [], "costs_best": [], "costs_avg": [], "costs_worst": []})
            line_costs_map[ln]["operations"].append(node.node_type)
            line_costs_map[ln]["costs_best"].append(best)
            line_costs_map[ln]["costs_avg"].append(avg)
            line_costs_map[ln]["costs_worst"].append(worst)

        result: List[LineCost] = []
        for ln in sorted(line_costs_map.keys()):
            if 1 <= ln <= len(lines):
                data = line_costs_map[ln]
                result.append(LineCost(
                    line_number=ln,
                    code=lines[ln - 1],
                    operations=data["operations"],
                    cost=CostExpr(
                        best=self._add_terms(data["costs_best"]),
                        avg=self._add_terms(data["costs_avg"]),
                        worst=self._add_terms(data["costs_worst"]),
                    ),
                ))
        return result

    def _wrap_in_sums(self, base: str, loops: List[Tuple[str, str, str]]) -> str:
        out = base
        for var, start, end in reversed(loops):
            out = self._create_sum(out, var, start, end)
        return out


class CostAnalyzerAgent:
    def __init__(self):
        self.analyzer = CostAnalyzer()

    def analyze(self, program: Program, source_code: str = "") -> CostsOut:
        return self.analyzer.analyze(program, source_code)

    def __call__(self, input_data: dict) -> dict:
        try:
            ast = input_data.get("ast")
            if not isinstance(ast, Program):
                raise ValueError("Input 'ast' debe ser Program")
            costs = self.analyze(ast, input_data.get("source_code", ""))
            return {"costs": costs.to_dict(), "success": True, "error": None}
        except Exception as e:
            return {"costs": None, "success": False, "error": str(e)}


_cost_analyzer: CostAnalyzerAgent | None = None

def get_cost_analyzer() -> CostAnalyzerAgent:
    global _cost_analyzer
    if _cost_analyzer is None:
        _cost_analyzer = CostAnalyzerAgent()
    return _cost_analyzer
