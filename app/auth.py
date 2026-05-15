from passlib.context import CryptContext
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)

    credentials_exception = HTTPException(
            status_code=401,
        )

    if not payload:
        raise credentials_exception

    username_sub = payload.get("sub")

    if not username_sub:
        raise credentials_exception

    stmt = select(models.User).where(models.User.username == username_sub)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    return user
