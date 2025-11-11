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
    
    def filter_genre(self, genre: str) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            for items in movies.movieGenres:
                if genre.lower() == items.lower():
                    filtered_movies.append(movies)
        return filtered_movies

    def filter_director(self, director: str) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            for items in movies.directors:
                if director.lower() in items.lower():
                    filtered_movies.append(movies)
        return filtered_movies

    def filter_main_stars(self, main_star: str) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []
        for movies in all_movies: 
            for items in movies.mainStars:
                if main_star.lower() in items.lower():
                    filtered_movies.append(movies)
        return filtered_movies
    

    
    def sort_by_release_date(self, descending: bool = False) -> List[Movie]:
        all_movies = load_all_movies()

        def _movie_date_key(movie: Movie):
            # The model uses `datePublished` (Optional[date]) not `releaseDate`.
            d = getattr(movie, "datePublished", None)
            if d is None:
                # place unrated/undated movies at the beginning when ascending
                return datetime.min

            # If stored as a string, try parsing common formats
            if isinstance(d, str):
                for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(d, fmt)
                    except Exception:
                        continue
                try:
                    # as a last resort, try fromisoformat
                    return datetime.fromisoformat(d)
                except Exception:
                    return datetime.min

            # If already a datetime.date (but not datetime), convert to datetime
            if isinstance(d, datetime):
                return d
            try:
                return datetime.combine(d, datetime.min.time())
            except Exception:
                return datetime.min

        sorted_movies = sorted(all_movies, key=_movie_date_key, reverse=descending)
        return sorted_movies
    

    




