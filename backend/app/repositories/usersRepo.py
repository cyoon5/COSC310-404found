from pathlib import Path
import json, os
from typing import List, Dict, Any
from ..models.models import User



DATA_PATH = Path(__file__).resolve().parents[3] /"data"/"users.json"


def load_users() -> List[Dict[str,any]]:
    if not DATA_PATH.exists():
      return []
    with DATA_PATH.open("r", encoding = "utf-8") as f:
       return json.load(f)


def save_users(users: List[Dict[str, any]]):
   tmp = DATA_PATH.with_suffix(".tmp")
   with tmp.open("w", encoding = "utf-8") as f:
      json.dump(users, f, ensure_ascii=False, indent=2)
   os.replace(tmp, DATA_PATH)


def add_user(new_user: Dict[str, any]): #To add a single user, not a list
    users = load_users()   #Gets current users
    users.append(new_user)     #Appends the new user to it
    save_users(users)          #Overides current user.json with additional user


   
