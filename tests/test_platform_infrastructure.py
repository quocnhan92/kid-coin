"""
Platform service tests (H1, H2, H5) — SQLite subset.
"""
import os
import uuid

import pytest
from sqlalchemy.orm import Session

TEST_DB_FILE = "test_platform_svc.db"
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB_FILE}"
os.environ["PLAY_TEST_UNLOCK_ALL"] = "false"

from app.core.database import engine, SessionLocal
from app.models.platform import FeatureFlag, DomainEventOutbox
from app.models.user_family import User, Role, Family
from app.models.logs_transactions import Transaction, TransactionType
from app.services import coin_ledger_service as ledger
from app.services import domain_event_service as events
from app.services import feature_flag_service as flags
from app.services.platform_seed import CORE_FLAGS


def _create_platform_tables():
    for table in (
        Family.__table__,
        User.__table__,
        Transaction.__table__,
        FeatureFlag.__table__,
        DomainEventOutbox.__table__,
    ):
        table.create(engine, checkfirst=True)


def _seed_flags_only(db):
    for key, enabled, desc in CORE_FLAGS:
        flags.upsert_flag(db, key, enabled, description=desc)
    db.commit()


@pytest.fixture(scope="module", autouse=True)
def setup_platform_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    _create_platform_tables()
    db = SessionLocal()
    try:
        _seed_flags_only(db)
    finally:
        db.close()
    yield
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def family_with_kid(db_session: Session):
    fam = Family(id=uuid.uuid4(), name="Test Fam", parent_pin="1234")
    kid = User(
        id=uuid.uuid4(),
        family_id=fam.id,
        role=Role.KID,
        display_name="Kid A",
        current_coin=100,
    )
    db_session.add(fam)
    db_session.add(kid)
    db_session.commit()
    return fam, kid


class TestCoinLedger:
    def test_credit_writes_transaction(self, db_session, family_with_kid):
        _, kid = family_with_kid
        before = kid.current_coin
        result = ledger.credit(db_session, kid, 25, TransactionType.BONUS, "test")
        db_session.commit()
        assert result == before + 25
        tx = db_session.query(Transaction).filter(Transaction.kid_id == kid.id).first()
        assert tx.amount == 25

    def test_debit_insufficient_raises(self, db_session, family_with_kid):
        _, kid = family_with_kid
        kid.current_coin = 5
        db_session.commit()
        with pytest.raises(ledger.InsufficientCoinsError):
            ledger.debit(db_session, kid, 10, TransactionType.PENALTY, "x")

    def test_credit_invalid_amount(self, db_session, family_with_kid):
        _, kid = family_with_kid
        with pytest.raises(ValueError):
            ledger.credit(db_session, kid, 0, TransactionType.BONUS, "x")


class TestFeatureFlags:
    def test_unknown_key_default_true(self, db_session):
        assert flags.is_enabled(db_session, "core.auth") is True

    def test_play_test_unlock_follows_env(self, db_session):
        assert flags.is_enabled(db_session, "play.test_unlock_all") is False

    def test_global_disabled(self, db_session):
        flags.upsert_flag(db_session, "mod.ads", False)
        db_session.commit()
        assert flags.is_enabled(db_session, "mod.ads") is False

    def test_market_override_beats_global(self, db_session):
        key = "play.hub"
        flags.upsert_flag(db_session, key, True, scope="global")
        flags.upsert_flag(db_session, key, False, scope="market", scope_value="vn")
        db_session.commit()
        assert flags.is_enabled(db_session, key, market="vn") is False
        assert flags.is_enabled(db_session, key, market="my") is True

    def test_family_override_beats_market(self, db_session, family_with_kid):
        fam, _ = family_with_kid
        key = "mod.teen"
        flags.upsert_flag(db_session, key, True, scope="global")
        flags.upsert_flag(db_session, key, False, scope="market", scope_value="vn")
        flags.upsert_flag(
            db_session, key, True, scope="family", scope_value=str(fam.id)
        )
        db_session.commit()
        assert flags.is_enabled(db_session, key, family_id=fam.id, market="vn") is True

    def test_multiple_scopes_same_key_coexist(self, db_session):
        key = "mod.clubs"
        flags.upsert_flag(db_session, key, True, scope="global")
        flags.upsert_flag(db_session, key, False, scope="market", scope_value="vn")
        db_session.commit()
        count = db_session.query(FeatureFlag).filter(FeatureFlag.key == key).count()
        assert count == 2


class TestDomainEvents:
    def test_emit_pending(self, db_session, family_with_kid):
        fam, kid = family_with_kid
        row = events.emit(
            db_session,
            events.EVENT_TASK_APPROVED,
            {"kid_id": str(kid.id)},
            family_id=fam.id,
        )
        db_session.commit()
        assert row.status == "pending"

    def test_process_pending(self, db_session, family_with_kid):
        fam, _ = family_with_kid
        events.emit(db_session, events.EVENT_REWARD_REDEEMED, {"cost": 1}, family_id=fam.id)
        db_session.commit()
        n = events.process_pending(db_session)
        assert n >= 1
        row = db_session.query(DomainEventOutbox).first()
        assert row.status == "published"
