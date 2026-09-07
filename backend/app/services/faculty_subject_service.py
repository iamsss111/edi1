"""
Faculty subject service.

Contains business logic for faculty subject management.
"""

from app.extensions.database import db
from app.models import Faculty, Subject


def create_subject(
        
    user_id: int,
    department_id: int,
    subject_code: str,
    subject_name: str,
    description: str | None,
    credits: int,
) -> Subject:
    """
    Create a subject for the authenticated faculty member.

    The subject must belong to the faculty member's department.
    """

    # ------------------------------------------------------------
    # 1. Find faculty profile
    # ------------------------------------------------------------

    faculty = Faculty.query.filter_by(
        user_id=user_id
    ).first()

    if faculty is None:
        raise ValueError(
            "Faculty profile not found."
        )

    # ------------------------------------------------------------
    # 2. Verify department ownership
    # ------------------------------------------------------------

    if faculty.department_id != department_id:
        raise ValueError(
            "You can only create subjects for your department."
        )

    # ------------------------------------------------------------
    # 3. Validate input
    # ------------------------------------------------------------

    if not subject_code or not subject_code.strip():
        raise ValueError(
            "Subject code is required."
        )

    if not subject_name or not subject_name.strip():
        raise ValueError(
            "Subject name is required."
        )

    if credits <= 0:
        raise ValueError(
            "Credits must be greater than zero."
        )

    # ------------------------------------------------------------
    # 4. Check subject code uniqueness
    # ------------------------------------------------------------

    existing_subject = Subject.query.filter_by(
        subject_code=subject_code.strip()
    ).first()

    if existing_subject is not None:
        raise ValueError(
            "Subject code already exists."
        )

    # ------------------------------------------------------------
    # 5. Create subject
    # ------------------------------------------------------------

    subject = Subject(
        department_id=department_id,
        created_by=user_id,
        subject_code=subject_code.strip(),
        subject_name=subject_name.strip(),
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


def get_my_subjects(user_id):
    faculty = Faculty.query.filter_by(user_id=user_id).first()

    if faculty is None:
        raise ValueError("Faculty profile not found.")

    subjects = Subject.query.filter_by(
        created_by=user_id
    ).order_by(
        Subject.subject_id.desc()
    ).all()

    return subjects