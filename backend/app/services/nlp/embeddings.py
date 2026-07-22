"""
Vector embeddings and semantic similarity calculation service.
"""
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings


class EmbeddingService:
    """Singleton wrapper for SentenceTransformer embedding generation."""

    _model = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Lazy load SentenceTransformer model."""
        if cls._model is None:
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate 384-dimensional vector embedding for text."""
        if not text or not text.strip():
            return [0.0] * 384
        model = cls.get_model()
        vector = model.encode(text, convert_to_numpy=True)
        return vector.tolist()

    @staticmethod
    def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vector embeddings.
        Returns score scaled from 0.0 to 100.0.
        """
        if not vec1 or not vec2:
            return 0.0
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)

        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0

        sim = cosine_similarity(v1, v2)[0][0]
        # Clip between 0 and 1, scale to 0-100
        score = max(0.0, min(1.0, float(sim))) * 100.0
        return round(score, 2)
