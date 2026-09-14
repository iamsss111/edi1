from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_exam_schedule_service import (
    create_exam_schedule,
    get_exam_schedule
)
from app.utils.rbac import role_required


faculty_exam_schedule_bp = Blueprint(
    'faculty_exam_schedule',
    __name__
)


@faculty_exam_schedule_bp.route(
    '/exams/<int:exam_id>/schedule',
    methods=['POST']
)
@role_required('FACULTY')
def create_exam_schedule_route(exam_id):

    data = request.get_json() or {}

    required_fields = [
        'start_time',
        'end_time',
        'max_attempts',
        'is_active'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'{field} is required.'
            }), 400

    try:
        user_id = int(get_jwt_identity())

        schedule = create_exam_schedule(
            user_id=user_id,
            exam_id=exam_id,
            start_time=data['start_time'],
            end_time=data['end_time'],
            room=data.get('room'),
            max_attempts=data['max_attempts'],
            is_active=data['is_active']
        )

        return jsonify({
            'success': True,
            'message': 'Exam schedule created successfully.',
            'data': {
                'schedule_id': schedule.schedule_id,
                'exam_id': schedule.exam_id,
                'start_time': schedule.start_time.isoformat(),
                'end_time': schedule.end_time.isoformat(),
                'room': schedule.room,
                'max_attempts': schedule.max_attempts,
                'is_active': schedule.is_active
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
            'message': 'Failed to create exam schedule.'
        }), 500
@faculty_exam_schedule_bp.route(
    '/exams/<int:exam_id>/schedule',
    methods=['GET']
)
@role_required('FACULTY')
def get_exam_schedule_route(exam_id):
    try:
        user_id = int(get_jwt_identity())

        schedule = get_exam_schedule(
            user_id=user_id,
            exam_id=exam_id
        )

        if schedule is None:
            return jsonify({
                'success': False,
                'message': 'No schedule found for this exam.'
            }), 404

        return jsonify({
            'success': True,
            'message': 'Exam schedule retrieved successfully.',
            'data': {
                'schedule_id': schedule.schedule_id,
                'exam_id': schedule.exam_id,
                'start_time': schedule.start_time.isoformat(),
                'end_time': schedule.end_time.isoformat(),
                'room': schedule.room,
                'max_attempts': schedule.max_attempts,
                'is_active': schedule.is_active
            }
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve exam schedule.'
        }), 500   