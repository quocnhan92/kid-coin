"""Phase 1–2: passage banks G1/G2."""

from app.data.learning_ket_noi_content import build_lesson_content
from app.data.passages import tv_g1, tv_g2


def test_g1_tv_passage_version_and_length():
    c = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
    assert c["_version"] == tv_g1.CONTENT_VERSION
    assert len(c["passage"]) >= 3


def test_g2_tv_passage_version_and_length():
    c = build_lesson_content(2, "tieng-viet", "G2-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
    assert c["_version"] == tv_g2.CONTENT_VERSION
    assert len(c["passage"]) >= 3


def test_g1_g2_same_topic_different_passages():
    g1 = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
    g2 = build_lesson_content(2, "tieng-viet", "G2-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
    assert g1["passage"] != g2["passage"]


def test_g1_luyen_tap_has_nine_sentences():
    c = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 3: Luyện tập", 2)
    assert len(c["passage"]) == 9
    assert c["passage_segments"] is not None
    assert len(c["passage_segments"]) == 3


def test_g1_bank_covers_all_chapters():
    from app.data.learning_ket_noi_curriculum import _tv_chapters

    keys = {ch[0].split(":")[-1].strip().lower() for ch in _tv_chapters(1)}
    assert keys <= set(tv_g1.BANK.keys())


def test_g2_bank_covers_all_chapters():
    from app.data.learning_ket_noi_curriculum import _tv_chapters

    keys = {ch[0].split(":")[-1].strip().lower() for ch in _tv_chapters(2)}
    assert keys <= set(tv_g2.BANK.keys())


def test_tv_questions_grounded_in_passage():
    from app.data.learning_passage_questions import question_grounded_in_passage

    c = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
    passage = c["passage"]
    qs = c["questions"]
    assert len(qs) == 3
    assert all(question_grounded_in_passage(q, passage) for q in qs)
    assert "liên quan thế nào" not in qs[0]["prompt"].lower()


def test_tv_questions_unique_per_lesson():
    from app.data.learning_ket_noi_content import begin_global_allocation, end_global_allocation

    begin_global_allocation()
    try:
        a = build_lesson_content(1, "tieng-viet", "G1-TV-CD1", "Chủ đề 1: Em đến trường", "Bài 1: Tuần 1: Đọc", 0)
        b = build_lesson_content(1, "tieng-viet", "G1-TV-CD2", "Chủ đề 2: Gia đình thân yêu", "Bài 1: Tuần 3: Đọc", 0)
    finally:
        end_global_allocation()
    prompts = {q["prompt"] for q in a["questions"] + b["questions"]}
    assert len(prompts) == 6
