# app/tools/ast_parser/parser_agent.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from lark import Lark, Transformer, Tree, Token, v_args
from app.tools.ast_parser.ast_nodes import (
    Program, Function, Param, Block,
    Assign, If, While, For, Return, ExprStmt,
    VarDeclaration, CallStatement, ActionStatement,
    Var, Literal, BinOp, UnOp, Compare, Call, ArrayAccess, ArrayLiteral,
    Expr, Stmt
)


# =========================
# Transformer (Lark -> AST)
# =========================
class PseudocodeToASTTransformer(Transformer):
    """Transforma el árbol de Lark a nuestro IR (AST) tipado."""

    # Utilidades
    def _block(self, children: List[Stmt]) -> Block:
        return Block(statements=[c for c in children if isinstance(c, Stmt)])

    def _meta_lines(self, meta) -> tuple[Optional[int], Optional[int]]:
        return getattr(meta, "line", None), getattr(meta, "end_line", None)

    # ===== Programa / funciones =====
    def start(self, children):
        functions = [c for c in children if isinstance(c, Function)]
        return Program(functions=functions)

    def statement(self, children):
        return children[0]

    def procedure_def(self, children):
        """
        Regla en gramática:
        procedure_def: "procedimiento" NAME "(" [parameter_list] ")" "begin" statement* "end"
                     | NAME "(" [parameter_list] ")" "begin" statement* "end"
        """
        name = str(children[0])
        params: List[Param] = []
        stmts: List[Stmt] = []
        for ch in children[1:]:
            if isinstance(ch, list):
                params = ch
            elif isinstance(ch, Stmt):
                stmts.append(ch)
        return Function(name=name, params=params, body=Block(statements=stmts))

    def parameter_list(self, children):
        return children

    def parameter(self, children):
        # Soporta NAME, NAME [array], "Clase" NAME (simplificado a Param con nombre)
        for ch in children:
            if isinstance(ch, Token) and ch.type == "NAME":
                return Param(name=str(ch))
        return Param(name="")

    # ===== Sentencias =====
    @v_args(meta=True)
    def assignment(self, meta, children):
        line_start, line_end = self._meta_lines(meta)
        return Assign(
            target=children[0],
            value=children[1],
            line_start=line_start,
            line_end=line_end,
        )

    @v_args(meta=True)
    def var_declaration(self, meta, children):
        names = [str(tok) for tok in children if isinstance(tok, Token)]
        line_start, line_end = self._meta_lines(meta)
        return VarDeclaration(names=names, line_start=line_start, line_end=line_end)

    def lvalue(self, children):
        # NAME | NAME[expr] | NAME . NAME
        if len(children) == 1:
            return Var(name=str(children[0]))
        name = str(children[0])
        second = children[1]
        if isinstance(second, Expr):
            return ArrayAccess(array=Var(name=name), index=second)
        return Var(name=f"{name}.{second}")

    @v_args(meta=True)
    def if_statement(self, meta, children):
        cond, then_block = children[0], children[1]
        else_block = children[2] if len(children) > 2 else None
        line_start, line_end = self._meta_lines(meta)
        return If(
            cond=cond,
            then_block=then_block,
            else_block=else_block,
            line_start=line_start,
            line_end=line_end,
        )

    def then_part(self, children):
        return self._block(children)

    def else_part(self, children):
        return self._block(children)

    @v_args(meta=True)
    def while_loop(self, meta, children):
        cond = children[0]
        body = self._block(children[1:])
        line_start, line_end = self._meta_lines(meta)
        return While(
            cond=cond,
            body=body,
            line_start=line_start,
            line_end=line_end,
        )

    @v_args(meta=True)
    def for_loop(self, meta, children):
        # for NAME 🡨 expr to expr do begin ... end
        var_name = str(children[0])
        start, end = children[1], children[2]
        body = self._block(children[3:])
        line_start, line_end = self._meta_lines(meta)
        return For(
            var=var_name,
            start=start,
            end=end,
            body=body,
            line_start=line_start,
            line_end=line_end,
        )

    @v_args(meta=True)
    def repeat_loop(self, meta, children):
        # repeat begin ... end until condition  ==> while (not condition) do ...
        *body_nodes, cond = children
        body = self._block(body_nodes)
        line_start, line_end = self._meta_lines(meta)
        return While(
            cond=UnOp(op="not", operand=cond),
            body=body,
            line_start=line_start,
            line_end=line_end,
        )

    @v_args(meta=True)
    def return_statement(self, meta, children):
        line_start, line_end = self._meta_lines(meta)
        return Return(
            value=children[0] if children else None,
            line_start=line_start,
            line_end=line_end,
        )

    def expr_stmt(self, children):
        return ExprStmt(expr=children[0])

    @v_args(meta=True)
    def call_statement(self, meta, children):
        name = str(children[0])
        args = children[1] if len(children) > 1 and isinstance(children[1], list) else []
        line_start, line_end = self._meta_lines(meta)
        return CallStatement(name=name, args=args, line_start=line_start, line_end=line_end)

    @v_args(meta=True)
    def action_statement(self, meta, _children):
        line_start, line_end = self._meta_lines(meta)
        return ActionStatement(line_start=line_start, line_end=line_end)

    # ===== Expresiones =====
    def expr(self, children):
        return children[0]

    def or_expr(self, children):
        if len(children) == 1:
            return children[0]
        res = children[0]
        for ch in children[1:]:
            if isinstance(ch, Token):
                continue
            res = BinOp(op="or", left=res, right=ch)
        return res

    def and_expr(self, children):
        if len(children) == 1:
            return children[0]
        res = children[0]
        for ch in children[1:]:
            if isinstance(ch, Token):
                continue
            res = BinOp(op="and", left=res, right=ch)
        return res

    def not_expr(self, children):
        return UnOp(op="not", operand=children[1]) if len(children) == 2 else children[0]

    def comparison(self, children):
        if len(children) == 1:
            return children[0]
        left, op_token, right = children[0], children[1], children[2]
        op_map = {
            "=": "==", "==": "==",
            "≠": "!=", "!=": "!=", "<>": "!=",
            "≤": "<=", "<=": "<=",
            "≥": ">=", ">=": ">=",
            "<": "<", ">": ">"
        }
        op = op_map.get(str(op_token), str(op_token))
        return Compare(op=op, left=left, right=right)

    def arith_expr(self, children):
        if len(children) == 1:
            return children[0]
        res, i = children[0], 1
        while i < len(children):
            res = BinOp(op=str(children[i]), left=res, right=children[i + 1])
            i += 2
        return res

    def term(self, children):
        if len(children) == 1:
            return children[0]
        res, i = children[0], 1
        while i < len(children):
            res = BinOp(op=str(children[i]), left=res, right=children[i + 1])
            i += 2
        return res

    def condition(self, children):
        return children[0]

    # ----- Átomos -----
    def number(self, children):
        val = str(children[0])
        return Literal(value=int(val) if "." not in val else float(val))

    def variable(self, children):
        return Var(name=str(children[0]))

    def function_call(self, children):
        name = str(children[0])
        args = children[1] if len(children) > 1 and isinstance(children[1], list) else []
        return Call(name=name, args=args)

    def argument_list(self, children):
        return children

    def array_access(self, children):
        # NAME "[" expression "]" ("[" expression "]")*
        base: Union[Var, ArrayAccess] = ArrayAccess(array=Var(name=str(children[0])), index=children[1])
        for extra in children[2:]:
            if isinstance(extra, Expr):
                base = ArrayAccess(array=base, index=extra)
        return base

    def field_access(self, children):
        return Var(name=f"{children[0]}.{children[1]}")

    def array_literal(self, children):
        elements = [child for child in children if isinstance(child, Expr)]
        return ArrayLiteral(elements=elements)

    def ceiling(self, children):
        return Call(name="ceil", args=[children[0]])

    def floor(self, children):
        return Call(name="floor", args=[children[0]])

    # Opcionales de la gramática (si se usan)
    def true_value(self, _):  # "T"
        return Literal(value=True)

    def false_value(self, _):  # "F"
        return Literal(value=False)

    def null_value(self, _):  # "NULL"
        return Literal(value=None)


