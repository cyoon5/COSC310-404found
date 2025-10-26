import json,os
from pathlib import Path
from typing import List, Dict, Any
from ..models.models import Movie
from pydantic import BaseModel



DATA_PATH = Path(__file__).resolve().parents[3] /"data"/"imdb"

def load_movies() ->  List[Movie]:
    movies = []
    for movieFolders in DATA_PATH.iterdir():
        if movieFolders.is_dir():
            #collectMovies points to that folder and to the metadata for all movies
            collectMovies = movieFolders / "metadata.json" 
            try:
             with collectMovies.open("r", encoding="utf-8") as f:
                movie_info = json.load(f) #deserialize into movies as objects
                unpackDict = Movie(**movie_info) #unpackage Dictionary, match movie Class
                movies.append(unpackDict) #append so it doesnt override
            except FileNotFoundError:
                print("File not found")
                
    return movies


def save_movies(movie: Movie):
    try:
        movieFolder = DATA_PATH / movie.title
        movieFolder.mkdir()

        metaPath = movieFolder / "metadata.json"
        with metaPath.open("w", encoding = "utf-8") as m:
            #model_dump converts Pydantic model to JSON/Dict, write the JSON strong into 
            m.write(movie.model_dump_json(indent=2))
        
        csvPath = movieFolder / "movieReviews.csv"

        if not csvPath.exists():
            csvPath.write_text("Date of Review,User,Usefulness Vote,Total Votes,User's Rating out of 10,Review Title,Review\n",
            encoding="utf-8")

    except FileExistsError:
        print("Folder exists already")


            


    


             
