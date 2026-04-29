from sqlmodel import Session, select
from models.user import User
from core.security import verify_password, get_deterministic_hash


def _rc_variants(rc: str) -> list[str]:
    """Return both the with-slash and without-slash forms of a rodné číslo."""
    rc = rc.strip()
    rc_clean = rc.replace('/', '').replace(' ', '')

    if '/' in rc:
        # Input already has slash → also try without
        return [rc, rc_clean]
    else:
        # Input has no slash → also try with slash inserted after digit 6
        rc_slash = (rc_clean[:6] + '/' + rc_clean[6:]) if len(rc_clean) >= 6 else rc_clean
        return [rc, rc_slash]


def authenticate_user(db: Session, rodne_cislo: str, password: str) -> User | None:
    if not rodne_cislo:
        return None

    # Try every normalisation variant so users can log in regardless of
    # whether their rodné číslo was stored with or without the slash.
    seen: set[str] = set()
    for candidate in _rc_variants(rodne_cislo):
        if candidate in seen:
            continue
        seen.add(candidate)

        user = db.exec(
            select(User).where(User.rodne_cislo_hash == get_deterministic_hash(candidate))
        ).first()

        if user:
            if not verify_password(password, user.password_hash):
                return None
            return user

    return None