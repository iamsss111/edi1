"""
Student answer routes.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.student_answer_service import (
    save_answer,
    get_answers,
)
from app.utils.rbac import role_required


student_answer_bp = Blueprint(
    'student_answer',
    __name__
)


@student_answer_bp.post(
    '/attempts/<int:attempt_id>/answers'
)
@role_required('STUDENT')
def save_answer_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required.',
        }), 400

    exam_question_id = data.get('exam_question_id')

    if exam_question_id is None:
        return jsonify({
            'success': False,
            'message': 'exam_question_id is required.',
        }), 400

    selected_option_id = data.get('selected_option_id')
    answer_text = data.get('answer_text')

    try:

        answer = save_answer(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
            exam_question_id=int(exam_question_id),
            selected_option_id=(
                int(selected_option_id)
                if selected_option_id is not None
                else None
            ),
            answer_text=answer_text,
        )

        return jsonify({
            'success': True,
            'message': 'Answer saved successfully.',
            'data': {
                'answer_id': answer.answer_id,
                'attempt_id': answer.attempt_id,
                'exam_question_id': answer.exam_question_id,
                'selected_option_id': answer.selected_option_id,
                'answer_text': answer.answer_text,
                'answered_at': (
                    answer.answered_at.isoformat()
                    if answer.answered_at
                    else None
                ),
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message == "You are not authorized to access this attempt.":
            status_code = 403

        elif message == "Question does not belong to this examination.":
            status_code = 400

        elif message == "Selected option does not belong to this question.":
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
            'message': 'An unexpected error occurred while saving the answer.',
        }), 500


@student_answer_bp.get(
    '/attempts/<int:attempt_id>/answers'
)
@role_required('STUDENT')
def get_answers_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    try:

        answers = get_answers(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
        )

        return jsonify({
            'success': True,
            'data': {
                'attempt_id': attempt_id,
                'answers': answers,
            },
        }), 200

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404
        elif message == "You are not authorized to access this attempt.":
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
                'An unexpected error occurred while retrieving answers.'
            ),
        }), 500