# =========================
# Agente de parseo (servicio)
# =========================
class ParserAgent:
    """
    Convierte pseudocódigo a AST tipado usando la gramática Lark compartida.
    Retorna dict con: {"ast": Program | None, "success": bool, "error": str | None}
    """

    def __init__(self):
        # grammar.lark: app/tools/ast_parser/grammar/grammar.lark
        self.grammar_path = (
            Path(__file__).parent / "grammar" / "grammar.lark"
        )
        self.transformer = PseudocodeToASTTransformer()
        self._load_grammar()

    def _load_grammar(self):
        if not self.grammar_path.exists():
            raise FileNotFoundError(f"Gramática no encontrada: {self.grammar_path}")
        with open(self.grammar_path, "r", encoding="utf-8") as f:
            grammar = f.read()
        self.parser = Lark(
            grammar,
            start="start",
            parser="lalr",
            propagate_positions=True,
            maybe_placeholders=False,
        )

    def parse(self, pseudocode: str) -> Program:
        tree = self.parser.parse(pseudocode)
        return self.transformer.transform(tree)

    def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            ast = self.parse(input_data.get("pseudocode", "") or "")
            return {"ast": ast, "success": True, "error": None}
        except Exception as e:
            return {"ast": None, "success": False, "error": str(e)}


# Singleton para no re-cargar gramática cada vez
_parser_agent: Optional[ParserAgent] = None

def get_parser_agent() -> ParserAgent:
    global _parser_agent
    if _parser_agent is None:
        _parser_agent = ParserAgent()
    return _parser_agent

__all__ = ["get_parser_agent", "ParserAgent", "PseudocodeToASTTransformer"]
