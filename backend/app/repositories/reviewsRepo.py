from pathlib import Path
import csv
from typing import List, Dict, Any
from ..models.models import Review
from ..repositories.moviesRepo import recompute_movie_ratings

DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "imdb"


CSV_HEADERS = [
    "Movie Title",
    "Date of Review",
    "User",
    "Usefulness Vote",
    "Total Votes",
    "User's Rating out of 10",
    "Review Title",
    "Review",
    "Reports"
]


def load_reviews(movieTitle: str, amount: int = 10) -> List[Dict[str, Any]]:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        return []

    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        reader = list(csv.DictReader(csvFile))
        reviews = []
        for r in reader[:amount]:
            r["Review"] = r["Review"].replace("\n", " ")  # replace newlines with space
            reviews.append(r)
        return reviews


def load_all_reviews(movieTitle: str) -> List[Dict[str, Any]]:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        return []

    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        rows = list(csv.DictReader(csvFile))
        for r in rows:
            if "Review" in r:
                r["Review"] = r["Review"].replace("\n", " ")  # remove newlines
        return rows


def find_review_by_user(movieTitle: str, username: str):
    rows = load_all_reviews(movieTitle)
    for r in rows:
        if r.get("User") == username:
            return r
    return None


def save_review(movieTitle: str, review: Review) -> None:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    
    # Map Review object to CSV fields
    data = {
        "Movie Title": review.movieTitle,
        "Date of Review": review.date,
        "User": review.user,
        "Usefulness Vote": review.usefulVotes or 0,
        "Total Votes": review.totalVotes or 0,
        "User's Rating out of 10": review.rating or 0,
        "Review Title": review.title,
        "Review": review.body,
        "Reports": review.reportCount
    }

    if moviePath.exists():
        with moviePath.open("a", newline="", encoding="utf-8") as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=data.keys())
            writer.writerow(data)
        # After adding a review, recompute movie aggregates
        try:
            recompute_movie_ratings(movieTitle)
        except Exception:
            pass
    else:
        print(f"Review file for {movieTitle} not found.")



def update_review(movieTitle: str, username: str, updateFields: Dict[str, Any]) -> None:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    rows = load_all_reviews(movieTitle)

    updated = False

    for row in rows:
        if row["Movie Title"] == movieTitle and row["User"] == username:
            for key, value in updateFields.items():
                if key in row:
                    row[key] = value
            updated = True
            break

    if not updated:
        print("Unable to update (review not found)")
        return

    with moviePath.open("w", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    # Recompute aggregates after updating a review
    try:
        recompute_movie_ratings(movieTitle)
    except Exception:
        pass


def delete_review(movieTitle: str, username: str) -> None:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    rows = load_all_reviews(movieTitle)

    new_rows = [
        r for r in rows
        if not (r["Movie Title"] == movieTitle and r["User"] == username)
    ]

    if len(new_rows) == len(rows):
        print("Unable to delete (review not found)")
        return

    with moviePath.open("w", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(new_rows)

    print("Deletion successful")
    try:
        recompute_movie_ratings(movieTitle)
    except Exception:
        pass

def upvote_review(movieTitle: str, username: str) -> None:
    """
    Increment the 'Usefulness Vote' and 'Total Votes' for a user's review.
    Recomputes movie stats if needed.
    """
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    rows = load_all_reviews(movieTitle)
    updated = False

    for row in rows:
        if row["User"] == username:
            row["Usefulness Vote"] = int(row.get("Usefulness Vote", 0)) + 1
            row["Total Votes"] = int(row.get("Total Votes", 0)) + 1
            updated = True
            break

    if not updated:
        print(f"Review by user '{username}' not found for movie '{movieTitle}'")
        return

    with moviePath.open("w", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    # Recompute aggregates for usefulness if you track that
    try:
        recompute_movie_ratings(movieTitle)
    except Exception:
        pass

