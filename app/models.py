from typing import Optional

from setuptools.command.setopt import option_base
from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.base_class import Base

user_room_association = Table(
    "user_room",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key = True),
    Column("room_id", Integer, ForeignKey("chat_rooms.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    rooms = relationship("ChatRoom", secondary=user_room_association, back_populates="members")
    messages = relationship("Message", back_populates="author")

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index = True)
    name: Mapped[str] = mapped_column(nullable = False, unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    members = relationship("User", secondary=user_room_association, back_populates="rooms")
    messages = relationship("Message",back_populates="room")

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default = datetime.utcnow)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("chat_rooms.id"))
    is_edited: Mapped[bool] = mapped_column(default=False)

    author = relationship("User", back_populates="messages")
    room = relationship("ChatRoom", back_populates="messages")
