"""Add SubjectID to Question and backfill existing questions."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = 'question_subject_01'
down_revision = '31d61f6cfec9'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add SubjectID temporarily as nullable
    op.add_column(
        'question',
        sa.Column(
            'SubjectID',
            mysql.BIGINT(unsigned=True),
            nullable=True
        )
    )

    # Step 2: Backfill existing questions
    op.execute(
        """
        UPDATE question
        SET SubjectID = 1
        WHERE QuestionID IN (1, 2, 4)
        """
    )

    op.execute(
        """
        UPDATE question
        SET SubjectID = 2
        WHERE QuestionID = 3
        """
    )

    # Step 3: Make SubjectID mandatory
    op.alter_column(
        'question',
        'SubjectID',
        existing_type=mysql.BIGINT(unsigned=True),
        nullable=False
    )

    # Step 4: Add index
    op.create_index(
        'idx_question_subject',
        'question',
        ['SubjectID']
    )

    # Step 5: Add foreign key
    op.create_foreign_key(
        'fk_question_subject',
        'question',
        'subject',
        ['SubjectID'],
        ['SubjectID'],
        ondelete='RESTRICT',
        onupdate='CASCADE'
    )


def downgrade():
    op.drop_constraint(
        'fk_question_subject',
        'question',
        type_='foreignkey'
    )

    op.drop_index(
        'idx_question_subject',
        table_name='question'
    )

    op.drop_column(
        'question',
        'SubjectID'
    )