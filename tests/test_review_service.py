import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.services.reviewService import ReviewService
from backend.app.main import app
from backend.app.models.models import Review
from datetime import date
from backend.app.dependencies import get_current_user
from backend.app.repositories.moviesRepo import recompute_movie_ratings





# UNIT TESTS

# Test getting reviews successfully
def test_get_reviews():
    fake_reviews = [
        {"title": "Great!", "rating": 9},
        {"title": "Not bad", "rating": 7}
    ]

    with patch("backend.app.services.reviewService.load_reviews", return_value=fake_reviews):
        service = ReviewService()
        result = service.get_reviews("Random", count=10)

        assert result == fake_reviews
        assert len(result) == 2

# Test exception during review loading
def test_get_reviews_exception():
    with patch("backend.app.services.reviewService.load_reviews", side_effect=FileNotFoundError):
        service = ReviewService()

        with pytest.raises(FileNotFoundError):
            service.get_reviews("NonexistentMovie")


# Test creating a valid review
def test_create_review_success():
    review = Review(
        user="tester",
        rating=8,
        title="Good movie",
        body="Really enjoyed it",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),           
        movieTitle="TestMovie"
    )

    with patch("backend.app.services.reviewService.load_movie_by_title", return_value={"title": "TestMovie"}), \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=None), \
         patch("backend.app.services.reviewService.save_review") as mock_save:

        service = ReviewService()
        service.create_review("TestMovie", review)

        mock_save.assert_called_once()
        saved_movie, saved_review = mock_save.call_args[0]
        assert saved_movie == "TestMovie"
        assert saved_review.user == "tester"
        assert saved_review.title == "Good movie"
        assert saved_review.rating == 8
        assert saved_review.movieTitle == "TestMovie"
        assert saved_review.date is not None  # date was set internally

# Test creating a review with duplicate user
def test_create_review_duplicate_user():
    # Arrange: a review that already exists
    existing_review = Review(
        user="tester",
        rating=8,
        title="Good movie",
        body="Really enjoyed it",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),
        movieTitle="TestMovie"
    )

    # New review with the same user for the same movie
    new_review = Review(
        user="tester",
        rating=9,
        title="Great movie",
        body="Loved it",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),
        movieTitle="TestMovie"
    )

    # Act & Assert: patch dependencies
    with patch("backend.app.services.reviewService.load_movie_by_title", return_value={"title": "TestMovie"}), \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=existing_review), \
         patch("backend.app.services.reviewService.save_review"):

        service = ReviewService()

        # Expect ValueError for duplicate user
        with pytest.raises(ValueError, match="has already reviewed this movie"):
            service.create_review("TestMovie", new_review)


# Test creating a review with invalid rating
def test_create_review_invalid_rating():
    # Arrange: review with invalid rating (e.g., 15)
    review = Review(
        user="tester",
        rating=15,  # Invalid rating
        title="Bad movie",
        body="Did not like it",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),
        movieTitle="TestMovie"
    )

    # Act & Assert: patch dependencies
    with patch("backend.app.services.reviewService.load_movie_by_title", return_value={"title": "TestMovie"}), \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=None), \
         patch("backend.app.services.reviewService.save_review"):

        service = ReviewService()

        # Expect ValueError for invalid rating
        with pytest.raises(ValueError, match="Rating must be between 1 and 10"):
            service.create_review("TestMovie", review)


#mock unit test for updating a review successfully
def test_update_review_success():
    existing_review = Review(
        user="tester",
        rating=6,
        title="Okay movie",
        body="It was fine",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),           
        movieTitle="TestMovie"
    )

    updated_data = {
        "rating": 9,
        "title": "Great movie",
        "body": "Really enjoyed it"
    }

    expected_csv_updates = {
        "User's Rating out of 10": 9,
        "Review Title": "Great movie",
        "Review": "Really enjoyed it"
    }

    with patch("backend.app.services.reviewService.find_review_by_user", return_value=existing_review), \
         patch("backend.app.services.reviewService.update_review") as mock_update:
        service = ReviewService()
        service.modify_review(
            "TestMovie",
            "tester",
            updated_data,
            current_user={"username": "tester", "role": "user"}
        )
        mock_update.assert_called_once_with("TestMovie", "tester", expected_csv_updates)


