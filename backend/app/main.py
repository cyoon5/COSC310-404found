from fastapi import FastAPI
from .controllers.movieController import router as movie_router
from .controllers.authController import router as auth_router
from .controllers.reviewController import router as review_router
from .controllers.moderationController import router as moderation_router
from app.controllers.watchlistController import router as watchlist_router

app = FastAPI(title="Rotten Eggs Movie Review System")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(movie_router)
app.include_router(auth_router)
app.include_router(review_router)
app.include_router(moderation_router)
app.include_router(watchlist_router) 