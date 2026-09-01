"""
CandidateRegistration model - represents a student's registration
for an examination.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class CandidateRegistration(db.Model):
    """Represents a student's registration for an examination."""

    __tablename__ = 'CandidateRegistration'

    registration_id = db.Column(
        'RegistrationID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    exam_id = db.Column(
        'ExamID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Exam.ExamID',
            name='fk_registration_exam',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    student_id = db.Column(
        'StudentID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Student.StudentID',
            name='fk_registration_student',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    registered_at = db.Column(
        'RegisteredAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    status = db.Column(
        'Status',
        db.String(20),
        nullable=False,
        default='Registered'
    )

    # Exam 1 ───── M CandidateRegistration
    exam = db.relationship(
        'Exam',
        back_populates='candidate_registrations'
    )

    # Student 1 ───── M CandidateRegistration
    student = db.relationship(
        'Student',
        back_populates='candidate_registrations'
    )

    attempts = db.relationship(
    'ExamAttempt',
    back_populates='registration',
    lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "Status IN ('Registered', 'Cancelled')",
            name='chk_registration_status'
        ),

        db.UniqueConstraint(
            'ExamID',
            'StudentID',
            name='uq_exam_student_registration'
        ),

        db.Index(
            'idx_registration_exam',
            'ExamID'
        ),

        db.Index(
            'idx_registration_student',
            'StudentID'
        ),

        db.Index(
            'idx_registration_status',
            'Status'
        ),
    )

    def __repr__(self) -> str:
        return f'<CandidateRegistration {self.registration_id}>'