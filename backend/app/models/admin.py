from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class Admin(BaseModel):
    adminName: str
    password: str
    role: str ="admin"