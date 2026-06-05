from datetime import date, datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# --- Catalog ---

class PlayModeCatalogItem(BaseModel):
    id: str
    display_name: str
    tracks_learning: bool = False


class PlayGameCatalogItem(BaseModel):
    id: str
    display_name: str
    game_type: str
    hub_zone: str = "learning"
    subject: Optional[str] = None
    grade_min: int = 1
    grade_max: int = 5
    requires_wallet: bool = False
    modes: List[PlayModeCatalogItem] = []
    meta: Dict[str, Any] = {}
    launch_url: Optional[str] = None
    min_client_version: str = "1.0.0"
    is_public: bool = True


class PlayGamesResponse(BaseModel):
    games: List[PlayGameCatalogItem]


class PlayLevelCatalogItem(BaseModel):
    id: str
    title: str
    chapter_id: Optional[str] = None
    is_boss: bool = False
    prerequisite_level_ids: List[str] = []
    sort_index: int = 0
    objective: Optional[str] = None


class PlayLevelsResponse(BaseModel):
    game_mode_id: str
    levels: List[PlayLevelCatalogItem]


# --- Bootstrap ---

class PlayProfileOut(BaseModel):
    user_id: UUID
    target_grade: Optional[int] = None
    active_content_pack_id: str
    preferences: Dict[str, Any] = {}


class PlayContentPackOut(BaseModel):
    id: str
    manifest_version: str
    manifest_hash: str
    manifest_url: str


class PlayMasteryOut(BaseModel):
    skill_unit_id: str
    mastery_score: float
    rolling_accuracy: float


class PlayLevelProgressOut(BaseModel):
    level_id: str
    stars: int
    is_unlocked: bool
    last_played_at: Optional[datetime] = None


class PlayRecommendationOut(BaseModel):
    type: str
    skill_unit_id: Optional[str] = None
    reason: Optional[str] = None
    label: Optional[str] = None


class PlayGameStatsOut(BaseModel):
    high_score: int = 0
    total_sessions: int = 0


class PlayFlappyBootstrapOut(BaseModel):
    tier_unlocked: List[str] = []
    tier_mastery_progress: Dict[str, str] = {}
    personal_best: Dict[str, int] = {}
    daily_session_count: int = 0
    daily_session_soft_cap: int = 6


class PlayEnglishBootstrapOut(BaseModel):
    game_id: str = "english_shooter"
    gold: int = 0
    last_grade: int = 1
    rank: str = "recruit"
    lifetime_correct: int = 0
    voice_skins: Dict[str, bool] = {}
    blocks: Dict[str, Any] = {}
    themes_completed: List[str] = []
    prairie_best_by_theme: Dict[str, int] = {}
    weapon: Optional[Dict[str, Any]] = None
    themes: List[Dict[str, Any]] = []
    default_mode_id: str = "english_shooter:prairie"


class PlayStreakOut(BaseModel):
    current: int = 0
    last_active_date: Optional[date] = None


class PlayBootstrapResponse(BaseModel):
    profile: PlayProfileOut
    content_pack: Optional[PlayContentPackOut] = None
    mastery: List[PlayMasteryOut] = []
    level_progress: List[PlayLevelProgressOut] = []
    recommendations_today: List[PlayRecommendationOut] = []
    game_stats: PlayGameStatsOut = PlayGameStatsOut()
    flappy: Optional[PlayFlappyBootstrapOut] = None
    english: Optional[PlayEnglishBootstrapOut] = None
    streak: Optional[PlayStreakOut] = None
    wallet: Optional[PlayWalletOut] = None


# --- Sessions batch ---

class SessionStartOp(BaseModel):
    op: Literal["start"] = "start"
    session_id: UUID
    game_id: str
    game_mode_id: Optional[str] = None
    started_at: datetime
    content_pack_id: Optional[str] = None
    manifest_hash: Optional[str] = None


class SessionSummaryIn(BaseModel):
    duration_s: float
    level_id: Optional[str] = None
    stars: Optional[int] = None
    accuracy: Optional[float] = None
    questions_count: int = 0
    correct_count: int = 0
    score: Optional[int] = None
    summary_json: Dict[str, Any] = {}


class SessionEndOp(BaseModel):
    op: Literal["end"] = "end"
    session_id: UUID
    ended_at: datetime
    summary: SessionSummaryIn


SessionOp = Annotated[
    Union[SessionStartOp, SessionEndOp],
    Field(discriminator="op"),
]


class SessionsBatchRequest(BaseModel):
    sessions: List[SessionOp] = Field(..., min_length=1, max_length=5)

    @field_validator("sessions", mode="before")
    @classmethod
    def normalize_sessions(cls, v: Any) -> Any:
        if isinstance(v, dict) and "op" in v:
            return [v]
        if not isinstance(v, list):
            return v
        # Client bug: sessions: [[{ op: "start", ... }]] — flatten one level
        if len(v) == 1 and isinstance(v[0], list):
            return v[0]
        return v


