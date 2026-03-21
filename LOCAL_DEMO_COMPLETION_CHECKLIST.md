## KidCoin - Local Demo Completion Checklist (No CI)

Mục tiêu: backend + UI đủ khớp nhau để demo chạy trơn luồng chính trên local (quests, approve/reject, coin balance, redeem/delivery, và UI cho parent).

### Done criteria
- UI bấm thao tác thì gọi đúng endpoint backend và backend xử lý logic nhất quán.
- Số liệu hiển thị trên UI (ví dụ `coin-balance`) phản ánh dữ liệu thật từ DB.
- Luồng “bị REJECT thì có thể submit lại trong ngày” (khớp UI).

---

### A. Backend logic gaps (integrate-first)
- [x] Quest daily uses latest log của hôm nay (không lấy log cũ).
- [x] Quest submit: cho phép bé submit lại nếu lần gần nhất trong ngày là `REJECTED`.
- [x] Add `GET /api/v1/users/me` để UI lấy `current_coin`.
- [x] Add `GET /api/v1/users/{kid_id}/history` (backend sẵn cho tương lai UI/diagnostic).

### B. UI + integration (front-end calls correct APIs)
- [x] `kid_dashboard.html`: lấy coin balance từ `GET /api/v1/users/me` lúc load trang.
- [x] `parent_dashboard.html`: thêm tab “Trả Quà”:
  - [x] fetch `/api/v1/parent/pending-redemptions`
  - [x] confirm delivery gọi `PUT /api/v1/rewards/delivery/{redemption_id}` với `{ "status": "DELIVERED" }`
- [x] `parent_dashboard.html`: tab “Nhiệm Vụ” hiển thị list `/api/v1/parent/tasks` và toggle active gọi `PUT /api/v1/parent/tasks/{task_id}/toggle`.

---

### C. Local smoke test (bạn tự chạy để tick tiếp)
- [ ] Khởi động local bằng `docker-compose up` (hoặc run backend + postgres).
- [ ] `GET /login` -> device-status -> quick-login -> redirect:
  - [ ] Login vai KID và kiểm tra coin hiển thị đúng.
  - [ ] Submit quest -> chuyển sang PARENT -> REJECT -> quay lại KID -> submit lại trong ngày thành công.
  - [ ] PARENT -> APPROVE -> coin tăng tương ứng.
- [ ] Redeem reward:
  - [ ] KID redeem 1 reward -> giảm coin + tạo redemption log.
  - [ ] PARENT vào tab “Trả Quà” -> bấm “Đã đưa quà” -> redemption status chuyển `DELIVERED`.
- [ ] Config tasks:
  - [ ] PARENT vào tab “Nhiệm Vụ” -> toggle `is_active` -> quay lại KID kiểm tra quest daily phản ánh thay đổi.

