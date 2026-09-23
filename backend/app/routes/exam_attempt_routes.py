"""
Examination attempt routes.

Provides endpoints for students to start examinations.
"""
from datetime import timedelta
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.exam_attempt_service import start_exam
from app.utils.rbac import role_required


exam_attempt_bp = Blueprint(
    'exam_attempt',
    __name__,
)


@exam_attempt_bp.post('/exams/<int:exam_id>/start')
@role_required('STUDENT')
def start_exam_endpoint(exam_id: int):
    """
    Start an examination for the authenticated student.
    """

    current_user_id = get_jwt_identity()

    try:
        attempt = start_exam(
            user_id=int(current_user_id),
            exam_id=exam_id
        )

        return jsonify({
            'success': True,
            'message': 'Examination started successfully.',
            'data': {
                'attempt_id': attempt.attempt_id,
                'exam_id': exam_id,
                'registration_id': attempt.registration_id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'started_at': (
                    attempt.started_at.isoformat()
                    if attempt.started_at
                    else None
                ),
                'ends_at': (
                    (
                        attempt.started_at
                        + timedelta(minutes=attempt.registration.exam.duration_minutes)
                    ).isoformat()
                    if attempt.started_at
                    else None
                ),
                'adaptive_enabled': attempt.registration.exam.adaptive_enabled,
            },
        }), 200

    except ValueError as error:
        message = str(error)

        if message == "Examination not found.":
            status_code = 404
        elif message == "Student profile not found or inactive.":
            status_code = 403
        elif message == "You are not registered for this examination.":
            status_code = 403
        else:
            status_code = 400

        return jsonify({
            'success': False,
            'message': message,
        }), status_code

    except Exception:
        return jsonify({
            'success': False,
            'message': (
                'An unexpected error occurred while starting '
                'the examination.'
            ),
        }), 500