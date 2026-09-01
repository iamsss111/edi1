"""
Result model - represents the final result of an examination attempt.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Result(db.Model):
    """Represents the published result for an examination attempt."""

    __tablename__ = 'Result'

    result_id = db.Column(
        'ResultID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    attempt_id = db.Column(
        'AttemptID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'ExamAttempt.AttemptID',
            name='fk_result_attempt',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False,
        unique=True
    )

    total_marks = db.Column(
        'TotalMarks',
        db.Numeric(8, 2),
        nullable=False
    )

    obtained_marks = db.Column(
        'ObtainedMarks',
        db.Numeric(8, 2),
        nullable=False
    )

    percentage = db.Column(
        'Percentage',
        db.Numeric(5, 2),
        nullable=False
    )

    grade = db.Column(
        'Grade',
        db.String(5)
    )

    result_status = db.Column(
        'ResultStatus',
        db.String(20),
        nullable=False,
        default='Pending'
    )

    published_at = db.Column(
        'PublishedAt',
        db.DateTime
    )

    # ExamAttempt 1 ───── 1 Result
    attempt = db.relationship(
        'ExamAttempt',
        back_populates='result'
    )

    __table_args__ = (
        db.CheckConstraint(
            'TotalMarks >= 0',
            name='chk_result_total_marks'
        ),

        db.CheckConstraint(
            'ObtainedMarks >= 0 AND ObtainedMarks <= TotalMarks',
            name='chk_result_obtained_marks'
        ),

        db.CheckConstraint(
            'Percentage >= 0 AND Percentage <= 100',
            name='chk_result_percentage'
        ),

        db.CheckConstraint(
            "ResultStatus IN ('Pending', 'Pass', 'Fail')",
            name='chk_result_status'
        ),

        db.Index(
            'idx_result_status',
            'ResultStatus'
        ),

        db.Index(
            'idx_result_published',
            'PublishedAt'
        ),
    )

    def __repr__(self) -> str:
        return f'<Result {self.result_id}>'