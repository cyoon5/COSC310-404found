from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..models.models import Movie
from ..repositories.moviesRepo import load_all_movies



class MovieService:
    
    def __init__(self):
        pass

    def filter_title(self, title: str) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            if title.lower() in movies.title.lower():
                filtered_movies.append(movies)
        return filtered_movies
    
    def filter_rating_min(self, min_rating: float) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            if movies.movieIMDbRating >= min_rating:
                filtered_movies.append(movies)
        return filtered_movies
    
        
    def filter_rating_max(self, max_rating: float) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            if movies.movieIMDbRating <= max_rating:
                filtered_movies.append(movies)
        return filtered_movies
    
    


