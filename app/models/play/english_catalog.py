"""English Shooter — nội dung catalog (GDD §8)."""
import sqlalchemy as sa
from sqlalchemy import Column, String, SmallInteger, Integer, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base


class PlayEnglishWeapon(Base):
    __tablename__ = "play_english_weapons"

    id = Column(String(32), primary_key=True)
    grade = Column(SmallInteger, nullable=False)
    name = Column(String(80), nullable=False)
    asset_id = Column(String(64), nullable=True)
    meta_json = Column(JSONB, server_default="{}", nullable=False)


class PlayEnglishBoss(Base):
    __tablename__ = "play_english_bosses"

    id = Column(String(32), primary_key=True)
    grade = Column(SmallInteger, nullable=False)
    name = Column(String(100), nullable=False)
    asset_id = Column(String(64), nullable=True)
    intro_audio = Column(String(256), nullable=True)
    meta_json = Column(JSONB, server_default="{}", nullable=False)


class PlayEnglishTheme(Base):
    __tablename__ = "play_english_themes"

    id = Column(String(32), primary_key=True)
    grade = Column(SmallInteger, nullable=False)
    title = Column(String(120), nullable=False)
    order_index = Column(SmallInteger, server_default="0", nullable=False)
    background_scene = Column(String(48), nullable=True)
    boss_id = Column(String(32), ForeignKey("play_english_bosses.id"), nullable=True)
    content_pack_id = Column(String(64), nullable=True)
    is_active = Column(Boolean, server_default="true", nullable=False)
    meta_json = Column(JSONB, server_default="{}", nullable=False)


class PlayEnglishStage(Base):
    __tablename__ = "play_english_stages"

    id = Column(String(48), primary_key=True)
    theme_id = Column(String(32), ForeignKey("play_english_themes.id"), nullable=False)
    stage_type = Column(String(16), nullable=False)
    instruction_audio = Column(String(256), nullable=True)
    time_limit_seconds = Column(Integer, nullable=True)
    speaking_required = Column(Boolean, server_default="false", nullable=False)
    min_confidence = Column(Numeric(4, 2), nullable=True)
    config_json = Column(JSONB, server_default="{}", nullable=False)


class PlayEnglishStageItem(Base):
    __tablename__ = "play_english_stage_items"

    id = Column(String(48), primary_key=True)
    stage_id = Column(String(48), ForeignKey("play_english_stages.id"), nullable=False)
    item_type = Column(String(16), server_default="target", nullable=False)
    target_text = Column(Text, nullable=False)
    audio_url = Column(String(256), nullable=True)
    visual_asset = Column(String(64), nullable=True)
    translation_vi = Column(String(200), nullable=True)
    options_json = Column(JSONB, server_default="{}", nullable=False)
    order_index = Column(SmallInteger, server_default="0", nullable=False)
    skill_unit_id = Column(String(64), nullable=True)
