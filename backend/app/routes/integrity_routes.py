"""
Browser integrity routes.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.integrity_service import (
    record_integrity_event,
)
from app.utils.rbac import role_required


integrity_bp = Blueprint(
    'integrity',
    __name__
)


@integrity_bp.post(
    '/attempts/<int:attempt_id>/integrity-events'
)
@role_required('STUDENT')
def record_integrity_event_endpoint(attempt_id: int):

    current_user_id = get_jwt_identity()

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            'success': False,
            'message': 'Request body is required.',
        }), 400

    event_type = data.get('event_type')

    if not event_type:
        return jsonify({
            'success': False,
            'message': 'event_type is required.',
        }), 400

    details = data.get('details')

    if details is not None and not isinstance(details, dict):
        return jsonify({
            'success': False,
            'message': 'details must be an object.',
        }), 400

    try:

        audit_log = record_integrity_event(
            user_id=int(current_user_id),
            attempt_id=attempt_id,
            event_type=event_type,
            details=details,
            ip_address=request.remote_addr,
        )

        return jsonify({
            'success': True,
            'message': 'Browser integrity event recorded successfully.',
            'data': {
                'audit_id': audit_log.audit_id,
                'attempt_id': attempt_id,
                'event_type': audit_log.action,
                'recorded_at': (
                    audit_log.created_at.isoformat()
                    if audit_log.created_at
                    else None
                ),
            },
        }), 201

    except ValueError as error:

        message = str(error)

        if message == "Examination attempt not found.":
            status_code = 404

        elif message in [
            "Examination registration not found.",
            "You are not authorized to record this event.",
        ]:
            status_code = 403

        elif message == (
            "Browser integrity events cannot be recorded "
            "after the examination is submitted."
        ):
            status_code = 400

        elif message == "Invalid browser integrity event type.":
            status_code = 400

        else:
            status_code = 400

        return jsonify({
            'success': False,
            'message': message,
        }), status_code

    except Exception:
        return jsonify({
            'success': False,
            'message': (
                'An unexpected error occurred while recording '
                'the browser integrity event.'
            ),
        }), 500