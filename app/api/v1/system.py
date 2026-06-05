from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from app.core.database import engine
from sqlalchemy import text
from sqlalchemy.orm import Session
import os
import uuid
from typing import Optional
from uuid import UUID

from app.api import deps
from app.core import context
from app.core.api_compat import API_VERSION, MIN_SUPPORTED_CLIENT
from app.locale.jinja import locale_from_request
from app.locale.registry import LOCALES, MARKETS
from app.models.user_family import User
from app.schemas.platform import FeaturesResponse, PublicGamesResponse
from app.services.feature_flag_service import is_enabled, list_effective_flags
from app.services.play_hub_catalog import ZONE_LEARNING, list_hub_games

router = APIRouter()


def _optional_user(request: Request, db: Session) -> Optional[User]:
    try:
        return deps.get_current_user(request, db)
    except HTTPException:
        return None


def _resolve_market(request: Request) -> Optional[str]:
    lc = locale_from_request(request)
    return lc.market if lc else context.get_market()


@router.get("/locale")
def get_locale_info(request: Request):
    """Current market/locale + catalog for market switcher UI."""
    lc = locale_from_request(request)
    return {
        "market": lc.market,
        "locale": lc.locale,
        "speech_lang": lc.speech_lang,
        "rtl": lc.is_rtl,
        "markets": [
            {
                "code": m.code,
                "label": m.label,
                "flag": m.flag,
                "default_locale": m.default_locale,
                "currency": m.currency,
            }
            for m in MARKETS.values()
        ],
        "locales": [
            {"tag": l.tag, "label": l.label, "native_label": l.native_label}
            for l in LOCALES.values()
        ],
    }


@router.get("/features", response_model=FeaturesResponse)
def get_features(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    user = _optional_user(request, db)
    family_id = user.family_id if user else None
    market = _resolve_market(request)
    flags = list_effective_flags(db, family_id=family_id, market=market)
    return FeaturesResponse(
        flags=flags,
        api_version=API_VERSION,
        min_client_version=MIN_SUPPORTED_CLIENT,
    )


@router.get("/public-games", response_model=PublicGamesResponse)
def get_public_games(
    request: Request,
    zone: str = ZONE_LEARNING,
    grade: Optional[int] = None,
    db: Session = Depends(deps.get_db),
):
    market = _resolve_market(request)
    if zone not in (ZONE_LEARNING, "reward"):
        zone = ZONE_LEARNING
    if grade is not None and not (1 <= grade <= 5):
        grade = None
    games = list_hub_games(db, zone=zone, grade=grade, market=market)
    return PublicGamesResponse(games=games)


@router.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

# --- Minimal Image Upload API for 1GB RAM Server ---
# We save directly to the filesystem instead of MinIO to save RAM.
UPLOAD_DIR = "app/static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Generate random filename
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_name = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Save file
        with open(file_path, "wb") as buffer:
            # Read in chunks to avoid memory overflow on 1GB RAM
            while chunk := await file.read(1024 * 1024): # 1MB chunks
                buffer.write(chunk)
                
        # Return URL (assuming static files are mounted at /static)
        return {"url": f"/static/uploads/{file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload: {str(e)}")
