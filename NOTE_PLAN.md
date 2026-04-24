# KidCoin Project - NotePlan & Roadmap

Tài liệu này tổng hợp các hạng mục lớn của dự án, giúp theo dõi tiến độ triển khai và lên kế hoạch cho các giai đoạn tiếp theo.

---

## 1. Các Hạng Mục Đã Triển Khai (Implemented)
- [x] **Cấu trúc Backend:** Khởi tạo dự án FastAPI, SQLAlchemy, Alembic migration.
- [x] **Module Game Hub (V1):**
    - [x] Landing page `/game` phong cách Arcade.
    - [x] Mini-games HTML5/JS: Snake, 2048, Memory Match, Flappy Coin.
    - [x] Tích hợp Ad Slots (đã quy hoạch nhưng đang ẩn).
- [x] **Database Schema:** Schema khởi tạo cho User, Family, Task, Reward, Transaction.
- [x] **Môi trường:** Cấu hình Docker (PostgreSQL) và port mapping cho dev local.

---

## 2. Các Hạng Mục Đã Phân Tích & Thiết Kế (Ready for Implementation)
Các hạng mục này đã có tài liệu thiết kế (Specs/Design Docs) nhưng chưa được viết code thực tế:

### 📊 Hệ Thống Web Analytics & Tracking
- **Mục tiêu:** Theo dõi lượt truy cập và hành vi người dùng nội bộ.
- **Trạng thái:** Đã có file thiết kế tại `.kiro/specs/web-analytics-tracking/design.md`.
- **Cần làm:**
    - Triển khai `AnalyticsMiddleware`.
    - Tạo các bảng: `web_page_views`, `web_sessions`, `web_daily_stats`.
    - Xây dựng Dashboard báo cáo cho Parent/Admin.

### 🎮 Mở Rộng Game Hub Tracking
- **Mục tiêu:** Theo dõi chi tiết Play Time và Event trong game.
- **Trạng thái:** Đã có phụ lục thiết kế trong file analytics.
- **Cần làm:**
    - Triển khai endpoint `POST /api/v1/analytics/events`.
    - Viết script JS định danh `device_id` ẩn danh và gửi `ping` từ client.

---

## 3. Các Hạng Mục Còn Trong Ý Tưởng (Ideas / Backlog)
Các ý tưởng lớn cần được cụ thể hóa thành Specs và triển khai trong tương lai:

### 💰 Tích Hợp Hệ Sinh Thái (App + Game)
- **Pay to Play:** Trẻ tiêu KidCoin để chơi game Premium.
- **Play to Earn:** Thưởng Coin khi trẻ đạt điểm cao ở game giáo dục (Toán, Tiếng Anh).
- **Leaderboard:** Bảng xếp hạng thi đua trong gia đình hoặc câu lạc bộ.

### 🚀 Phát Triển Game Hub & Quảng Cáo
- **Bổ sung game:** Math Blast (Toán), Sudoku Kids, Word Scramble, Dino Run, Tetris.
- **Kích hoạt Ads:** Bật banner quảng cáo đối tác khi traffic ổn định.
- **Rewarded Video:** Xem quảng cáo để nhận thêm lượt chơi hoặc Coin.

### 🔗 Mở Rộng Hệ Thống (External)
- **Mini-App:** Đưa Game Hub lên Zalo, MoMo, Telegram để kéo user.
- **Open Platform:** Cho phép bên thứ 3 đưa game giáo dục lên hệ thống.
- **Cross-Promotion:** Hợp tác quảng cáo chéo với các app giáo dục khác.

---

## 4. Thứ Tự Ưu Tiên Triển Khai (Updated Roadmap)
1. **Làm phong phú kho game & Tối ưu SEO:** 
    - Bổ sung các game: Math Blast, Sudoku, Dino Run, Tetris...
    - Tối ưu SEO (Meta tags, OpenGraph, Sitemap) cho từng trang game cụ thể để tăng hạng tìm kiếm và tiếp cận người dùng rộng rãi nhất.
2. **Triển khai Game Hub Tracking:** Đo lường hiệu quả tương tác thực tế bên trong từng game (Play time, Events).
3. **Hoàn thiện Web Analytics:** Cài đặt Middleware và Dashboard để theo dõi tổng thể traffic toàn hệ thống.
4. **Hiện thực hóa "Pay to Play":** Kết nối ví Coin và tích hợp sâu vào hệ sinh thái KidCoin sau khi đã có lượng user ổn định.

---
*Ghi chú: NotePlan này sẽ được cập nhật liên tục dựa trên tiến trình thực tế của dự án.*
