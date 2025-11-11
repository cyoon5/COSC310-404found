from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models.models import Movie
from datetime import datetime
from ..services.movieService import MovieService

#create a router instance for movie endpoints
router = APIRouter(prefix="/movies", tags=["Movies"])

#Instantiate the service class
movie_service = MovieService()

#Define the endpoint to filter movies by title
@router.get("/search", response_model=List[Movie])
def search_movies(title: str = Query(..., description="Keyword to search in movie titles")):
    """
    Search movies by title keyword (case-insensitive)
    """
    try:
        #Call the service layer to get filtered movies
        filtered_movies = movie_service.filter_title(title)

        #If no movies are found, return HTTP 404 ie not found
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found")

        #Return the list of filtered movies (FastAPI converts it to JSON automatically)
        return filtered_movies

    #Handle invalid input (empty keyword)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

    
@router.get("/filter-by-rating-min", response_model=List[Movie])
#... Signifies that the parameter is required by the user
def filter_by_rating(min_rating: float = Query(..., ge=0.0, le=10.0, description="Minimum IMDb rating")):
    """
    Returns all movies with a rating equal to or greater than the given value.
    Example: /movies/filter-by-rating?min_rating=8.0
    """
    try:
        filtered_movies = movie_service.filter_rating_min(min_rating)
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found above that rating")
        return filtered_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.get("/filter-by-rating-max", response_model=List[Movie])
def filter_by_rating(max_rating: float = Query(..., ge=0.0, le=10.0, description="Maximum IMDb rating")):
    """
    Returns all movies with a rating equal to or less than the given value.
    Example: /movies/filter-by-rating-max?max_rating=8.0
    """
    try:
        filtered_movies = movie_service.filter_rating_max(max_rating)
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found below that rating")
        return filtered_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/filter-by-genre", response_model=List[Movie])
def filter_by_genre(genre: str = Query(..., description="Genre to filter movies by")):
    """
    Returns all movies that belong to the specified genre.
    Example: /movies/filter-by-genre?genre=Action
    """
    try:
        filtered_movies = movie_service.filter_genre(genre)
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found for that genre")
        return filtered_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/filter-by-director", response_model=List[Movie])
def filter_by_director(director: str = Query(..., description="Director to filter movies by")):
    """
    Returns all movies directed by the specified director.
    Example: /movies/filter-by-director?director=Steven Spielberg
    """
    try:
        filtered_movies = movie_service.filter_director(director)
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found for that director")
        return filtered_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/filter-by-main-star", response_model=List[Movie])
def filter_by_main_star(main_star: str = Query(..., description="Main star to filter movies by")):
    """
    Returns all movies featuring the specified main star.
    Example: /movies/filter-by-main-star?main_star=Robert Downey Jr.
    """
    try:
        filtered_movies = movie_service.filter_main_stars(main_star)
        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found for that main star")
        return filtered_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/sort-by-release-date", response_model=List[Movie]) 
def sort_by_release_date(descending: bool = Query(False, description="Sort by release date in descending order")):
    """
    Returns all movies sorted by their release date.
    Example: /movies/sort-by-release-date?descending=true
    """
    try:
        sorted_movies = movie_service.sort_by_release_date(descending)
        if not sorted_movies:
            raise HTTPException(status_code=404, detail="No movies found")
        return sorted_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
                                                  
    
