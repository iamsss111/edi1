"""
Examination submission routes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.exam_submission_service import submit_exam
from app.utils.rbac import role_required


exam_submission_bp = Blueprint(
    'exam_submission',
    __name__
)


@exam_submission_bp.post(
    '/attempts/<int:attempt_id>/submit'
)
@role_required('STUDENT')
def submit_exam_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:

        attempt = submit_exam(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
        )

        return jsonify({
            'success': True,
            'message': 'Examination submitted successfully.',
            'data': {
                'attempt_id': attempt.attempt_id,
                'status': attempt.status,
                'submitted_at': (
                    attempt.submitted_at.isoformat()
                    if attempt.submitted_at
                    else None
                ),
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message in [
            "You are not authorized to submit this attempt.",
            "Examination registration not found.",
        ]:
            status_code = 403

        elif message == (
            "This examination attempt has already been submitted."
        ):
            status_code = 400

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
                'An unexpected error occurred while submitting '
                'the examination.'
            ),
        }), 500