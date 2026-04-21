from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from pydantic import BaseModel
import os

from core.database import get_session
from core.security import get_current_user
from models.user import User
from models.selection_process import SelectionProcess

from models.calificacion import Calificacion
from models.document import Document
from models.final_list import FinalList
from models.interview import Interview

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

@router.delete("/end_ERASMUS")
def delete_erasmus(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if not any(role.name.lower() in ['admin', 'administrador'] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have no rights to end erasmus")
    
    try:
        db.exec(delete(FinalList))
        db.exec(delete(Interview))
        db.exec(delete(Calificacion))

        documents = db.exec(select(Document)).all()
        for doc in documents:

            if doc.file_path and os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            
            db.delete(doc)
            
        db.exec(delete(Document))
        db.commit()

        return {"message": "All Erasmus data (Final List, Interviews, Qualifications, and Documents) has been successfully deleted."}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An error occurred while ending ERASMUS: {str(e)}"
        )