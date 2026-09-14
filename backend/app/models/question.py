"""
Question model - represents examination questions.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class Question(db.Model):
    """Represents a question created for examinations."""

    __tablename__ = 'Question'

    question_id = db.Column(
        'QuestionID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    created_by = db.Column(
        'CreatedBy',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'User.UserID',
            name='fk_question_created_by',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    subject_id = db.Column(
        'SubjectID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Subject.SubjectID',
            name='fk_question_subject',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    question_text = db.Column(
        'QuestionText',
        db.Text,
        nullable=False
    )

    question_type = db.Column(
        'QuestionType',
        db.String(20),
        nullable=False
    )

    marks = db.Column(
        'Marks',
        db.Numeric(6, 2),
        nullable=False
    )

    difficulty = db.Column(
        'Difficulty',
        db.String(20),
        nullable=False
    )

    explanation = db.Column(
        'Explanation',
        db.Text
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

    # User 1 ───── M Question
    created_by_user = db.relationship(
        'User',
        foreign_keys=[created_by],
        back_populates='created_questions'
    )

    # Question 1 ───── M QuestionOption
    options = db.relationship(
        'QuestionOption',
        back_populates='question',
        lazy=True
    )

    # Question M ───── M Exam through ExamQuestion
    exam_questions = db.relationship(
        'ExamQuestion',
        back_populates='question',
        lazy=True
    )

    subject = db.relationship(
        'Subject',
        back_populates='questions'
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(QuestionText) <> ''",
            name='chk_question_text'
        ),

        db.CheckConstraint(
            "QuestionType IN ('MCQ', 'TrueFalse', 'ShortAnswer', 'Descriptive')",
            name='chk_question_type'
        ),

        db.CheckConstraint(
            'Marks > 0',
            name='chk_question_marks'
        ),

        db.CheckConstraint(
            "Difficulty IN ('Easy', 'Medium', 'Hard')",
            name='chk_question_difficulty'
        ),

        db.Index(
            'idx_question_created_by',
            'CreatedBy'
        ),

        db.Index(
            'idx_question_type',
            'QuestionType'
        ),

        db.Index(
            'idx_question_difficulty',
            'Difficulty'
        ),

        db.Index(
            'idx_question_active',
            'IsActive'
        ),

        db.Index(
            'idx_question_subject',
            'SubjectID'
        ),
    )

    def __repr__(self) -> str:
        return f'<Question {self.question_id}>'