from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr, ConfigDict

# Database dependency
from app.database import get_db

# Auth utilities
from app.utils.auth import get_current_user, get_password_hash

# SQLAlchemy model import
from app.models.users import Users

# Pydantic schema import for UserUpdate to avoid duplicate definition
from app.schemas.user import UserUpdate

# OAuth2 scheme (not used directly here but defined for completeness)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ----- Inline Pydantic Schemas -----

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., min_length=1)
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = Field(default=None, min_length=1)

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: EmailStr
    display_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    display_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ----- Router -----

user_router = APIRouter()

# GET /users - list with optional search and pagination
@user_router.get("/users", response_model=dict)
def list_users(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    query = db.query(Users)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Users.email.ilike(pattern) | Users.username.ilike(pattern) | Users.display_name.ilike(pattern)
        )
    total = query.with_entities(func.count(Users.id)).scalar()
    users = query.offset(offset).limit(limit).all()
    items = [UserRead.model_validate(u, from_attributes=True).model_dump() for u in users]
    return {"items": items, "total": total, "limit": limit, "offset": offset}

# GET /users/{id}
@user_router.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return UserRead.model_validate(user, from_attributes=True)

# POST /users - create a new user
@user_router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: RegisterRequest,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    hashed_pwd = get_password_hash(user_in.password)
    new_user = Users(
        email=user_in.email, password=hashed_pwd, full_name=user_in.display_name,
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username already exists")
    db.refresh(new_user)
    return UserRead.model_validate(new_user, from_attributes=True)

# PUT /users/{id} - update user details
@user_router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_in: UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.username is not None:
        user.username = user_in.username
    if user_in.display_name is not None:
        user.display_name = user_in.display_name
    if user_in.password is not None:
        user.password = get_password_hash(user_in.password)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or username already exists")
    db.refresh(user)
    return UserRead.model_validate(user, from_attributes=True)

# DELETE /users/{id}
@user_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(user)
    db.commit()
    return None