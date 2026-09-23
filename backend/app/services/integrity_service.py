"""
Browser integrity service.

Handles browser integrity events generated during
an active examination attempt.
"""

import json

from app.extensions.database import db
from app.models import (
    ExamAttempt,
    CandidateRegistration,
    Student,
    AuditLog,
)


ALLOWED_EVENTS = {
    'TAB_SWITCH',
    'WINDOW_BLUR',
    'FULLSCREEN_EXIT',
    'PAGE_HIDDEN',
}

VIOLATION_EVENTS = {
    'TAB_SWITCH',
    'WINDOW_BLUR',
    'FULLSCREEN_EXIT',
}

MAX_INTEGRITY_VIOLATIONS = 3


def record_integrity_event(
    user_id: int,
    attempt_id: int,
    event_type: str,
    details: dict | None = None,
    ip_address: str | None = None,
) -> tuple[AuditLog, int, bool]:

    # ------------------------------------------------------------
    # 1. Validate event type
    # ------------------------------------------------------------

    event_type = event_type.upper().strip()

    if event_type not in ALLOWED_EVENTS:
        raise ValueError(
            "Invalid browser integrity event type."
        )

    # ------------------------------------------------------------
    # 2. Find attempt
    # ------------------------------------------------------------

    attempt = ExamAttempt.query.filter_by(
        attempt_id=attempt_id
    ).first()

    if attempt is None:
        raise ValueError(
            "Examination attempt not found."
        )

    # ------------------------------------------------------------
    # 3. Find registration
    # ------------------------------------------------------------

    registration = CandidateRegistration.query.filter_by(
        registration_id=attempt.registration_id
    ).first()

    if registration is None:
        raise ValueError(
            "Examination registration not found."
        )

    # ------------------------------------------------------------
    # 4. Verify student ownership
    # ------------------------------------------------------------

    student = Student.query.filter_by(
        student_id=registration.student_id
    ).first()

    if student is None or student.user_id != user_id:
        raise ValueError(
            "You are not authorized to record this event."
        )

    # ------------------------------------------------------------
    # 5. Only active attempts should generate events
    # ------------------------------------------------------------

    if attempt.status != 'InProgress':
        raise ValueError(
            "Browser integrity events cannot be recorded "
            "after the examination is submitted."
        )

    # ------------------------------------------------------------
    # 6. Prepare details
    # ------------------------------------------------------------

    event_details = details or {}

    audit_log = AuditLog(
        user_id=user_id,
        action=event_type,
        entity_type='ExamAttempt',
        entity_id=attempt_id,
        details=json.dumps(event_details),
        ip_address=ip_address,
    )

    # ------------------------------------------------------------
    # 7. Save audit event and calculate violation count
    # ------------------------------------------------------------

    try:
        db.session.add(audit_log)
        db.session.flush()

        violation_count = 0

        if event_type in VIOLATION_EVENTS:
            violation_count = AuditLog.query.filter(
                AuditLog.entity_type == 'ExamAttempt',
                AuditLog.entity_id == attempt_id,
                AuditLog.action.in_(VIOLATION_EVENTS),
            ).count()

        auto_submit_triggered = (
            violation_count >= MAX_INTEGRITY_VIOLATIONS
        )

        if auto_submit_triggered:
            attempt.status = 'AutoSubmitted'
            attempt.submitted_at = db.func.current_timestamp()

        db.session.commit()

        return (
            audit_log,
            violation_count,
            auto_submit_triggered,
        )

    except Exception:
        db.session.rollback()
        raise