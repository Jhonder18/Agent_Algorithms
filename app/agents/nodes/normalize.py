# app/agents/nodes/normalize.py
from __future__ import annotations
from typing import Dict, Any
import re

from app.services.llm import get_llm, strip_code_fences
from app.constants import ARROW
from app.agents.state import AnalyzerState, update_metadata

# --- Heurística: solo consideramos "canónico" si usa PALABRAS CLAVE EN INGLÉS
#     y NO contiene equivalentes en español (para/si/mientras/etc.)
CANONICAL_KW = re.compile(
    r"\b(for|while|repeat|until|if|then|else|begin|end|return|to|do)\b", re.I
)
SPANISH_KW = re.compile(
    r"\b(para|mientras|repetir|hasta|si|entonces|sino|procedimiento)\b", re.I
)


def looks_like_canonical_pseudo(text: str) -> bool:
    if not CANONICAL_KW.search(text):
        return False
    if SPANISH_KW.search(text):
        # Tiene keywords en español -> NO es canónico, hay que normalizar con LLM
        return False
    return True


# --- Prompt ESTRICTO para producir pseudocódigo que cumpla la gramática
PROMPT = f"""
Convierte la siguiente descripción en PSEUDOCÓDIGO ESTRUCTURADO siguiendo EXACTAMENTE estas reglas:

SINTAXIS OBLIGATORIA:
1. PROCEDIMIENTOS: Siempre usar "begin" y "end"
   nombre_procedimiento(parametros)
   begin
       instrucciones
   end

2. FOR: Siempre terminar con "do" seguido de "begin...end"
   for variable {ARROW} inicio to fin do
   begin
       instrucciones
   end

3. WHILE: Siempre terminar con "do" seguido de "begin...end"
   while (condicion) do
   begin
       instrucciones
   end

4. REPEAT-UNTIL: DEBE usar "begin" inmediatamente después de "repeat"
   repeat
   begin
       instrucciones
   end
   until (condicion)

5. IF-THEN-ELSE: Siempre usar "begin...end" en bloques
   if (condicion) then
   begin
       instrucciones
   end
   else
   begin
       instrucciones
   end

6. ASIGNACIONES: Usar flecha {ARROW}
   variable {ARROW} valor

7. ARRAYS: A[i] o rangos A[1..n]

8. OPERADORES LÓGICOS: Siempre en minúsculas
   - and (conjunción)
   - or (disyunción)
   - not (negación)
   Ejemplo: if (i > 0 and i < n) then

PAUTAS DE SALIDA:
- NO mezcles español e inglés en palabras clave: usa SOLO (if, then, else, for, while, repeat, until, do, to, begin, end).
- NO uses comentarios ni markdown.
- NO expliques nada, SOLO devuelve el pseudocódigo.
- Asegúrate de cerrar SIEMPRE todos los bloques con "end".
- Incluye SIEMPRE una firma de procedimiento al inicio: nombre(params)

EJEMPLOS CORRECTOS:

Ejemplo 1 - Burbuja:
burbuja(A, n)
begin
    for i {ARROW} 1 to n-1 do
    begin
        for j {ARROW} 1 to n-i do
        begin
            if (A[j] > A[j+1]) then
            begin
                temp {ARROW} A[j]
                A[j] {ARROW} A[j+1]
                A[j+1] {ARROW} temp
            end
        end
    end
end

Ejemplo 2 - Con REPEAT:
buscar(A, n, x)
begin
    i {ARROW} 1
    repeat
    begin
        if (A[i] = x) then
        begin
            return i
        end
        i {ARROW} i + 1
    end
    until (i > n)
    return -1
end

Ejemplo 3 - Inserción:
insercion(A, n)
begin
    for i {ARROW} 2 to n do
    begin
        clave {ARROW} A[i]
        j {ARROW} i - 1
        while (j > 0 and A[j] > clave) do
        begin
            A[j+1] {ARROW} A[j]
            j {ARROW} j - 1
        end
        A[j+1] {ARROW} clave
    end
end

ERRORES COMUNES A EVITAR:
❌ NUNCA escribir "repeat" sin "begin" después
❌ NUNCA omitir "begin...end" en loops o condicionales
❌ NUNCA usar ":" para asignaciones (usar {ARROW})
❌ NUNCA mezclar español e inglés en palabras clave
❌ NUNCA usar AND/OR/NOT en MAYÚSCULAS (usar: and, or, not en minúsculas)
"""


def normalize_node(state: AnalyzerState) -> Dict[str, Any]:
    """
    Entrada:
      - input_text (o text): descripción en lenguaje natural o pseudocódigo "mezclado"
    Salida:
      - pseudocode normalizado y metadata indicando el tipo de input.
    """
    text = (state.get("input_text") or state.get("text") or "").strip()
    if not text:
        return {
            "pseudocode": "",
            **update_metadata(state, input_type="unknown", used_normalization=False),
        }

    # Si parece canónico (solo keywords en inglés + begin/end), aceptar y normalizar flecha
    if looks_like_canonical_pseudo(text):
        pseudo = text.replace("->", ARROW).replace("←", ARROW).strip()
        if not pseudo.endswith("\n"):
            pseudo += "\n"
        return {
            "pseudocode": pseudo,
            **update_metadata(
                state,
                input_type="pseudocode",
                used_normalization=False,
            ),
        }

    # Caso contrario: pedimos al LLM la versión canónica EXACTA
    llm = get_llm(temperature=0.0)
    msgs = [
        {"role": "system", "content": PROMPT},
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

    # Post-procesado mínimo: flecha y newline final
    out = out.replace("->", ARROW).replace("←", ARROW).strip()
    if not out.endswith("\n"):
        out += "\n"

    return {
        "pseudocode": out,
        **update_metadata(
            state,
            input_type="natural_language",
            used_normalization=True,
        ),
    }


__all__ = ["normalize_node"]
