from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app import models, schemas, auth
from app.models import User, ChatRoom
from app.schemas import RoomOut, RoomCreate, MessageCreate, UserOut

router = APIRouter(
    prefix="/rooms",
    tags=["rooms"]
)

async def check_room(room_id: int, db: AsyncSession):
    room = await db.get(models.ChatRoom, room_id)
    if not room:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

@router.post("/", response_model=RoomOut)
async def create_room(roomData: RoomCreate, current_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):

    stmt = select(models.ChatRoom).where(models.ChatRoom.name == roomData.name)
    result = await db.execute(stmt)
    room = result.scalar_one_or_none()

    if room:
        raise HTTPException(
            status_code=409,
            detail="Room already exists"
        )

    new_room = ChatRoom(
        name = roomData.name,
        description = roomData.description
    )

    db.add(new_room)

    await db.commit()
    await db.refresh(new_room)

    return new_room

@router.get("/", response_model=list[schemas.RoomOut])
async def get_all_rooms(current_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(models.ChatRoom)
    result = await db.execute(stmt)
    rooms = result.scalars().all()

    return rooms

@router.post("/{room_id}/join")
async def join_in_room(room_id: int, current_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    room = await db.get(models.ChatRoom, room_id, options=[selectinload(models.ChatRoom.members)])


    if not room:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    if current_user in room.members:
        raise HTTPException(
            status_code=400,
            detail="Вы уже состоите в этой комнате"
        )

    room.members.append(current_user)

    await db.commit()

    return {"status": "joined"}

@router.get("/{room_id}/members", response_model=list[UserOut])
async def get_room_members(room_id: int, db: AsyncSession = Depends(get_db)):
    await check_room(room_id, db)

    room = await db.get(models.ChatRoom, room_id, options=[selectinload(models.ChatRoom.members)])

    return room.members
