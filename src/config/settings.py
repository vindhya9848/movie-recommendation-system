from pathlib import Path

# ========================
# Base paths
# ========================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "datasets" / "cleaned"
# MOVIES_CSV_PATH = DATASET_DIR / "movies_cleaned.csv"
MOVIES_CSV_PATH = DATASET_DIR / "movies_cleaned_2.csv"

#=========Mood Predictor================
MODEL_PATH = PROJECT_ROOT /"src" /"models" / "emotion_model"
MODEL_NAME = "borisn70/bert-43-multilabel-emotion-detection"

# ========================
# Embedding configuration
# ========================
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
EMBEDDING_DTYPE = "float32"

# ========================
# FAISS configuration
# ========================
FAISS_INDEX_DIR = PROJECT_ROOT / "datasets" / "faiss"
FAISS_INDEX_PATH = FAISS_INDEX_DIR / "movies.index"

# ========================
# Recommendation defaults
# ========================
TOP_K_RECOMMENDATIONS = 10

# Similarity weights (used later)
GENRE_BOOST = 0.3
LANGUAGE_BOOST = 0.3
POPULARITY_BOOST = 0.05

YES_WORDS = ["yes", "yeah", "yep", "sure", "okay", "ok", "Yah", "absolutely", "definitely","Yes please","Ya", 'y', 'yea', "sure"]
NO_WORDS = ["no", "nope", "nah", "not really", "don't", "do not","No thanks","No thank you", 'n', 'nah', 'noo']
LANGUAGES = [
    "English", "Hindi", "Telugu", "Tamil", "Korean",
    "Japanese", "Spanish", "French", "Persian", "Urdu", 
    "Arabic", "Bengali","Chinese","German"
]
genres = [
    "action",
    "adventure",
    "animation",
    "comedy",
    "crime",
    "documentary",
    "biography",
    "drama",
    "family",
    "fantasy",
    "history",
    "horror",
    "music",
    "mystery",
    "romance",
    "sci-fi",
    "thriller",
    "war",
    "western"
]
# ========================
# Validation schema
# ========================
REQUIRED_COLUMNS = {
    "movie_id",
    "title",
    "embedding_text",
    "genres",
    "cast",
    "keywords",
    "runtime",
    "language",
    "release_year",
}
