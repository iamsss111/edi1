"""
Faculty question option service.

Contains business logic for managing question options.
"""

from app.extensions.database import db
from app.models import Faculty, Question, QuestionOption


def create_question_option(
    user_id: int,
    question_id: int,
    option_text: str,
    option_order: int,
    is_correct: bool,
) -> QuestionOption:
    """
    Create an option for a question owned by the authenticated faculty member.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    question = Question.query.filter_by(
        question_id=question_id
    ).first()

    if question is None:
        raise ValueError("Question not found.")

    if question.created_by != user_id:
        raise ValueError(
            "You can only manage options for your own questions."
        )

    if not option_text or not option_text.strip():
        raise ValueError("Option text is required.")

    try:
        option_order = int(option_order)
    except (TypeError, ValueError):
        raise ValueError("Option order must be a valid integer.")

    if option_order <= 0:
        raise ValueError("Option order must be greater than zero.")

    if not isinstance(is_correct, bool):
        raise ValueError("is_correct must be true or false.")

    existing_option = QuestionOption.query.filter_by(
        question_id=question_id,
        option_order=option_order,
    ).first()

    if existing_option is not None:
        raise ValueError(
            "An option with this order already exists for this question."
        )

    option = QuestionOption(
        question_id=question_id,
        option_text=option_text.strip(),
        is_correct=is_correct,
        option_order=option_order,
    )

    try:
        db.session.add(option)
        db.session.commit()

        return option

    except Exception:
        db.session.rollback()
        raise