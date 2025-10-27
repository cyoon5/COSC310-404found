from pathlib import Path
import json, os, csv
from typing import List,Dict,Any
from ..models.models import Review

#__file__ holds pathname of module from where module was loaded, in this case reviewsRepo is held
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "imdb"




def load_reviews(movieTitle: str) -> List[Dict[str,any]]: 
    reviews = []
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if moviePath.exists():
            with moviePath.open('r', newline = '', encoding = 'utf-8') as csvFile:
                 reader = csv.DictReader(csvFile)
                 reviews = list(reader) #convert to list of dict
    else:
        print(f"Review file for {movieTitle} not found.")

    return reviews





def save_review(movieTitle : str, review : Review) -> None:
    data = [review.date, review.user, review.usefulVotes, review.totalVotes,review.rating, review.title, review.body]
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if moviePath.exists():
        with moviePath.open('a', newline = '', encoding='utf-8') as csvFile: #'a' is append so it dont override
            writer = csv.writer(csvFile)
            writer.writerow(data)
    else:
        print(f"Review file for {movieTitle} not found.")


