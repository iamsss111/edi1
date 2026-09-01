"""
Department model - represents academic departments.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Department(db.Model):
    """Department model for managing academic departments."""

    __tablename__ = 'Department'

    department_id = db.Column(
        'DepartmentID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    department_code = db.Column(
        'DepartmentCode',
        db.String(20),
        nullable=False,
        unique=True
    )

    department_name = db.Column(
        'DepartmentName',
        db.String(100),
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

    created_at = db.Column(
        'CreatedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    students = db.relationship(
        'Student',
        back_populates='department',
        lazy=True
    )

    faculties = db.relationship(
        'Faculty',
        back_populates='department',
        lazy=True
    )

    subjects = db.relationship(
        'Subject',
        back_populates='department',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(DepartmentCode) <> ''",
            name='chk_department_code'
        ),
        db.CheckConstraint(
            "TRIM(DepartmentName) <> ''",
            name='chk_department_name'
        ),
        db.Index(
            'idx_department_active',
            'IsActive'
        ),
    )

    def __repr__(self) -> str:
        return f'<Department {self.department_name}>'