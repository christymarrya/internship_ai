# 🎓 AI-Driven Internship Discovery & Application Automation Backend

A production-ready FastAPI backend using NLP, semantic embeddings, FAISS vector search,
and LLM generation to automate every stage of the internship application process.

---

## 📁 Project Structure

```
internship_ai/
│
├── app/
│   ├── main.py                         # FastAPI app entry point, router registration
│   │
│   ├── core/
│   │   ├── config.py                   # Pydantic settings — loads from .env
│   │   ├── dependencies.py             # Dependency injection (singleton services)
│   │   └── logger.py                   # Structured logging utility
│   │
│   ├── models/
│   │   ├── schemas.py                  # All Pydantic request/response models
│   │   └── store.py                    # In-memory resume session store
│   │
│   ├── services/
│   │   ├── nlp_service.py              # spaCy NLP: NER, entity extraction, tokenization
│   │   ├── resume_parser.py            # Resume → structured JSON (skills, edu, exp)
│   │   ├── embedding_service.py        # SentenceTransformers: embed(), embed_batch()
│   │   ├── faiss_service.py            # FAISS: add_vectors(), search(), persist/load
│   │   ├── matching_service.py         # Job match: cosine similarity + skill gap
│   │   ├── llm_service.py              # OpenAI-compatible LLM client wrapper
│   │   ├── cover_letter_service.py     # Cover letter generation with RAG injection
│   │   └── rag_service.py              # RAG: chunk → embed → index → retrieve
│   │
│   ├── api/
│   │   └── endpoints/
│   │       ├── resume.py               # Phase 1: POST /resume/upload, GET, DELETE
│   │       ├── matching.py             # Phase 2: POST /match/
│   │       ├── cover_letter.py         # Phase 3: POST /cover-letter/generate-cover-letter
│   │       ├── rag.py                  # Phase 4: POST /rag/index, /rag/query, GET /rag/status
│   │       └── profile.py              # Phase 5: GET /profile/{id}, /automation-schema
│   │
│   └── utils/
│       ├── pdf_extractor.py            # PDF → text (pdfplumber + PyPDF2 fallback)
│       └── chunker.py                  # Text chunking for RAG (overlapping windows)
│
├── tests/
│   └── test_api.py                     # Integration tests for all 5 phases
│
├── scripts/
│   └── autofill_playwright.py          # Phase 5: Playwright autofill scaffold
│
├── data/                               # Auto-created at runtime
│   ├── uploads/                        # Stored PDF files
│   └── faiss_index/                    # Persisted FAISS indices
│
├── requirements.txt                    # All Python dependencies
├── env.example                         # Environment variable template
└── README.md                           # This file
```

---

## 🔄 System Architecture — 5 Phases

```
PDF Upload
    │
    ▼
[Phase 1] pdfplumber → spaCy NLP → ParsedResume JSON
    │              (skills, edu, exp, name, email)
    │
    ├──────────────────────────────────────────────────┐
    ▼                                                  ▼
[Phase 2] SentenceTransformer                   [Phase 4] Chunker
    ├── embed(resume_text)                          ├── chunk_text()
    ├── embed(job_description)                      ├── embed_batch()
    ├── cosine_similarity()                         └── FAISS.add_vectors(resume_id)
    ├── FAISS global index
    └── skill gap analysis                          [Phase 3] LLM Cover Letter
                                                        ├── RAG retrieval (FAISS)
[Phase 5] Autofill Profile                             ├── Prompt template
    ├── /profile/{id} → JSON fields                    └── OpenAI API → cover letter
    └── Playwright automation scaffold
```

---

## ⚡ Quick Start

### 1. Clone & Navigate
```bash
git clone <your-repo>
cd internship_ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment
```bash
cp env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 6. Create Data Directories
```bash
mkdir -p data/uploads data/faiss_index
```

### 7. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Open API Docs
Navigate to: **http://localhost:8000/docs**

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🔌 API Reference

### Phase 1 — Resume Intelligence
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resume/upload` | Upload PDF resume → returns `resume_id` + parsed JSON |
| GET | `/api/v1/resume/{resume_id}` | Retrieve parsed resume by ID |
| DELETE | `/api/v1/resume/{resume_id}` | Remove resume from store |

### Phase 2 — Job Matching
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/match/` | Match resume vs job description → score, skill gaps |

### Phase 3 — Cover Letter Generator
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cover-letter/generate-cover-letter` | Generate personalized cover letter |

### Phase 4 — RAG Enhancement
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rag/index` | Chunk + embed + index resume into FAISS |
| POST | `/api/v1/rag/query` | Retrieve top-K relevant chunks for query |
| GET | `/api/v1/rag/status/{resume_id}` | Check index status |

### Phase 5 — Automation Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/profile/{resume_id}` | Autofill-ready profile (form field mapping) |
| GET | `/api/v1/profile/{resume_id}/automation-schema` | Integration guide |

---

## 📋 Complete Usage Workflow

```bash
# Step 1: Upload resume
curl -X POST "http://localhost:8000/api/v1/resume/upload" \
  -F "file=@my_resume.pdf"
# → Returns: {"resume_id": "abc-123", "parsed": {...}}

# Step 2: Match against job description
curl -X POST "http://localhost:8000/api/v1/match/" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": "abc-123", "job_description": "We need a Python developer..."}'
# → Returns: {"match_score": 78.4, "match_label": "Good Match", "missing_skills": [...]}

# Step 3 (Optional): Index for RAG
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": "abc-123"}'

# Step 4: Generate cover letter (uses RAG if indexed)
curl -X POST "http://localhost:8000/api/v1/cover-letter/generate-cover-letter" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": "abc-123",
    "job_description": "We need a Python developer...",
    "company_name": "Acme Corp",
    "job_title": "Software Engineering Intern",
    "tone": "professional"
  }'

# Step 5: Get autofill profile
curl "http://localhost:8000/api/v1/profile/abc-123"

# Step 6: Run browser autofill (Phase 5)
python scripts/autofill_playwright.py abc-123 https://jobs.lever.co/company/job-id lever
```

---

## 🔧 Alternative LLM Providers

Set these in your `.env` to use providers other than OpenAI:

**Groq (fast, free tier):**
```
OPENAI_API_KEY=gsk_your-groq-key
OPENAI_MODEL=llama-3.1-70b-versatile
OPENAI_BASE_URL=https://api.groq.com/openai/v1
```

**Ollama (local, free):**
```
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.2
OPENAI_BASE_URL=http://localhost:11434/v1
```

---

## 🚀 Production Checklist

- [ ] Replace in-memory `ResumeStore` with Redis or PostgreSQL
- [ ] Add JWT authentication middleware
- [ ] Set `ALLOWED_ORIGINS` to your frontend domain
- [ ] Use `faiss-gpu` for GPU-accelerated vector search
- [ ] Add rate limiting (slowapi)
- [ ] Configure persistent FAISS index (already supported)
- [ ] Set `DEBUG=false` and `ENVIRONMENT=production`
- [ ] Add Sentry for error monitoring
- [ ] Containerize with Docker (Dockerfile provided below)

---

## 🐳 Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
RUN mkdir -p data/uploads data/faiss_index
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t internship-ai .
docker run -p 8000:8000 --env-file .env internship-ai
```
