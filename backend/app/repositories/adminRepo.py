from pathlib import Path
import json, os
from typing import List, Dict, Any
from ..models.models import Admin

# Path to admins.json
DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "admins.json"

def load_admins() -> List[Dict[str, Any]]:
    """
    Load all admins from admins.json. Returns empty list if file does not exist.
    """
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_admins(admins: List[Dict[str, Any]]):
    """
    Save the full list of admins to admins.json safely using a temporary file.
    """
    tmp = DATA_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(admins, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def add_admin(new_admin: Dict[str, Any]):
    """
    Add a new admin to admins.json.
    """
    admins = load_admins()
    admins.append(new_admin)
    save_admins(admins)

def find_admin_by_name(admin_name: str) -> Dict[str, Any] | None:
    """
    Return a single admin dict by name, or None if not found.
    """
    admins = load_admins()
    for admin in admins:
        if admin.get("adminName") == admin_name:
            return admin
    return None

def update_admin(admin_name: str, updated_fields: Dict[str, Any]):
    """
    Update an existing admin with new fields. Raises ValueError if not found.
    """
    admins = load_admins()
    for idx, admin in enumerate(admins):
        if admin.get("adminName") == admin_name:
            admins[idx].update(updated_fields)
            save_admins(admins)
            return
    raise ValueError(f"Admin '{admin_name}' not found")

def delete_admin(admin_name: str):
    """
    Delete an admin by name. Raises ValueError if not found.
    """
    admins = load_admins()
    for idx, admin in enumerate(admins):
        if admin.get("adminName") == admin_name:
            admins.pop(idx)
            save_admins(admins)
            return
    raise ValueError(f"Admin '{admin_name}' not found")
