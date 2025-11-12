# Agent Algorithms

Este proyecto contiene agentes y algoritmos desarrollados en Python.

## Requisitos
- Python 3.8 o superior
- uv (recomendado para gestión de dependencias)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Jhonder18/Agent_Algorithms.git
   cd Agent_Algorithms
   ```

2. Instala uv si no lo tienes:
   ```bash
   pip install uv
   ```

3. Instala las dependencias:
   ```bash
   uv venv
   uv pip install -r pyproject.toml
   uv pip install -r uv.lock
   ```
   O simplemente:
   ```bash
   uv pip install
   ```

4. Activa el entorno virtual:
   - En Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - En Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

5. Ejecuta el proyecto:
   ```bash
   python main.py
   ```

## Estructura del proyecto
- `main.py`: punto de entrada principal.
- `app/`: código fuente de la aplicación.
- `pyproject.toml` y `uv.lock`: gestión de dependencias.

## Notas
- Si agregas nuevas dependencias, recuerda actualizar el lockfile:
  ```bash
  uv pip freeze > uv.lock
  ```
- Para más información sobre uv: https://github.com/astral-sh/uv
