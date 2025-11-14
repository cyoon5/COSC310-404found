from fastapi import Depends, HTTPException, Header
from backend.app.repositories.usersRepo import find_user_by_username
from backend.app.repositories.adminRepo import find_admin_by_name


def get_current_user(x_username: str = Header(...)):
    """
    Extract the username from the X-Username header and determine whether
    they are a user or admin by checking the JSON files.
    """
    # Check normal users
    user = find_user_by_username(x_username)
    if user:
        return {
            "username": x_username,
            "role": "user"
        }

    # Check admins
    admin = find_admin_by_name(x_username)
    if admin:
        return {
            "username": x_username,
            "role": "admin"
        }

    # Not found anywhere
    raise HTTPException(status_code=401, detail="Invalid or unknown user")


def admin_required(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

