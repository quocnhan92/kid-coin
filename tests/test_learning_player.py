"""Guided player API — steps, schedule, checkpoints."""

import pytest
from uuid import uuid4

from app.models.learning import LearningLesson
from app.models.user_family import Family, Role, User
from app.services.learning_curriculum_seed import seed_learning_curriculum
from app.services import learning_player_service, learning_service
from app.data.learning_g1_guided_seed import GUIDED_LESSON_TITLE


@pytest.fixture
def learning_family(db_session):
    seed_learning_curriculum(db_session)
    family = Family(id=uuid4(), name="Test", parent_pin="1234")
    db_session.add(family)
    parent = User(
        id=uuid4(),
        family_id=family.id,
        role=Role.PARENT,
        display_name="Bố Test",
        username=f"parent_{uuid4().hex[:8]}",
    )
    kid = User(
        id=uuid4(),
        family_id=family.id,
        role=Role.KID,
        display_name="Bé Test",
        username=f"kid_{uuid4().hex[:8]}",
    )
    db_session.add(parent)
    db_session.add(kid)
    db_session.commit()
    return db_session, parent, kid


def _guided_lesson(db):
    return db.query(LearningLesson).filter(LearningLesson.title == GUIDED_LESSON_TITLE).first()


def test_schedule_today_has_slots(learning_family):
    db, _, kid = learning_family
    sched = learning_player_service.get_schedule_today(db, 1, kid)
    assert sched["daily_goal"]["target_lessons"] >= 1
    assert len(sched["slots"]) >= 1


def test_guided_player_flow(learning_family):
    db, parent, kid = learning_family
    lesson = _guided_lesson(db)
    assert lesson is not None
    assert lesson.content_type == "guided"

    player = learning_player_service.get_lesson_player(db, lesson.id, kid)
    assert len(player["steps"]) >= 4
    assert player["resume_at_step_index"] == 0

    steps = player["steps"]
    r1 = learning_player_service.submit_step(db, lesson.id, steps[0]["id"], kid, "observe", {})
    assert r1["feedback"]["type"] == "success"
    assert not r1["lesson_complete"]

    lr = next(s for s in steps if s["step_type"] == "listen_read")
    lr_cfg = lr["config"]
    r_lr = learning_player_service.submit_step(
        db, lesson.id, lr["id"], kid, "stt", {"transcript": lr_cfg["display_text"]}
    )
    assert r_lr["feedback"]["type"] == "success"

    choice_step = next(s for s in steps if s["step_type"] == "choice")
    r2 = learning_player_service.submit_step(
        db, lesson.id, choice_step["id"], kid, "choice", {"selected_index": 0}
    )
    assert r2["feedback"]["type"] == "success"

    quiz_step = next(s for s in steps if s["step_type"] == "quiz")
    r3 = learning_player_service.submit_step(
        db,
        lesson.id,
        quiz_step["id"],
        kid,
        "quiz",
        {"answers": [{"question_index": 0, "selected": quiz_step["config"]["questions"][0]["answer_index"]}]},
    )
    assert r3["feedback"]["type"] == "success"

    cp_step = next(s for s in steps if s["step_type"] == "family_checkpoint")
    r4 = learning_player_service.submit_step(db, lesson.id, cp_step["id"], kid, "checkpoint_request", {})
    assert r4["feedback"]["type"] == "waiting_parent"
    cp_id = r4["feedback"]["checkpoint_id"]

    confirmed = learning_player_service.confirm_checkpoint(db, cp_id, parent)
    assert confirmed["ok"] is True

    reward = next(s for s in steps if s["step_type"] == "reward")
    if not confirmed["lesson_complete"]:
        learning_player_service.submit_step(db, lesson.id, reward["id"], kid, "observe", {})


def test_levenshtein_keyword():
    assert learning_player_service.levenshtein_ratio("a", "a") == 100
    assert learning_player_service.levenshtein_ratio("", "abc") == 0


def test_parent_overview_includes_checkpoints(learning_family):
    db, parent, kid = learning_family
    overview = learning_service.parent_overview(db, parent)
    assert "pending_checkpoints" in overview
    assert isinstance(overview["pending_checkpoints"], list)


