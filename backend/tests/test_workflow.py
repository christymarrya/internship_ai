"""
tests/test_workflow.py — Integration tests for the multi-agent workflow orchestrator.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ParsedResume, ExperienceEntry
from app.models.store import resume_store

client = TestClient(app)

SAMPLE_RESUME_ID = "workflow-test-resume"
SAMPLE_PARSED = ParsedResume(
    raw_text="Jane Doe\njane@example.com\nAI Engineer\nSkills: Python, TensorFlow, SQL",
    name="Jane Doe",
    email="jane@example.com",
    skills=["Python", "TensorFlow", "SQL"],
    experience=[ExperienceEntry(
        title="AI Engineer", company="AI Corp", duration="2022-2023", description="Developed ML models."
    )]
)

@pytest.fixture(autouse=True)
def seed_store():
    resume_store.save(SAMPLE_RESUME_ID, SAMPLE_PARSED)
    yield
    resume_store.delete(SAMPLE_RESUME_ID)

class TestWorkflowEndpoint:
    def test_run_workflow(self):
        # We need to mock the LLM generate calls as it's non-deterministic and requires an API key in CI.
        with patch("app.services.llm_service.LLMService.generate") as mock_generate, \
             patch("app.services.embedding_service.EmbeddingService.embed") as mock_embed, \
             patch("app.services.embedding_service.EmbeddingService.cosine_similarity") as mock_cos:
             
            import numpy as np
            mock_embed.return_value = np.zeros(384, dtype="float32")
            mock_cos.return_value = 0.85  # 85% match (>= 70 threshold for cover letter)
            
            # Mock the responses for: 1. Categorize Skills, 2. Internships, 3. Cover Letter
            mock_generate.side_effect = [
                # Response 1: Categorized Skills
                '{"programming_languages": ["Python", "SQL"], "ai_ml_skills": ["TensorFlow"], "tools_frameworks": []}',
                # Response 2: Internships
                '''[
                    {
                        "role": "Machine Learning Intern",
                        "company": "Tech Corp",
                        "location": "Remote",
                        "description": "Looking for Python and TensorFlow experience.",
                        "application_link": "https://example.com/apply"
                    }
                ]''',
                # Response 3: Cover Letter
                "Dear Hiring Manager,\n\nI am very excited to apply for this role..."
            ]

            resp = client.post("/api/v1/workflow/run", json={
                "resume_id": SAMPLE_RESUME_ID,
                "preferred_field": "Artificial Intelligence",
                "location": "Remote"
            })
            
            assert resp.status_code == 200, resp.text
            data = resp.json()
            assert data["resume_id"] == SAMPLE_RESUME_ID
            assert "Python" in data["categorized_skills"]["programming_languages"]
            assert len(data["applications"]) == 1
            
            app1 = data["applications"][0]
            assert app1["internship"]["company"] == "Tech Corp"
            assert app1["match_evaluation"]["match_score"] >= 8
            assert app1.get("cover_letter") is None
