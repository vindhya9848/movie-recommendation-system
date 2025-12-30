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
        Build or append to FAISS index from movie embeddings.
        """
        df = self.repository.get_all_movies()

        if "embedding_text" not in df.columns:
            raise ValueError("embedding_text column missing")

        if df.empty:
            return

        # 👉 IMPORTANT: Only embed rows we are about to add
        texts = df["embedding_text"].tolist()
        vectors = self.embedding_model.embed_texts(texts)

        # Load or create index
        if self.index_path.exists():
            index = FaissIndex.load(self.index_path)
        else:
            index = FaissIndex(dim=vectors.shape[1])

        # Append vectors (THIS is the real add)
        index.add(vectors)

        # Save index first
        index.save(self.index_path)

        # Append mapping AFTER index.add()
        self._save_mapping(df)

        # Safety check
        self._validate_index_vs_mapping(index)

    def _save_mapping(self, df: pd.DataFrame) -> None:
        """
        Append FAISS index → movie_id mapping.
        """
        new_movie_ids = df["movie_id"].to_numpy()

        self.mapping_path.parent.mkdir(parents=True, exist_ok=True)

        if self.mapping_path.exists():
            existing_movie_ids = np.load(self.mapping_path)
            combined_movie_ids = np.concatenate(
                [existing_movie_ids, new_movie_ids]
            )
        else:
            combined_movie_ids = new_movie_ids

        np.save(self.mapping_path, combined_movie_ids)

    def _validate_index_vs_mapping(self, index: FaissIndex) -> None:
        """
        Ensure FAISS index and mapping stay aligned.
        """
        movie_ids = np.load(self.mapping_path)
        if index.index.ntotal != len(movie_ids):
            raise RuntimeError(
                f"FAISS index size ({index.index.ntotal}) "
                f"!= mapping size ({len(movie_ids)})"
            )

    def load_index(self) -> tuple[FaissIndex, np.ndarray]:
        """
        Load FAISS index and movie_id mapping.
        """
        index = FaissIndex.load(self.index_path)

        if not self.mapping_path.exists():
            raise FileNotFoundError(
                f"Mapping file not found at {self.mapping_path}"
            )

        movie_ids = np.load(self.mapping_path)
        return index, movie_ids
