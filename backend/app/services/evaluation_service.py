"""
Evaluation service.

Evaluates submitted examination attempts and calculates scores.
"""

from app.extensions.database import db
from app.models import (
    ExamAttempt,
    StudentAnswer,
)


def evaluate_attempt(user_id: int, attempt_id: int) -> ExamAttempt:
    """
    Evaluate a submitted examination attempt.

    Only submitted attempts can be evaluated.
    """

    # ------------------------------------------------------------
    # 1. Find attempt
    # ------------------------------------------------------------

    attempt = ExamAttempt.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if attempt is None:
        raise ValueError(
            "Examination attempt not found."
        )

    # ------------------------------------------------------------
    # 2. Verify ownership
    # ------------------------------------------------------------

    registration = attempt.registration

    if registration is None:
        raise ValueError(
            "Examination registration not found."
        )

    student = registration.student

    if student is None or student.user_id != user_id:
        raise ValueError(
            "You are not authorized to evaluate this attempt."
        )

    # ------------------------------------------------------------
    # 3. Verify submission
    # ------------------------------------------------------------

    if attempt.status != 'Submitted':
        raise ValueError(
            "Only submitted examination attempts can be evaluated."
        )

    # ------------------------------------------------------------
    # 4. Retrieve answers
    # ------------------------------------------------------------

    answers = (
        StudentAnswer.query
        .filter_by(attempt_id=attempt_id)
        .all()
    )

    total_score = 0.0

    # ------------------------------------------------------------
    # 5. Evaluate each answer
    # ------------------------------------------------------------

    for answer in answers:

        exam_question = answer.exam_question

        if exam_question is None:
            continue

        question = exam_question.question

        if question is None:
            continue

        marks = float(exam_question.marks)

        obtained = 0.0

        # --------------------------------------------------------
        # MCQ evaluation
        # --------------------------------------------------------

        if answer.selected_option_id is not None:

            selected_option = next(
                (
                    option
                    for option in question.options
                    if option.option_id == answer.selected_option_id
                ),
                None
            )

            if selected_option is not None:
                if selected_option.is_correct:
                    obtained = marks

        # --------------------------------------------------------
        # Store marks
        # --------------------------------------------------------

        answer.marks_obtained = obtained

        total_score += obtained

    # ------------------------------------------------------------
    # 6. Store total score
    # ------------------------------------------------------------

    attempt.score = total_score

    try:
        db.session.commit()
        return attempt

    except Exception:
        db.session.rollback()
        raise