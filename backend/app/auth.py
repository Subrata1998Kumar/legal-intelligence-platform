import json
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

security = HTTPBasic()

ROLE_HIERARCHY = {
    "Legal_Officer": 1,
    "Senior_Advisor": 2,
    "Admin": 3
}


def _load_users_from_json():
    json_path = os.path.join(os.path.dirname(__file__), "users.json")
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def verify_password(plain_password, stored_password):
    return plain_password is not None and stored_password is not None and plain_password == stored_password


def get_current_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

    # users.json is authoritative for this POC's hardcoded credentials.
    for entry in _load_users_from_json():
        if entry.get("username") != credentials.username:
            continue
        if not verify_password(credentials.password, entry.get("password")):
            raise credentials_exception

        user = db.query(User).filter(User.username == credentials.username).first()
        if user is None:
            user = User(
                username=entry["username"],
                password=entry["password"],
                role=entry["role"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        elif user.password != entry["password"] or user.role != entry["role"]:
            user.password = entry["password"]
            user.role = entry["role"]
            db.commit()
            db.refresh(user)
        return user

    raise credentials_exception

class RoleChecker:
    def __init__(self, required_role: str):
        self.required_role = required_role

    def __call__(self, current_user: User = Depends(get_current_user)):
        user_lvl = ROLE_HIERARCHY.get(current_user.role, 0)
        req_lvl = ROLE_HIERARCHY.get(self.required_role, 0)
        if user_lvl < req_lvl:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted under current security clearance."
            )
        return current_user