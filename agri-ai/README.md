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

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- A running **PostgreSQL** instance (default URL points at `localhost:5432`)
- A running **Redis** instance (default URL points at `localhost:6379`)

Install Postgres and Redis with your OS package manager (e.g. `apt install postgresql redis-server`) and make sure both services are running before starting the app.

## One terminal — frontend + backend (local)

From the repo root, with **Postgres** and **Redis** running:

```bash
cd agri-ai
cp -n .env.example .env   # configure API_KEY, GROQ_API_KEY, DATABASE_URL, REDIS_URL
npm run dev
# or: bash scripts/dev.sh
```

This starts **FastAPI on :8000** and **Next.js on :3000**, loads variables from the **root `.env`**, and stops both on **Ctrl+C**.

Open **http://localhost:3000**. Backend docs at `http://localhost:8000/docs`, health at `http://localhost:8000/health` (no API key).

## Local development (separate terminals)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Optional CPU PyTorch (for the crop model hook):
pip install torch --index-url https://download.pytorch.org/whl/cpu
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/agriclimate
export REDIS_URL=redis://localhost:6379/0
export API_KEY=dev-local
export CORS_ORIGINS=http://localhost:3000
export GROQ_API_KEY=your-groq-key
export GROQ_MODEL=llama-3.3-70b-versatile
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The same app also loads under `fastapi dev` (FastAPI CLI) if you prefer that workflow; keep the same environment variables and port.

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

- **`AUTH_MODE`** (in `.env`): **`api_key`** (default) — shared `API_KEY` header; **`none`** — no auth (local/demo only); **`trusted_host`** — only loopback + private LAN/Docker IPs, no secret (never expose `:8000` publicly in this mode).
- Rotate `API_KEY` for any public deployment when using `api_key` mode; the Next.js app keeps it **server-side** and proxies via `/api/proxy/*`.
- Image uploads are type- and size-validated (5MB cap).
- Prefer TLS termination at your edge (nginx, cloud LB) in production.

## Testing

**Unit / offline tests** (no running server; uses `backend/.venv`):

```bash
cd agri-ai
chmod +x scripts/run-tests.sh scripts/smoke-test.sh
npm test
# or: bash scripts/run-tests.sh
```

**With a live API** (Postgres + Redis + `uvicorn` on :8000; set `API_KEY` if `AUTH_MODE=api_key`):

```bash
export RUN_LIVE=1
npm run test:live
```

**HTTP smoke** (curl against `LIVE_API_BASE`, default `http://127.0.0.1:8000`):

```bash
npm run smoke
```

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
