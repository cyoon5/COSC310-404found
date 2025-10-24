from pydantic import BaseModel
import datetime


class Movie(BaseModel):
    movieId: int
    title: str
    category: str
    releaseDate: datetime
    averageRating: float

class Review(BaseModel):
    reviewId: int
    userId: int
    movieId: int
    header: str
    body: str
    date: datetime
    reportCount: int

class Watchlist(BaseModel):
    watchlistId: int
    userId: int
    movies: List[Movie]

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

class Admin(BaseModel):
    adminId: int
    userName: str
    password: str