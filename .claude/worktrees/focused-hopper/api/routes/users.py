from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

# Importamos el Modelo (DB) y los Schemas (Validación)
from models.user import Usuario
from schemas.user_schema import UserCreate, UserPublic, UserUpdate
from core.database import get_session
# Imaginemos que tienes esta función para encriptar
from core.security import get_password_hash 

router = APIRouter(prefix="/users", tags=["Users"])

# --- CREAR USUARIO ---
@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_session)):
    # 1. Verificar si ya existe el email
    existing_user = db.exec(select(Usuario).where(Usuario.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # 2. Convertir Schema -> Model (y hashear password)
    db_user = Usuario(
        email=user_in.email,
        nombre=user_in.nombre,
        apellidos=user_in.apellidos,
        password_hash=get_password_hash(user_in.password) # Guardamos el hash, no la plana
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user # FastAPI lo filtra usando UserPublic automáticamente

# --- LEER USUARIOS ---
@router.get("/", response_model=List[UserPublic])
def read_users(db: Session = Depends(get_session)):
    users = db.exec(select(Usuario)).all()
    return users

# --- ACTUALIZAR USUARIO ---
@router.patch("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_session)):
    db_user = db.get(Usuario, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Extraer solo los datos enviados (evita sobreescribir con None)
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        password = update_data.pop("password")
        db_user.password_hash = get_password_hash(password)

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user