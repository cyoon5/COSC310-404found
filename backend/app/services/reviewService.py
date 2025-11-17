from typing import List, Dict, Any
from fastapi import HTTPException
from datetime import date
import sys
from backend.app.repositories.moviesRepo import load_movie_by_title


from ..models.models import Review
from ..repositories.reviewsRepo import (
    load_reviews,
    save_review,
    update_review,
    delete_review,
    find_review_by_user
)


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

    def create_review(self, movieTitle: str, review: Review) -> None:


               
        movie = load_movie_by_title(movieTitle)
        if not movie:
            raise ValueError(f"Movie '{movieTitle}' does not exist.")

        if not review.user or not review.user.strip():
            raise ValueError("User cannot be empty")

        if review.rating is None or not (1 <= review.rating <= 10):
            raise ValueError("Rating must be between 1 and 10")

        if not review.title.strip():
            raise ValueError("Review title cannot be empty")

        if not review.body.strip():
            raise ValueError("Review body cannot be empty")

        if find_review_by_user(movieTitle, review.user):
            raise ValueError(f"User '{review.user}' has already reviewed this movie.")
 
        
        # Just to make sure it works on both windows/mac/linux
        if sys.platform.startswith("win"):
            day_format = "%#d"
        else:
            day_format = "%-d"

        review.date = date.today().strftime(f"{day_format} %B %Y") #match formatting w/ kaggle
        review.movieTitle = movieTitle

        save_review(movieTitle, review)

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
