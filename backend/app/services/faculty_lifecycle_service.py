"""Faculty-owned candidate, evaluation, result, and analytics workflows."""

from datetime import datetime

from sqlalchemy import or_

from app.extensions.database import db
from app.models import (
    AuditLog,
    CandidateRegistration,
    Exam,
    ExamAttempt,
    ExamQuestion,
    Faculty,
    Result,
    Student,
    StudentAnswer,
)


def _owned_exam(user_id: int, exam_id: int) -> Exam:
    if Faculty.query.filter_by(user_id=user_id).first() is None:
        raise ValueError("Faculty profile not found.")
    exam = Exam.query.filter_by(exam_id=exam_id, created_by=user_id).first()
    if exam is None:
        raise LookupError("Exam not found or not owned by this faculty member.")
    return exam


def _student_data(student: Student) -> dict:
    return {
        "student_id": student.student_id,
        "roll_number": student.roll_number,
        "enrollment_number": student.enrollment_number,
        "name": f"{student.user.first_name} {student.user.last_name}",
        "email": student.user.email,
    }


def exam_registrations(user_id: int, exam_id: int) -> list[CandidateRegistration]:
    _owned_exam(user_id, exam_id)
    return (
        CandidateRegistration.query.filter_by(exam_id=exam_id)
        .order_by(CandidateRegistration.registered_at.asc())
        .all()
    )


def exam_attempts(user_id: int, exam_id: int) -> list[ExamAttempt]:
    _owned_exam(user_id, exam_id)
    return (
        ExamAttempt.query.join(CandidateRegistration)
        .filter(CandidateRegistration.exam_id == exam_id)
        .order_by(ExamAttempt.started_at.desc())
        .all()
    )


def owned_attempt(user_id: int, attempt_id: int) -> ExamAttempt:
    attempt = ExamAttempt.query.join(CandidateRegistration).join(Exam).filter(
        ExamAttempt.attempt_id == attempt_id, Exam.created_by == user_id
    ).first()
    if attempt is None:
        raise LookupError("Attempt not found or not owned by this faculty member.")
    return attempt


def attempt_detail(user_id: int, attempt_id: int) -> dict:
    attempt = owned_attempt(user_id, attempt_id)
    data = {
        "attempt_id": attempt.attempt_id,
        "registration_id": attempt.registration_id,
        "student": _student_data(attempt.registration.student),
        "exam_id": attempt.registration.exam_id,
        "exam_title": attempt.registration.exam.title,
        "attempt_number": attempt.attempt_number,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "score": float(attempt.score) if attempt.score is not None else None,
        "result_id": attempt.result.result_id if attempt.result else None,
        "result_published": bool(attempt.result and attempt.result.published_at),
        "answers": [],
    }
    answer_by_question = {a.exam_question_id: a for a in attempt.answers}
    for eq in sorted(attempt.registration.exam.exam_questions, key=lambda row: row.question_order):
        answer = answer_by_question.get(eq.exam_question_id)
        selected = answer.selected_option if answer else None
        correct = [o for o in eq.question.options if o.is_correct]
        data["answers"].append({
            "exam_question_id": eq.exam_question_id,
            "question_order": eq.question_order,
            "question_text": eq.question.question_text,
            "marks_available": float(eq.marks),
            "answer_text": answer.answer_text if answer else None,
            "selected_option": ({"option_id": selected.option_id, "option_text": selected.option_text} if selected else None),
            "correct_options": [{"option_id": o.option_id, "option_text": o.option_text} for o in correct],
            "marks_obtained": float(answer.marks_obtained) if answer and answer.marks_obtained is not None else None,
        })
    return data


def attempt_integrity_events(user_id: int, attempt_id: int) -> list[AuditLog]:
    owned_attempt(user_id, attempt_id)
    return AuditLog.query.filter_by(entity_type="ExamAttempt", entity_id=attempt_id).order_by(AuditLog.created_at.asc()).all()


def pending_evaluations(user_id: int, exam_id: int | None = None) -> list[ExamAttempt]:
    if Faculty.query.filter_by(user_id=user_id).first() is None:
        raise ValueError("Faculty profile not found.")
    query = ExamAttempt.query.join(CandidateRegistration).join(Exam).filter(
        Exam.created_by == user_id,
        ExamAttempt.status.in_(["Submitted", "AutoSubmitted"]),
        or_(
            ExamAttempt.score.is_(None),
            ExamAttempt.result.has(Result.published_at.is_(None)),
        ),
    )
    if exam_id is not None:
        query = query.filter(Exam.exam_id == exam_id)
    return query.order_by(ExamAttempt.submitted_at.asc()).all()


