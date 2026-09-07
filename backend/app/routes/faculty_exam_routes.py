from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_exam_service import (create_exam, get_my_exams, get_exam_details, get_exam_results)
from app.utils.rbac import role_required


faculty_exam_bp = Blueprint(
    'faculty_exam',
    __name__
)


@faculty_exam_bp.route('/exams', methods=['POST'])
@role_required('FACULTY')
def create_exam_route():

    data = request.get_json() or {}

    required_fields = [
        'subject_id',
        'title',
        'duration_minutes',
        'total_marks',
        'pass_marks'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'{field} is required.'
            }), 400

    try:
        user_id = int(get_jwt_identity())

        exam = create_exam(
            user_id=user_id,
            subject_id=data['subject_id'],
            title=data['title'],
            description=data.get('description'),
            duration_minutes=data['duration_minutes'],
            total_marks=data['total_marks'],
            pass_marks=data['pass_marks'],
            instructions=data.get('instructions')
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
                'status': exam.status,
                'instructions': exam.instructions
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
            'message': 'Failed to create exam.'
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


@faculty_exam_bp.route('/exams/<int:exam_id>', methods=['GET'])
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


@faculty_exam_bp.route(
    '/exams/<int:exam_id>/results',
    methods=['GET']
)
@role_required('FACULTY')
def get_exam_results_route(exam_id):
    """
    Retrieve results of students who attempted
    an exam created by the authenticated faculty member.
    """

    try:
        user_id = int(get_jwt_identity())

        exam, results = get_exam_results(
            user_id=user_id,
            exam_id=exam_id
        )

        return jsonify({
            'success': True,
            'message': 'Exam results retrieved successfully.',
            'data': {
                'exam_id': exam.exam_id,
                'title': exam.title,
                'total_marks': float(exam.total_marks),
                'pass_marks': float(exam.pass_marks),
                'results': [
                    {
                        'result_id': result.result_id,
                        'attempt_id': result.attempt_id,
                        'total_marks': float(result.total_marks),
                        'obtained_marks': float(
                            result.obtained_marks
                        ),
                        'percentage': float(result.percentage),
                        'grade': result.grade,
                        'result_status': result.result_status,
                        'published_at': (
                            result.published_at.isoformat()
                            if result.published_at
                            else None
                        ),
                    }
                    for result in results
                ]
            }
        }), 200

    except ValueError as error:
        message = str(error)

        if message == "Faculty profile not found.":
            status_code = 403

        elif message == (
            "Exam not found or you do not have access to it."
        ):
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
            'message': 'Failed to retrieve exam results.',
        }), 500