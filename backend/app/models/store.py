"""
models/store.py — In-memory session store for resume data.
In production, replace with Redis or a database (PostgreSQL, MongoDB).
Maps resume_id → ParsedResume + raw_text for use across all phases.
"""

from typing import Dict, Optional
from app.models.schemas import ParsedResume


class ResumeStore:
    """Thread-safe in-memory key-value store for parsed resume data."""

    def __init__(self):
        self._store: Dict[str, ParsedResume] = {}

    def save(self, resume_id: str, resume: ParsedResume) -> None:
        self._store[resume_id] = resume

    def get(self, resume_id: str) -> Optional[ParsedResume]:
        return self._store.get(resume_id)

    def exists(self, resume_id: str) -> bool:
        return resume_id in self._store

    def delete(self, resume_id: str) -> bool:
        if resume_id in self._store:
            del self._store[resume_id]
            return True
        return False

    def all_ids(self):
        return list(self._store.keys())


# Global singleton — replace with dependency-injected DB in production
resume_store = ResumeStore()
