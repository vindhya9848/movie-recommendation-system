
from src.conversation.state import ConversationState


def get_useful_info(state: ConversationState) -> dict:
    info = {
        "query_text": state.movie_description if state.movie_description else '',
        "genres": list(state.selected_genres) if state.selected_genres else list(state.suggested_genres),
        # "fallback_genres": list(state.suggested_genres) if state.suggested_genres else [],
        "language": list(state.language) if state.language else [],
        "runtime": state.runtime if state.runtime else None
    }
    return info