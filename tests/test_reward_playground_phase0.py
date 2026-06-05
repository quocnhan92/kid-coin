"""Reward Playground Phase 0 — rollout status, per-game flags, sections."""
import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

TEST_DB = "test_reward_phase0.db"
os.environ["PLAY_TEST_UNLOCK_ALL"] = "false"

from app.core import database
from app.data.reward_playground_catalog import reward_flag_key
from app.models.platform import FeatureFlag
from app.services.feature_flag_service import upsert_flag
from app.services import play_reward_service

test_engine = create_engine(f"sqlite:///./{TEST_DB}", connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _create_tables():
    FeatureFlag.__table__.create(test_engine, checkfirst=True)


def _seed_flags(db, *, test_unlock: bool = False, co_op: bool = False):
    upsert_flag(db, "play.reward_playground", True)
    upsert_flag(db, "play.test_unlock_all", test_unlock)
    upsert_flag(db, "play.reward.co_op_hub", co_op)
    upsert_flag(db, reward_flag_key("snake"), True)
    upsert_flag(db, reward_flag_key("hextris"), False)
    db.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    _create_tables()
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
        db.rollback()
        db.close()


class TestRewardPhase0:
    def test_prod_hides_draft_games(self, db_session):
        _seed_flags(db_session, test_unlock=False, co_op=False)
        payload = play_reward_service.build_reward_playground(db_session, None)
        ids = {g["id"] for g in payload["games"]}
        assert "snake" in ids
        assert "hextris" not in ids
        assert payload["total_count"] == 5

    def test_test_unlock_shows_draft_when_flag_on(self, db_session):
        _seed_flags(db_session, test_unlock=True, co_op=True)
        upsert_flag(db_session, reward_flag_key("hextris"), True)
        db_session.commit()
        payload = play_reward_service.build_reward_playground(
            db_session, None, include_draft=True
        )
        ids = {g["id"] for g in payload["games"]}
        assert "hextris" in ids
        assert payload["test_unlock_all"] is True
        assert all(g["unlocked"] for g in payload["games"])

    def test_sections_exclude_co_op_when_flag_off(self, db_session):
        _seed_flags(db_session, test_unlock=True, co_op=False)
        db_session.commit()
        payload = play_reward_service.build_reward_playground(db_session, None)
        keys = {s["key"] for s in payload["sections"]}
        assert "co_op" not in keys
        assert "reflex" in keys

    def test_genre_filter(self, db_session):
        _seed_flags(db_session, test_unlock=False, co_op=False)
        payload = play_reward_service.build_reward_playground(
            db_session, None, genre="puzzle"
        )
        assert payload["games"]
        assert all(g["genre"] == "puzzle" for g in payload["games"])

    def test_validate_draft_blocked_without_test(self, db_session):
        _seed_flags(db_session, test_unlock=False, co_op=False)
        uid = uuid.uuid4()
        ok, msg, status = play_reward_service.validate_reward_play(
            db_session, uid, "hextris"
        )
        assert not ok
        assert status == 400

    def test_game_item_has_rollout_fields(self, db_session):
        _seed_flags(db_session, test_unlock=False, co_op=False)
        payload = play_reward_service.build_reward_playground(db_session, None)
        snake = next(g for g in payload["games"] if g["id"] == "snake")
        assert snake["rollout_status"] == "live"
        assert snake["genre"] == "reflex"
        assert snake["session_cap_seconds"] == 600
