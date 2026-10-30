"""
Faculty question routes.

Provides endpoints for faculty question management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.extensions.database import db
from app.models import Question

from app.services.faculty_question_service import (
    create_question,
    get_my_questions,
    import_questions_csv,
)
from app.utils.rbac import role_required


faculty_question_bp = Blueprint('faculty_question', __name__)


@faculty_question_bp.post('/questions/import-csv')
@role_required('FACULTY')
def import_questions_csv_endpoint():
    if request.content_length and request.content_length > 5 * 1024 * 1024 + 64 * 1024:
        return jsonify({'success': False, 'message': 'CSV uploads must be 5 MB or smaller.'}), 413
    uploaded_file = request.files.get('file')
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({'success': False, 'message': 'Choose a CSV file to upload.'}), 400
    if not uploaded_file.filename.lower().endswith('.csv'):
        return jsonify({'success': False, 'message': 'Only .csv files are supported.'}), 400

    csv_bytes = uploaded_file.stream.read(5 * 1024 * 1024 + 1)
    if len(csv_bytes) > 5 * 1024 * 1024:
        return jsonify({'success': False, 'message': 'CSV files must be 5 MB or smaller.'}), 413

    try:
        imported = import_questions_csv(
            user_id=int(get_jwt_identity()),
            subject_id=request.form.get('subject_id'),
            csv_bytes=csv_bytes,
        )
        return jsonify({
            'success': True,
            'message': f'{len(imported)} questions imported into your question bank.',
            'data': {
                'imported_count': len(imported),
                'question_ids': [question.question_id for question in imported],
            },
        }), 201
    except (TypeError, ValueError) as error:
        return jsonify({'success': False, 'message': str(error)}), 400
    except Exception:
        return jsonify({'success': False, 'message': 'CSV import failed. No questions were saved.'}), 500


@faculty_question_bp.get('/questions/<int:question_id>')
@role_required('FACULTY')
def get_question_detail_endpoint(question_id: int):
    question = Question.query.filter_by(question_id=question_id, created_by=int(get_jwt_identity())).first()
    if question is None:
        return jsonify({'success': False, 'message': 'Question not found or not owned by you.'}), 404
    return jsonify({'success': True, 'data': {
        'question_id': question.question_id, 'subject_id': question.subject_id,
        'question_text': question.question_text, 'question_type': question.question_type,
        'marks': float(question.marks), 'difficulty': question.difficulty,
        'explanation': question.explanation,
        'options': [{'option_id': o.option_id, 'option_text': o.option_text, 'is_correct': o.is_correct, 'option_order': o.option_order} for o in question.options],
    }}), 200


@faculty_question_bp.put('/questions/<int:question_id>')
@role_required('FACULTY')
def update_question_endpoint(question_id: int):
    question = Question.query.filter_by(question_id=question_id, created_by=int(get_jwt_identity())).first()
    if question is None:
        return jsonify({'success': False, 'message': 'Question not found or not owned by you.'}), 404
    data = request.get_json(silent=True) or {}
    question_text = str(data.get('question_text', '')).strip()
    try:
        marks = float(data.get('marks'))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Marks must be a valid number.'}), 400
    if not question_text or marks <= 0:
        return jsonify({'success': False, 'message': 'Question text and positive marks are required.'}), 400
    question.question_text = question_text
    question.marks = marks
    question.explanation = (data.get('explanation') or '').strip() or None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Question update failed.'}), 500
    return jsonify({'success': True, 'message': 'Question updated.', 'data': {'question_id': question.question_id}}), 200


@faculty_question_bp.post('/questions')
@role_required('FACULTY')
def create_question_endpoint():
    """
    Create a new question for a subject currently assigned
    to the authenticated faculty member.
    """

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body must contain JSON data.'
        }), 400

    required_fields = [
        'subject_id',
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
            subject_id=data['subject_id'],
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
                'subject_id': question.subject_id,
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
    Retrieve active questions from subjects currently
    assigned to the authenticated faculty member.
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
                    'subject_id': question.subject_id,
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
