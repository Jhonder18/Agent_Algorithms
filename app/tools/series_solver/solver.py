# app/tools/series_solver/solver.py
import re
from typing import Dict, Optional, List, Tuple
import sympy as sp
from sympy import symbols, Sum, simplify, sympify, Poly


class CostExpr:
    def __init__(self, best: str = "0", avg: str = "0", worst: str = "0"):
        self.best = best
        self.avg = avg
        self.worst = worst


class SolutionStep:
    def __init__(self, step_number: int, description: str, expression: str, case: str):
        self.step_number = step_number
        self.description = description
        self.expression = expression
        self.case = case


class ExactCosts:
    def __init__(self, best: str, avg: str, worst: str):
        self.best = best
        self.avg = avg
        self.worst = worst


class AsymptoticBounds:
    def __init__(self, omega: str, theta: str, big_o: str):
        self.omega = omega
        self.theta = theta
        self.big_o = big_o


class SolveOut:
    def __init__(self, steps: List[SolutionStep], steps_by_line: List[SolutionStep],
                 exact: ExactCosts, big_o: ExactCosts, bounds: AsymptoticBounds):
        self.steps = steps
        self.steps_by_line = steps_by_line
        self.exact = exact
        self.big_o = big_o
        self.bounds = bounds
    
    def to_dict(self):
        return {
            "steps": [
                {"step_number": s.step_number, "description": s.description, "expression": s.expression, "case": s.case}
                for s in self.steps
            ],
            "steps_by_line": [
                {"step_number": s.step_number, "description": s.description, "expression": s.expression, "case": s.case}
                for s in self.steps_by_line
            ],
            "exact": {"best": self.exact.best, "avg": self.exact.avg, "worst": self.exact.worst},
            "big_o": {"best": self.big_o.best, "avg": self.big_o.avg, "worst": self.big_o.worst},
            "bounds": {"omega": self.bounds.omega, "theta": self.bounds.theta, "big_o": self.bounds.big_o}
        }


