"""
Faculty subject routes.

Provides endpoints for faculty subject management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity


from app.services.faculty_subject_service import (create_subject, get_my_subjects)
from app.utils.rbac import role_required


faculty_subject_bp = Blueprint('faculty_subject', __name__)


@faculty_subject_bp.post('/subjects')
@role_required('FACULTY')
def create_subject_endpoint():
    """
    Create a new subject for the authenticated faculty member's department.
    """

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    required_fields = [
        'department_id',
        'subject_code',
        'subject_name',
        'credits',
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            'success': False,
            'message': 'Required fields are missing.',
            'fields': missing_fields,
        }), 400

    try:
        department_id = int(data['department_id'])
        credits = int(data['credits'])

        subject = create_subject(
            user_id=int(current_user_id),
            department_id=department_id,
            subject_code=data['subject_code'],
            subject_name=data['subject_name'],
            description=data.get('description'),
            credits=credits,
        )

        return jsonify({
            'success': True,
            'message': 'Subject created successfully.',
            'data': {
                'subject_id': subject.subject_id,
                'department_id': subject.department_id,
                'created_by': subject.created_by,
                'subject_code': subject.subject_code,
                'subject_name': subject.subject_name,
                'description': subject.description,
                'credits': subject.credits,
                'is_active': subject.is_active,
                'created_at': (
                    subject.created_at.isoformat()
                    if subject.created_at
                    else None
                ),
            },
        }), 201

    except (TypeError, ValueError) as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': (
                'An unexpected error occurred while creating the subject.'
            ),
        }), 500


@faculty_subject_bp.route('/subjects', methods=['GET'])
@role_required('FACULTY')
def get_my_subjects_route():

    try:
        user_id = int(get_jwt_identity())

        subjects = get_my_subjects(user_id)

        return jsonify({
            'success': True,
            'message': 'Subjects retrieved successfully.',
            'data': [
                {
                    'subject_id': subject.subject_id,
                    'department_id': subject.department_id,
                    'created_by': subject.created_by,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                    'description': subject.description,
                    'credits': subject.credits,
                    'is_active': subject.is_active,
                    'created_at': subject.created_at.isoformat()
                    if subject.created_at else None
                }
                for subject in subjects
            ]
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve subjects.'
        }), 500