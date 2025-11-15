from ..services.reviewService import ReviewService
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any




router = APIRouter(prefix="/reviews", tags=["Reviews"])
review_service = ReviewService()



@router.get("/{movieTitle}", response_model=List[Dict[str, Any]])
def get_reviews(movieTitle: str, count: int = Query(10, ge=1)):
    """
    Returns the first count reviews for a movie.
    Example: count=10 = reviews 0-9, count=20 = reviews 0-19.
    Avoided doing load_all_reviews due to too many reviews causing performance issues.
    """
    try:
        reviews = review_service.get_reviews(movieTitle, count=count)
        if not reviews:
            raise HTTPException(status_code=404, detail="No reviews found for this movie")
        return reviews
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    

@router.post("/{movieTitle}")
def create_review(movieTitle: str, review: Dict[str,Any]):
    """
    Create a new review for a specific movie
    """
    try:
        review_service.create_review(movieTitle, review)
        return {"message": "Review created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/{movieTitle}/{username}")
def update_review(movieTitle: str, username: str, updateFields: Dict[str,Any]):
    """
    Update an existing review for a specific movie by a user
    """
    try:
        review_service.modify_review(movieTitle, username, updateFields)
        return {"message": "Review updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/{movieTitle}/{username}")
def delete_review(movieTitle: str, username: str):
    """
    Delete a review for a specific movie by a user
    """
    try:
        review_service.remove_review(movieTitle, username)
        return {"message": "Review deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))