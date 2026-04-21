from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .user import User
    from .opportunity import Opportunity


class Chat(SQLModel, table=True):
    __tablename__ = "chat"

    id: Optional[int] = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunity.id")
    student_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    opportunity: Optional["Opportunity"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Chat.opportunity_id]"}
    )
    student: Optional["User"] = Relationship(
        back_populates="chats_as_student",
        sa_relationship_kwargs={"foreign_keys": "[Chat.student_id]"},
    )
    messages: List["ChatMessage"] = Relationship(back_populates="chat")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_message"

    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    sender_id: int = Field(foreign_key="user.id")
    content: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    chat: Optional["Chat"] = Relationship(back_populates="messages")
    sender: Optional["User"] = Relationship(
        back_populates="chat_messages_sent",
        sa_relationship_kwargs={"foreign_keys": "[ChatMessage.sender_id]"},
    )
