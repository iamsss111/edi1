"""
Evaluation routes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.evaluation_service import evaluate_attempt
from app.utils.rbac import role_required


evaluation_bp = Blueprint(
    'evaluation',
    __name__
)


@evaluation_bp.post(
    '/attempts/<int:attempt_id>/evaluate'
)
@role_required('STUDENT')
def evaluate_attempt_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:

        attempt = evaluate_attempt(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
        )

        return jsonify({
            'success': True,
            'message': 'Examination evaluated successfully.',
            'data': {
                'attempt_id': attempt.attempt_id,
                'status': attempt.status,
                'score': (
                    float(attempt.score)
                    if attempt.score is not None
                    else None
                ),
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message in [
            "You are not authorized to evaluate this attempt.",
            "Examination registration not found.",
        ]:
            status_code = 403

        elif message == (
            "Only submitted examination attempts can be evaluated."
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
                'An unexpected error occurred while evaluating '
                'the examination.'
            ),
        }), 500