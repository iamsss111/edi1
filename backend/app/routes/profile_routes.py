"""Authenticated profile details for student, faculty, and admin accounts."""

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models import User


profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/profile")
@jwt_required()
def get_my_profile():
    user = User.query.filter_by(user_id=int(get_jwt_identity())).first()
    if user is None:
        return jsonify({"success": False, "message": "Account not found."}), 404

    role_name = user.role.role_name
    profile = {}
    if role_name == "STUDENT" and user.student:
        student = user.student
        profile = {
            "student_id": student.student_id,
            "roll_number": student.roll_number,
            "enrollment_number": student.enrollment_number,
            "department_code": student.department.department_code,
            "department_name": student.department.department_name,
            "year": student.year,
            "semester": student.semester,
            "is_active": student.is_active,
        }
    elif role_name == "FACULTY" and user.faculty:
        faculty = user.faculty
        profile = {
            "faculty_id": faculty.faculty_id,
            "employee_number": faculty.employee_number,
            "designation": faculty.designation,
            "department_code": faculty.department.department_code,
            "department_name": faculty.department.department_name,
        }
    elif role_name == "ADMIN":
        profile = {"account_type": "Administrator"}

    return jsonify({
        "success": True,
        "data": {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "phone": user.phone,
            "role": role_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile": profile,
        },
    }), 200