def test_update_review_not_found():
    with patch("backend.app.services.reviewService.find_review_by_user", return_value=None):
        service = ReviewService()
        with pytest.raises(ValueError, match="Review by user 'nonexistent' for movie 'TestMovie' not found."):
            service.modify_review(
                "TestMovie",
                "nonexistent",
                {"rating": 7},
                current_user={"username": "nonexistent", "role": "user"}
            )

def test_delete_review_success():
    # Arrange: existing review to delete
    existing_review = Review(
        user="tester",
        rating=8,
        title="Good movie",
        body="Really enjoyed it",
        usefulVotes=0,
        totalVotes=0,
        reportCount=0,
        date=date.today(),
        movieTitle="TestMovie"
    )

    # Act & Assert: patch dependencies
    with patch("backend.app.services.reviewService.load_movie_by_title", return_value={"title": "TestMovie"}), \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=existing_review), \
         patch("backend.app.services.reviewService.delete_review") as mock_delete:

        service = ReviewService()
        service.remove_review(
            "TestMovie",
            "tester",
            current_user={"username": "tester", "role": "user"}
        )

        # Ensure delete_review was called correctly
        mock_delete.assert_called_once_with("TestMovie", "tester")

def test_delete_review_not_found():
    # Act & Assert: patch dependencies
    with patch("backend.app.services.reviewService.load_movie_by_title", return_value={"title": "TestMovie"}), \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=None), \
         patch("backend.app.services.reviewService.delete_review"):

        service = ReviewService()

        # Expect ValueError because review does not exist
        with pytest.raises(ValueError, match="Review by user 'nonexistent' for movie 'TestMovie' not found."):
            service.remove_review(
                "TestMovie",
                "nonexistent",
                current_user={"username": "nonexistent", "role": "user"}
            )

def test_rating_recalculation():
    # Recompute ratings for TestMovie1
    recompute_movie_ratings("TestMovie1")

    # Load the movie metadata to verify
    from backend.app.repositories.moviesRepo import load_movie_by_title
    movie = load_movie_by_title("TestMovie1")

    assert movie is not None
    assert movie.movieIMDbRating == 3.0  # (5.0 + 1.0) / 2 = 3.0
    assert movie.totalRatingCount == 2
    assert movie.totalUserReviews == 2






# INTEGRATION TESTS

client = TestClient(app)

# Integration test for getting reviews for a movie
def test_get_reviews_endpoint_success():
    fake_reviews = [
        {"title": "Amazing movie", "rating": 9},
        {"title": "Pretty good", "rating": 8},
    ]

    # Patch the service method used inside the endpoint
    with patch("backend.app.controllers.reviewController.review_service.get_reviews", return_value=fake_reviews):
        response = client.get("/reviews/Random?amount=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data == fake_reviews






def test_create_review_endpoint_success():
    review_payload = {
        "user": "testuser",
        "rating": 8,
        "title": "Good movie",
        "body": "Enjoyed it",
        "usefulVotes": 0,
        "totalVotes": 0,
        "reportCount": 0,
        "date": str(date.today()),           
        "movieTitle": "TestMovie"       
    }

    # We do this because get_current_user normally looks up the user in the repo (JSON files)
    # Something to do with dependency injection in FastAPI
    client.app.dependency_overrides[get_current_user] = lambda: {"username": "testuser", "role": "user"}
    try:
        with patch("backend.app.controllers.reviewController.review_service.create_review") as mock_create:
            response = client.post("/reviews/TestMovie", json=review_payload)
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Review created successfully"
            mock_create.assert_called_once()
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_update_review_endpoint_success():
    update_payload = {
        "rating": 9,
        "title": "Great movie",
        "body": "Really enjoyed it"
    }

    client.app.dependency_overrides[get_current_user] = lambda: {"username": "testuser", "role": "user"}
    try:
        with patch("backend.app.controllers.reviewController.review_service.modify_review") as mock_modify:
            response = client.put("/reviews/TestMovie/testuser", json=update_payload)
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Review updated successfully"
            mock_modify.assert_called_once_with(
                "TestMovie",
                "testuser",
                update_payload,
                {"username": "testuser", "role": "user"}
            )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)
    
def test_delete_review_endpoint_success():
    client.app.dependency_overrides[get_current_user] = lambda: {"username": "testuser", "role": "user"}
    try:
        with patch("backend.app.controllers.reviewController.review_service.remove_review") as mock_remove:
            response = client.delete("/reviews/TestMovie/testuser")
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "Review deleted successfully"
            mock_remove.assert_called_once_with(
                "TestMovie",
                "testuser",
                {"username": "testuser", "role": "user"}
            )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)





     

