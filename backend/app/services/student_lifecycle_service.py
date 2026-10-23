"""Student-facing registration and published-result workflows."""

from datetime import datetime

from app.extensions.database import db
from app.models import (
    CandidateRegistration,
    Exam,
    ExamAttempt,
    ExamQuestion,
    ExamSchedule,
    Result,
    Student,
    FacultySubject,
    StudentSubjectEnrollment,
)


def _student_for_user(user_id: int) -> Student:
    student = Student.query.filter_by(user_id=user_id, is_active=True).first()
    if student is None:
        raise ValueError("Active student profile not found.")
    return student


def available_subjects(user_id: int) -> list[dict]:
    student = _student_for_user(user_id)
    assignments = (
        FacultySubject.query.join(FacultySubject.subject)
        .join(FacultySubject.faculty)
        .filter(
            FacultySubject.is_active.is_(True),
            FacultySubject.semester == student.semester,
            FacultySubject.subject.has(department_id=student.department_id, is_active=True),
        )
        .order_by(FacultySubject.subject_id, FacultySubject.year.desc(), FacultySubject.faculty_subject_id)
        .all()
    )
    enrolled = {
        row.faculty_subject_id
        for row in StudentSubjectEnrollment.query.filter_by(student_id=student.student_id, is_active=True).all()
    }
    return [
        {
            "faculty_subject_id": assignment.faculty_subject_id,
            "subject_id": assignment.subject.subject_id,
            "subject_code": assignment.subject.subject_code,
            "subject_name": assignment.subject.subject_name,
            "description": assignment.subject.description,
            "credits": assignment.subject.credits,
            "semester": assignment.semester,
            "academic_year": assignment.year,
            "faculty": {
                "faculty_id": assignment.faculty.faculty_id,
                "name": f"{assignment.faculty.user.first_name} {assignment.faculty.user.last_name}".strip(),
                "designation": assignment.faculty.designation,
            },
            "is_enrolled": assignment.faculty_subject_id in enrolled,
        }
        for assignment in assignments
        if assignment.faculty.user.is_active
    ]


def enroll_in_subject(user_id: int, faculty_subject_id: int) -> StudentSubjectEnrollment:
    student = _student_for_user(user_id)
    assignment = FacultySubject.query.filter_by(
        faculty_subject_id=faculty_subject_id, is_active=True
    ).first()
    if assignment is None or not assignment.subject.is_active or not assignment.faculty.user.is_active:
        raise LookupError("Active subject offering not found.")
    if assignment.subject.department_id != student.department_id or assignment.semester != student.semester:
        raise ValueError("This subject offering is not available for your department and semester.")
    existing = StudentSubjectEnrollment.query.filter_by(
        student_id=student.student_id, faculty_subject_id=assignment.faculty_subject_id
    ).first()
    if existing:
        if existing.is_active:
            raise ValueError("You are already enrolled in this subject.")
        existing.is_active = True
        enrollment = existing
    else:
        enrollment = StudentSubjectEnrollment(
            student_id=student.student_id, faculty_subject_id=assignment.faculty_subject_id, is_active=True
        )
        db.session.add(enrollment)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return enrollment


def student_enrollments(user_id: int) -> list[StudentSubjectEnrollment]:
    student = _student_for_user(user_id)
    return (
        StudentSubjectEnrollment.query.filter_by(student_id=student.student_id, is_active=True)
        .order_by(StudentSubjectEnrollment.enrolled_at.desc()).all()
    )


def serialize_student_enrollment(enrollment: StudentSubjectEnrollment) -> dict:
    assignment = enrollment.faculty_subject
    return {
        "enrollment_id": enrollment.enrollment_id,
        "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
        "faculty_subject_id": assignment.faculty_subject_id,
        "subject_id": assignment.subject.subject_id,
        "subject_code": assignment.subject.subject_code,
        "subject_name": assignment.subject.subject_name,
        "semester": assignment.semester,
        "academic_year": assignment.year,
        "faculty": {
            "faculty_id": assignment.faculty.faculty_id,
            "name": f"{assignment.faculty.user.first_name} {assignment.faculty.user.last_name}".strip(),
            "designation": assignment.faculty.designation,
        },
    }


