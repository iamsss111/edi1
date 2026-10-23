"""Student enrollment in a faculty's active subject offering."""

from app.extensions.database import db
from sqlalchemy.dialects.mysql import BIGINT


class StudentSubjectEnrollment(db.Model):
    __tablename__ = 'StudentSubjectEnrollment'

    enrollment_id = db.Column('EnrollmentID', BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    student_id = db.Column('StudentID', BIGINT(unsigned=True), db.ForeignKey('Student.StudentID', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    faculty_subject_id = db.Column('FacultySubjectID', BIGINT(unsigned=True), db.ForeignKey('FacultySubject.FacultySubjectID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    enrolled_at = db.Column('EnrolledAt', db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    is_active = db.Column('IsActive', db.Boolean, nullable=False, default=True, server_default='1')

    student = db.relationship('Student')
    faculty_subject = db.relationship('FacultySubject')

    __table_args__ = (
        db.UniqueConstraint('StudentID', 'FacultySubjectID', name='uq_student_subject_enrollment'),
        db.Index('idx_student_subject_enrollment_student', 'StudentID'),
        db.Index('idx_student_subject_enrollment_active', 'IsActive'),
    )
