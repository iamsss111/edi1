"""
Role-Based Access Control utilities.
"""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def role_required(*allowed_roles):
    """
    Restrict an endpoint to users having one of the specified roles.

    Example:
        @role_required('Admin')
        @role_required('Admin', 'Faculty')
    """

    def decorator(function):
        @wraps(function)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()

            user_role = claims.get('role')

            if not user_role:
                return jsonify({
                    'success': False,
                    'message': 'User role not found in token'
                }), 403

            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': 'Access denied'
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator