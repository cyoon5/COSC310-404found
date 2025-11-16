from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, date
import re
from ..models.models import Movie
from ..repositories.moviesRepo import load_all_movies, save_movies, update_movies, delete_movies, load_movie_by_title


class MovieService:

    def __init__(self):
        pass

    def get_all_movies(self) -> List[Movie]:    
        return load_all_movies()

    def filter_title(self, movies: List[Movie], title: str) -> List[Movie]:
        filtered = []
        for m in movies:
            if title.lower() in m.title.lower():
                filtered.append(m)
        return filtered

    def filter_rating_min(self, movies: List[Movie], min_rating: float) -> List[Movie]:
        filtered = []
        for m in movies:
            if m.movieIMDbRating is not None and m.movieIMDbRating >= min_rating:
                filtered.append(m)
        return filtered

    def filter_rating_max(self, movies: List[Movie], max_rating: float) -> List[Movie]:
        filtered = []
        for m in movies:
            if m.movieIMDbRating is not None and m.movieIMDbRating <= max_rating:
                filtered.append(m)
        return filtered

    def filter_genre(self, movies: List[Movie], genre: str) -> List[Movie]:
        filtered = []
        for m in movies:
            for g in m.movieGenres:
                if genre.lower() == g.lower():
                    filtered.append(m)
                    break
        return filtered

    def filter_director(self, movies: List[Movie], director: str) -> List[Movie]:
        filtered = []
        for m in movies:
            for d in m.directors:
                if director.lower() in d.lower():
                    filtered.append(m)
                    break
        return filtered

    def filter_main_stars(self, movies: List[Movie], main_star: str) -> List[Movie]:
        filtered = []
        for m in movies:
            for s in m.mainStars:
                if main_star.lower() in s.lower():
                    filtered.append(m)
                    break
        return filtered

    def filter_by_start_date(self, movies: List[Movie], start_date: datetime) -> List[Movie]:
        filtered = []
        for m in movies:
            d = getattr(m, "datePublished", None)
            if d:
                if not isinstance(d, datetime):
                    d = datetime.combine(d, datetime.min.time())
                if d >= start_date:
                    filtered.append(m)
        return filtered

    #Provides a key function to extract datePublished for sorting if stored in different formats or missing
    def _movie_date_key(self, movie: Movie):
        d = getattr(movie, "datePublished", None)
        if not d:
            return datetime.min
        if isinstance(d, str):
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(d, fmt)
                except:
                    continue
            try:
                return datetime.fromisoformat(d)
            except:
                return datetime.min
        if isinstance(d, datetime):
            return d
        return datetime.combine(d, datetime.min.time())

    def sort_by_rating(self, movies: List[Movie], descending: bool = False) -> List[Movie]:
        return sorted(movies, key=lambda m: m.movieIMDbRating or float('-inf'), reverse=descending)

    def sort_by_release_date(self, movies: List[Movie], descending: bool = False) -> List[Movie]:
        return sorted(movies, key=self._movie_date_key, reverse=descending)



    #Uses the individual filters and sorting helpers to apply multiple filters and sorting in one call
    #Able to produce a query where multiple filters and sorting are applied together
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
        movies = load_all_movies()

        if title:
            movies = self.filter_title(movies, title)
        if genre:
            movies = self.filter_genre(movies, genre)
        if min_rating is not None:
            movies = self.filter_rating_min(movies, min_rating)
        if max_rating is not None:
            movies = self.filter_rating_max(movies, max_rating)
        if director:
            movies = self.filter_director(movies, director)
        if main_star:
            movies = self.filter_main_stars(movies, main_star)
        if start_date:
            movies = self.filter_by_start_date(movies, start_date)

        if sort_by == "rating":
            movies = self.sort_by_rating(movies, descending)
        elif sort_by == "release_date":
            movies = self.sort_by_release_date(movies, descending)

        return movies



    # CRUD Operations
    def create_movie(self, movie: Movie) -> Movie:
        """
        Create a new movie after validating required fields are non-empty.
        Raises ValueError if validation fails or duplicate exists.
        """
        # Ensure that required fields are non-empty otherwise raise error
        if not movie.title or not movie.title.strip():
            raise ValueError("Title cannot be empty")
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
    
    
    def update_movie(self, title: str, updated_values: Any) -> Movie:
        """Update an existing movie's metadata.
        `updated_values` may be a dict or a `Movie` instance; convert to a dict
        of provided (non-None) values before persisting.
        """
        existing_movie = load_movie_by_title(title)
        if not existing_movie:
            raise ValueError(f"Movie with title '{title}' does not exist")
        updated_data = existing_movie.model_dump()
        if isinstance(updated_values, Movie):
            values_dict = updated_values.model_dump(exclude_none=True)
        elif isinstance(updated_values, dict):
            values_dict = {k: v for k, v in updated_values.items() if v is not None}
        else:
            try:
                values_dict = {k: v for k, v in dict(updated_values).items() if v is not None}
            except Exception:
                raise ValueError("updated_values must be a dict or Movie instance")

        for key, value in values_dict.items():
            updated_data[key] = value
        updated_movie = Movie(**updated_data)
        update_movies(title, values_dict)
        return updated_movie



    def delete_movie(self, title: str) -> None:
        """Delete a movie and its files."""
        return delete_movies(title)


#Allow users to download JSON movie data customizable by them
 
    def export_movies(
        self,
        title: str = None,
        genre: str = None,
        min_rating: float = None,
        max_rating: float = None,
        director: str = None,
        main_star: str = None,
        start_date: datetime = None,
        sort_by: str = None,
        descending: bool = False
    ) -> list:
        """
        Returns a list of movies as dictionaries, filtered and sorted according
        to the specified criteria. Dates are converted to ISO format strings.
        """
        movies = self.get_filtered_movies(
            title=title,
            genre=genre,
            min_rating=min_rating,
            max_rating=max_rating,
            director=director,
            main_star=main_star,
            start_date=start_date,
            sort_by=sort_by,
            descending=descending
        )
        
        movie_dicts = []
        for m in movies:
            d = m.model_dump()
            if isinstance(d.get("datePublished"), (datetime, date)):
                d["datePublished"] = d["datePublished"].isoformat()
            movie_dicts.append(d)
        
        return movie_dicts






