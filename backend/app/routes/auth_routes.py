"""
Authentication routes.

Provides registration and login endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.rbac import role_required

from app.services.auth_service import (
    register_user,
    authenticate_user,
)


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.post('/register')
def register():
    """
    Register a new student account.

    ---
    tags:
      - Authentication
    summary: Register a new student
    description: Creates a new student account. The role is automatically assigned as STUDENT.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - first_name
            - last_name
            - email
            - password
          properties:
            first_name:
              type: string
              example: Saniya
            last_name:
              type: string
              example: Patil
            email:
              type: string
              format: email
              example: student@example.com
            password:
              type: string
              format: password
              example: Password123
            phone:
              type: string
              example: "9876543210"
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid or incomplete request
      500:
        description: Unexpected server error
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

    ---
    tags:
      - Authentication
    summary: Login and obtain JWT token
    description: Authenticate a user and receive a JWT Bearer access token.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: student@example.com
            password:
              type: string
              format: password
              example: Password123
    responses:
      200:
        description: Login successful
      400:
        description: Email and password are required
      401:
        description: Invalid email or password
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
            'role': user.role.role_name
        }
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


@auth_bp.get('/me')
@jwt_required()
def get_current_user():
    """
    Return the identity of the currently authenticated user.

    ---
    tags:
      - Authentication
    summary: Get current authenticated user
    security:
      - BearerAuth: []
    produces:
      - application/json
    responses:
      200:
        description: JWT authentication successful
      401:
        description: Missing or invalid JWT token
    """

    current_user_id = get_jwt_identity()

    return jsonify({
        'success': True,
        'message': 'JWT authentication successful',
        'user_id': current_user_id
    }), 200

@auth_bp.get('/student-test')
@role_required('STUDENT')
def student_test():
    """
    Test endpoint accessible only to students.

    ---
    tags:
      - Authentication
      - RBAC
    summary: Test student role authorization
    description: Demonstrates role-based access control. Only users with the STUDENT role can access this endpoint.
    security:
      - BearerAuth: []
    produces:
      - application/json
    responses:
      200:
        description: Student RBAC access granted
      401:
        description: Missing or invalid JWT token
      403:
        description: User does not have the STUDENT role
    """
    return jsonify({
        'success': True,
        'message': 'Student RBAC access granted'
    }), 200