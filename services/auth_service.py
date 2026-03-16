from sqlmodel import Session, select
from models.user import User
from core.security import verify_password


def authenticate_user(db: Session, rodne_cislo: str, password: str) -> User | None:
    user = db.exec(select(User).where(User.rodne_cislo == rodne_cislo)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
