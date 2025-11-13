from pathlib import Path
import json, os
from typing import List, Dict, Any
from ..models.models import User

# Path to users.json
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "users.json"

def load_users() -> List[Dict[str, Any]]:
    """
    Load all users from users.json. 
    Returns an empty list if file does not exist.
    """
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users: List[Dict[str, Any]]):
    """
    Save the full list of users to users.json safely using a temporary file.
    """
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def add_user(new_user: Dict[str, Any]):
    """
    Add a new user to users.json.
    """
    users = load_users()
    users.append(new_user)
    save_users(users)

def find_user_by_username(username: str) -> Dict[str, Any] | None:
    """
    Return a single user dict by username, or None if not found.
    """
    users = load_users()
    for user in users:
        if user.get("userName") == username:
            return user
    return None

def update_user(username: str, updated_fields: Dict[str, Any]):
    """
    Update an existing user with new fields. Raises ValueError if not found.
    """
    users = load_users()
    for idx, user in enumerate(users):
        if user.get("userName") == username:
            users[idx].update(updated_fields)
            save_users(users)
            return
    raise ValueError(f"User '{username}' not found")

def delete_user(username: str):
    """
    Delete a user by username. Raises ValueError if not found.
    """
    users = load_users()
    for idx, user in enumerate(users):
        if user.get("userName") == username:
            users.pop(idx)
            save_users(users)
            return
    raise ValueError(f"User '{username}' not found")
