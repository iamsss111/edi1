"""
StudentAnswer model - represents an answer submitted by a student
during an examination attempt.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class StudentAnswer(db.Model):
    """Represents a student's answer to an examination question."""

    __tablename__ = 'StudentAnswer'

    answer_id = db.Column(
        'AnswerID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    attempt_id = db.Column(
        'AttemptID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'ExamAttempt.AttemptID',
            name='fk_answer_attempt',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    exam_question_id = db.Column(
        'ExamQuestionID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'ExamQuestion.ExamQuestionID',
            name='fk_answer_exam_question',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    selected_option_id = db.Column(
        'SelectedOptionID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'QuestionOption.OptionID',
            name='fk_answer_option',
            ondelete='SET NULL',
            onupdate='CASCADE'
        )
    )

    answer_text = db.Column(
        'AnswerText',
        db.Text
    )

    marks_obtained = db.Column(
        'MarksObtained',
        db.Numeric(6, 2)
    )

    answered_at = db.Column(
        'AnsweredAt',
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    # ExamAttempt 1 ───── M StudentAnswer
    attempt = db.relationship(
        'ExamAttempt',
        back_populates='answers'
    )

    # ExamQuestion 1 ───── M StudentAnswer
    exam_question = db.relationship(
        'ExamQuestion',
        back_populates='student_answers'
    )

    # QuestionOption 1 ───── M StudentAnswer
    selected_option = db.relationship(
        'QuestionOption',
        back_populates='student_answers'
    )

    __table_args__ = (
        db.CheckConstraint(
            'MarksObtained IS NULL OR MarksObtained >= 0',
            name='chk_answer_marks'
        ),

        db.UniqueConstraint(
            'AttemptID',
            'ExamQuestionID',
            name='uq_attempt_exam_question_answer'
        ),

        db.Index(
            'idx_answer_attempt',
            'AttemptID'
        ),

        db.Index(
            'idx_answer_exam_question',
            'ExamQuestionID'
        ),

        db.Index(
            'idx_answer_option',
            'SelectedOptionID'
        ),
    )

    def __repr__(self) -> str:
        return f'<StudentAnswer {self.answer_id}>'