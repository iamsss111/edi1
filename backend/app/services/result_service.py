"""
Result service.

Contains business logic for generating and retrieving
examination results.
"""

from datetime import datetime

from app.extensions.database import db
from app.models import (
    ExamAttempt,
    CandidateRegistration,
    Exam,
    Result,
    Student,
)


def _get_attempt_for_student(
    user_id: int,
    attempt_id: int
) -> ExamAttempt:
    """
    Verify that the examination attempt belongs
    to the authenticated student.
    """

    attempt = ExamAttempt.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if attempt is None:
        raise ValueError(
            "Examination attempt not found."
        )

    registration = CandidateRegistration.query.filter_by(
        registration_id=attempt.registration_id
    ).first()

    if registration is None:
        raise ValueError(
            "Examination registration not found."
        )

    student = Student.query.filter_by(
        student_id=registration.student_id
    ).first()

    if student is None or student.user_id != user_id:
        raise ValueError(
            "You are not authorized to access this result."
        )

    return attempt


def _calculate_grade(percentage: float) -> str:
    """
    Calculate grade from percentage.

    Grade scale:
    90-100 = A+
    80-89  = A
    70-79  = B
    60-69  = C
    50-59  = D
    Below 50 = F
    """

    if percentage >= 90:
        return 'A+'

    if percentage >= 80:
        return 'A'

    if percentage >= 70:
        return 'B'

    if percentage >= 60:
        return 'C'

    if percentage >= 50:
        return 'D'

    return 'F'


def generate_result(
    user_id: int,
    attempt_id: int
) -> Result:
    """
    Generate a result for a completed and evaluated attempt.
    """

    # ------------------------------------------------------------
    # 1. Verify attempt ownership
    # ------------------------------------------------------------

    attempt = _get_attempt_for_student(
        user_id=user_id,
        attempt_id=attempt_id,
    )

    # ------------------------------------------------------------
    # 2. Attempt must be submitted
    # ------------------------------------------------------------

    if attempt.status != 'Submitted':
        raise ValueError(
            "Only submitted examination attempts can have a result."
        )

    # ------------------------------------------------------------
    # 3. Attempt must be evaluated
    # ------------------------------------------------------------

    if attempt.score is None:
        raise ValueError(
            "The examination attempt has not been evaluated yet."
        )

    # ------------------------------------------------------------
    # 4. Get registration
    # ------------------------------------------------------------

    registration = CandidateRegistration.query.filter_by(
        registration_id=attempt.registration_id
    ).first()

    if registration is None:
        raise ValueError(
            "Examination registration not found."
        )

    # ------------------------------------------------------------
    # 5. Get exam
    # ------------------------------------------------------------

    exam = Exam.query.filter_by(
        exam_id=registration.exam_id
    ).first()

    if exam is None:
        raise ValueError(
            "Examination not found."
        )

    # ------------------------------------------------------------
    # 6. Check whether result already exists
    # ------------------------------------------------------------

    existing_result = Result.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if existing_result is not None:
        return existing_result

    # ------------------------------------------------------------
    # 7. Calculate result
    # ------------------------------------------------------------

    total_marks = float(exam.total_marks)
    obtained_marks = float(attempt.score)

    if total_marks <= 0:
        raise ValueError(
            "Examination total marks must be greater than zero."
        )

    percentage = (
        obtained_marks / total_marks
    ) * 100

    grade = _calculate_grade(percentage)

    if obtained_marks >= float(exam.pass_marks):
        result_status = 'Pass'
    else:
        result_status = 'Fail'

    # ------------------------------------------------------------
    # 8. Create result
    # ------------------------------------------------------------

    result = Result(
        attempt_id=attempt_id,
        total_marks=total_marks,
        obtained_marks=obtained_marks,
        percentage=round(percentage, 2),
        grade=grade,
        result_status=result_status,
        published_at=datetime.now(),
    )

    try:
        db.session.add(result)
        db.session.commit()

        return result

    except Exception:
        db.session.rollback()
        raise


def get_result(
    user_id: int,
    attempt_id: int
) -> Result:

    # ------------------------------------------------------------
    # 1. Verify ownership
    # ------------------------------------------------------------

    _get_attempt_for_student(
        user_id=user_id,
        attempt_id=attempt_id,
    )

    # ------------------------------------------------------------
    # 2. Retrieve result
    # ------------------------------------------------------------

    result = Result.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if result is None:
        raise ValueError(
            "Result has not been generated yet."
        )

    return result