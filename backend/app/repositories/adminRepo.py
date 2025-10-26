from pathlib import Path
import json, os
from typing import List, Dict, any
from ..models.models import Admin



DATA_PATH = Path(__file__).resolve().parents[3] /"data"/"admins.json"


def load_admins() -> List[Dict[str,any]]:
    if not DATA_PATH.exists():
      return []
    with DATA_PATH.open("r", encoding = "utf-8") as f:
       return json.load(f)


def save_admins(admins: List[Dict[str, any]]):
   tmp = DATA_PATH.with_suffix(".tmp")
   with tmp.open("w", encoding = "utf-8") as f:
      json.dump(admins, f, ensure_ascii=False, indent=2)
   os.replace(tmp, DATA_PATH)


def add_admin(new_admin: Dict[str, any]):
    admins = load_admins()  
    admins.append(new_admin)    
    save_admins(admins)        


   
