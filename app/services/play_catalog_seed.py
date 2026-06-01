"""Idempotent seed for play catalog (games, modes, World 1 sample levels)."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.play import (
    PlayGame,
    PlayGameMode,
    PlayContentPack,
    PlaySkillUnit,
    PlayLevel,
    PlayGameRelease,
)

logger = logging.getLogger(__name__)

CONTENT_PACK_ID = "vn_gdpt2018_candy_v1"
MANIFEST_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def seed_play_catalog(db: Session) -> None:
    if db.query(PlayGame).first():
        return

    logger.info("Seeding play catalog...")
    now = datetime.now(timezone.utc)

    db.add(
        PlayContentPack(
            id=CONTENT_PACK_ID,
            locale="vi-VN",
            grade_min=1,
            grade_max=5,
            manifest_version="1.0.0",
            manifest_hash=MANIFEST_HASH,
            published_at=now,
        )
    )

    games = [
        PlayGame(
            id="math_blast",
            display_name="Math Blast",
            game_type="learning",
            is_active=True,
            current_release_id="math_blast@1.0.0",
            sort_order=1,
            meta_json={"icon": "🚀", "route": "/game/math-blast-v2"},
        ),
        PlayGame(id="snake", display_name="Rắn săn mồi", game_type="arcade", is_active=True, sort_order=2, meta_json={"route": "/game/snake"}),
        PlayGame(id="2048", display_name="2048", game_type="arcade", is_active=True, sort_order=3, meta_json={"route": "/game/2048"}),
        PlayGame(id="memory", display_name="Lật bài", game_type="arcade", is_active=True, sort_order=4, meta_json={"route": "/game/memory"}),
        PlayGame(id="flappy_classic", display_name="Flappy Baby", game_type="arcade", is_active=True, sort_order=5, meta_json={"route": "/game/flappy"}),
    ]
    db.add_all(games)

    modes = [
        PlayGameMode(
            id="math_blast:candy",
            game_id="math_blast",
            mode_key="candy",
            display_name="Phiêu lưu 300 màn",
            tracks_learning=True,
            content_pack_id=CONTENT_PACK_ID,
            config_json={},
        ),
        PlayGameMode(
            id="math_blast:flappy",
            game_id="math_blast",
            mode_key="flappy",
            display_name="Gà Toán",
            tracks_learning=True,
            content_pack_id=CONTENT_PACK_ID,
            config_json={"sprint_seconds": 60, "tiers": ["T1", "T2", "T3", "T4", "T5"]},
        ),
        PlayGameMode(
            id="math_blast:chim",
            game_id="math_blast",
            mode_key="chim",
            display_name="Chim Toán Vui",
            tracks_learning=True,
            content_pack_id=CONTENT_PACK_ID,
            config_json={"prairie_grades": [1, 2], "blocks": ["T3", "T4", "T5"]},
        ),
        PlayGameMode(
            id="math_blast:arcade_class",
            game_id="math_blast",
            mode_key="arcade_class",
            display_name="Giải trí lớp học",
            tracks_learning=False,
            config_json={},
        ),
        PlayGameMode(
            id="math_blast:arcade_free",
            game_id="math_blast",
            mode_key="arcade_free",
            display_name="Giải trí tự do",
            tracks_learning=False,
            config_json={},
        ),
    ]
    db.add_all(modes)

    skill = PlaySkillUnit(
        id="l1_add_within_10",
        content_pack_id=CONTENT_PACK_ID,
        grade=1,
        title="Cộng trong phạm vi 10",
        tags_json=["add", "grade1"],
    )
    db.add(skill)
    db.flush()

    for i in range(1, 19):
        lid = f"L{i:03d}"
        prereq = [f"L{i-1:03d}"] if i > 1 else []
        db.add(
            PlayLevel(
                id=lid,
                game_mode_id="math_blast:candy",
                skill_unit_id="l1_add_within_10",
                grade=1,
                chapter_id="W1_CH1",
                title=f"Màn {i}" if i % 6 != 0 else f"Boss {i}",
                star_ref="BOSS" if i % 6 == 0 else "G1",
                is_boss=(i % 6 == 0),
                prerequisite_level_ids=prereq,
                sort_index=i,
                objective="Hoàn thành 10 câu đúng",
            )
        )

    db.add(
        PlayGameRelease(
            id="math_blast@1.0.0",
            game_id="math_blast",
            version="1.0.0",
            released_at=now,
            changelog="MVP play API",
            is_active=True,
        )
    )
    db.commit()
    logger.info("Play catalog seeded.")


def ensure_chim_toan_mode(db: Session) -> None:
    """Thêm mode Chim Toán Vui nếu DB đã seed trước đó."""
    if db.query(PlayGameMode).filter(PlayGameMode.id == "math_blast:chim").first():
        return
    db.add(
        PlayGameMode(
            id="math_blast:chim",
            game_id="math_blast",
            mode_key="chim",
            display_name="Chim Toán Vui",
            tracks_learning=True,
            content_pack_id=CONTENT_PACK_ID,
            config_json={"prairie_grades": [1, 2], "blocks": ["T3", "T4", "T5"]},
        )
    )
    db.commit()
    logger.info("Added play mode math_blast:chim (Chim Toán Vui).")
