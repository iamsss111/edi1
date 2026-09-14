from app.extensions.database import db
from app.models import Faculty, FacultySubject, Question, Subject


ALLOWED_QUESTION_TYPES = {
    'MCQ',
    'TrueFalse',
    'ShortAnswer',
    'Descriptive'
}

ALLOWED_DIFFICULTIES = {
    'Easy',
    'Medium',
    'Hard'
}


def create_question(
    user_id: int,
    subject_id: int,
    question_text: str,
    question_type: str,
    marks,
    difficulty: str,
    explanation: str | None
) -> Question:

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

    assignment = FacultySubject.query.filter_by(
        faculty_id=faculty.faculty_id,
        subject_id=subject_id,
        is_active=True
    ).first()

    if assignment is None:
        raise ValueError(
            "You can only create questions for subjects currently assigned to you."
        )

    if not question_text or not question_text.strip():
        raise ValueError("Question text is required.")

    question_text = question_text.strip()

    question_type = str(question_type).strip()

    if question_type not in ALLOWED_QUESTION_TYPES:
        raise ValueError(
            f"Invalid question type. Allowed types: "
            f"{', '.join(sorted(ALLOWED_QUESTION_TYPES))}"
        )

    try:
        marks = float(marks)
    except (TypeError, ValueError):
        raise ValueError("Marks must be a valid number.")

    if marks <= 0:
        raise ValueError("Marks must be greater than 0.")

    difficulty = str(difficulty).strip()

    if difficulty not in ALLOWED_DIFFICULTIES:
        raise ValueError(
            f"Invalid difficulty. Allowed values: "
            f"{', '.join(sorted(ALLOWED_DIFFICULTIES))}"
        )

    if explanation is not None:
        explanation = str(explanation).strip()

        if not explanation:
            explanation = None

    question = Question(
        subject_id=subject_id,
        created_by=user_id,
        question_text=question_text,
        question_type=question_type,
        marks=marks,
        difficulty=difficulty,
        explanation=explanation,
        is_active=True
    )

    try:
        db.session.add(question)
        db.session.commit()
        return question

    except Exception:
        db.session.rollback()
        raise


def get_my_questions(user_id: int):

    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    active_subject_ids = (
        db.select(FacultySubject.subject_id)
        .where(
            FacultySubject.faculty_id == faculty.faculty_id,
            FacultySubject.is_active.is_(True)
        )
    )

    questions = (
        Question.query
        .filter(
            Question.subject_id.in_(active_subject_ids),
            Question.is_active.is_(True)
        )
        .order_by(Question.question_id.desc())
        .all()
    )

    return questions