"""
Admin services.

Admin is responsible for creating subjects and assigning
subjects to Faculty.
"""

from app.extensions.database import db
from app.models import Faculty, FacultySubject, Subject


def create_subject(
    user_id,
    department_id,
    subject_code,
    subject_name,
    description=None,
    credits=None,
):
    """Create a new subject."""

    if not subject_code or not str(subject_code).strip():
        raise ValueError("Subject code is required.")

    if not subject_name or not str(subject_name).strip():
        raise ValueError("Subject name is required.")

    try:
        department_id = int(department_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid department_id.")

    subject_code = str(subject_code).strip()
    subject_name = str(subject_name).strip()

    existing = Subject.query.filter_by(subject_code=subject_code).first()
    if existing is not None:
        raise ValueError("A subject with this subject code already exists.")

    if credits is not None:
        try:
            credits = int(credits)
        except (TypeError, ValueError):
            raise ValueError("Credits must be a valid integer.")

        if credits <= 0:
            raise ValueError("Credits must be greater than 0.")

    subject = Subject(
        department_id=department_id,
        created_by=user_id,
        subject_code=subject_code,
        subject_name=subject_name,
        description=description,
        credits=credits,
        is_active=True,
    )

    try:
        db.session.add(subject)
        db.session.commit()
        return subject
    except Exception:
        db.session.rollback()
        raise


def get_all_subjects():
    """Return all subjects."""

    return (
        Subject.query
        .order_by(Subject.subject_id.desc())
        .all()
    )


def get_all_faculty():
    """Return all Faculty profiles."""

    return (
        Faculty.query
        .order_by(Faculty.faculty_id.asc())
        .all()
    )


def assign_subject_to_faculty(
    faculty_id,
    subject_id,
    semester,
    year,
):
    """Assign a subject to a Faculty member."""

    try:
        faculty_id = int(faculty_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_id.")

    try:
        subject_id = int(subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid subject_id.")

    try:
        semester = int(semester)
    except (TypeError, ValueError):
        raise ValueError("Semester must be a valid integer.")

    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ValueError("Year must be a valid integer.")

    if semester <= 0:
        raise ValueError("Semester must be greater than 0.")

    if year <= 0:
        raise ValueError("Year must be greater than 0.")

    faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()

    if faculty is None:
        raise ValueError("Faculty not found.")

    subject = Subject.query.filter_by(subject_id=subject_id).first()

    if subject is None:
        raise ValueError("Subject not found.")

    if not subject.is_active:
        raise ValueError("Cannot assign an inactive subject.")

    existing = FacultySubject.query.filter_by(
        faculty_id=faculty_id,
        subject_id=subject_id,
        semester=semester,
        year=year,
    ).first()

    if existing is not None:
        if existing.is_active:
            raise ValueError(
                "This subject is already assigned to this Faculty for this semester and year."
            )

        # Reactivate an old assignment instead of creating a duplicate.
        existing.is_active = True

        try:
            db.session.commit()
            return existing
        except Exception:
            db.session.rollback()
            raise

    assignment = FacultySubject(
        faculty_id=faculty_id,
        subject_id=subject_id,
        semester=semester,
        year=year,
        is_active=True,
    )

    try:
        db.session.add(assignment)
        db.session.commit()
        return assignment
    except Exception:
        db.session.rollback()
        raise


def get_faculty_subjects(faculty_id):
    """Return all assignments for a Faculty member."""

    try:
        faculty_id = int(faculty_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_id.")

    faculty = Faculty.query.filter_by(faculty_id=faculty_id).first()

    if faculty is None:
        raise ValueError("Faculty not found.")

    return (
        FacultySubject.query
        .filter_by(faculty_id=faculty_id)
        .order_by(
            FacultySubject.year.desc(),
            FacultySubject.semester.desc(),
            FacultySubject.faculty_subject_id.desc(),
        )
        .all()
    )


def deactivate_faculty_subject(faculty_subject_id):
    """Deactivate an assignment while preserving its history."""

    try:
        faculty_subject_id = int(faculty_subject_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid faculty_subject_id.")

    assignment = FacultySubject.query.filter_by(
        faculty_subject_id=faculty_subject_id
    ).first()

    if assignment is None:
        raise ValueError("Faculty subject assignment not found.")

    assignment.is_active = False

    try:
        db.session.commit()
        return assignment
    except Exception:
        db.session.rollback()
        raise