import pytest
from backend.app.services.movieService import MovieService
from backend.app.models.models import Movie

def test_filter_title():
    service = MovieService()
        
    result = service.filter_title("Avengers")
    assert len(result) == 2
# Check that the returned movies contain the keyword in their title
    for movie in result:
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
   

