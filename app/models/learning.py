import uuid

import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, DateTime, SmallInteger, Integer, Text, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class LearningSubject(Base):
    __tablename__ = "learning_subjects"

    id = Column(String(32), primary_key=True)
    grade = Column(SmallInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(8), server_default="📚", nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, server_default="true", nullable=False)
    sort_order = Column(SmallInteger, server_default="0", nullable=False)
    color_primary = Column(String(16), server_default="#E85D24", nullable=False)
    color_bg = Column(String(16), server_default="#FAECE7", nullable=False)
    color_dark = Column(String(16), server_default="#993C1D", nullable=False)
    textbook_series = Column(String(64), server_default="ket_noi_tri_thuc", nullable=False)
    is_active = Column(Boolean, server_default="true", nullable=False)


class LearningChapter(Base):
    __tablename__ = "learning_chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(String(32), ForeignKey("learning_subjects.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    subtitle = Column(String(300), nullable=True)
    sort_index = Column(Integer, server_default="0", nullable=False)
    est_minutes = Column(SmallInteger, server_default="25", nullable=False)
    prerequisite_chapter_id = Column(UUID(as_uuid=True), ForeignKey("learning_chapters.id"), nullable=True)
    textbook_ref = Column(String(200), nullable=True)
    week_number = Column(SmallInteger, nullable=True)
    is_published = Column(Boolean, server_default="false", nullable=False)


class LearningLesson(Base):
    __tablename__ = "learning_lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("learning_chapters.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(String(500), nullable=True)
    sort_index = Column(Integer, server_default="0", nullable=False)
    duration_min = Column(SmallInteger, server_default="5", nullable=False)
    content_type = Column(String(16), server_default="quiz", nullable=False)
    content_json = Column(JSONB, server_default="{}", nullable=False)
    progress_emoji = Column(String(8), server_default="🍏", nullable=False)
    is_published = Column(Boolean, server_default="false", nullable=False)


class LearningLessonStep(Base):
    __tablename__ = "learning_lesson_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("learning_lessons.id"), nullable=False, index=True)
    sort_index = Column(SmallInteger, server_default="0", nullable=False)
    step_type = Column(String(32), nullable=False)
    emoji_icon = Column(String(8), server_default="👀", nullable=False)
    config_json = Column(JSONB, server_default="{}", nullable=False)
    est_seconds = Column(Integer, server_default="60", nullable=False)
    is_required = Column(Boolean, server_default="true", nullable=False)


class LearningStepProgress(Base):
    __tablename__ = "learning_step_progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("learning_lesson_steps.id"), primary_key=True)
    status = Column(String(16), server_default="not_started", nullable=False)
    score = Column(SmallInteger, server_default="0", default=0, nullable=False)
    attempts = Column(Integer, server_default="0", default=0, nullable=False)
    result_json = Column(JSONB, server_default="{}", nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class LearningGradeSchedule(Base):
    __tablename__ = "learning_grade_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    grade = Column(SmallInteger, nullable=False, index=True)
    semester = Column(SmallInteger, server_default="1", nullable=False)
    week_number = Column(SmallInteger, server_default="1", nullable=False)
    label = Column(String(100), nullable=False)
    is_active = Column(Boolean, server_default="true", nullable=False)


class LearningScheduleSlot(Base):
    __tablename__ = "learning_schedule_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("learning_grade_schedules.id"), nullable=False, index=True)
    weekday = Column(SmallInteger, nullable=False)
    session = Column(String(16), nullable=False)
    slot_order = Column(SmallInteger, server_default="1", nullable=False)
    subject_id = Column(String(32), ForeignKey("learning_subjects.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("learning_lessons.id"), nullable=True)


class LearningFamilyCheckpoint(Base):
    __tablename__ = "learning_family_checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    step_id = Column(UUID(as_uuid=True), ForeignKey("learning_lesson_steps.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("learning_lessons.id"), nullable=False)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(String(16), server_default="pending", nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)


class LearningChapterProgress(Base):
    __tablename__ = "learning_chapter_progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("learning_chapters.id"), primary_key=True)
    status = Column(String(16), server_default="empty", nullable=False)
    stars = Column(SmallInteger, server_default="0", default=0, nullable=False)
    lessons_completed = Column(Integer, server_default="0", default=0, nullable=False)
    total_lessons = Column(Integer, server_default="0", default=0, nullable=False)
    last_studied_at = Column(DateTime(timezone=True), nullable=True)


class LearningLessonProgress(Base):
    __tablename__ = "learning_lesson_progress"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("learning_lessons.id"), primary_key=True)
    status = Column(String(16), server_default="not_started", nullable=False)
    score = Column(SmallInteger, server_default="0", default=0, nullable=False)
    stars = Column(SmallInteger, server_default="0", default=0, nullable=False)
    time_spent_sec = Column(Integer, server_default="0", default=0, nullable=False)
    attempts = Column(Integer, server_default="0", default=0, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    answers_json = Column(JSONB, server_default="{}", nullable=False)
    steps_summary = Column(JSONB, server_default="{}", nullable=False)


class LearningDailySummary(Base):
    __tablename__ = "learning_daily_summary"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    study_date = Column(Date, primary_key=True)
    minutes_studied = Column(Integer, server_default="0", default=0, nullable=False)
    lessons_completed = Column(Integer, server_default="0", default=0, nullable=False)
    chapters_touched = Column(Integer, server_default="0", default=0, nullable=False)
    steps_completed = Column(Integer, server_default="0", default=0, nullable=False)
    checkpoints_confirmed = Column(Integer, server_default="0", default=0, nullable=False)