def evaluate_owned_attempt(user_id: int, attempt_id: int) -> tuple[ExamAttempt, Result]:
    """Auto-grade objective answers for an attempt on an owned exam."""
    attempt = owned_attempt(user_id, attempt_id)
    if attempt.status not in ("Submitted", "AutoSubmitted"):
        raise ValueError("Only submitted attempts can be evaluated.")
    for answer in attempt.answers:
        eq = answer.exam_question
        question = eq.question if eq else None
        score = 0.0
        if question and answer.selected_option_id is not None:
            if any(o.option_id == answer.selected_option_id and o.is_correct for o in question.options):
                score = float(eq.marks)
        answer.marks_obtained = score
    attempt.score = sum(float(a.marks_obtained or 0) for a in attempt.answers)
    try:
        db.session.commit()
        from app.services.result_service import generate_result

        result = generate_result(
            user_id=attempt.registration.student.user_id,
            attempt_id=attempt_id,
        )
    except Exception:
        db.session.rollback()
        raise
    return attempt, result


def faculty_results(user_id: int, exam_id: int) -> tuple[Exam, list[Result]]:
    exam = _owned_exam(user_id, exam_id)
    results = (
        Result.query.join(ExamAttempt).join(CandidateRegistration)
        .filter(CandidateRegistration.exam_id == exam_id)
        .order_by(Result.result_id.asc()).all()
    )
    return exam, results


def publish_result(user_id: int, result_id: int) -> Result:
    result = Result.query.join(ExamAttempt).join(CandidateRegistration).join(Exam).filter(
        Result.result_id == result_id, Exam.created_by == user_id
    ).first()
    if result is None:
        raise LookupError("Result not found or not owned by this faculty member.")
    if result.published_at is None:
        result.published_at = datetime.now()
        try:
            db.session.add(_result_notification(result))
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    return result


def publish_exam_results(user_id: int, exam_id: int) -> list[Result]:
    exam = _owned_exam(user_id, exam_id)
    results = (
        Result.query.join(ExamAttempt).join(CandidateRegistration)
        .filter(CandidateRegistration.exam_id == exam_id, Result.published_at.is_(None))
        .all()
    )
    now = datetime.now()
    try:
        for result in results:
            result.published_at = now
            db.session.add(_result_notification(result))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return results


def _result_notification(result: Result):
    from app.models import Notification

    student = result.attempt.registration.student
    return Notification(
        user_id=student.user_id,
        title="Exam result published",
        message=f"Your result for {result.attempt.registration.exam.title} is now available.",
        notification_type="RESULT",
    )


def dashboard_statistics(user_id: int) -> dict:
    if Faculty.query.filter_by(user_id=user_id).first() is None:
        raise ValueError("Faculty profile not found.")
    exams = Exam.query.filter_by(created_by=user_id).all()
    exam_ids = [exam.exam_id for exam in exams]
    if not exam_ids:
        return {"total_exams": 0, "published_exams": 0, "upcoming_exams": 0, "registered_students": 0, "completed_attempts": 0, "pending_evaluations": 0}
    now = datetime.now()
    upcoming = sum(1 for exam in exams for schedule in exam.schedules if schedule.is_active and schedule.start_time > now)
    registrations = CandidateRegistration.query.filter(
        CandidateRegistration.exam_id.in_(exam_ids),
        CandidateRegistration.status == "Registered",
    ).count()
    submitted = ExamAttempt.query.join(CandidateRegistration).filter(CandidateRegistration.exam_id.in_(exam_ids), ExamAttempt.status.in_(["Submitted", "AutoSubmitted"])).count()
    pending = ExamAttempt.query.join(CandidateRegistration).filter(
        CandidateRegistration.exam_id.in_(exam_ids),
        ExamAttempt.status.in_(["Submitted", "AutoSubmitted"]),
        or_(
            ExamAttempt.score.is_(None),
            ExamAttempt.result.has(Result.published_at.is_(None)),
        ),
    ).count()
    return {
        "total_exams": len(exams),
        "published_exams": sum(exam.status == "Published" for exam in exams),
        "upcoming_exams": upcoming,
        "registered_students": registrations,
        "completed_attempts": submitted,
        "pending_evaluations": pending,
    }


