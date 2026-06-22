# QA Bản quyền nội dung học — checklist

Nội dung **gốc**, chỉ mượn **khung chủ đề** SGK. Không paste/paraphrase sát SGK.

## Trước mỗi batch merge

- [ ] Không chuỗi >8 từ liên tiếp trùng vietjack/SGK (diff thủ công 20% mẫu)
- [ ] Tên riêng generic (Minh, Linh, bé, mẹ…) — không nhân vật SGK
- [ ] Độ dài đúng tier lớp (G1: 3 câu; G2+: 4–5; Luyện tập: 3×3)
- [ ] Câu hỏi TV: đáp án đúng lấy từ `passage` (`question_grounded_in_passage`)
- [ ] G1 ≠ G2 cùng chủ đề (câu khác nhau)
- [ ] Chạy `alembic upgrade head` + `scripts/export_content_matrix.py`

## Sign-off

| Vai trò | Tên | Ngày |
|---------|-----|------|
| PO | | |
| Content reviewer | | |
| Dev | | |
