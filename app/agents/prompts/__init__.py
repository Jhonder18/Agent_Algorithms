# app/prompts/__init__.py
"""
Módulo para cargar prompts externos desde archivos .md
"""
import os
from pathlib import Path


def load_prompt(name: str) -> str:
    """
    Carga un prompt desde un archivo .md en esta carpeta.
    
    Args:
        name: Nombre del archivo sin extensión (ej: "generate_pseudo" carga "generate_pseudo.md")
        
    Returns:
        Contenido del archivo como string
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    prompt_file = Path(__file__).parent / f"{name}.md"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    
    with open(prompt_file, "r", encoding="utf-8") as f:
        return f.read().strip()


__all__ = ["load_prompt"]
