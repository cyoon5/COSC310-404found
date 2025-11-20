import os
from typing import List

from backend.app.repositories import usersRepo

IMDB_ROOT = os.path.join("data", "imdb")
MOVIE_REVIEWS_FILENAME = "movieReviews.csv"


def _assert_movie_exists(movie_title: str) -> None:
    """
    Ensure that the given movieTitle exists under data/imdb/<MovieTitle>/movieReviews.csv.

    Raises:
        ValueError: if the movie cannot be found in the IMDb folder structure.
    """
    movie_reviews_path = os.path.join(IMDB_ROOT, movie_title, MOVIE_REVIEWS_FILENAME)

    # IMPORTANT: use exists so the tests' mock works
    if not os.path.exists(movie_reviews_path):
        # IMPORTANT: keep this **exact** string for the tests
        raise ValueError("Movie not found in IMDb dataset")

class WatchlistService:
    def get_watchlist(self, username: str) -> List[str]:
        return usersRepo.get_watchlist(username)

    def add_movie(self, username: str, movie_title: str) -> List[str]:
        _assert_movie_exists(movie_title)
        return usersRepo.add_to_watchlist(username, movie_title)

    def remove_movie(self, username: str, movie_title: str) -> List[str]:
        _assert_movie_exists(movie_title)
        return usersRepo.remove_from_watchlist(username, movie_title)

watchlist_service = WatchlistService()