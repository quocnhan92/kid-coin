"""Play hub taxonomy — learning vs reward zones (service-level)."""
import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

TEST_DB = "test_hub_taxonomy_svc.db"
os.environ["PLAY_TEST_UNLOCK_ALL"] = "false"

from app.core import database
from app.models.platform import FeatureFlag
from app.models.play import PlayGame
from app.services.feature_flag_service import upsert_flag
from app.services.play_hub_catalog import list_hub_games
from app.core.reward_route_guard import reward_route_guard

test_engine = create_engine(f"sqlite:///./{TEST_DB}", connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _create_tables():
    FeatureFlag.__table__.create(test_engine, checkfirst=True)
    with test_engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS play_games (
                    id VARCHAR(32) PRIMARY KEY,
                    display_name VARCHAR(100) NOT NULL,
                    game_type VARCHAR(16) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    current_release_id VARCHAR(64),
                    sort_order INTEGER DEFAULT 0,
                    meta_json TEXT DEFAULT '{}',
                    ssr_template VARCHAR(255),
                    launch_url VARCHAR(255),
                    is_public BOOLEAN DEFAULT 1,
                    min_client_version VARCHAR(16) DEFAULT '1.0.0',
                    hub_zone VARCHAR(16) DEFAULT 'learning',
                    requires_wallet BOOLEAN DEFAULT 0,
                    subject VARCHAR(16),
                    grade_min INTEGER DEFAULT 1,
                    grade_max INTEGER DEFAULT 5
                )
                """
            )
        )


def _seed_games(db):
    games = [
        PlayGame(
            id="math_blast",
            display_name="Math Blast",
            game_type="learning",
            hub_zone="learning",
            is_public=True,
            subject="math",
            sort_order=1,
            launch_url="/game/math-blast-v2",
            meta_json={"icon": "🚀"},
        ),
        PlayGame(
            id="english_shooter",
            display_name="English Shooter",
            game_type="learning",
            hub_zone="learning",
            is_public=True,
            subject="english",
            sort_order=2,
            launch_url="/game/english-shooter",
        ),
        PlayGame(
            id="snake",
            display_name="Snake",
            game_type="arcade",
            hub_zone="reward",
            is_public=False,
            requires_wallet=True,
            sort_order=20,
            launch_url="/game/snake",
        ),
        PlayGame(
            id="memory",
            display_name="Lật bài học",
            game_type="learning",
            hub_zone="learning",
            is_public=True,
            subject="memory",
            sort_order=3,
            launch_url="/game/memory",
        ),
    ]
    db.add_all(games)
    upsert_flag(db, "play.hub", True)
    upsert_flag(db, "play.reward_playground", True)
    db.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    _create_tables()
    db = TestSession()
    try:
        _seed_games(db)
    finally:
        db.close()
    database.SessionLocal = TestSession
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def db_session():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


class TestListHubGames:
    def test_learning_excludes_arcade(self, db_session):
        games = list_hub_games(db_session, zone="learning")
        ids = {g.id for g in games}
        assert "math_blast" in ids
        assert "snake" not in ids
        assert "reward_playground" not in ids

    def test_learning_has_metadata(self, db_session):
        games = list_hub_games(db_session, zone="learning")
        mb = next(g for g in games if g.id == "math_blast")
        assert mb.hub_zone == "learning"
        assert mb.subject == "math"

    def test_grade_filter(self, db_session):
        games = list_hub_games(db_session, zone="learning", grade=1)
        assert len(games) >= 1


class TestRewardRouteGuard:
    def test_snake_redirects(self, db_session):
        scope = {"type": "http", "method": "GET", "path": "/game/snake", "headers": []}
        resp = reward_route_guard(Request(scope))
        assert resp is not None
        assert resp.status_code == 302
        assert "/game/rewards" in resp.headers.get("location", "")

    def test_memory_not_blocked(self, db_session):
        scope = {"type": "http", "method": "GET", "path": "/game/memory-learn", "headers": []}
        assert reward_route_guard(Request(scope)) is None
