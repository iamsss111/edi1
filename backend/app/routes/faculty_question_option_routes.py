"""
Faculty question option routes.

Provides endpoints for faculty question option management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_question_option_service import (
    create_question_option,
)
from app.utils.rbac import role_required


faculty_question_option_bp = Blueprint(
    'faculty_question_option',
    __name__
)


@faculty_question_option_bp.post(
    '/questions/<int:question_id>/options'
)
@role_required('FACULTY')
def create_question_option_endpoint(question_id: int):
    """
    Create an option for a faculty-owned question.
    """

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    required_fields = [
        'option_text',
        'option_order',
        'is_correct',
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
        option = create_question_option(
            user_id=int(current_user_id),
            question_id=question_id,
            option_text=data['option_text'],
            option_order=data['option_order'],
            is_correct=data['is_correct'],
        )

        return jsonify({
            'success': True,
            'message': 'Question option created successfully.',
            'data': {
                'option_id': option.option_id,
                'question_id': option.question_id,
                'option_text': option.option_text,
                'is_correct': option.is_correct,
                'option_order': option.option_order,
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
                'An unexpected error occurred while creating '
                'the question option.'
            ),
        }), 500