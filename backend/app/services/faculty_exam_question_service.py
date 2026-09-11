"""
Faculty Exam Question Service

Handles adding/removing questions from faculty-owned exams.

Faculty can use any active question from the shared question bank
provided that:
- the faculty is currently assigned to the exam's subject
- the question belongs to the same subject as the exam
- the question is active
- the faculty owns the exam
"""

from app.extensions.database import db
from app.models import (
    Faculty,
    FacultySubject,
    Exam,
    Question,
    ExamQuestion,
)


def add_question_to_exam(
    user_id,
    exam_id,
    question_id,
    question_order,
    marks
):
    # ---------------------------------------------------------
    # 1. Verify faculty profile
    # ---------------------------------------------------------
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    # ---------------------------------------------------------
    # 2. Verify exam exists
    # ---------------------------------------------------------
    exam = Exam.query.filter_by(exam_id=exam_id).first()

    if exam is None:
        raise ValueError("Exam not found.")

    # ---------------------------------------------------------
    # 3. Faculty can manage only their own exams
    # ---------------------------------------------------------
    if exam.created_by != user_id:
        raise ValueError("You can only manage your own exams.")

    # ---------------------------------------------------------
    # 4. Verify faculty is currently assigned to
    #    the exam's subject
    # ---------------------------------------------------------
    assignment = FacultySubject.query.filter_by(
        faculty_id=faculty.faculty_id,
        subject_id=exam.subject_id,
        is_active=True
    ).first()

    if assignment is None:
        raise ValueError(
            "You are not currently assigned to this exam's subject."
        )

    # ---------------------------------------------------------
    # 5. Verify question exists
    # ---------------------------------------------------------
    question = Question.query.filter_by(
        question_id=question_id
    ).first()

    if question is None:
        raise ValueError("Question not found.")

    # ---------------------------------------------------------
    # 6. Question must be active
    # ---------------------------------------------------------
    if not question.is_active:
        raise ValueError("This question is inactive.")

    # ---------------------------------------------------------
    # 7. Question and exam must belong to the same subject
    # ---------------------------------------------------------
    if question.subject_id != exam.subject_id:
        raise ValueError(
            "The question must belong to the same subject as the exam."
        )

    # ---------------------------------------------------------
    # IMPORTANT:
    # Do NOT check question.created_by == user_id.
    #
    # Questions are now part of a shared subject question bank.
    # Any faculty currently assigned to the subject can use them.
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # 8. Validate question order
    # ---------------------------------------------------------
    try:
        question_order = int(question_order)
    except (TypeError, ValueError):
        raise ValueError(
            "Question order must be a valid integer."
        )

    if question_order <= 0:
        raise ValueError(
            "Question order must be greater than 0."
        )

    # ---------------------------------------------------------
    # 9. Validate marks
    # ---------------------------------------------------------
    try:
        marks = float(marks)
    except (TypeError, ValueError):
        raise ValueError(
            "Marks must be a valid number."
        )

    if marks <= 0:
        raise ValueError(
            "Marks must be greater than 0."
        )

    # ---------------------------------------------------------
    # 10. Prevent same question from being added twice
    # ---------------------------------------------------------
    existing_question = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_id=question_id
    ).first()

    if existing_question is not None:
        raise ValueError(
            "This question has already been added to the exam."
        )

    # ---------------------------------------------------------
    # 11. Prevent duplicate question order
    # ---------------------------------------------------------
    existing_order = ExamQuestion.query.filter_by(
        exam_id=exam_id,
        question_order=question_order
    ).first()

    if existing_order is not None:
        raise ValueError(
            "This question order is already being used in the exam."
        )

    # ---------------------------------------------------------
    # 12. Create ExamQuestion
    # ---------------------------------------------------------
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