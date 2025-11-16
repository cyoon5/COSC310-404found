from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.authenticationService import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()

# Request models for registration and login, to help with data validation
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# User registration
@router.post("/register")

def register(request: RegisterRequest):
    """
        Register a new user, ensuring the username is unique.
    """
    try:
        user = auth_service.register_user(request.username, request.password)
        return {"message": "User registered successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login for users/admins
@router.post("/login")
def login(request: LoginRequest):
    """
        Login a user or admin by verifying credentials.
    """
    try:
        result = auth_service.login(request.username, request.password)
        return {"message": f"{result['role'].capitalize()} logged in successfully", "role": result['role']}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
