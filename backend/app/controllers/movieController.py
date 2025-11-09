from fastapi import APIRouter, HTTPException, Query
from typing import List
from ..models.models import Movie
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
