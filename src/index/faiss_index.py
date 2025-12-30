from typing import Tuple
from pathlib import Path
import numpy as np
import faiss


class FaissIndex:
    """
    Thin wrapper around FAISS index for vector similarity search.
    """

    def __init__(self, dim: int):
        """
        :param dim: embedding dimension (e.g. 768 for SBERT)
        """
        self.dim = dim
        self.index: faiss.Index | None = None

    # -----------------------------
    # BUILD (fresh index)
    # -----------------------------
    def build(self, vectors: np.ndarray) -> None:
        """
        Build a NEW FAISS index from vectors.
        This overwrites any existing index in memory.
        """
        self._validate_vectors(vectors)

        faiss.normalize_L2(vectors)

        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)

    # -----------------------------
    # ADD (append vectors)
    # -----------------------------
    def add(self, vectors: np.ndarray) -> None:
        """
        Append vectors to an existing FAISS index.
        Creates index if not present.
        """
        if vectors is None or len(vectors) == 0:
            return

        self._validate_vectors(vectors)

        faiss.normalize_L2(vectors)

        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dim)

        self.index.add(vectors)

    # -----------------------------
    # SAVE / LOAD
    # -----------------------------
    def save(self, path: Path) -> None:
        """
        Persist FAISS index to disk.
        """
        if self.index is None:
            raise RuntimeError("Index has not been built or loaded")

        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path: Path) -> "FaissIndex":
        """
        Load FAISS index from disk and return a FaissIndex instance.
        """
        if not path.exists():
            raise FileNotFoundError(f"FAISS index not found at {path}")

        index = faiss.read_index(str(path))
        obj = cls(dim=index.d)
        obj.index = index
        return obj

    # -----------------------------
    # SEARCH
    # -----------------------------
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform similarity search.
        """
        if self.index is None:
            raise RuntimeError("Index not loaded or built")

        if query_vector.ndim != 1 or query_vector.shape[0] != self.dim:
            raise ValueError(
                f"Expected query vector of shape ({self.dim},), got {query_vector.shape}"
            )

        query_vector = query_vector.astype(np.float32)
        faiss.normalize_L2(query_vector.reshape(1, -1))

        scores, indices = self.index.search(
            query_vector.reshape(1, -1),
            top_k
        )

        return scores[0], indices[0]

    # -----------------------------
    # INTERNAL HELPERS
    # -----------------------------
    def _validate_vectors(self, vectors: np.ndarray) -> None:
        if vectors.ndim != 2:
            raise ValueError(f"Vectors must be 2D, got {vectors.shape}")

        if vectors.shape[1] != self.dim:
            raise ValueError(
                f"Vector dim {vectors.shape[1]} != index dim {self.dim}"
            )

        if vectors.dtype != np.float32:
            raise ValueError("Vectors must be float32")
