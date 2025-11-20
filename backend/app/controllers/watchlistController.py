# backend/app/controllers/watchlistController.py

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_current_user
from backend.app.services.watchlistService import watchlist_service

router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)


@router.get("")
def get_my_watchlist(current_user: dict = Depends(get_current_user)):
    """
    Return the current user's watchlist.
    """
    try:
        items = watchlist_service.get_watchlist(current_user["username"])
        return {"watchlist": items}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{movieTitle}")
def add_to_my_watchlist(
    movieTitle: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Add a movie to the current user's watchlist.
    """
    try:
        items = watchlist_service.add_movie(current_user["username"], movieTitle)
        return {"message": "Movie added to watchlist", "watchlist": items}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{movieTitle}")
def remove_from_my_watchlist(
    movieTitle: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Remove a movie from the current user's watchlist.
    Returns:
        A JSON object with a confirmation message and the updated watchlist.
    Raises:
        HTTPException(400): if the movie does not exist in the IMDb dataset.
    """
    try:
        items = watchlist_service.remove_movie(current_user["username"], movieTitle)
        return {"message": "Movie removed from watchlist", "watchlist": items}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))