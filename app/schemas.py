from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}

class RoomCreate(BaseModel):
    name: str = Field(min_length=1)
    description: Optional[str] = None

class RoomOut(BaseModel):
    id : int
    name: str
    created_at : datetime

    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
    room_id: int

class MessageOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author_id: int
    room_id: int

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str