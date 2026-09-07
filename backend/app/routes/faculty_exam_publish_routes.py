from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.faculty_exam_publish_service import publish_exam
from app.utils.rbac import role_required


faculty_exam_publish_bp = Blueprint(
    'faculty_exam_publish',
    __name__
)


@faculty_exam_publish_bp.route(
    '/exams/<int:exam_id>/publish',
    methods=['POST']
)
@role_required('FACULTY')
def publish_exam_route(exam_id):

    try:
        user_id = int(get_jwt_identity())

        exam = publish_exam(
            user_id=user_id,
            exam_id=exam_id
        )

        return jsonify({
            'success': True,
            'message': 'Exam published successfully.',
            'data': {
                'exam_id': exam.exam_id,
                'title': exam.title,
                'status': exam.status
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
            'message': 'Failed to publish exam.'
        }), 500