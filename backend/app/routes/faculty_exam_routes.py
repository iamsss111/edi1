"""
Faculty exam routes.

Provides endpoints for faculty exam management.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app.extensions.database import db

from app.services.faculty_exam_service import (
    create_exam,
    get_my_exams,
    get_exam_details,
    get_exam_results,
)
from app.services import faculty_lifecycle_service
from app.utils.rbac import role_required


faculty_exam_bp = Blueprint('faculty_exam', __name__)


@faculty_exam_bp.put('/exams/<int:exam_id>')
@role_required('FACULTY')
def update_exam_endpoint(exam_id: int):
    try:
        exam = get_exam_details(int(get_jwt_identity()), exam_id)
        if exam.status != 'Draft' or exam.candidate_registrations:
            return jsonify({'success': False, 'message': 'Only draft exams with no registrations can be edited.'}), 409
        data = request.get_json(silent=True) or {}
        title = str(data.get('title', '')).strip()
        try:
            duration = int(data.get('duration_minutes'))
            total_marks = float(data.get('total_marks'))
            pass_marks = float(data.get('pass_marks'))
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'Duration and marks must be valid numbers.'}), 400
        if not title or duration <= 0 or total_marks <= 0 or pass_marks < 0 or pass_marks > total_marks:
            return jsonify({'success': False, 'message': 'Enter a title, positive duration and total marks, and valid passing marks.'}), 400
        exam.title = title
        exam.duration_minutes = duration
        exam.total_marks = total_marks
        exam.pass_marks = pass_marks
        exam.instructions = data.get('instructions')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Exam updated.', 'data': {'exam_id': exam.exam_id, 'title': exam.title}}), 200
    except ValueError as error:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(error)}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Exam update failed.'}), 500


@faculty_exam_bp.post('/exams')
@role_required('FACULTY')
def create_exam_endpoint():
    """
    Create an exam for a subject currently assigned
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
        'title',
        'duration_minutes',
        'total_marks',
        'pass_marks',
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
        exam = create_exam(
            user_id=int(current_user_id),
            subject_id=data['subject_id'],
            title=data['title'],
            duration_minutes=data['duration_minutes'],
            total_marks=data['total_marks'],
            pass_marks=data['pass_marks'],
            adaptive_enabled=data.get(
                'adaptive_enabled',
                False
            ),
            initial_difficulty=data.get(
                'initial_difficulty',
                'Medium'
            ),
        )

        return jsonify({
            'success': True,
            'message': 'Exam created successfully.',
            'data': {
                'exam_id': exam.exam_id,
                'subject_id': exam.subject_id,
                'created_by': exam.created_by,
                'title': exam.title,
                'description': exam.description,
                'duration_minutes': exam.duration_minutes,
                'total_marks': float(exam.total_marks),
                'pass_marks': float(exam.pass_marks),
                'adaptive_enabled': exam.adaptive_enabled,
                'initial_difficulty': exam.initial_difficulty,
                'status': exam.status,
                'instructions': exam.instructions,
                'created_at': (
                    exam.created_at.isoformat()
                    if exam.created_at
                    else None
                ),
                'updated_at': (
                    exam.updated_at.isoformat()
                    if exam.updated_at
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
                'An unexpected error occurred while creating the exam.'
            ),
        }), 500


@faculty_exam_bp.route('/exams', methods=['GET'])
@role_required('FACULTY')
def get_my_exams_route():
    """
    Retrieve exams created by the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        exams = get_my_exams(user_id)

        return jsonify({
            'success': True,
            'message': 'Exams retrieved successfully.',
            'data': [
                {
                    'exam_id': exam.exam_id,
                    'subject_id': exam.subject_id,
                    'created_by': exam.created_by,
                    'title': exam.title,
                    'description': exam.description,
                    'duration_minutes': exam.duration_minutes,
                    'total_marks': float(exam.total_marks),
                    'pass_marks': float(exam.pass_marks),
                    'adaptive_enabled': exam.adaptive_enabled,
                    'initial_difficulty': exam.initial_difficulty,
                    'status': exam.status,
                    'instructions': exam.instructions,
                    'created_at': (
                        exam.created_at.isoformat()
                        if exam.created_at
                        else None
                    ),
                    'updated_at': (
                        exam.updated_at.isoformat()
                        if exam.updated_at
                        else None
                    ),
                }
                for exam in exams
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
            'message': 'Failed to retrieve exams.',
        }), 500


@faculty_exam_bp.get('/exams/<int:exam_id>')
@role_required('FACULTY')
def get_exam_details_route(exam_id):
    """
    Retrieve details of an exam created by the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        exam = get_exam_details(
            user_id=user_id,
            exam_id=exam_id
        )

        return jsonify({
            'success': True,
            'message': 'Exam details retrieved successfully.',
            'data': {
                'exam_id': exam.exam_id,
                'subject_id': exam.subject_id,
                'created_by': exam.created_by,
                'title': exam.title,
                'description': exam.description,
                'duration_minutes': exam.duration_minutes,
                'total_marks': float(exam.total_marks),
                'pass_marks': float(exam.pass_marks),
                'adaptive_enabled': exam.adaptive_enabled,
                'initial_difficulty': exam.initial_difficulty,
                'status': exam.status,
                'instructions': exam.instructions,
                'created_at': (
                    exam.created_at.isoformat()
                    if exam.created_at
                    else None
                ),
                'updated_at': (
                    exam.updated_at.isoformat()
                    if exam.updated_at
                    else None
                ),
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve exam details.',
        }), 500


@faculty_exam_bp.get('/exams/<int:exam_id>/results')
@role_required('FACULTY')
def get_exam_results_route(exam_id):
    """
    Retrieve results for an exam created by the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        exam, results = faculty_lifecycle_service.faculty_results(user_id, exam_id)

        return jsonify({
            'success': True,
            'data': {
                'exam_id': exam.exam_id,
                'exam_title': exam.title,
                'total_marks': float(exam.total_marks),
                'pass_marks': float(exam.pass_marks),
                'results': [faculty_lifecycle_service.serialize_result(result) for result in results],
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except LookupError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve exam results.',
        }), 500
