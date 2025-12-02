from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.authenticationService import AuthService
from ..dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


# ─────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str


class UpdateBioRequest(BaseModel):
    username: str
    bio: str


class ChangeUsernameRequest(BaseModel):
    newUsername: str


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post("/register")
def register(request: RegisterRequest):
    """
    Register a new normal user (not admin).
    Returns the created user object in the 'user' field
    (keeps existing integration test behaviour).
    """
    try:
        user = auth_service.register_user(request.username, request.password)
        return {
            "message": "User registered successfully",
            "user": user,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(request: LoginRequest):
    """
    Login a user or admin by verifying credentials.
    """
    try:
        result = auth_service.login(request.username, request.password)
        return {
            "message": f"{result['role'].capitalize()} logged in successfully",
            "role": result["role"],
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/change-password")
def change_password(request: ChangePasswordRequest):
    """
    Change an existing user's password.
    (Currently takes username from body; you can later switch to get_current_user.)
    """
    try:
        result = auth_service.change_password(
            request.username,
            request.old_password,
            request.new_password,
        )
        return {
            "message": "Password changed successfully",
            "username": result["username"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-bio")
def update_bio(request: UpdateBioRequest):
    """
    Update the profile bio for an existing user.
    """
    try:
        result = auth_service.update_bio(request.username, request.bio)
        return {
            "message": "Bio updated successfully",
            "username": result["username"],
            "bio": result["bio"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change-username")
def change_username(
    request: ChangeUsernameRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Change an existing user's password.

    - Verifies the old password.
    - Stores the new password as a bcrypt hash in users.json.
    """
    try:
        result = auth_service.change_password(
            request.username,
            request.old_password,
            request.new_password,
        )
        return {"message": "Password changed successfully", "username": result["username"]}
    except ValueError as e:
        # You can tune status codes (400 vs 401) as you like
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-bio")
def update_bio(request: UpdateBioRequest):
    """
    Update the profile bio for an existing user.
    """
    try:
        result = auth_service.update_bio(request.username, request.bio)
        return {
            "message": "Bio updated successfully",
            "username": result["username"],
            "bio": result["bio"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))