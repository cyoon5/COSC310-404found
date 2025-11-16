from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import date
from pydantic import BaseModel
from ..services.reviewService import ReviewService
from ..models.models import Review
from ..dependencies import get_current_user, ensure_not_banned

router = APIRouter(prefix="/reviews", tags=["Reviews"])
review_service = ReviewService()

# Request model for updating reviews
class ReviewUpdate(BaseModel):
    #Only these fields as user should not update fields like date, user, movieTitle
    rating: Optional[float] = None
    title: Optional[str] = None
    body: Optional[str] = None


@router.get("/{movieTitle}", response_model=List[Dict[str, Any]])
def get_reviews(movieTitle: str, amount: int = Query(10, ge=1, le=100)):
    """Get reviews for a specific movie, limited by amount."""
    reviews = review_service.get_reviews(movieTitle, amount)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this movie")
    return reviews

@router.post("/{movieTitle}")
def create_review(
    movieTitle: str,
    review: Review,
    current_user: dict = Depends(ensure_not_banned),
):
    """Create a new review for a specific movie."""
    try:
        review.user = current_user["username"]
        review_service.create_review(movieTitle, review)
        return {"message": "Review created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{movieTitle}/{username}")
def update_review(
    movieTitle: str,
    username: str,
    updateFields: ReviewUpdate,
    current_user: dict = Depends(ensure_not_banned),
):
    """Update a review for a specific movie by a specific user"""
    try:
        review_service.modify_review(
            movieTitle,
            username,
            updateFields.model_dump(exclude_unset=True),
            current_user,
        )
        return {"message": "Review updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{movieTitle}/{username}")
def delete_review(
    movieTitle: str,
    username: str,
    current_user: dict = Depends(ensure_not_banned),
):
    """Delete a review for a specific movie by a specific user."""
    try:
        review_service.remove_review(movieTitle, username, current_user)
        return {"message": "Review deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))