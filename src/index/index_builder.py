from pathlib import Path
import numpy as np
import pandas as pd

from src.data.movie_repository import MovieRepository
from src.models.embedding_model import EmbeddingModel
from src.index.faiss_index import FaissIndex
from src.config.settings import FAISS_INDEX_PATH


class IndexBuilder:
    """
    Builds and persists a FAISS index for movies.
    """

    def __init__(
        self,
        repository: MovieRepository,
        embedding_model: EmbeddingModel,
        index_path: Path = FAISS_INDEX_PATH,
    ):
        self.repository = repository
        self.embedding_model = embedding_model
        self.index_path = index_path
        self.mapping_path = index_path.with_suffix(".mapping.npy")

    def build(self) -> None:
        """
        Build FAISS index from movie embeddings and save it.
        """
        # Ensure data is loaded
        df = self.repository.get_all_movies()

        if "embedding_text" not in df.columns:
            raise ValueError("embedding_text column missing")

        texts = df["embedding_text"].tolist()

        # Generate embeddings
        vectors = self.embedding_model.embed_texts(texts)

        # Build FAISS index
        index = FaissIndex(dim=vectors.shape[1])
        index.build(vectors)

        # Persist index and mapping
        index.save(self.index_path)
        self._save_mapping(df)

    def _save_mapping(self, df: pd.DataFrame) -> None:
        """
        Save FAISS index → movie_id mapping.
        """
        movie_ids = df["movie_id"].to_numpy()
        self.mapping_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(self.mapping_path, movie_ids)

    def load_index(self) -> tuple[FaissIndex, np.ndarray]:
        """
        Load FAISS index and movie_id mapping.
        """
        index = FaissIndex(dim=0)
        index.load(self.index_path)

        if not self.mapping_path.exists():
            raise FileNotFoundError(
                f"Mapping file not found at {self.mapping_path}"
            )

        movie_ids = np.load(self.mapping_path)
        return index, movie_ids
