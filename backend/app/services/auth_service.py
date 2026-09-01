"""
Authentication service.

Contains business logic for user registration and authentication.
"""

from app.extensions.database import db
from app.models import User, Role
from app.utils.password import hash_password, verify_password


def register_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    role_name: str = 'STUDENT',
    phone: str | None = None,
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