from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.opportunity import Opportunity
from models.application import Application
from models.chat import Chat, ChatMessage
from schemas.chat_schema import ChatRead, MessageCreate, MessageRead, TeacherAssign, TeacherInfo

router = APIRouter(prefix="/chat", tags=["Chat"])


def _build_chat_read(chat: Chat, current_user_id: int, db: Session) -> ChatRead:
    unread = db.exec(
        select(ChatMessage).where(
            ChatMessage.chat_id == chat.id,
            ChatMessage.sender_id != current_user_id,
            ChatMessage.is_read == False,
        )
    ).all()

    last_msg_row = db.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(1)
    ).first()

    last_msg = None
    if last_msg_row:
        sender = db.get(User, last_msg_row.sender_id)
        last_msg = MessageRead(
            id=last_msg_row.id,
            chat_id=last_msg_row.chat_id,
            sender_id=last_msg_row.sender_id,
            sender_name=f"{sender.first_name} {sender.last_name}" if sender else "?",
            content=last_msg_row.content,
            is_read=last_msg_row.is_read,
            created_at=last_msg_row.created_at,
        )

    student = db.get(User, chat.student_id)
    teacher = db.get(User, chat.teacher_id)
    opp = db.get(Opportunity, chat.opportunity_id)

    return ChatRead(
        id=chat.id,
        opportunity_id=chat.opportunity_id,
        opportunity_name=opp.name if opp else "?",
        student_id=chat.student_id,
        student_name=f"{student.first_name} {student.last_name}" if student else "?",
        teacher_id=chat.teacher_id,
        teacher_name=f"{teacher.first_name} {teacher.last_name}" if teacher else "?",
        unread_count=len(unread),
        last_message=last_msg,
        created_at=chat.created_at,
    )


@router.get("/", response_model=List[ChatRead])
def list_my_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List all chats for the current user (student or teacher)."""
    chats = db.exec(
        select(Chat).where(
            (Chat.student_id == current_user.id) | (Chat.teacher_id == current_user.id)
        )
    ).all()
    return [_build_chat_read(c, current_user.id, db) for c in chats]


@router.get("/opportunity/{opp_id}", response_model=ChatRead)
def get_or_create_chat(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get or create the chat for the current student in a given opportunity."""
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if not opp.responsible_teacher_id:
        raise HTTPException(status_code=400, detail="This opportunity has no responsible teacher assigned")

    # Only students who applied can open a chat
    application = db.exec(
        select(Application).where(
            Application.opportunity_id == opp_id,
            Application.user_id == current_user.id,
        )
    ).first()

    # Teachers can also access all chats for their opportunity
    role_names = [r.name.lower() for r in current_user.roles] if current_user.roles else []
    is_teacher = "teacher" in role_names or "coordinator" in role_names
    is_responsible = current_user.id == opp.responsible_teacher_id

    if not application and not (is_teacher and is_responsible):
        raise HTTPException(status_code=403, detail="You must have applied to this opportunity to access chat")

    # Teachers see all chats for their opportunity, not their own
    if is_responsible and not application:
        chats = db.exec(select(Chat).where(Chat.opportunity_id == opp_id)).all()
        if not chats:
            raise HTTPException(status_code=404, detail="No chats yet for this opportunity")
        # Return first (teachers should use GET /chat/ for the full list)
        return _build_chat_read(chats[0], current_user.id, db)

    # Student: find or create their chat
    chat = db.exec(
        select(Chat).where(
            Chat.opportunity_id == opp_id,
            Chat.student_id == current_user.id,
        )
    ).first()

    if not chat:
        chat = Chat(
            opportunity_id=opp_id,
            student_id=current_user.id,
            teacher_id=opp.responsible_teacher_id,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)

    return _build_chat_read(chat, current_user.id, db)


@router.get("/{chat_id}/messages", response_model=List[MessageRead])
def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if current_user.id not in (chat.student_id, chat.teacher_id):
        raise HTTPException(status_code=403, detail="Not a participant of this chat")

    messages = db.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
    ).all()

    # Mark messages from the other party as read
    for msg in messages:
        if msg.sender_id != current_user.id and not msg.is_read:
            msg.is_read = True
            db.add(msg)
    db.commit()

    result = []
    for msg in messages:
        sender = db.get(User, msg.sender_id)
        result.append(MessageRead(
            id=msg.id,
            chat_id=msg.chat_id,
            sender_id=msg.sender_id,
            sender_name=f"{sender.first_name} {sender.last_name}" if sender else "?",
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at,
        ))
    return result


@router.post("/{chat_id}/messages", response_model=MessageRead)
def send_message(
    chat_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if current_user.id not in (chat.student_id, chat.teacher_id):
        raise HTTPException(status_code=403, detail="Not a participant of this chat")

    msg = ChatMessage(
        chat_id=chat_id,
        sender_id=current_user.id,
        content=data.content.strip(),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageRead(
        id=msg.id,
        chat_id=msg.chat_id,
        sender_id=msg.sender_id,
        sender_name=f"{current_user.first_name} {current_user.last_name}",
        content=msg.content,
        is_read=msg.is_read,
        created_at=msg.created_at,
    )


# ── Opportunity teacher assignment ──────────────────────────────

@router.put("/opportunities/{opp_id}/teacher", response_model=TeacherInfo)
def assign_teacher(
    opp_id: int,
    data: TeacherAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Assign (or change) the responsible teacher for an opportunity. Admin only."""
    from models.user_role import UserRole
    role = db.exec(select(UserRole).where(UserRole.user_id == current_user.id)).first()
    if not role or role.role_id != 1:
        raise HTTPException(status_code=403, detail="Only admins can assign teachers")

    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    teacher = db.get(User, data.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    opp.responsible_teacher_id = data.teacher_id
    db.add(opp)
    db.commit()
    db.refresh(opp)

    return TeacherInfo(
        id=teacher.id,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        email=teacher.email,
    )


@router.get("/opportunities/{opp_id}/teacher", response_model=TeacherInfo)
def get_teacher(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Get the responsible teacher for an opportunity."""
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if not opp.responsible_teacher_id:
        raise HTTPException(status_code=404, detail="No teacher assigned to this opportunity")

    teacher = db.get(User, opp.responsible_teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return TeacherInfo(
        id=teacher.id,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        email=teacher.email,
    )
