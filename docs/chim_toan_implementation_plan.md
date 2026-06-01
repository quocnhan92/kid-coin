# Chim Toán Vui — Kế hoạch triển khai

## 1. Tên thương hiệu (5–10 tuổi)

| Đề xuất | Lý do |
|---------|--------|
| **Chim Toán Vui** (chọn) | Dễ đọc, gợi chim/gà vui, không “súng đạn”, hợp Thảo nguyên |
| Gà Toán (đã có) | Giữ làm chế độ luyện nhảy; Chim Toán = chế độ bắn đáp án |
| Bắn Toán Siêu Vui | Rõ gameplay nhưng hơi “game” |

**API id:** `math_blast:chim` · **Route:** `/game/math-blast-v2/chim`

## 2. UI & an toàn nội dung

- Vũ khí: **súng cao su gỗ**, đạn **sỏi / nấm** (emoji + canvas), không máu.
- Mục tiêu: gà/chim cartoon; sai → chim kêu rồi bay đi.
- Màu pastel, font Nunito, nút to (44px+).
- Asset: procedural canvas + emoji, **không** lấy sprite game thương mại.

## 3. Logo

- SVG inline: chim con + dấu cộng nhỏ, gradient xanh–vàng (file trong template).

## 4. Khung cấp độ (Block)

| Block | Lớp | Trạng thái Phase 1 |
|-------|-----|-------------------|
| Thảo nguyên | 1–2 | ✅ MVP |
| Rừng sương | 3 | 🔒 Khung + “Sắp mở” |
| Ngoại ô | 4 | 🔒 |
| Thành phố | 5 | 🔒 |

Mở khóa T3: `prairie_best` Lớp 2 ≥ 30 hoặc tổng 50 câu đúng (server).

## 5. Phase triển khai

- **P0 (xong):** Chim Toán Vui, Thảo nguyên L1–L2, gold, resume grade, API `extra_json`.
- **P1:** Cung L2 visual, lá rụng; sticker chim.
- **P2:** Block L3 + timer 20s/câu.
- **P3:** Bảo vệ Thành phố L3–5.
- **P4:** Boss L1 Vua Gà.

## 6. API tiến trình (`extra_json`)

```json
{
  "gold": 0,
  "last_grade": 1,
  "last_play_mode": "prairie",
  "prairie_best_by_tier": { "T1": 0, "T2": 0 },
  "lifetime_correct": 0,
  "blocks": {
    "T3": { "unlocked": false, "label": "Rừng sương" },
    "T4": { "unlocked": false, "label": "Ngoại ô" },
    "T5": { "unlocked": false, "label": "Thành phố" }
  }
}
```

Bootstrap trả về → client khôi phục lớp, vàng, block đã mở.
