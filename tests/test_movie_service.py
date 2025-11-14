import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from backend.app.services.movieService import MovieService
from backend.app.models.models import Movie
from backend.app.main import app


# UNIT TESTS
@pytest.fixture
def sample_movies():
    return [
        Movie(title="Movie A", movieIMDbRating=7.2, movieGenres=["Action"], directors=["Dir1"], mainStars=["Star1"],
              datePublished=datetime(2020, 1, 1), creators=["Creator1"]),
        Movie(title="Movie B", movieIMDbRating=9.0, movieGenres=["Drama"], directors=["Dir2"], mainStars=["Star2"],
              datePublished=datetime(2021, 1, 1), creators=["Creator2"]),
        Movie(title="Movie C", movieIMDbRating=5.5, movieGenres=["Comedy"], directors=["Dir3"], mainStars=["Star3"],
              datePublished=datetime(2019, 6, 1), creators=["Creator3"]),
    ]


# Equivalence partitioning test for rating boundary
def test_filter_rating_min_equivalence(sample_movies):
    service = MovieService()
    result = service.filter_rating_min(sample_movies, 7.2)
    assert all(m.movieIMDbRating >= 7.2 for m in result)
    assert any(m.movieIMDbRating == 7.2 for m in result)


# Mocking repository layer method so it uses sample data
@patch("backend.app.services.movieService.load_all_movies")
def test_sort_by_rating(mock_load_all, sample_movies):
    mock_load_all.return_value = sample_movies
    service = MovieService()
    result = service.sort_by_rating(sample_movies, descending=True)
    assert result[0].movieIMDbRating == 9.0 #highest rating
    assert result[-1].movieIMDbRating == 5.5 #lowest rating


# Exception handling test (missing title)
def test_create_movie_raises_value_error_on_empty_title():
    service = MovieService()
    movie = Movie(
        title="",
        movieIMDbRating=8.0,
        totalRatingCount=100,
        movieGenres=["Drama"],
        directors=["A Director"],
        creators=["A Creator"],
        mainStars=["Actor"],
        datePublished=datetime(2020, 1, 1).date()
    )
    with pytest.raises(ValueError, match="Title cannot be empty"):
        service.create_movie(movie)


# Fault injection test – simulate repo failure
@patch("backend.app.services.movieService.save_movies", side_effect=Exception("Disk write error"))
@patch("backend.app.services.movieService.load_all_movies", return_value=[])
def test_create_movie_repo_failure(mock_load, mock_save):
    service = MovieService()
    movie = Movie(
        title="CrashMovie",
        movieIMDbRating=7.8,
        totalRatingCount=1234,
        movieGenres=["Drama"],
        directors=["A Director"],
        creators=["A Creator"],
        mainStars=["Star Person"],
        datePublished=datetime(2020, 1, 1).date()
    )
    with pytest.raises(RuntimeError, match="Failed to save movie"):
        service.create_movie(movie)


# Update logic – partial dict update
@patch("backend.app.services.movieService.load_movie_by_title")
@patch("backend.app.services.movieService.update_movies")
def test_update_movie_partial(mock_update, mock_load):
    existing = Movie(
        title="OldMovie", movieIMDbRating=6.0, movieGenres=["Comedy"],
        directors=["DirX"], mainStars=["StarY"], creators=["CreatorZ"],
        datePublished=datetime(2019, 5, 1)
    )
    mock_load.return_value = existing
    service = MovieService()

    updated = service.update_movie("OldMovie", {"movieIMDbRating": 8.5})
    assert updated.movieIMDbRating == 8.5
    mock_update.assert_called_once_with("OldMovie", {"movieIMDbRating": 8.5})


# Deletion – test exception if missing movie
@patch("backend.app.services.movieService.delete_movies", side_effect=FileNotFoundError("No such movie"))
def test_delete_movie_missing(mock_delete):
    service = MovieService()
    with pytest.raises(FileNotFoundError):
        service.delete_movie("NonexistentMovie")



#Integration Tests

client = TestClient(app)


# Integration test: getting all movies
def test_integration_get_all_movies(monkeypatch):
    mock_movie = Movie(
        title="Random", movieIMDbRating=8.5, movieGenres=["Thriller"],
        directors=["Int Director"], mainStars=["Int Star"], creators=["Int Creator"],
        datePublished=datetime(2021, 5, 15)
    )
    with patch("backend.app.services.movieService.load_all_movies", return_value=[mock_movie]):
        response = client.get("/movies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Random"


# Integration test: create and retrieve movie
def test_integration_create_and_get_movie(monkeypatch, tmp_path):
    # Patch DATA_PATH to temp dir (avoids touching real data)
    monkeypatch.setattr("backend.app.repositories.moviesRepo.DATA_PATH", tmp_path)

    new_movie = {
        "title": "RandomMovie",
        "movieIMDbRating": 8.3,
        "totalRatingCount": 5000,
        "movieGenres": ["Sci-Fi"],
        "directors": ["Test Director"],
        "creators": ["Test Creator"],
        "mainStars": ["Test Star"],
        "datePublished": "2020-01-01"
    }

    # Create movie
    response = client.post("/movies/create-movie", json=new_movie)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "RandomMovie"

    # Retrieve movie
    response_get = client.get("/movies")
    assert response_get.status_code == 200
    assert isinstance(response_get.json(), list)


# Integration test: filtering endpoint
def test_integration_filter_movies(monkeypatch):
    mock_movie = Movie(
        title="MockedMovie", movieIMDbRating=9.0, movieGenres=["Action"],
        directors=["Someone"], mainStars=["Actor"], creators=["C"], datePublished=datetime(2020, 1, 1)
    )
    with patch("backend.app.services.movieService.MovieService.get_filtered_movies", return_value=[mock_movie]):
        response = client.get("/movies/get-filtered-movies?title=MockedMovie")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "MockedMovie"


# Integration test: update endpoint
def test_integration_update_movie(monkeypatch):
    mock_movie = Movie(
    title="OldMovie",
    movieIMDbRating=7.0,
    totalRatingCount=150,
    totalUserReviews="120",
    totalCriticReviews="15",
    metaScore="85",
    movieGenres=["Action"],
    directors=["A Dir"],
    creators=["A Creator"],
    mainStars=["A Star"],
    datePublished=datetime(2020, 1, 1),
    description="Updated description",
    duration=300
)
    # Implementation expects full Movie object thus must mock full object not just an attribute
    with patch("backend.app.services.movieService.MovieService.update_movie", return_value=mock_movie):
        response = client.put("/movies/update-movie/OldMovie", json={
                                                                    "title": "OldMovie",
                                                                    "movieIMDbRating": 8.0,
                                                                    "totalRatingCount": 150,
                                                                    "totalUserReviews": "120",
                                                                    "totalCriticReviews": "15",
                                                                    "metaScore": "85",
                                                                    "movieGenres": ["Action"],
                                                                    "directors": ["A Dir"],
                                                                    "creators": ["A Creator"],
                                                                    "mainStars": ["A Star"],
                                                                    "datePublished": "2020-01-01",
                                                                    "description": "Updated description",
                                                                    "duration": 300
                                                                })
        assert response.status_code == 200
        assert "title" in response.json()


#Integration test: delete endpoint
def test_integration_delete_movie(monkeypatch):
    with patch("backend.app.services.movieService.MovieService.delete_movie", return_value=None) as mock_delete:
        response = client.delete("/movies/delete-movie/OldMovie")
        assert response.status_code == 204
        mock_delete.assert_called_once_with("OldMovie")
