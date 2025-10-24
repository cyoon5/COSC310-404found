import json,os
from pathlib import Path
from typing import List, Dict, Any
from app.models.models import Movie




DATA_PATH = Path(__file__).resolve().parents[3] /"data"

def load_movies() ->  List[Movie]:
    movies = []
    for movieFolders in DATA_PATH.iteradir():
        if movieFolders.is_dir():
            #collectMovies points to that folder and to the metadata for all movies
            collectMovies = movieFolders / "metadata.json" 
            with collectMovies.open("r", encoding="utf-8") as f:
                movie_info = json.load(f) #deserialize into movies as objects
                unpackDict = Movie(**movie_info) #unpackage Dictionary, match movie Class
                movies.append(unpackDict) #append so it doesnt override
    return movies


def save_movies(movie: Movie):
    pass #do later
            


    


             
