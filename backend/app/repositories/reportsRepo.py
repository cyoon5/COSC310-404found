from pathlib import Path
import json, os
from typing import List, Dict, Any
from ..models.models import Report
from ..repositories.reviewsRepo import load_all_reviews


DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "imdb"


def load_all_reports() -> List[Dict[str, Any]]:
    all_reviews = []
    reported_reviews = []
    for movies in DATA_PATH.iterdir():
        all_reviews.extend(load_all_reviews(movies.name))
    for review in all_reviews:
        report = int(review.get("Reports", ""))
        if(report > 0):
            reported_reviews.append(review)
    
    return reported_reviews





