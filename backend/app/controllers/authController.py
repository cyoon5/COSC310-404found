from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.authenticationService import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()

# Request models
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# User registration
@router.post("/register")
def register(request: RegisterRequest):
    try:
        user = auth_service.register_user(request.username, request.password)
        return {"message": "User registered successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login for users/admins
@router.post("/login")
def login(request: LoginRequest):
    try:
        result = auth_service.login(request.username, request.password)
        return {"message": f"{result['role'].capitalize()} logged in successfully", "role": result['role']}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
