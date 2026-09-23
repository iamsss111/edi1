"""Add current adaptive exam question to attempts."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = 'c6ae915ded28'
down_revision = 'adaptive_difficulty_01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'ExamAttempt',
        sa.Column(
            'CurrentAdaptiveExamQuestionID',
            mysql.BIGINT(unsigned=True),
            nullable=True
        )
    )

    op.create_foreign_key(
        'fk_attempt_current_adaptive_question',
        'ExamAttempt',
        'ExamQuestion',
        ['CurrentAdaptiveExamQuestionID'],
        ['ExamQuestionID'],
        ondelete='SET NULL',
        onupdate='CASCADE'
    )


def downgrade():
    op.drop_constraint(
        'fk_attempt_current_adaptive_question',
        'ExamAttempt',
        type_='foreignkey'
    )

    op.drop_column(
        'ExamAttempt',
        'CurrentAdaptiveExamQuestionID'
    )