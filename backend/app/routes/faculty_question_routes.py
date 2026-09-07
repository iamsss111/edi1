"""
Faculty question routes.

Provides endpoints for faculty question management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_question_service import (create_question, get_my_questions)
from app.utils.rbac import role_required


faculty_question_bp = Blueprint('faculty_question', __name__)


@faculty_question_bp.post('/questions')
@role_required('FACULTY')
def create_question_endpoint():
    """
    Create a new question for the authenticated faculty member.
    """

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    required_fields = [
        'question_text',
        'question_type',
        'marks',
        'difficulty',
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
        question = create_question(
            user_id=int(current_user_id),
            question_text=data['question_text'],
            question_type=data['question_type'],
            marks=data['marks'],
            difficulty=data['difficulty'],
            explanation=data.get('explanation'),
        )

        return jsonify({
            'success': True,
            'message': 'Question created successfully.',
            'data': {
                'question_id': question.question_id,
                'created_by': question.created_by,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'marks': float(question.marks),
                'difficulty': question.difficulty,
                'explanation': question.explanation,
                'is_active': question.is_active,
                'created_at': (
                    question.created_at.isoformat()
                    if question.created_at
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
                'An unexpected error occurred while creating the question.'
            ),
        }), 500


@faculty_question_bp.route('/questions', methods=['GET'])
@role_required('FACULTY')
def get_my_questions_route():
    """
    Retrieve questions created by the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        questions = get_my_questions(user_id)

        return jsonify({
            'success': True,
            'message': 'Questions retrieved successfully.',
            'data': [
                {
                    'question_id': question.question_id,
                    'created_by': question.created_by,
                    'question_text': question.question_text,
                    'question_type': question.question_type,
                    'marks': float(question.marks),
                    'difficulty': question.difficulty,
                    'explanation': question.explanation,
                    'is_active': question.is_active,
                    'created_at': (
                        question.created_at.isoformat()
                        if question.created_at
                        else None
                    ),
                }
                for question in questions
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
            'message': 'Failed to retrieve questions.',
        }), 500