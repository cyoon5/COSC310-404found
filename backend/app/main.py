from fastapi import FastAPI
from .controllers.movieController import router as movie_router
from .controllers.authController import router as auth_router


app = FastAPI(title="Rotton Eggs Movie Review System")

#Mount the movies router
app.include_router(movie_router)

app.include_router(auth_router)
