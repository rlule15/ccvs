# TODO Implement user routes
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

import app.db.schema as schema
from app.core.security import authenticate_user, hash_password, verify_session
from app.db.db_config import get_db
from app.models.user_model import UserCreate, UserResponse

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=201)
def sign_up(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    exisitng_user = db.execute(
        select(schema.User).where(schema.User.username == user.username)
    ).scalar_one_or_none()
    if exisitng_user:
        raise HTTPException(status_code=400, detail="Username not available")

    count_white = (
        db.execute(
            select(func.count(schema.User.id)).filter(schema.User.team == "white")
        ).scalar()
    ) or 0
    count_black = (
        db.execute(
            select(func.count(schema.User.id)).filter(schema.User.team == "black")
        ).scalar()
    ) or 0

    if count_white > count_black:
        assigned_team = "black"
    else:
        assigned_team = "white"

    new_user = schema.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=hash_password(user.password),
        team=assigned_team,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/signin", response_model=UserResponse, status_code=201)
def sign_in(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
    request: Request,
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return user


@router.post("/signout")
def sign_out(request: Request):
    request.session.clear()
    return "Successfully signed out"


@router.get("/me", response_model=UserResponse, status_code=201)
def get_me(
    user_id: Annotated[int, Depends(verify_session)],
    db: Annotated[Session, Depends(get_db)],
):
    user = db.execute(
        select(schema.User).where(schema.User.id == user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
