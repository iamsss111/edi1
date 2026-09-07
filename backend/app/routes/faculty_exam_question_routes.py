from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_exam_question_service import add_question_to_exam
from app.utils.rbac import role_required


faculty_exam_question_bp = Blueprint(
    'faculty_exam_question',
    __name__
)


@faculty_exam_question_bp.route(
    '/exams/<int:exam_id>/questions',
    methods=['POST']
)
@role_required('FACULTY')
def add_question_to_exam_route(exam_id):

    data = request.get_json() or {}

    required_fields = [
        'question_id',
        'question_order',
        'marks'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'{field} is required.'
            }), 400

    try:
        user_id = int(get_jwt_identity())

        exam_question = add_question_to_exam(
            user_id=user_id,
            exam_id=exam_id,
            question_id=data['question_id'],
            question_order=data['question_order'],
            marks=data['marks']
        )

        return jsonify({
            'success': True,
            'message': 'Question added to exam successfully.',
            'data': {
                'exam_question_id': exam_question.exam_question_id,
                'exam_id': exam_question.exam_id,
                'question_id': exam_question.question_id,
                'question_order': exam_question.question_order,
                'marks': float(exam_question.marks)
            }
        }), 201

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to add question to exam.'
        }), 500