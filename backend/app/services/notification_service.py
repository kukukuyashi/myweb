from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    user_id: int,
    actor_id: int | None,
    type: str,
    thread_id: int | None = None,
    reply_id: int | None = None,
) -> Notification | None:
    """写入一条站内通知。给自己触发的动作跳过。"""
    if actor_id is not None and actor_id == user_id:
        return None
    note = Notification(
        user_id=user_id,
        actor_id=actor_id,
        type=type,
        thread_id=thread_id,
        reply_id=reply_id,
    )
    db.add(note)
    return note