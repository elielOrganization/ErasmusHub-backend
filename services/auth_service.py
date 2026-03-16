from sqlmodel import Session, select
from models.user import User
from core.security import verify_password


<<<<<<< Updated upstream
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.exec(select(User).where(User.email == email)).first()
=======
def authenticate_user(db: Session, rodne_cislo: str, password: str) -> Usuario | None:
    user = db.exec(select(Usuario).where(Usuario.rodne_cislo == rodne_cislo)).first()
>>>>>>> Stashed changes
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
