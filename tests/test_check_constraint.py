"""
Integration tests for the CheckConstraint on task_logs table.

    CONSTRAINT chk_one_task_source CHECK (num_nonnulls(family_task_id, club_task_id) = 1)

These tests require a live PostgreSQL database with the schema already applied
(i.e., `alembic upgrade head` must have been run).

Set DATABASE_URL env var or rely on the default:
    postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db

Run with:
    pytest tests/test_check_constraint.py -v -m integration
"""
import uuid
import pytest
import sqlalchemy.exc
from sqlalchemy import text

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers — insert prerequisite rows directly via raw SQL to avoid ORM
# model-level validation and keep tests focused on the DB constraint.
# ---------------------------------------------------------------------------

def _insert_family(conn, family_id: uuid.UUID) -> None:
    conn.execute(
        text(
            "INSERT INTO families (id, name) VALUES (:id, :name)"
        ),
        {"id": str(family_id), "name": "Test Family"},
    )


def _insert_user(conn, user_id: uuid.UUID, family_id: uuid.UUID) -> None:
    conn.execute(
        text(
            "INSERT INTO users (id, family_id, role, display_name) "
            "VALUES (:id, :family_id, 'KID', 'Test Kid')"
        ),
        {"id": str(user_id), "family_id": str(family_id)},
    )


def _insert_family_task(conn, task_id: uuid.UUID, family_id: uuid.UUID) -> None:
    conn.execute(
        text(
            "INSERT INTO family_tasks (id, family_id, name, points_reward) "
            "VALUES (:id, :family_id, 'Test Task', 10)"
        ),
        {"id": str(task_id), "family_id": str(family_id)},
    )


def _insert_club(conn, club_id: uuid.UUID, family_id: uuid.UUID) -> None:
    conn.execute(
        text(
            "INSERT INTO clubs (id, name, creator_family_id, invite_code) "
            "VALUES (:id, 'Test Club', :family_id, :code)"
        ),
        {"id": str(club_id), "family_id": str(family_id), "code": str(club_id)[:20]},
    )


def _insert_club_task(conn, task_id: uuid.UUID, club_id: uuid.UUID, family_id: uuid.UUID) -> None:
    conn.execute(
        text(
            "INSERT INTO club_tasks (id, club_id, creator_family_id, name, points_reward) "
            "VALUES (:id, :club_id, :family_id, 'Club Task', 10)"
        ),
        {"id": str(task_id), "club_id": str(club_id), "family_id": str(family_id)},
    )


def _insert_task_log(conn, kid_id: uuid.UUID, family_task_id, club_task_id) -> None:
    """Insert a task_log row. family_task_id / club_task_id may be None or a UUID."""
    conn.execute(
        text(
            "INSERT INTO task_logs (id, kid_id, family_task_id, club_task_id) "
            "VALUES (:id, :kid_id, :ftid, :ctid)"
        ),
        {
            "id": str(uuid.uuid4()),
            "kid_id": str(kid_id),
            "ftid": str(family_task_id) if family_task_id else None,
            "ctid": str(club_task_id) if club_task_id else None,
        },
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def prereq(db_session):
    """
    Insert the minimum prerequisite rows needed to test task_log inserts:
      - one family
      - one kid user
      - one family_task
      - one club + one club_task
    Returns a dict with the relevant UUIDs.
    """
    family_id = uuid.uuid4()
    user_id = uuid.uuid4()
    family_task_id = uuid.uuid4()
    club_id = uuid.uuid4()
    club_task_id = uuid.uuid4()

    conn = db_session.connection()
    _insert_family(conn, family_id)
    _insert_user(conn, user_id, family_id)
    _insert_family_task(conn, family_task_id, family_id)
    _insert_club(conn, club_id, family_id)
    _insert_club_task(conn, club_task_id, club_id, family_id)
    db_session.flush()

    return {
        "family_id": family_id,
        "user_id": user_id,
        "family_task_id": family_task_id,
        "club_id": club_id,
        "club_task_id": club_task_id,
    }


# ---------------------------------------------------------------------------
# Tests — Validates: Requirements 2.4
# ---------------------------------------------------------------------------

def test_both_fk_null_is_rejected(db_session, prereq):
    """
    INSERT task_log with both family_task_id=NULL and club_task_id=NULL
    must be rejected by the DB (num_nonnulls = 0, not 1).
    """
    conn = db_session.connection()
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        _insert_task_log(conn, prereq["user_id"], None, None)
        db_session.flush()


def test_both_fk_set_is_rejected(db_session, prereq):
    """
    INSERT task_log with both family_task_id and club_task_id set
    must be rejected by the DB (num_nonnulls = 2, not 1).
    """
    conn = db_session.connection()
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        _insert_task_log(
            conn,
            prereq["user_id"],
            prereq["family_task_id"],
            prereq["club_task_id"],
        )
        db_session.flush()


def test_only_family_task_id_is_accepted(db_session, prereq):
    """
    INSERT task_log with only family_task_id set (club_task_id=NULL)
    must succeed (num_nonnulls = 1).
    """
    conn = db_session.connection()
    # Should not raise
    _insert_task_log(conn, prereq["user_id"], prereq["family_task_id"], None)
    db_session.flush()


def test_only_club_task_id_is_accepted(db_session, prereq):
    """
    INSERT task_log with only club_task_id set (family_task_id=NULL)
    must succeed (num_nonnulls = 1).
    """
    conn = db_session.connection()
    # Should not raise
    _insert_task_log(conn, prereq["user_id"], None, prereq["club_task_id"])
    db_session.flush()
