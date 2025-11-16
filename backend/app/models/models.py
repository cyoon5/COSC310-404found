from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Annotated
from datetime import date

class Movie(BaseModel):
    title: str  # required
    movieIMDbRating: float  # required
    movieGenres: List[str]  # required
    directors: List[str]  # required
    mainStars: List[str]  # required
    totalRatingCount: Optional[int] = None
    totalUserReviews: Optional[str] = None
    totalCriticReviews: Optional[str] = None
    metaScore: Optional[str] = None
    datePublished: Optional[date] = None
    creators: Optional[List[str]] = None
    description: Optional[str] = None
    duration: Optional[int] = None

class Review(BaseModel):
    movieTitle: str
    user: str
    date: Annotated[date, Field(default_factory=date.today)] 
    rating: Optional[float] = None
    usefulVotes: Optional[int] = None
    totalVotes: Optional[int] = None
    title: str
    body: str
    reportCount: int = 0

class Report(BaseModel):
    review: Review  
    status: str = "pending"
    dateReported: date
    reason: Optional[str] = None 

class User(BaseModel):
    userName: str
    passwordHash: str
    role: Literal["user"] = "user"
    penalties: int = 0
    watchlist: List[str] = []

class Admin(BaseModel):
    adminName: str
    passwordHash: str
    role: Literal["admin"] = "admin"

