"""
User service.

Contains business logic related to users.
"""

from app.extensions.database import db


def save_user(user):
    """
    Save a user to the database.

    Args:
        user: User model instance.

    Returns:
        The saved User instance.
    """

    try:
        db.session.add(user)
        db.session.commit()

        return user

    except Exception:
        db.session.rollback()
        raise