"""
AuditLog model - represents auditable system activity.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class AuditLog(db.Model):
    """Represents an auditable action performed in the system."""

    __tablename__ = 'AuditLog'

    audit_id = db.Column(
        'AuditID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        'UserID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_audit_user',
            ondelete='SET NULL',
            onupdate='CASCADE'
        )
    )

    action = db.Column(
        'Action',
        db.String(100),
        nullable=False
    )

    entity_type = db.Column(
        'EntityType',
        db.String(50)
    )

    entity_id = db.Column(
        'EntityID',
        BIGINT(unsigned=True)
    )

    details = db.Column(
        'Details',
        db.Text
    )

    ip_address = db.Column(
        'IPAddress',
        db.String(45)
    )

    created_at = db.Column(
        'CreatedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    # User 1 ───── M AuditLog
    user = db.relationship(
        'User',
        back_populates='audit_logs'
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(Action) <> ''",
            name='chk_audit_action'
        ),

        db.Index(
            'idx_audit_user',
            'UserID'
        ),

        db.Index(
            'idx_audit_action',
            'Action'
        ),

        db.Index(
            'idx_audit_entity',
            'EntityType',
            'EntityID'
        ),

        db.Index(
            'idx_audit_created',
            'CreatedAt'
        ),
    )

    def __repr__(self) -> str:
        return f'<AuditLog {self.audit_id}>'