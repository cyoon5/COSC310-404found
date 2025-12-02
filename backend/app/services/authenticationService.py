from passlib.hash import bcrypt
from typing import Dict, Any

from pathlib import Path
import json, csv

from ..repositories.usersRepo import load_users, save_users, add_user
from ..repositories.usersRepo import load_users, add_user, update_user

from ..repositories.usersRepo import load_users, add_user, update_user
from ..repositories.adminRepo import load_admins
from ..repositories.reviewsRepo import DATA_PATH as REVIEWS_DATA_PATH

# Project/data paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
BANS_JSON = DATA_DIR / "bans.json"
REPORTS_JSON = DATA_DIR / "reports.json"
#!!! ADMINS WILL BE MADE MANUALLY, NO REGISTRATION FOR ADMINS THUS NO ENDPOINT !!!
class AuthService:
    """Service for handling authentication and role-based access."""

    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        Checks that the username doesn't exist in either users or admins.
        Stores password as a hashed string.
        """
        users = load_users()
        admins = load_admins()

        # Check if username exists in users or admins, ensure that it is unique
        if any(u['userName'] == username for u in users) or any(a['adminName'] == username for a in admins):
            raise ValueError("Username already exists")

        hashed_pw = bcrypt.hash(password[:72])

        new_user = {
            "userName": username,
            "passwordHash": hashed_pw,
            "role": "user",
            "bio": None,
            "penalties": 0,
            "watchlist": []
        }

        # Save to users repo, persist to file(users.json)
        add_user(new_user)
        return new_user

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login a user or admin.
        Returns a dict with role and username on success.
        Raises ValueError on failure.
        """
        users = load_users()
        admins = load_admins()

        # Check users
        for user in users:
            if user['userName'] == username:
                if bcrypt.verify(password[:72], user['passwordHash']):
                    return {"username": username, "role": "user"}
                else:
                    raise ValueError("Incorrect password")

        # Check admins
        for admin in admins:
            if admin['adminName'] == username:
                if bcrypt.verify(password[:72], admin['passwordHash']):
                    return {"username": username, "role": "admin"}
                else:
                    raise ValueError("Incorrect password")

        raise ValueError("Username not found")
    

    def change_username_everywhere(self, current_username: str, new_username: str) -> None:
        """
        Rename a user across:
        - users.json (userName field)
        - bans.json (userName, reportedBy, reviewUser)
        - reports.json (review.user, reportedBy)
        - all review CSVs under data/imdb (User column)
        """

        if not new_username:
            raise ValueError("New username cannot be empty")

        if current_username == new_username:
            raise ValueError("New username must be different from current username")

        # 1) users.json
        users = load_users()
        found = False
        for u in users:
            if u.get("userName") == current_username:
                u["userName"] = new_username
                found = True

        if not found:
            raise ValueError("User not found")

        save_users(users)

        # 2) bans.json
        if BANS_JSON.exists():
            with BANS_JSON.open("r", encoding="utf-8") as f:
                bans = json.load(f)

            bans_changed = False
            for b in bans:
                # userName (who is banned)
                if b.get("userName") == current_username:
                    b["userName"] = new_username
                    bans_changed = True
                # reportedBy (who reported)
                if b.get("reportedBy") == current_username:
                    b["reportedBy"] = new_username
                    bans_changed = True
                # reviewUser (author of review that was banned)
                if b.get("reviewUser") == current_username:
                    b["reviewUser"] = new_username
                    bans_changed = True

            if bans_changed:
                tmp = BANS_JSON.with_suffix(".tmp")
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(bans, f, ensure_ascii=False, indent=2)
                tmp.replace(BANS_JSON)

        # 3) reports.json
        if REPORTS_JSON.exists():
            with REPORTS_JSON.open("r", encoding="utf-8") as f:
                reports = json.load(f)

            reports_changed = False
            for r in reports:
                # reportedBy (if present)
                if r.get("reportedBy") == current_username:
                    r["reportedBy"] = new_username
                    reports_changed = True

                review = r.get("review") or {}
                # review.user (author of the review)
                if review.get("user") == current_username:
                    review["user"] = new_username
                    reports_changed = True

            if reports_changed:
                tmp = REPORTS_JSON.with_suffix(".tmp")
                with tmp.open("w", encoding="utf-8") as f:
                    json.dump(reports, f, ensure_ascii=False, indent=2)
                tmp.replace(REPORTS_JSON)

        # 4) All movie review CSVs (data/imdb/*.csv)
        if REVIEWS_DATA_PATH.exists():
            for csv_path in REVIEWS_DATA_PATH.glob("*.csv"):
                with csv_path.open("r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    fieldnames = reader.fieldnames or []

                rows_changed = False
                for row in rows:
                    if row.get("User") == current_username:
                        row["User"] = new_username
                        rows_changed = True

                if rows_changed:
                    with csv_path.open("w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)

    def update_bio(self, username: str, bio: str) -> Dict[str, Any]:
        """
        Update the bio field for an existing user in users.json.
        """
        users = load_users()
        if not any(u["userName"] == username for u in users):
            raise ValueError("User not found")

        update_user(username, {"bio": bio})
        return {"username": username, "bio": bio}
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change the password for an existing *user* (not admin).
        Verifies the old password, then updates users.json with a new bcrypt hash.
        """
        users = load_users()

        # Find the user
        for user in users:
            if user.get("userName") == username:
                # Verify current (old) password
                if not bcrypt.verify(old_password[:72], user["passwordHash"]):
                    raise ValueError("Incorrect current password")

                # (Optional) prevent using same password again
                if bcrypt.verify(new_password[:72], user["passwordHash"]):
                    raise ValueError("New password must be different from the old password")

                # Hash and update
                new_hash = bcrypt.hash(new_password[:72])
                update_user(username, {"passwordHash": new_hash})

                return {"username": username, "message": "Password updated"}

        # If we didn't find the user
        raise ValueError("User not found")
