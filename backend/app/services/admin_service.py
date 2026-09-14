"""
Admin services.

Admin is responsible for creating subjects and assigning
subjects to Faculty.
"""

from app.extensions.database import db
from app.models import Faculty, FacultySubject, Subject, User, Role
from app.utils.password import hash_password


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

def get_all_users():
    """
    Return all platform users for Admin management.
    """
    return (
        User.query
        .join(Role)
        .order_by(User.user_id.asc())
        .all()
    )


def get_user_by_id(user_id):
    """
    Return a single user by ID.
    """
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise ValueError("Invalid user_id.")

    user = User.query.filter_by(user_id=user_id).first()

    if user is None:
        raise ValueError("User not found.")

    return user


def create_user(
    first_name,
    last_name,
    email,
    password,
    role_name,
    phone=None,
):
    """
    Admin creates a platform user.
    """

    if not first_name or not str(first_name).strip():
        raise ValueError("First name is required.")

    if not last_name or not str(last_name).strip():
        raise ValueError("Last name is required.")

    if not email or not str(email).strip():
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    if not role_name or not str(role_name).strip():
        raise ValueError("Role is required.")

    first_name = str(first_name).strip()
    last_name = str(last_name).strip()
    email = str(email).strip().lower()
    role_name = str(role_name).strip().upper()

    allowed_roles = {"ADMIN", "FACULTY", "STUDENT"}

    if role_name not in allowed_roles:
        raise ValueError(
            "Role must be ADMIN, FACULTY, or STUDENT."
        )

    existing_email = User.query.filter_by(email=email).first()

    if existing_email is not None:
        raise ValueError(
            "A user with this email already exists."
        )

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing_phone = User.query.filter_by(
                phone=phone
            ).first()

            if existing_phone is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

    role = Role.query.filter_by(role_name=role_name).first()

    if role is None:
        raise ValueError("Role not found.")

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        role_id=role.role_id,
        is_active=True,
    )

    try:
        db.session.add(user)
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def update_user(
    user_id,
    first_name=None,
    last_name=None,
    email=None,
    phone=None,
):
    """
    Admin updates basic user information.
    """

    user = get_user_by_id(user_id)

    if first_name is not None:
        first_name = str(first_name).strip()

        if not first_name:
            raise ValueError("First name cannot be empty.")

        user.first_name = first_name

    if last_name is not None:
        last_name = str(last_name).strip()

        if not last_name:
            raise ValueError("Last name cannot be empty.")

        user.last_name = last_name

    if email is not None:
        email = str(email).strip().lower()

        if not email:
            raise ValueError("Email cannot be empty.")

        existing = (
            User.query
            .filter(
                User.email == email,
                User.user_id != user.user_id,
            )
            .first()
        )

        if existing is not None:
            raise ValueError(
                "A user with this email already exists."
            )

        user.email = email

    if phone is not None:
        phone = str(phone).strip()

        if not phone:
            phone = None

        if phone is not None:
            existing = (
                User.query
                .filter(
                    User.phone == phone,
                    User.user_id != user.user_id,
                )
                .first()
            )

            if existing is not None:
                raise ValueError(
                    "A user with this phone number already exists."
                )

        user.phone = phone

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def set_user_status(user_id, is_active):
    """
    Activate or deactivate a user.

    An Admin cannot deactivate the last active Admin.
    """

    user = get_user_by_id(user_id)

    if not isinstance(is_active, bool):
        raise ValueError("is_active must be true or false.")

    if user.is_active == is_active:
        return user

    if not is_active and user.role.role_name == "ADMIN":
        active_admin_count = (
            User.query
            .join(Role)
            .filter(
                Role.role_name == "ADMIN",
                User.is_active.is_(True),
            )
            .count()
        )

        if active_admin_count <= 1:
            raise ValueError(
                "Cannot deactivate the last active Admin."
            )

    user.is_active = is_active

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def change_user_role(user_id, role_name):
    """
    Change a user's platform role.
    """

    user = get_user_by_id(user_id)

    role_name = str(role_name).strip().upper()

    allowed_roles = {"ADMIN", "FACULTY", "STUDENT"}

    if role_name not in allowed_roles:
        raise ValueError(
            "Role must be ADMIN, FACULTY, or STUDENT."
        )

    role = Role.query.filter_by(role_name=role_name).first()

    if role is None:
        raise ValueError("Role not found.")

    if user.role.role_name == "ADMIN" and role_name != "ADMIN":
        active_admin_count = (
            User.query
            .join(Role)
            .filter(
                Role.role_name == "ADMIN",
                User.is_active.is_(True),
            )
            .count()
        )

        if user.is_active and active_admin_count <= 1:
            raise ValueError(
                "Cannot remove the role from the last active Admin."
            )

    user.role_id = role.role_id

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise


def reset_user_password(user_id, new_password):
    """
    Admin resets a user's password.
    """

    user = get_user_by_id(user_id)

    if not new_password:
        raise ValueError("New password is required.")

    if len(str(new_password)) < 8:
        raise ValueError(
            "Password must be at least 8 characters long."
        )

    user.password_hash = hash_password(str(new_password))

    try:
        db.session.commit()
        return user

    except Exception:
        db.session.rollback()
        raise