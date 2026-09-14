"""
Subject model - represents academic subjects.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Subject(db.Model):
    """Academic subject created and managed by faculty."""

    __tablename__ = 'Subject'

    subject_id = db.Column(
        'SubjectID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    department_id = db.Column(
        'DepartmentID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Department.DepartmentID',
            name='fk_subject_department',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    created_by = db.Column(
        'CreatedBy',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_subject_created_by',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    subject_code = db.Column(
        'SubjectCode',
        db.String(30),
        nullable=False,
        unique=True
    )

    subject_name = db.Column(
        'SubjectName',
        db.String(100),
        nullable=False
    )

    description = db.Column(
        'Description',
        db.String(255)
    )

    credits = db.Column(
        'Credits',
        db.Integer,
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

    # Department 1 ───── M Subject
    department = db.relationship(
        'Department',
        back_populates='subjects'
    )

    # User 1 ───── M Subject
    created_by_user = db.relationship(
        'User',
        foreign_keys=[created_by],
        back_populates='created_subjects'
    )

    # Subject 1 ───── M Exam
    exams = db.relationship(
    'Exam',
    back_populates='subject',
    lazy=True
    )

    # Subject 1 ───── M FacultySubject
    faculty_assignments = db.relationship(
        'FacultySubject',
        back_populates='subject',
        lazy=True
    )

    questions = db.relationship(
        'Question',
        back_populates='subject',
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(SubjectCode) <> ''",
            name='chk_subject_code'
        ),

        db.CheckConstraint(
            "TRIM(SubjectName) <> ''",
            name='chk_subject_name'
        ),

        db.CheckConstraint(
            'Credits > 0',
            name='chk_subject_credits'
        ),

        db.Index(
            'idx_subject_department',
            'DepartmentID'
        ),

        db.Index(
            'idx_subject_created_by',
            'CreatedBy'
        ),

        db.Index(
            'idx_subject_active',
            'IsActive'
        ),
    )

    def __repr__(self) -> str:
        return f'<Subject {self.subject_code}>'