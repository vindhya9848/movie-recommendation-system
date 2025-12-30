from sentence_transformers import CrossEncoder
import numpy as np
from typing import List, Tuple

class ReRankerModel:
    """
    Wrapper for Cross-Encoder models to re-rank candidates.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model: CrossEncoder | None = None

    def load(self) -> None:
        if self._model is None:
            self._model = CrossEncoder(self.model_name)

    def rank(self, query: str, documents: List[str]) -> np.ndarray:
        """
        Returns a relevance score for each document relative to the query.
        """
        if not documents:
            return np.array([])
            
        self.load()
        # Create pairs: [[query, doc1], [query, doc2]...]
        pairs = [[query, doc] for doc in documents]
        scores = self._model.predict(pairs)
        return scores