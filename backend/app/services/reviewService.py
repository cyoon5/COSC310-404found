from typing import List, Dict, Any
from fastapi import HTTPException
from datetime import date
import sys
from backend.app.repositories.moviesRepo import load_movie_by_title
from ..repositories.moviesRepo import recompute_movie_ratings
from ..repositories.reviewsRepo import load_reviews, save_review, update_review, delete_review, find_review_by_user
from ..models.models import ReviewCreate
from ..models.models import Review




# Map backend field names
CSV_KEYS = {
    "rating": "User's Rating out of 10",
    "usefulVotes": "Usefulness Vote",
    "totalVotes": "Total Votes",
    "title": "Review Title",
    "body": "Review",
    "reportCount": "Reports"
}


class ReviewService:

    def get_reviews(self, movieTitle: str, count: int = 10):
        return load_reviews(movieTitle, count)

    def create_review(self, movieTitle: str, review: ReviewCreate, current_user: Dict[str, str]) -> None:


               
        movie = load_movie_by_title(movieTitle)
        if not movie:
            raise ValueError(f"Movie '{movieTitle}' does not exist.")

        if review.rating is None or not (1 <= review.rating <= 10):
            raise ValueError("Rating must be between 1 and 10")

        if not review.title.strip():
            raise ValueError("Review title cannot be empty")

        if not review.body.strip():
            raise ValueError("Review body cannot be empty")

        if find_review_by_user(movieTitle, current_user["username"]):
            raise ValueError(f"User '{current_user['username']}' has already reviewed this movie.")
        
       
        
        full_review = Review(
            movieTitle=movieTitle,
            user=current_user["username"],                # username from auth
            date = date.today(),
            rating=review.rating,
            title=review.title,
            body=review.body,
            usefulVotes=0,
            totalVotes=0,
            reportCount=0
)

        save_review(movieTitle, full_review)
        # Recompute movie aggregates after creating a review
        try:
            recompute_movie_ratings(movieTitle)
        except Exception:
            pass



    def modify_review( 
        self,
        movieTitle: str,
        username: str,
        updateFields: Dict[str, Any],
        current_user: Dict[str, str]
    ) -> None:
        """ Takes two username params, username and x-username to verify permissions"""
        # Must either be admin or the user who wrote the review
        if current_user["role"] != "admin" and current_user["username"] != username:
            raise HTTPException(status_code=403, detail="Not allowed to edit this review")
        
        review = find_review_by_user(movieTitle, username)
        if not review:
            raise ValueError(f"Review by user '{username}' for movie '{movieTitle}' not found.")

        # Validation (using backend field keys)
        if "rating" in updateFields:
            r = updateFields["rating"]
            if r is None or not (1 <= r <= 10):
                raise ValueError("Rating must be between 1 and 10")

        if "title" in updateFields and not updateFields["title"].strip():
            raise ValueError("Updated title cannot be empty")

        if "body" in updateFields and not updateFields["body"].strip():
            raise ValueError("Updated body cannot be empty")

        # Convert backend field names --> CSV keys
        csv_updates = {
            CSV_KEYS.get(k, k): v
            for k, v in updateFields.items()
        }

        update_review(movieTitle, username, csv_updates)
        # Recompute aggregates after updating a review
        try:
            recompute_movie_ratings(movieTitle)
        except Exception:
            pass

    def remove_review(
        self,
        movieTitle: str,
        username: str,
        current_user: Dict[str, str]
    ) -> None:
        """ Takes two username params, username and x-username to verify permissions"""

        movie = load_movie_by_title(movieTitle)
        if not movie:
            raise ValueError(f"Movie '{movieTitle}' does not exist.")

        #Must either be admin or the user who wrote the review
        review = find_review_by_user(movieTitle, username)
        if not review:
            raise ValueError(f"Review by user '{username}' for movie '{movieTitle}' not found.")

        if current_user["role"] != "admin" and current_user["username"] != username:
            raise HTTPException(status_code=403, detail="Not allowed to delete this review")

        delete_review(movieTitle, username)
        # Recompute aggregates after deleting a review
        try:
            recompute_movie_ratings(movieTitle)
        except Exception:
            pass
