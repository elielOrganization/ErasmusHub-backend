from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import or_
from typing import List

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.opportunity import Opportunity
from models.application import Application
from models.chat import Chat, ChatMessage
from models.opportunity_teacher import OpportunityTeacher
from models.user_role import UserRole
from models.role import Role
from schemas.chat_schema import ChatRead, MessageCreate, MessageRead, TeacherAssign, TeacherInfo

router = APIRouter(prefix="/chat", tags=["Chat"])


# ── Helpers ─────────────────────────────────────────────────────

def _get_opp_teachers(opportunity_id: int, db: Session) -> List[User]:
    rows = db.exec(
        select(User)
        .join(OpportunityTeacher, OpportunityTeacher.teacher_id == User.id)
        .where(OpportunityTeacher.opportunity_id == opportunity_id)
    ).all()
    return rows


def _is_teacher_of_opp(user_id: int, opportunity_id: int, db: Session) -> bool:
    row = db.exec(
        select(OpportunityTeacher).where(
            OpportunityTeacher.opportunity_id == opportunity_id,
            OpportunityTeacher.teacher_id == user_id,
        )
    ).first()
    return row is not None


def _is_admin(user_id: int, db: Session) -> bool:
    role = db.exec(select(UserRole).where(UserRole.user_id == user_id)).first()
    return role is not None and role.role_id == 1


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
    opp = db.get(Opportunity, chat.opportunity_id)
    teachers = _get_opp_teachers(chat.opportunity_id, db)
    teachers_names = ", ".join(f"{t.first_name} {t.last_name}" for t in teachers) or "Sin profesor"

    return ChatRead(
        id=chat.id,
        opportunity_id=chat.opportunity_id,
        opportunity_name=opp.name if opp else "?",
        student_id=chat.student_id,
        student_name=f"{student.first_name} {student.last_name}" if student else "?",
        teachers_names=teachers_names,
        unread_count=len(unread),
        last_message=last_msg,
        created_at=chat.created_at,
    )


# ── Opportunity teacher assignment ───────────────────────────────

@router.get("/opportunities/{opp_id}/teachers", response_model=List[TeacherInfo])
def get_opportunity_teachers(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    teachers = _get_opp_teachers(opp_id, db)
    return [TeacherInfo(id=t.id, first_name=t.first_name, last_name=t.last_name, email=t.email) for t in teachers]


@router.post("/opportunities/{opp_id}/teachers", response_model=TeacherInfo)
def add_opportunity_teacher(
    opp_id: int,
    data: TeacherAssign,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if not _is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Only admins can assign teachers")

    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    teacher = db.get(User, data.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    existing = db.exec(
        select(OpportunityTeacher).where(
            OpportunityTeacher.opportunity_id == opp_id,
            OpportunityTeacher.teacher_id == data.teacher_id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher already assigned to this opportunity")

    db.add(OpportunityTeacher(opportunity_id=opp_id, teacher_id=data.teacher_id))
    db.commit()

    return TeacherInfo(id=teacher.id, first_name=teacher.first_name, last_name=teacher.last_name, email=teacher.email)


@router.delete("/opportunities/{opp_id}/teachers/{teacher_id}", status_code=204)
def remove_opportunity_teacher(
    opp_id: int,
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    if not _is_admin(current_user.id, db):
        raise HTTPException(status_code=403, detail="Only admins can remove teachers")

    row = db.exec(
        select(OpportunityTeacher).where(
            OpportunityTeacher.opportunity_id == opp_id,
            OpportunityTeacher.teacher_id == teacher_id,
        )
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Assignment not found")

    db.delete(row)
    db.commit()


# ── Chat endpoints ───────────────────────────────────────────────

@router.get("/", response_model=List[ChatRead])
def list_my_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """List all chats for the current user."""
    # Students: chats where they are the student
    student_chats = db.exec(
        select(Chat).where(Chat.student_id == current_user.id)
    ).all()

    # Teachers/coordinators: chats for opportunities they're assigned to
    teacher_opp_ids = db.exec(
        select(OpportunityTeacher.opportunity_id).where(
            OpportunityTeacher.teacher_id == current_user.id
        )
    ).all()

    teacher_chats = []
    if teacher_opp_ids:
        teacher_chats = db.exec(
            select(Chat).where(Chat.opportunity_id.in_(teacher_opp_ids))
        ).all()

    seen = set()
    all_chats = []
    for c in student_chats + teacher_chats:
        if c.id not in seen:
            seen.add(c.id)
            all_chats.append(c)

    return [_build_chat_read(c, current_user.id, db) for c in all_chats]


@router.get("/opportunity/{opp_id}", response_model=ChatRead)
def get_or_create_chat(
    opp_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Student opens (or creates) their chat for an opportunity."""
    opp = db.get(Opportunity, opp_id)
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    teachers = _get_opp_teachers(opp_id, db)
    if not teachers:
        raise HTTPException(status_code=400, detail="This opportunity has no responsible teachers assigned yet")

    # Check if current user is a teacher of this opportunity
    if _is_teacher_of_opp(current_user.id, opp_id, db):
        chats = db.exec(select(Chat).where(Chat.opportunity_id == opp_id)).all()
        if not chats:
            raise HTTPException(status_code=404, detail="No student chats yet for this opportunity")
        return _build_chat_read(chats[0], current_user.id, db)

    # Student must have applied
    application = db.exec(
        select(Application).where(
            Application.opportunity_id == opp_id,
            Application.user_id == current_user.id,
        )
    ).first()
    if not application:
        raise HTTPException(status_code=403, detail="You must have applied to this opportunity to chat")

    chat = db.exec(
        select(Chat).where(
            Chat.opportunity_id == opp_id,
            Chat.student_id == current_user.id,
        )
    ).first()

    if not chat:
        chat = Chat(opportunity_id=opp_id, student_id=current_user.id)
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

    is_student = chat.student_id == current_user.id
    is_teacher = _is_teacher_of_opp(current_user.id, chat.opportunity_id, db)

    if not is_student and not is_teacher:
        raise HTTPException(status_code=403, detail="Not a participant of this chat")

    messages = db.exec(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
    ).all()

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

    is_student = chat.student_id == current_user.id
    is_teacher = _is_teacher_of_opp(current_user.id, chat.opportunity_id, db)

    if not is_student and not is_teacher:
        raise HTTPException(status_code=403, detail="Not a participant of this chat")

    msg = ChatMessage(chat_id=chat_id, sender_id=current_user.id, content=data.content.strip())
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
