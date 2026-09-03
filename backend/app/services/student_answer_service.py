"""
Student answer service.

Contains business logic for saving, updating, and retrieving
answers submitted by a student during an examination attempt.
"""

from app.extensions.database import db
from app.models import (
    ExamAttempt,
    ExamQuestion,
    StudentAnswer,
)


def _get_attempt_for_student(user_id: int, attempt_id: int) -> ExamAttempt:
    """
    Verify that the attempt belongs to the authenticated student.
    """

    attempt = (
        ExamAttempt.query
        .join(ExamAttempt.registration)
        .join(ExamAttempt.registration.property.mapper.class_.student)
        .filter(
            ExamAttempt.attempt_id == attempt_id,
        )
        .first()
    )

    if attempt is None:
        raise ValueError("Examination attempt not found.")

    student = attempt.registration.student

    if student is None or student.user_id != user_id:
        raise ValueError("You are not authorized to access this attempt.")

    return attempt


def save_answer(
    user_id: int,
    attempt_id: int,
    exam_question_id: int,
    selected_option_id: int | None = None,
    answer_text: str | None = None,
) -> StudentAnswer:

    attempt = _get_attempt_for_student(
        user_id=user_id,
        attempt_id=attempt_id,
    )

    if attempt.status != 'InProgress':
        raise ValueError(
            "Answers cannot be changed after the examination is submitted."
        )

    exam_question = ExamQuestion.query.filter_by(
        exam_question_id=exam_question_id,
        exam_id=attempt.registration.exam_id,
    ).first()

    if exam_question is None:
        raise ValueError(
            "Question does not belong to this examination."
        )

    # ------------------------------------------------------------
    # Validate selected option
    # ------------------------------------------------------------

    if selected_option_id is not None:

        option = next(
            (
                option
                for option in exam_question.question.options
                if option.option_id == selected_option_id
            ),
            None
        )

        if option is None:
            raise ValueError(
                "Selected option does not belong to this question."
            )

    # ------------------------------------------------------------
    # Find existing answer
    # ------------------------------------------------------------

    answer = StudentAnswer.query.filter_by(
        attempt_id=attempt_id,
        exam_question_id=exam_question_id,
    ).first()

    # ------------------------------------------------------------
    # Update existing answer
    # ------------------------------------------------------------

    if answer is not None:

        answer.selected_option_id = selected_option_id
        answer.answer_text = answer_text
        answer.marks_obtained = None

    # ------------------------------------------------------------
    # Create new answer
    # ------------------------------------------------------------

    else:

        answer = StudentAnswer(
            attempt_id=attempt_id,
            exam_question_id=exam_question_id,
            selected_option_id=selected_option_id,
            answer_text=answer_text,
            marks_obtained=None,
        )

        db.session.add(answer)

    try:
        db.session.commit()
        return answer

    except Exception:
        db.session.rollback()
        raise


def get_answers(
    user_id: int,
    attempt_id: int,
) -> list:

    attempt = _get_attempt_for_student(
        user_id=user_id,
        attempt_id=attempt_id,
    )

    answers = (
        StudentAnswer.query
        .filter_by(attempt_id=attempt.attempt_id)
        .order_by(StudentAnswer.exam_question_id.asc())
        .all()
    )

    result = []

    for answer in answers:

        result.append({
            'answer_id': answer.answer_id,
            'exam_question_id': answer.exam_question_id,
            'selected_option_id': answer.selected_option_id,
            'answer_text': answer.answer_text,
            'marks_obtained': (
                float(answer.marks_obtained)
                if answer.marks_obtained is not None
                else None
            ),
            'answered_at': (
                answer.answered_at.isoformat()
                if answer.answered_at
                else None
            ),
        })

    return result