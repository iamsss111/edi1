"""
Models package - contains all SQLAlchemy ORM models
"""
from app.models.role import Role
from app.models.user import User
from app.models.department import Department
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.exam import Exam
from app.models.exam_schedule import ExamSchedule
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.exam_question import ExamQuestion
from app.models.candidate_registration import CandidateRegistration
from app.models.exam_attempt import ExamAttempt
from app.models.student_answer import StudentAnswer
from app.models.result import Result
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.faculty_subject import FacultySubject

__all__ = [
    'Role',
    'User',
    'Department',
    'Student',
    'Faculty',
    'FacultySubject',
    'Subject',
    'Exam',
    'ExamSchedule',
    'Question',
    'QuestionOption',
    'ExamQuestion',
    'CandidateRegistration',
    'ExamAttempt',
    'StudentAnswer',
    'Result',
    'Notification',
    'AuditLog',
]
