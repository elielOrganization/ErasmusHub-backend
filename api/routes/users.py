from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from sqlalchemy import or_
from typing import List
from datetime import date


from models.user import User
from models.role import Role
from models.user_role import UserRole
from models.notification import Notification
from models.document import Document
from models.task import Task
from models.application import Application
from models.internship import Internship
from models.communication import Communication
from models.exemption import Exemption
from models.opportunity import Opportunity
from models.weekly_schedule import WeeklySchedule
from models.follow_up import FollowUp
from models.daily_log import DailyLog
from models.attendance import Attendance
from schemas.user_schema import UserCreate, UserPublic, UserUpdate
from models.calificacion import Calificacion
from models.interview import Interview, InterviewStatus
from core.database import get_session
from core.security import get_password_hash, encrypt_data, decrypt_data, get_deterministic_hash

router = APIRouter(tags=["Users"])


@router.post("/users/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    
    existing_user = db.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user_in.rodne_cislo:
        search_hash = get_deterministic_hash(user_in.rodne_cislo)
        existing_dni = db.exec(select(User).where(User.rodne_cislo_hash == search_hash)).first()
        if existing_dni:
            raise HTTPException(status_code=400, detail="Rodne cislo already registered")
            
        encrypted_rod = encrypt_data(user_in.rodne_cislo)
        hash_rod = search_hash
    else:
        raise HTTPException(status_code=400, detail="Rodne cislo is required")

    db_user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password_hash=get_password_hash(user_in.password),
        rodne_cislo=encrypted_rod,    
        rodne_cislo_hash=hash_rod,     
        birth_date=user_in.birth_date,
        address=user_in.address,
        phone=user_in.phone,
        is_minor=user_in.is_minor,
    )

    db.add(db_user)
    db.flush()

    today = date.today()

    age = today.year - user_in.birth_date.year - (
        (today.month, today.day) < (user_in.birth_date.month, user_in.birth_date.day)
    )

    if age < 15:
        db_user_rol = UserRole(
            user_id=db_user.id,
            role_id=4
        )
    else:
        db_user_rol = UserRole(
            user_id=db_user.id,
            role_id=6
        )

    db.add(db_user_rol)
    db.commit()
    db.refresh(db_user)
    
    roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == db_user.id)).all()
    user_dict = db_user.model_dump(exclude={'roles'})
    user_dict['rodne_cislo'] = decrypt_data(user_dict.get('rodne_cislo'))
    
    user_data = UserPublic.model_validate(user_dict)
    user_data.role = roles[0] if roles else None
    return user_data

@router.get("/users/graded", response_model=List[UserPublic])
def get_graded_users(db: Session = Depends(get_session)):
    """Devuelve todos los usuarios que tienen una nota final, ordenados de mayor a menor."""
    
    statement = select(User).where(User.final_grade.isnot(None))
    graded_users = db.exec(statement).all()
    
    user_publics = []
    
    for user in graded_users:
        roles = db.exec(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user.id)
        ).all()
        
        user_dict = user.model_dump(exclude={'roles'})
        if user_dict.get('rodne_cislo'):
            user_dict['rodne_cislo'] = decrypt_data(user_dict['rodne_cislo'])
            
        user_data = UserPublic.model_validate(user_dict)
        user_data.role = roles[0] if roles else None
        
        user_publics.append(user_data)
        
    user_publics.sort(key=lambda x: x.final_grade, reverse=True)
        
    return user_publics

@router.get("/users/", response_model=List[UserPublic])
def read_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    user_publics = []
    
    for user in users:
        roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == user.id)).all()
        
        user_dict = user.model_dump(exclude={'roles'})
        if user_dict.get('rodne_cislo'):
            user_dict['rodne_cislo'] = decrypt_data(user_dict['rodne_cislo'])
            
        user_data = UserPublic.model_validate(user_dict)
        user_data.role = roles[0] if roles else None
        user_publics.append(user_data)
        
    return user_publics


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Delete internships owned by this user and all their children
    student_internships = db.exec(select(Internship).where(Internship.student_id == user_id)).all()
    for internship in student_internships:
        iid = internship.id
        for record in db.exec(select(WeeklySchedule).where(WeeklySchedule.internship_id == iid)).all():
            db.delete(record)
        for record in db.exec(select(FollowUp).where(FollowUp.internship_id == iid)).all():
            db.delete(record)
        for record in db.exec(select(DailyLog).where(DailyLog.internship_id == iid)).all():
            db.delete(record)
        for record in db.exec(select(Attendance).where(Attendance.internship_id == iid)).all():
            db.delete(record)
        for record in db.exec(select(Communication).where(Communication.internship_id == iid)).all():
            db.delete(record)
        db.delete(internship)

    # 2. Nullify tutor/co-tutor references in internships not owned by this user
    for internship in db.exec(select(Internship).where(Internship.tutor_id == user_id)).all():
        internship.tutor_id = None
        db.add(internship)
    for internship in db.exec(select(Internship).where(Internship.co_tutor_id == user_id)).all():
        internship.co_tutor_id = None
        db.add(internship)

    # 3. Delete remaining communications sent by this user (in other internships)
    for record in db.exec(select(Communication).where(Communication.sender_id == user_id)).all():
        db.delete(record)

    # 4. Delete documents and tasks (FK to user and optionally to application)
    for record in db.exec(select(Document).where(Document.user_id == user_id)).all():
        db.delete(record)
    for record in db.exec(select(Task).where(Task.user_id == user_id)).all():
        db.delete(record)

    # 5. Delete applications
    for record in db.exec(select(Application).where(Application.user_id == user_id)).all():
        db.delete(record)

    # 6. Delete notifications
    for record in db.exec(select(Notification).where(Notification.user_id == user_id)).all():
        db.delete(record)

    # 7. Delete exemptions (as student or as reviewer)
    for record in db.exec(select(Exemption).where(
        or_(Exemption.student_id == user_id, Exemption.reviewed_by == user_id)
    )).all():
        db.delete(record)

    # 8. Nullify opportunity creator references
    for opp in db.exec(select(Opportunity).where(Opportunity.creator_id == user_id)).all():
        opp.creator_id = None
        db.add(opp)

    # 9. Delete user roles
    for record in db.exec(select(UserRole).where(UserRole.user_id == user_id)).all():
        db.delete(record)

    # 10. Delete user
    db.delete(db_user)
    db.commit()


