# app/services/llm.py
from __future__ import annotations
import os, json, re
from typing import Any, Dict
from dotenv import load_dotenv

# Carga .env de la raíz (langgraph dev no lo hace solo)
load_dotenv()  # si tu .env no está en la raíz, pásale dotenv_path

def strip_code_fences(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = t.strip("`")
        import re as _re
        t = _re.sub(r"^(json|js|javascript|python|pseudocode)\s*", "", t, flags=_re.I)
    return t.strip()

def get_llm(temperature: float = 0.0, model: str | None = None):
    provider = (os.getenv("LLM_PROVIDER", "gemini") or "gemini").lower()

    if provider == "stub":
        # LLM mínimo para pruebas en Studio (no requiere API key)
        from langchain_core.messages import AIMessage
        class _Stub:
            def invoke(self, msgs, **kw):
                return AIMessage(content='{"ok": true}')
        return _Stub()

    if provider == "gemini":
        # Import perezoso para no romper si usas stub
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY no configurada en el entorno")
        model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        # LangChain lee GOOGLE_API_KEY directamente del entorno
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            convert_system_message_to_human=True,
        )

    raise RuntimeError(f"LLM_PROVIDER desconocido: {provider}")

def llm_json_call(system: str, user: str, temperature: float = 0.0) -> Dict[str, Any]:
    llm = get_llm(temperature=temperature)
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    raw = strip_code_fences(llm.invoke(msgs).content)

    def _try_parse(s: str) -> Dict[str, Any]:
        s = s.strip()
        l, r = s.find("{"), s.rfind("}")
        if l != -1 and r != -1 and r > l:
            s = s[l:r + 1]
        return json.loads(s)

    try:
        return _try_parse(raw)
    except Exception:
        repair = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"El siguiente JSON no parsea. Arréglalo y responde SOLO JSON válido:\n\n{raw}"},
        ]
        fixed = strip_code_fences(llm.invoke(repair).content)
        return _try_parse(fixed)
