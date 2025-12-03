from fastapi import Depends, HTTPException, Header
from app.repositories.usersRepo import find_user_by_username
from app.repositories.adminRepo import find_admin_by_name
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

def ensure_not_banned(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that blocks actions for currently banned users.

    Behaviour:
    - Only applies to normal users (role == "user").
    - Looks up the full user record via find_user_by_username to access banExpiresAt.
    - If banExpiresAt is a future Unix timestamp, raises 403.
    - Admins are never blocked by this dependency.

    Returns:
        The same user dict that came from get_current_user if the user is allowed
        to proceed (not banned or ban has expired).
    """
    # Only enforce bans on regular users
    if user.get("role") != "user":
        return user

    # Reload full record so we can see banExpiresAt, penalties, etc.
    record = find_user_by_username(user.get("username"))
    if not record:
        # If the user somehow isn't in users.json, just allow (CSV-only etc.)
        return user

    ban_expires_at = record.get("banExpiresAt")
    if ban_expires_at is None:
        # No ban recorded
        return user

    try:
        expires = float(ban_expires_at)
    except (TypeError, ValueError):
        # Corrupt / non-numeric value → treat as unbanned
        return user

    # If ban expiry is in the future, block the action
    if expires > time.time():
        raise HTTPException(
            status_code=403,
            detail="User is currently banned and cannot perform this action",
        )

    # Ban is in the past → treat as unbanned
    return user