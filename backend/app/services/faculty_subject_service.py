"""
Faculty Subject Service

Faculty do not create or manage subjects.

Subjects are created by Admin and assigned to Faculty through
FacultySubject.

This service only exposes subjects that are currently assigned
to the logged-in faculty.
"""

from app.models import Faculty, FacultySubject


def get_my_subjects(user_id):
    """
    Return subjects currently assigned to the logged-in faculty.

    Historical/inactive assignments are excluded.
    """

    faculty = Faculty.query.filter_by(
        user_id=user_id
    ).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    assignments = (
        FacultySubject.query
        .filter_by(
            faculty_id=faculty.faculty_id,
            is_active=True
        )
        .order_by(
            FacultySubject.year.desc(),
            FacultySubject.semester.desc(),
            FacultySubject.faculty_subject_id.desc()
        )
        .all()
    )

    return assignments