"""
Admin Routes

Admin manages subjects and Faculty subject assignments.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.admin_service import (
    create_subject,
    get_all_subjects,
    get_all_faculty,
    assign_subject_to_faculty,
    get_faculty_subjects,
    deactivate_faculty_subject,
)
from app.utils.rbac import role_required


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/subjects', methods=['POST'])
@role_required('ADMIN')
def create_subject_endpoint():

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        subject = create_subject(
            user_id=user_id,
            department_id=data.get('department_id'),
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            description=data.get('description'),
            credits=data.get('credits'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject created successfully.',
            'data': {
                'subject_id': subject.subject_id,
                'subject_code': subject.subject_code,
                'subject_name': subject.subject_name,
                'description': subject.description,
                'credits': subject.credits,
                'department_id': subject.department_id,
                'is_active': subject.is_active,
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
            'message': 'Failed to create subject.',
        }), 500


@admin_bp.route('/admin/subjects', methods=['GET'])
@role_required('ADMIN')
def get_all_subjects_endpoint():

    try:
        subjects = get_all_subjects()

        return jsonify({
            'success': True,
            'message': 'Subjects retrieved successfully.',
            'data': [
                {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                    'description': subject.description,
                    'credits': subject.credits,
                    'department_id': subject.department_id,
                    'is_active': subject.is_active,
                }
                for subject in subjects
            ],
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve subjects.',
        }), 500


@admin_bp.route('/admin/faculty', methods=['GET'])
@role_required('ADMIN')
def get_all_faculty_endpoint():

    try:
        faculty_list = get_all_faculty()

        return jsonify({
            'success': True,
            'message': 'Faculty retrieved successfully.',
            'data': [
                {
                    'faculty_id': faculty.faculty_id,
                    'user_id': faculty.user_id,
                    'employee_number': faculty.employee_number,
                    'designation': faculty.designation,
                    'department_id': faculty.department_id,
                    'email': faculty.user.email,
                    'first_name': faculty.user.first_name,
                    'last_name': faculty.user.last_name,
                }
                for faculty in faculty_list
            ],
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve Faculty.',
        }), 500


@admin_bp.route(
    '/admin/faculty/<int:faculty_id>/subjects',
    methods=['POST']
)
@role_required('ADMIN')
def assign_subject_endpoint(faculty_id):

    try:
        data = request.get_json() or {}

        assignment = assign_subject_to_faculty(
            faculty_id=faculty_id,
            subject_id=data.get('subject_id'),
            semester=data.get('semester'),
            year=data.get('year'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject assigned to Faculty successfully.',
            'data': {
                'faculty_subject_id': assignment.faculty_subject_id,
                'faculty_id': assignment.faculty_id,
                'subject_id': assignment.subject_id,
                'semester': assignment.semester,
                'year': assignment.year,
                'is_active': assignment.is_active,
                'assigned_at': (
                    assignment.assigned_at.isoformat()
                    if assignment.assigned_at
                    else None
                ),
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
            'message': 'Failed to assign subject.',
        }), 500


@admin_bp.route(
    '/admin/faculty/<int:faculty_id>/subjects',
    methods=['GET']
)
@role_required('ADMIN')
def get_faculty_subjects_endpoint(faculty_id):

    try:
        assignments = get_faculty_subjects(faculty_id)

        return jsonify({
            'success': True,
            'message': 'Faculty subject assignments retrieved successfully.',
            'data': [
                {
                    'faculty_subject_id': assignment.faculty_subject_id,
                    'faculty_id': assignment.faculty_id,
                    'subject_id': assignment.subject_id,
                    'subject_code': assignment.subject.subject_code,
                    'subject_name': assignment.subject.subject_name,
                    'semester': assignment.semester,
                    'year': assignment.year,
                    'is_active': assignment.is_active,
                    'assigned_at': (
                        assignment.assigned_at.isoformat()
                        if assignment.assigned_at
                        else None
                    ),
                }
                for assignment in assignments
            ],
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve Faculty subjects.',
        }), 500


@admin_bp.route(
    '/admin/faculty-subjects/<int:faculty_subject_id>/deactivate',
    methods=['PATCH']
)
@role_required('ADMIN')
def deactivate_faculty_subject_endpoint(faculty_subject_id):

    try:
        assignment = deactivate_faculty_subject(
            faculty_subject_id
        )

        return jsonify({
            'success': True,
            'message': 'Faculty subject assignment deactivated successfully.',
            'data': {
                'faculty_subject_id': assignment.faculty_subject_id,
                'faculty_id': assignment.faculty_id,
                'subject_id': assignment.subject_id,
                'semester': assignment.semester,
                'year': assignment.year,
                'is_active': assignment.is_active,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to deactivate Faculty subject assignment.',
        }), 500