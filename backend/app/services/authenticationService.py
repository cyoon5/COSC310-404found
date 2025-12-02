from passlib.hash import bcrypt
from typing import Dict, Any
from ..repositories.usersRepo import load_users, add_user, update_user
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
