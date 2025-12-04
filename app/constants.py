# app/constants.py
from __future__ import annotations
import os

# Símbolo de asignación esperado por la gramática y los normalizadores.
ARROW = os.getenv("PSEUDO_ARROW", "🡨")

__all__ = ["ARROW"]
