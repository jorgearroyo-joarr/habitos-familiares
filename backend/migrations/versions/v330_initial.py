"""initial schema v3.3

Revision ID: v330_initial
Revises:
Create Date: 2026-03-17 18:00:00.000000

This migration creates the complete v3.3 schema from scratch.
Used as the starting point for systems that never used Alembic before.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "v330_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # TABLE: app_settings
    # ============================================================
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_pin_hash", sa.String(length=128), nullable=False),
        sa.Column("currency_symbol", sa.String(length=10), nullable=True),
        sa.Column("app_name", sa.String(length=100), nullable=True),
        sa.Column("streak_bonus_days", sa.Integer(), nullable=True),
        sa.Column("streak_bonus_pct", sa.Float(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # Set default id=1
    op.execute("INSERT INTO app_settings (id) VALUES (1)")

    # ============================================================
    # TABLE: profiles
    # ============================================================
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("avatar", sa.String(length=10), nullable=True),
        sa.Column("theme", sa.String(length=50), nullable=True),
        sa.Column("level_idx", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1"),
        sa.Column("pin_hash", sa.String(length=128), nullable=True),
        sa.Column(
            "weekly_reward_base", sa.Float(), nullable=True, server_default="2.0"
        ),
        sa.Column(
            "weekly_reward_full", sa.Float(), nullable=True, server_default="4.0"
        ),
        sa.Column("monthly_reward_desc", sa.String(length=255), nullable=True),
        sa.Column("monthly_min_pct", sa.Float(), nullable=True, server_default="0.75"),
        sa.Column("balance", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column(
            "unlocked_themes", sa.Text(), nullable=True, server_default='["default"]'
        ),
        sa.Column("unlocked_avatars", sa.Text(), nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # ============================================================
    # TABLE: habit_templates
    # ============================================================
    op.create_table(
        "habit_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("habit_key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("icon", sa.String(length=10), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("stars", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("motivation", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1"),
        sa.Column("consecutive_days", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_mastered", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("mastered_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "habit_key", name="uq_profile_habit_key"),
    )

    # ============================================================
    # TABLE: micro_habits
    # ============================================================
    op.create_table(
        "micro_habits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("habit_template_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["habit_template_id"], ["habit_templates.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # TABLE: reward_tiers
    # ============================================================
    op.create_table(
        "reward_tiers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("tier_type", sa.String(length=20), nullable=True),
        sa.Column("min_pct", sa.Float(), nullable=False),
        sa.Column("multiplier", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("emoji", sa.String(length=10), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ============================================================
    # TABLE: day_logs
    # ============================================================
    op.create_table(
        "day_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=False),
        sa.Column("completed_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total", sa.Integer(), nullable=True, server_default="6"),
        sa.Column("pct", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("day_done", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("bonus_star", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "date", name="uq_profile_date"),
    )
    op.create_index("ix_day_logs_date", "day_logs", ["date"])

    # ============================================================
    # TABLE: habit_entries
    # ============================================================
    op.create_table(
        "habit_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("day_log_id", sa.Integer(), nullable=False),
        sa.Column("habit_id", sa.String(length=50), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("mini_tasks_json", sa.Text(), nullable=True, server_default="{}"),
        sa.Column("toggled_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["day_log_id"], ["day_logs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("day_log_id", "habit_id", name="uq_daylog_habit"),
    )

    # ============================================================
    # TABLE: week_rewards
    # ============================================================
    op.create_table(
        "week_rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.String(length=10), nullable=False),
        sa.Column("week_end", sa.String(length=10), nullable=False),
        sa.Column("days_completed", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_pct", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("streak_at_close", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("shield_used", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("earned_amount", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("reward_paid", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "week_start", name="uq_profile_week"),
    )

    # ============================================================
    # TABLE: month_rewards
    # ============================================================
    op.create_table(
        "month_rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("month_key", sa.String(length=7), nullable=False),
        sa.Column("days_completed", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_days", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("pct", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("reward_unlocked", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("reward_paid", sa.Boolean(), nullable=True, server_default="0"),
        sa.Column("reward_desc", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["profile_id"], ["profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("profile_id", "month_key", name="uq_profile_month"),
    )


def downgrade() -> None:
    # Drop all tables in reverse order (respecting foreign keys)
    op.drop_table("month_rewards")
    op.drop_table("week_rewards")
    op.drop_table("habit_entries")
    op.drop_index("ix_day_logs_date", table_name="day_logs")
    op.drop_table("day_logs")
    op.drop_table("reward_tiers")
    op.drop_table("micro_habits")
    op.drop_table("habit_templates")
    op.drop_table("profiles")
    op.drop_table("app_settings")
