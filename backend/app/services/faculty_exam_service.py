"""
Faculty exam service.

Handles exam creation and retrieval for faculty members.
Faculty can only create and manage exams for subjects
currently assigned to them through FacultySubject.
"""

from app.extensions.database import db
from app.models import (
    Faculty,
    FacultySubject,
    Subject,
    Exam,
    Result,
    ExamAttempt,
    CandidateRegistration,
)


ALLOWED_STATUSES = {
    'Draft',
    'Published',
    'Completed',
    'Cancelled'
}


def create_exam(
    user_id: int,
    subject_id: int,
    title: str,
    duration_minutes,
    total_marks,
    pass_marks
) -> Exam:
    """
    Create an exam for a subject currently assigned
    to the authenticated faculty member.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid subject_id.")

    subject = Subject.query.filter_by(subject_id=subject_id).first()

    if subject is None:
        raise ValueError("Subject not found.")

    # Faculty may only create exams for subjects
    # currently assigned to them.
    assignment = FacultySubject.query.filter_by(
        faculty_id=faculty.faculty_id,
        subject_id=subject_id,
        is_active=True
    ).first()

    if assignment is None:
        raise ValueError(
            "You can only create exams for subjects currently assigned to you."
        )

    if not title or not str(title).strip():
        raise ValueError("Exam title is required.")

    title = str(title).strip()

    try:
        duration_minutes = int(duration_minutes)
    except (TypeError, ValueError):
        raise ValueError("Duration must be a valid integer.")

    if duration_minutes <= 0:
        raise ValueError("Duration must be greater than 0 minutes.")

    try:
        total_marks = float(total_marks)
    except (TypeError, ValueError):
        raise ValueError("Total marks must be a valid number.")

    if total_marks <= 0:
        raise ValueError("Total marks must be greater than 0.")

    try:
        pass_marks = float(pass_marks)
    except (TypeError, ValueError):
        raise ValueError("Pass marks must be a valid number.")

    if pass_marks < 0:
        raise ValueError("Pass marks cannot be negative.")

    if pass_marks > total_marks:
        raise ValueError(
            "Pass marks cannot be greater than total marks."
        )

    exam = Exam(
        subject_id=subject_id,
        created_by=user_id,
        title=title,
        duration_minutes=duration_minutes,
        total_marks=total_marks,
        pass_marks=pass_marks,
        status='Draft'
    )

    try:
        db.session.add(exam)
        db.session.commit()

        return exam

    except Exception:
        db.session.rollback()
        raise


def get_my_exams(user_id: int):
    """
    Retrieve exams created by the authenticated faculty member.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    return (
        Exam.query
        .filter_by(created_by=user_id)
        .order_by(Exam.exam_id.desc())
        .all()
    )


def get_exam_details(user_id: int, exam_id: int):
    """
    Retrieve details of an exam created by the authenticated faculty member.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    if exam.created_by != user_id:
        raise ValueError(
            "You can only access exams created by you."
        )

    return exam


def get_exam_results(user_id: int, exam_id: int):
    """
    Retrieve results for an exam created by the authenticated faculty member.
    """

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    if exam.created_by != user_id:
        raise ValueError(
            "You can only access results for your own exams."
        )

    results = (
        db.session.query(Result, ExamAttempt, CandidateRegistration)
        .join(
            ExamAttempt,
            Result.attempt_id == ExamAttempt.attempt_id
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id
            == CandidateRegistration.registration_id
        )
        .filter(
            CandidateRegistration.exam_id == exam_id
        )
        .all()
    )

    return exam, results