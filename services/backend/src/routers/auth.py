from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..authentication.token import create_access_token
from ..commons.db_storage.models import User
from ..placeholder.get_db import get_db
from ..schemas.schemas import Token, UserCreate

router = APIRouter()
ACCESS_TOKEN_EXPIRE_MINUTES = 600


@router.post("/signup/", response_model=dict)
async def post_signup(signup: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    # Check if user already exists
    db_user = db.query(User).filter(User.username == signup.username).first()
    if db_user:
        return JSONResponse(status_code=400, content={"msg": "Username already registered"})

    # Create new user and add to the database
    user = User(username=signup.username, hashed_password=User.get_password_hash(signup.password))
    db.add(user)
    db.commit()

    # Return a success message
    return JSONResponse(status_code=200, content={"msg": "User created successfully, please log in."})


@router.post("/login/", response_model=Token)
def login_for_access_token(response: Response, login: UserCreate, db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(User).filter(User.username == login.username).first()
    if not user or not user.verify_password(login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "is_admin": user.is_admin}, expires_delta=access_token_expires)

    # Optionally, set a cookie with the token and redirect
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return Token(access_token=access_token, token_type="bearer")
