"""
Question delivery routes.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.question_delivery_service import (
    get_exam_questions
)
from app.services.adaptive_exam_service import (
    get_next_question
)
from app.utils.rbac import role_required


question_bp = Blueprint(
    'question',
    __name__
)


@question_bp.get('/exams/<int:exam_id>/questions')
@role_required('STUDENT')
def get_exam_questions_endpoint(exam_id: int):

    current_user_id = get_jwt_identity()

    try:
        data = get_exam_questions(
            user_id=int(current_user_id),
            exam_id=exam_id
        )

        return jsonify({
            'success': True,
            'data': data,
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
                'An unexpected error occurred while retrieving '
                'examination questions.'
            ),
        }), 500


@question_bp.get('/attempts/<int:attempt_id>/next-question')
@role_required('STUDENT')
def get_next_adaptive_question_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:
        data = get_next_question(
            user_id=int(current_user_id),
            attempt_id=attempt_id
        )

        return jsonify({
            'success': True,
            'data': data,
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': (
                'An unexpected error occurred while retrieving '
                'the next adaptive question.'
            ),
        }), 500