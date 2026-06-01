"""Unit tests for Chim Toán Vui progress."""

from app.schemas.play import SessionSummaryIn
from app.services.chim_toan_progress_service import (
    apply_chim_live_sync,
    apply_chim_progress,
    merge_extra,
)


def test_apply_chim_adds_gold_and_pb():
    summary = SessionSummaryIn(
        duration_s=120,
        score=40,
        questions_count=5,
        correct_count=4,
        accuracy=0.8,
        summary_json={"grade": 1, "tier": "T1", "play_mode": "prairie", "gold_earned": 8},
    )
    extra, events = apply_chim_progress({}, summary, summary.summary_json)
    assert extra["gold"] == 8
    assert extra["prairie_best_by_tier"]["T1"] == 40
    assert extra["lifetime_correct"] == 4
    assert events == []


def test_apply_chim_live_sync_adds_gold():
    extra = apply_chim_live_sync({"gold": 10}, 2)
    assert extra["gold"] == 14


def test_unlock_t3_after_lifetime():
    extra = merge_extra({"lifetime_correct": 48, "prairie_best_by_tier": {"T2": 10}})
    summary = SessionSummaryIn(
        duration_s=60,
        score=5,
        questions_count=2,
        correct_count=2,
        summary_json={"grade": 2, "tier": "T2", "gold_earned": 4},
    )
    extra, events = apply_chim_progress(extra, summary, summary.summary_json)
    assert extra["blocks"]["T3"]["unlocked"] is True
    assert "unlock_T3" in events
