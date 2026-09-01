"""
Authentication routes.

Provides registration and login endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.services.auth_service import (
    register_user,
    authenticate_user,
)


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.post('/register')
def register():
    """
    Register a new student account.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    required_fields = [
        'first_name',
        'last_name',
        'email',
        'password',
    ]

    missing_fields = [
        field for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            'success': False,
            'message': 'Required fields are missing.',
            'fields': missing_fields,
        }), 400

    try:
        user = register_user(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            role_name='STUDENT',
            phone=data.get('phone'),
        )

        return jsonify({
            'success': True,
            'message': 'User registered successfully.',
            'data': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role.role_name,
            },
        }), 201

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during registration.',
        }), 500


@auth_bp.post('/login')
def login():
    """
    Authenticate a user and return a JWT access token.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            'success': False,
            'message': 'Email and password are required.',
        }), 400

    user = authenticate_user(email, password)

    if user is None:
        return jsonify({
            'success': False,
            'message': 'Invalid email or password.',
        }), 401

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={
            'role': user.role.role_name,
            'email': user.email,
        },
    )

    return jsonify({
        'success': True,
        'message': 'Login successful.',
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role.role_name,
            },
        },
    }), 200