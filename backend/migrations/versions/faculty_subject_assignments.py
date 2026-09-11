"""add faculty subject assignments

Revision ID: 31d61f6cfec9
Revises: 98b568baa82e
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = '31d61f6cfec9'
down_revision = '98b568baa82e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'facultysubject',

        sa.Column(
            'FacultySubjectID',
            mysql.BIGINT(unsigned=True),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            'FacultyID',
            mysql.BIGINT(unsigned=True),
            nullable=False
        ),

        sa.Column(
            'SubjectID',
            mysql.BIGINT(unsigned=True),
            nullable=False
        ),

        sa.Column(
            'Semester',
            sa.SmallInteger(),
            nullable=False
        ),

        sa.Column(
            'Year',
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            'IsActive',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('1')
        ),

        sa.Column(
            'AssignedAt',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP')
        ),

        sa.CheckConstraint(
            'Semester > 0',
            name='chk_faculty_subject_semester'
        ),

        sa.CheckConstraint(
            'Year > 0',
            name='chk_faculty_subject_year'
        ),

        sa.ForeignKeyConstraint(
            ['FacultyID'],
            ['faculty.FacultyID'],
            name='fk_faculty_subject_faculty',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),

        sa.ForeignKeyConstraint(
            ['SubjectID'],
            ['subject.SubjectID'],
            name='fk_faculty_subject_subject',
            ondelete='RESTRICT',
            onupdate='CASCADE'
        ),

        sa.PrimaryKeyConstraint(
            'FacultySubjectID'
        ),

        sa.UniqueConstraint(
            'FacultyID',
            'SubjectID',
            'Semester',
            'Year',
            name='uq_faculty_subject_assignment'
        ),
    )

    op.create_index(
        'idx_faculty_subject_faculty',
        'facultysubject',
        ['FacultyID']
    )

    op.create_index(
        'idx_faculty_subject_subject',
        'facultysubject',
        ['SubjectID']
    )

    op.create_index(
        'idx_faculty_subject_active',
        'facultysubject',
        ['IsActive']
    )


def downgrade():
    op.drop_index(
        'idx_faculty_subject_active',
        table_name='facultysubject'
    )

    op.drop_index(
        'idx_faculty_subject_subject',
        table_name='facultysubject'
    )

    op.drop_index(
        'idx_faculty_subject_faculty',
        table_name='facultysubject'
    )

    op.drop_table('facultysubject')