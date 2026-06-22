# Content Audit — Phase 0 Inventory

## Mục tiêu
Ma trận trạng thái nội dung G1–G5, chuẩn QA bản quyền, `content_version` trước khi scale Phase 1+.

## Quy ước version
| Môn / Lớp | `_version` |
|-----------|------------|
| TV G1 | `tv-g1-v2` |
| TV G2 | `tv-g2-v2` |
| TV G3–G5 | `tv-shared-v0` (Phase 3) |
| Toán | `math-g{n}-v0` (Phase 4–5) |

## Chuẩn độ dài (TV)
- **T1** G1 Đọc ch.1: 3 câu, ≤12 từ/câu
- **T2** G2+ Đọc: 4–5 câu
- **Luyện tập**: 3 đoạn × 3 câu (`passage_segments`)

## Ma trận phase (tóm tắt)

| Lớp | Môn | Chương×Bài | Phase | Trạng thái hiện tại |
|-----|-----|------------|-------|---------------------|
| G1 | Tiếng Việt | 11×3=33 | **1** | Bank G1 v1 |
| G2 | Tiếng Việt | 33 | **2** | Bank G2 v1 |
| G1–G2 | Toán | 10×3=30 | 4 | quiz_only |
| G1–G3 | Đạo đức, TN&XH | 6×3 | 6 | quiz_ok |
| G4–G5 | LSDL, KH | 6×3 | 7 | quiz_ok |
| G3–G5 | TV + môn phụ | — | 3,8 | planned/shared |

**Tổng slot Việc nhà:** ~900+ (7–10 môn × 5 lớp).

## Chạy inventory
```bash
python3 -c "
from app.db.session import SessionLocal
from app.data.learning_content_audit import audit_content_matrix
import json
db = SessionLocal()
print(json.dumps(audit_content_matrix(db)['summary'], indent=2))
"
```

## QA bản quyền (mỗi batch)
- [ ] Không >8 từ liên tiếp trùng SGK/vietjack
- [ ] Nhân vật/địa danh generic hoặc hư cấu
- [ ] Độ dài đúng tier lớp
- [x] Câu hỏi trả lời được từ passage (TV G1/G2 v2)
- [x] G1 ≠ G2 cùng chủ đề (diff câu)

## File liên quan
- `app/data/passages/tv_g1.py`, `tv_g2.py`
- `app/data/learning_reading_passages.py`
- `app/data/learning_content_audit.py`
- Migration `026_tv_g1_g2_passages.py`
