from passlib.hash import bcrypt
from typing import Dict, Any
from pathlib import Path
import json
import csv

from ..repositories.usersRepo import load_users, save_users, add_user, update_user
from ..repositories.adminRepo import load_admins

# Project/data paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
BANS_JSON = DATA_DIR / "bans.json"
REPORTS_JSON = DATA_DIR / "reports.json"


# !!! ADMINS WILL BE MADE MANUALLY, NO REGISTRATION FOR ADMINS THUS NO ENDPOINT !!!
class AuthService:
    """Service for handling authentication and role-based access."""

    # ─────────────────────────────────────────
    # Registration / login
    # ─────────────────────────────────────────

    def register_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        Checks that the username does not exist in either users or admins.
        Stores password as a hashed string.
        """
        users = load_users()
        admins = load_admins()

        # Check if username exists in users or admins, ensure that it is unique
        if any(u.get("userName") == username for u in users) or any(
            a.get("adminName") == username for a in admins
        ):
            raise ValueError("Username already exists")

        hashed_pw = bcrypt.hash(password[:72])

        new_user: Dict[str, Any] = {
            "userName": username,
            "passwordHash": hashed_pw,
            "role": "user",
            # existing fields
            "penalties": 0,
            "watchlist": [],
            # new optional field
            "bio": None,
        }

        # Save to users repo, persist to file (users.json)
        add_user(new_user)
        return new_user

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login a user or admin by verifying credentials.
        Returns {"username": <name>, "role": "user"|"admin"} on success.
        """
        users = load_users()
        admins = load_admins()

        # Check users first
        for user in users:
            if user.get("userName") == username:
                if bcrypt.verify(password[:72], user["passwordHash"]):
                    return {"username": username, "role": "user"}
                else:
                    raise ValueError("Incorrect password")

        # Check admins
        for admin in admins:
            if admin.get("adminName") == username:
                if bcrypt.verify(password[:72], admin["passwordHash"]):
                    return {"username": username, "role": "admin"}
                else:
                    raise ValueError("Incorrect password")

        raise ValueError("Username not found")

    # ─────────────────────────────────────────
    # Password + bio updates
    # ─────────────────────────────────────────

    def change_password(
        self,
        username: str,
        old_password: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """
        Change the password for an existing user (not admin).

        - Verifies the old password.
        - Ensures the new password is different.
        - Persists a new bcrypt hash in users.json.
        """
        users = load_users()

        for user in users:
            if user.get("userName") == username:
                # Verify current (old) password
                if not bcrypt.verify(old_password[:72], user["passwordHash"]):
                    raise ValueError("Incorrect current password")

                # Optional: prevent using same password again
                if bcrypt.verify(new_password[:72], user["passwordHash"]):
                    raise ValueError(
                        "New password must be different from the old password"
                    )

                # Hash and update
                new_hash = bcrypt.hash(new_password[:72])
                update_user(username, {"passwordHash": new_hash})

                return {"username": username, "message": "Password updated"}

        # If we didn't find the user
        raise ValueError("User not found")

    def update_bio(self, username: str, bio: str) -> Dict[str, Any]:
        """
        Update the bio field for an existing user in users.json.
        """
        users = load_users()
        if not any(u.get("userName") == username for u in users):
            raise ValueError("User not found")

        update_user(username, {"bio": bio})
        return {"username": username, "bio": bio}

    # ─────────────────────────────────────────
    # Username rename everywhere
    # ─────────────────────────────────────────

    def change_username_everywhere(self, current_username: str, new_username: str) -> None:
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
