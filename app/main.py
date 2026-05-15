from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.base_class import Base
from app.database import engine, get_db
from app import models, schemas, auth
from app.auth import hash_password, verify_password, create_access_token
from app.models import User
from app.routers import rooms, messages
from app.schemas import UserOut, UserCreate,TokenResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Chat API", lifespan=lifespan)

routers = [
    rooms.router,
    messages.router
]

for router in routers:
    app.include_router(router)


@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(userData: UserCreate, db: AsyncSession = Depends(get_db)):

    stmt = select(models.User).where(models.User.username == userData.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code = 400,
            detail="Username already registered"
        )

    new_user = User(
        username = userData.username,
        hashed_password = hash_password(userData.password)
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user

@app.post("/login", response_model=TokenResponse)
async def login_user( form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db) ):
    stmt = select(models.User).where(models.User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserOut)
async def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

