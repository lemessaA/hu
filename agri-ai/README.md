# AgriClimate AI Agent

Production-oriented monorepo for a **climate-smart agriculture** assistant aimed at Ethiopian farmers. The backend runs a **LangGraph** multi-tool agent (intent → weather → crop → knowledge → LLM reasoning) with **PostgreSQL** persistence and **Redis** short-term memory (last 5 messages). The frontend is **Next.js 14 (App Router)** with **Tailwind**, **React Query**, English/Amharic UI strings, chat, image upload + analysis, optional streaming, and a simple advice dashboard.

## Architecture (text diagram)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Next.js 14 (frontend)                        │
│  Chat UI · Image upload · i18n (EN/am) · React Query · /api/proxy/*  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │  server-side BFF adds X-API-Key
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI (backend) — middleware                    │
│  Logging · API key · CORS · routes: /chat /chat/stream /analyze…    │
└───────┬───────────────────────┬──────────────────────┬───────────────┘
        │                       │                      │
        ▼                       ▼                      ▼
┌───────────────┐     ┌─────────────────┐    ┌────────────────────────┐
│  PostgreSQL   │     │     Redis       │    │ Groq LLM (LangChain)   │
│ users,        │     │ weather cache   │    │ + optional OpenAI API  │
│ chat_history  │     │ last 5 msgs     │    │ (demo if no keys)      │
└───────────────┘     └─────────────────┘    └────────────────────────┘
        ▲
        │  LangGraph state flow
        │  intent → weather → crop → knowledge → reasoning
        └──────────────────────────────────────────────────
```

## Quick start (Docker)

1. Copy environment template:

   ```bash
   cd agri-ai
   cp .env.example .env
   ```

2. Set `API_KEY` and **`GROQ_API_KEY`** in `.env` (from [Groq Console](https://console.groq.com)). Optionally set `GROQ_MODEL`. If Groq is unset, the backend uses **`OPENAI_API_KEY`** when provided; otherwise it runs in **demo** mode (no external LLM).

3. Build and run:

   ```bash
   docker compose up --build
   ```

4. Open the app: `http://localhost:3000`  
   Backend docs: `http://localhost:8000/docs`  
   Health: `http://localhost:8000/health` (no API key)

Default compose API key: `dev-agri-key` (override via `.env`).

## One terminal — frontend + backend (local)

From the repo root, with **Postgres** and **Redis** running (e.g. `docker compose up -d postgres redis`):

```bash
cd agri-ai
cp -n .env.example .env   # configure API_KEY, GROQ_API_KEY, DATABASE_URL, REDIS_URL
npm run deps:up           # optional: Postgres + Redis via Docker
npm run dev
# or: bash scripts/dev.sh
```

This starts **FastAPI on :8000** and **Next.js on :3000**, loads variables from the **root `.env`**, and stops both on **Ctrl+C**.

Open **http://localhost:3000**.

## Local development (separate terminals)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Optional CPU PyTorch for parity with Docker:
pip install torch --index-url https://download.pytorch.org/whl/cpu
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5433/agriclimate
export REDIS_URL=redis://localhost:6379/0
export API_KEY=dev-local
export CORS_ORIGINS=http://localhost:3000
export GROQ_API_KEY=your-groq-key
export GROQ_MODEL=llama-3.3-70b-versatile
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run Postgres + Redis locally (or via Docker only for those services).

### Frontend

```bash
cd frontend
npm install
export BACKEND_URL=http://localhost:8000
export API_KEY=dev-local   # must match backend
npm run dev
```

Visit `http://localhost:3000`.

## API (FastAPI)

All routes except `GET /health` expect header `X-API-Key: <API_KEY>` (or `Authorization: Bearer <API_KEY>`).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness + Postgres/Redis checks |
| `POST` | `/chat` | JSON body: `message`, optional `location`, `session_id`, optional `crop_result` |
| `POST` | `/chat/stream` | Same body; SSE-style stream after graph completes |
| `POST` | `/chat/multipart` | `message`, optional `location`, optional `image` file |
| `POST` | `/analyze-image` | Multipart `file` — returns mock disease JSON (+ real PyTorch hook later) |
| `GET` | `/advice/recent` | Recent assistant replies (dashboard) |

### Example: chat

```bash
curl -s http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"message":"Will it rain this week in Jimma?","location":"Jimma","session_id":"demo"}'
```

## Agent & memory

- **LangGraph** nodes live under `backend/app/agent/nodes/`.
- **Redis** stores the last **5** messages per `session_id` (`app/agent/memory.py`).
- **Reasoning LLM**: **Groq** (`langchain-groq`, `GROQ_API_KEY`, `GROQ_MODEL`) when configured; else **OpenAI-compatible** `ChatOpenAI` if `OPENAI_API_KEY` is set; else structured **demo** output.
- **System prompt** is fixed in `backend/app/agent/prompt.py` (Problem / Insight / Action Steps).
- **Weather**: `services/weather_service.py` — OpenWeatherMap if `OPENWEATHER_API_KEY` is set, else demo data; always cached in Redis.
- **Crop**: `models/crop_model.py` — validates image, returns mock prediction; PyTorch import is optional for future weights.

## Security notes

- Rotate `API_KEY` for any public deployment; the Next.js app keeps it **server-side** and proxies via `/api/proxy/*`.
- Image uploads are type- and size-validated (5MB cap).
- Prefer TLS termination at your edge (nginx, cloud LB) in production.

## Project layout

```
agri-ai/
  backend/pyproject.toml # Python deps (install: pip install -e .)
  backend/app/…        # FastAPI, LangGraph, SQLAlchemy models, services
  frontend/src/…       # Next.js App Router, components, React Query
  docker-compose.yml
  README.md
  .env.example
```

## License

Provided as a conference-ready demo scaffold — adapt licensing for your organization.
