import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.services.reviewService import ReviewService
from backend.app.main import app
from backend.app.models.models import Review
from fastapi import HTTPException
from datetime import date



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

    with patch("backend.app.services.reviewService.save_review") as mock_save, \
         patch("backend.app.services.reviewService.find_review_by_user", return_value=None):
        service = ReviewService()
        service.create_review("TestMovie", review)
        mock_save.assert_called_once_with("TestMovie", review)


