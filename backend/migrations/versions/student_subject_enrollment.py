"""Add student enrollment to faculty subject offerings."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'student_subject_enroll_01'
down_revision = 'registration_window_01'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'StudentSubjectEnrollment',
        sa.Column('EnrollmentID', mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column('StudentID', mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column('FacultySubjectID', mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column('EnrolledAt', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('IsActive', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.ForeignKeyConstraint(['StudentID'], ['Student.StudentID'], name='fk_student_subject_enrollment_student', ondelete='CASCADE', onupdate='CASCADE'),
        sa.ForeignKeyConstraint(['FacultySubjectID'], ['FacultySubject.FacultySubjectID'], name='fk_student_subject_enrollment_offering', ondelete='RESTRICT', onupdate='CASCADE'),
        sa.PrimaryKeyConstraint('EnrollmentID'),
        sa.UniqueConstraint('StudentID', 'FacultySubjectID', name='uq_student_subject_enrollment'),
    )
    op.create_index('idx_student_subject_enrollment_student', 'StudentSubjectEnrollment', ['StudentID'])
    op.create_index('idx_student_subject_enrollment_active', 'StudentSubjectEnrollment', ['IsActive'])


def downgrade():
    op.drop_index('idx_student_subject_enrollment_active', table_name='StudentSubjectEnrollment')
    op.drop_index('idx_student_subject_enrollment_student', table_name='StudentSubjectEnrollment')
    op.drop_table('StudentSubjectEnrollment')
