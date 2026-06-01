"""English Shooter — đọc catalog & bootstrap payload."""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.play.english_catalog import (
    PlayEnglishTheme,
    PlayEnglishStage,
    PlayEnglishStageItem,
    PlayEnglishBoss,
    PlayEnglishWeapon,
)
from app.services.english_shooter_progress_service import merge_extra, GAME_ID, MODE_PRAIRIE


def list_themes_for_grade(db: Session, grade: int) -> List[Dict[str, Any]]:
    rows = (
        db.query(PlayEnglishTheme)
        .filter(PlayEnglishTheme.grade == grade, PlayEnglishTheme.is_active.is_(True))
        .order_by(PlayEnglishTheme.order_index)
        .all()
    )
    out = []
    for t in rows:
        boss = db.query(PlayEnglishBoss).filter(PlayEnglishBoss.id == t.boss_id).first() if t.boss_id else None
        out.append(
            {
                "id": t.id,
                "title": t.title,
                "grade": t.grade,
                "order_index": t.order_index,
                "background_scene": t.background_scene,
                "boss_name": boss.name if boss else None,
                "meta": t.meta_json or {},
            }
        )
    return out


def get_theme_stage_bundle(db: Session, theme_id: str, stage_type: str) -> Optional[Dict[str, Any]]:
    stage = (
        db.query(PlayEnglishStage)
        .filter(PlayEnglishStage.theme_id == theme_id, PlayEnglishStage.stage_type == stage_type)
        .first()
    )
    if not stage:
        return None
    items = (
        db.query(PlayEnglishStageItem)
        .filter(PlayEnglishStageItem.stage_id == stage.id)
        .order_by(PlayEnglishStageItem.order_index)
        .all()
    )
    return {
        "stage_id": stage.id,
        "stage_type": stage.stage_type,
        "time_limit_seconds": stage.time_limit_seconds,
        "speaking_required": stage.speaking_required,
        "min_confidence": float(stage.min_confidence) if stage.min_confidence is not None else None,
        "config": stage.config_json or {},
        "items": [
            {
                "id": it.id,
                "item_type": it.item_type,
                "target_text": it.target_text,
                "audio_url": it.audio_url,
                "visual_asset": it.visual_asset,
                "translation_vi": it.translation_vi,
                "options": it.options_json or {},
            }
            for it in items
        ],
    }


def build_english_bootstrap(db: Session, stats_extra: Optional[Dict[str, Any]], grade: int = 1) -> Dict[str, Any]:
    extra = merge_extra(stats_extra)
    weapon = db.query(PlayEnglishWeapon).filter(PlayEnglishWeapon.grade == grade).first()
    themes = list_themes_for_grade(db, grade)
    return {
        "game_id": GAME_ID,
        "gold": extra.get("gold", 0),
        "last_grade": extra.get("last_grade", grade),
        "rank": extra.get("rank", "recruit"),
        "lifetime_correct": extra.get("lifetime_correct", 0),
        "voice_skins": extra.get("voice_skins", {}),
        "blocks": extra.get("blocks", {}),
        "themes_completed": extra.get("themes_completed", []),
        "prairie_best_by_theme": extra.get("prairie_best_by_theme", {}),
        "weapon": {
            "name": weapon.name if weapon else "Súng cao su",
            "asset_id": weapon.asset_id if weapon else "weapon_slingshot",
        }
        if weapon
        else None,
        "themes": themes,
        "default_mode_id": MODE_PRAIRIE,
    }
