from app.extensions.database import db
from app.models import Faculty, Exam, ExamQuestion, ExamSchedule


def publish_exam(user_id, exam_id):
    # Verify faculty profile
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    # Verify exam
    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    # Faculty can only publish own exams
    if exam.created_by != user_id:
        raise ValueError("You can only publish your own exams.")

    # Exam must currently be Draft
    if exam.status != 'Draft':
        raise ValueError(
            f"Exam cannot be published because its current status is '{exam.status}'."
        )

    # Exam must contain at least one question
    question_count = ExamQuestion.query.filter_by(
        exam_id=exam_id
    ).count()

    if question_count == 0:
        raise ValueError(
            "Exam must contain at least one question before publishing."
        )

    # Exam must have an active schedule
    schedule = ExamSchedule.query.filter_by(
        exam_id=exam_id,
        is_active=True
    ).first()

    if schedule is None:
        raise ValueError(
            "Exam must have an active schedule before publishing."
        )

    # Update status
    exam.status = 'Published'

    try:
        db.session.commit()
        return exam

    except Exception:
        db.session.rollback()
        raise