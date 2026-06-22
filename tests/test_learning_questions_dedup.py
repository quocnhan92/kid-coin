"""Đảm bảo mỗi prompt quiz chỉ xuất hiện 1 lần toàn hệ thống."""

from app.data.learning_ket_noi_curriculum import refresh_all_lesson_content
from app.data.learning_question_allocator import audit_duplicates
from app.models.learning import LearningLesson
from app.services.learning_curriculum_seed import seed_learning_curriculum


def test_no_duplicate_prompts_after_seed(db_session):
    seed_learning_curriculum(db_session)
    contents = [les.content_json or {} for les in db_session.query(LearningLesson).all()]
    dups = audit_duplicates(contents)
    assert dups == [], f"Found {len(dups)} duplicate prompts: {dups[:5]}"


def test_no_duplicate_prompts_after_refresh(db_session):
    seed_learning_curriculum(db_session)
    refresh_all_lesson_content(db_session)
    contents = [les.content_json or {} for les in db_session.query(LearningLesson).all()]
    dups = audit_duplicates(contents)
    assert dups == []
    total_q = sum(len(c.get("questions", [])) for c in contents)
    assert total_q >= 2700


def test_tieng_viet_read_lessons_have_passage(db_session):
    from app.data.learning_ket_noi_content import build_lesson_content
    from app.data.passages import tv_g1, tv_g2

    seed_learning_curriculum(db_session)
    refresh_all_lesson_content(db_session)
    for grade, ver in ((1, tv_g1.CONTENT_VERSION), (2, tv_g2.CONTENT_VERSION)):
        content = build_lesson_content(
            grade, "tieng-viet", f"G{grade}-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0
        )
        assert len(content.get("passage") or []) >= 3
        assert content.get("_version") == ver
