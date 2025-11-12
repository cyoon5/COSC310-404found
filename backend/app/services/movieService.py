from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import re
from ..models.models import Movie
from ..repositories.moviesRepo import load_all_movies, save_movies



class MovieService:
    
    def __init__(self):
        pass

    def get_all_movies(self) -> List[Movie]:    
        return load_all_movies()

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
    
    def filter_by_start_date(self, start_date: datetime) -> List[Movie]:
        all_movies = load_all_movies()
        filtered_movies = []

        for movie in all_movies:
            movie_date = getattr(movie, "datePublished", None)
            if movie_date:
                # Convert to datetime if it's a date object
                if not isinstance(movie_date, datetime):
                    movie_date = datetime.combine(movie_date, datetime.min.time())
                if movie_date >= start_date:
                    filtered_movies.append(movie)

        return filtered_movies

        
    def sort_by_rating(self, descending: bool = False) -> List[Movie]:
        all_movies = load_all_movies()
        sorted_movies = sorted(all_movies, key=lambda m: m.movieIMDbRating if m.movieIMDbRating is not None else float('-inf'), reverse=descending)
        return sorted_movies

    
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
    

    def get_filtered_movies(
        self,
        title: str = None,
        genre: str = None,
        min_rating: float = None,
        max_rating: float = None,
        director: str = None,
        main_star: str = None,
        start_date: datetime = None,  # Only start date
        sort_by: str = None,  # Only "rating" or "release_date"
        descending: bool = False
    ) -> List[Movie]:
        """
        Returns movies filtered by multiple optional criteria and sorted.
        """
        movies = load_all_movies()

        #Apply filters if provided by user
        if title:
            movies = [m for m in movies if title.lower() in m.title.lower()]
        if genre:
            movies = [m for m in movies if genre.lower() in [g.lower() for g in m.movieGenres]]
        if min_rating is not None:
            movies = [m for m in movies if m.movieIMDbRating is not None and m.movieIMDbRating >= min_rating]
        if max_rating is not None:
            movies = [m for m in movies if m.movieIMDbRating is not None and m.movieIMDbRating <= max_rating]
        if director:
            movies = [m for m in movies if any(director.lower() in d.lower() for d in m.directors)]
        if main_star:
            movies = [m for m in movies if any(main_star.lower() in s.lower() for s in m.mainStars)]
        if start_date:
            filtered = []
            for m in movies:
                d = getattr(m, "datePublished", None)
                if d:
                    if not isinstance(d, datetime):
                        d = datetime.combine(d, datetime.min.time())
                    if d >= start_date:
                        filtered.append(m)
            movies = filtered

        # Apply sorting
        if sort_by == "rating":
            movies.sort(key=lambda m: m.movieIMDbRating or float('-inf'), reverse=descending)
        elif sort_by == "release_date":
            def _movie_date_key(movie: Movie):
                d = getattr(movie, "datePublished", None)
                if not d:
                    return datetime.min
                if isinstance(d, str):
                    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                        try:
                            return datetime.strptime(d, fmt)
                        except Exception:
                            continue
                    try:
                        return datetime.fromisoformat(d)
                    except Exception:
                        return datetime.min
                if isinstance(d, datetime):
                    return d
                return datetime.combine(d, datetime.min.time())
            movies.sort(key=_movie_date_key, reverse=descending)

        return movies
    

    



    #CRUD Operations

    def create_movie(self, movie: Movie) -> Movie:
        """
        Create a new movie after validating required fields are non-empty.
        Raises ValueError if validation fails or duplicate exists.
        """
        if not movie.title or not movie.title.strip():
            raise ValueError("Title cannot be empty")
        # Ensures directors, movieGenres, mainStars, creators must be present and non-empty
        if not movie.directors or len(movie.directors) == 0:
            raise ValueError("Directors list cannot be empty")
        if not movie.movieGenres or len(movie.movieGenres) == 0:
            raise ValueError("Genres list cannot be empty")
        if not movie.mainStars or len(movie.mainStars) == 0:
            raise ValueError("Main stars list cannot be empty")
        if not movie.creators or len(movie.creators) == 0:
            raise ValueError("Creators list cannot be empty")
        #datePublished has to be provided, cant be none
        if getattr(movie, "datePublished", None) is None:
            raise ValueError("datePublished cannot be empty")
        title_norm = movie.title.strip().lower()
        all_movies = load_all_movies()
        for m in all_movies:
            if m.title.strip().lower() == title_norm:
                raise ValueError(f"Movie with title '{movie.title}' already exists")
        movie.title = re.sub(r'[\\/:"*?<>|]+', "", movie.title).strip() #Ensure title is safe for filesystem
        try:
            save_movies(movie)
        except FileExistsError:
            raise ValueError(f"Movie folder already exists for '{movie.title}'")
        except Exception as e:
            raise RuntimeError(f"Failed to save movie: {e}")
        return movie
    




