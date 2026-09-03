"""
Result routes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.result_service import (
    generate_result,
    get_result,
)
from app.utils.rbac import role_required


result_bp = Blueprint(
    'result',
    __name__
)


@result_bp.post(
    '/attempts/<int:attempt_id>/result'
)
@role_required('STUDENT')
def generate_result_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:

        result = generate_result(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
        )

        return jsonify({
            'success': True,
            'message': 'Result generated successfully.',
            'data': {
                'result_id': result.result_id,
                'attempt_id': result.attempt_id,
                'total_marks': float(result.total_marks),
                'obtained_marks': float(result.obtained_marks),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,
                'published_at': (
                    result.published_at.isoformat()
                    if result.published_at
                    else None
                ),
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message in [
            "You are not authorized to access this result.",
            "Examination registration not found.",
        ]:
            status_code = 403

        elif message == "Examination not found.":
            status_code = 404

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
                'An unexpected error occurred while generating '
                'the result.'
            ),
        }), 500


@result_bp.get(
    '/attempts/<int:attempt_id>/result'
)
@role_required('STUDENT')
def get_result_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:

        result = get_result(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
        )

        return jsonify({
            'success': True,
            'data': {
                'result_id': result.result_id,
                'attempt_id': result.attempt_id,
                'total_marks': float(result.total_marks),
                'obtained_marks': float(result.obtained_marks),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,
                'published_at': (
                    result.published_at.isoformat()
                    if result.published_at
                    else None
                ),
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message == "You are not authorized to access this result.":
            status_code = 403

        elif message == "Result has not been generated yet.":
            status_code = 404

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
                'An unexpected error occurred while retrieving '
                'the result.'
            ),
        }), 500