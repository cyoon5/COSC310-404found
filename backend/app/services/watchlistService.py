from __future__ import annotations

import os
from typing import List

from backend.app.repositories import usersRepo

IMDB_ROOT = os.path.join("data", "imdb")
MOVIE_REVIEWS_FILENAME = "movieReviews.csv"


def _movie_reviews_path(movie_title: str) -> str:
    """
    Build the expected path for the movie's reviews CSV file.
    Example:
        data/imdb/<movie_title>/movieReviews.csv
    """
    return os.path.join(IMDB_ROOT, movie_title, MOVIE_REVIEWS_FILENAME)


def _assert_movie_exists(movie_title: str) -> None:
    """
    Ensure that the given movieTitle exists under data/imdb/<MovieTitle>/movieReviews.csv.
    Raises:
        ValueError: if the movie cannot be found in the IMDb folder structure.
    """
    movie_reviews_path = _movie_reviews_path(movie_title)
    # IMPORTANT: use exists so the tests' mock works
    if not os.path.exists(movie_reviews_path):
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