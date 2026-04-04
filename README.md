# Internship AI

Production-oriented monorepo for internship discovery and application automation.

## Repository Layout

- `backend/`: FastAPI service for auth, resume parsing, matching, RAG, workflow automation, and PDF/email tooling.
- `frontend/`: Next.js app for dashboard, internship discovery, and application workflows.

## Quick Start

### 1) Backend

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
cp ..\\env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend docs: `http://localhost:8000/docs`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend app: `http://localhost:3000`

## Production Notes

- Set all secrets in `.env` (especially `SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`).
- Runtime artifacts (`backend/data/uploads`, `backend/data/faiss_index`, local DB files) are git-ignored by default.
- Use process management (systemd/PM2/container orchestration) and reverse proxy/TLS for deployment.

## Tests

```bash
cd backend
pytest tests -v
```

## Cleanup Policy

This repository intentionally excludes:

- ad-hoc debug scripts
- test output dumps and tracebacks
- generated runtime files (uploads, FAISS index, local DBs)
