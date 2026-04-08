from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.selection_process import SelectionProcess

router = APIRouter(prefix="/selection-process", tags=["Selection Process"])

class SelectionProcessStatus(BaseModel):
    active: bool

@router.get("/", response_model=SelectionProcessStatus)
def get_selection_process_status(db: Session = Depends(get_session)):
    # Asumimos que hay solo un registro, o tomamos el último
    process = db.exec(select(SelectionProcess).order_by(SelectionProcess.id.desc())).first()
    if not process:
        # Crear uno por defecto si no existe
        process = SelectionProcess(active=False)
        db.add(process)
        db.commit()
        db.refresh(process)
    return SelectionProcessStatus(active=process.active)

@router.post("/toggle", response_model=SelectionProcessStatus)
def toggle_selection_process(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Solo admin puede cambiar
    if not any(role.name.lower() in ['admin', 'administrator'] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar el proceso")
    
    process = db.exec(select(SelectionProcess).order_by(SelectionProcess.id.desc())).first()
    if not process:
        process = SelectionProcess(active=False)
        db.add(process)
    
    process.active = not process.active
    db.commit()
    db.refresh(process)
    
    return SelectionProcessStatus(active=process.active)