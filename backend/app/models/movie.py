from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Movie(BaseModel):
    title: str
    movieIMDbRating: Optional[float] = None
    totalRatingCount: Optional[int] = None
    totalUserReviews: Optional[str] = None
    totalCriticReviews: Optional[str] = None
    metaScore: Optional[str] = None
    movieGenres: Optional[List[str]] = None
    directors: Optional[List[str]] = None
    datePublished: Optional[date] = None
    creators: Optional[List[str]] = None
    mainStars: Optional[List[str]] = None
    description: Optional[str] = None
    duration: Optional[int] = None