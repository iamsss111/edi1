"""
Database session utilities.
"""

from app.extensions.database import db


def commit_session():
    """Commit the current database session."""
    db.session.commit()


def rollback_session():
    """Rollback the current database session."""
    db.session.rollback()


def close_session():
    """Close the current database session."""
    db.session.close()