def _schedule_for(exam_id: int, now: datetime | None = None):
    now = now or datetime.now()
    return (
        ExamSchedule.query.filter(
            ExamSchedule.exam_id == exam_id,
            ExamSchedule.is_active.is_(True),
            ExamSchedule.end_time > now,
        )
        .order_by(ExamSchedule.start_time.asc())
        .first()
    )


def _exam_summary(
    exam: Exam,
    schedule: ExamSchedule | None,
    registration_status: str,
    now: datetime | None = None,
):
    now = now or datetime.now()
    subject = exam.subject
    return {
        "exam_id": exam.exam_id,
        "title": exam.title,
        "subject": {
            "subject_id": subject.subject_id,
            "subject_code": subject.subject_code,
            "name": subject.subject_name,
        },
        "duration_minutes": exam.duration_minutes,
        "total_marks": float(exam.total_marks),
        "status": exam.status,
        "registration_open": bool(
            schedule
            and schedule.end_time > now
            and (schedule.registration_end_time or schedule.end_time) > now
        ),
        "schedule": (
            {
                "schedule_id": schedule.schedule_id,
                "start_time": schedule.start_time.isoformat(),
                "end_time": schedule.end_time.isoformat(),
                "registration_end_time": (
                    schedule.registration_end_time.isoformat()
                    if schedule.registration_end_time
                    else None
                ),
            }
            if schedule
            else None
        ),
        "registration_status": registration_status,
    }


def available_exams(user_id: int) -> list[dict]:
    student = _student_for_user(user_id)
    exams = (
        Exam.query.join(Exam.subject)
        .filter(
            Exam.status == "Published",
            Exam.subject.has(
                department_id=student.department_id,
                is_active=True,
            ),
        )
        .order_by(Exam.exam_id.desc())
        .all()
    )
    now = datetime.now()
    data = []
    for exam in exams:
        schedule = _schedule_for(exam.exam_id, now)
        if schedule is None:
            continue
        registration = CandidateRegistration.query.filter_by(
            exam_id=exam.exam_id, student_id=student.student_id
        ).first()
        # Preserve access to an existing registration; new registrations require an
        # active enrollment in the offering for the exam's subject and faculty.
        if registration is None and not StudentSubjectEnrollment.query.join(
            FacultySubject, StudentSubjectEnrollment.faculty_subject_id == FacultySubject.faculty_subject_id
        ).filter(
            StudentSubjectEnrollment.student_id == student.student_id,
            StudentSubjectEnrollment.is_active.is_(True),
            FacultySubject.is_active.is_(True),
            FacultySubject.subject_id == exam.subject_id,
            FacultySubject.faculty.has(user_id=exam.created_by),
        ).first():
            continue
        status = registration.status if registration else "NOT_REGISTERED"
        data.append(_exam_summary(exam, schedule, status, now))
    return data


def register_for_exam(user_id: int, exam_id: int) -> CandidateRegistration:
    student = _student_for_user(user_id)
    exam = Exam.query.filter_by(exam_id=exam_id).first()
    if exam is None:
        raise LookupError("Exam not found.")
    if exam.status != "Published":
        raise ValueError("Exam is not available for registration.")
    if exam.subject.department_id != student.department_id:
        raise ValueError("This exam is not available to your department.")
    existing = CandidateRegistration.query.filter_by(
        exam_id=exam_id, student_id=student.student_id
    ).first()
    if existing:
        if existing.status == "Registered":
            raise ValueError("You are already registered for this exam.")
        raise ValueError("This registration was cancelled and cannot be reused.")
    if not StudentSubjectEnrollment.query.join(
        FacultySubject, StudentSubjectEnrollment.faculty_subject_id == FacultySubject.faculty_subject_id
    ).filter(
        StudentSubjectEnrollment.student_id == student.student_id,
        StudentSubjectEnrollment.is_active.is_(True),
        FacultySubject.is_active.is_(True),
        FacultySubject.subject_id == exam.subject_id,
        FacultySubject.faculty.has(user_id=exam.created_by),
    ).first():
        raise ValueError("Enroll in this subject with the exam's faculty before registering.")
    now = datetime.now()
    schedule = _schedule_for(exam_id, now)
    if schedule is None:
        raise ValueError("Exam has no active upcoming or in-progress schedule.")
    registration_end = schedule.registration_end_time or schedule.end_time
    if now >= registration_end:
        raise ValueError("Registration is closed for this exam.")
    registration = CandidateRegistration(
        exam_id=exam_id,
        student_id=student.student_id,
        status="Registered",
    )
    try:
        db.session.add(registration)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return registration


