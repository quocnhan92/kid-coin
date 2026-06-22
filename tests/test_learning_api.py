"""Learning path API tests."""

import pytest
from uuid import uuid4

from app.models.learning import LearningChapter, LearningLesson, LearningSubject
from app.models.user_family import Family, Role, User
from app.services.learning_curriculum_seed import seed_learning_curriculum
from app.services import learning_service


@pytest.fixture
def learning_db(db_session):
    seed_learning_curriculum(db_session)
    family = Family(id=uuid4(), name="Test", parent_pin="1234")
    db_session.add(family)
    kid = User(
        id=uuid4(),
        family_id=family.id,
        role=Role.KID,
        display_name="Bé Test",
        username=f"kid_{uuid4().hex[:8]}",
    )
    db_session.add(kid)
    db_session.commit()
    return db_session, kid


def test_list_grades():
    grades = learning_service.list_grades()
    assert len(grades) == 5
    assert grades[0]["grade"] == 1


def test_subjects_and_map(learning_db):
    db, kid = learning_db
    subs = learning_service.list_subjects(db, 1, kid)
    assert len(subs["subjects"]) >= 7
    toan = next(s for s in subs["subjects"] if s["id"] == "toan-g1")
    assert toan["name"] == "Toán"
    m = learning_service.get_subject_map(db, "toan-g1", kid)
    assert len(m["chapters"]) == 10
    assert m["overall"]["total"] == 10


def test_complete_lesson_flow(learning_db):
    db, kid = learning_db
    ch = db.query(LearningChapter).filter(LearningChapter.subject_id == "toan-g1").first()
    les = (
        db.query(LearningLesson)
        .filter(LearningLesson.chapter_id == ch.id, LearningLesson.is_published.is_(True))
        .first()
    )
    qs = (les.content_json or {}).get("questions", [])
    answers = [{"question_index": i, "selected": q["answer_index"]} for i, q in enumerate(qs)]
    res = learning_service.complete_lesson(db, les.id, kid, 100, 300, answers)
    assert res["lesson"]["status"] == "completed"
    assert res["daily"]["minutes_studied"] >= 1


def test_complete_lesson_replay_no_extra_score(learning_db):
    db, kid = learning_db
    ch = db.query(LearningChapter).filter(LearningChapter.subject_id == "toan-g1").first()
    les = (
        db.query(LearningLesson)
        .filter(LearningLesson.chapter_id == ch.id, LearningLesson.is_published.is_(True))
        .first()
    )
    qs = (les.content_json or {}).get("questions", [])
    answers = [{"question_index": i, "selected": q["answer_index"]} for i, q in enumerate(qs)]
    first = learning_service.complete_lesson(db, les.id, kid, 100, 300, answers)
    assert first["lesson"]["status"] == "completed"
    assert not first.get("replay")
    stars_first = first["lesson"]["stars"]
    daily_first = first["daily"]["lessons_completed"]

    second = learning_service.complete_lesson(db, les.id, kid, 100, 200, answers)
    assert second.get("replay") is True
    assert second["lesson"]["stars"] == stars_first
    assert second["daily"]["lessons_completed"] == daily_first
