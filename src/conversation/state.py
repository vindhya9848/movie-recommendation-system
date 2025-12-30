# src/conversation_state.py

from dataclasses import dataclass, field
from typing import List, Optional

from src.mood_genre import MovieGenre

@dataclass
class ConversationState:
    mood: Optional[str] = None
    suggested_genres: List[str] = field(default_factory=list)
    selected_genres: List[str] = None
    movie_description: str = None
    language: Optional[str] = None
    res: Optional[MovieGenre] = None
    runtime: Optional[str] = None
    current_step: str = "ask_mood"
    intents: List[str] = None
    is_complete = False
    # genres_suggested: str= None
    # genres_selected: str= None

    def clear(self):
        self.__init__()