def student_registrations(user_id: int) -> list[CandidateRegistration]:
    student = _student_for_user(user_id)
    return (
        CandidateRegistration.query.filter_by(student_id=student.student_id)
        .order_by(CandidateRegistration.registered_at.desc())
        .all()
    )


def student_registration_detail(user_id: int, registration_id: int) -> CandidateRegistration:
    student = _student_for_user(user_id)
    registration = CandidateRegistration.query.filter_by(
        registration_id=registration_id, student_id=student.student_id
    ).first()
    if registration is None:
        raise LookupError("Registration not found.")
    return registration


def student_results(user_id: int) -> list[Result]:
    student = _student_for_user(user_id)
    return (
        Result.query.join(ExamAttempt, Result.attempt_id == ExamAttempt.attempt_id)
        .join(CandidateRegistration, ExamAttempt.registration_id == CandidateRegistration.registration_id)
        .filter(CandidateRegistration.student_id == student.student_id, Result.published_at.isnot(None))
        .order_by(Result.published_at.desc())
        .all()
    )


def student_result_detail(user_id: int, result_id: int) -> tuple[Result, list[dict]]:
    student = _student_for_user(user_id)
    result = (
        Result.query.join(ExamAttempt, Result.attempt_id == ExamAttempt.attempt_id)
        .join(CandidateRegistration, ExamAttempt.registration_id == CandidateRegistration.registration_id)
        .filter(
            Result.result_id == result_id,
            Result.published_at.isnot(None),
            CandidateRegistration.student_id == student.student_id,
        )
        .first()
    )
    if result is None:
        raise LookupError("Published result not found.")
    attempt = result.attempt
    exam = attempt.registration.exam
    answers = {a.exam_question_id: a for a in attempt.answers}
    breakdown = []
    for eq in sorted(exam.exam_questions, key=lambda row: row.question_order):
        question = eq.question
        answer = answers.get(eq.exam_question_id)
        selected = answer.selected_option if answer else None
        correct_options = [o for o in question.options if o.is_correct]
        marks = float(answer.marks_obtained or 0) if answer else 0.0
        breakdown.append({
            "exam_question_id": eq.exam_question_id,
            "question_order": eq.question_order,
            "question_text": question.question_text,
            "marks_available": float(eq.marks),
            "marks_obtained": marks,
            "answer_text": answer.answer_text if answer else None,
            "selected_option": ({"option_id": selected.option_id, "option_text": selected.option_text} if selected else None),
            "correct_options": [{"option_id": o.option_id, "option_text": o.option_text} for o in correct_options],
            "remarks": (
                "Correct" if marks >= float(eq.marks)
                else "Partially correct" if marks > 0
                else "Incorrect or unanswered"
            ),
        })
    return result, breakdown


def serialize_student_result(result: Result) -> dict:
    attempt = result.attempt
    exam = attempt.registration.exam
    return {
        "result_id": result.result_id,
        "exam_id": exam.exam_id,
        "exam_title": exam.title,
        "subject_code": exam.subject.subject_code,
        "total_marks": float(result.total_marks),
        "obtained_marks": float(result.obtained_marks),
        "percentage": float(result.percentage),
        "grade": result.grade,
        "result_status": result.result_status,
        "published_at": result.published_at.isoformat() if result.published_at else None,
    }


def serialize_registration(registration: CandidateRegistration) -> dict:
    exam = registration.exam
    schedule = _schedule_for(exam.exam_id)
    return {
        "registration_id": registration.registration_id,
        "exam_id": exam.exam_id,
        "student_id": registration.student_id,
        "status": registration.status,
        "registered_at": registration.registered_at.isoformat() if registration.registered_at else None,
        "exam": _exam_summary(exam, schedule, registration.status),
    }
