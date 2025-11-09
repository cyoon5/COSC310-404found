from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Report(BaseModel):
    review: Review  
    status: str = "pending"
    dateReported: date
    reason: Optional[str] = None 