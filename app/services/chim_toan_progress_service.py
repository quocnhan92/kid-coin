"""Chim Toán Vui — tiến trình Thảo nguyên & khung block L3–5."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.schemas.play import SessionSummaryIn

MODE_ID = "math_blast:chim"
UNLOCK_T3_LIFETIME = 50
UNLOCK_T3_T2_BEST = 30


def default_blocks() -> Dict[str, Dict[str, Any]]:
    return {
        "T3": {"unlocked": False, "label": "Rừng sương", "grade": 3},
        "T4": {"unlocked": False, "label": "Ngoại ô", "grade": 4},
        "T5": {"unlocked": False, "label": "Thành phố", "grade": 5},
    }


def default_extra() -> Dict[str, Any]:
    return {
        "gold": 0,
        "last_grade": 1,
        "last_play_mode": "prairie",
        "prairie_best_by_tier": {},
        "lifetime_correct": 0,
        "blocks": default_blocks(),
    }


def merge_extra(extra: Dict[str, Any] | None) -> Dict[str, Any]:
    base = default_extra()
    if not extra:
        return base
    out = {**base, **extra}
    pb = dict(base["prairie_best_by_tier"])
    pb.update(extra.get("prairie_best_by_tier") or {})
    out["prairie_best_by_tier"] = pb
    blocks = default_blocks()
    for k, v in (extra.get("blocks") or {}).items():
        if k in blocks and isinstance(v, dict):
            blocks[k] = {**blocks[k], **v}
    out["blocks"] = blocks
    return out


def _tier_from_summary(summary_json: Dict[str, Any]) -> str:
    tier = summary_json.get("tier")
    if tier:
        return str(tier)
    grade = summary_json.get("grade")
    return f"T{int(grade)}" if grade is not None else "T1"


GOLD_PER_CORRECT = 2


def apply_chim_live_sync(extra: Dict[str, Any] | None, correct_count: int) -> Dict[str, Any]:
    """Cộng vàng / lifetime khi client sync batch (mỗi 2 câu đúng)."""
    extra = merge_extra(extra)
    if correct_count <= 0:
        return extra
    extra["gold"] = int(extra.get("gold") or 0) + correct_count * GOLD_PER_CORRECT
    return extra


def apply_chim_progress(
    extra: Dict[str, Any],
    summary: SessionSummaryIn,
    summary_json: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """Cập nhật extra_json sau phiên; trả về (extra, events) events = unlock messages."""
    extra = merge_extra(extra)
    events: List[str] = []
    tier = _tier_from_summary(summary_json)
    grade = int(summary_json.get("grade") or int(tier.replace("T", "") or 1))
    correct = int(summary.correct_count or 0)
    score = int(summary.score or 0)
    gold_delta = int(summary_json.get("gold_earned") or 0)
    if gold_delta <= 0 and correct > 0:
        gold_delta = correct * GOLD_PER_CORRECT

    extra["gold"] = int(extra.get("gold") or 0) + gold_delta
    extra["last_grade"] = grade
    extra["last_play_mode"] = summary_json.get("play_mode") or "prairie"
    extra["lifetime_correct"] = int(extra.get("lifetime_correct") or 0) + correct

    pb = dict(extra.get("prairie_best_by_tier") or {})
    if score > int(pb.get(tier, 0) or 0):
        pb[tier] = score
        extra["prairie_best_by_tier"] = pb

    blocks = dict(extra.get("blocks") or default_blocks())
    lifetime = extra["lifetime_correct"]
    t2_best = int(pb.get("T2", 0) or 0)
    if lifetime >= UNLOCK_T3_LIFETIME or t2_best >= UNLOCK_T3_T2_BEST:
        if not blocks.get("T3", {}).get("unlocked"):
            blocks["T3"] = {**blocks.get("T3", {}), "unlocked": True}
            events.append("unlock_T3")
    extra["blocks"] = blocks
    return extra, events
