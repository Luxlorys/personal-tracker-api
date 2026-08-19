"""Initial habits schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-19 12:00:00+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "habits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("cadence_period", sa.String(length=16), nullable=False),
        sa.Column("cadence_target", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "habit_check_ins",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("habit_id", sa.Uuid(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_habit_check_ins_habit_id_recorded_at",
        "habit_check_ins",
        ["habit_id", "recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_habit_check_ins_habit_id_recorded_at", table_name="habit_check_ins")
    op.drop_table("habit_check_ins")
    op.drop_table("habits")
