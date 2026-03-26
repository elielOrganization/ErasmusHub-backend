from sqlmodel import Session, select
from models.user import User
from core.security import verify_password, get_deterministic_hash

def authenticate_user(db: Session, rodne_cislo: str, password: str) -> User | None:
    if not rodne_cislo:
        return None
        
    search_hash = get_deterministic_hash(rodne_cislo)

    user = db.exec(select(User).where(User.rodne_cislo_hash == search_hash)).first()
    
    if not user:
        return None
        
    if not verify_password(password, user.password_hash):
        return None
        
    return user