# app/agents/nodes/generate_pseudo.py
"""
Nodo para generar pseudocódigo estructurado desde lenguaje natural o
normalizar pseudocódigo existente siguiendo la gramática del proyecto.
"""
from __future__ import annotations

import re
from typing import Dict, Any

from app.services.llm import get_llm, strip_code_fences
from app.agents.state import AnalyzerState, update_metadata
from app.services.utils import normalize_arrows, ensure_final_newline
from app.prompts import load_prompt


# Heurística: solo consideramos "canónico" si usa palabras clave EN INGLÉS
# y NO contiene equivalentes en español (para/si/mientras/etc.)
CANONICAL_KW = re.compile(
    r"\b(for|while|repeat|until|if|then|else|begin|end|return|to|do)\b", re.I
)
SPANISH_KW = re.compile(
    r"\b(para|mientras|repetir|hasta|si|entonces|sino|procedimiento)\b", re.I
)


def looks_like_canonical_pseudo(text: str) -> bool:
    """
    Determina si el texto ya parece pseudocódigo canónico.
    
    Returns:
        True si tiene keywords en inglés y NO tiene keywords en español
    """
    if not CANONICAL_KW.search(text):
        return False
    if SPANISH_KW.search(text):
        return False  # Tiene español -> necesita normalización
    return True


def generate_pseudo_node(state: AnalyzerState) -> Dict[str, Any]:
    """
    Genera pseudocódigo estructurado desde lenguaje natural o normaliza
    pseudocódigo existente para que cumpla con la gramática del proyecto.
    
    Entrada:
      - input_text (o text): descripción en lenguaje natural o pseudocódigo "mezclado"
      
    Salida:
      - pseudocode: pseudocódigo normalizado
      - metadata: indicando el tipo de input y si se usó normalización
    """
    text = (state.get("input_text") or state.get("text") or "").strip()
    
    if not text:
        return {
            "pseudocode": "",
            **update_metadata(state, input_type="unknown", used_normalization=False),
        }
    
    # Si parece canónico (solo keywords en inglés + begin/end), solo normalizar flechas
    if looks_like_canonical_pseudo(text):
        pseudo = normalize_arrows(text).strip()
        pseudo = ensure_final_newline(pseudo)
        
        return {
            "pseudocode": pseudo,
            **update_metadata(
                state,
                input_type="pseudocode",
                used_normalization=False,
            ),
        }
    
    # Caso contrario: generar pseudocódigo canónico con LLM
    llm = get_llm(temperature=0.0)
    prompt_system = load_prompt("generate_pseudo")
    
    msgs = [
        {"role": "system", "content": prompt_system},
        {
            "role": "user",
            "content": (
                "AHORA CONVIERTE:\n"
                f"{text}\n\n"
                "RESPUESTA (solo pseudocódigo, sin explicaciones, "
                "sin markdown, sin ```):"
            ),
        },
    ]
    
    out = strip_code_fences(llm.invoke(msgs).content).strip()
    
    # Post-procesado: normalizar flechas y asegurar newline final
    out = normalize_arrows(out).strip()
    out = ensure_final_newline(out)
    
    return {
        "pseudocode": out,
        **update_metadata(
            state,
            input_type="natural_language",
            used_normalization=True,
        ),
    }


__all__ = ["generate_pseudo_node"]
