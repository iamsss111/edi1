"""Add adaptive difficulty configuration to Exam."""

from alembic import op
import sqlalchemy as sa


revision = 'adaptive_difficulty_01'
down_revision = 'question_subject_01'
branch_labels = None
depends_on = None


def upgrade():
    # Add adaptive mode flag.
    op.add_column(
        'exam',
        sa.Column(
            'AdaptiveEnabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('0')
        )
    )

    # Add initial adaptive difficulty.
    op.add_column(
        'exam',
        sa.Column(
            'InitialDifficulty',
            sa.String(20),
            nullable=False,
            server_default='Medium'
        )
    )

    # Restrict initial difficulty to supported values.
    op.create_check_constraint(
        'chk_exam_initial_difficulty',
        'exam',
        "InitialDifficulty IN ('Easy', 'Medium', 'Hard')"
    )


def downgrade():
    op.drop_constraint(
        'chk_exam_initial_difficulty',
        'exam',
        type_='check'
    )

    op.drop_column(
        'exam',
        'InitialDifficulty'
    )

    op.drop_column(
        'exam',
        'AdaptiveEnabled'
    )