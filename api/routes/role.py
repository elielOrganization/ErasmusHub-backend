from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_session
from models.role import Role
from schemas.role_schema import RoleRead

router = APIRouter(tags=["Role"])

@router.get("/role/", response_model=list[RoleRead])
def get_roles(db: Session = Depends(get_session)):
    roles = db.exec(select(Role)).all()
    if not roles:
        return HTTPException(status_code=404, detail="No existen roles (si esto pasa chungo peluco)")
    
    return roles
