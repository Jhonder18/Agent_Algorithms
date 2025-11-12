# main.py
"""
Entry point local. En producción suele bastar con: `uvicorn app.api:app`.
"""
import os
import uvicorn
from dotenv import load_dotenv

# Carga variables de .env (GOOGLE_API_KEY, HOST, PORT, etc.)
load_dotenv()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true").lower() in ("1", "true", "yes")

if __name__ == "__main__":
    # Nota: la app FastAPI está en app/api.py con docs en /docs y /redoc
    uvicorn.run(
        "app.api:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="info",
    )
