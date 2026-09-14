"""
Faculty Subject Routes

Faculty can view subjects currently assigned to them.

Subjects are created and assigned by Admin.
Faculty cannot create, edit, or delete subjects.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_subject_service import get_my_subjects
from app.utils.rbac import role_required


faculty_subject_bp = Blueprint(
    'faculty_subject',
    __name__
)


@faculty_subject_bp.route('/subjects', methods=['GET'])
@role_required('FACULTY')
def get_my_subjects_route():
    """
    Retrieve subjects currently assigned to the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        assignments = get_my_subjects(user_id)

        return jsonify({
            'success': True,
            'message': 'Subjects retrieved successfully.',
            'data': [
                {
                    'faculty_subject_id': assignment.faculty_subject_id,
                    'subject_id': assignment.subject.subject_id,
                    'subject_code': assignment.subject.subject_code,
                    'subject_name': assignment.subject.subject_name,
                    'description': assignment.subject.description,
                    'credits': assignment.subject.credits,
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
            'message': 'Failed to retrieve subjects.',
        }), 500