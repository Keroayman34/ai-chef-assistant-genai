# AI Chef Assistant

Beginner-friendly modular Python version of the instructor GenAI lab (without notebook).

## Project Structure

- app.py
- chef_agent.py
- schemas.py
- config.py
- utils.py
- requirements.txt
- .env.example
- README.md

## Tech Used

- Python
- LangChain
- langchain_openai
- langgraph memory/checkpointer (`InMemorySaver`)
- Pydantic structured output
- langchain-ollama
- python-dotenv

## What the app does

- Accepts ingredients from text (and optional image)
- Follows strict conversation workflow (never skips):
  1. Analyze ingredients
  2. Suggest meals
  3. Ask user preference
  4. Confirm meal
  5. Return final recipe
- Remembers context by `thread_id`
- Supports strict vs creative mode
- Supports concise vs detailed mode
- Supports OpenAI and Ollama (mistral) with the same flow

## Setup in VS Code

1. Open this folder in VS Code.
2. Create a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` from `.env.example` and add your OpenAI key:

   ```env
   OPENAI_API_KEY=your_real_key_here
   ```

## Run OpenAI Version

```bash
python app.py
```

When prompted:

- choose `openai`
- choose mode values
- enter ingredients
- optionally add image path

## New Web App Upgrade (FastAPI + React)

This project now includes:

- `backend_api/` (FastAPI wrapper reusing existing agent logic)
- `frontend/` (Vite + React + Tailwind UI)

### 1) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2) Run FastAPI backend

From project root:

```bash
uvicorn backend_api.main:app --reload --host 127.0.0.1 --port 8000
```

API endpoints:

- `POST /chat/start`
- `POST /chat/select-meal`
- `POST /chat/confirm`
- `POST /upload-image`
- `GET /history/{thread_id}`

### 3) Run React frontend

Open a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173`.

### 4) Backend + frontend connection

- Frontend uses `VITE_API_BASE_URL` in `frontend/.env`
- Default value: `http://127.0.0.1:8000`
- CORS is already enabled in backend for:
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`

### 5) Keep CLI version unchanged

Your original CLI flow still works:

```bash
python app.py
```

## Run Ollama Version (mistral)

1. Install Ollama from official site.
2. Pull model:

   ```bash
   ollama pull mistral
   ```

3. Start using the same app:

   ```bash
   python app.py
   ```

4. When prompted, choose `ollama`.

## Notes

- OpenAI key is loaded from `.env` using `python-dotenv`.
- Image input support is optional and depends on model capability.
- The code is intentionally simple with many comments for learning.
