"""
User model - represents system users.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class User(db.Model):
    """User model for authentication and profile management."""

    __tablename__ = 'User'

    user_id = db.Column(
        'UserID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    role_id = db.Column(
        'RoleID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Role.RoleID',
            name='fk_user_role',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    first_name = db.Column(
        'FirstName',
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        'LastName',
        db.String(50),
        nullable=False
    )

    email = db.Column(
        'Email',
        db.String(255),
        nullable=False,
        unique=True
    )

    phone = db.Column(
        'Phone',
        db.String(15),
        unique=True
    )

    password_hash = db.Column(
        'PasswordHash',
        db.String(255),
        nullable=False
    )

    is_active = db.Column(
        'IsActive',
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        'CreatedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    updated_at = db.Column(
        'UpdatedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp(),
        server_onupdate=db.func.current_timestamp()
    )

    role = db.relationship(
        'Role',
        back_populates='users'
    )

    student = db.relationship(
        'Student',
        back_populates='user',
        uselist=False
    )

    faculty = db.relationship(
        'Faculty',
        back_populates='user',
        uselist=False
    )

    created_subjects = db.relationship(
        'Subject',
        foreign_keys='Subject.created_by',
        back_populates='created_by_user',
        lazy=True
    )

    created_exams = db.relationship(
        'Exam',
        foreign_keys='Exam.created_by',
        back_populates='created_by_user',
        lazy=True
    )

    created_questions = db.relationship(
        'Question',
        foreign_keys='Question.created_by',
        back_populates='created_by_user',
        lazy=True
    )

    notifications = db.relationship(
        'Notification',
        back_populates='user',
        lazy=True
    )

    audit_logs = db.relationship(
        'AuditLog',
        back_populates='user',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(FirstName) <> ''",
            name='chk_user_first_name'
        ),
        db.CheckConstraint(
            "TRIM(LastName) <> ''",
            name='chk_user_last_name'
        ),
        db.CheckConstraint(
            "Email LIKE '%@%'",
            name='chk_user_email'
        ),
        db.Index(
            'idx_user_role',
            'RoleID'
        ),
        db.Index(
            'idx_user_active',
            'IsActive'
        ),
    )

    def __repr__(self) -> str:
        return f'<User {self.email}>'