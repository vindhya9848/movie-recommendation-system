from typing import List
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """Structured data about a movie."""
    title: str = Field(description="The full title of the movie.")
    themes: List[str] = []
    plot: str  = Field(description="keyword based plot")
