"""
Admin Routes

Admin manages subjects and Faculty subject assignments.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.services import admin_service
from app.services.admin_service import get_dashboard_statistics

from app.services.admin_service import (
    create_subject,
    get_all_subjects,
    get_all_faculty,
    assign_subject_to_faculty,
    get_faculty_subjects,
    deactivate_faculty_subject,
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    set_user_status,
    change_user_role,
    reset_user_password,
    get_all_exams,
    get_exam_by_id,
    update_subject,
    set_subject_status,
    get_all_questions,
    get_question_by_id,
    set_question_status,
    get_all_exam_registrations,
    get_exam_registrations,
    get_registration_by_id,
    get_all_attempts,
    get_exam_attempts,
    get_attempt_by_id,
    get_attempt_integrity_events,
    get_all_results,
    get_exam_results_for_admin,
    get_result_by_id,
    get_all_audit_logs,
    get_audit_log_by_id,
)
from app.utils.rbac import role_required


admin_bp = Blueprint('admin', __name__)
@admin_bp.route('/admin/exams', methods=['GET'])
@role_required('ADMIN')
def admin_get_all_exams():
    try:
        results = admin_service.get_all_exams()

        data = []

        for exam, subject, creator, question_count, candidate_count in results:
            schedules = []

            for schedule in exam.schedules:
                schedules.append({
                    "schedule_id": schedule.schedule_id,
                    "start_time": (
                        schedule.start_time.isoformat()
                        if schedule.start_time else None
                    ),
                    "end_time": (
                        schedule.end_time.isoformat()
                        if schedule.end_time else None
                    ),
                    "room": schedule.room,
                    "max_attempts": schedule.max_attempts,
                    "is_active": schedule.is_active
                })

            data.append({
                "exam_id": exam.exam_id,
                "title": exam.title,
                "description": exam.description,

                "subject": {
                    "subject_id": subject.subject_id,
                    "subject_code": subject.subject_code,
                    "subject_name": subject.subject_name
                },

                "faculty": {
                    "user_id": creator.user_id,
                    "first_name": creator.first_name,
                    "last_name": creator.last_name,
                    "email": creator.email
                },

                "duration_minutes": exam.duration_minutes,
                "total_marks": float(exam.total_marks),
                "pass_marks": float(exam.pass_marks),
                "status": exam.status,
                "instructions": exam.instructions,

                "question_count": int(question_count),
                "candidate_count": int(candidate_count),

                "schedules": schedules,

                "created_at": (
                    exam.created_at.isoformat()
                    if exam.created_at else None
                ),
                "updated_at": (
                    exam.updated_at.isoformat()
                    if exam.updated_at else None
                )
            })

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


@admin_bp.route('/admin/exams/<int:exam_id>', methods=['GET'])
@role_required('ADMIN')
def admin_get_exam(exam_id):
    try:
        exam, subject, creator, question_count, candidate_count = (
            admin_service.get_exam_by_id(exam_id)
        )

        schedules = []

        for schedule in exam.schedules:
            schedules.append({
                "schedule_id": schedule.schedule_id,
                "start_time": (
                    schedule.start_time.isoformat()
                    if schedule.start_time else None
                ),
                "end_time": (
                    schedule.end_time.isoformat()
                    if schedule.end_time else None
                ),
                "room": schedule.room,
                "max_attempts": schedule.max_attempts,
                "is_active": schedule.is_active
            })

        return jsonify({
            "success": True,
            "data": {
                "exam_id": exam.exam_id,
                "title": exam.title,
                "description": exam.description,

                "subject": {
                    "subject_id": subject.subject_id,
                    "subject_code": subject.subject_code,
                    "subject_name": subject.subject_name
                },

                "faculty": {
                    "user_id": creator.user_id,
                    "first_name": creator.first_name,
                    "last_name": creator.last_name,
                    "email": creator.email
                },

                "duration_minutes": exam.duration_minutes,
                "total_marks": float(exam.total_marks),
                "pass_marks": float(exam.pass_marks),
                "status": exam.status,
                "instructions": exam.instructions,

                "question_count": int(question_count),
                "candidate_count": int(candidate_count),

                "schedules": schedules,

                "created_at": (
                    exam.created_at.isoformat()
                    if exam.created_at else None
                ),
                "updated_at": (
                    exam.updated_at.isoformat()
                    if exam.updated_at else None
                )
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

@admin_bp.route('/admin/subjects', methods=['POST'])
@role_required('ADMIN')
def create_subject_endpoint():

    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        subject = create_subject(
            user_id=user_id,
            department_id=data.get('department_id'),
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            description=data.get('description'),
            credits=data.get('credits'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject created successfully.',
            'data': {
                'subject_id': subject.subject_id,
                'subject_code': subject.subject_code,
                'subject_name': subject.subject_name,
                'description': subject.description,
                'credits': subject.credits,
                'department_id': subject.department_id,
                'is_active': subject.is_active,
            },
        }), 201

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to create subject.',
        }), 500


@admin_bp.route('/admin/subjects', methods=['GET'])
@role_required('ADMIN')
def get_all_subjects_endpoint():

    try:
        subjects = get_all_subjects()

        return jsonify({
            'success': True,
            'message': 'Subjects retrieved successfully.',
            'data': [
                {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                    'description': subject.description,
                    'credits': subject.credits,
                    'department_id': subject.department_id,
                    'is_active': subject.is_active,
                }
                for subject in subjects
            ],
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve subjects.',
        }), 500

@admin_bp.route('/admin/subjects/<int:subject_id>', methods=['PUT'])
@role_required('ADMIN')
def update_subject_endpoint(subject_id):

    try:
        data = request.get_json() or {}

        subject = update_subject(
            subject_id=subject_id,
            department_id=data.get('department_id'),
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            description=data.get('description'),
            credits=data.get('credits'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject updated successfully.',
            'data': {
                'subject_id': subject.subject_id,
                'subject_code': subject.subject_code,
                'subject_name': subject.subject_name,
                'description': subject.description,
                'credits': subject.credits,
                'department_id': subject.department_id,
                'is_active': subject.is_active,
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
            'message': 'Failed to update subject.',
        }), 500


@admin_bp.route(
    '/admin/subjects/<int:subject_id>/status',
    methods=['PATCH']
)
@role_required('ADMIN')
def set_subject_status_endpoint(subject_id):

    try:
        data = request.get_json() or {}

        if 'is_active' not in data:
            return jsonify({
                'success': False,
                'message': 'is_active is required.',
            }), 400

        subject = set_subject_status(
            subject_id=subject_id,
            is_active=data.get('is_active'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject status updated successfully.',
            'data': {
                'subject_id': subject.subject_id,
                'subject_code': subject.subject_code,
                'subject_name': subject.subject_name,
                'is_active': subject.is_active,
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
            'message': 'Failed to update subject status.',
        }), 500

@admin_bp.route('/admin/faculty', methods=['GET'])
@role_required('ADMIN')
def get_all_faculty_endpoint():
    """Get all Faculty members."""

    faculty_list = admin_service.get_all_faculty()

    data = []

    for faculty in faculty_list:
        data.append({
            'faculty_id': faculty.faculty_id,
            'user_id': faculty.user_id,
            'first_name': faculty.user.first_name,
            'last_name': faculty.user.last_name,
            'email': faculty.user.email,
            'phone': faculty.user.phone,
            'employee_number': faculty.employee_number,
            'designation': faculty.designation,
            'department_id': faculty.department_id,
            'department_name': faculty.department.department_name,
            'is_active': faculty.user.is_active,
        })

    return jsonify({
        'success': True,
        'data': data
    }), 200


@admin_bp.route(
    '/admin/faculty/<int:faculty_id>/subjects',
    methods=['POST']
)
@role_required('ADMIN')
def assign_subject_endpoint(faculty_id):

    try:
        data = request.get_json() or {}

        assignment = assign_subject_to_faculty(
            faculty_id=faculty_id,
            subject_id=data.get('subject_id'),
            semester=data.get('semester'),
            year=data.get('year'),
        )

        return jsonify({
            'success': True,
            'message': 'Subject assigned to Faculty successfully.',
            'data': {
                'faculty_subject_id': assignment.faculty_subject_id,
                'faculty_id': assignment.faculty_id,
                'subject_id': assignment.subject_id,
                'semester': assignment.semester,
                'year': assignment.year,
                'is_active': assignment.is_active,
                'assigned_at': (
                    assignment.assigned_at.isoformat()
                    if assignment.assigned_at
                    else None
                ),
            },
        }), 201

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to assign subject.',
        }), 500


@admin_bp.route(
    '/admin/faculty/<int:faculty_id>/subjects',
    methods=['GET']
)
@role_required('ADMIN')
def get_faculty_subjects_endpoint(faculty_id):

    try:
        assignments = get_faculty_subjects(faculty_id)

        return jsonify({
            'success': True,
            'message': 'Faculty subject assignments retrieved successfully.',
            'data': [
                {
                    'faculty_subject_id': assignment.faculty_subject_id,
                    'faculty_id': assignment.faculty_id,
                    'subject_id': assignment.subject_id,
                    'subject_code': assignment.subject.subject_code,
                    'subject_name': assignment.subject.subject_name,
                    'semester': assignment.semester,
                    'year': assignment.year,
                    'is_active': assignment.is_active,
                    'assigned_at': (
                        assignment.assigned_at.isoformat()
                        if assignment.assigned_at
                        else None
                    ),
                }
                for assignment in assignments
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
            'message': 'Failed to retrieve Faculty subjects.',
        }), 500


@admin_bp.route(
    '/admin/faculty-subjects/<int:faculty_subject_id>/deactivate',
    methods=['PATCH']
)
@role_required('ADMIN')
def deactivate_faculty_subject_endpoint(faculty_subject_id):

    try:
        assignment = deactivate_faculty_subject(
            faculty_subject_id
        )

        return jsonify({
            'success': True,
            'message': 'Faculty subject assignment deactivated successfully.',
            'data': {
                'faculty_subject_id': assignment.faculty_subject_id,
                'faculty_id': assignment.faculty_id,
                'subject_id': assignment.subject_id,
                'semester': assignment.semester,
                'year': assignment.year,
                'is_active': assignment.is_active,
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
            'message': 'Failed to deactivate Faculty subject assignment.',
        }), 500


@admin_bp.route('/admin/users', methods=['GET'])
@role_required('ADMIN')
def get_all_users_endpoint():

    try:
        users = get_all_users()

        return jsonify({
            'success': True,
            'message': 'Users retrieved successfully.',
            'data': [
                {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role.role_name,
                    'role_id': user.role_id,
                    'is_active': user.is_active,
                    'created_at': (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    ),
                    'updated_at': (
                        user.updated_at.isoformat()
                        if user.updated_at
                        else None
                    ),
                }
                for user in users
            ],
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve users.',
        }), 500


@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@role_required('ADMIN')
def get_user_endpoint(user_id):

    try:
        user = get_user_by_id(user_id)

        return jsonify({
            'success': True,
            'message': 'User retrieved successfully.',
            'data': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.role_name,
                'role_id': user.role_id,
                'is_active': user.is_active,
                'created_at': (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                ),
                'updated_at': (
                    user.updated_at.isoformat()
                    if user.updated_at
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
            'message': 'Failed to retrieve user.',
        }), 500


@admin_bp.route('/admin/users', methods=['POST'])
@role_required('ADMIN')
def create_user_endpoint():

    try:
        data = request.get_json() or {}

        user = create_user(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
            role_name=data.get('role'),
            phone=data.get('phone'),
        )

        return jsonify({
            'success': True,
            'message': 'User created successfully.',
            'data': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.role_name,
                'role_id': user.role_id,
                'is_active': user.is_active,
            },
        }), 201

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error),
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to create user.',
        }), 500


@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@role_required('ADMIN')
def update_user_endpoint(user_id):

    try:
        data = request.get_json() or {}

        user = update_user(
            user_id=user_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
        )

        return jsonify({
            'success': True,
            'message': 'User updated successfully.',
            'data': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role.role_name,
                'role_id': user.role_id,
                'is_active': user.is_active,
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
            'message': 'Failed to update user.',
        }), 500


@admin_bp.route(
    '/admin/users/<int:user_id>/status',
    methods=['PATCH']
)
@role_required('ADMIN')
def set_user_status_endpoint(user_id):

    try:
        data = request.get_json() or {}

        if 'is_active' not in data:
            return jsonify({
                'success': False,
                'message': 'is_active is required.',
            }), 400

        user = set_user_status(
            user_id=user_id,
            is_active=data.get('is_active'),
        )

        return jsonify({
            'success': True,
            'message': 'User status updated successfully.',
            'data': {
                'user_id': user.user_id,
                'is_active': user.is_active,
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
            'message': 'Failed to update user status.',
        }), 500


@admin_bp.route(
    '/admin/users/<int:user_id>/role',
    methods=['PATCH']
)
@role_required('ADMIN')
def change_user_role_endpoint(user_id):

    try:
        data = request.get_json() or {}

        user = change_user_role(
            user_id=user_id,
            role_name=data.get('role'),
        )

        return jsonify({
            'success': True,
            'message': 'User role updated successfully.',
            'data': {
                'user_id': user.user_id,
                'role': user.role.role_name,
                'role_id': user.role_id,
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
            'message': 'Failed to update user role.',
        }), 500


@admin_bp.route(
    '/admin/users/<int:user_id>/password',
    methods=['PATCH']
)
@role_required('ADMIN')
def reset_user_password_endpoint(user_id):

    try:
        data = request.get_json() or {}

        user = reset_user_password(
            user_id=user_id,
            new_password=data.get('new_password'),
        )

        return jsonify({
            'success': True,
            'message': 'User password updated successfully.',
            'data': {
                'user_id': user.user_id,
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
            'message': 'Failed to update user password.',
        }), 500

@admin_bp.route('/admin/faculty/<int:faculty_id>', methods=['GET'])
@role_required('ADMIN')
def get_faculty_endpoint(faculty_id):
    """Get one Faculty member."""

    try:
        faculty = admin_service.get_faculty_by_id(faculty_id)

        return jsonify({
            'success': True,
            'data': {
                'faculty_id': faculty.faculty_id,
                'user_id': faculty.user_id,
                'first_name': faculty.user.first_name,
                'last_name': faculty.user.last_name,
                'email': faculty.user.email,
                'phone': faculty.user.phone,
                'employee_number': faculty.employee_number,
                'designation': faculty.designation,
                'department_id': faculty.department_id,
                'department_name': faculty.department.department_name,
                'is_active': faculty.user.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404


@admin_bp.route('/admin/faculty', methods=['POST'])
@role_required('ADMIN')
def create_faculty_endpoint():
    """Create a Faculty User and Faculty profile."""

    data = request.get_json() or {}

    try:
        faculty = admin_service.create_faculty(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            employee_number=data.get('employee_number'),
            designation=data.get('designation'),
        )

        return jsonify({
            'success': True,
            'message': 'Faculty created successfully.',
            'data': {
                'faculty_id': faculty.faculty_id,
                'user_id': faculty.user_id,
                'first_name': faculty.user.first_name,
                'last_name': faculty.user.last_name,
                'email': faculty.user.email,
                'phone': faculty.user.phone,
                'employee_number': faculty.employee_number,
                'designation': faculty.designation,
                'department_id': faculty.department_id,
                'department_name': faculty.department.department_name,
                'is_active': faculty.user.is_active,
            }
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@admin_bp.route('/admin/faculty/<int:faculty_id>', methods=['PUT'])
@role_required('ADMIN')
def update_faculty_endpoint(faculty_id):
    """Update Faculty and associated User information."""

    data = request.get_json() or {}

    try:
        faculty = admin_service.update_faculty(
            faculty_id=faculty_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            employee_number=data.get('employee_number'),
            designation=data.get('designation'),
        )

        return jsonify({
            'success': True,
            'message': 'Faculty updated successfully.',
            'data': {
                'faculty_id': faculty.faculty_id,
                'user_id': faculty.user_id,
                'first_name': faculty.user.first_name,
                'last_name': faculty.user.last_name,
                'email': faculty.user.email,
                'phone': faculty.user.phone,
                'employee_number': faculty.employee_number,
                'designation': faculty.designation,
                'department_id': faculty.department_id,
                'department_name': faculty.department.department_name,
                'is_active': faculty.user.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@admin_bp.route('/admin/faculty/<int:faculty_id>/status', methods=['PATCH'])
@role_required('ADMIN')
def set_faculty_status_endpoint(faculty_id):
    """Activate or deactivate a Faculty member."""

    data = request.get_json() or {}

    try:
        faculty = admin_service.set_faculty_status(
            faculty_id=faculty_id,
            is_active=data.get('is_active'),
        )

        return jsonify({
            'success': True,
            'message': 'Faculty status updated successfully.',
            'data': {
                'faculty_id': faculty.faculty_id,
                'user_id': faculty.user_id,
                'is_active': faculty.user.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@admin_bp.route('/admin/students', methods=['GET'])
@role_required('ADMIN')
def get_all_students_endpoint():
    """Return all Students."""

    student_list = admin_service.get_all_students()

    data = []

    for student in student_list:
        data.append({
            'student_id': student.student_id,
            'user_id': student.user_id,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'email': student.user.email,
            'phone': student.user.phone,
            'department_id': student.department_id,
            'department_name': student.department.department_name,
            'roll_number': student.roll_number,
            'enrollment_number': student.enrollment_number,
            'year': student.year,
            'semester': student.semester,
            'is_active': student.is_active,
        })

    return jsonify({
        'success': True,
        'data': data
    }), 200


@admin_bp.route('/admin/students/<int:student_id>', methods=['GET'])
@role_required('ADMIN')
def get_student_endpoint(student_id):
    """Return a single Student."""

    try:
        student = admin_service.get_student_by_id(student_id)

        return jsonify({
            'success': True,
            'data': {
                'student_id': student.student_id,
                'user_id': student.user_id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'phone': student.user.phone,
                'department_id': student.department_id,
                'department_name': student.department.department_name,
                'roll_number': student.roll_number,
                'enrollment_number': student.enrollment_number,
                'year': student.year,
                'semester': student.semester,
                'is_active': student.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404


@admin_bp.route('/admin/students', methods=['POST'])
@role_required('ADMIN')
def create_student_endpoint():
    """Create a Student User and Student profile."""

    data = request.get_json() or {}

    try:
        student = admin_service.create_student(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            password=data.get('password'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            roll_number=data.get('roll_number'),
            enrollment_number=data.get('enrollment_number'),
            year=data.get('year'),
            semester=data.get('semester'),
        )

        return jsonify({
            'success': True,
            'message': 'Student created successfully.',
            'data': {
                'student_id': student.student_id,
                'user_id': student.user_id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'phone': student.user.phone,
                'department_id': student.department_id,
                'department_name': student.department.department_name,
                'roll_number': student.roll_number,
                'enrollment_number': student.enrollment_number,
                'year': student.year,
                'semester': student.semester,
                'is_active': student.is_active,
            }
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@admin_bp.route('/admin/students/<int:student_id>', methods=['PUT'])
@role_required('ADMIN')
def update_student_endpoint(student_id):
    """Update Student User and profile information."""

    data = request.get_json() or {}

    try:
        student = admin_service.update_student(
            student_id=student_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            department_id=data.get('department_id'),
            roll_number=data.get('roll_number'),
            enrollment_number=data.get('enrollment_number'),
            year=data.get('year'),
            semester=data.get('semester'),
        )

        return jsonify({
            'success': True,
            'message': 'Student updated successfully.',
            'data': {
                'student_id': student.student_id,
                'user_id': student.user_id,
                'first_name': student.user.first_name,
                'last_name': student.user.last_name,
                'email': student.user.email,
                'phone': student.user.phone,
                'department_id': student.department_id,
                'department_name': student.department.department_name,
                'roll_number': student.roll_number,
                'enrollment_number': student.enrollment_number,
                'year': student.year,
                'semester': student.semester,
                'is_active': student.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@admin_bp.route('/admin/students/<int:student_id>/status', methods=['PATCH'])
@role_required('ADMIN')
def set_student_status_endpoint(student_id):
    """Activate or deactivate a Student."""

    data = request.get_json() or {}

    try:
        student = admin_service.set_student_status(
            student_id=student_id,
            is_active=data.get('is_active')
        )

        return jsonify({
            'success': True,
            'message': 'Student status updated successfully.',
            'data': {
                'student_id': student.student_id,
                'user_id': student.user_id,
                'is_active': student.is_active,
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@admin_bp.route('/admin/questions', methods=['GET'])
@role_required('ADMIN')
def get_all_questions_endpoint():
    try:
        results = get_all_questions()

        data = []

        for question, subject, creator, option_count in results:
            data.append({
                'question_id': question.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'marks': question.marks,
                'difficulty': question.difficulty,
                'is_active': question.is_active,
                'created_at': question.created_at.isoformat()
                    if question.created_at else None,
                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },
                'created_by': {
                    'user_id': creator.user_id,
                    'first_name': creator.first_name,
                    'last_name': creator.last_name,
                    'email': creator.email,
                },
                'option_count': option_count,
            })

        return jsonify({
            'success': True,
            'data': data,
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch questions.'
        }), 500

@admin_bp.route('/admin/questions/<int:question_id>', methods=['GET'])
@role_required('ADMIN')
def get_question_by_id_endpoint(question_id):
    try:
        question = get_question_by_id(question_id)

        return jsonify({
            'success': True,
            'data': {
                'question_id': question.question_id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'marks': question.marks,
                'difficulty': question.difficulty,
                'is_active': question.is_active,
                'subject_id': question.subject_id,
                'created_by': question.created_by,
                'created_at': question.created_at.isoformat()
                    if question.created_at else None,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch question.'
        }), 500

@admin_bp.route(
    '/admin/questions/<int:question_id>/status',
    methods=['PATCH']
)
@role_required('ADMIN')
def set_question_status_endpoint(question_id):
    try:
        data = request.get_json() or {}

        if 'is_active' not in data:
            return jsonify({
                'success': False,
                'message': 'is_active is required.'
            }), 400

        question = set_question_status(
            question_id=question_id,
            is_active=data.get('is_active')
        )

        return jsonify({
            'success': True,
            'message': 'Question status updated successfully.',
            'data': {
                'question_id': question.question_id,
                'is_active': question.is_active,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 400

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to update question status.'
        }), 500

@admin_bp.route('/admin/registrations', methods=['GET'])
@role_required('ADMIN')
def get_all_exam_registrations_endpoint():
    try:
        results = get_all_exam_registrations()

        data = []

        for registration, exam, subject, student, user in results:
            data.append({
                'registration_id': registration.registration_id,
                'registered_at': (
                    registration.registered_at.isoformat()
                    if registration.registered_at else None
                ),
                'status': registration.status,

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                    'year': student.year,
                    'semester': student.semester,
                },
            })

        return jsonify({
            'success': True,
            'data': data,
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch registrations.'
        }), 500

@admin_bp.route('/admin/exams/<int:exam_id>/registrations', methods=['GET'])
@role_required('ADMIN')
def get_exam_registrations_endpoint(exam_id):
    try:
        exam, registrations = get_exam_registrations(exam_id)

        data = []

        for registration, student, user in registrations:
            data.append({
                'registration_id': registration.registration_id,
                'registered_at': (
                    registration.registered_at.isoformat()
                    if registration.registered_at else None
                ),
                'status': registration.status,

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                    'year': student.year,
                    'semester': student.semester,
                },
            })

        return jsonify({
            'success': True,
            'data': {
                'exam_id': exam.exam_id,
                'exam_title': exam.title,
                'registrations': data,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch exam registrations.'
        }), 500

@admin_bp.route(
    '/admin/registrations/<int:registration_id>',
    methods=['GET']
)
@role_required('ADMIN')
def get_registration_by_id_endpoint(registration_id):
    try:
        registration, exam, subject, student, user = (
            get_registration_by_id(registration_id)
        )

        return jsonify({
            'success': True,
            'data': {
                'registration_id': registration.registration_id,
                'registered_at': (
                    registration.registered_at.isoformat()
                    if registration.registered_at else None
                ),
                'status': registration.status,

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                    'year': student.year,
                    'semester': student.semester,
                },
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch registration.'
        }), 500

@admin_bp.route('/admin/attempts', methods=['GET'])
@role_required('ADMIN')
def get_all_attempts_endpoint():
    try:
        results = get_all_attempts()

        data = []

        for (
            attempt,
            registration,
            exam,
            subject,
            student,
            user,
            result
        ) in results:

            data.append({
                'attempt_id': attempt.attempt_id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'started_at': (
                    attempt.started_at.isoformat()
                    if attempt.started_at else None
                ),
                'submitted_at': (
                    attempt.submitted_at.isoformat()
                    if attempt.submitted_at else None
                ),
                'score': (
                    float(attempt.score)
                    if attempt.score is not None else None
                ),

                'registration_id': registration.registration_id,

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },

                'result': (
                    {
                        'result_id': result.result_id,
                        'total_marks': float(result.total_marks),
                        'obtained_marks': float(result.obtained_marks),
                        'percentage': float(result.percentage),
                        'grade': result.grade,
                        'result_status': result.result_status,
                        'published_at': (
                            result.published_at.isoformat()
                            if result.published_at else None
                        ),
                    }
                    if result else None
                ),
            })

        return jsonify({
            'success': True,
            'data': data,
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch examination attempts.'
        }), 500

@admin_bp.route('/admin/exams/<int:exam_id>/attempts', methods=['GET'])
@role_required('ADMIN')
def get_exam_attempts_endpoint(exam_id):
    try:
        exam, results = get_exam_attempts(exam_id)

        data = []

        for (
            attempt,
            registration,
            student,
            user,
            result
        ) in results:

            data.append({
                'attempt_id': attempt.attempt_id,
                'registration_id': registration.registration_id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'started_at': (
                    attempt.started_at.isoformat()
                    if attempt.started_at else None
                ),
                'submitted_at': (
                    attempt.submitted_at.isoformat()
                    if attempt.submitted_at else None
                ),
                'score': (
                    float(attempt.score)
                    if attempt.score is not None else None
                ),

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },

                'result': (
                    {
                        'result_id': result.result_id,
                        'total_marks': float(result.total_marks),
                        'obtained_marks': float(result.obtained_marks),
                        'percentage': float(result.percentage),
                        'grade': result.grade,
                        'result_status': result.result_status,
                    }
                    if result else None
                ),
            })

        return jsonify({
            'success': True,
            'data': {
                'exam_id': exam.exam_id,
                'exam_title': exam.title,
                'attempts': data,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch examination attempts.'
        }), 500

@admin_bp.route('/admin/attempts/<int:attempt_id>', methods=['GET'])
@role_required('ADMIN')
def get_attempt_by_id_endpoint(attempt_id):
    try:
        (
            attempt,
            registration,
            exam,
            subject,
            student,
            user,
            result
        ) = get_attempt_by_id(attempt_id)

        return jsonify({
            'success': True,
            'data': {
                'attempt_id': attempt.attempt_id,
                'attempt_number': attempt.attempt_number,
                'status': attempt.status,
                'started_at': (
                    attempt.started_at.isoformat()
                    if attempt.started_at else None
                ),
                'submitted_at': (
                    attempt.submitted_at.isoformat()
                    if attempt.submitted_at else None
                ),
                'score': (
                    float(attempt.score)
                    if attempt.score is not None else None
                ),

                'registration_id': registration.registration_id,

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },

                'result': (
                    {
                        'result_id': result.result_id,
                        'total_marks': float(result.total_marks),
                        'obtained_marks': float(result.obtained_marks),
                        'percentage': float(result.percentage),
                        'grade': result.grade,
                        'result_status': result.result_status,
                        'published_at': (
                            result.published_at.isoformat()
                            if result.published_at else None
                        ),
                    }
                    if result else None
                ),
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch examination attempt.'
        }), 500

@admin_bp.route(
    '/admin/attempts/<int:attempt_id>/integrity-events',
    methods=['GET']
)
@role_required('ADMIN')
def get_attempt_integrity_events_endpoint(attempt_id):
    try:
        attempt, events = get_attempt_integrity_events(attempt_id)

        data = []

        for event in events:
            data.append({
                'audit_id': event.audit_id,
                'action': event.action,
                'entity_type': event.entity_type,
                'entity_id': event.entity_id,
                'details': event.details,
                'ip_address': event.ip_address,
                'created_at': (
                    event.created_at.isoformat()
                    if event.created_at else None
                ),
                'user_id': event.user_id,
            })

        return jsonify({
            'success': True,
            'data': {
                'attempt_id': attempt.attempt_id,
                'status': attempt.status,
                'integrity_event_count': len(data),
                'events': data,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch integrity events.'
        }), 500

@admin_bp.route('/admin/results', methods=['GET'])
@role_required('ADMIN')
def get_all_results_endpoint():
    try:
        results = get_all_results()

        data = []

        for (
            result,
            attempt,
            registration,
            exam,
            subject,
            student,
            user,
        ) in results:

            data.append({
                'result_id': result.result_id,
                'attempt_id': attempt.attempt_id,
                'attempt_number': attempt.attempt_number,

                'total_marks': float(result.total_marks),
                'obtained_marks': float(result.obtained_marks),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,

                'published_at': (
                    result.published_at.isoformat()
                    if result.published_at else None
                ),

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },
            })

        return jsonify({
            'success': True,
            'data': data,
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch results.'
        }), 500

@admin_bp.route('/admin/exams/<int:exam_id>/results', methods=['GET'])
@role_required('ADMIN')
def get_exam_results_for_admin_endpoint(exam_id):
    try:
        exam, results = get_exam_results_for_admin(exam_id)

        data = []

        for (
            result,
            attempt,
            registration,
            student,
            user,
        ) in results:

            data.append({
                'result_id': result.result_id,
                'attempt_id': attempt.attempt_id,
                'attempt_number': attempt.attempt_number,

                'total_marks': float(result.total_marks),
                'obtained_marks': float(result.obtained_marks),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,

                'published_at': (
                    result.published_at.isoformat()
                    if result.published_at else None
                ),

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },
            })

        return jsonify({
            'success': True,
            'data': {
                'exam_id': exam.exam_id,
                'exam_title': exam.title,
                'results': data,
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch exam results.'
        }), 500

@admin_bp.route('/admin/results/<int:result_id>', methods=['GET'])
@role_required('ADMIN')
def get_result_by_id_endpoint(result_id):
    try:
        (
            result,
            attempt,
            registration,
            exam,
            subject,
            student,
            user,
        ) = get_result_by_id(result_id)

        return jsonify({
            'success': True,
            'data': {
                'result_id': result.result_id,
                'attempt_id': attempt.attempt_id,
                'attempt_number': attempt.attempt_number,

                'total_marks': float(result.total_marks),
                'obtained_marks': float(result.obtained_marks),
                'percentage': float(result.percentage),
                'grade': result.grade,
                'result_status': result.result_status,

                'published_at': (
                    result.published_at.isoformat()
                    if result.published_at else None
                ),

                'exam': {
                    'exam_id': exam.exam_id,
                    'title': exam.title,
                    'status': exam.status,
                },

                'subject': {
                    'subject_id': subject.subject_id,
                    'subject_code': subject.subject_code,
                    'subject_name': subject.subject_name,
                },

                'student': {
                    'student_id': student.student_id,
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'roll_number': student.roll_number,
                    'enrollment_number': student.enrollment_number,
                },
            },
        }), 200

    except ValueError as error:
        return jsonify({
            'success': False,
            'message': str(error)
        }), 404

    except Exception:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch result.'
        }), 500

@admin_bp.route('/admin/dashboard/statistics', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def dashboard_statistics():
    try:
        statistics = get_dashboard_statistics()

        return jsonify({
            "success": True,
            "data": statistics
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@admin_bp.route('/admin/audit-logs', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_all_audit_logs_endpoint():
    try:
        results = get_all_audit_logs()

        data = []

        for audit, user in results:
            data.append({
                "audit_id": audit.audit_id,
                "user": {
                    "user_id": user.user_id if user else None,
                    "first_name": user.first_name if user else None,
                    "last_name": user.last_name if user else None,
                    "email": user.email if user else None,
                },
                "action": audit.action,
                "entity_type": audit.entity_type,
                "entity_id": audit.entity_id,
                "details": audit.details,
                "ip_address": audit.ip_address,
                "created_at": audit.created_at.isoformat()
                    if audit.created_at else None,
            })

        return jsonify({
            "success": True,
            "data": data,
            "count": len(data)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@admin_bp.route('/admin/audit-logs/<int:audit_id>', methods=['GET'])
@jwt_required()
@role_required('ADMIN')
def get_audit_log_by_id_endpoint(audit_id):
    try:
        audit, user = get_audit_log_by_id(audit_id)

        data = {
            "audit_id": audit.audit_id,
            "user": {
                "user_id": user.user_id if user else None,
                "first_name": user.first_name if user else None,
                "last_name": user.last_name if user else None,
                "email": user.email if user else None,
            },
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "details": audit.details,
            "ip_address": audit.ip_address,
            "created_at": audit.created_at.isoformat()
                if audit.created_at else None,
        }

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

