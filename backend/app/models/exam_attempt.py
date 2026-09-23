"""
ExamAttempt model - represents an examination attempt by a student.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class ExamAttempt(db.Model):
    """Represents one attempt made by a student."""

    __tablename__ = 'ExamAttempt'

    attempt_id = db.Column(
        'AttemptID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    registration_id = db.Column(
        'RegistrationID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'CandidateRegistration.RegistrationID',
            name='fk_attempt_registration',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    attempt_number = db.Column(
        'AttemptNumber',
        db.Integer,
        nullable=False
    )

    started_at = db.Column(
        'StartedAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    submitted_at = db.Column(
        'SubmittedAt',
        db.DateTime
    )

    status = db.Column(
        'Status',
        db.String(20),
        nullable=False,
        default='InProgress'
    )

    score = db.Column(
        'Score',
        db.Numeric(8, 2)
    )

    current_adaptive_exam_question_id = db.Column(
        'CurrentAdaptiveExamQuestionID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'ExamQuestion.ExamQuestionID',
            name='fk_attempt_current_adaptive_question',
            ondelete='SET NULL',
            onupdate='CASCADE'
        ),
        nullable=True
    )

    # CandidateRegistration 1 ───── M ExamAttempt
    registration = db.relationship(
        'CandidateRegistration',
        back_populates='attempts'
    )

    # ExamAttempt 1 ───── M StudentAnswer
    answers = db.relationship(
        'StudentAnswer',
        back_populates='attempt',
        lazy=True
    )

    # ExamAttempt 1 ───── 1 Result
    result = db.relationship(
        'Result',
        back_populates='attempt',
        uselist=False
    )


    __table_args__ = (
        db.CheckConstraint(
            'AttemptNumber > 0',
            name='chk_attempt_number'
        ),

        db.CheckConstraint(
            "Status IN ('InProgress', 'Submitted', 'AutoSubmitted')",
            name='chk_attempt_status'
        ),

        db.CheckConstraint(
            'Score IS NULL OR Score >= 0',
            name='chk_attempt_score'
        ),

        db.UniqueConstraint(
            'RegistrationID',
            'AttemptNumber',
            name='uq_registration_attempt'
        ),

        db.Index(
            'idx_attempt_registration',
            'RegistrationID'
        ),

        db.Index(
            'idx_attempt_status',
            'Status'
        ),

        db.Index(
            'idx_attempt_started',
            'StartedAt'
        ),
    )

    def __repr__(self) -> str:
        return f'<ExamAttempt {self.attempt_id}>'