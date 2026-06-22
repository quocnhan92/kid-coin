"""Online teacher: lesson steps, schedule, family checkpoints

Revision ID: 024_online_teacher_steps
Revises: 023_learning_questions_dedup
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "024_online_teacher_steps"
down_revision: Union[str, None] = "023_learning_questions_dedup"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "learning_chapters",
        sa.Column("week_number", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "learning_lessons",
        sa.Column("progress_emoji", sa.String(8), server_default="🍏", nullable=False),
    )
    op.add_column(
        "learning_lesson_progress",
        sa.Column("steps_summary", JSONB(), server_default="{}", nullable=False),
    )
    op.add_column(
        "learning_daily_summary",
        sa.Column("steps_completed", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "learning_daily_summary",
        sa.Column("checkpoints_confirmed", sa.Integer(), server_default="0", nullable=False),
    )

    op.create_table(
        "learning_lesson_steps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("lesson_id", UUID(as_uuid=True), sa.ForeignKey("learning_lessons.id"), nullable=False),
        sa.Column("sort_index", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("step_type", sa.String(32), nullable=False),
        sa.Column("emoji_icon", sa.String(8), server_default="👀", nullable=False),
        sa.Column("config_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("est_seconds", sa.Integer(), server_default="60", nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default="true", nullable=False),
    )
    op.create_index("ix_learning_lesson_steps_lesson", "learning_lesson_steps", ["lesson_id"])

    op.create_table(
        "learning_step_progress",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("step_id", UUID(as_uuid=True), sa.ForeignKey("learning_lesson_steps.id"), primary_key=True),
        sa.Column("status", sa.String(16), server_default="not_started", nullable=False),
        sa.Column("score", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("result_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "learning_grade_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("semester", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("week_number", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.create_index("ix_learning_grade_schedules_grade", "learning_grade_schedules", ["grade"])

    op.create_table(
        "learning_schedule_slots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("schedule_id", UUID(as_uuid=True), sa.ForeignKey("learning_grade_schedules.id"), nullable=False),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("session", sa.String(16), nullable=False),
        sa.Column("slot_order", sa.SmallInteger(), server_default="1", nullable=False),
        sa.Column("subject_id", sa.String(32), sa.ForeignKey("learning_subjects.id"), nullable=False),
        sa.Column("lesson_id", UUID(as_uuid=True), sa.ForeignKey("learning_lessons.id"), nullable=True),
    )
    op.create_index("ix_learning_schedule_slots_schedule", "learning_schedule_slots", ["schedule_id"])

    op.create_table(
        "learning_family_checkpoints",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("step_id", UUID(as_uuid=True), sa.ForeignKey("learning_lesson_steps.id"), nullable=False),
        sa.Column("lesson_id", UUID(as_uuid=True), sa.ForeignKey("learning_lessons.id"), nullable=False),
        sa.Column("confirmed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(16), server_default="pending", nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_learning_family_checkpoints_user", "learning_family_checkpoints", ["user_id", "status"])


def downgrade() -> None:
    op.drop_table("learning_family_checkpoints")
    op.drop_table("learning_schedule_slots")
    op.drop_table("learning_grade_schedules")
    op.drop_table("learning_step_progress")
    op.drop_table("learning_lesson_steps")
    op.drop_column("learning_daily_summary", "checkpoints_confirmed")
    op.drop_column("learning_daily_summary", "steps_completed")
    op.drop_column("learning_lesson_progress", "steps_summary")
    op.drop_column("learning_lessons", "progress_emoji")
    op.drop_column("learning_chapters", "week_number")
