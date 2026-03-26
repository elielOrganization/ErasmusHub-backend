from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from core.database import get_session
from core.security import create_access_token, get_current_user, decrypt_data 
from models.user import User
from models.role import Role
from models.user_role import UserRole
from schemas.auth_schema import LoginRequest, Token
from schemas.user_schema import UserPublic
from services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_session)):
    user = authenticate_user(db, credentials.rodne_cislo, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="DNI o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    roles = db.exec(
        select(Role)
        .join(UserRole, Role.id == UserRole.role_id)
        .where(UserRole.user_id == user.id)
    ).all()
    role_name = roles[0].name if roles else None

    token = create_access_token(subject=user.id, role=role_name)
    return Token(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    roles = db.exec(select(Role).join(UserRole, Role.id == UserRole.role_id).where(UserRole.user_id == current_user.id)).all()
    user_dict = current_user.model_dump(exclude={'roles'})
    if user_dict.get('rodne_cislo'):
        user_dict['rodne_cislo'] = decrypt_data(user_dict['rodne_cislo'])
        
    user_data = UserPublic.model_validate(user_dict)
    user_data.role = roles[0] if roles else None
    return user_data