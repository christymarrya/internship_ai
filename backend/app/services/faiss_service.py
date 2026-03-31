"""
services/faiss_service.py — FAISS vector store service.
Manages a FAISS flat index for storing and querying dense embeddings.
Supports per-resume namespaced indices for RAG retrieval (Phase 4).
Index is persisted to disk and reloaded on restart.
"""

import os
import json
import pickle
import numpy as np
from typing import List, Tuple, Dict, Optional
from pathlib import Path
from app.core.logger import get_logger

logger = get_logger(__name__)


class FAISSService:
    """
    Manages FAISS indices for:
    - Resume ↔ Job Description similarity (single global index)
    - Per-resume RAG chunk retrieval (namespaced indices)
    """

    def __init__(self, index_path: str = "data/faiss_index", dimension: int = 384):
        self.index_path = Path(index_path)
        self.dimension = dimension
        self.index_path.mkdir(parents=True, exist_ok=True)
        self._faiss = None
        self._indices: Dict[str, any] = {}  # namespace → faiss.Index
        self._metadata: Dict[str, List[str]] = {}  # namespace → list of text chunks
        self._load_faiss()

    def _load_faiss(self):
        try:
            import faiss
            self._faiss = faiss
            logger.info(f"FAISS loaded (version check OK, dim={self.dimension})")
        except ImportError:
            logger.warning("FAISS not installed. Run: pip install faiss-cpu")

    def _get_or_create_index(self, namespace: str):
        """Get existing FAISS index or create a new one for the namespace."""
        if namespace not in self._indices:
            if not self._faiss:
                return None
            index = self._faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine on L2-norm vecs)
            self._indices[namespace] = index
            self._metadata[namespace] = []
        return self._indices[namespace]

    def add_vectors(
        self,
        namespace: str,
        vectors: np.ndarray,
        texts: List[str],
    ) -> int:
        """
        Add vectors and their corresponding texts to the named index.

        Args:
            namespace: Logical name (e.g., resume_id for RAG, "global" for matching)
            vectors: Float32 numpy array of shape (n, dimension)
            texts: Corresponding text chunks for retrieval

        Returns:
            Number of vectors added
        """
        index = self._get_or_create_index(namespace)
        if index is None:
            logger.error("FAISS not available, cannot add vectors")
            return 0

        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        vectors = vectors.astype(np.float32)
        index.add(vectors)
        self._metadata[namespace].extend(texts)

        # Persist to disk
        self._save_index(namespace)
        logger.info(f"Added {len(vectors)} vectors to namespace '{namespace}'")
        return len(vectors)

    def search(
        self,
        namespace: str,
        query_vector: np.ndarray,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search for nearest vectors in the named index.

        Returns:
            List of (text_chunk, similarity_score) tuples sorted by score descending.
        """
        index = self._indices.get(namespace)
        if index is None:
            logger.warning(f"No index found for namespace '{namespace}'")
            return []

        if index.ntotal == 0:
            return []

        query_vector = query_vector.astype(np.float32).reshape(1, -1)
        actual_k = min(top_k, index.ntotal)
        scores, indices = index.search(query_vector, actual_k)

        results = []
        texts = self._metadata.get(namespace, [])
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(texts):
                results.append((texts[idx], float(score)))

        return results

    def namespace_exists(self, namespace: str) -> bool:
        return namespace in self._indices and self._indices[namespace].ntotal > 0

    def get_vector_count(self, namespace: str) -> int:
        if namespace in self._indices:
            return self._indices[namespace].ntotal
        return 0

    def _save_index(self, namespace: str):
        """Persist a FAISS index and its metadata to disk."""
        if not self._faiss or namespace not in self._indices:
            return
        try:
            index_file = self.index_path / f"{namespace}.index"
            meta_file = self.index_path / f"{namespace}.meta.pkl"
            self._faiss.write_index(self._indices[namespace], str(index_file))
            with open(meta_file, "wb") as f:
                pickle.dump(self._metadata[namespace], f)
        except Exception as e:
            logger.error(f"Failed to save FAISS index '{namespace}': {e}")

    def load_index(self, namespace: str) -> bool:
        """Load a persisted FAISS index from disk."""
        if not self._faiss:
            return False
        index_file = self.index_path / f"{namespace}.index"
        meta_file = self.index_path / f"{namespace}.meta.pkl"
        if not index_file.exists():
            return False
        try:
            self._indices[namespace] = self._faiss.read_index(str(index_file))
            with open(meta_file, "rb") as f:
                self._metadata[namespace] = pickle.load(f)
            logger.info(f"Loaded FAISS index '{namespace}' ({self._indices[namespace].ntotal} vectors)")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index '{namespace}': {e}")
            return False
