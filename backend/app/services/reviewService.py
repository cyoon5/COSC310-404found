from ..models.models import Review
from typing import List,Dict,Any
from ..repositories.reviewsRepo import load_reviews, save_review, update_review, delete_review


class ReviewService:
    def __init__(self):
        pass

    def get_reviews(self, movieTitle: str, count: int = 10):
        # Ensure count is positive
        if count < 1:
            count = 10
        return load_reviews(movieTitle, count)

    def create_review(self, movieTitle: str, review: Review) -> None:
        save_review(movieTitle, review)

    def modify_review(self, movieTitle: str, username: str, updateFields: Dict[str, Any]) -> None:
        update_review(movieTitle, username, updateFields)

    def remove_review(self, movieTitle: str, username: str) -> None:
        delete_review(movieTitle, username)
