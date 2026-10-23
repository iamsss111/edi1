"""
ExamSchedule model - represents scheduled examination sessions.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class ExamSchedule(db.Model):
    """Represents when an examination is scheduled."""

    __tablename__ = 'ExamSchedule'

    schedule_id = db.Column(
        'ScheduleID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    exam_id = db.Column(
        'ExamID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Exam.ExamID',
            name='fk_schedule_exam',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    start_time = db.Column(
        'StartTime',
        db.DateTime,
        nullable=False
    )

    end_time = db.Column(
        'EndTime',
        db.DateTime,
        nullable=False
    )

    # Optional registration cutoff; faculty schedules default this to end_time
    # so registration stays open throughout the exam window.
    registration_end_time = db.Column(
        'RegistrationEndTime',
        db.DateTime,
        nullable=True
    )

    room = db.Column(
        'Room',
        db.String(50)
    )

    max_attempts = db.Column(
        'MaxAttempts',
        db.Integer,
        nullable=False,
        default=1
    )

    is_active = db.Column(
        'IsActive',
        db.Boolean,
        nullable=False,
        default=True
    )

    # Exam 1 ───── M ExamSchedule
    exam = db.relationship(
        'Exam',
        back_populates='schedules'
    )

    __table_args__ = (
        db.CheckConstraint(
            'EndTime > StartTime',
            name='chk_schedule_time'
        ),

        db.CheckConstraint(
            'MaxAttempts > 0',
            name='chk_schedule_attempts'
        ),

        db.Index(
            'idx_schedule_exam',
            'ExamID'
        ),

        db.Index(
            'idx_schedule_start',
            'StartTime'
        ),

        db.Index(
            'idx_schedule_active',
            'IsActive'
        ),
    )

    def __repr__(self) -> str:
        return f'<ExamSchedule {self.schedule_id}>'
