from pathlib import Path
import json, os, csv
from typing import List,Dict,Any
from ..models.models import Review


#__file__ holds pathname of module from where module was loaded, in this case reviewsRepo is held
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "imdb"


# Planning to integrate with frontend in a way that reviews are loaded in batches of 10
def load_reviews(movieTitle: str, amount: int = 10) -> List[Dict[str, Any]]:
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if not moviePath.exists():
        return []

    with moviePath.open("r", newline="", encoding="utf-8") as csvFile:
        reader = list(csv.DictReader(csvFile))
        return reader[:amount]   # Return first N reviews



def save_review(movieTitle : str, review : Review) -> None:
    data = [review.movieTitle,review.date, review.user, review.usefulVotes, review.totalVotes,review.rating, review.title, review.body, review.reportCount]
    moviePath = DATA_PATH / movieTitle / "movieReviews.csv"
    if moviePath.exists():
        with moviePath.open('a', newline = '', encoding='utf-8') as csvFile: #'a' is append so it dont override
            writer = csv.writer(csvFile)
            writer.writerow(data)
    else:
        print(f"Review file for {movieTitle} not found.")

        

#Use movie title and username as PK to uniquely identify a row
def update_review(movieTitle : str, username : str, updateFields : Dict[str, Any]) -> None:
     checkUpdated = False
     updatePath = DATA_PATH / movieTitle / "movieReviews.csv"
     rows = load_all_reviews(movieTitle)
          
 

     for dicts in rows: #Basically rows contain every review and dicts contains individual review
        if dicts["Movie Title"] == movieTitle and dicts["User"] == username:
             for key, value in updateFields.items(): #returns dictioanry key and value pair as a tuple e.g Rating : 9.0
                  if key in dicts: #If the key listed in updateFIelds is in that dict then it updates it to a new value
                       dicts[key] = value #updates the value in dictionary to the new value
                       checkUpdated = True
             break 
             
     if checkUpdated:
          with updatePath.open("w", newline = '', encoding = 'utf-8') as csvFile:
               fields = rows[0].keys() 
               writer = csv.DictWriter(csvFile, fieldnames=fields)
               writer.writeheader()
               writer.writerows(rows)
     else:
          print("Unable to update")


def delete_review(movieTitle: str, username: str) -> None:
     keepRows = []
     deletePath = DATA_PATH / movieTitle / "movieReviews.csv"
     rows = load_all_reviews(movieTitle)

     for dicts in rows:
          if not (dicts["Movie Title"] == movieTitle and dicts["User"] == username):
               keepRows.append(dicts)  

     if(len(rows) == len(keepRows)):
          print("Unable to delete")
          return

     with deletePath.open("w", newline = '', encoding='utf-8')as writeCsvFile:
          fields = rows[0].keys()
          writer = csv.DictWriter(writeCsvFile, fieldnames=fields)
          writer.writeheader()
          writer.writerows(keepRows)
     print("Deletion successful")
  


          






