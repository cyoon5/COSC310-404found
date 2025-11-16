from pathlib import Path
import csv
from typing import List, Dict, Any
from ..models.models import Review

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
        return reader[:amount]


def load_all_reviews(movieTitle: str) -> List[Dict[str, Any]]:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        return []

    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        return list(csv.DictReader(csvFile))


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
