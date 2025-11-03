from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..models.models import Movie
from backend.app.repositories import moviesRepo

##There's probably much more efficient way to write these functions, but this is all I got.
## Also I wasn't able to figure out how to import the moviesRepo, so I couldn't check these codes if it actually works.
## Also you probably need the virtual environment on to test this.

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
    
    
    ##Returns the list of movies that have HIGHER IMDb rating than the specified amount.
    def filterIMDbRatingHigher(self,searchIMDbRatingMin) ->  List[Movie]:
        for movie in self.movies:
            if searchIMDbRatingMin <= movie.movieIMDbRating:
                self.matching_movies.append(movie)
        return self.matching_movies
    
     ##Returns the list of movies that have LOWER IMDb rating than the specified amount.
    def filterIMDbRatingLower(self,searchIMDbRatingMax) ->  List[Movie]:
        for movie in self.movies:
            if searchIMDbRatingMax >= movie.movieIMDbRating:
                self.matching_movies.append(movie)
        return self.matching_movies
    

    ##Returns the list of movies that have HIGHER total rating than the specified amount.
    def filterTotalRatingHigher(self,searchTotalRatingMin) ->  List[Movie]:
        for movie in self.movies:
            if searchTotalRatingMin <= movie.totalRatingCount:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    ##Retuns the list of movies that have LOWER total rating than the specified amount.
    def filterTotalRatingLower(self,searchTotalRatingMax) ->  List[Movie]:
        for movie in self.movies:
            if searchTotalRatingMax >= movie.totalRatingCount:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    
    ##Retuns the list of movies that have HIGHER user reviews than the specified amount.
    def filterUserReviewHigher(self,searchUserReviewMin) ->  List[Movie]:
        for movie in self.movies:
            if searchUserReviewMin <= self.convertInt(movie.totalUserReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    ##Returns the list of movies that have LOWER user reviews than the specified amount.
    def filterUserReviewLower(self,searchUserReviewMax) ->  List[Movie]:
        for movie in self.movies:
            if searchUserReviewMax >= self.convertInt(movie.totalUserReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    ##Returns the list of movies that have HIGHER critic reviews than the specified amount.
    def filterUserReviewHigher(self,searchCriticReviewMin) ->  List[Movie]:
        for movie in self.movies:
            if searchCriticReviewMin <= self.convertInt(movie.totalCriticReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    ##Returns the list of movies that have LOWER critic reviews than the specified amount.
    def filterUserReviewLower(self,searchCriticReviewMax) ->  List[Movie]:
        for movie in self.movies:
            if searchCriticReviewMax >= self.convertInt(movie.totalCriticReviews):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    ##Returns the list of movies that have HIGHER metascore than the specified amount.
    def filterMetaHigher(self,searchMetaMin) ->  List[Movie]:
        for movie in self.movies:
            if searchMetaMin <= self.convertInt(movie.metaScore):
                self.matching_movies.append(movie)
        return self.matching_movies
    
    ##Returns the list of movies that have LOWER metascore than the specified amount.
    def filterMetaLower(self,searchMetaMax) ->  List[Movie]:
        for movie in self.movies:
            if searchMetaMax >= self.convertInt(movie.metaScore):
                self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterGenres(self, searchGenres) ->  List[Movie]:
       
       ## searchGenres: list of genre strings to match.
       ## Returns a list of Movie objects where at least one genre matches.

        for movie in self.movies:
            for keyword in searchGenres:
                # Check if any keyword matches a genre (case-insensitive)
                if any(keyword.lower() == genre.lower() for genre in movie.movieGenres):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterDirector(self, searchDirectors) ->  List[Movie]:
       
       # searchDirectors: list of directors strings to match.
       # Returns a list of Movie objects where at least one director matches.

        for movie in self.movies:
            for keyword in searchDirectors:
                # Check if any keyword matches a director (case-insensitive)
                if any(keyword.lower() == director.lower() for director in movie.directors):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterDateAfter(self, searchDateMax) ->  List[Movie]:
        ##Filters movies published on or after the given date.
        ##start_date_str: string in "YYYY-MM-DD" format

        # Convert the input string to a date object
        start_date = datetime.strptime(searchDateMax, "%Y-%m-%d").date()

        for movie in self.movies:
        # Convert movie's datePublished string to date
            movie_date = datetime.strptime(movie.datePublished, "%Y-%m-%d")
            if movie_date >= start_date:
                self.matching_movies.append(movie)
        return self.matching_movies
    
    def filterDateBefore(self, searchDateMin) ->  List[Movie]:
        ##Filters movies published on or before the given date.
        ##start_date_str: string in "YYYY-MM-DD" format

        # Convert the input string to a date object
        end_date = datetime.strptime(searchDateMin, "%Y-%m-%d").date()

        for movie in self.movies:
        # Convert movie's datePublished string to date
            movie_date = datetime.strptime(movie.datePublished, "%Y-%m-%d").date()
            if movie_date >= end_date:
                self.matching_movies.append(movie)

        return self.matching_movies
    

    def filterCreators(self, searchCreators) ->  List[Movie]:
       
       ## searchCreators: list of Creators strings to match.
       ## Returns a list of Movie objects where at least one creators matches.

        for movie in self.movies:
            for keyword in searchCreators:
                # Check if any keyword matches a creator (case-insensitive)
                if any(keyword.lower() == creator.lower() for creator in movie.creators):
                    self.matching_movies.append(movie)
        return self.matching_movies
    

    def filterMains(self, searchMains) ->  List[Movie]:
       
       ## searchMains: list of mainStars strings to match.
       ## Returns a list of Movie objects where at least one mainStars matches.

        for movie in self.movies:
            for keyword in searchMains:
                # Check if any keyword matches a mainStar (case-insensitive)
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
    

    
    ##Converts String that has a form of "9.5K" or "1.2M" into int numbers.
    ##If the String just has a castable int number, it'll automatically do that as well.
    def convertInt(s):
        s = s.strip().upper()

        if s.endswith("K"):
            return int(float(s[:-1]) * 1000)
        elif s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        else:
            return int(float(s))


