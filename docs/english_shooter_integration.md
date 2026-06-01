# English Shooter — tích hợp Play Hub

Tài liệu map **GDD** (`GDD_EnglishShooter_v1.md`) ↔ DB ↔ API ↔ UI.

## Game & modes

| GDD | `game_id` | `game_mode_id` |
|-----|-----------|----------------|
| Thảo nguyên | `english_shooter` | `english_shooter:prairie` |
| Bảo vệ thành phố | `english_shooter` | `english_shooter:city` |
| Đại Boss | `english_shooter` | `english_shooter:boss` |

Seed: `app/services/english_catalog_seed.py` (startup sau `seed_play_catalog`).

## Catalog DB (migration `012`)

| Bảng | Nội dung |
|------|----------|
| `play_english_weapons` | Vũ khí theo lớp 1–5 |
| `play_english_bosses` | Boss theo lớp |
| `play_english_themes` | Chủ đề (My Family L1 mẫu) |
| `play_english_stages` | `vocab` / `sentence` / `paragraph` |
| `play_english_stage_items` | Câu hỏi, distractors, `options_json` |

## Tiến trình người chơi

- Bảng: `play_user_game_stats` (`game_id=english_shooter`, `game_mode_id` theo mode).
- Payload: `extra_json` — schema trong `english_shooter_progress_service.py` (vàng, rank, `themes_completed`, unlock city/boss).

## API

| Endpoint | Mục đích |
|----------|----------|
| `GET /api/v1/play/bootstrap?game_id=english_shooter&game_mode_id=english_shooter:prairie` | Vàng, rank, themes, weapon |
| `GET /api/v1/play/english/themes?grade=1` | Danh sách chủ đề |
| `GET /api/v1/play/english/themes/{id}/stages/vocab` | Câu hỏi Thảo nguyên |
| `POST /api/v1/play/sessions/batch` | Start/end phiên (giống Math Blast) |
| `POST /api/v1/play/events/batch` | Sync câu đúng → cộng vàng live (prairie: 5 vàng/câu) |
| `GET /api/v1/play/games` | Catalog có English Shooter sau seed |

## UI routes

- Hub: `/game/english-shooter`
- Thảo nguyên MVP: `/game/english-shooter/prairie`
- Kho game: thẻ **Xạ thủ Tiếng Anh** trên `game_hub.html`

## Chạy migration

```bash
alembic upgrade head
```

Khởi động lại app để `ensure_english_shooter_catalog()` chạy trên DB đã có sẵn `play_games`.

## Việc tiếp theo (ngoài MVP)

- UI Thành phố / Boss + speech confidence
- Thêm themes lớp 2–5 theo ma trận GDD §7
- Parent dashboard filter `english_shooter:*`