@router.patch("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        password = update_data.pop("password")
        db_user.password_hash = get_password_hash(password)

    if "rodne_cislo" in update_data:
        new_dni = update_data.pop("rodne_cislo")
        
        if new_dni:
            new_hash = get_deterministic_hash(new_dni)
            
            existing_dni = db.exec(select(User).where(User.rodne_cislo_hash == new_hash, User.id != user_id)).first()
            if existing_dni:
                raise HTTPException(status_code=400, detail="Rodne cislo already registered")
                
            db_user.rodne_cislo = encrypt_data(new_dni)
            db_user.rodne_cislo_hash = new_hash
        else:
            db_user.rodne_cislo = None
            db_user.rodne_cislo_hash = None

    if "role_id" in update_data:
        new_role_id = update_data.pop("role_id")
        role_exists = db.get(Role, new_role_id)
        if not role_exists:
            raise HTTPException(status_code=400, detail="Role not found")
        
        db.exec(delete(UserRole).where(UserRole.user_id == db_user.id)) 
        new_user_role = UserRole(user_id=db_user.id, role_id=new_role_id)
        db.add(new_user_role)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == db_user.id)).all()
    
    user_dict = db_user.model_dump(exclude={'roles'})
    if user_dict.get('rodne_cislo'):
        user_dict['rodne_cislo'] = decrypt_data(user_dict['rodne_cislo'])
        
    user_data = UserPublic.model_validate(user_dict)
    user_data.role = roles[0] if roles else None
    return user_data

@router.post("/users/calculate-all-grades", response_model=List[UserPublic])
def calculate_all_users_final_grade(db: Session = Depends(get_session)):
    calificacion = db.exec(select(Calificacion)).first()
    if not calificacion:
        raise HTTPException(
            status_code=404, 
            detail="Calification weights are not configured in the system"
        )
    
    statement = (
        select(User)
        .join(Interview, User.id == Interview.user_id)
        .where(
            Interview.status == InterviewStatus.passed
        )
    )
    eligible_users = db.exec(statement).all()

    if not eligible_users:
        return []

    updated_users_response = []

    # Map legacy/alias doc types to their calificacion field name
    DOC_TYPE_TO_CALIFICACION = {
        "cover_letter": "motivation_letter",  # legacy alias
    }

    for user in eligible_users:
        weighted_sum = 0.0

        interview = db.exec(
            select(Interview).where(
                Interview.user_id == user.id,
                Interview.status == InterviewStatus.passed,
                Interview.grade.isnot(None)
            )
        ).first()

        if interview:
            weighted_sum += interview.grade * calificacion.interview

        documents = db.exec(
            select(Document).where(
                Document.user_id == user.id,
                Document.state == "approved"
            )
        ).all()

        # Track which calificacion fields have already been counted (avoid double-counting)
        counted_fields: set = set()
        for doc in documents:
            doc_type_key = doc.document_type.value if hasattr(doc.document_type, "value") else str(doc.document_type)
            cal_field = DOC_TYPE_TO_CALIFICACION.get(doc_type_key, doc_type_key)
            if cal_field in counted_fields:
                continue
            peso = getattr(calificacion, cal_field, 0)
            if peso > 0:
                # Calificable docs use their grade; non-calificable approved docs count as 10
                nota = doc.grade if doc.grade is not None else 10.0
                weighted_sum += nota * peso
                counted_fields.add(cal_field)

        # Divide by 100 — weights always sum to 100, missing docs contribute 0
        user.final_grade = round(weighted_sum / 100, 2)
        db.add(user)

        roles = db.exec(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user.id)
        ).all()
        
        user_dict = user.model_dump(exclude={'roles'})
        if user_dict.get('rodne_cislo'):
            user_dict['rodne_cislo'] = decrypt_data(user_dict['rodne_cislo'])
            
        user_data = UserPublic.model_validate(user_dict)
        user_data.role = roles[0] if roles else None
        
        updated_users_response.append(user_data)

    db.commit()
    
    return updated_users_response