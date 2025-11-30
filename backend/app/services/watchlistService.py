from __future__ import annotations

import os
from typing import List
from pathlib import Path

from backend.app.repositories import usersRepo

# Resolve project root and absolute IMDB_ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .../COSC310-Project
IMDB_ROOT = os.getenv("IMDB_ROOT", str(PROJECT_ROOT / "data" / "imdb"))
WATCHLIST_ALLOW_UNKNOWN = os.getenv("WATCHLIST_ALLOW_UNKNOWN", "0") == "1"
MOVIE_REVIEWS_FILENAME = "movieReviews.csv"


def _movie_reviews_path(movie_title: str) -> str:
    """
    Build the path for the movie's reviews CSV file with case-insensitive matching.
    """
    root = Path(IMDB_ROOT)
    candidate = root / movie_title / MOVIE_REVIEWS_FILENAME
    if candidate.exists():
        return str(candidate)
    # Case-insensitive directory match
    try:
        for d in root.iterdir():
            if d.is_dir() and d.name.lower() == movie_title.lower():
                csv = d / MOVIE_REVIEWS_FILENAME
                if csv.exists():
                    return str(csv)
    except FileNotFoundError:
        pass
    return str(candidate)


def _assert_movie_exists(movie_title: str) -> None:
    """
    Ensure that the given movieTitle exists under data/imdb/<MovieTitle>/movieReviews.csv.
    """
    movie_reviews_path = _movie_reviews_path(movie_title)
    if not os.path.exists(movie_reviews_path):
        if WATCHLIST_ALLOW_UNKNOWN:
            return  # allow bypassing in non-strict environments
        # IMPORTANT: keep this exact string for the tests
        raise ValueError("Movie not found in IMDb dataset")


class WatchlistService:
    """Service layer for user watchlists backed by usersRepo."""
    def get_watchlist(self, username: str) -> List[str]:
        """Return the current watchlist for the given user."""
        return usersRepo.get_watchlist(username)

    def add_movie(self, username: str, movie_title: str) -> List[str]:
        """
        Add a movie to the user's watchlist after verifying it exists
        in the IMDb dataset.
        """
        _assert_movie_exists(movie_title)
        return usersRepo.add_to_watchlist(username, movie_title)

    def remove_movie(self, username: str, movie_title: str) -> List[str]:
        """
        Remove a movie from the user's watchlist.
        Still validates that the movie exists in the IMDb dataset to
        avoid arbitrary/nonexistent titles being used.
        """
        _assert_movie_exists(movie_title)
        return usersRepo.remove_from_watchlist(username, movie_title)


watchlist_service = WatchlistService()