from passlib.hash import bcrypt
import json
from pathlib import Path

# Path to your admins.json file
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "admins.json"

admin = {
    "adminName": "admin2",
    "passwordHash": bcrypt.hash("AdminPass123"[:72]),
    "role": "admin"
}

# Load existing admins
if DATA_PATH.exists():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        admins = json.load(f)
else:
    admins = []

admins.append(admin)

# Save back
with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(admins, f, ensure_ascii=False, indent=2)

print("Admin created successfully!")
