"""
Student model - represents student-specific information.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Student(db.Model):
    """Represents a student in the examination system."""

    __tablename__ = 'Student'

    student_id = db.Column(
        'StudentID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        'UserID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_student_user',
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
            name='fk_student_department',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    roll_number = db.Column(
        'RollNumber',
        db.String(30),
        nullable=False,
        unique=True
    )

    enrollment_number = db.Column(
        'EnrollmentNumber',
        db.String(30),
        nullable=False,
        unique=True
    )

    year = db.Column(
        'Year',
        db.SmallInteger,
        nullable=False
    )

    semester = db.Column(
        'Semester',
        db.SmallInteger,
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

    user = db.relationship(
        'User',
        back_populates='student'
    )

    department = db.relationship(
        'Department',
        back_populates='students'
    )

    candidate_registrations = db.relationship(
        'CandidateRegistration',
        back_populates='student',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(RollNumber) <> ''",
            name='chk_student_roll'
        ),

        db.CheckConstraint(
            "TRIM(EnrollmentNumber) <> ''",
            name='chk_student_enrollment'
        ),

        db.CheckConstraint(
            'Year > 0',
            name='chk_student_year'
        ),

        db.CheckConstraint(
            'Semester > 0',
            name='chk_student_semester'
        ),

        db.Index(
            'idx_student_department',
            'DepartmentID'
        ),
    )

    def __repr__(self) -> str:
        return f'<Student {self.enrollment_number}>'