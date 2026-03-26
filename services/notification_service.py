import json
from sqlmodel import Session
from models.notification import Notification
from models.user import User
from sqlmodel import select


def create_notification(
    db: Session,
    user_id: int,
    message_key: str,
    notif_type: str,
    params: dict | None = None,
) -> Notification:
    """
    Create and persist a notification.

    Args:
        db:           Active DB session.
        user_id:      Recipient user ID.
        message_key:  Translation key (e.g. "app_accepted", "task_due_soon").
                      Must exist in messages/<locale>.json under avisos.messages.
        notif_type:   One of: "application_update", "task_reminder", "weekly_digest".
        params:       Optional dict of template variables, e.g. {"university": "Praga"}.
    """
    notif = Notification(
        user_id=user_id,
        message_key=message_key,
        params=json.dumps(params) if params else None,
        type=notif_type,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

def notify_all_users_service(db: Session, message_key: str, notif_type: str, params: dict | None = None):
    """
    Obtiene todos los usuarios y crea una notificación para cada uno.
    """
    # 1. Obtener todos los IDs de usuarios activos
    users = db.exec(select(User)).all()
    
    # 2. Crear las notificaciones
    for user in users:
        # Reutilizamos tu lógica existente
        create_notification(
            db=db,
            user_id=user.id,
            message_key=message_key,
            notif_type=notif_type,
            params=params
        )