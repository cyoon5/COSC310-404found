from pathlib import Path
import csv, json , os
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
    else:
        print(f"Review file for {movieTitle} not found.")



def update_review(movieTitle: str, username: str, updateFields: Dict[str, Any]) -> None:
    """
    Update a single review row in movieReviews.csv for this movie/user.

    - Maps logical fields from the API (rating, title, body) to the actual
      CSV column names:
        rating -> "User's Rating out of 10"
        title  -> "Review Title"
        body   -> "Review Body"
    - If a key in updateFields already matches a CSV column name, it is used directly.
    - Raises ValueError if the review is not found.
    """
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        raise ValueError(f"No reviews file found for movie '{movieTitle}'.")

    # Read existing rows
    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        reader = csv.DictReader(csvFile)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # Map API field names -> CSV column names
    column_map = {
        "rating": "User's Rating out of 10",
        "title": "Review Title",
        "body": "Review Body",
        # You can extend this if you ever allow updating other fields
        # "usefulVotes": "Usefulness Vote",
        # "totalVotes": "Total Votes",
    }

    updated = False

    for row in rows:
        if row.get("Movie Title") == movieTitle and row.get("User") == username:
            for key, value in updateFields.items():
                if value is None:
                    continue  # don't overwrite with None

                csv_key = column_map.get(key, key)  # fall back to raw key
                if csv_key in row:
                    # Store as string in CSV
                    row[csv_key] = str(value)
            updated = True
            break

    if not updated:
        raise ValueError(
            f"Review by user '{username}' for movie '{movieTitle}' not found."
        )

    # Write back all rows with the updated values
    with moviePath.open("w", newline="", encoding="utf-8") as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def delete_review(movieTitle: str, username: str) -> None:
    """
    Delete a single review row for this movie/user from movieReviews.csv.

    CSV header (TestMovie1/movieReviews.csv):
    Movie Title,Date of Review,User,Usefulness Vote,Total Votes,
    User's Rating out of 10,Review Title,Review Body,Reports
    """
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        raise ValueError(f"No reviews file found for movie '{movieTitle}'.")

    # Read all rows
    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        reader = csv.DictReader(csvFile)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    # Filter out the row for this user
    original_len = len(rows)
    remaining = [row for row in rows if row.get("User") != username]

    if len(remaining) == original_len:
        # Nothing was removed → the review didn't exist
        raise ValueError(
            f"Review by user '{username}' for movie '{movieTitle}' not found."
        )

    # Write back the filtered rows
    with moviePath.open("w", newline="", encoding="utf-8") as writeCsvFile:
        writer = csv.DictWriter(writeCsvFile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(remaining)

def recompute_movie_rating(movieTitle: str) -> None:
    """
    Recompute the movie's average rating and rating count from movieReviews.csv
    and update metadata.json for that movie.

    - movieIMDbRating: new average (0.0 if no valid ratings)
    - totalRatingCount: number of reviews with a valid numeric rating
    """
    movie_folder = DATA_PATH / movieTitle
    csv_path = movie_folder / "movieReviews.csv"
    meta_path = movie_folder / "metadata.json"

    if not csv_path.exists() or not meta_path.exists():
        # Nothing to do if either file is missing
        return

    ratings = []

    # Read all ratings from CSV
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            value = row.get("User's Rating out of 10")
            if value is None:
                continue
            try:
                r = float(value)
            except (TypeError, ValueError):
                continue
            ratings.append(r)

    if ratings:
        avg_rating = round(sum(ratings) / len(ratings), 1)
        count = len(ratings)
    else:
        avg_rating = 0.0
        count = 0

    # Update metadata.json
    try:
        with meta_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        metadata = {}

    metadata["movieIMDbRating"] = avg_rating
    metadata["totalRatingCount"] = count

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)