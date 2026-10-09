from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal

from app.models.user import User

from app.schemas.user_schema import UserLogin

from app.auth.security import (
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# DATABASE SESSION
# =========================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================
# LOGIN
# =========================

@router.post("/login")

def login_user(
    user: UserLogin
):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    valid_password = verify_password(
        user.password,
        existing_user.password
    )

    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token({

        "sub": existing_user.email,

        "role": existing_user.role
    })

    return {

        "message": "Login Successful",

        "access_token": access_token,

        "role": existing_user.role,

        "full_name": existing_user.full_name
    }