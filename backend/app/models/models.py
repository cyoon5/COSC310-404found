from pydantic import BaseModel
from typing import List, Optional
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
    date: date                         
    rating: Optional[float] = None    #out of 10
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
    password: str
    penalties: int = 0
    watchlist: List[str] = []  # list of movie title

class Admin(BaseModel):
    adminName: str
    password: str
