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

    result2 = service.filter_title("NonExistentMovie")
    assert result2 == []

   

