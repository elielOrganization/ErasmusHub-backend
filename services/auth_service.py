from sqlmodel import Session, select
from models.user import Usuario
from core.security import verify_password


def authenticate_user(db: Session, email: str, password: str) -> Usuario | None:
    user = db.exec(select(Usuario).where(Usuario.email == email)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
