import json,os, csv,shutil
from pathlib import Path
from typing import List, Dict, Any
from ..models.models import Movie
from pydantic import BaseModel



DATA_PATH = Path(__file__).resolve().parents[3] /"data"/"imdb"

def load_all_movies() ->  List[Movie]:
    movies = []
    for movie_folders in DATA_PATH.iterdir():
        if movie_folders.is_dir():
            collect_movies = movie_folders / "metadata.json" 
            try:
             with collect_movies.open("r", encoding="utf-8") as f:
                movie_info = json.load(f) #deserialize into movies as objects
                unpack_dict = Movie(**movie_info) #unpackage Dictionary, match movie Class
                movies.append(unpack_dict) #append so it doesnt override
            except FileNotFoundError:
                print("File not found")
                
    return movies

def load_movie_by_title(title: str) -> Movie:
    movie_path = DATA_PATH / title / "metadata.json"
    try:
        with movie_path.open("r", encoding="utf-8") as f:
            movie_info = json.load(f)
            unpack_dict = Movie(**movie_info)
            return unpack_dict
    except FileNotFoundError:
        print("Movie not found")
        return None


def save_movies(movie: Movie):
    try:
        movie_folder = DATA_PATH / movie.title
        movie_folder.mkdir()

        meta_path = movie_folder / "metadata.json"
        with meta_path.open("w", encoding = "utf-8") as m:
            #model_dump converts Pydantic model to JSON/Dict, write the JSON strong into 
            m.write(movie.model_dump_json(indent=2))
        
        csv_path = movie_folder / "movieReviews.csv"

        if not csv_path.exists():
            csv_path.write_text("Movie Title,Date of Review,User,Usefulness Vote,Total Votes,User's Rating out of 10,Review Title,Review,Reports\n",
            encoding="utf-8")

    except FileExistsError:
        print("Folder exists already")

def update_movies(movie_title: str, values : dict):
    update_path = DATA_PATH / movie_title / "metadata.json"
    def _make_serializable(obj): # Uses recursion to handle nested structures and convert non-serializable types
        if isinstance(obj, dict):
            return {k: _make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_make_serializable(v) for v in obj]
        try:
            from datetime import date, datetime as _dt
        except Exception:
            return obj
        if isinstance(obj, (_dt, date)):
            return obj.isoformat()
        return obj # Returns the object as is if no conversion is needed

    with update_path.open("r", encoding="utf-8") as f:
        movie_data = json.load(f)
    safe_values = _make_serializable(values)
    movie_data.update(safe_values)

    with update_path.open("w", encoding="utf-8") as f:
        json.dump(movie_data, f, indent=2, ensure_ascii=False)
    print(f"Updated {movie_title} successfully")



def delete_movies(movie_title : str):
    delete_path = DATA_PATH / movie_title
    if not delete_path.exists():
            raise ValueError(f"Movie with title '{movie_title}' does not exist")
    try:
        shutil.rmtree(delete_path)
        print(f"{movie_title} and its contents sucessfully deleted")
    except OSError as e:
        print(f"Error: {e}")



#Do not expose as endpoint, used for data migration only
def update_movie_csv(): 
    new_csv_header = [ 
        "Movie Title",
        "Date of Review",
        "User",
        "Usefulness Vote",
        "Total Votes",
        "User's Rating out of 10",
        "Review Title",
        "Review",
        "Reports"]

    for movies in DATA_PATH.iterdir():
        movie_title = movies.name #pathlib
        csv_path = DATA_PATH /movie_title/ "movieReviews.csv"

        with csv_path.open("r", encoding= "utf-8", newline = "") as r:
            reader = csv.DictReader(r)
            rows = list(reader) #list of dict

        with csv_path.open("w", encoding = "utf-8", newline = "") as w:
            writer = csv.DictWriter(w, fieldnames=new_csv_header)
            writer.writeheader()

            for dicts in rows:
                updated_rows = {
                    "Movie Title": movie_title,
                    "Date of Review": dicts.get("Date of Review", "Date not found"), 
                    "User": dicts.get("User", "User not found"),
                    "Usefulness Vote": dicts.get("Usefulness Vote", "Usefulness Vote not found"),
                    "Total Votes": dicts.get("Total Votes", "Total votes not found"),
                    "User's Rating out of 10": dicts.get("User's Rating out of 10", "Rating not found"),
                    "Review Title": dicts.get("Review Title", "Review Title not found"),
                    "Review": dicts.get("Review", "Review body not found"),
                    "Reports": 0
                }
                writer.writerow(updated_rows)
        print(f"Updated {movie_title}")



            
        