def exam_analytics(user_id: int, exam_id: int) -> dict:
    exam = _owned_exam(user_id, exam_id)
    total_candidates = CandidateRegistration.query.filter_by(exam_id=exam_id).count()
    reg_count = CandidateRegistration.query.filter_by(exam_id=exam_id, status="Registered").count()
    attempts = ExamAttempt.query.join(CandidateRegistration).filter(CandidateRegistration.exam_id == exam_id).all()
    submitted = [a for a in attempts if a.status in ("Submitted", "AutoSubmitted")]
    scores = [float(a.score) for a in submitted if a.score is not None]
    results = Result.query.join(ExamAttempt).join(CandidateRegistration).filter(CandidateRegistration.exam_id == exam_id).all()
    published = [r for r in results if r.published_at is not None]
    accuracy = []
    for eq in exam.exam_questions:
        question = eq.question
        correct_ids = {o.option_id for o in question.options if o.is_correct}
        answer_count = 0
        correct_count = 0
        answers = StudentAnswer.query.join(ExamAttempt).filter(StudentAnswer.exam_question_id == eq.exam_question_id, ExamAttempt.status.in_(["Submitted", "AutoSubmitted"])).all()
        for answer in answers:
            answer_count += 1
            if answer.selected_option_id in correct_ids:
                correct_count += 1
        accuracy.append({"exam_question_id": eq.exam_question_id, "question_order": eq.question_order, "question_type": question.question_type, "difficulty": question.difficulty, "answered": answer_count, "correct": correct_count, "accuracy_percentage": round(100 * correct_count / answer_count, 2) if answer_count else None})
    return {
        "exam_id": exam_id,
        "total_candidates": total_candidates,
        "registered_candidates": reg_count,
        "attempted": len(attempts),
        "submitted": len(submitted),
        "pass_count": sum(r.result_status == "Pass" for r in published),
        "fail_count": sum(r.result_status == "Fail" for r in published),
        "average_score": round(sum(scores) / len(scores), 2) if scores else None,
        "highest_score": max(scores) if scores else None,
        "lowest_score": min(scores) if scores else None,
        "question_accuracy": accuracy,
    }


def student_performance(user_id: int, student_id: int) -> list[dict]:
    if Faculty.query.filter_by(user_id=user_id).first() is None:
        raise ValueError("Faculty profile not found.")
    student = Student.query.filter_by(student_id=student_id).first()
    if student is None:
        raise LookupError("Student not found.")
    rows = Result.query.join(ExamAttempt).join(CandidateRegistration).join(Exam).filter(
        CandidateRegistration.student_id == student_id,
        Exam.created_by == user_id,
        Result.published_at.isnot(None),
    ).all()
    return [{
        "result_id": r.result_id,
        "exam_id": r.attempt.registration.exam_id,
        "exam_title": r.attempt.registration.exam.title,
        "total_marks": float(r.total_marks),
        "obtained_marks": float(r.obtained_marks),
        "percentage": float(r.percentage),
        "grade": r.grade,
        "result_status": r.result_status,
        "published_at": r.published_at.isoformat() if r.published_at else None,
    } for r in rows]


def serialize_candidate(registration: CandidateRegistration) -> dict:
    student = registration.student
    return {
        "registration_id": registration.registration_id,
        "student": _student_data(student),
        "student_id": student.student_id,
        "roll_number": student.roll_number,
        "name": f"{student.user.first_name} {student.user.last_name}",
        "email": student.user.email,
        "registered_at": registration.registered_at.isoformat() if registration.registered_at else None,
        "status": registration.status,
    }


def serialize_attempt(attempt: ExamAttempt) -> dict:
    return {
        "attempt_id": attempt.attempt_id,
        "registration_id": attempt.registration_id,
        "exam_id": attempt.registration.exam_id,
        "exam_title": attempt.registration.exam.title,
        "student": _student_data(attempt.registration.student),
        "attempt_number": attempt.attempt_number,
        "status": attempt.status,
        "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
        "submitted_at": attempt.submitted_at.isoformat() if attempt.submitted_at else None,
        "score": float(attempt.score) if attempt.score is not None else None,
        "evaluation_status": (
            "PENDING" if attempt.score is None
            else "PENDING_PUBLICATION" if not attempt.result or attempt.result.published_at is None
            else "COMPLETE"
        ),
    }


def serialize_result(result: Result) -> dict:
    attempt = result.attempt
    student = attempt.registration.student
    return {
        "result_id": result.result_id,
        "attempt_id": attempt.attempt_id,
        "student_id": student.student_id,
        "student_name": f"{student.user.first_name} {student.user.last_name}",
        "obtained_marks": float(result.obtained_marks),
        "total_marks": float(result.total_marks),
        "percentage": float(result.percentage),
        "grade": result.grade,
        "result_status": result.result_status,
        "published": result.published_at is not None,
        "published_at": result.published_at.isoformat() if result.published_at else None,
    }


def serialize_integrity_event(event: AuditLog) -> dict:
    return {
        "event_id": event.audit_id,
        "event_type": event.action,
        "occurred_at": event.created_at.isoformat() if event.created_at else None,
        "details": event.details,
        "ip_address": event.ip_address,
    }
