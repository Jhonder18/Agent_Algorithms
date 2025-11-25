# app/agents/nodes/shared_utils.py
"""
Utilidades compartidas para normalización de pseudocódigo.
Evita duplicación entre generate_pseudo.py y validate.py
"""
from __future__ import annotations

import re
from typing import List, Tuple

from app.constants import ARROW


def normalize_arrows(code: str) -> str:
    """
    Convierte todas las flechas de asignación a la flecha estándar.
    
    Args:
        code: Pseudocódigo con posibles variantes de flechas (-> o ←)
        
    Returns:
        Código con flechas normalizadas a ARROW (🡨)
    """
    return code.replace("->", ARROW).replace("←", ARROW)


def normalize_keywords(code: str) -> str:
    """
    Normaliza palabras clave a minúsculas (excepto CALL que va en mayúsculas).
    
    Args:
        code: Pseudocódigo con palabras clave en cualquier caso
        
    Returns:
        Código con palabras clave normalizadas
    """
    result = code
    
    # Palabras clave a minúscula
    keywords_to_lower = [
        "BEGIN", "END", "FOR", "WHILE", "IF", "ELSE",
        "REPEAT", "UNTIL", "RETURN", "AND", "OR",
        "NOT", "DO", "THEN", "PROCEDIMIENTO",
    ]
    
    for kw in keywords_to_lower:
        if kw in result:
            result = re.sub(rf"\b{kw}\b", kw.lower(), result)
    
    # CALL siempre en mayúsculas
    if re.search(r"\bcall\b", result, flags=re.I):
        result = re.sub(r"\bcall\b", "CALL", result, flags=re.I)
    
    return result


def ensure_final_newline(code: str) -> str:
    """
    Asegura que el código termine con una nueva línea.
    
    Args:
        code: Pseudocódigo
        
    Returns:
        Código con nueva línea final
    """
    return code if code.endswith("\n") else code + "\n"


def balance_begin_end(code: str) -> Tuple[str, List[str]]:
    """
    Asegura que exista el mismo número de 'begin' y 'end' añadiendo
    los 'end' faltantes al final del pseudocódigo.
    
    Args:
        code: Pseudocódigo posiblemente desbalanceado
        
    Returns:
        Tupla de (código_balanceado, lista_de_cambios_realizados)
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


def quick_normalize(code: str) -> Tuple[str, List[str]]:
    """
    Aplica normalizaciones rápidas: flechas, keywords, newline final.
    
    Args:
        code: Pseudocódigo a normalizar
        
    Returns:
        Tupla de (código_normalizado, lista_de_cambios_realizados)
    """
    changes: List[str] = []
    result = code
    
    # Normalizar flechas
    if "->" in result or "←" in result:
        result = normalize_arrows(result)
        changes.append("Reemplazo de asignación por flecha")
    
    # Normalizar palabras clave
    original = result
    result = normalize_keywords(result)
    if result != original:
        changes.append("Normalización de palabras clave")
    
    # Asegurar newline final
    if not result.endswith("\n"):
        result = ensure_final_newline(result)
        changes.append("Nueva línea añadida al final")
    
    return result, changes


__all__ = [
    "normalize_arrows",
    "normalize_keywords",
    "ensure_final_newline",
    "balance_begin_end",
    "quick_normalize",
]
