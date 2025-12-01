from passlib.hash import bcrypt
from typing import Dict, Any
from ..repositories.usersRepo import load_users, add_user
from ..repositories.adminRepo import load_admins



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
