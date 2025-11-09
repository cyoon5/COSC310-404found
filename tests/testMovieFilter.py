from backend.app.repositories import moviesRepo
from backend.app.services.movieService import filter_title
from backend.app.models.models import Movie










result = filter_title("th")
for movies in result:
    print(movies.title)


# def test():
#     movies = moviesRepo.load_all_movies()
#     print(f" Loaded {len(movies)} movies from repository.\n")

#     fm = filterMovie(movies)



#     print("containing 'Jo':") #ERROR, SEEMS TO SAVE 7.4 OR SOMETHING John Wick for some reason
#     for m in fm.filterTitle("Jo"):
#         print("  ", m.title)

#     print("\n IMDb rating >= 8.0:")
#     for m in fm.filterIMDbRatingHigher(8.0):
#         print("  ", m.title, m.movieIMDbRating)

#     print("\n Movies with genre 'Action':")
#     for m in fm.filterGenres(["Action"]):
#         print("  ", m.title, m.movieGenres)

#     print("\n Movies released after 2015-01-01:")
#     for m in fm.filterDateAfter("2015-01-01"):
#         print("  ", m.title, m.datePublished)

