"""
QuestionOption model - represents options for objective questions.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class QuestionOption(db.Model):
    """Represents an option belonging to a question."""

    __tablename__ = 'QuestionOption'

    option_id = db.Column(
        'OptionID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    question_id = db.Column(
        'QuestionID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Question.QuestionID',
            name='fk_option_question',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    option_text = db.Column(
        'OptionText',
        db.String(500),
        nullable=False
    )

    is_correct = db.Column(
        'IsCorrect',
        db.Boolean,
        nullable=False,
        default=False
    )

    option_order = db.Column(
        'OptionOrder',
        db.Integer,
        nullable=False
    )

    # Question 1 ───── M QuestionOption
    question = db.relationship(
        'Question',
        back_populates='options'
    )

    student_answers = db.relationship(
    'StudentAnswer',
    back_populates='selected_option',
    lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "TRIM(OptionText) <> ''",
            name='chk_option_text'
        ),

        db.CheckConstraint(
            'OptionOrder > 0',
            name='chk_option_order'
        ),

        db.UniqueConstraint(
            'QuestionID',
            'OptionOrder',
            name='uq_question_option_order'
        ),

        db.Index(
            'idx_option_question',
            'QuestionID'
        ),
    )

    def __repr__(self) -> str:
        return f'<QuestionOption {self.option_id}>'