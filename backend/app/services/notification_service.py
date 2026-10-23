"""Per-user notification listing and read-state management."""

from datetime import datetime

from app.extensions.database import db
from app.models import Notification


def list_notifications(user_id: int, unread_only: bool = False) -> list[Notification]:
    query = Notification.query.filter_by(user_id=user_id)
    if unread_only:
        query = query.filter_by(is_read=False)
    return query.order_by(Notification.created_at.desc()).all()


def unread_count(user_id: int) -> int:
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def mark_read(user_id: int, notification_id: int) -> Notification:
    notification = Notification.query.filter_by(
        notification_id=notification_id, user_id=user_id
    ).first()
    if notification is None:
        raise LookupError("Notification not found.")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now()
        db.session.commit()
    return notification


def mark_all_read(user_id: int) -> int:
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
    now = datetime.now()
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now
    db.session.commit()
    return len(notifications)


def serialize_notification(notification: Notification) -> dict:
    return {
        "notification_id": notification.notification_id,
        "title": notification.title,
        "message": notification.message,
        "notification_type": notification.notification_type,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "read_at": notification.read_at.isoformat() if notification.read_at else None,
    }
