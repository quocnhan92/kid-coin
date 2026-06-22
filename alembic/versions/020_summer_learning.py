"""Summer learning path tables

Revision ID: 020_summer_learning
Revises: 019_play_policy
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "020_summer_learning"
down_revision = "019_play_policy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_subjects",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column("grade", sa.SmallInteger(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(8), server_default="📚", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_required", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("color_primary", sa.String(16), server_default="#E85D24", nullable=False),
        sa.Column("color_bg", sa.String(16), server_default="#FAECE7", nullable=False),
        sa.Column("color_dark", sa.String(16), server_default="#993C1D", nullable=False),
        sa.Column("textbook_series", sa.String(64), server_default="ket_noi_tri_thuc", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.create_index("ix_learning_subjects_grade", "learning_subjects", ["grade"])

    op.create_table(
        "learning_chapters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("subject_id", sa.String(32), sa.ForeignKey("learning_subjects.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("subtitle", sa.String(300), nullable=True),
        sa.Column("sort_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("est_minutes", sa.SmallInteger(), server_default="25", nullable=False),
        sa.Column("prerequisite_chapter_id", UUID(as_uuid=True), sa.ForeignKey("learning_chapters.id"), nullable=True),
        sa.Column("textbook_ref", sa.String(200), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_learning_chapters_subject", "learning_chapters", ["subject_id"])

    op.create_table(
        "learning_lessons",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("chapter_id", UUID(as_uuid=True), sa.ForeignKey("learning_chapters.id"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(500), nullable=True),
        sa.Column("sort_index", sa.Integer(), server_default="0", nullable=False),
        sa.Column("duration_min", sa.SmallInteger(), server_default="5", nullable=False),
        sa.Column("content_type", sa.String(16), server_default="quiz", nullable=False),
        sa.Column("content_json", JSONB(), server_default="{}", nullable=False),
        sa.Column("is_published", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_learning_lessons_chapter", "learning_lessons", ["chapter_id"])

    op.create_table(
        "learning_chapter_progress",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("chapter_id", UUID(as_uuid=True), sa.ForeignKey("learning_chapters.id"), primary_key=True),
        sa.Column("status", sa.String(16), server_default="empty", nullable=False),
        sa.Column("stars", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("lessons_completed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_lessons", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_studied_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "learning_lesson_progress",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("lesson_id", UUID(as_uuid=True), sa.ForeignKey("learning_lessons.id"), primary_key=True),
        sa.Column("status", sa.String(16), server_default="not_started", nullable=False),
        sa.Column("score", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("stars", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("time_spent_sec", sa.Integer(), server_default="0", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("answers_json", JSONB(), server_default="{}", nullable=False),
    )

    op.create_table(
        "learning_daily_summary",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("study_date", sa.Date(), primary_key=True),
        sa.Column("minutes_studied", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lessons_completed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("chapters_touched", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_table("learning_daily_summary")
    op.drop_table("learning_lesson_progress")
    op.drop_table("learning_chapter_progress")
    op.drop_table("learning_lessons")
    op.drop_table("learning_chapters")
    op.drop_table("learning_subjects")
