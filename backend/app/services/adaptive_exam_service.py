"""
Adaptive exam service.

Handles difficulty-based question selection for exams where
adaptive mode is enabled.

Adaptive behavior:
    Correct:
        Easy   -> Medium
        Medium -> Hard
        Hard   -> Hard

    Incorrect:
        Hard   -> Medium
        Medium -> Easy
        Easy   -> Easy
"""

from flask import abort
from sqlalchemy import and_

from app.extensions.database import db
from app.models import (
    Exam,
    ExamAttempt,
    ExamQuestion,
    StudentAnswer,
    Question,
    CandidateRegistration,
)


DIFFICULTY_LEVELS = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}


def calculate_next_difficulty(current_difficulty: str, is_correct: bool) -> str:
    """
    Calculate the next difficulty based on the current difficulty
    and whether the previous answer was correct.
    """

    if current_difficulty not in DIFFICULTY_LEVELS:
        current_difficulty = "Medium"

    current_level = DIFFICULTY_LEVELS[current_difficulty]

    if is_correct:
        next_level = min(current_level + 1, 3)
    else:
        next_level = max(current_level - 1, 1)

    for difficulty, level in DIFFICULTY_LEVELS.items():
        if level == next_level:
            return difficulty

    return "Medium"


def _get_attempt_for_student(user_id: int, attempt_id: int) -> ExamAttempt:
    """
    Get an exam attempt belonging to the logged-in student.
    """

    attempt = (
        ExamAttempt.query
        .join(
            CandidateRegistration,
            ExamAttempt.registration_id
            == CandidateRegistration.registration_id
        )
        .filter(
            ExamAttempt.attempt_id == attempt_id,
            CandidateRegistration.student_id == user_id,
        )
        .first()
    )

    if not attempt:
        abort(404, description="Exam attempt not found.")

    return attempt


def _get_answered_question_ids(attempt_id: int) -> set:
    """
    Return the ExamQuestion IDs already answered in this attempt.
    """

    answers = (
        StudentAnswer.query
        .filter(StudentAnswer.attempt_id == attempt_id)
        .all()
    )

    return {
        answer.exam_question_id
        for answer in answers
    }


def _difficulty_candidates(desired_difficulty: str) -> list[str]:
    """
    Return difficulty fallback order.

    The requested difficulty is always preferred.

    For a tie between equally close difficulties, the easier
    difficulty is preferred.
    """

    fallback_order = {
        "Easy": ["Easy", "Medium", "Hard"],
        "Medium": ["Medium", "Easy", "Hard"],
        "Hard": ["Hard", "Medium", "Easy"],
    }

    return fallback_order.get(
        desired_difficulty,
        ["Medium", "Easy", "Hard"],
    )


def select_question_with_fallback(
    exam_id: int,
    attempt_id: int,
    desired_difficulty: str,
):
    """
    Select an unused question from the exam's configured question pool.

    Selection order:
        1. Desired difficulty
        2. Nearest fallback difficulty

    Already answered questions are excluded.
    """

    answered_question_ids = _get_answered_question_ids(attempt_id)

    query = (
        db.session.query(ExamQuestion, Question)
        .join(
            Question,
            ExamQuestion.question_id == Question.question_id,
        )
        .filter(
            ExamQuestion.exam_id == exam_id,
        )
    )

    if answered_question_ids:
        query = query.filter(
            ~ExamQuestion.exam_question_id.in_(answered_question_ids)
        )

    candidates = query.all()

    if not candidates:
        return None

    difficulty_order = _difficulty_candidates(desired_difficulty)

    for difficulty in difficulty_order:
        matching = [
            (exam_question, question)
            for exam_question, question in candidates
            if question.difficulty == difficulty
        ]

        if matching:
            # Preserve the faculty-configured question order.
            matching.sort(
                key=lambda item: item[0].question_order
            )

            return matching[0]

    return None


def _serialize_question(exam_question, question):
    """
    Serialize a question for student delivery.

    Correct answers are deliberately not exposed.
    """

    options = []

    for option in question.options:
        if not getattr(option, "is_active", True):
            continue

        options.append(
            {
                "option_id": option.option_id,
                "option_text": option.option_text,
            }
        )

    return {
        "exam_question_id": exam_question.exam_question_id,
        "question_id": question.question_id,
        "question_order": exam_question.question_order,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "marks": exam_question.marks,
        "difficulty": question.difficulty,
        "options": options,
    }


