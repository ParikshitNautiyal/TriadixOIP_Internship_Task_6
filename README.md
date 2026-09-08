# Reading Room — AI Document Knowledge Assistant

Upload your own PDFs, Word documents, or PowerPoint decks, then ask
questions about them in plain English. Every answer is generated only
from what's actually in your documents and cited back to the exact page,
slide, or section it came from — if the answer isn't in there, the app
says so instead of guessing.

**Live demo:** (https://triadix-oip-internship-task-6.vercel.app/)

## How it works

1. **Extraction** — text is pulled out page-by-page (PDF), slide-by-slide
   (PowerPoint, including speaker notes), or section-by-section (Word).
2. **Chunking** — each unit is split into overlapping ~1000-character
   chunks so retrieval stays focused.
3. **Embedding** — chunks are embedded locally with a Sentence-Transformers
   model (`all-MiniLM-L6-v2`) — free, no network call, no API cost.
4. **Storage** — chunk text + embeddings + metadata go into a persistent
   ChromaDB collection.
5. **Retrieval** — your question is embedded the same way and compared
   against every stored chunk to find the most semantically similar ones.
6. **Generation** — the retrieved chunks are inserted into a prompt sent
   to [Groq](https://groq.com) (fast, generous free tier), which is
   instructed to answer *only* from that context.
7. **Citations** — the document name + page/slide/section of every chunk
   actually used comes back with the answer.

If nothing retrieved is relevant enough, the app skips the LLM call
entirely and returns "not found" directly — saving a request and avoiding
a confidently-wrong guess.

## Architecture

```
        User
         │
         ▼
┌─────────────────┐
│    Frontend     │
│  React + Vite   │
│     Vercel      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Backend     │
│    FastAPI      │
│     Render      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI / RAG      │
│                 │
│ • Embeddings    │
│ • ChromaDB      │
│ • Groq API      │
└─────────────────┘
         │
         ▼
      AI Answer
```

Originally this was a single Streamlit app doing both UI and logic in one
process. It's now split into a stateless FastAPI backend and a separate
static frontend — see **"Why not Streamlit on Vercel?"** below for why
that split was necessary, not just a nice-to-have.

### Why not Streamlit on Vercel?

Streamlit isn't deployable on Vercel, and this isn't a workaround-able
config issue — the two are architecturally incompatible. Vercel runs
static assets and short-lived serverless functions; Streamlit needs a
single, persistent, stateful Python process that holds a live WebSocket
connection to the browser for the whole session. Vercel's serverless
functions have execution time limits and don't keep a process running
between requests, so a Streamlit server has nowhere to live there.
Streamlit's own deployment target is Streamlit Community Cloud (or any
platform that runs a persistent process — Render, Railway, Fly.io, a VM).

That's why this project doesn't try to "deploy Streamlit to Vercel" —
instead, the actual logic (document processing, embeddings, retrieval,
RAG, testing) has been pulled out from underneath the Streamlit UI into a
plain FastAPI backend, which is stateless per-request and deploys
anywhere, including behind Vercel-hosted frontends.

## Project layout

```
backend/
  app/
    main.py                 FastAPI app, CORS, rate limiting, routers
    config.py                Settings from environment variables
    schemas.py                Pydantic request/response models
    document_processor.py     PDF/DOCX/PPTX extraction + chunking
    embeddings.py              Local Sentence-Transformers embeddings
    vector_store.py            ChromaDB wrapper + singleton accessor
    retrieval.py                Semantic search + relevance filtering
    rag_pipeline.py              Prompt construction + Groq call
    llm_utils.py                  Rate limiter + retry/backoff for Groq
    testing.py                     Batch test-suite runner
    routers/
      documents.py    POST /api/documents/upload, GET/DELETE /api/documents
      chat.py           POST /api/chat
      test.py             POST /api/test, GET /api/test/default-questions
  Dockerfile
  requirements.txt
  .env.example

frontend/
  src/
    api/client.js        Typed fetch wrapper around the backend
    components/           Library, ChatPanel, TestPanel, AboutPanel, SourceList
    App.jsx
  vercel.json
  .env.example

render.yaml            Render Blueprint for the backend
docker-compose.yml      Local dev for the backend
```

## Running locally

### Backend

**With Docker (recommended, especially on Windows):**

```bash
cd task6-new
cp backend/.env.example backend/.env    # then add your GROQ_API_KEY
docker compose up --build
```

The API is at `http://localhost:8000` (interactive docs at `/docs`). The
build runs on Linux inside the container regardless of your host OS, which
sidesteps a real gotcha: `chroma-hnswlib` (a ChromaDB dependency) has never
published a Windows wheel for Python 3.12, so a native `pip install` on
Windows + Python 3.12 tries to compile it from source and fails without
the MSVC C++ Build Tools installed. Docker avoids this entirely.

**Without Docker** (fine on macOS/Linux, or Windows with Python 3.11):

```bash
cd backend
cp .env.example .env        # then add your GROQ_API_KEY
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

Run the frontend natively either way — it's a separate process from the
backend and isn't part of the Docker setup above:

```bash
cd frontend
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000 by default
npm install
npm run dev
```

The app is at `http://localhost:5173`.

## Deploying

### Backend → Render

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point it at the repo. Render reads
   `render.yaml` and provisions the service automatically.
3. Set `GROQ_API_KEY` in the service's **Environment** tab (get a free key
   at [console.groq.com/keys](https://console.groq.com/keys) — it's marked
   `sync: false` in the blueprint on purpose, so it's never committed).
4. Once deployed, note the service URL (`https://your-service.onrender.com`).

**Free-tier caveats, worth knowing before you share the link:**
- Render's free web services **don't support persistent disks** — only
  paid plans do. Without one, `/app/data` (the ChromaDB store and the
  cached embedding model) resets on every restart, redeploy, or scale
  event. In practice: after the service spins down from inactivity or is
  redeployed, previously uploaded documents are gone and need
  re-uploading. This is expected on the free tier, not a bug. Upgrade the
  `plan` in `render.yaml` to `starter` or above and uncomment the `disk`
  block if you want the library to persist.
- Free services also **spin down after ~15 minutes idle** and take
  30-60 seconds to cold-start on the next request — the first request
  after a period of inactivity will be slow. A loading state in the
  frontend would help; keeping the plan on `starter`+ avoids it entirely.

### Frontend → Vercel

1. In Vercel: **Add New → Project**, import the repo, and set the **Root
   Directory** to `frontend` (Vercel auto-detects the Vite framework from
   there).
2. Add an environment variable: `VITE_API_BASE_URL` =
   `https://your-service.onrender.com` (your Render URL from above).
3. Deploy. Vercel gives you a `https://your-app.vercel.app` URL.
4. Back in Render, update `ALLOWED_ORIGINS` to include that Vercel URL
   (comma-separated, no spaces) so the browser's CORS check passes, then
   redeploy the backend.

## API reference

| Method | Path                          | Description                                  |
|--------|-------------------------------|-----------------------------------------------|
| GET    | `/health`                     | Health check (used by Docker/Render)           |
| GET    | `/api/documents`               | List indexed documents + chunk count            |
| POST   | `/api/documents/upload`         | Upload one or more files (`multipart/form-data`) |
| DELETE | `/api/documents`                 | Clear the entire knowledge base                   |
| POST   | `/api/chat`                       | `{"question": "..."}` → answer + sources          |
| GET    | `/api/test/default-questions`      | Sample questions for the test suite                |
| POST   | `/api/test`                          | `{"questions": [...]}` → batch results              |

Full interactive docs (Swagger UI) are served at `/docs` on the running
backend.

## Keeping API usage in check

Two independent layers keep this from running away with either your
Groq quota or your Render hosting resources, since it's a public demo:

- **Outbound**: `llm_utils.py` throttles calls to Groq to a rolling
  per-minute budget (`GROQ_MAX_REQUESTS_PER_MINUTE`) and retries
  rate-limit/5xx errors with exponential backoff, instead of firing
  requests as fast as visitors click and surfacing raw 429s.
- **Inbound**: each LLM-backed endpoint (`/api/chat`, `/api/documents/upload`,
  `/api/test`, `DELETE /api/documents`) is rate-limited per client IP via
  `slowapi`, so one visitor can't monopolize the shared Groq quota or spam
  the vector store. Limits are configurable via `RATE_LIMIT_*` env vars.
- Retrieval that comes back empty or below the relevance threshold skips
  the LLM call entirely — no wasted request on an unanswerable question.

## Tech stack

**Backend:** FastAPI, ChromaDB, Sentence-Transformers, Groq API, Docker
**Frontend:** React, Vite
**Hosting:** Render (API), Vercel (frontend)
