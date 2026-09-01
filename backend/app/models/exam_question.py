"""
ExamQuestion model - associates questions with examinations.
"""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class ExamQuestion(db.Model):
    """Associates a question with an examination."""

    __tablename__ = 'ExamQuestion'

    exam_question_id = db.Column(
        'ExamQuestionID',
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    exam_id = db.Column(
        'ExamID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Exam.ExamID',
            name='fk_exam_question_exam',
            ondelete='CASCADE',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    question_id = db.Column(
        'QuestionID',
        BIGINT(unsigned=True),
        db.ForeignKey(
            'Question.QuestionID',
            name='fk_exam_question_question',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),
        nullable=False
    )

    question_order = db.Column(
        'QuestionOrder',
        db.Integer,
        nullable=False
    )

    marks = db.Column(
        'Marks',
        db.Numeric(6, 2),
        nullable=False
    )

    # Exam 1 ───── M ExamQuestion
    exam = db.relationship(
        'Exam',
        back_populates='exam_questions'
    )

    # Question 1 ───── M ExamQuestion
    question = db.relationship(
        'Question',
        back_populates='exam_questions'
    )

    student_answers = db.relationship(
    'StudentAnswer',
    back_populates='exam_question',
    lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            'QuestionOrder > 0',
            name='chk_exam_question_order'
        ),

        db.CheckConstraint(
            'Marks > 0',
            name='chk_exam_question_marks'
        ),

        db.UniqueConstraint(
            'ExamID',
            'QuestionOrder',
            name='uq_exam_question_order'
        ),

        db.UniqueConstraint(
            'ExamID',
            'QuestionID',
            name='uq_exam_question'
        ),

        db.Index(
            'idx_exam_question_exam',
            'ExamID'
        ),

        db.Index(
            'idx_exam_question_question',
            'QuestionID'
        ),
    )

    def __repr__(self) -> str:
        return f'<ExamQuestion {self.exam_question_id}>'