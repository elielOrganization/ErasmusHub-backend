import os
import shutil
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.user_role import UserRole
from models.role import Role
from models.chat import Chat, ChatMessage
from models.application import Application
from models.document import Document
from models.interview import Interview
from models.final_list import FinalList
from models.opportunity_teacher import OpportunityTeacher
from models.notification import Notification
from models.selection_process import SelectionProcess
from models.opportunity import Opportunity

router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "library")


# ── Helper ──────────────────────────────────────────────────────

def _require_admin(current_user: User, db: Session):
    row = db.exec(
        select(UserRole)
        .join(Role, Role.id == UserRole.role_id)
        .where(UserRole.user_id == current_user.id, Role.name.ilike("%admin%"))
    ).first()
    if not row:
        raise HTTPException(status_code=403, detail="Admin access required")


# ── Stats ────────────────────────────────────────────────────────

@router.get("/stats")
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    _require_admin(current_user, db)
    return {
        "total_users": len(db.exec(select(User)).all()),
        "total_opportunities": len(db.exec(select(Opportunity)).all()),
        "total_applications": len(db.exec(select(Application)).all()),
        "total_chats": len(db.exec(select(Chat)).all()),
        "total_messages": len(db.exec(select(ChatMessage)).all()),
        "total_documents": len(db.exec(select(Document)).all()),
        "total_interviews": len(db.exec(select(Interview)).all()),
    }


# ── Reset chats ──────────────────────────────────────────────────

@router.post("/reset-chats")
def reset_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Delete all chat messages and chats. Admin only."""
    _require_admin(current_user, db)

    messages = db.exec(select(ChatMessage)).all()
    for m in messages:
        db.delete(m)

    chats = db.exec(select(Chat)).all()
    for c in chats:
        db.delete(c)

    db.commit()
    return {"deleted_chats": len(chats), "deleted_messages": len(messages)}


# ── Full Erasmus reset ───────────────────────────────────────────

@router.post("/reset-erasmus")
def reset_erasmus(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Full system reset: wipes all Erasmus process data.
    Keeps: users, roles, opportunities.
    Deletes: applications, documents, chats, internships, interviews,
             final list, opportunity-teacher assignments, notifications.
    Deactivates the selection process.
    Admin only.
    """
    _require_admin(current_user, db)

    # 1. Chat messages → chats
    for m in db.exec(select(ChatMessage)).all():
        db.delete(m)
    for c in db.exec(select(Chat)).all():
        db.delete(c)

    # 2. Applications
    for row in db.exec(select(Application)).all():
        db.delete(row)

    # 4. Documents (DB + files on disk)
    docs = db.exec(select(Document)).all()
    for doc in docs:
        if doc.file_path:
            full_path = os.path.join(UPLOAD_DIR, doc.file_path)
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                except OSError:
                    pass
        db.delete(doc)

    # 5. Interviews
    for row in db.exec(select(Interview)).all():
        db.delete(row)

    # 6. Final list
    for row in db.exec(select(FinalList)).all():
        db.delete(row)

    # 7. Opportunity-teacher assignments
    for row in db.exec(select(OpportunityTeacher)).all():
        db.delete(row)

    # 8. Notifications
    for row in db.exec(select(Notification)).all():
        db.delete(row)

    # 9. Deactivate selection process
    sp = db.exec(select(SelectionProcess)).first()
    if sp:
        sp.active = False
        db.add(sp)

    # 10. Reset filled_slots to 0 on all opportunities
    for opp in db.exec(select(Opportunity)).all():
        opp.filled_slots = 0
        db.add(opp)

    db.commit()
    return {"status": "reset_complete"}
