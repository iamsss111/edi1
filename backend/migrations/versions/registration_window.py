"""Add an optional registration cutoff to exam schedules."""

from alembic import op
import sqlalchemy as sa


revision = 'registration_window_01'
down_revision = 'c6ae915ded28'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'ExamSchedule',
        sa.Column('RegistrationEndTime', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_column('ExamSchedule', 'RegistrationEndTime')
