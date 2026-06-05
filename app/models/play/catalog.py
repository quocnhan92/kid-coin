import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, DateTime, SmallInteger, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from app.core.database import Base


class PlayGame(Base):
    __tablename__ = "play_games"

    id = Column(String(32), primary_key=True)
    display_name = Column(String(100), nullable=False)
    game_type = Column(String(16), nullable=False)  # learning | arcade
    is_active = Column(Boolean, server_default="true", nullable=False)
    current_release_id = Column(String(64), nullable=True)
    sort_order = Column(SmallInteger, server_default="0", nullable=False)
    meta_json = Column(JSONB, server_default="{}", nullable=False)
    ssr_template = Column(String(255), nullable=True)
    launch_url = Column(String(255), nullable=True)
    is_public = Column(Boolean, server_default="true", nullable=False)
    min_client_version = Column(String(16), server_default="1.0.0", nullable=False)
    hub_zone = Column(String(16), server_default="learning", nullable=False)
    requires_wallet = Column(Boolean, server_default="false", nullable=False)
    subject = Column(String(16), nullable=True)
    grade_min = Column(SmallInteger, server_default="1", nullable=False)
    grade_max = Column(SmallInteger, server_default="5", nullable=False)


class PlayGameMode(Base):
    __tablename__ = "play_game_modes"

    id = Column(String(32), primary_key=True)
    game_id = Column(String(32), ForeignKey("play_games.id"), nullable=False, index=True)
    mode_key = Column(String(32), nullable=False)
    display_name = Column(String(100), nullable=False)
    tracks_learning = Column(Boolean, server_default="false", nullable=False)
    content_pack_id = Column(String(64), nullable=True)
    config_json = Column(JSONB, server_default="{}", nullable=False)


class PlayContentPack(Base):
    __tablename__ = "play_content_packs"

    id = Column(String(64), primary_key=True)
    locale = Column(String(8), server_default="vi-VN", nullable=False)
    grade_min = Column(SmallInteger, nullable=False)
    grade_max = Column(SmallInteger, nullable=False)
    manifest_version = Column(String(16), nullable=False)
    manifest_hash = Column(String(64), nullable=False)
    published_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class PlaySkillUnit(Base):
    __tablename__ = "play_skill_units"

    id = Column(String(64), primary_key=True)
    content_pack_id = Column(String(64), ForeignKey("play_content_packs.id"), nullable=False, index=True)
    grade = Column(SmallInteger, nullable=False)
    title = Column(String(200), nullable=False)
    tags_json = Column(JSONB, server_default="[]", nullable=False)
    description = Column(Text, nullable=True)


class PlaySkillEdge(Base):
    __tablename__ = "play_skill_edges"

    from_skill_id = Column(String(64), ForeignKey("play_skill_units.id"), primary_key=True)
    to_skill_id = Column(String(64), ForeignKey("play_skill_units.id"), primary_key=True)
    edge_type = Column(String(8), nullable=False)  # hard | soft


class PlayLevel(Base):
    __tablename__ = "play_levels"

    id = Column(String(16), primary_key=True)
    game_mode_id = Column(String(32), ForeignKey("play_game_modes.id"), nullable=False, index=True)
    skill_unit_id = Column(String(64), ForeignKey("play_skill_units.id"), nullable=True)
    grade = Column(SmallInteger, nullable=True)
    chapter_id = Column(String(16), nullable=True)
    title = Column(String(200), nullable=False)
    star_ref = Column(String(8), nullable=True)
    is_boss = Column(Boolean, server_default="false", nullable=False)
    prerequisite_level_ids = Column(JSONB, server_default="[]", nullable=False)
    sort_index = Column(Integer, nullable=False, default=0)
    objective = Column(String(500), nullable=True)


class PlayGameRelease(Base):
    __tablename__ = "play_game_releases"

    id = Column(String(64), primary_key=True)
    game_id = Column(String(32), ForeignKey("play_games.id"), nullable=False, index=True)
    version = Column(String(32), nullable=False)
    released_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    changelog = Column(Text, nullable=True)
    is_active = Column(Boolean, server_default="true", nullable=False)
