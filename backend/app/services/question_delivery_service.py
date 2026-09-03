"""
Question delivery service.

Contains business logic for retrieving examination questions
and their answer options for an authenticated student.
"""

from app.models import (
    Exam,
    Student,
    CandidateRegistration,
    ExamQuestion,
)


def get_exam_questions(user_id: int, exam_id: int) -> dict:
    """
    Retrieve questions for an examination for an authenticated student.

    The student must:
    - have an active Student profile
    - be registered for the examination

    Correct answers and explanations are deliberately not returned.
    """

    # ------------------------------------------------------------
    # 1. Verify student
    # ------------------------------------------------------------

    student = Student.query.filter_by(
        user_id=user_id,
        is_active=True
    ).first()

    if student is None:
        raise ValueError("Student profile not found or inactive.")

    # ------------------------------------------------------------
    # 2. Verify exam
    # ------------------------------------------------------------

    exam = Exam.query.filter_by(
        exam_id=exam_id
    ).first()

    if exam is None:
        raise ValueError("Examination not found.")

    # ------------------------------------------------------------
    # 3. Verify registration
    # ------------------------------------------------------------

    registration = CandidateRegistration.query.filter_by(
        exam_id=exam_id,
        student_id=student.student_id,
        status='Registered'
    ).first()

    if registration is None:
        raise ValueError(
            "You are not registered for this examination."
        )

    # ------------------------------------------------------------
    # 4. Retrieve exam questions
    # ------------------------------------------------------------

    exam_questions = (
        ExamQuestion.query
        .filter_by(exam_id=exam_id)
        .order_by(ExamQuestion.question_order.asc())
        .all()
    )

    questions = []

    for exam_question in exam_questions:

        question = exam_question.question

        # Skip inactive questions
        if question is None or not question.is_active:
            continue

        # --------------------------------------------------------
        # Build options WITHOUT IsCorrect
        # --------------------------------------------------------

        options = []

        for option in sorted(
            question.options,
            key=lambda item: item.option_order
        ):
            options.append({
                'option_id': option.option_id,
                'option_text': option.option_text,
                'option_order': option.option_order,
            })

        questions.append({
            'exam_question_id': exam_question.exam_question_id,
            'question_order': exam_question.question_order,
            'question_text': question.question_text,
            'question_type': question.question_type,
            'marks': float(exam_question.marks),
            'options': options,
        })

    return {
        'exam_id': exam.exam_id,
        'title': exam.title,
        'questions': questions,
    }