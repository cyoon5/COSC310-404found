from backend.app.repositories import moviesRepo
from backend.app.services.movieService import filterMovie

def main():
    # Load all movies from /data/imdb
    movies = moviesRepo.load_all_movies()
    print(f"✅ Loaded {len(movies)} movies from repository.\n")

    # Initialize the filter with the loaded movies
    fm = filterMovie(movies)

    # Test 1: Filter by title
    print("containing 'Jo':") #ERROR, SEEMS TO SAVE 7.4 OR SOMETHING John Wick for some reason
    for m in fm.filterTitle("Jo"):
        print("  ", m.title)

    # Test 2: Filter IMDb rating higher than 8
    print("\n⭐ IMDb rating >= 8.0:")
    for m in fm.filterIMDbRatingHigher(8.0):
        print("  ", m.title, m.movieIMDbRating)

    # Test 3: Filter by genre
    print("\n🎬 Movies with genre 'Action':")
    for m in fm.filterGenres(["Action"]):
        print("  ", m.title, m.movieGenres)

    # Test 4: Filter by release date after 2015
    print("\n📅 Movies released after 2015-01-01:")
    for m in fm.filterDateAfter("2015-01-01"):
        print("  ", m.title, m.datePublished)

if __name__ == "__main__":
    main()
