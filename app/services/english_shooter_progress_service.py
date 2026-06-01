"""English Shooter — tiến trình vàng, chủ đề, rank (extra_json trên play_user_game_stats)."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.schemas.play import SessionSummaryIn

MODE_PRAIRIE = "english_shooter:prairie"
MODE_CITY = "english_shooter:city"
MODE_BOSS = "english_shooter:boss"
GAME_ID = "english_shooter"

GOLD_PER_VOCAB_HIT = 5
GOLD_PER_SENTENCE = 20
SPEAKING_BONUS = 30

RANK_THRESHOLDS = [
    (0, "recruit", "Tân binh"),
    (1, "soldier", "Chiến sĩ"),
    (50, "commander", "Chỉ huy"),
    (200, "global_commander", "Global Commander"),
]


def default_extra() -> Dict[str, Any]:
    return {
        "gold": 0,
        "last_grade": 1,
        "rank": "recruit",
        "lifetime_correct": 0,
        "themes_completed": [],
        "prairie_best_by_theme": {},
        "voice_skins": {
            "robot": False,
            "phoenix": False,
            "airship": False,
            "mecha": False,
            "ai_commander": False,
            "dragon": False,
        },
        "blocks": {
            "city": {"unlocked": False, "label": "Bảo vệ thành phố", "grades": "1–5"},
            "boss": {"unlocked": False, "label": "Đại Boss", "grades": "1–5"},
        },
        "journal_entries": [],
    }


def merge_extra(extra: Dict[str, Any] | None) -> Dict[str, Any]:
    base = default_extra()
    if not extra:
        return base
    out = {**base, **extra}
    pb = dict(base["prairie_best_by_theme"])
    pb.update(extra.get("prairie_best_by_theme") or {})
    out["prairie_best_by_theme"] = pb
    skins = dict(base["voice_skins"])
    skins.update(extra.get("voice_skins") or {})
    out["voice_skins"] = skins
    blocks = dict(base["blocks"])
    for k, v in (extra.get("blocks") or {}).items():
        if k in blocks and isinstance(v, dict):
            blocks[k] = {**blocks[k], **v}
    out["blocks"] = blocks
    return out


def _rank_for_lifetime(lifetime: int) -> str:
    rank = "recruit"
    for threshold, key, _ in RANK_THRESHOLDS:
        if lifetime >= threshold:
            rank = key
    return rank


def apply_english_live_sync(extra: Dict[str, Any] | None, correct_count: int, gold_delta: int = 0) -> Dict[str, Any]:
    """Cộng vàng khi sync batch câu đúng (client gọi events/batch)."""
    extra = merge_extra(extra)
    if correct_count > 0:
        extra["lifetime_correct"] = int(extra.get("lifetime_correct") or 0) + correct_count
    if gold_delta > 0:
        extra["gold"] = int(extra.get("gold") or 0) + gold_delta
    extra["rank"] = _rank_for_lifetime(int(extra.get("lifetime_correct") or 0))
    return extra


def apply_english_session_end(
    extra: Dict[str, Any],
    summary: SessionSummaryIn,
    summary_json: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """Cập nhật sau phiên; trả (extra, unlock_messages)."""
    extra = merge_extra(extra)
    events: List[str] = []
    correct = int(summary.correct_count or 0)
    live_synced = bool(summary_json.get("live_synced"))
    gold_delta = int(summary_json.get("gold_earned") or 0)
    if not live_synced:
        if gold_delta <= 0 and correct > 0:
            play_mode = summary_json.get("play_mode") or "prairie"
            if play_mode == "prairie":
                gold_delta = correct * GOLD_PER_VOCAB_HIT
            elif play_mode == "city":
                gold_delta = correct * GOLD_PER_SENTENCE
        if gold_delta > 0:
            extra["gold"] = int(extra.get("gold") or 0) + gold_delta
        extra["lifetime_correct"] = int(extra.get("lifetime_correct") or 0) + correct
    elif gold_delta > 0:
        extra["gold"] = int(extra.get("gold") or 0) + gold_delta

    grade = int(summary_json.get("grade") or extra.get("last_grade") or 1)
    extra["last_grade"] = grade
    extra["rank"] = _rank_for_lifetime(int(extra.get("lifetime_correct") or 0))

    theme_id = summary_json.get("theme_id")
    score = int(summary.score or 0)
    if theme_id and summary_json.get("play_mode") == "prairie":
        pb = dict(extra.get("prairie_best_by_theme") or {})
        if score > int(pb.get(theme_id, 0) or 0):
            pb[theme_id] = score
            extra["prairie_best_by_theme"] = pb

    if summary_json.get("theme_completed") and theme_id:
        completed = list(extra.get("themes_completed") or [])
        if theme_id not in completed:
            completed.append(theme_id)
            extra["themes_completed"] = completed

    if len(extra.get("themes_completed") or []) >= 1:
        blocks = dict(extra.get("blocks") or {})
        if not blocks.get("city", {}).get("unlocked"):
            blocks["city"] = {**blocks.get("city", {}), "unlocked": True}
            extra["blocks"] = blocks
            events.append("unlock_city")

    if int(extra.get("lifetime_correct") or 0) >= 30:
        blocks = dict(extra.get("blocks") or {})
        if not blocks.get("boss", {}).get("unlocked"):
            blocks["boss"] = {**blocks.get("boss", {}), "unlocked": True}
            extra["blocks"] = blocks
            events.append("unlock_boss")

    return extra, events
