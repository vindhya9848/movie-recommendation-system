from typing import List, Dict, Any
import numpy as np
import pandas as pd
from typing import Optional
from src.models.embedding_model import EmbeddingModel
from src.index.faiss_index import FaissIndex
from src.data.movie_repository import MovieRepository
from src.config.settings import (
    TOP_K_RECOMMENDATIONS,
    GENRE_BOOST,
    POPULARITY_BOOST,
)


class RecommendationEngine:
    """
    Core recommendation engine combining semantic similarity,
    hard filters, and soft ranking boosts.
    """

    def __init__(
        self,
        repository: MovieRepository,
        embedding_model: EmbeddingModel,
        faiss_index: FaissIndex,
        index_to_movie_id: np.ndarray,
    ):
        self.repository = repository
        self.embedding_model = embedding_model
        self.index = faiss_index
        self.index_to_movie_id = index_to_movie_id

    def recommend(
        self,
        user_profile: Dict[str, Any],
        top_k: int = TOP_K_RECOMMENDATIONS,
        faiss_k: int = 50,
    ) -> pd.DataFrame:
        """
        Generate movie recommendations.
        """
        query_text = user_profile.get("query_text")
        # intents = user_profile.get('intent_terms')
        if not query_text:
            raise ValueError("query_text is required")

        # 1. Embed user query
        text_to_embed = query_text
        query_vector = self.embedding_model.embed_text(text_to_embed)

        # 2. FAISS retrieval
        scores, indices = self.index.search(query_vector, top_k=faiss_k)

        candidate_ids = self.index_to_movie_id[indices]
        df_candidates = self.repository.df[
            self.repository.df["movie_id"].isin(candidate_ids)
        ].copy()

        # Attach similarity scores
        score_map = dict(zip(candidate_ids, scores))
        df_candidates["similarity_score"] = df_candidates["movie_id"].map(score_map)

        # 3. Hard filters
        df_candidates = self._apply_hard_filters(
            df_candidates,
            user_profile
        )

        if df_candidates.empty:
            return df_candidates

        # 4. Soft boosts
        df_candidates["final_score"] = df_candidates["similarity_score"]
        df_candidates["final_score"] += self._genre_boost(
            df_candidates,
            user_profile.get("genres")
        )
        df_candidates["final_score"] += self._popularity_boost(df_candidates)
        df_candidates = df_candidates.drop_duplicates(subset=['movie_id'])

        # 5. Rank & return
        return (
            df_candidates
            .sort_values("final_score", ascending=False)
            .head(top_k)
            .reset_index(drop=True)
        )

    # -----------------------
    # Hard filters
    # -----------------------

    def _apply_hard_filters(
        self,
        df: pd.DataFrame,
        user_profile: Dict[str, Any],
    ) -> pd.DataFrame:
        languages = user_profile.get("language")
        runtime = user_profile.get("runtime", {})

        if languages:
            df = df[df["language"].isin(languages)]

        if runtime:
            if runtime.get("max") is not None:
                df = df[df["runtime"] <= runtime["max"]]
            if runtime.get("min") is not None:
                df = df[df["runtime"] >= runtime["min"]]
            if runtime.get("exact") is not None:
                df = df[df["runtime"] == runtime["exact"]]
            
        if not runtime:
            df = df[df['runtime'] >= 50]

        return df

    # -----------------------
    # Soft boosts
    # -----------------------

    def _genre_boost(
        self,
        df: pd.DataFrame,
        preferred_genres: Optional[List[str]],
    ) -> np.ndarray:
        if not preferred_genres:
            return 0.0

        def match(genres: str) -> float:
            if not isinstance(genres, str):
                return 0.0
            movie_genres = set(genres.split(","))
            return GENRE_BOOST if movie_genres & set(preferred_genres) else 0.0

        return df["genres"].apply(match)

    def _popularity_boost(self, df: pd.DataFrame) -> np.ndarray:
        """
        Light popularity boost using vote_average.
        """
        if "vote_average" not in df.columns:
            return 0.0

        # Normalize to 0–1 range
        votes = df["vote_average"].fillna(0)
        norm = (votes - votes.min()) / (votes.max() - votes.min() + 1e-6)

        return norm * POPULARITY_BOOST
