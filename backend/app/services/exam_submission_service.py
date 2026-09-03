"""
Examination submission service.

Contains business logic for submitting and locking
an examination attempt.
"""

from datetime import datetime

from app.extensions.database import db
from app.models import ExamAttempt


def submit_exam(user_id: int, attempt_id: int) -> ExamAttempt:
    """
    Submit an examination attempt.

    The attempt must:
    - exist
    - belong to the authenticated student
    - currently be InProgress

    Once submitted, the attempt cannot be modified.
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
    # 2. Verify student ownership
    # ------------------------------------------------------------

    registration = attempt.registration

    if registration is None:
        raise ValueError(
            "Examination registration not found."
        )

    student = registration.student

    if student is None or student.user_id != user_id:
        raise ValueError(
            "You are not authorized to submit this attempt."
        )

    # ------------------------------------------------------------
    # 3. Verify attempt status
    # ------------------------------------------------------------

    if attempt.status != 'InProgress':
        raise ValueError(
            "This examination attempt has already been submitted."
        )

    # ------------------------------------------------------------
    # 4. Submit and lock attempt
    # ------------------------------------------------------------

    attempt.status = 'Submitted'
    attempt.submitted_at = datetime.now()

    try:
        db.session.commit()
        return attempt

    except Exception:
        db.session.rollback()
        raise