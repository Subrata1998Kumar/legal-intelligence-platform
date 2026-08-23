from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse
from ..auth import get_current_user, RoleChecker

router = APIRouter(prefix="/users", tags=["Users & RBAC"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker("Admin"))):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered.")
    
    user = User(username=user_in.username, password=user_in.password, role=user_in.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=UserResponse)
def login(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user