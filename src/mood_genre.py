from pydantic import BaseModel, Field

class MovieGenre(BaseModel):
    """Structured data about a movie."""
    response_text: str = Field(description="The customized response text based on mood.")
    genres: list = Field(description="list of genres associated with the mood.")