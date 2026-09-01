"""
Notification model - represents notifications sent to users.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Notification(db.Model):
    """Represents a notification belonging to a user."""

    __tablename__ = 'Notification'

    notification_id = db.Column(
        'NotificationID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        'UserID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_notification_user',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    title = db.Column(
        'Title',
        db.String(150),
        nullable=False
    )

    message = db.Column(
        'Message',
        db.Text,
        nullable=False
    )

    notification_type = db.Column(
        'NotificationType',
        db.String(30),
        nullable=False
    )

    is_read = db.Column(
        'IsRead',
        db.Boolean,
        nullable=False,
        default=False
    )

    created_at = db.Column(
        'CreatedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    read_at = db.Column(
        'ReadAt',
        db.DateTime
    )

    # User 1 ───── M Notification
    user = db.relationship(
        'User',
        back_populates='notifications'
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(Title) <> ''",
            name='chk_notification_title'
        ),

        db.CheckConstraint(
            "TRIM(Message) <> ''",
            name='chk_notification_message'
        ),

        db.Index(
            'idx_notification_user',
            'UserID'
        ),

        db.Index(
            'idx_notification_read',
            'IsRead'
        ),

        db.Index(
            'idx_notification_created',
            'CreatedAt'
        ),
    )

    def __repr__(self) -> str:
        return f'<Notification {self.notification_id}>'