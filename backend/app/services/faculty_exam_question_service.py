from app.extensions.database import db
from app.models import Faculty, Exam, Question, ExamQuestion


def add_question_to_exam(
    user_id,
    exam_id,
    question_id,
    question_order,
    marks
):
    # Verify faculty profile
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    # Verify exam
    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    # Faculty can only manage their own exams
    if exam.created_by != user_id:
        raise ValueError("You can only manage your own exams.")

    # Verify question
    question = Question.query.filter_by(question_id=question_id).first()

    if question is None:
        raise ValueError("Question not found.")

    # Faculty can only use their own questions
    if question.created_by != user_id:
        raise ValueError("You can only use your own questions.")

    # Validate question order
    try:
        question_order = int(question_order)
    except (TypeError, ValueError):
        raise ValueError("Question order must be a valid integer.")

    if question_order <= 0:
        raise ValueError("Question order must be greater than zero.")

    # Validate marks
    try:
        marks = float(marks)
    except (TypeError, ValueError):
        raise ValueError("Marks must be a valid number.")

    if marks <= 0:
        raise ValueError("Marks must be greater than zero.")

    # Check duplicate question in this exam
    existing_question = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_id=question_id
    ).first()

    if existing_question is not None:
        raise ValueError("This question is already added to the exam.")

    # Check duplicate order in this exam
    existing_order = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_order=question_order
    ).first()

    if existing_order is not None:
        raise ValueError(
            "A question with this order already exists in the exam."
        )

    exam_question = ExamQuestion(
        exam_id=exam_id,
        question_id=question_id,
        question_order=question_order,
        marks=marks
    )

    try:
        db.session.add(exam_question)
        db.session.commit()

        return exam_question

    except Exception:
        db.session.rollback()
        raise