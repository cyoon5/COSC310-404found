from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..models.models import Movie
from backend.app.repositories.moviesRepo import load_all_movies


all_movies = load_all_movies()

def filter_title(title: str) -> List[Movie]:
    filter = []
    for movies in all_movies: 
        if title.lower() in movies.title.lower():
            filter.append(movies)
    return filter

def filter_imdb_higher():
    pass





class filterMovie:
    def __init__(self):
        self.movies = moviesRepo.load_all_movies()
        self.matching_movies = []
    
    def __init__(self,movieList):
        self.movies = movieList
        self.matching_movies = []
    

    def filterTitle(self,searchTitle) ->  List[Movie]:
        for movie in self.movies:
            if searchTitle.lower() in movie.title.lower():
                self.matching_movies.append(movie)
        return self.matching_movies
    
    
    def filterIMDbRatingHigher(self,searchIMDbRatingMin) ->  List[Movie]:
        for movie in self.movies:
            if searchIMDbRatingMin <= movie.movieIMDbRating:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterIMDbRatingLower(self,searchIMDbRatingMax) ->  List[Movie]:
        for movie in self.movies:
            if searchIMDbRatingMax >= movie.movieIMDbRating:
                self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterTotalRatingHigher(self,searchTotalRatingMin) ->  List[Movie]:
        for movie in self.movies:
            if searchTotalRatingMin <= movie.totalRatingCount:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterTotalRatingLower(self,searchTotalRatingMax) ->  List[Movie]:
        for movie in self.movies:
            if searchTotalRatingMax >= movie.totalRatingCount:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    
    def filterUserReviewHigher(self,searchUserReviewMin) ->  List[Movie]:
        for movie in self.movies:
            if searchUserReviewMin <= self.convertInt(movie.totalUserReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterUserReviewLower(self,searchUserReviewMax) ->  List[Movie]:
        for movie in self.movies:
            if searchUserReviewMax >= self.convertInt(movie.totalUserReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterUserReviewHigher(self,searchCriticReviewMin) ->  List[Movie]:
        for movie in self.movies:
            if searchCriticReviewMin <= self.convertInt(movie.totalCriticReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterUserReviewLower(self,searchCriticReviewMax) ->  List[Movie]:
        for movie in self.movies:
            if searchCriticReviewMax >= self.convertInt(movie.totalCriticReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterMetaHigher(self,searchMetaMin) ->  List[Movie]:
        for movie in self.movies:
            if searchMetaMin <= self.convertInt(movie.metaScore):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterMetaLower(self,searchMetaMax) ->  List[Movie]:
        for movie in self.movies:
            if searchMetaMax >= self.convertInt(movie.metaScore):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterGenres(self, searchGenres) ->  List[Movie]:
        for movie in self.movies:
            for keyword in searchGenres:
                if any(keyword.lower() == genre.lower() for genre in movie.movieGenres):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterDirector(self, searchDirectors) ->  List[Movie]:
        for movie in self.movies:
            for keyword in searchDirectors:
                if any(keyword.lower() == director.lower() for director in movie.directors):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterDateAfter(self, searchDateMax) ->  List[Movie]:
        start_date = datetime.strptime(searchDateMax, "%Y-%m-%d").date()

        for movie in self.movies:
            movie_date = datetime.strptime(movie.datePublished, "%Y-%m-%d")
            if movie_date >= start_date:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterDateBefore(self, searchDateMin) ->  List[Movie]:

        end_date = datetime.strptime(searchDateMin, "%Y-%m-%d").date()

        for movie in self.movies:
            movie_date = datetime.strptime(movie.datePublished, "%Y-%m-%d").date()
            if movie_date >= end_date:
                self.matching_movies.append(movie)

        return self.matching_movies
    

    def filterCreators(self, searchCreators) ->  List[Movie]:
        for movie in self.movies:
            for keyword in searchCreators:
                if any(keyword.lower() == creator.lower() for creator in movie.creators):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterMains(self, searchMains) ->  List[Movie]:
        for movie in self.movies:
            for keyword in searchMains:
                if any(keyword.lower() == mains.lower() for mains in movie.mainStars):
                    self.matching_movies.append(movie)
        return self.matching_movies
    
    
    def filterDurationHigher(self,searchDurationMin) ->  List[Movie]:
        for movie in self.movies:
            if searchDurationMin <= movie.duration:
                self.matching_movies.append(movie)
        
        return self.matching_movies
    
    def filterDurationLower(self,searchDurationMax) ->  List[Movie]:
        for movie in self.movies:
            if searchDurationMax >= movie.duration:
                self.matching_movies.append(movie)
        
        return self.matching_movies
    

    
    #Converts String that has a form of "9.5K" or "1.2M" into int numbers.
    #If the String just has a castable int number, it'll automatically do that as well.
    def convertInt(s):
        s = s.strip().upper()

        if s.endswith("K"):
            return int(float(s[:-1]) * 1000)
        elif s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        else:
            return int(float(s))


