# app/agents/nodes/validate.py
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Tuple

from app.constants import ARROW
from app.agents.state import AnalyzerState, update_metadata
from app.tools.ast_parser.parser_agent import get_parser_agent
from app.services.llm import get_llm, strip_code_fences

# Por defecto intentamos reparar con LLM si Lark falla
REPAIR_MODE = os.getenv("VALIDATION_REPAIR_MODE", "llm").lower()


# ---------------------------
# Normalización barata
# ---------------------------
def _simple_normalize(code: str) -> Tuple[str, List[str]]:
    changes: List[str] = []
    new = code

    # Flechas
    if "->" in new or "←" in new:
        new = new.replace("->", ARROW).replace("←", ARROW)
        changes.append("Reemplazo de asignación por flecha")

    # Palabras clave a minúscula
    for kw in [
        "BEGIN", "END", "FOR", "WHILE", "IF", "ELSE",
        "REPEAT", "UNTIL", "RETURN", "AND", "OR",
        "NOT", "DO", "THEN", "PROCEDIMIENTO",
    ]:
        if kw in new:
            new = re.sub(rf"\b{kw}\b", kw.lower(), new)
            changes.append(f"Lowercase de '{kw}'")

    if re.search(r"\bcall\b", new, flags=re.I):
        new = re.sub(r"\bcall\b", "CALL", new, flags=re.I)
        changes.append("Normalización de 'CALL' a mayúsculas")

    # Newline final
    if not new.endswith("\n"):
        new += "\n"
        changes.append("Nueva línea añadida al final")

    return new, changes


def _ensure_balanced_blocks(code: str) -> Tuple[str, List[str]]:
    """
    Asegura que exista el mismo número de 'begin' y 'end' añadiendo los que falten
    al final del pseudocódigo. No intenta remover 'end' extra.
    """
    notes: List[str] = []
    begins = len(re.findall(r"\bbegin\b", code, flags=re.I))
    ends = len(re.findall(r"\bend\b", code, flags=re.I))

    if begins > ends:
        missing = begins - ends
        addition = "\n".join("end" for _ in range(missing))
        code = code.rstrip() + "\n" + addition + "\n"
        notes.append(f"Se añadieron {missing} 'end' faltantes al final")

    return code, notes


# ---------------------------
# Validar con Lark
# ---------------------------
def _parse_with_lark(code: str) -> Tuple[bool, str | None]:
    agent = get_parser_agent()
    try:
        agent.parser.parse(code)
        return True, None
    except Exception as e:
        return False, str(e)


# ---------------------------
# Reparar con LLM + gramática
# ---------------------------
REPAIR_SYS_BASE = f"""
Eres un asistente que CORRIGE pseudocódigo de ADA para que sea válido
según la gramática del proyecto (WHILE, FOR, REPEAT, IF/THEN/ELSE, CALL, etc.).

Reglas IMPORTANTES:
- Usa SIEMPRE la flecha {ARROW} para asignaciones.
- Cierra TODOS los bloques con 'begin' ... 'end'.
- Respeta la estructura original del algoritmo: no inventes pasos nuevos.
- Puedes añadir 'begin/end', paréntesis, 'then', 'do', etc. si son necesarios.
- Usa SOLO (if, then, else, for, while, repeat, until, do, to, begin, end).
- No agregues comentarios ni explicaciones.
- Devuelve SOLO el pseudocódigo corregido, sin ``` ni markdown.
"""


def _repair_with_llm(code: str, parse_error: str) -> str:
    try:
        llm = get_llm(temperature=0.0)
    except Exception:
        return code

    # Cargar gramática para dársela al modelo
    grammar = ""
    try:
        agent = get_parser_agent()
        path = getattr(agent, "grammar_path", None)
        if path:
            with open(path, "r", encoding="utf-8") as f:
                grammar = f.read()
    except Exception:
        pass

    sys_content = REPAIR_SYS_BASE
    if grammar:
        sys_content += "\n\nGRAMÁTICA LARK DEL PROYECTO:\n" + grammar

    msgs = [
        {"role": "system", "content": sys_content},
        {
            "role": "user",
            "content": (
                "PSEUDOCÓDIGO ORIGINAL:\n"
                f"{code}\n\n"
                "ERROR DEL PARSER (Lark):\n"
                f"{parse_error}\n\n"
                "Corrige SOLO los errores de sintaxis para que cumpla la gramática "
                "y devuélvelo sin explicaciones:"
            ),
        },
    ]
    out = strip_code_fences(llm.invoke(msgs).content).strip()
    out = out.replace("->", ARROW).replace("←", ARROW).strip()
    if not out.endswith("\n"):
        out += "\n"
    return out


