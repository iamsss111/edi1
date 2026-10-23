"""Student/faculty lifecycle and notification API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services import faculty_lifecycle_service as faculty_service
from app.services import student_lifecycle_service as student_service
from app.services import notification_service
from app.utils.rbac import role_required


lifecycle_bp = Blueprint("lifecycle", __name__)


def _error(error: Exception):
    if isinstance(error, LookupError):
        return jsonify({"success": False, "message": str(error)}), 404
    if isinstance(error, ValueError):
        return jsonify({"success": False, "message": str(error)}), 400
    return jsonify({"success": False, "message": "An unexpected error occurred."}), 500


@lifecycle_bp.get("/student/subjects")
@role_required("STUDENT")
def student_subjects_route():
    try:
        rows = student_service.available_subjects(int(get_jwt_identity()))
        return jsonify({"success": True, "data": rows}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/enrollments")
@role_required("STUDENT")
def student_enrollments_route():
    try:
        rows = student_service.student_enrollments(int(get_jwt_identity()))
        return jsonify({"success": True, "data": [student_service.serialize_student_enrollment(row) for row in rows]}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.post("/student/subjects/<int:faculty_subject_id>/enroll")
@role_required("STUDENT")
def enroll_in_subject_route(faculty_subject_id: int):
    try:
        row = student_service.enroll_in_subject(int(get_jwt_identity()), faculty_subject_id)
        return jsonify({"success": True, "message": "Enrolled in subject.", "data": student_service.serialize_student_enrollment(row)}), 201
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/exams/available")
@role_required("STUDENT")
def available_exams_route():
    try:
        data = student_service.available_exams(int(get_jwt_identity()))
        return jsonify({"success": True, "data": data}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.post("/student/exams/<int:exam_id>/register")
@role_required("STUDENT")
def register_for_exam_route(exam_id: int):
    try:
        registration = student_service.register_for_exam(int(get_jwt_identity()), exam_id)
        return jsonify({
            "success": True,
            "message": "Registered for exam.",
            "data": student_service.serialize_registration(registration),
        }), 201
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/registrations")
@role_required("STUDENT")
def student_registrations_route():
    try:
        rows = student_service.student_registrations(int(get_jwt_identity()))
        return jsonify({"success": True, "data": [student_service.serialize_registration(r) for r in rows]}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/registrations/<int:registration_id>")
@role_required("STUDENT")
def student_registration_detail_route(registration_id: int):
    try:
        row = student_service.student_registration_detail(int(get_jwt_identity()), registration_id)
        return jsonify({"success": True, "data": student_service.serialize_registration(row)}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/results")
@role_required("STUDENT")
def student_results_route():
    try:
        rows = student_service.student_results(int(get_jwt_identity()))
        return jsonify({"success": True, "data": [student_service.serialize_student_result(r) for r in rows]}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/student/results/<int:result_id>")
@role_required("STUDENT")
def student_result_detail_route(result_id: int):
    try:
        result, breakdown = student_service.student_result_detail(int(get_jwt_identity()), result_id)
        data = student_service.serialize_student_result(result)
        data["exam"] = {
            "exam_id": result.attempt.registration.exam.exam_id,
            "title": result.attempt.registration.exam.title,
            "subject_code": result.attempt.registration.exam.subject.subject_code,
        }
        data["student"] = {
            "student_id": result.attempt.registration.student.student_id,
            "roll_number": result.attempt.registration.student.roll_number,
            "name": f"{result.attempt.registration.student.user.first_name} {result.attempt.registration.student.user.last_name}",
        }
        data["question_breakdown"] = breakdown
        return jsonify({"success": True, "data": data}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/exams/<int:exam_id>/registrations")
@role_required("FACULTY")
def faculty_registrations_route(exam_id: int):
    try:
        rows = faculty_service.exam_registrations(int(get_jwt_identity()), exam_id)
        return jsonify({"success": True, "data": {"exam_id": exam_id, "candidates": [faculty_service.serialize_candidate(r) for r in rows]}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/exams/<int:exam_id>/attempts")
@role_required("FACULTY")
def faculty_attempts_route(exam_id: int):
    try:
        rows = faculty_service.exam_attempts(int(get_jwt_identity()), exam_id)
        return jsonify({"success": True, "data": {"exam_id": exam_id, "attempts": [faculty_service.serialize_attempt(a) for a in rows]}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/attempts/<int:attempt_id>")
@role_required("FACULTY")
def faculty_attempt_detail_route(attempt_id: int):
    try:
        return jsonify({"success": True, "data": faculty_service.attempt_detail(int(get_jwt_identity()), attempt_id)}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.post("/faculty/attempts/<int:attempt_id>/evaluate")
@role_required("FACULTY")
def evaluate_faculty_attempt_route(attempt_id: int):
    try:
        attempt, result = faculty_service.evaluate_owned_attempt(int(get_jwt_identity()), attempt_id)
        return jsonify({
            "success": True,
            "message": "Attempt evaluated; result is awaiting publication.",
            "data": {
                "attempt_id": attempt.attempt_id,
                "result_id": result.result_id,
                "score": float(attempt.score),
                "published": result.published_at is not None,
            },
        }), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/attempts/<int:attempt_id>/integrity-events")
@role_required("FACULTY")
def faculty_integrity_events_route(attempt_id: int):
    try:
        events = faculty_service.attempt_integrity_events(int(get_jwt_identity()), attempt_id)
        violations = sum(event.action in {"TAB_SWITCH", "WINDOW_BLUR", "FULLSCREEN_EXIT"} for event in events)
        return jsonify({"success": True, "data": {"attempt_id": attempt_id, "violation_count": violations, "events": [faculty_service.serialize_integrity_event(e) for e in events]}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/evaluations/pending")
@role_required("FACULTY")
def pending_evaluations_route():
    try:
        exam_id = request.args.get("exam_id", type=int)
        rows = faculty_service.pending_evaluations(int(get_jwt_identity()), exam_id)
        return jsonify({"success": True, "data": [faculty_service.serialize_attempt(a) for a in rows]}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.post("/faculty/results/<int:result_id>/publish")
@role_required("FACULTY")
def publish_result_route(result_id: int):
    try:
        result = faculty_service.publish_result(int(get_jwt_identity()), result_id)
        return jsonify({"success": True, "message": "Result published.", "data": faculty_service.serialize_result(result)}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.post("/faculty/exams/<int:exam_id>/results/publish")
@role_required("FACULTY")
def publish_exam_results_route(exam_id: int):
    try:
        rows = faculty_service.publish_exam_results(int(get_jwt_identity()), exam_id)
        return jsonify({"success": True, "message": "Exam results published.", "data": {"exam_id": exam_id, "published_count": len(rows), "results": [faculty_service.serialize_result(r) for r in rows]}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/dashboard/statistics")
@role_required("FACULTY")
def faculty_dashboard_route():
    try:
        return jsonify({"success": True, "data": faculty_service.dashboard_statistics(int(get_jwt_identity()))}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/exams/<int:exam_id>/analytics")
@role_required("FACULTY")
def exam_analytics_route(exam_id: int):
    try:
        return jsonify({"success": True, "data": faculty_service.exam_analytics(int(get_jwt_identity()), exam_id)}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/faculty/students/<int:student_id>/performance")
@role_required("FACULTY")
def student_performance_route(student_id: int):
    try:
        data = faculty_service.student_performance(int(get_jwt_identity()), student_id)
        return jsonify({"success": True, "data": {"student_id": student_id, "results": data}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/notifications")
@role_required("STUDENT", "FACULTY", "ADMIN")
def notifications_route():
    try:
        unread_only = request.args.get("unread", "false").lower() == "true"
        rows = notification_service.list_notifications(int(get_jwt_identity()), unread_only)
        return jsonify({"success": True, "data": [notification_service.serialize_notification(n) for n in rows]}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.get("/notifications/unread-count")
@role_required("STUDENT", "FACULTY", "ADMIN")
def notification_unread_count_route():
    try:
        return jsonify({"success": True, "data": {"unread_count": notification_service.unread_count(int(get_jwt_identity()))}}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.patch("/notifications/<int:notification_id>/read")
@role_required("STUDENT", "FACULTY", "ADMIN")
def notification_mark_read_route(notification_id: int):
    try:
        notification = notification_service.mark_read(int(get_jwt_identity()), notification_id)
        return jsonify({"success": True, "data": notification_service.serialize_notification(notification)}), 200
    except Exception as error:
        return _error(error)


@lifecycle_bp.patch("/notifications/read-all")
@role_required("STUDENT", "FACULTY", "ADMIN")
def notification_mark_all_read_route():
    try:
        count = notification_service.mark_all_read(int(get_jwt_identity()))
        return jsonify({"success": True, "data": {"marked_read": count}}), 200
    except Exception as error:
        return _error(error)