class SeriesSolver:
    def __init__(self):
        self.n = symbols('n', positive=True, integer=True)
        self.i = symbols('i', positive=True, integer=True)
        self.j = symbols('j', positive=True, integer=True)
        self.k = symbols('k', positive=True, integer=True)
        self.m = symbols('m', positive=True, integer=True)
        self._unknown_symbols: Dict[str, sp.Symbol] = {}

    def solve(self, cost_expr: CostExpr, show_steps: bool = True, per_line_costs: list = None) -> SolveOut:
        steps = []
        best_exact, _ = self._solve_expression_with_steps(cost_expr.best, "best", 1)
        avg_exact, _  = self._solve_expression_with_steps(cost_expr.avg,  "avg",  1)
        worst_exact, _= self._solve_expression_with_steps(cost_expr.worst,"worst",1)

        steps_by_line = self._solve_by_line_with_steps(per_line_costs) if (per_line_costs and show_steps) else []

        best_big_o  = self._extract_big_o(best_exact)
        avg_big_o   = self._extract_big_o(avg_exact)
        worst_big_o = self._extract_big_o(worst_exact)

        bounds = self._calculate_bounds(best_exact, avg_exact, worst_exact)

        return SolveOut(
            steps=steps,
            steps_by_line=steps_by_line,
            exact=ExactCosts(best=str(best_exact), avg=str(avg_exact), worst=str(worst_exact)),
            big_o=ExactCosts(best=best_big_o, avg=avg_big_o, worst=worst_big_o),
            bounds=bounds
        )

    def _solve_expression(self, expr_str: str) -> sp.Expr:
        if not expr_str or expr_str == "0":
            return sp.Integer(0)
        try:
            expr = self._parse_expression(expr_str).doit()
            expr = sp.nsimplify(simplify(expr), rational=True)
            try:
                factored = sp.factor(expr)
                if len(str(factored)) <= len(str(expr)):
                    expr = factored
            except Exception:
                pass
            return expr
        except Exception:
            key = f"unknown({expr_str})"
            self._unknown_symbols.setdefault(key, symbols(key))
            return self._unknown_symbols[key]

    def _solve_expression_with_steps(self, expr_str: str, case: str, start_step: int) -> Tuple[sp.Expr, List[SolutionStep]]:
        steps, step = [], start_step
        if not expr_str or expr_str == "0":
            return sp.Integer(0), steps
        try:
            expr = self._parse_expression(expr_str)
            sums = self._find_sums(expr)
            if sums:
                expr_resolved = expr.doit()
                unique, seen = [], set()
                for s in sums:
                    s_str = str(s)
                    if s_str not in seen:
                        seen.add(s_str); unique.append(s)

                for s in unique:
                    if isinstance(s, Sum) and len(s.limits) > 1:
                        cur = s.function
                        limits = list(s.limits)
                        total = len(limits)
                        for idx, lim in enumerate(limits, 1):
                            lvl = Sum(cur, lim); val = lvl.doit()
                            if total == 2:
                                desc = f"Resolver sumatoria {'interna' if idx==1 else 'externa'} (sobre {lim[0]})"
                            else:
                                if idx == 1: desc = f"Resolver sumatoria más interna (nivel {idx}/{total}, sobre {lim[0]})"
                                elif idx == total: desc = f"Resolver sumatoria más externa (nivel {idx}/{total}, sobre {lim[0]})"
                                else: desc = f"Resolver sumatoria intermedia (nivel {idx}/{total}, sobre {lim[0]})"
                            steps.append(SolutionStep(step_number=step, description=desc, expression=f"{lvl} = {val}", case=case))
                            step += 1
                            cur = val
                    else:
                        val = s.doit()
                        steps.append(SolutionStep(step_number=step, description="Resolver sumatoria", expression=f"{s} = {val}", case=case))
                        step += 1

                if str(expr_resolved) != str(expr):
                    steps.append(SolutionStep(step_number=step, description=f"Sustituir sumatorias resueltas ({case})", expression=f"T(n) = {expr_resolved}", case=case))
                    step += 1
                expr = expr_resolved

            simp = simplify(expr)
            if str(simp) != str(expr):
                steps.append(SolutionStep(step_number=step, description=f"Simplificar algebraicamente ({case})", expression=f"T(n) = {simp}", case=case))
                step += 1

            rat = sp.nsimplify(simp, rational=True)
            if str(rat) != str(simp):
                steps.append(SolutionStep(step_number=step, description=f"Convertir a fracciones ({case})", expression=f"T(n) = {rat}", case=case))
                step += 1

            try:
                fac = sp.factor(rat)
                final = fac if str(fac) != str(rat) and len(str(fac)) <= len(str(rat)) else rat
            except Exception:
                final = rat

            steps.append(SolutionStep(step_number=step, description=f"Resultado final ({case})", expression=f"T(n) = {final}", case=case))
            return final, steps
        except Exception:
            key = f"unknown({expr_str})"
            self._unknown_symbols.setdefault(key, symbols(key))
            return self._unknown_symbols[key], steps

    def _solve_by_line_with_steps(self, per_line_costs: list) -> List[SolutionStep]:
        if not per_line_costs:
            return []
        steps, step = [], 1
        
        # Helper para extraer atributos de objetos o dicts
        def get_attr(obj, attr_name, default=None):
            if isinstance(obj, dict):
                return obj.get(attr_name, default)
            return getattr(obj, attr_name, default)
        
        for title, attr in [("best","best"), ("avg","avg"), ("worst","worst")]:
            form = " + ".join([f"C{idx+1}*L{get_attr(lc, 'line_number', idx+1)}" for idx, lc in enumerate(per_line_costs)])
            steps.append(SolutionStep(step_number=step, description=f"Fórmula de costo línea por línea ({title})", expression=f"T(n) = {form}", case=attr)); step += 1

            for lc in per_line_costs:
                line_num = get_attr(lc, 'line_number', 0)
                code = get_attr(lc, 'code', '...')
                lc_cost = get_attr(lc, 'cost', {})
                cost_value = get_attr(lc_cost, attr, '0')
                steps.append(SolutionStep(step_number=step, description=f"Línea {line_num}: {str(code).strip()[:40]}...", expression=f"L{line_num} = {cost_value}", case=attr)); step += 1

            sum_terms = []
            for lc in per_line_costs:
                lc_cost = get_attr(lc, 'cost', {})
                cost_value = get_attr(lc_cost, attr, '0')
                sum_terms.append(f"({cost_value})")
            sum_expr = " + ".join(sum_terms)
            steps.append(SolutionStep(step_number=step, description=f"Simplificar (C1=C2=...=1) ({title})", expression=f"T(n) = {sum_expr}", case=attr)); step += 1

            total, res_steps = self._solve_expression_with_steps(sum_expr, attr, step)
            steps.extend(res_steps); step += len(res_steps)
            steps.append(SolutionStep(step_number=step, description=f"Resultado final línea por línea ({title})", expression=f"T(n) = {total}", case=attr)); step += 1
        return steps

    def _find_sums(self, expr):
        out = []
        if hasattr(expr, 'args'):
            for a in expr.args:
                out.extend(self._find_sums(a))
        if isinstance(expr, Sum):
            out.append(expr)
        return out

    def _parse_expression(self, expr_str: str) -> sp.Expr:
        expr_str = expr_str.replace("^", "**")
        expr_str = re.sub(r'\bmin\b', 'Min', expr_str)
        expr_str = re.sub(r'\bmax\b', 'Max', expr_str)
        ns = {'n': self.n, 'i': self.i, 'j': self.j, 'k': self.k, 'm': self.m, 'Sum': Sum, 'Min': sp.Min, 'Max': sp.Max}
        try:
            expr = eval(expr_str, {"__builtins__": {}}, ns)
            return sp.sympify(expr)
        except Exception as e:
            try:
                return sympify(expr_str, locals=ns)
            except Exception:
                raise ValueError(f"No se pudo parsear: {expr_str}. Error: {e}")

    def _extract_big_o(self, expr: sp.Expr) -> str:
        if expr == 0:
            return "O(1)"
        try:
            if str(expr).startswith("unknown"):
                return f"O({expr})"
            exp = sp.expand(expr)
            terms = exp.as_ordered_terms() if exp.is_Add else [exp]
            
            # Encontrar todas las variables libres en la expresión (excluyendo índices de suma)
            free_vars = exp.free_symbols
            excluded_indices = {self.i, self.j, self.k}  # Índices típicos de bucles
            problem_vars = sorted([v for v in free_vars if v not in excluded_indices], key=str)
            
            if not problem_vars:
                return "O(1)"
            
            # Encontrar el término dominante considerando todas las variables del problema
            max_total_deg = 0
            dom_term = sp.Integer(1)
            
            for t in terms:
                # Calcular el grado total sumando grados de todas las variables
                total_deg = sum(self._get_degree(t, var) for var in problem_vars)
                if total_deg > max_total_deg:
                    max_total_deg = total_deg
                    dom_term = self._extract_multivariable_dependency(t, problem_vars)
            
            if max_total_deg == 0:
                return "O(1)"
            
            # Simplificar notación para casos comunes
            dom_str = str(dom_term)
            if dom_str == "n":
                return "O(n)"
            if dom_str == "n**2":
                return "O(n**2)"
            if dom_str == "n**3":
                return "O(n**3)"
            
            return f"O({dom_term})"
        except Exception:
            return f"O({expr})"

    def _get_degree(self, expr: sp.Expr, var: sp.Symbol) -> int:
        try:
            if expr.is_polynomial(var):
                return Poly(expr, var).degree()
            if expr.has(sp.log):
                return 0
            if expr.has(var):
                mx = 0
                for a in sp.preorder_traversal(expr):
                    if a.is_Pow and a.base == var and a.exp.is_number:
                        mx = max(mx, int(a.exp))
                return mx
            return 0
        except Exception:
            return 0

    def _extract_n_dependency(self, expr: sp.Expr) -> sp.Expr:
        if not expr.has(self.n):
            return sp.Integer(1)
        try:
            if expr.is_Mul:
                parts = [a for a in expr.args if a.has(self.n)]
                return sp.Mul(*parts) if parts else sp.Integer(1)
            if expr.is_Pow and expr.base == self.n:
                return expr
            return expr
        except Exception:
            return expr

    def _extract_multivariable_dependency(self, expr: sp.Expr, variables: list) -> sp.Expr:
        """
        Extrae la dependencia de múltiples variables del término.
        Para 3*m*n, devuelve m*n.
        Para 5*n**2*m, devuelve n**2*m.
        """
        if not any(expr.has(var) for var in variables):
            return sp.Integer(1)
        try:
            if expr.is_Mul:
                # Filtrar solo las partes que contienen alguna de las variables
                parts = [a for a in expr.args if any(a.has(var) for var in variables)]
                return sp.Mul(*parts) if parts else sp.Integer(1)
            if expr.is_Pow and expr.base in variables:
                return expr
            # Para otros casos, devolver solo las partes con variables
            result_parts = []
            for a in sp.preorder_traversal(expr):
                if a in variables or (a.is_Pow and a.base in variables):
                    result_parts.append(a)
            return sp.Mul(*result_parts) if result_parts else expr
        except Exception:
            return expr

    def _calculate_bounds(self, best_expr: sp.Expr, avg_expr: sp.Expr, worst_expr: sp.Expr) -> AsymptoticBounds:
        best_o  = self._extract_big_o(best_expr)
        avg_o   = self._extract_big_o(avg_expr)
        worst_o = self._extract_big_o(worst_expr)
        omega = best_o.replace("O(", "Ω(")
        big_o = worst_o
        theta = best_o.replace("O(", "Θ(") if best_o == worst_o else avg_o.replace("O(", "Θ(")
        return AsymptoticBounds(omega=omega, theta=theta, big_o=big_o)


