
import os
from typing import List

from backend.app.repositories import usersRepo

IMDB_ROOT = os.path.join("data", "imdb")


def _assert_movie_exists(movie_title: str) -> None:
    """
    Ensure that the given movieTitle exists under data/imdb/<MovieTitle>/movieReviews.csv.

    Raises:
        ValueError: if the movie cannot be found in the imdb folder structure.
    """
    # basic sanity
    if not movie_title or movie_title.strip() == "":
        raise ValueError("Movie title cannot be empty")

    folder = os.path.join(IMDB_ROOT, movie_title)
    csv_path = os.path.join(folder, "movieReviews.csv")

    if not os.path.exists(csv_path):
        raise ValueError("Movie not found in IMDb dataset")


class WatchlistService:
    """
    Service layer for user watchlists.
    """

    def get_watchlist(self, username: str) -> List[str]:
        return usersRepo.get_watchlist(username)

    def add_movie(self, username: str, movie_title: str) -> List[str]:
        """
        Add a movie to the user's watchlist.

        - Rejects empty titles.
        - Rejects movies that are not present in data/imdb/<MovieTitle>/movieReviews.csv.
        """
        _assert_movie_exists(movie_title)
        return usersRepo.add_to_watchlist(username, movie_title)

    def remove_movie(self, username: str, movie_title: str) -> List[str]:
        """
        Remove a movie from the user's watchlist.

        - Still enforces that the movie must be a valid IMDb movie,
          so users cannot add/remove arbitrary fake names.
        """
        _assert_movie_exists(movie_title)
        return usersRepo.remove_from_watchlist(username, movie_title)


watchlist_service = WatchlistService()