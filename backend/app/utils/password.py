"""
Password hashing utilities.

Provides secure password hashing and verification using Argon2id.
"""

from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)


# PasswordHasher uses Argon2id by default.
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using Argon2id.

    Args:
        password: Plaintext password supplied by the user.

    Returns:
        Argon2id password hash.
    """

    if not password:
        raise ValueError("Password cannot be empty.")

    return password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """
    Verify a plaintext password against an Argon2id hash.

    Args:
        password_hash: Stored Argon2id password hash.
        password: Plaintext password supplied by the user.

    Returns:
        True if the password matches.
        False if the password does not match or the hash is invalid.
    """

    if not password_hash or not password:
        return False

    try:
        return password_hasher.verify(password_hash, password)

    except (
        VerifyMismatchError,
        VerificationError,
        InvalidHashError,
    ):
        return False