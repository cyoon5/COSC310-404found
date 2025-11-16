from fastapi import Depends, HTTPException, Header
from backend.app.repositories.usersRepo import find_user_by_username
from backend.app.repositories.adminRepo import find_admin_by_name
import time

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

def ensure_not_banned(user: dict = Depends(get_current_user)):
    """
    Dependency that blocks actions for currently banned users.

    - Only applies to normal users (role == "user").
    - Looks up the full user record via find_user_by_username to access banExpiresAt.
    - If banExpiresAt is a future Unix timestamp, raises 403.
    - Admins are never blocked by this dependency.
    """
    # Only enforce bans on regular users
    if user.get("role") != "user":
        return user

    record = find_user_by_username(user.get("username"))
    if not record:
        return user

    ban_expires_at = record.get("banExpiresAt")
    if ban_expires_at is None:
        return user

    try:
        expires = float(ban_expires_at)
    except (TypeError, ValueError):
        return user

    now = time.time()
    if expires > now:
        raise HTTPException(
            status_code=403,
            detail="User is currently banned and cannot perform this action",
        )

    return user