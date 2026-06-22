from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GradeItem(BaseModel):
    grade: int
    label: str
    stars_hint: str = "⭐⭐⭐"
    color_primary: str
    color_bg: str
    color_dark: str


class GradesResponse(BaseModel):
    grades: List[GradeItem]


class SubjectItem(BaseModel):
    id: str
    name: str
    icon: str
    description: Optional[str] = None
    is_required: bool = True
    color_primary: str
    color_bg: str
    color_dark: str
    progress_pct: int = 0
    chapters_done: int = 0
    chapters_total: int = 0


class SubjectsResponse(BaseModel):
    grade: int
    subjects: List[SubjectItem]


class ChapterMapItem(BaseModel):
    id: UUID
    name: str
    subtitle: Optional[str] = None
    sort_index: int
    status: str = "empty"
    stars: int = 0
    est_minutes: int = 25
    lesson_count: int = 0


class SubjectMapMeta(BaseModel):
    id: str
    name: str
    icon: str
    grade: int
    description: Optional[str] = None
    color_primary: str
    color_bg: str
    color_dark: str


class OverallProgress(BaseModel):
    done: int = 0
    partial: int = 0
    total: int = 0
    progress_pct: int = 0


class SubjectMapResponse(BaseModel):
    subject: SubjectMapMeta
    overall: OverallProgress
    chapters: List[ChapterMapItem]


class LessonListItem(BaseModel):
    id: UUID
    title: str
    summary: Optional[str] = None
    duration_min: int
    content_type: str
    status: str = "not_started"
    stars: int = 0
    sort_index: int = 0
    already_completed: bool = False


class ChapterLessonsResponse(BaseModel):
    chapter: Dict[str, Any]
    lessons: List[LessonListItem]


class TeacherLessonItem(BaseModel):
    id: UUID
    title: str
    summary: Optional[str] = None
    duration_min: int
    content_type: str = "quiz"
    subject_id: str
    subject_name: str
    subject_icon: str
    chapter_name: str
    status: str = "not_started"
    stars: int = 0
    step_count: int = 0
    progress_emoji: str = "🍏"
    already_completed: bool = False
    sort_index: int = 0


class TeacherLessonsResponse(BaseModel):
    grade: int
    total: int = 0
    lessons: List[TeacherLessonItem]


class LessonContentResponse(BaseModel):
    id: UUID
    title: str
    duration_min: int
    content_type: str
    content: Dict[str, Any]
    already_completed: bool = False
    is_replay: bool = False


class LessonCompleteRequest(BaseModel):
    score: int = Field(ge=0, le=100)
    time_spent_sec: int = Field(ge=0, le=7200)
    answers: List[Dict[str, Any]] = Field(default_factory=list)


class LessonProgressResult(BaseModel):
    status: str
    stars: int
    score: int


class ChapterProgressResult(BaseModel):
    status: str
    stars: int
    lessons_completed: int
    total_lessons: int


class DailySummaryResult(BaseModel):
    study_date: date
    minutes_studied: int
    lessons_completed: int


class LessonCompleteResponse(BaseModel):
    lesson: LessonProgressResult
    chapter: ChapterProgressResult
    daily: DailySummaryResult
    replay: bool = False


class TodaySummaryResponse(BaseModel):
    minutes_studied: int
    lessons_completed: int
    goal_min: int = 15
    goal_max: int = 60


class ParentSubjectProgress(BaseModel):
    subject_id: str
    name: str
    icon: str
    grade: int
    progress_pct: int
    stars_total: int


class ParentKidOverview(BaseModel):
    kid_id: UUID
    display_name: str
    today_minutes: int
    week_minutes: int
    today_lessons: int = 0
    subjects: List[ParentSubjectProgress]


class ParentCheckpointItem(BaseModel):
    checkpoint_id: str
    kid_id: str
    kid_name: str
    lesson_id: str
    lesson_title: str
    requested_at: Optional[str] = None


class ParentOverviewResponse(BaseModel):
    kids: List[ParentKidOverview]
    pending_checkpoints: List[ParentCheckpointItem] = Field(default_factory=list)


class ParentTimelineDay(BaseModel):
    date: date
    minutes: int
    lessons: int


class ParentTimelineResponse(BaseModel):
    days: List[ParentTimelineDay]


# Guided player
class StepSubmitRequest(BaseModel):
    interaction: str = Field(description="stt|choice|write|checkpoint_request|skip")
    payload: Dict[str, Any] = Field(default_factory=dict)
    time_spent_sec: int = Field(default=0, ge=0, le=7200)


class StepFeedback(BaseModel):
    type: str
    tts_text: Optional[str] = None
    emoji_burst: List[str] = Field(default_factory=list)
    checkpoint_id: Optional[str] = None


class StepSubmitResponse(BaseModel):
    step: Dict[str, Any]
    feedback: StepFeedback
    next_step_index: int
    lesson_complete: bool
    completion: Optional[Dict[str, Any]] = None


class LessonPlayerResponse(BaseModel):
    lesson: Dict[str, Any]
    steps: List[Dict[str, Any]]
    resume_at_step_index: int


class ScheduleTodayResponse(BaseModel):
    date: str
    weekday: int
    week_label: str
    slots: List[Dict[str, Any]]
    daily_goal: Dict[str, int]


class CheckpointConfirmResponse(BaseModel):
    ok: bool
    checkpoint_id: str
    lesson_complete: bool
    completion: Optional[Dict[str, Any]] = None


# Admin
class AdminSubjectCreate(BaseModel):
    id: str
    grade: int
    name: str
    icon: str = "📚"
    description: Optional[str] = None
    is_required: bool = True
    sort_order: int = 0
    color_primary: str = "#E85D24"
    color_bg: str = "#FAECE7"
    color_dark: str = "#993C1D"


class AdminSubjectUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None
    color_primary: Optional[str] = None
    color_bg: Optional[str] = None
    color_dark: Optional[str] = None
    is_active: Optional[bool] = None


class AdminChapterCreate(BaseModel):
    subject_id: str
    name: str
    subtitle: Optional[str] = None
    sort_index: int = 0
    est_minutes: int = 25
    textbook_ref: Optional[str] = None


class AdminChapterUpdate(BaseModel):
    name: Optional[str] = None
    subtitle: Optional[str] = None
    sort_index: Optional[int] = None
    est_minutes: Optional[int] = None
    textbook_ref: Optional[str] = None
    is_published: Optional[bool] = None


class AdminLessonCreate(BaseModel):
    chapter_id: UUID
    title: str
    summary: Optional[str] = None
    sort_index: int = 0
    duration_min: int = 5
    content_type: str = "quiz"
    content_json: Dict[str, Any] = Field(default_factory=dict)
    is_published: bool = False


class AdminLessonUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    sort_index: Optional[int] = None
    duration_min: Optional[int] = None
    content_type: Optional[str] = None
    content_json: Optional[Dict[str, Any]] = None
    progress_emoji: Optional[str] = None
    is_published: Optional[bool] = None


class AdminStepCreate(BaseModel):
    sort_index: int = 0
    step_type: str
    emoji_icon: str = "👀"
    config_json: Dict[str, Any] = Field(default_factory=dict)
    est_seconds: int = 60
    is_required: bool = True


class AdminStepUpdate(BaseModel):
    sort_index: Optional[int] = None
    step_type: Optional[str] = None
    emoji_icon: Optional[str] = None
    config_json: Optional[Dict[str, Any]] = None
    est_seconds: Optional[int] = None
    is_required: Optional[bool] = None
