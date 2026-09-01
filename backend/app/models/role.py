"""
Role model - represents system roles.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Role(db.Model):
    """Role model for user role management."""

    __tablename__ = 'Role'

    role_id = db.Column(
        'RoleID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    role_name = db.Column(
        'RoleName',
        db.String(30),
        nullable=False,
        unique=True
    )

    description = db.Column(
        'Description',
        db.String(255)
    )

    is_active = db.Column(
        'IsActive',
        db.Boolean,
        nullable=False,
        default=True
    )

    users = db.relationship(
        'User',
        back_populates='role',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(RoleName) <> ''",
            name='chk_role_name'
        ),
    )

    def __repr__(self) -> str:
        return f'<Role {self.role_name}>'