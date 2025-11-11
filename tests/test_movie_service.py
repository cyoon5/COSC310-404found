import pytest
from backend.app.services.movieService import MovieService
from backend.app.models.models import Movie
from datetime import datetime

def test_filter_title():
    service = MovieService()
        
    result = service.filter_title("Avengers")
    assert len(result) == 2
    for movie in result: # Check that the returned movies contain the keyword in their title
        assert "Avengers" in movie.title    

    result2 = service.filter_title("this movie does not exist")
    assert result2 == []

def test_filter_rating_min():
    service = MovieService()
    result = service.filter_rating_min(8.0)
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result has rating >= 8.0
        assert movie.movieIMDbRating >= 8.0 

def test_filter_rating_max():
    service = MovieService()
    result = service.filter_rating_max(6.0)
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result has rating <= 6.0
        assert movie.movieIMDbRating <= 6.0

def test_filter_genre():
    service = MovieService()
    result = service.filter_genre("Action")
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result has genre "Action"
        assert "Action" in movie.movieGenres

def test_filter_director():
    service = MovieService()
    result = service.filter_director("Todd Phillips")
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result is directed by "Steven Spielberg"
        assert any("Todd Phillips".lower() in director.lower() for director in movie.directors)
   
def test_filter_main_stars():
    service = MovieService()
    result = service.filter_main_stars("Robert Downey Jr.")
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result features "Robert Downey Jr." as main star
        assert any("Robert Downey Jr.".lower() in star.lower() for star in movie.mainStars)


def test_sort_by_release_date():
    service = MovieService()
    def _to_datetime(d):
        if d is None:
            return datetime.min
        if isinstance(d, datetime):
            return d
        # avoid importing date at top-level in case of name clash
        try:
            from datetime import date as _date
        except Exception:
            _date = None
        if _date is not None and isinstance(d, _date):
            return datetime.combine(d, datetime.min.time())
        if isinstance(d, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(d, fmt)
                except Exception:
                    continue
            try:
                return datetime.fromisoformat(d)
            except Exception:
                return datetime.min
        # fallback
        return datetime.min

    # Sort movies by release date ascending
    sorted_movies = service.sort_by_release_date()
    for i in range(len(sorted_movies) - 1):
        date_current = _to_datetime(sorted_movies[i].datePublished)
        date_next = _to_datetime(sorted_movies[i + 1].datePublished)
        assert date_current <= date_next  # Ensure the list is sorted in ascending order

