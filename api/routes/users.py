from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from models.user import User
from models.role import Role
from models.user_role import UserRole
from schemas.user_schema import UserCreate, UserPublic, UserUpdate
from core.database import get_session
from core.security import get_password_hash

router = APIRouter(tags=["Users"])


@router.post("/users/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    existing_user = db.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_in.rodne_cislo:
        existing_dni = db.exec(select(User).where(User.rodne_cislo == user_in.rodne_cislo)).first()
        if existing_dni:
            raise HTTPException(status_code=400, detail="DNI already registered")
        

    db_user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password_hash=get_password_hash(user_in.password),
        rodne_cislo=user_in.rodne_cislo,
        birth_date=user_in.birth_date,
        address=user_in.address,
        phone=user_in.phone,
        is_minor=user_in.is_minor,
    )

    db.add(db_user)
    db.flush()

    if user_in.is_minor:
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
    
    # Load roles for the response
    roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == db_user.id)).all()
    user_data = UserPublic.model_validate(db_user.model_dump(exclude={'roles'}))
    user_data.roles = roles
    return user_data


@router.get("/users/", response_model=List[UserPublic])
def read_users(db: Session = Depends(get_session)):
    users = db.exec(select(User)).all()
    user_publics = []
    for user in users:
        roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == user.id)).all()
        user_data = UserPublic.model_validate(user.model_dump(exclude={'roles'}))
        user_data.roles = roles
        user_publics.append(user_data)
    return user_publics


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_session)):
    db_user = db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)

    if "password" in update_data:
        password = update_data.pop("password")
        db_user.password_hash = get_password_hash(password)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == db_user.id)).all()
    user_data = UserPublic.model_validate(db_user.model_dump(exclude={'roles'}))
    user_data.roles = roles
    return user_data
