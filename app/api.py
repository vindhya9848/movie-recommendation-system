from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import pandas as pd

from src.models.reranker_model import ReRankerModel
from src.data.movie_repository import MovieRepository
from src.models.embedding_model import EmbeddingModel
from src.index.index_builder import IndexBuilder
from src.recommender.recommendation_engine import RecommendationEngine
from src.chatbotservice.chatbot_service import ChatbotService
from src.conversation.get_useful_info import get_useful_info


router = APIRouter()

# ----------------------------
# App singleton state
# ----------------------------
class AppState:
    def __init__(self):
        self.repo = None
        self.embedder = None
        self.re_ranker = None
        self.recommender = None
        self.chatbot = None

 

STATE = AppState()

def ensure_initialized():
    if STATE.recommender is not None:
        return
    
    print("Initializing movie bot ..✅.")
    repo = MovieRepository()
    repo.load()

    embedder = EmbeddingModel()
    re_ranker = ReRankerModel()
    builder = IndexBuilder(repo, embedder)
    faiss_index, mapping = builder.load_index()

    recommmender = RecommendationEngine(
        repository=repo,
        embedding_model=embedder,
        faiss_index=faiss_index,
        index_to_movie_id=mapping)
    
    chatbot = ChatbotService()

    STATE.repo = repo
    STATE.re_ranker = re_ranker
    STATE.embedder = embedder
    STATE.recommender = recommmender
    STATE.chatbot = chatbot

    print("Movie bot is ready! 🚀")
    



@router.on_event("startup")
def startup():
    pass
    # Equivalent of your main()



# ----------------------------
# API models
# ----------------------------
class MessageIn(BaseModel):
    text: str


class RecommendationOut(BaseModel):
    title: str
    genres: Optional[str] = None
    runtime: Optional[int]  = None
    final_score: float


class MessageOut(BaseModel):
    reply: str
    recommendations: List[RecommendationOut] = []


# ----------------------------
# API endpoint
# ----------------------------
@router.post("/message", response_model=MessageOut)
def message(payload: MessageIn):
    ensure_initialized()
    reply, ready, state, exited = STATE.chatbot.handle_user_message(payload.text)

    # if not ready:
    #     return {"reply": reply, "recommendations": [], "exited": False}
    
    if exited:
        return {
        "reply": reply,
        "recommendations": [],
        "exited": True  
          }
    
    if state.is_complete:
        STATE.chatbot = ChatbotService()
        return MessageOut(
            reply="Good Bye! Type something to start new conversation",
            recommendations=[],
            exited=False
        )

    if not ready:
        return MessageOut(reply=reply, recommendations=[], exited=False)

    # 🔹 EXACTLY your existing flow
    user_profile = get_useful_info(state)
    print("================user profile:=====================",user_profile)
    state.is_complete = True
    recommended_df = STATE.recommender.recommend(user_profile)

    recommendations = [
        RecommendationOut(
            title=row["title"],
            genres=row.get("genres", "") if pd.notna(row["genres"]) else "",
            runtime=row.get("runtime"),
            final_score=float(row["final_score"]),
        )
        for _, row in recommended_df.iterrows()
    ]

    

    return MessageOut(
        reply="🎬 Here are some movies you might enjoy! Please enter exit to reset the chat",
        recommendations=recommendations,
        exited= False
    )
