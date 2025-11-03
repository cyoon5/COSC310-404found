from pathlib import Path
from backend.app.models.models import Movie
from backend.app.repositories.moviesRepo import save_movies, load_all_movies, update_movie_csv, delete_movies, update_movies



movieTest = Movie(
    title="TestMovie1",
    movieIMDbRating=9.0,
    totalRatingCount=100,
    totalUserReviews="100",
    totalCriticReviews="10",
    metaScore="80",
    movieGenres=["Action"],
    directors=["Director A"],
    datePublished="2023-01-01",
    creators=["Creator X"],
    mainStars=["Star 1", "Star 2"],
    description="Test description",
    duration=120
)



update_movies("TestMovie1", {"directors": ["NEW DIRECTOR A"]})








