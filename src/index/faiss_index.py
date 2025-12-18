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

    def build(self, vectors: np.ndarray) -> None:
        """
        Build a FAISS index from vectors.

        :param vectors: shape (n, dim), dtype float32, normalized
        """
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(
                f"Expected vectors of shape (n, {self.dim}), got {vectors.shape}"
            )

        if vectors.dtype != np.float32:
            raise ValueError("Vectors must be float32")

        # Inner product index (works as cosine similarity if vectors are normalized)
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(vectors)

    def save(self, path: Path) -> None:
        """
        Persist FAISS index to disk.
        """
        if self.index is None:
            raise RuntimeError("Index has not been built")

        path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path))

    def load(self, path: Path) -> None:
        """
        Load FAISS index from disk.
        """
        if not path.exists():
            raise FileNotFoundError(f"FAISS index not found at {path}")

        self.index = faiss.read_index(str(path))
        self.dim = self.index.d

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform similarity search.

        :returns:
            scores: shape (top_k,)
            indices: shape (top_k,)
        """
        if self.index is None:
            raise RuntimeError("Index not loaded or built")

        if query_vector.ndim != 1 or query_vector.shape[0] != self.dim:
            raise ValueError(
                f"Expected query vector of shape ({self.dim},), got {query_vector.shape}"
            )

        # FAISS expects shape (1, dim)
        scores, indices = self.index.search(
            query_vector.reshape(1, -1),
            top_k
        )

        return scores[0], indices[0]
