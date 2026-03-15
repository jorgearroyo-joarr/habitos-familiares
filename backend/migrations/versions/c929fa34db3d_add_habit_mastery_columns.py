"""add_habit_mastery_columns

Revision ID: c929fa34db3d
Revises:
Create Date: 2026-03-15 16:40:07.724645

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c929fa34db3d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add habit mastery columns to habit_templates table
    # These columns track consecutive days and mastery status for the dopamine system

    op.add_column(
        "habit_templates",
        sa.Column("consecutive_days", sa.Integer(), nullable=False, server_default="0"),
    )

    op.add_column(
        "habit_templates",
        sa.Column("is_mastered", sa.Boolean(), nullable=False, server_default="false"),
    )

    op.add_column(
        "habit_templates", sa.Column("mastered_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Remove habit mastery columns
    op.drop_column("habit_templates", "mastered_at")
    op.drop_column("habit_templates", "is_mastered")
    op.drop_column("habit_templates", "consecutive_days")
