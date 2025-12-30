import sys
from pathlib import Path
from dotenv import load_dotenv
from src.models.reranker_model import ReRankerModel
from src.conversation.get_useful_info import get_useful_info
from src.chatbotservice.chatbot_service import ChatbotService

# ------------------------------------------------
# Ensure project root is on PYTHONPATH
# ------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

# ------------------------------------------------
# Imports
# ------------------------------------------------
from src.data.movie_repository import MovieRepository
from src.models.embedding_model import EmbeddingModel
from src.index.index_builder import IndexBuilder
from src.recommender.recommendation_engine import RecommendationEngine



def print_recommendations(df):
    print("\n There you Go! 🎬 Here are some recommended movies for you!:\n")
    for i, row in df.iterrows():
        print(
            f"{i+1}. {row['title']} "
            f"(Score: {row['final_score']:.3f})"
        )
        
        # Check if genres is a string; if not (like NaN), use "Unknown"
        raw_genres = row['genres']
        if isinstance(raw_genres, str):
            genres_list = raw_genres.split('|')
            genres_display = ', '.join(genres_list)
        else:
            genres_display = "Unknown"
            
        print(f"   Genres: {genres_display}")
        print(f"   Runtime: {row['runtime']} mins")
        print()


def main():
    # ------------------------------------------------
    # Load data
    # ------------------------------------------------
    load_dotenv()
    repo = MovieRepository()
    repo.load()



    # engine.recommend(user_profile)

    # ------------------------------------------------
    # Load embedding model
    # ------------------------------------------------
    embedder = EmbeddingModel()

    re_ranker = ReRankerModel()

    # ------------------------------------------------
    # Load FAISS index + mapping
    # ------------------------------------------------
    builder = IndexBuilder(repo, embedder)
    faiss_index, mapping = builder.load_index()

    # ------------------------------------------------
    # Initialize core services
    # ------------------------------------------------



    service = ChatbotService()

    result =service.run_chatbot()

    print("Conversation State:", vars(result))


    recommender = RecommendationEngine(
        repository=repo,
        embedding_model=embedder,
        faiss_index=faiss_index,
        index_to_movie_id=mapping
    )
     

    user_profile = get_useful_info(result)

    # user_profile = {'query_text': 'love destiny power mythology good vs evil epic magical saga', 'genres': ['comedy', 'action', 'adventure'], 'language': None, 'runtime': None}

    # user_profile = get_useful_info(result)
    print("User Profile for Recommendations:", user_profile)
    recommended_df = recommender.recommend(user_profile)
    print_recommendations(recommended_df)


 


if __name__ == "__main__":
    main()
