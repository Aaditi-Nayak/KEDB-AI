from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.utils.jwt import verify_access_token

# every protected api expects a bearer token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def get_current_user(
        token:str=Depends(oauth2_scheme),
        db:Session=Depends(get_db)
):
    payload=verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    
    email=payload.get("sub")
    user=db.query(User).filter(User.email==email).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    
    return user