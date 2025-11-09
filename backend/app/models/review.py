from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Review(BaseModel):
    movieTitle: str
    user: str                          
    date: date                         
    rating: Optional[float] = None    #out of 10
    usefulVotes: Optional[int] = None 
    totalVotes: Optional[int] = None  
    title: str                        
    body: str                          
    reportCount: int = 0      