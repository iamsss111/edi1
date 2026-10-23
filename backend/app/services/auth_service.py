"""
Authentication service.

Contains business logic for user registration and authentication.
"""

from app.extensions.database import db
from app.models import User, Role, Student, Department
from app.utils.password import hash_password, verify_password


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role_name: str = 'STUDENT',
    phone: str | None = None,
    department_id: int | None = None,
    roll_number: str | None = None,
    enrollment_number: str | None = None,
    year: int | None = None,
    semester: int | None = None,
) -> User:
    """
    Register a new user.

    Args:
        first_name: User's first name.
        last_name: User's last name.
        email: User's email address.
        password: Plaintext password.
        role_name: Role to assign to the user.
        phone: Optional phone number.

    Returns:
        Newly created User instance.

    Raises:
        ValueError: If validation fails.
    """

    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()

    if not first_name:
        raise ValueError("First name is required.")

    if not last_name:
        raise ValueError("Last name is required.")

    if not email:
        raise ValueError("Email is required.")

    if not password:
        raise ValueError("Password is required.")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        raise ValueError("A user with this email already exists.")

    role = Role.query.filter_by(role_name=role_name).first()

    if role is None:
        raise ValueError(f"Role '{role_name}' does not exist.")

    profile_values = (department_id, roll_number, enrollment_number, year, semester)
    if role_name == 'STUDENT' and any(value is not None for value in profile_values) and not all(value is not None for value in profile_values):
        raise ValueError('Department, roll number, enrollment number, year, and semester are all required for student registration.')
    if role_name == 'STUDENT' and all(value is not None for value in profile_values):
        try:
            department_id, year, semester = int(department_id), int(year), int(semester)
        except (TypeError, ValueError):
            raise ValueError('Department, year, and semester must be valid numbers.')
        roll_number, enrollment_number = str(roll_number).strip(), str(enrollment_number).strip()
        if not roll_number or not enrollment_number or year <= 0 or semester <= 0:
            raise ValueError('Student identifiers and academic year/semester must be valid.')
        if Department.query.filter_by(department_id=department_id, is_active=True).first() is None:
            raise ValueError('Choose an active department.')
        if Student.query.filter_by(roll_number=roll_number).first() or Student.query.filter_by(enrollment_number=enrollment_number).first():
            raise ValueError('That roll or enrollment number is already in use.')

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
        db.session.flush()
        if role_name == 'STUDENT' and all(value is not None for value in profile_values):
            student = Student(
                user_id=user.user_id,
                department_id=int(department_id),
                roll_number=str(roll_number).strip(),
                enrollment_number=str(enrollment_number).strip(),
                year=int(year),
                semester=int(semester),
                is_active=True,
            )
            if not student.roll_number or not student.enrollment_number or student.year <= 0 or student.semester <= 0:
                raise ValueError('Student identifiers and academic year/semester must be valid.')
            db.session.add(student)
        db.session.commit()

        return user

    except Exception:
        db.session.rollback()
        raise


def authenticate_user(email: str, password: str) -> User | None:
    """
    Authenticate a user using email and password.

    Args:
        email: User's email address.
        password: Plaintext password.

    Returns:
        Authenticated User instance, or None if authentication fails.
    """

    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(user.password_hash, password):
        return None

    return user
