import csv
import io
import math

from app.extensions.database import db
from app.models import Faculty, FacultySubject, Question, QuestionOption, Subject


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

CSV_OPTION_COLUMNS = ('option_a', 'option_b', 'option_c', 'option_d', 'option_e', 'option_f')


def import_questions_csv(user_id: int, subject_id, csv_bytes: bytes) -> list[Question]:
    """Validate and atomically import a faculty question bank CSV."""
    faculty = Faculty.query.filter_by(user_id=user_id).first()
    if faculty is None:
        raise ValueError('Faculty profile not found.')
    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError('Select a valid subject.')

    subject = Subject.query.filter_by(subject_id=subject_id, is_active=True).first()
    if subject is None:
        raise ValueError('Selected subject was not found or is inactive.')
    assignment = FacultySubject.query.filter_by(
        faculty_id=faculty.faculty_id,
        subject_id=subject_id,
        is_active=True,
    ).first()
    if assignment is None:
        raise ValueError('You can only import questions for a subject currently assigned to you.')

    try:
        csv_text = csv_bytes.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise ValueError('The CSV file must use UTF-8 encoding.')

    reader = csv.DictReader(io.StringIO(csv_text, newline=''))
    required_columns = {'question_text', 'question_type', 'marks', 'difficulty'}
    headers = {str(header or '').strip().lower() for header in (reader.fieldnames or [])}
    missing = sorted(required_columns - headers)
    if missing:
        raise ValueError(f"CSV is missing required column(s): {', '.join(missing)}.")

    parsed_rows = []
    errors = []
    for row_number, raw_row in enumerate(reader, start=2):
        row = {str(key or '').strip().lower(): (value or '').strip() for key, value in raw_row.items() if key}
        if not any(row.values()):
            continue
        question_text = row.get('question_text', '')
        question_type_value = row.get('question_type', '').replace(' ', '').lower()
        type_aliases = {
            'mcq': 'MCQ', 'truefalse': 'TrueFalse', 'shortanswer': 'ShortAnswer', 'descriptive': 'Descriptive'
        }
        question_type = type_aliases.get(question_type_value)
        difficulty_value = row.get('difficulty', '').capitalize()
        try:
            marks = float(row.get('marks', ''))
        except (TypeError, ValueError):
            marks = 0
        if not question_text:
            errors.append(f'Row {row_number}: question_text is required.')
        if question_type is None:
            errors.append(f'Row {row_number}: question_type must be MCQ, TrueFalse, ShortAnswer, or Descriptive.')
        if not math.isfinite(marks) or marks <= 0:
            errors.append(f'Row {row_number}: marks must be a number greater than zero.')
        if difficulty_value not in ALLOWED_DIFFICULTIES:
            errors.append(f'Row {row_number}: difficulty must be Easy, Medium, or Hard.')

        options = [(column, row.get(column, '')) for column in CSV_OPTION_COLUMNS if row.get(column, '')]
        if any(len(value) > 500 for _, value in options):
            errors.append(f'Row {row_number}: each option must be 500 characters or fewer.')
        correct_value = row.get('correct_answer', '').strip()
        correct_index = None
        if question_type in {'MCQ', 'TrueFalse'}:
            if len(options) < 2:
                errors.append(f'Row {row_number}: {question_type} requires at least two options.')
            matches = [index for index, (column, value) in enumerate(options)
                       if correct_value.lower() in {column[-1], column, value.lower()}]
            if not correct_value or len(matches) != 1:
                errors.append(f'Row {row_number}: correct_answer must match one option text or its A–F label.')
            elif matches:
                correct_index = matches[0]
        elif options or correct_value:
            errors.append(f'Row {row_number}: options and correct_answer must be blank for {question_type or "this question type"}.')

        parsed_rows.append({
            'row_number': row_number,
            'question_text': question_text,
            'question_type': question_type,
            'marks': marks,
            'difficulty': difficulty_value,
            'explanation': row.get('explanation') or None,
            'options': options,
            'correct_index': correct_index,
        })
        if len(parsed_rows) > 500:
            errors.append('A CSV upload can contain at most 500 non-empty question rows.')
            break

    if not parsed_rows:
        errors.append('The CSV contains no question rows.')
    if errors:
        raise ValueError('CSV import validation failed. ' + ' '.join(errors[:25]))

    imported = []
    try:
        for row in parsed_rows:
            question = Question(
                subject_id=subject_id,
                created_by=user_id,
                question_text=row['question_text'],
                question_type=row['question_type'],
                marks=row['marks'],
                difficulty=row['difficulty'],
                explanation=row['explanation'],
                is_active=True,
            )
            db.session.add(question)
            db.session.flush()
            for index, (_, option_text) in enumerate(row['options'], start=1):
                db.session.add(QuestionOption(
                    question_id=question.question_id,
                    option_text=option_text,
                    is_correct=index - 1 == row['correct_index'],
                    option_order=index,
                ))
            imported.append(question)
        db.session.commit()
        return imported
    except Exception:
        db.session.rollback()
        raise


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
