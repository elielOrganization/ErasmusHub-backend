import os
import bcrypt
import hmac
import hashlib
from cryptography.fernet import Fernet
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from core.database import get_session
from models.user import User

SECRET_KEY = os.getenv("SECRET_KEY", "tu_jwt_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key() 

cipher_suite = Fernet(ENCRYPTION_KEY)
HMAC_SECRET_KEY = os.getenv("HMAC_SECRET_KEY", "llave-secreta-para-hash").encode('utf-8')


def encrypt_data(data: str) -> str:
    if not data: return data
    return cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data: return encrypted_data
    try:
        return cipher_suite.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    except Exception:
        return encrypted_data

def get_deterministic_hash(data: str) -> str:
    if not data: return data
    return hmac.new(HMAC_SECRET_KEY, data.encode('utf-8'), hashlib.sha256).hexdigest()

# --- FUNCIONES PARA LA CONTRASEÑA Y TOKENS ---
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(subject: Union[str, Any], role: str | None = None) -> str:
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": now_utc,
    }

    # Include the role in the token so the frontend can use it without
    # calling /auth/me on every render. The backend still validates the token
    # against the database on critical routes.
    if role is not None:
        to_encode["role"] = role

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_session),
) -> Optional[User]:
    """Like get_current_user but returns None instead of raising when unauthenticated."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return db.get(User, int(user_id))
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user
