"""Unit tests for Gà Toán sticker unlock rules."""

from app.schemas.play import SessionSummaryIn
from app.services.flappy_sticker_service import apply_flappy_stickers, FLAPPY_STICKER_CATALOG


def _end_summary(**kwargs):
    base = {
        "duration_s": 120,
        "score": 25,
        "questions_count": 8,
        "correct_count": 5,
        "accuracy": 0.625,
        "summary_json": {
            "play_mode": "practice",
            "tier": "T1",
            "grade": 1,
            "combo_max": 3,
            "play_date": "2026-05-21",
            "manual_end": True,
            "persistent_correct": False,
            "ended_by_timer": False,
        },
    }
    base.update(kwargs)
    sj = base.pop("summary_json", {})
    return SessionSummaryIn(
        duration_s=base["duration_s"],
        score=base["score"],
        questions_count=base["questions_count"],
        correct_count=base["correct_count"],
        accuracy=base["accuracy"],
        summary_json=sj,
    )


def test_practice_unlocks_ga_con_and_ga_nhay():
    extra, new = apply_flappy_stickers({}, _end_summary(correct_count=5))
    assert "ga_con" in new
    assert "ga_nhay" in new
    assert "ga_con" in extra["stickers_unlocked"]


def test_sprint_unlocks_combo_and_score():
    summary = _end_summary(
        correct_count=10,
        score=55,
        summary_json={
            "play_mode": "sprint",
            "tier": "T1",
            "grade": 1,
            "combo_max": 5,
            "play_date": "2026-05-21",
            "ended_by_timer": True,
        },
    )
    extra, new = apply_flappy_stickers({}, summary, new_pb_for_tier=False)
    assert "ga_dua" in new
    assert "chuoi_3" in new
    assert "chuoi_5" in new
    assert "nhanh_tay" in new
    assert "diem_50" in new
    assert "het_gio" in new


def test_lifetime_trung_vang_after_accumulation():
    extra = {"stickers_unlocked": ["ga_con"], "sticker_stats": {"lifetime_correct": 8, "play_days": ["2026-05-20"]}}
    summary = _end_summary(correct_count=2, score=10)
    extra, new = apply_flappy_stickers(extra, summary)
    assert "trung_vang" in new
    assert extra["sticker_stats"]["lifetime_correct"] == 10


def test_catalog_has_sixteen_stickers():
    assert len(FLAPPY_STICKER_CATALOG) == 16
