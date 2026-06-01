"""English Shooter — catalog read API (themes, stages)."""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user_family import User
from app.services.english_shooter_service import (
    list_themes_for_grade,
    get_theme_stage_bundle,
)

router = APIRouter(prefix="/english", tags=["Play English"])


class EnglishThemeOut(BaseModel):
    id: str
    title: str
    grade: int
    order_index: int
    background_scene: Optional[str] = None
    boss_name: Optional[str] = None
    meta: Dict[str, Any] = {}


class EnglishThemesResponse(BaseModel):
    grade: int
    themes: List[EnglishThemeOut]


class EnglishStageResponse(BaseModel):
    theme_id: str
    stage_type: str
    stage: Dict[str, Any]


@router.get("/themes", response_model=EnglishThemesResponse)
def english_themes(
    grade: int = 1,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return EnglishThemesResponse(grade=grade, themes=list_themes_for_grade(db, grade))


@router.get("/themes/{theme_id}/stages/{stage_type}", response_model=EnglishStageResponse)
def english_theme_stage(
    theme_id: str,
    stage_type: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    bundle = get_theme_stage_bundle(db, theme_id, stage_type)
    if not bundle:
        raise HTTPException(status_code=404, detail="Stage not found")
    return EnglishStageResponse(theme_id=theme_id, stage_type=stage_type, stage=bundle)
