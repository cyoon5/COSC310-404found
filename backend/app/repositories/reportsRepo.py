from pathlib import Path
from typing import List, Dict, Any

from ..repositories.reviewsRepo import load_all_reviews

# Base path: project_root/data/imdb
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "imdb"


def load_all_reports() -> List[Dict[str, Any]]:
    """
    Scan all movie review CSVs and return only reviews that have been reported
    at least once.

    Semantics of the CSV "Reports" column after the moderation rework:
      - It stores the *number of times* a review has been reported.
      - Blank, missing, or non-numeric values are treated as 0.
      - Any review with Reports > 0 is considered "reported".

    Each returned review dict will have:
      - "Reports" normalised to an int
      - an extra "reportCount" key mirroring that integer
    """
    all_reviews: List[Dict[str, Any]] = []
    reported_reviews: List[Dict[str, Any]] = []

    # Collect reviews for every movie folder under data/imdb
    for movie_dir in DATA_PATH.iterdir():
        if not movie_dir.is_dir():
            continue
        all_reviews.extend(load_all_reviews(movie_dir.name))

    # Filter only those with Reports > 0, normalising the count
    for review in all_reviews:
        raw_reports = review.get("Reports", "")
        try:
            count = int(raw_reports)
        except (ValueError, TypeError):
            count = 0

        if count > 0:
            # Copy so we don't mutate the original reference unexpectedly
            normalised = dict(review)
            normalised["Reports"] = count
            normalised["reportCount"] = count
            reported_reviews.append(normalised)

    return reported_reviews