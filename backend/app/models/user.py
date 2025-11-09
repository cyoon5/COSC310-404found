from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class User(BaseModel):
    userName: str
    password: str
    role: str ="user"
    penalties: int = 0
    watchlist: List[str] = []  # list of movie title