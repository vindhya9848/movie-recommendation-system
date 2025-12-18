from typing import Optional, List
import pandas as pd

from src.config.settings import (
    MOVIES_CSV_PATH,
    REQUIRED_COLUMNS
)


class MovieRepository:
    """
    Handles loading and querying the cleaned movie dataset.
    This class is the single source of truth for movie data access.
    """

    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or MOVIES_CSV_PATH
        self._df: Optional[pd.DataFrame] = None

    def load(self) -> None:
        """Load the movie dataset into memory."""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"Movie dataset not found at: {self.csv_path}"
            )

        self._df = pd.read_csv(self.csv_path)
        self._validate_schema()

    def _validate_schema(self) -> None:
        """Ensure required columns exist."""
        if self._df is None:
            raise RuntimeError("Dataset not loaded")

        missing = REQUIRED_COLUMNS - set(self._df.columns)
        if missing:
            raise ValueError(
                f"Dataset missing required columns: {missing}"
            )

    @property
    def df(self) -> pd.DataFrame:
        """Safe access to underlying dataframe."""
        if self._df is None:
            raise RuntimeError("Call load() before accessing data")
        return self._df

    def get_all_movies(self) -> pd.DataFrame:
        """Return full dataset."""
        return self.df.copy()

    def filter_movies(
        self,
        language: Optional[List[str]] = None,
        max_runtime: Optional[int] = None,
        min_runtime: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Apply hard filters only (no ranking).
        """
        df = self.df

        if language:
            df = df[df["language"].isin(language)]

        if max_runtime is not None:
            df = df[df["runtime"] <= max_runtime]

        if min_runtime is not None:
            df = df[df["runtime"] >= min_runtime]

        return df.copy()

    def get_movie_by_id(self, movie_id: int) -> pd.Series:
        """Fetch a single movie by ID."""
        movie = self.df[self.df["movie_id"] == movie_id]
        if movie.empty:
            raise ValueError(f"Movie with id {movie_id} not found")
        return movie.iloc[0]