class SessionBatchResult(BaseModel):
    session_id: UUID
    status: str
    level_progress: Optional[Dict[str, Any]] = None
    mastery_updated: List[str] = []
    new_high_score: bool = False


class SessionsBatchResponse(BaseModel):
    results: List[SessionBatchResult]
    bootstrap_etag: str


# --- Events batch ---

class PlayEventIn(BaseModel):
    client_seq: int
    occurred_at: datetime
    event_type: str
    skill_unit_id: Optional[str] = None
    level_id: Optional[str] = None
    item_id: Optional[str] = None
    correct: Optional[bool] = None
    latency_ms: Optional[int] = None
    score_delta: Optional[int] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class EventsBatchRequest(BaseModel):
    session_id: UUID
    events: List[PlayEventIn]

    @field_validator("events")
    @classmethod
    def max_events(cls, v):
        if len(v) > 100:
            raise ValueError("Maximum 100 events per batch")
        return v


class EventsBatchResponse(BaseModel):
    accepted: int
    duplicates: int
    rejected: int
    server_seq_max: int


# --- History ---

class PlayHistoryItem(BaseModel):
    session_id: UUID
    started_at: datetime
    duration_s: float
    mode: Optional[str] = None
    level_id: Optional[str] = None
    stars: Optional[int] = None
    accuracy: Optional[float] = None
    score: Optional[int] = None


class PlayHistoryResponse(BaseModel):
    items: List[PlayHistoryItem]
    next_cursor: Optional[str] = None


# --- Leaderboard ---

class LeaderboardEntry(BaseModel):
    rank: int
    display_name: str
    score: int
    is_you: bool = False


class LeaderboardResponse(BaseModel):
    period: str
    tier: Optional[str] = None
    entries: List[LeaderboardEntry]
    your_rank: Optional[int] = None
    your_score: Optional[int] = None


# --- Parent ---

class ParentChildGameSummary(BaseModel):
    game_id: str
    game_mode_id: Optional[str] = None
    sessions: int = 0
    levels_cleared: int = 0
    avg_accuracy: Optional[float] = None
    weak_skills: List[Dict[str, Any]] = []
    recent_levels: List[Dict[str, Any]] = []
    personal_best: Optional[int] = None
    daily_session_count: Optional[int] = None
    soft_cap: Optional[int] = None


class ParentChildDashboard(BaseModel):
    user_id: UUID
    display_name: str
    target_grade: Optional[int] = None
    streak: Dict[str, Any] = {}
    totals: Dict[str, Any] = {}
    by_game: List[ParentChildGameSummary] = []
    recommendations_today: List[PlayRecommendationOut] = []


class ParentDashboardResponse(BaseModel):
    family_id: UUID
    period: str
    children: List[ParentChildDashboard]
    etag: str


class ParentChildLevelsResponse(BaseModel):
    user_id: UUID
    levels: List[PlayLevelProgressOut]


class PlayWalletOut(BaseModel):
    available_balance: int = 0
    accounts: Dict[str, int] = {}
    total_earned_learning: int = 0
    total_spent_reward: int = 0


class PlayWalletLedgerItem(BaseModel):
    id: int
    account_code: str
    entry_type: str
    amount: int
    balance_after: int
    ref_game_id: Optional[str] = None
    ref_reward_game_id: Optional[str] = None
    note: Optional[str] = None
    created_at: Optional[str] = None


class RewardGameOut(BaseModel):
    id: str
    title: str
    title_vi: str
    emoji: str
    route: str
    color: str
    desc_en: str
    desc_vi: str
    genre: str = "reflex"
    player_mode: str = "solo"
    co_op_parent: bool = False
    rollout_status: str = "live"
    session_cap_seconds: int = 600
    unlocked: bool
    unlock_hint: str
    play_cost: int = 0


class RewardSectionOut(BaseModel):
    key: str
    title_en: str
    title_vi: str
    game_ids: List[str] = []


class RewardPlaygroundResponse(BaseModel):
    test_unlock_all: bool = False
    skip_reward_spend: bool = False
    logged_in: bool = False
    metrics: Optional[Dict[str, Any]] = None
    wallet: Optional[PlayWalletOut] = None
    games: List[RewardGameOut] = []
    sections: List[RewardSectionOut] = []
    unlocked_count: int = 0
    total_count: int = 0


class SpendRewardPlayRequest(BaseModel):
    reward_game_id: str
    session_id: Optional[UUID] = None


class SpendRewardPlayResponse(BaseModel):
    ok: bool
    message: str
    wallet: Optional[PlayWalletOut] = None
