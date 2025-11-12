# app/agents/nodes/normalize.py
from __future__ import annotations
from typing import TypedDict, Dict
import re
from app.services.llm import get_llm, strip_code_fences

ARROW = "🡨"  # si prefieres "←", cámbialo aquí

class AgentState(TypedDict, total=False):
    input_text: str
    pseudocode: str

NORMALIZE_SYS = f"""
Convierte la descripción a PSEUDOCÓDIGO ESTRUCTURADO válido siguiendo estas reglas EXACTAS:

1) PROCEDIMIENTOS:
   nombre(param1, param2)
   begin
       ...
   end

2) FOR:
   for i {ARROW} inicio to fin do
   begin
       ...
   end

3) WHILE:
   while (condicion) do
   begin
       ...
   end

4) REPEAT-UNTIL:
   repeat
   begin
       ...
   end
   until (condicion)

5) IF-THEN-ELSE:
   if (condicion) then
   begin
       ...
   end
   else
   begin
       ...
   end

6) Asignación SIEMPRE con {ARROW}
7) Operadores lógicos en minúscula: and, or, not
8) Arrays: A[i] o A[1..n]

Responde SOLO el pseudocódigo, sin comentarios, sin markdown.
"""

def looks_like_pseudo(text: str) -> bool:
    return bool(re.search(r"\bbegin\b|\bend\b|←|🡨|->|\bfor\b|\bwhile\b|\bif\b|\brepeat\b|\buntil\b", text, flags=re.I))

def normalize_node(state: AgentState) -> Dict:
    text = (state.get("input_text") or "").strip()

    # Si ya parece pseudocódigo, haz pequeñas normalizaciones locales
    if looks_like_pseudo(text):
        pseudo = text
        pseudo = pseudo.replace("->", ARROW).replace("←", ARROW)
        if not pseudo.endswith("\n"):
            pseudo += "\n"
        return {"pseudocode": pseudo}

    # Si es NL, pedir al LLM
    llm = get_llm(temperature=0)
    msgs = [
        {"role":"system","content": NORMALIZE_SYS},
        {"role":"user","content": text},
    ]
    out = strip_code_fences(llm.invoke(msgs).content)
    out = out.replace("->", ARROW).replace("←", ARROW).strip()
    if not out.endswith("\n"):
        out += "\n"
    return {"pseudocode": out}

__all__ = ["normalize_node"]
