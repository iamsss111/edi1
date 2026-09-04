"""
Exam attempt service.

Contains business logic for starting and managing examination attempts.
"""

from datetime import datetime, timedelta

from app.extensions.database import db
from app.models import (
    Student,
    Exam,
    ExamSchedule,
    CandidateRegistration,
    ExamAttempt,
)


def start_exam(user_id: int, exam_id: int) -> ExamAttempt:
    """
    Start an examination for an authenticated student.

    Args:
        user_id: Authenticated UserID.
        exam_id: Examination ID.

    Returns:
        Existing in-progress ExamAttempt or newly created ExamAttempt.

    Raises:
        ValueError: If the student cannot start the examination.
    """

    # Find student profile associated with authenticated user.
    student = Student.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()

    if student is None:
        raise ValueError("Student profile not found or inactive.")

    # Find examination.
    exam = Exam.query.filter_by(
        exam_id=exam_id
    ).first()

    if exam is None:
        raise ValueError("Examination not found.")

    # Only published examinations can be started.
    if exam.status != 'Published':
        raise ValueError("This examination is not available.")

    # Find active registration for this student and examination.
    registration = CandidateRegistration.query.filter_by(
        exam_id=exam_id,
        student_id=student.student_id,
        status='Registered'
    ).first()

    if registration is None:
        raise ValueError(
            "You are not registered for this examination."
        )

    # Current server time.
    now = datetime.now()

    # Find an active schedule currently allowing the examination.
    schedule = (
        ExamSchedule.query
        .filter(
            ExamSchedule.exam_id == exam_id,
            ExamSchedule.is_active.is_(True),
            ExamSchedule.start_time <= now,
            ExamSchedule.end_time >= now,
        )
        .order_by(ExamSchedule.start_time.asc())
        .first()
    )

    if schedule is None:
        raise ValueError(
            "The examination is not currently scheduled."
        )

    # Check whether an attempt is already in progress.
    existing_attempt = (
        ExamAttempt.query
        .filter_by(
            registration_id=registration.registration_id,
            status='InProgress'
        )
        .order_by(ExamAttempt.attempt_number.desc())
        .first()
    )

    if existing_attempt is not None:
        expiry_time = (
        existing_attempt.started_at
        + timedelta(minutes=exam.duration_minutes)
        )

        if now >= expiry_time:
            existing_attempt.status = 'AutoSubmitted'
            existing_attempt.submitted_at = now

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

            raise ValueError(
                "The examination time has expired."
            )

        return existing_attempt

    # Count all attempts made for this registration.
    attempt_count = ExamAttempt.query.filter_by(
        registration_id=registration.registration_id
    ).count()

    if attempt_count >= schedule.max_attempts:
        raise ValueError(
            "Maximum number of examination attempts has been reached."
        )

    # Attempt numbers start at 1.
    attempt_number = attempt_count + 1

    attempt = ExamAttempt(
        registration_id=registration.registration_id,
        attempt_number=attempt_number,
        status='InProgress',
    )

    try:
        db.session.add(attempt)
        db.session.commit()

        return attempt

    except Exception:
        db.session.rollback()
        raise