def _summarize_fix_with_llm(original: str, fixed: str) -> str:
    """Descripción corta de qué se corrigió, para meterla en 'normalizaciones'."""
    try:
        llm = get_llm(temperature=0.0)
    except Exception:
        return ""

    sys_msg = (
        "Resume en 1–2 líneas qué se corrigió entre el pseudocódigo ORIGINAL y el CORREGIDO "
        "(ej: se agregaron begin/end, se normalizaron flechas, se ajustó sintaxis de for/while/if, etc.)."
    )
    msgs = [
        {"role": "system", "content": sys_msg},
        {
            "role": "user",
            "content": (
                "ORIGINAL:\n"
                f"{original}\n\n"
                "CORREGIDO:\n"
                f"{fixed}\n\n"
                "RESPONDE SOLO CON UNA BREVE DESCRIPCIÓN:"
            ),
        },
    ]
    return llm.invoke(msgs).content.strip()


# ---------------------------
# Nodo del grafo
# ---------------------------
def validate_node(state: AnalyzerState) -> Dict[str, Any]:
    """
    pseudocode → normaliza → valida con Lark → si falla, repara con LLM (+gramática)
    → devuelve código corregido + reporte de normalizaciones/errores.
    """
    # Si pseudocode está vacío pero input_text tiene seudocódigo, usarlo
    raw_code = (state.get("pseudocode") or state.get("input_text") or state.get("text") or "").strip()

    if not raw_code:
        validation = {
            "era_algoritmo_valido": False,
            "codigo_corregido": "",
            "errores": ["Pseudocódigo vacío"],
            "normalizaciones": [],
            "hints": {
                "parser_engine": "lark-lalr",
                "language_hint": "es",
                "code_length": 0,
                "line_count": 0,
                "repaired_with_llm": False,
            },
        }
        meta_updates = update_metadata(
            state,
            input_type=(state.get("metadata") or {}).get("input_type", "pseudocode"),
            used_lark_validation=False,
        )
        return {"validation": validation, "pseudocode": "", **meta_updates}

    era_algo = bool(re.search(r"\bbegin\b.*\bend\b", raw_code, flags=re.I | re.S))

    # 1) Normalización barata
    code, normalizaciones = _simple_normalize(raw_code)
    code, balance_notes = _ensure_balanced_blocks(code)
    normalizaciones.extend(balance_notes)

    # 2) Lark
    parser_ok, parse_error = _parse_with_lark(code)
    repaired_with_llm = False

    # 3) Reparar si falla
    if not parser_ok and REPAIR_MODE == "llm" and parse_error:
        fixed = _repair_with_llm(code, parse_error)
        if fixed != code:
            fixed, post_balance_notes = _ensure_balanced_blocks(fixed)
            normalizaciones.extend(post_balance_notes)
            ok2, err2 = _parse_with_lark(fixed)
            if ok2:
                desc = _summarize_fix_with_llm(raw_code, fixed)
                if desc:
                    normalizaciones.append(f"Resumen corrección LLM: {desc}")
                normalizaciones.append(
                    "Corrección de sintaxis con LLM usando error de Lark"
                )
                code = fixed
                parser_ok, parse_error = True, None
                repaired_with_llm = True
            else:
                parse_error = err2

    # 4) Errores (informativos, no bloquean el pipeline)
    errores: List[str] = []
    if not era_algo:
        errores.append("Bloques begin/end no detectados en el código original")
    if not parser_ok and parse_error:
        errores.append(f"Error de gramática Lark tras reparación: {parse_error}")

    hints = {
        "parser_engine": "lark-lalr",
        "language_hint": "es",
        "code_length": len(code),
        "line_count": code.count("\n"),
        "repaired_with_llm": repaired_with_llm,
    }

    validation = {
        # true solo si el ORIGINAL ya era válido, sin tocar LLM
        "era_algoritmo_valido": bool(era_algo and parser_ok and not repaired_with_llm),
        "codigo_corregido": code,
        "errores": errores,
        "normalizaciones": normalizaciones,
        "hints": hints,
    }

    meta_updates = update_metadata(
        state,
        input_type=(state.get("metadata") or {}).get("input_type", "pseudocode"),
        used_lark_validation=True,
    )

    return {
        "validation": validation,
        "pseudocode": code,
        **meta_updates,
    }


__all__ = ["validate_node"]
