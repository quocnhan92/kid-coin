# 🐍 Snake Quest — Kế Hoạch Build Demo

## Tổng quan

Xây dựng game **Snake Quest** — phiên bản hoàn toàn mới của rắn săn mồi tích hợp vào Game Hub của KidCoin. Người chơi **đặt ô đường (tile placement)** để dẫn hướng con rắn tự chạy đến đáp án đúng của câu hỏi toán học. Kết hợp puzzle + hành động + học tập — thú vị hơn hẳn phiên bản rắn bình thường.

---

## Proposed Changes

### Frontend — Game Engine (Pure HTML/JS/CSS)

#### [NEW] `snake_quest.html` → `app/templates/games/snake_quest.html`

Toàn bộ logic game nằm trong 1 file HTML self-contained (~1000 dòng). Không dùng framework nào.

**Cấu trúc màn hình:**
```
┌────────────────────────────────────────────────────┐
│  HEADER: Score | Lives ❤️❤️❤️ | Level | Timer     │
├─────────────────────┬──────────────────────────────┤
│                     │  ❓ Câu hỏi: 3 × 7 = ?       │
│   GAME BOARD        │  🃏 Hand: [Tile] [Tile] [Tile]│
│   (12×12 grid)      │  ⚡ Power-ups                 │
│   Canvas-based      │  📊 Combo meter               │
│                     │  🐍 Speed indicator           │
└─────────────────────┴──────────────────────────────┘
```

**Các thành phần chính:**

##### 🗺️ Tile System (Cơ chế đặt ô đường)
- **6 loại tile:** Thẳng ngang (━), thẳng dọc (┃), cong ┘┐┘└, ngã tư (+), ngã ba (T-shape)
- Mỗi tile biết hướng rắn vào và hướng rắn ra
- Người chơi có **4 tile trong hand** (được random mỗi level)
- **Drag & Drop** hoặc **Click để chọn, click ô để đặt**
- Tile đã đặt vẫn xoay được (Right-click hoặc nút rotate)
- Tile hiển thị bằng SVG path đẹp với glow effect

##### 🐍 Snake Engine
- Rắn di chuyển tự động theo tick timer
- Tốc độ: Level 1 = 600ms/bước → Level 5 = 250ms/bước
- Khi gặp tile → đổi hướng theo tile
- Khi không có tile → dừng (countdown 1s) → mất mạng
- Rắn render trên Canvas với gradient body + glow head

##### ❓ Question System
- Phép tính: Cộng (+), Trừ (-), Nhân (×), Chia (÷) tuỳ level
- Mỗi màn: 1 câu hỏi, 3 ô mồi xuất hiện trên bảng (1 đúng, 2 sai)
- Mồi đúng → điểm + rắn dài thêm
- Mồi sai → rắn ngắn lại + mất 1 màng nhện nhưng không chết ngay
- Câu hỏi thay đổi sau mỗi lần ăn mồi

##### 🌟 Combo & Power-ups
- **Combo x3**: Đúng liên tiếp 3 lần → mồi vàng xuất hiện (x3 điểm)
- **Power-up ❄️ Freeze**: Đóng băng rắn 3 giây — bé có thêm thời gian đặt tile
- **Power-up ⚡ Hint**: Highlight đường đúng trên bản đồ trong 2 giây
- **Power-up 🔀 Reshuffle**: Xáo lại 4 tile trong hand
- Power-up xuất hiện ngẫu nhiên sau mỗi màn (20% chance)

##### 🗺️ World Map (Màn hình chọn màn)
- Thay vì menu khô khan → bản đồ thế giới với rắn nhỏ dạo chơi
- 5 vùng đất: 🌿 Rừng Xanh (Cộng/Trừ) → 🏜️ Sa Mạc (Nhân/Chia) → ❄️ Tuyết Sơn → 🌊 Đại Dương → 🌋 Núi Lửa
- Mỗi vùng 5 màn, tiến trình lưu vào localStorage

##### 📊 Progress & Score
- Màn hình kết quả sau mỗi màn: Sao ⭐⭐⭐ (1/2/3 sao tuỳ thời gian)
- Bảng kiến thức: Phụ huynh xem được các phép tính bé đã làm đúng/sai
- localStorage lưu: bestScore, levelProgress, streakDays

