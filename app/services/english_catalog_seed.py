"""Seed English Shooter game + catalog (idempotent)."""
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.play import PlayGame, PlayGameMode, PlayGameRelease
from app.models.play.english_catalog import (
    PlayEnglishWeapon,
    PlayEnglishBoss,
    PlayEnglishTheme,
    PlayEnglishStage,
    PlayEnglishStageItem,
)

logger = logging.getLogger(__name__)

CONTENT_PACK_EN = "vn_english_shooter_v1"
GAME_ID = "english_shooter"


def ensure_english_shooter_catalog(db: Session) -> None:
    """Thêm game/mode/catalog nếu DB đã seed math_blast trước đó."""
    if not db.query(PlayGame).filter(PlayGame.id == GAME_ID).first():
        db.add(
            PlayGame(
                id=GAME_ID,
                display_name="English Shooter",
                game_type="learning",
                is_active=True,
                current_release_id=f"{GAME_ID}@1.0.0",
                sort_order=2,
                meta_json={
                    "icon": "🎯",
                    "route": "/game/english-shooter",
                    "subject": "english",
                    "tagline": "Xạ thủ Tiếng Anh",
                },
            )
        )
        db.add(
            PlayGameRelease(
                id=f"{GAME_ID}@1.0.0",
                game_id=GAME_ID,
                version="1.0.0",
                released_at=datetime.now(timezone.utc),
                changelog="English Shooter MVP — Thảo nguyên",
                is_active=True,
            )
        )

    modes = [
        ("prairie", "Thảo nguyên", True, {"play_mode": "vocab", "no_game_over": True}),
        ("city", "Bảo vệ thành phố", True, {"play_mode": "sentence", "hp": 3}),
        ("boss", "Đại Boss", True, {"play_mode": "paragraph", "boss_fight": True}),
    ]
    for key, label, tracks, cfg in modes:
        mid = f"{GAME_ID}:{key}"
        if not db.query(PlayGameMode).filter(PlayGameMode.id == mid).first():
            db.add(
                PlayGameMode(
                    id=mid,
                    game_id=GAME_ID,
                    mode_key=key,
                    display_name=label,
                    tracks_learning=True,
                    content_pack_id=CONTENT_PACK_EN,
                    config_json=cfg,
                )
            )

    if db.query(PlayEnglishTheme).first():
        db.commit()
        return

    logger.info("Seeding English Shooter catalog...")
    weapons = [
        ("slingshot", 1, "Súng cao su gỗ", "weapon_slingshot"),
        ("bow", 2, "Cung tên gỗ", "weapon_bow"),
        ("crossbow", 3, "Nỏ liên thanh", "weapon_crossbow"),
        ("rifle", 4, "Súng trường", "weapon_rifle"),
        ("sniper", 5, "Súng bắn tỉa", "weapon_sniper"),
    ]
    for wid, grade, name, asset in weapons:
        db.add(PlayEnglishWeapon(id=wid, grade=grade, name=name, asset_id=asset, meta_json={}))

    bosses = [
        ("boss_g1_chicken", 1, "King Chicken", "boss_chicken"),
        ("boss_g2_phoenix", 2, "Fire Phoenix", "boss_phoenix"),
        ("boss_g3_zeppelin", 3, "Zeppelin Fortress", "boss_zeppelin"),
        ("boss_g4_spider", 4, "Grammar Mecha-Spider", "boss_spider"),
        ("boss_g5_mothership", 5, "Cyber-Mothership", "boss_mothership"),
    ]
    for bid, grade, name, asset in bosses:
        db.add(
            PlayEnglishBoss(
                id=bid,
                grade=grade,
                name=name,
                asset_id=asset,
                meta_json={"intro_line": f"I am {name}!"},
            )
        )

    db.flush()
    _seed_theme_grade1_family(db)
    db.commit()
    logger.info("English Shooter catalog seeded.")


def _seed_theme_grade1_family(db: Session) -> None:
    theme_id = "en_g1_family"
    db.add(
        PlayEnglishTheme(
            id=theme_id,
            grade=1,
            title="My Family",
            order_index=1,
            background_scene="savannah",
            boss_id="boss_g1_chicken",
            content_pack_id=CONTENT_PACK_EN,
            is_active=True,
            meta_json={"vi_title": "Gia đình của em"},
        )
    )
    stage_vocab = f"{theme_id}_vocab"
    stage_sent = f"{theme_id}_sentence"
    stage_para = f"{theme_id}_paragraph"
    for sid, stype, limit, speak, conf in [
        (stage_vocab, "vocab", None, False, None),
        (stage_sent, "sentence", 30, True, 0.50),
        (stage_para, "paragraph", None, True, 0.50),
    ]:
        db.add(
            PlayEnglishStage(
                id=sid,
                theme_id=theme_id,
                stage_type=stype,
                time_limit_seconds=limit,
                speaking_required=speak,
                min_confidence=conf,
                config_json={"boss_fight": stype == "paragraph"},
            )
        )

    vocab = [
        ("mom", "Mẹ", "👩", "en_vocab_mom"),
        ("dad", "Bố", "👨", "en_vocab_dad"),
        ("baby", "Em bé", "👶", "en_vocab_baby"),
        ("sister", "Chị/em gái", "👧", "en_vocab_sister"),
        ("brother", "Anh/em trai", "👦", "en_vocab_brother"),
        ("family", "Gia đình", "👨‍👩‍👧", "en_vocab_family"),
    ]
    distractors = ["cat", "dog", "apple", "ball"]
    for i, (word, vi, emoji, asset) in enumerate(vocab):
        db.add(
            PlayEnglishStageItem(
                id=f"{stage_vocab}_{word}",
                stage_id=stage_vocab,
                item_type="target",
                target_text=word,
                visual_asset=asset,
                translation_vi=vi,
                options_json={
                    "emoji": emoji,
                    "prompt_en": f"Shoot the {word}!",
                    "distractors": [d for d in distractors if d != word][:3],
                },
                order_index=i,
                skill_unit_id=f"en_g1_vocab_{word}",
            )
        )

    db.add(
        PlayEnglishStageItem(
            id=f"{stage_sent}_q1",
            stage_id=stage_sent,
            item_type="target",
            target_text="This is my mom.",
            translation_vi="Đây là mẹ của tôi.",
            options_json={
                "prompt": "This is my [____].",
                "choices": ["mom", "dad", "cat"],
                "answer": "mom",
            },
            order_index=0,
            skill_unit_id="en_g1_sent_family",
        )
    )
