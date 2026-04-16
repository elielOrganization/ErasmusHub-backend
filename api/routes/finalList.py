from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, delete

from core.database import get_session
from core.security import get_current_user

from models.user import User
from models.interview import Interview
from models.role import Role
from models.user_role import UserRole
from models.final_list import FinalList 

router = APIRouter(prefix="/final-list", tags=["Final List"])

ALLOWED_PUBLISHER_ROLES = ("admin", "coordinator", "tutor", "co-tutor")

@router.post("/publish")
def publish_final_list(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Generates the final list by taking approved users and saving a snapshot.
    """
    role_id = db.exec(select(UserRole.role_id).where(UserRole.user_id == current_user.id)).first()
    role_name = db.exec(select(Role.name).where(Role.id == role_id)).first() or ""
    
    is_authorized = any(r in role_name.lower() for r in ALLOWED_PUBLISHER_ROLES)
    if not is_authorized:
        raise HTTPException(
            status_code=403, 
            detail="You do not have permission to publish the final list."
        )

    try:
        db.exec(delete(FinalList))
        
        statement = select(User).join(Interview, User.id == Interview.user_id).where(
            Interview.status == "passed",
            User.final_grade != None
        )
        approved_users = db.exec(statement).unique().all()
        
        new_records = []
        for user in approved_users:
            snapshot = FinalList(
                user_id=user.id,
                first_name=user.first_name, 
                last_name=user.last_name,
                year=user.year,
                final_grade=user.final_grade,
                published_by=current_user.id
            )
            db.add(snapshot)
            new_records.append(snapshot)
            
        db.commit()
        
        return {
            "message": "Final list published successfully.",
            "total_published": len(new_records)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while publishing the list: {str(e)}"
        )

@router.get("", response_model=List[FinalList])
def get_final_list(db: Session = Depends(get_session)):
    """
    Reads the published final list to display it on the frontend.
    """
    statement = select(FinalList)
    results = db.exec(statement).all()
    
    return results