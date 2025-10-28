from pathlib import Path
from backend.app.models.models import Review
from backend.app.repositories.reviewsRepo import save_review, load_reviews, update_review
from datetime import date
from typing import List,Dict,Any

rev = Review(
    movieTitle="TestMovie1",
    user="testuser1",
    title="Goat Movie",
    body="abasdjkalsfjklsafjklsa",
    date=date.today(),
    usefulVotes=5,
    totalVotes=10,
    rating=9.0,
    reportCount=0
)

rev2 = Review(
    movieTitle="TestMovie1",
    user="testuser2",
    title="Goat Movie",
    body="abasdjkalsfjklsafjklsa",
    date=date.today(),
    usefulVotes=5,
    totalVotes=10,
    rating=9.0,
    reportCount=0
)



update_review(
    "TestMovie1", 
    "testuser2", 
    {"User's Rating out of 10": "5"}
)

# save_review("TestMovie1",rev)
# save_review("TestMovie1",rev2)


# update_review("TestMovie1", "testuser2", {"User's Rating out of 10": "5.0"})
# print(load_reviews("TestMovie1"))
