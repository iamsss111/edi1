from app.extensions.database import db
from app.models import Faculty, Subject, Exam, ExamAttempt, CandidateRegistration, Result


ALLOWED_STATUSES = {
    'Draft',
    'Published',
    'Completed',
    'Cancelled'
}


def create_exam(
    user_id,
    subject_id,
    title,
    description,
    duration_minutes,
    total_marks,
    pass_marks,
    instructions
):
    # Verify faculty profile
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    # Verify subject
    subject = Subject.query.filter_by(subject_id=subject_id).first()

    if subject is None:
        raise ValueError("Subject not found.")

    # Faculty can only create exams for their department
    if subject.department_id != faculty.department_id:
        raise ValueError("You can only create exams for subjects in your department.")

    # Basic validation
    if not title or not title.strip():
        raise ValueError("Exam title is required.")

    try:
        duration_minutes = int(duration_minutes)
    except (TypeError, ValueError):
        raise ValueError("Duration must be a valid integer.")

    if duration_minutes <= 0:
        raise ValueError("Duration must be greater than zero.")

    try:
        total_marks = float(total_marks)
    except (TypeError, ValueError):
        raise ValueError("Total marks must be a valid number.")

    if total_marks <= 0:
        raise ValueError("Total marks must be greater than zero.")

    try:
        pass_marks = float(pass_marks)
    except (TypeError, ValueError):
        raise ValueError("Pass marks must be a valid number.")

    if pass_marks < 0:
        raise ValueError("Pass marks cannot be negative.")

    if pass_marks > total_marks:
        raise ValueError("Pass marks cannot exceed total marks.")

    # Create exam
    exam = Exam(
        subject_id=subject_id,
        created_by=user_id,
        title=title.strip(),
        description=description,
        duration_minutes=duration_minutes,
        total_marks=total_marks,
        pass_marks=pass_marks,
        status='Draft',
        instructions=instructions
    )

    try:
        db.session.add(exam)
        db.session.commit()

        return exam

    except Exception:
        db.session.rollback()
        raise


def get_my_exams(user_id):
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    exams = Exam.query.filter_by(
        created_by=user_id
    ).order_by(
        Exam.exam_id.desc()
    ).all()

    return exams


def get_exam_details(user_id, exam_id):
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    exam = Exam.query.filter_by(
        exam_id=exam_id,
        created_by=user_id
    ).first()

    if exam is None:
        raise ValueError("Exam not found or you do not have access to it.")

    return exam


def get_exam_results(user_id, exam_id):
    faculty = Faculty.query.filter_by(
        user_id=user_id
    ).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    exam = Exam.query.filter_by(
        exam_id=exam_id,
        created_by=user_id
    ).first()

    if exam is None:
        raise ValueError(
            "Exam not found or you do not have access to it."
        )

    results = (
        Result.query
        .join(
            ExamAttempt,
            Result.attempt_id == ExamAttempt.attempt_id
        )
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id ==
            CandidateRegistration.registration_id
        )
        .filter(
            CandidateRegistration.exam_id == exam_id
        )
        .order_by(
            Result.result_id.desc()
        )
        .all()
    )

    return exam, results