from fastapi import  Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import models, auth
from app.models import User
from app.schemas import MessageCreate, MessageOut
from app.routers.rooms import check_room

router = APIRouter(
    prefix="/rooms/{room_id}/messages",
    tags=["messages"]
)



@router.post("/", response_model=MessageOut)
async def send_message(room_id: int, messageData: MessageCreate, current_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    await check_room(room_id, db)

    new_message = models.Message(
        content = messageData.content,
        author_id = current_user.id,
        room_id = room_id
    )

    db.add(new_message)

    await db.commit()
    await db.refresh(new_message)

    return new_message

@router.get("/", response_model=list[MessageOut])
async def get_all_messages(room_id: int, current_user: User = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    await check_room(room_id, db)

    stmt = select(models.Message).where(models.Message.room_id == room_id).order_by(models.Message.created_at.asc())
    result = await db.execute(stmt)
    messages = result.scalars().all()

    return messages