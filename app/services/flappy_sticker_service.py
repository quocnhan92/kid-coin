"""Gà Toán — bộ sưu tập sticker (luyện tập + cuộc đua)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.play import SessionSummaryIn

# Catalog exposed to clients via bootstrap sticker_meta
FLAPPY_STICKER_CATALOG: List[Dict[str, str]] = [
    # Luyện tập nhẹ
    {"id": "ga_con", "emoji": "🐥", "name": "Gà con", "hint": "Luyện tập: làm đúng 1 câu", "group": "practice"},
    {"id": "ga_nhay", "emoji": "⭐", "name": "Gà nhảy", "hint": "Luyện tập: 5 câu đúng trong một phiên", "group": "practice"},
    {"id": "xong_roi", "emoji": "✅", "name": "Xong rồi", "hint": "Luyện tập: bấm Xong rồi sau ≥3 câu đúng", "group": "practice"},
    {"id": "kien_tri", "emoji": "💪", "name": "Kiên trì", "hint": "Luyện tập: đúng sau khi sai 2 lần liên tiếp", "group": "practice"},
    {"id": "ga_thong_thai", "emoji": "🎓", "name": "Gà thông thái", "hint": "Luyện tập: 8 câu đúng trong một phiên", "group": "practice"},
    # Cuộc đua 60 giây
    {"id": "ga_dua", "emoji": "🏁", "name": "Gà đua", "hint": "Cuộc đua: làm đúng 1 câu", "group": "sprint"},
    {"id": "chuoi_3", "emoji": "🔥", "name": "Chuỗi 3", "hint": "Cuộc đua: chuỗi đúng ≥3", "group": "sprint"},
    {"id": "chuoi_5", "emoji": "⚡", "name": "Chuỗi 5", "hint": "Cuộc đua: chuỗi đúng ≥5", "group": "sprint"},
    {"id": "nhanh_tay", "emoji": "👆", "name": "Nhanh tay", "hint": "Cuộc đua: 10 câu đúng trong 60 giây", "group": "sprint"},
    {"id": "diem_50", "emoji": "🥈", "name": "50 điểm", "hint": "Cuộc đua: đạt ≥50 điểm", "group": "sprint"},
    {"id": "diem_100", "emoji": "🥇", "name": "100 điểm", "hint": "Cuộc đua: đạt ≥100 điểm", "group": "sprint"},
    {"id": "ky_luc", "emoji": "🏆", "name": "Kỷ lục mới", "hint": "Cuộc đua: phá kỷ lục lớp đang chơi", "group": "sprint"},
    {"id": "het_gio", "emoji": "⏱", "name": "Trọn 60 giây", "hint": "Cuộc đua: chơi hết thời gian", "group": "sprint"},
    # Chung (cả hai chế độ)
    {"id": "trung_vang", "emoji": "🥚", "name": "Trứng vàng", "hint": "Tổng cộng 10 câu đúng (mọi chế độ)", "group": "both"},
    {"id": "ga_ban", "emoji": "🌽", "name": "Bạn gà", "hint": "Tổng cộng 25 câu đúng", "group": "both"},
    {"id": "ga_mua", "emoji": "🌧", "name": "Gà mưa", "hint": "Chơi 3 ngày khác nhau", "group": "both"},
    {"id": "tuan_vui", "emoji": "🌈", "name": "Tuần vui", "hint": "Chơi 7 ngày khác nhau", "group": "both"},
]

STICKER_IDS: Set[str] = {s["id"] for s in FLAPPY_STICKER_CATALOG}


def _default_stats() -> Dict[str, Any]:
    return {
        "lifetime_correct": 0,
        "play_days": [],
        "practice_sessions": 0,
        "sprint_sessions": 0,
        "best_combo_sprint": 0,
    }


def _parse_play_date(summary_json: Dict[str, Any], ended_at: Optional[datetime]) -> str:
    raw = summary_json.get("play_date")
    if isinstance(raw, str) and len(raw) >= 10:
        return raw[:10]
    if ended_at:
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        return ended_at.date().isoformat()
    return date.today().isoformat()


def apply_flappy_stickers(
    extra: Dict[str, Any],
    summary: SessionSummaryIn,
    summary_json: Dict[str, Any],
    *,
    new_pb_for_tier: bool = False,
    ended_at: Optional[datetime] = None,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Cập nhật extra_json (stickers_unlocked, sticker_stats) và trả về id sticker mới mở.
    """
    extra = dict(extra or {})
    unlocked: Set[str] = set(extra.get("stickers_unlocked") or [])
    stats = dict(extra.get("sticker_stats") or _default_stats())
    for k, v in _default_stats().items():
        stats.setdefault(k, v if not isinstance(v, list) else [])

    play_mode = summary_json.get("play_mode") or "sprint"
    correct = int(summary.correct_count or 0)
    score = int(summary.score or 0)
    combo_max = int(summary_json.get("combo_max") or 0)
    manual_end = bool(summary_json.get("manual_end"))
    persistent_correct = bool(summary_json.get("persistent_correct"))
    ended_by_timer = bool(summary_json.get("ended_by_timer"))
    duration_s = int(summary.duration_s or 0)

    play_day = _parse_play_date(summary_json, ended_at)
    days: Set[str] = set(stats.get("play_days") or [])
    days.add(play_day)
    stats["play_days"] = sorted(days)

    stats["lifetime_correct"] = int(stats.get("lifetime_correct") or 0) + correct
    if play_mode == "practice":
        stats["practice_sessions"] = int(stats.get("practice_sessions") or 0) + 1
    else:
        stats["sprint_sessions"] = int(stats.get("sprint_sessions") or 0) + 1
        stats["best_combo_sprint"] = max(int(stats.get("best_combo_sprint") or 0), combo_max)

    candidates: List[str] = []

    if play_mode == "practice":
        if correct >= 1:
            candidates.append("ga_con")
        if correct >= 5:
            candidates.append("ga_nhay")
        if correct >= 8:
            candidates.append("ga_thong_thai")
        if manual_end and correct >= 3:
            candidates.append("xong_roi")
        if persistent_correct:
            candidates.append("kien_tri")
    else:
        if correct >= 1:
            candidates.append("ga_dua")
        if combo_max >= 3:
            candidates.append("chuoi_3")
        if combo_max >= 5:
            candidates.append("chuoi_5")
        if correct >= 10:
            candidates.append("nhanh_tay")
        if score >= 50:
            candidates.append("diem_50")
        if score >= 100:
            candidates.append("diem_100")
        if new_pb_for_tier and score > 0:
            candidates.append("ky_luc")
        if ended_by_timer or duration_s >= 55:
            candidates.append("het_gio")

    lifetime = int(stats["lifetime_correct"])
    if lifetime >= 10:
        candidates.append("trung_vang")
    if lifetime >= 25:
        candidates.append("ga_ban")
    if len(days) >= 3:
        candidates.append("ga_mua")
    if len(days) >= 7:
        candidates.append("tuan_vui")

    new_unlocks = [c for c in candidates if c in STICKER_IDS and c not in unlocked]
    unlocked.update(new_unlocks)
    extra["stickers_unlocked"] = sorted(unlocked)
    extra["sticker_stats"] = stats
    return extra, new_unlocks