def _get_last_answer_state(attempt_id: int):
    """
    Determine the correctness of the most recently answered question.

    Returns:
        None if no answer exists.
        True if the latest answer is correct.
        False if the latest answer is incorrect.
    """

    last_answer = (
        StudentAnswer.query
        .filter(StudentAnswer.attempt_id == attempt_id)
        .order_by(StudentAnswer.answered_at.desc(), StudentAnswer.answer_id.desc())
        .first()
    )

    if not last_answer:
        return None

    exam_question = ExamQuestion.query.filter_by(
        exam_question_id=last_answer.exam_question_id
    ).first()

    if not exam_question:
        return None

    question = Question.query.filter_by(
        question_id=exam_question.question_id
    ).first()

    if not question:
        return None

    if last_answer.selected_option_id is None:
        return False

    selected_option = next(
        (
            option
            for option in question.options
            if option.option_id == last_answer.selected_option_id
        ),
        None,
    )

    if not selected_option:
        return False

    return bool(selected_option.is_correct)


def get_next_question(user_id: int, attempt_id: int):
    """
    Return the next adaptive question for an attempt.

    First question:
        Uses Exam.initial_difficulty.

    Subsequent questions:
        Uses the previous answer's correctness to determine
        the next desired difficulty.

    Standard exams are rejected here so that this service is
    only used for adaptive attempts.
    """

    attempt = _get_attempt_for_student(user_id, attempt_id)

    if attempt.status != "InProgress":
        abort(400, description="Exam attempt is no longer in progress.")

    exam = Exam.query.filter_by(
        exam_id=attempt.registration.exam_id
    ).first()

    if not exam:
        abort(404, description="Exam not found.")

    if not exam.adaptive_enabled:
        abort(
            400,
            description="Adaptive mode is not enabled for this exam.",
        )

    # If a question has already been selected but not answered,
    # return the same question instead of selecting another one.
    if attempt.current_adaptive_exam_question_id:
        current = (
            db.session.query(ExamQuestion, Question)
            .join(
                Question,
                ExamQuestion.question_id == Question.question_id,
            )
            .filter(
                ExamQuestion.exam_question_id
                == attempt.current_adaptive_exam_question_id,
                ExamQuestion.exam_id == exam.exam_id,
            )
            .first()
        )

        if current:
            exam_question, question = current

            return {
                "has_next_question": True,
                "desired_difficulty": question.difficulty,
                "question": _serialize_question(
                    exam_question,
                    question,
                ),
            }

        # Safety fallback if the stored question no longer exists.
        attempt.current_adaptive_exam_question_id = None
        db.session.commit()

    last_answer_state = _get_last_answer_state(attempt_id)

    if last_answer_state is None:
        desired_difficulty = exam.initial_difficulty
    else:
        last_answer = (
            StudentAnswer.query
            .filter(StudentAnswer.attempt_id == attempt_id)
            .order_by(
                StudentAnswer.answered_at.desc(),
                StudentAnswer.answer_id.desc(),
            )
            .first()
        )

        last_exam_question = ExamQuestion.query.filter_by(
            exam_question_id=last_answer.exam_question_id
        ).first()

        last_question = Question.query.filter_by(
            question_id=last_exam_question.question_id
        ).first()

        desired_difficulty = calculate_next_difficulty(
            last_question.difficulty,
            last_answer_state,
        )

    selected = select_question_with_fallback(
        exam_id=exam.exam_id,
        attempt_id=attempt_id,
        desired_difficulty=desired_difficulty,
    )

    if not selected:
        return {
            "has_next_question": False,
            "message": "No unused questions remain in the exam pool.",
        }

    exam_question, question = selected

    attempt.current_adaptive_exam_question_id = (
        exam_question.exam_question_id
    )
    db.session.commit()

    return {
        "has_next_question": True,
        "desired_difficulty": desired_difficulty,
        "question": _serialize_question(
            exam_question,
            question,
        ),
    }