class SeriesSolverAgent:
    def __init__(self):
        self.solver = SeriesSolver()

    def solve(self, cost_expr: CostExpr, show_steps: bool = True, per_line_costs: list = None) -> SolveOut:
        return self.solver.solve(cost_expr, show_steps=show_steps, per_line_costs=per_line_costs)

    def __call__(self, state: Dict) -> Dict:
        try:
            costs = state.get("costs")
            if costs is None:
                return {"success": False, "error": "No se encontró 'costs' en el estado", "solution": None}

            per_line = None
            if hasattr(costs, "per_line"):
                per_line = costs.per_line
            elif isinstance(costs, dict) and "per_line" in costs:
                per_line = costs["per_line"]

            def _get_case(lc_cost, case):
                if hasattr(lc_cost, case):
                    return getattr(lc_cost, case)
                return lc_cost.get(case, "0")

            if per_line:
                items = per_line if not isinstance(per_line, dict) else list(per_line.values())
                best_terms, avg_terms, worst_terms = [], [], []
                for lc in items:
                    lc_cost = getattr(lc, "cost", None) if not isinstance(lc, dict) else lc.get("cost", {})
                    if not lc_cost:
                        continue
                    b = _get_case(lc_cost, "best");   best_terms.append(f"({b})") if b and b != "0" else None
                    a = _get_case(lc_cost, "avg");    avg_terms.append(f"({a})")  if a and a != "0" else None
                    w = _get_case(lc_cost, "worst");  worst_terms.append(f"({w})") if w and w != "0" else None

                line_total = CostExpr(
                    best=" + ".join(best_terms) if best_terms else "0",
                    avg=" + ".join(avg_terms) if avg_terms else "0",
                    worst=" + ".join(worst_terms) if worst_terms else "0",
                )

                solution = self.solve(line_total, show_steps=True, per_line_costs=items)
                return {"solution": solution.to_dict(), "success": True, "error": None}

            if isinstance(costs, CostExpr):
                sol = self.solve(costs, show_steps=True, per_line_costs=None)
                return {"solution": sol.to_dict(), "success": True, "error": None}

            return {"success": False, "error": "No hay costos por línea para resolver", "solution": None}

        except Exception as e:
            return {"success": False, "error": str(e), "solution": None}


_solver_instance: Optional[SeriesSolverAgent] = None

def get_series_solver() -> SeriesSolverAgent:
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = SeriesSolverAgent()
    return _solver_instance
