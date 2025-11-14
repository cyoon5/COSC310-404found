from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from ..models.models import Movie
from datetime import datetime
from ..services.movieService import MovieService
from backend.app.dependencies import admin_required
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/movies", tags=["Movies"])

movie_service = MovieService()



#Filter and Sort Endpoints
@router.get("", response_model=List[Movie])
def get_movies():
    """
    Get all movies
    """
    try:
        all_movies = movie_service.get_all_movies()
        if not all_movies:
            raise HTTPException(status_code=404, detail="No movies found")
        return all_movies
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    
@router.get("/get-filtered-movies", response_model=List[Movie])
def get_filtered_movies(
    title: str = Query(None, description="Keyword to search in movie titles"),
    min_rating: float = Query(None, ge=0.0, le=10.0, description="Minimum IMDb rating"),
    max_rating: float = Query(None, ge=0.0, le=10.0, description="Maximum IMDb rating"),
    genre: str = Query(None, description="Genre to filter movies by"),
    director: str = Query(None, description="Director to filter movies by"),
    main_star: str = Query(None, description="Main star to filter movies by"),
    start_date: datetime = Query(None, description="Start date in YYYY-MM-DD format"),
    sort_by: str = Query(None, description="Sort by: rating or release_date"),
    descending: bool = Query(False, description="Sort in descending order")
):
    """
    Returns all movies filtered by the specified criteria and optionally sorted.
    Example: /movies/get-filtered-movies?title=avg&min_rating=7.0&genre=Action&sort_by=rating&descending=true
    """
    try:
        filtered_movies = movie_service.get_filtered_movies(
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

        if not filtered_movies:
            raise HTTPException(status_code=404, detail="No movies found matching the criteria")

        return filtered_movies

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    


    

#CRUD Endpoints

@router.post("/create-movie", response_model=Movie, status_code=201)
def create_movie(movie: Movie, user = Depends(admin_required)):
    """
    Create a new movie.
    Example: /movies/create-movie
    """
    try:
        created_movie = movie_service.create_movie(movie)
        return created_movie
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
                                                  

@router.put("/update-movie/{title}", response_model=Movie)
def update_movie(title: str, movie: Movie, user = Depends(admin_required)):
    """
    Update an existing movie by title.
    Example: /movies/update-movie/{title}
    """
    try:
        updated_movie = movie_service.update_movie(title, movie)
        return updated_movie
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete-movie/{title}", status_code=204)
def delete_movie(title: str, user = Depends(admin_required)):
    """
    Delete a movie by title.
    Example: /movies/delete-movie/{title}
    """
    try:
        movie_service.delete_movie(title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




#Allow users to download JSON movie data

@router.get("/export-json", response_class=JSONResponse)
def export_movies_json(
    title: str = Query(None, description="Keyword to search in movie titles"),
    min_rating: float = Query(None, ge=0.0, le=10.0, description="Minimum IMDb rating"),
    max_rating: float = Query(None, ge=0.0, le=10.0, description="Maximum IMDb rating"),
    genre: str = Query(None, description="Genre to filter movies by"),
    director: str = Query(None, description="Director to filter movies by"),
    main_star: str = Query(None, description="Main star to filter movies by"),
    start_date: datetime = Query(None, description="Start date in YYYY-MM-DD format"),
    sort_by: str = Query(None, description="Sort by: rating or release_date"),
    descending: bool = Query(False, description="Sort in descending order")
):
    """
    Download movies as a JSON file. Users can filter and sort movies before downloading.
    """
    # Call the service method with all query parameters
    data = movie_service.export_movies(
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
    return JSONResponse(content=data)


