from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Movie(BaseModel): #Field can be emtpty due to Optional keyword
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


class Review(BaseModel):
    reviewId: int
    userId: int
    movieId: int
    header: str
    body: str
    date: date
    reportCount: int = 0

class Watchlist(BaseModel):
    watchlistId: int
    userId: int
    movies: List[int] #Store movie id instead of full movie obj more efficient

class Report(BaseModel):
    status: str
    review: Review

class Rating(BaseModel):
    rating: int
    movieId: int
    userId: int

class User(BaseModel):
    userId: int
    userName: str
    password: str
    watchlist : Optional[Watchlist] = None

class Admin(BaseModel):
    adminId: int
    userName: str
    password: str