from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config.settings import EMBEDDING_MODEL_NAME, EMBEDDING_DTYPE


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer for generating embeddings.
    Responsible ONLY for embedding text.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def load(self) -> None:
        """Load the embedding model into memory."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single string into a vector.
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        self.load()

        vector = self._model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return vector.astype(EMBEDDING_DTYPE)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed multiple strings into a 2D array.
        Shape: (num_texts, embedding_dim)
        """
        if not texts or not isinstance(texts, list):
            raise ValueError("Texts must be a non-empty list of strings")

        self.load()

        vectors = self._model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return vectors.astype(EMBEDDING_DTYPE)