---

### Backend — Route

#### [MODIFY] `main.py`
Thêm route `/game/snake-quest` phục vụ template mới:
```python
@app.get("/game/snake-quest", response_class=HTMLResponse)
async def game_snake_quest(request: Request):
    """Game Snake Quest — Tile Placement Learning Game"""
    return templates.TemplateResponse(request, "games/snake_quest.html")
```

#### [MODIFY] `app/templates/game_hub.html`
Thêm card game **Snake Quest** vào danh sách game hub, với badge "🆕 MỚI" nổi bật.

---

## Kỹ thuật Implementation Chi Tiết

### Canvas Rendering Pipeline
```
gameLoop (requestAnimationFrame)
  ├── updateSnake() — di chuyển theo timer tick
  ├── checkCollision() — kiểm tra va chạm
  ├── renderBoard() — vẽ grid + tiles
  ├── renderSnake() — vẽ rắn với gradient
  └── renderFoods() — vẽ mồi với animation
```

### Tile Data Structure
```javascript
const TILE_TYPES = {
  STRAIGHT_H: { paths: ['W', 'E'], svg: '━━━' },
  STRAIGHT_V: { paths: ['N', 'S'], svg: '┃' },
  CURVE_NE: { paths: ['N', 'E'], svg: '└' },
  CURVE_NW: { paths: ['N', 'W'], svg: '┘' },
  CURVE_SE: { paths: ['S', 'E'], svg: '┌' },
  CURVE_SW: { paths: ['S', 'W'], svg: '┐' },
  T_SHAPE: { paths: ['N', 'E', 'W'], svg: '┴' },
  CROSS: { paths: ['N', 'S', 'E', 'W'], svg: '┼' },
}
```

### Question Generator
```javascript
const levels = {
  1: { ops: ['+', '-'], max: 10 },
  2: { ops: ['+', '-'], max: 20 },
  3: { ops: ['+', '-', '×'], max: 12 },
  4: { ops: ['×', '÷'], max: 9 },
  5: { ops: ['+', '-', '×', '÷'], max: 12 },
}
```

---

## Design Aesthetic

- **Màu chủ đạo:** Deep purple `#1a0a2e` + neon green `#00ff88` + gold `#ffd700`
- **Font:** `Orbitron` (futuristic numbers) + `Nunito` (câu hỏi thân thiện với bé)
- **Tiles:** SVG với glow animation khi hover
- **Snake:** Gradient xanh lá → vàng theo body length
- **Background:** Particle starfield animation
- **Responsive:** Tốt trên mobile (touch drag tiles)

---

## Verification Plan

### Gameplay Testing (Browser)
- [ ] Rắn di chuyển đúng hướng theo tile đặt
- [ ] Va chạm tường → mất mạng
- [ ] Ăn mồi đúng → điểm tăng, rắn dài
- [ ] Ăn mồi sai → rắn ngắn, mất 1 mạng
- [ ] Combo x3 → mồi vàng xuất hiện
- [ ] Power-up ❄️ đóng băng hoạt động
- [ ] Drag & drop tile hoạt động trên desktop
- [ ] Level tăng → rắn nhanh hơn
- [ ] localStorage lưu tiến trình

### Route Testing
- [ ] `/game/snake-quest` trả về 200
- [ ] Card game xuất hiện trong `/game` hub

---

## Câu Hỏi Mở

> [!IMPORTANT]
> **Tile placement UX:** Nên dùng **click-to-select + click-to-place** (đơn giản hơn cho bé) hay **drag-and-drop** (trực quan hơn)? Mình sẽ implement **cả hai** (click trên mobile, drag trên desktop).

> [!NOTE]
> **Snake cũ `/game/snake`:** Giữ nguyên song song hay thay thế? → Đề xuất giữ nguyên, thêm Snake Quest là game riêng mới vì đây là cơ chế khác hoàn toàn.

> [!NOTE]
> **Toán học theo độ tuổi:** Level 1-2 dùng phép cộng/trừ đến 10/20 (bé 4-6 tuổi), Level 3-5 thêm nhân chia (bé 7-10 tuổi). Có muốn thêm lựa chọn "Chế độ dễ / khó" khi bắt đầu không?
