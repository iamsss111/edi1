"""
Faculty model - represents faculty members in the system.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Faculty(db.Model):
    """Faculty profile associated with a User account."""

    __tablename__ = 'Faculty'

    faculty_id = db.Column(
        'FacultyID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        'UserID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_faculty_user',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False,
        unique=True
    )

    department_id = db.Column(
        'DepartmentID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Department.DepartmentID',
            name='fk_faculty_department',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    employee_number = db.Column(
        'EmployeeNumber',
        db.String(30),
        nullable=False,
        unique=True
    )

    designation = db.Column(
        'Designation',
        db.String(100),
        nullable=False
    )

    # User 1 ───── 1 Faculty
    user = db.relationship(
        'User',
        back_populates='faculty'
    )

    # Department 1 ───── M Faculty
    department = db.relationship(
        'Department',
        back_populates='faculties'
    )

    # Faculty 1 ───── M FacultySubject
    subject_assignments = db.relationship(
        'FacultySubject',
        back_populates='faculty',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(EmployeeNumber) <> ''",
            name='chk_faculty_employee'
        ),

        db.CheckConstraint(
            "TRIM(Designation) <> ''",
            name='chk_faculty_designation'
        ),

        db.Index(
            'idx_faculty_department',
            'DepartmentID'
        ),
    )

    def __repr__(self) -> str:
        return f'<Faculty {self.employee_number}>'