def test_teacher_lessons_list(learning_family):
    db, _, kid = learning_family
    data = learning_service.list_teacher_lessons(db, 1, kid)
    assert data["grade"] == 1
    assert data["total"] >= 20
    assert len(data["lessons"]) == data["total"]
    guided = [x for x in data["lessons"] if x["content_type"] == "guided"]
    assert len(guided) >= 4
    assert any(x["title"] == GUIDED_LESSON_TITLE for x in guided)


def test_teacher_lessons_grades_2_to_5(learning_family):
    db, _, kid = learning_family
    for grade in (2, 3, 4, 5):
        data = learning_service.list_teacher_lessons(db, grade, kid)
        assert data["grade"] == grade
        assert data["total"] >= 20, f"grade {grade} should list all curriculum lessons"
        assert len(data["lessons"]) == data["total"]
        guided = [x for x in data["lessons"] if x["content_type"] == "guided"]
        assert len(guided) >= 4


def test_quiz_lesson_still_works(learning_family):
    db, _, kid = learning_family
    ch_lesson = (
        db.query(LearningLesson)
        .filter(LearningLesson.content_type == "quiz", LearningLesson.is_published.is_(True))
        .first()
    )
    assert ch_lesson is not None
    qs = (ch_lesson.content_json or {}).get("questions", [])
    answers = [{"question_index": i, "selected": q["answer_index"]} for i, q in enumerate(qs)]
    res = learning_service.complete_lesson(db, ch_lesson.id, kid, 100, 120, answers)
    assert res["lesson"]["status"] == "completed"


def test_listen_read_step_eval(learning_family):
    db, _, kid = learning_family
    lesson = _guided_lesson(db)
    assert lesson is not None
    steps = learning_player_service.get_lesson_player(db, lesson.id, kid)["steps"]
    lr = next((s for s in steps if s["step_type"] == "listen_read"), None)
    assert lr is not None, "guided lesson should include listen_read step"
    cfg = lr["config"]
    assert len((cfg.get("display_text") or "").split()) >= 8
    ok, score, _, fb = learning_player_service._eval_step(
        type("S", (), {"step_type": "listen_read", "config_json": cfg})(),
        "stt",
        {"transcript": cfg["display_text"]},
    )
    assert ok is True
    assert fb == "success"

    from app.models.learning import LearningLesson

    reading = (
        db.query(LearningLesson)
        .filter(LearningLesson.title == "Luyện đọc — Giáo viên online", LearningLesson.content_type == "guided")
        .first()
    )
    assert reading is not None
    passage_lr = next(
        s for s in learning_player_service.get_lesson_player(db, reading.id, kid)["steps"]
        if s["step_type"] == "listen_read"
    )
    assert len(passage_lr["config"]["display_segments"]) == 3


def test_guided_lesson_replay_resumes_at_start(learning_family):
    db, parent, kid = learning_family
    lesson = _guided_lesson(db)
    assert lesson is not None

    steps = learning_player_service.get_lesson_player(db, lesson.id, kid)["steps"]
    for step in steps:
        if step["step_type"] == "family_checkpoint":
            learning_player_service.submit_step(db, lesson.id, step["id"], kid, "skip", {})
        elif step["step_type"] == "listen_read":
            txt = (step["config"].get("display_text") or "").strip()
            learning_player_service.submit_step(db, lesson.id, step["id"], kid, "stt", {"transcript": txt})
        elif step["step_type"] == "choice":
            learning_player_service.submit_step(
                db, lesson.id, step["id"], kid, "choice",
                {"selected_index": step["config"].get("answer_index", 0)},
            )
        elif step["step_type"] == "quiz":
            qs = step["config"].get("questions") or []
            payload = {
                "answers": [
                    {"question_index": i, "selected": q.get("answer_index", 0)}
                    for i, q in enumerate(qs)
                ]
            }
            learning_player_service.submit_step(db, lesson.id, step["id"], kid, "quiz", payload)
        elif step["step_type"] in ("observe", "reward"):
            learning_player_service.submit_step(db, lesson.id, step["id"], kid, "observe", {})

    replay = learning_player_service.get_lesson_player(db, lesson.id, kid)
    assert replay["lesson"]["is_replay"] is True
    assert replay["resume_at_step_index"] == 0

    r1 = learning_player_service.submit_step(db, lesson.id, steps[0]["id"], kid, "observe", {})
    assert r1["lesson_complete"] is False
    assert r1["next_step_index"] == 1
