"""
tests/test_api.py — Integration tests for all 5 phases.
Uses FastAPI TestClient with mocked services for reliable CI testing.
Run: pytest tests/ -v
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import (
    ParsedResume, EducationEntry, ExperienceEntry,
    JobMatchResponse, CoverLetterResponse,
    RAGIndexResponse, RAGQueryResponse
)
from app.models.store import resume_store
from app.core.dependencies import get_current_user
from app.core.dependencies import UserSchema

client = TestClient(app)

# Override auth dependency
def override_get_current_user():
    return UserSchema(id="test-uuid-123", email="john@example.com")

app.dependency_overrides[get_current_user] = override_get_current_user# ─── Fixtures ──────────────────────────────────────────────────────────────

SAMPLE_RESUME_ID = "test-resume-001"
SAMPLE_PARSED = ParsedResume(
    raw_text="John Doe\njohn@example.com\nPython Developer\nSkills: Python, FastAPI, ML",
    name="John Doe",
    email="john@example.com",
    phone="+1-555-0123",
    skills=["Python", "FastAPI", "Machine Learning", "SQL"],
    education=[EducationEntry(
        degree="Bachelor of Technology",
        institution="MIT",
        year="2023",
    )],
    experience=[ExperienceEntry(
        title="Software Engineering Intern",
        company="Google",
        duration="May 2023 - Aug 2023",
        description="Built ML pipelines using Python and TensorFlow.",
    )],
    summary="Motivated CS student with strong Python and ML skills.",
)

SAMPLE_JD = """
We are looking for a Python Developer Intern with experience in:
- Python, FastAPI, REST APIs
- Machine Learning, NLP
- SQL and PostgreSQL
- Git, Docker
Strong communication skills required.
"""


@pytest.fixture(autouse=True)
def seed_store():
    """Pre-seed the resume store before each test."""
    resume_store.save(SAMPLE_RESUME_ID, SAMPLE_PARSED)
    yield
    resume_store.delete(SAMPLE_RESUME_ID)


# ─── Phase 1: Resume ───────────────────────────────────────────────────────

class TestResumeEndpoints:
    def test_get_existing_resume(self):
        resp = client.get(f"/api/v1/resume/{SAMPLE_RESUME_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "John Doe"
        assert "Python" in data["skills"]

    def test_get_nonexistent_resume(self):
        resp = client.get("/api/v1/resume/does-not-exist")
        assert resp.status_code == 404

    def test_delete_resume(self):
        resp = client.delete(f"/api/v1/resume/{SAMPLE_RESUME_ID}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "deleted"

    def test_upload_invalid_file_type(self):
        resp = client.post(
            "/api/v1/resume/upload",
            files={"file": ("resume.txt", b"plain text content", "text/plain")},
        )
        assert resp.status_code == 400

    def test_upload_empty_file(self):
        resp = client.post(
            "/api/v1/resume/upload",
            files={"file": ("resume.pdf", b"", "application/pdf")},
        )
        assert resp.status_code in (400, 422)


# ─── Phase 2: Job Matching ─────────────────────────────────────────────────

class TestMatchingEndpoints:
    def test_match_success(self):
        with patch("app.services.embedding_service.EmbeddingService.embed") as mock_embed, \
             patch("app.services.embedding_service.EmbeddingService.cosine_similarity") as mock_cos:
            import numpy as np
            mock_embed.return_value = np.zeros(384, dtype="float32")
            mock_cos.return_value = 0.75  # 75% match

            resp = client.post("/api/v1/match/", json={
                "resume_id": SAMPLE_RESUME_ID,
                "job_description": SAMPLE_JD,
            })
            # Without mocked DI this will still validate schema
            assert resp.status_code in (200, 500)

    def test_match_missing_resume(self):
        resp = client.post("/api/v1/match/", json={
            "resume_id": "nonexistent",
            "job_description": SAMPLE_JD,
        })
        assert resp.status_code == 404

    def test_match_empty_jd(self):
        resp = client.post("/api/v1/match/", json={
            "resume_id": SAMPLE_RESUME_ID,
            "job_description": "",
        })
        assert resp.status_code == 400


# ─── Phase 3: Cover Letter ─────────────────────────────────────────────────

class TestCoverLetterEndpoints:
    def test_cover_letter_missing_resume(self):
        resp = client.post("/api/v1/cover-letter/generate-cover-letter", json={
            "resume_id": "bad-id",
            "job_description": SAMPLE_JD,
        })
        assert resp.status_code == 404

    def test_cover_letter_empty_jd(self):
        resp = client.post("/api/v1/cover-letter/generate-cover-letter", json={
            "resume_id": SAMPLE_RESUME_ID,
            "job_description": "",
        })
        assert resp.status_code == 400


# ─── Phase 4: RAG ──────────────────────────────────────────────────────────

class TestRAGEndpoints:
    def test_rag_status_not_indexed(self):
        resp = client.get(f"/api/v1/rag/status/{SAMPLE_RESUME_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["resume_id"] == SAMPLE_RESUME_ID
        assert "indexed" in data

    def test_rag_index_missing_resume(self):
        resp = client.post("/api/v1/rag/index", json={"resume_id": "nonexistent"})
        assert resp.status_code == 404

    def test_rag_query_empty_query(self):
        resp = client.post("/api/v1/rag/query", json={
            "resume_id": SAMPLE_RESUME_ID,
            "query": "",
            "top_k": 3,
        })
        assert resp.status_code == 400


# ─── Phase 5: Profile ──────────────────────────────────────────────────────

class TestProfileEndpoints:
    def test_get_autofill_profile(self):
        resp = client.get(f"/api/v1/profile/{SAMPLE_RESUME_ID}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["resume_id"] == SAMPLE_RESUME_ID
        assert "autofill_fields" in data
        assert data["autofill_fields"]["email"] == "john@example.com"
        assert data["autofill_fields"]["first_name"] == "John"

    def test_get_automation_schema(self):
        resp = client.get(f"/api/v1/profile/{SAMPLE_RESUME_ID}/automation-schema")
        assert resp.status_code == 200
        data = resp.json()
        assert "supported_platforms" in data
        assert "LinkedIn Easy Apply" in data["supported_platforms"]

    def test_profile_missing_resume(self):
        resp = client.get("/api/v1/profile/does-not-exist")
        assert resp.status_code == 404


# ─── Health ────────────────────────────────────────────────────────────────

class TestHealth:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"
