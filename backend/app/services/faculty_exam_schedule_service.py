from datetime import datetime

from app.extensions.database import db
from app.models import Faculty, Exam, ExamSchedule


def create_exam_schedule(
    user_id,
    exam_id,
    start_time,
    end_time,
    room,
    max_attempts,
    is_active
):
    # Verify faculty
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    # Verify exam
    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    # Faculty can only manage own exams
    if exam.created_by != user_id:
        raise ValueError("You can only schedule your own exams.")

    # Parse datetime values
    try:
        start_time = datetime.fromisoformat(start_time)
    except (TypeError, ValueError):
        raise ValueError(
            "start_time must be a valid ISO datetime."
        )

    try:
        end_time = datetime.fromisoformat(end_time)
    except (TypeError, ValueError):
        raise ValueError(
            "end_time must be a valid ISO datetime."
        )

    # Validate time range
    if end_time <= start_time:
        raise ValueError(
            "End time must be after start time."
        )

    # Validate max attempts
    try:
        max_attempts = int(max_attempts)
    except (TypeError, ValueError):
        raise ValueError(
            "Max attempts must be a valid integer."
        )

    if max_attempts <= 0:
        raise ValueError(
            "Max attempts must be greater than zero."
        )

    # Validate room
    if room is not None:
        room = str(room).strip()

        if not room:
            room = None

    # Validate is_active
    if not isinstance(is_active, bool):
        raise ValueError(
            "is_active must be true or false."
        )

    # Prevent overlapping active schedule
    if is_active:
        existing_schedule = ExamSchedule.query.filter_by(
            exam_id=exam_id,
            is_active=True
        ).first()

        if existing_schedule is not None:
            raise ValueError(
                "An active schedule already exists for this exam."
            )

    schedule = ExamSchedule(
        exam_id=exam_id,
        start_time=start_time,
        end_time=end_time,
        room=room,
        max_attempts=max_attempts,
        is_active=is_active
    )

    try:
        db.session.add(schedule)
        db.session.commit()

        return schedule

    except Exception:
        db.session.rollback()
        raise