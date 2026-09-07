"""
Faculty question service.

Contains business logic for faculty question management.
"""

from app.extensions.database import db
from app.models import Faculty, Question


ALLOWED_QUESTION_TYPES = {
    'MCQ',
    'TrueFalse',
    'ShortAnswer',
    'Descriptive',
}

ALLOWED_DIFFICULTIES = {
    'Easy',
    'Medium',
    'Hard',
}


def create_question(
    user_id: int,
    question_text: str,
    question_type: str,
    marks,
    difficulty: str,
    explanation: str | None,
) -> Question:
    """
    Create a question for the authenticated faculty member.

    Args:
        user_id: ID of the authenticated faculty user.
        question_text: Question content.
        question_type: Type of question.
        marks: Marks assigned to the question.
        difficulty: Question difficulty.
        explanation: Optional explanation.

    Returns:
        Newly created Question instance.

    Raises:
        ValueError: If validation fails or faculty profile is missing.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    if not question_text or not question_text.strip():
        raise ValueError("Question text is required.")

    question_type = str(question_type).strip()

    if question_type not in ALLOWED_QUESTION_TYPES:
        raise ValueError(
            "Question type must be one of: "
            "MCQ, TrueFalse, ShortAnswer, Descriptive."
        )

    try:
        marks = float(marks)
    except (TypeError, ValueError):
        raise ValueError("Marks must be a valid number.")

    if marks <= 0:
        raise ValueError("Marks must be greater than zero.")

    difficulty = str(difficulty).strip()

    if difficulty not in ALLOWED_DIFFICULTIES:
        raise ValueError(
            "Difficulty must be one of: Easy, Medium, Hard."
        )

    if explanation is not None:
        explanation = str(explanation).strip()

        if not explanation:
            explanation = None

    question = Question(
        created_by=user_id,
        question_text=question_text.strip(),
        question_type=question_type,
        marks=marks,
        difficulty=difficulty,
        explanation=explanation,
        is_active=True,
    )

    try:
        db.session.add(question)
        db.session.commit()

        return question

    except Exception:
        db.session.rollback()
        raise


def get_my_questions(user_id):
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    questions = Question.query.filter_by(
        created_by=user_id
    ).order_by(
        Question.question_id.desc()
    ).all()

    return questions