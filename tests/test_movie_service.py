from unittest.mock import patch
import pytest
from backend.app.services.movieService import MovieService
from backend.app.models.models import Movie
from datetime import datetime


def test_get_all_movies():
    service = MovieService()
    all_movies = service.get_all_movies()
    assert len(all_movies) > 0  #At least one movie should be present in the dataset

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

def test_filter_by_start_date():
    service = MovieService()
    start_date = datetime(2010, 1, 1)
    result = service.filter_by_start_date(start_date)
    assert len(result) > 0
    for movie in result: #Ensure that every movie in the result was released on or after the start date
        assert movie.datePublished >= start_date.date()


# Sample movies to use in the test(Mocking)
sample_movies = [
    Movie(title="Movie A", movieIMDbRating=7.2, movieGenres=["Action"], directors=["Dir1"], mainStars=["Star1"], datePublished=datetime(2020, 1, 1), creators=["Creator1"]),
    Movie(title="Movie B", movieIMDbRating=9.0, movieGenres=["Drama"], directors=["Dir2"], mainStars=["Star2"], datePublished=datetime(2021, 1, 1), creators=["Creator2"]),
    Movie(title="Movie C", movieIMDbRating=5.5, movieGenres=["Comedy"], directors=["Dir3"], mainStars=["Star3"], datePublished=datetime(2019, 6, 1), creators=["Creator3"]),
]
@patch("backend.app.services.movieService.load_all_movies") # Mocked path
def test_sort_by_rating(mock_load_all):
    #  Mock load_all_movies to return the sample list
    mock_load_all.return_value = sample_movies

    service = MovieService()

    # Test ascending sort
    ascending = service.sort_by_rating(descending=False)
    assert ascending[0].title == "Movie C"
    assert ascending[1].title == "Movie A"
    assert ascending[2].title == "Movie B"

    # Test descending sort
    descending = service.sort_by_rating(descending=True)
    assert descending[0].title == "Movie B"
    assert descending[1].title == "Movie A"
    assert descending[2].title == "Movie C"

def test_sort_by_release_date():
    service = MovieService()
    sorted_movies_asc = service.sort_by_release_date(descending=False)
    sorted_movies_desc = service.sort_by_release_date(descending=True)

    # Check ascending order
    for i in range(len(sorted_movies_asc) - 1):
        assert sorted_movies_asc[i].datePublished <= sorted_movies_asc[i + 1].datePublished

    # Check descending order
    for i in range(len(sorted_movies_desc) - 1):
        assert sorted_movies_desc[i].datePublished >= sorted_movies_desc[i + 1].datePublished


def test_get_filtered_movies():
    service = MovieService()
    title = "Avengers"
    start_date = datetime(2015, 1, 1)
    min_rating = 8.1

    result = service.get_filtered_movies(start_date=start_date, min_rating=min_rating)
    assert len(result) == 1 # Only "Avengers: Endgame" should match
    for movie in result:
        assert title in movie.title
        assert movie.datePublished >= start_date.date()
        assert min_rating <= movie.movieIMDbRating

def test_movie_creation():
    service = MovieService()
    new_movie = Movie(
        title="TestMovie2",
        movieIMDbRating=7.8,
        totalRatingCount=1234,
        movieGenres=["Drama"],
        directors=["A Director"],
        creators=["A Creator"],
        mainStars=["Star Person"],
        datePublished=datetime(2020, 1, 1).date()
    )
    try:
        service.create_movie(new_movie)
    except ValueError as e:
        pytest.fail(f"Movie creation failed with error: {e}")

    result = service.filter_title("TestMovie2")
    assert len(result) == 1
    assert result[0].title == "TestMovie2"



