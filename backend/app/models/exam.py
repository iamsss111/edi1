"""
Exam model - represents examinations created by faculty.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Exam(db.Model):
    """Represents an examination."""

    __tablename__ = 'Exam'

    exam_id = db.Column(
        'ExamID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    subject_id = db.Column(
        'SubjectID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Subject.SubjectID',
            name='fk_exam_subject',
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
            name='fk_exam_created_by',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    title = db.Column(
        'Title',
        db.String(150),
        nullable=False
    )

    description = db.Column(
        'Description',
        db.String(255)
    )

    duration_minutes = db.Column(
        'DurationMinutes',
        db.Integer,
        nullable=False
    )

    total_marks = db.Column(
        'TotalMarks',
        db.Numeric(8, 2),
        nullable=False
    )

    pass_marks = db.Column(
        'PassMarks',
        db.Numeric(8, 2),
        nullable=False
    )

    status = db.Column(
        'Status',
        db.String(20),
        nullable=False,
        default='Draft'
    )

    instructions = db.Column(
        'Instructions',
        db.Text
    )

    adaptive_enabled = db.Column(
        'AdaptiveEnabled',
        db.Boolean,
        nullable=False,
        default=False,
        server_default='0'
    )

    initial_difficulty = db.Column(
        'InitialDifficulty',
        db.String(20),
        nullable=False,
        default='Medium',
        server_default='Medium'
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

    # Subject 1 ───── M Exam
    subject = db.relationship(
        'Subject',
        back_populates='exams'
    )

    # User 1 ───── M Exam
    created_by_user = db.relationship(
        'User',
        foreign_keys=[created_by],
        back_populates='created_exams'
    )

    # Exam 1 ───── M ExamSchedule
    schedules = db.relationship(
        'ExamSchedule',
        back_populates='exam',
        lazy=True
    )

    # Exam M ───── M Question through ExamQuestion
    exam_questions = db.relationship(
        'ExamQuestion',
        back_populates='exam',
        lazy=True
    )

    candidate_registrations = db.relationship(
    'CandidateRegistration',
    back_populates='exam',
    lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(Title) <> ''",
            name='chk_exam_title'
        ),

        db.CheckConstraint(
            'DurationMinutes > 0',
            name='chk_exam_duration'
        ),

        db.CheckConstraint(
            'TotalMarks > 0',
            name='chk_exam_total_marks'
        ),

        db.CheckConstraint(
            'PassMarks >= 0 AND PassMarks <= TotalMarks',
            name='chk_exam_pass_marks'
        ),

        db.CheckConstraint(
            "Status IN ('Draft', 'Published', 'Completed', 'Cancelled')",
            name='chk_exam_status'
        ),

        db.CheckConstraint(
            "InitialDifficulty IN ('Easy', 'Medium', 'Hard')",
            name='chk_exam_initial_difficulty'
        ),

        db.Index(
            'idx_exam_subject',
            'SubjectID'
        ),

        db.Index(
            'idx_exam_created_by',
            'CreatedBy'
        ),

        db.Index(
            'idx_exam_status',
            'Status'
        ),
    )

    def __repr__(self) -> str:
        return f'<Exam {self.title}>'