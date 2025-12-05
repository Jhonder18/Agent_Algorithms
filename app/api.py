# app/api.py
import os
# Deshabilitar LangSmith tracing para mejor performance en API
os.environ["LANGSMITH_TRACING"] = "false"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import build_graph
from app.agents.state import AnalyzerState

app = FastAPI(
    title="Complexity Agents API",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeIn(BaseModel):
    text: str
    language_hint: Optional[str] = "es"


def make_json_serializable(obj: Any) -> Any:
    """
    Convierte un objeto Python a un formato serializable en JSON.
    Maneja tuplas usadas como claves de diccionario y otros tipos no serializables.
    """
    if isinstance(obj, dict):
        # Convertir diccionario, reemplazando claves tuple por strings
        new_dict = {}
        for key, value in obj.items():
            # Convertir la clave
            if isinstance(key, tuple):
                # Convertir tupla a string legible, ej: ('for', 'n-1') -> 'for:n-1'
                new_key = ":".join(str(k) for k in key)
            else:
                new_key = str(key) if not isinstance(key, str) else key
            
            # Recursivamente convertir el valor
            new_dict[new_key] = make_json_serializable(value)
        return new_dict
    
    elif isinstance(obj, (list, tuple)):
        # Convertir listas y tuplas recursivamente
        return [make_json_serializable(item) for item in obj]
    
    elif isinstance(obj, (str, int, float, bool, type(None))):
        # Tipos primitivos ya son serializables
        return obj
    
    else:
        # Para otros tipos (como objetos sympy), convertir a string
        return str(obj)


@app.post("/api/v2/analyze")
def analyze(in_: AnalyzeIn):
    try:
        state = AnalyzerState()
        state["nl_description"] = f"{in_.text}"
        graph = build_graph().compile()
        result = graph.invoke(state)
        
        # Convertir el resultado a un formato JSON-serializable
        serializable_result = make_json_serializable(result)        
        return serializable_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
