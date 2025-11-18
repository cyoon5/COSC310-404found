from datetime import date
from typing import Any, Dict, List, Optional

from ..models.models import Review
from ..repositories.moviesRepo import load_movie_by_title
from ..repositories.reviewsRepo import (
    load_reviews,
    save_review,
    update_review,
    delete_review,
    find_review_by_user,
    recompute_movie_rating,
)


class ReviewService:
    def get_reviews(self, movieTitle: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return reviews for a movie.

        Tests expect:
        - Signature: get_reviews(movieTitle, count=...)
        - No movie-exists check here.
        - If load_reviews raises (e.g., FileNotFoundError), we just let it bubble.
        """
        if count is None:
            return load_reviews(movieTitle)
        return load_reviews(movieTitle, count)

    def create_review(self, movieTitle: str, review: Review) -> None:
        """
        Create a new review.

        Rules (from tests + spec):
        - Movie must exist (use load_movie_by_title).
        - Rating must be between 1 and 10 (inclusive).
        - A user can only have one review per movie.
        - If date missing, default to today.
        - After saving, recompute aggregate rating from CSV.
        """
        movie = load_movie_by_title(movieTitle)
        if not movie:
            print("Movie not found")
            raise ValueError(f"Movie '{movieTitle}' does not exist.")

        # Rating validation that matches test expectations
        if review.rating is None or review.rating < 1 or review.rating > 10:
            raise ValueError("Rating must be between 1 and 10")

        # One review per (movie, user)
        existing = find_review_by_user(movieTitle, review.user)
        if existing:
            # Message just needs to contain this exact phrase for the test
            raise ValueError(f"User '{review.user}' has already reviewed this movie")

        # Default date
        if review.date is None:
            review.date = date.today()

        # Persist + recompute
        save_review(movieTitle, review)
        recompute_movie_rating(movieTitle)

    def modify_review(
        self,
        movieTitle: str,
        username: str,
        updateFields: Dict[str, Any],
        current_user: Dict[str, Any],
    ) -> None:
        """
        Update an existing review.

        Rules (from tests + spec):
        - Review must exist.
        - Only author or admin may edit.
        - If rating is present, it must be between 1 and 10.
        - Map logical fields (rating/title/body) to CSV columns and pass that
          dict into update_review.
        - After updating, recompute aggregate rating.
        """
        # Permission check
        if current_user.get("role") != "admin" and current_user.get("username") != username:
            raise PermissionError("Only the review author or an admin can edit this review.")

        # Look up existing review in CSV
        existing = find_review_by_user(movieTitle, username)
        if not existing:
            raise ValueError(
                f"Review by user '{username}' for movie '{movieTitle}' not found."
            )

        # Rating validation (if present)
        if "rating" in updateFields and updateFields["rating"] is not None:
            rating = updateFields["rating"]
            if rating < 1 or rating > 10:
                raise ValueError("Rating must be between 1 and 10")

        # Build the CSV field update dict the tests expect
        csv_updates: Dict[str, Any] = {}

        if "rating" in updateFields and updateFields["rating"] is not None:
            csv_updates["User's Rating out of 10"] = updateFields["rating"]

        if "title" in updateFields and updateFields["title"] is not None:
            csv_updates["Review Title"] = updateFields["title"]

        if "body" in updateFields and updateFields["body"] is not None:
            # CSV column for body is "Review"
            csv_updates["Review"] = updateFields["body"]

        # Pass through any raw CSV keys that might be in updateFields already
        for key, value in updateFields.items():
            if key in ("rating", "title", "body"):
                continue
            if value is not None:
                csv_updates[key] = value

        if not csv_updates:
            # Nothing to change
            return

        update_review(movieTitle, username, csv_updates)
        recompute_movie_rating(movieTitle)

    def remove_review(
        self,
        movieTitle: str,
        username: str,
        current_user: Dict[str, Any],
    ) -> None:
        """
        Delete a review (author or admin only), then recompute rating.
        """
        # Permission check
        if current_user.get("role") != "admin" and current_user.get("username") != username:
            raise PermissionError("Only the review author or an admin can delete this review.")

        # Check if review exists (so tests can patch this)
        existing = find_review_by_user(movieTitle, username)
        if not existing:
            raise ValueError(
                f"Review by user '{username}' for movie '{movieTitle}' not found."
            )
        # Perform delete + recompute
        delete_review(movieTitle, username)
        recompute_movie_rating(movieTitle)