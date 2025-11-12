# app/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from app.agents.graph import build_graph

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

graph = build_graph()

class AnalyzeIn(BaseModel):
    text: str
    language_hint: Optional[str] = "es"

@app.post("/api/v2/analyze")
def analyze(in_: AnalyzeIn):
    try:
        state = {"input_text": in_.text.strip()}
        out = graph.invoke(state)
        # out YA tiene input_text, validation, ast, costs, solution, metadata
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
