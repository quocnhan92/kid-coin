Đây là bản tái cấu trúc tài liệu thiết kế dự án **KidCoin** theo chuẩn Software Architecture Document (SAD), giúp bạn có một cái nhìn tổng thể, khoa học và dễ dàng theo dõi trong suốt quá trình phát triển dự án.

---

# TÀI LIỆU THIẾT KẾ HỆ THỐNG - KIDCOIN

## 1. MỤC TIÊU DỰ ÁN (TARGET)

KidCoin là nền tảng quản lý gia đình định hướng Gamification (Trò chơi hóa) và Social Gamification (Thi đua cộng đồng).

* **Vấn đề giải quyết:** Giảm tải áp lực nhắc nhở việc nhà cho phụ huynh; tạo động lực tự giác và bài học quản lý tài chính sớm cho trẻ em.
* **Đối tượng (Users):** Phụ huynh (Người giao việc & cấp quyền) và Trẻ em (Người thực hiện & nhận thưởng).
* **Giá trị cốt lõi:**
* *Gia đình:* Không gian khép kín, an toàn để quản lý nội bộ.
* *Hệ thống:* Giao dịch điểm số minh bạch, bất biến như ngân hàng.
* *Cộng đồng:* Sân chơi thi đua chéo giữa các gia đình (Clubs/Leaderboard).



---

# 2.️ THIẾT KẾ CƠ SỞ DỮ LIỆU CHUYÊN SÂU (DATABASE DESIGN SPECIFICATION)

* **Hệ quản trị:** PostgreSQL
* **Schema:** `public`

---

## 2.1. Cụm Định danh & Phân quyền (Identity & Access)

Cụm này quản lý thông tin cốt lõi của các gia đình và các thành viên bên trong. Thiết kế đảm bảo sự cô lập dữ liệu (Multi-tenancy) ở cấp độ `family_id`.

### Bảng: `families` (Root Tenant)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK, Default `uuid_generate_v4()` | Khóa chính định danh gia đình. |
| `name` | `VARCHAR(100)` | NOT NULL | Tên hiển thị (VD: "Nhà Cà Rốt"). *Index: `idx_family_name*` |
| `parent_pin` | `VARCHAR(60)` | NOT NULL | Mã PIN 4 số (đã hash qua bcrypt) để khóa quyền thiết lập. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Thời gian khởi tạo. |

### Bảng: `users` (Thành viên gia đình)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK, Default `uuid_generate_v4()` | Khóa chính. |
| `family_id` | `UUID` | FK -> `families.id` | Trỏ về gia đình. *Index: B-Tree `(family_id, role)*` |
| `role` | `VARCHAR(20)` | NOT NULL | ENUM: `'PARENT'`, `'KID'`. |
| `username` | `VARCHAR(100)` | UNIQUE, Nullable | Định danh đăng nhập của PARENT (SĐT/Email). *Index: `idx_user_username*` |
| `display_name` | `VARCHAR(50)` | NOT NULL | Tên gọi ở nhà (VD: Bố Tuấn, Bé Bin). |
| `avatar_url` | `VARCHAR(255)` | Nullable | Đường dẫn ảnh đại diện/icon. |
| `current_coin` | `BIGINT` | Default `0` | Số dư khả dụng (Wallet Balance) để đổi quà. |
| `total_earned_score` | `BIGINT` | Default `0` | Tổng điểm tích lũy trọn đời (Experience/XP). Dùng để xếp hạng Leaderboard, không bị trừ khi tiêu Coin. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Thời gian tạo tài khoản. |

---

## 2.2. Cụm Động cơ Gamification (Task & Reward Engine)

Lưu trữ danh mục công việc và phần thưởng. Tách biệt giữa dữ liệu mồi của hệ thống (`master_`) và dữ liệu tùy biến của từng nhà (`family_`).

### Bảng: `master_tasks` (Nhiệm vụ hệ thống gợi ý)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `SERIAL` | PK | Dùng auto-increment cho dữ liệu tĩnh. |
| `name` | `VARCHAR(100)` | NOT NULL | Tên mẫu (VD: "Đánh răng trước khi ngủ"). |
| `icon_url` | `VARCHAR(255)` | Nullable | Hình ảnh icon chuẩn. |
| `suggested_value` | `BIGINT` | NOT NULL | Mức điểm khuyến nghị (VD: 10). |
| `category` | `VARCHAR(50)` | NOT NULL | Nhóm (Việc nhà, Học tập). *Index: `idx_master_task_category*` |

> **Lưu ý:** Cần tạo thêm bảng `master_rewards` có cấu trúc tương tự `master_tasks`, dùng để mồi dữ liệu phần thưởng gợi ý cho hệ thống.

### Bảng: `family_tasks` (Nhiệm vụ thực tế của gia đình)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính nhiệm vụ tùy biến. |
| `family_id` | `UUID` | FK -> `families.id` | Chỉ hiển thị trong gia đình này. *Index: `idx_family_task_fid*` |
| `master_task_id` | `INTEGER` | FK -> `master_tasks.id` | Null nếu bố mẹ tự tạo mới hoàn toàn. Dữ liệu tại đây độc lập với Master sau khi tạo. |
| `name` | `VARCHAR(100)` | NOT NULL | Tên công việc. |
| `points_reward` | `BIGINT` | NOT NULL, `> 0` | Điểm cộng (XP) và Coin nhận được khi hoàn thành. |
| `is_active` | `BOOLEAN` | Default `TRUE` | Trạng thái hiển thị trên app của con. |
| `is_deleted` | `BOOLEAN` | Default `FALSE` | Soft Delete bảo toàn lịch sử. |

### Bảng: `family_rewards` (Phần thưởng do gia đình cấu hình)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính phần thưởng. |
| `family_id` | `UUID` | FK -> `families.id` | *Index: `idx_family_reward_fid*` |
| `name` | `VARCHAR(100)` | NOT NULL | Tên quà (VD: "30 phút chơi iPad"). |
| `points_cost` | `BIGINT` | NOT NULL, `> 0` | Giá quy đổi (Số xu trừ đi). |
| `stock_limit` | `INTEGER` | Nullable | Số lượng tối đa có thể đổi (VD: 2 lần/tuần). |
| `is_active` | `BOOLEAN` | Default `TRUE` | Hiển thị/Ẩn trong Cửa hàng. |
| `is_deleted` | `BOOLEAN` | Default `FALSE` | Soft Delete. |

---

## 2.3. Cụm Giao dịch cốt lõi & Nhật ký (Core Ledger & Audit)

Trái tim của hệ thống tài chính ảo. Đảm bảo tính nhất quán (ACID) của toàn bộ luồng điểm số.

### Bảng: `task_logs` (Nhật ký thực thi nhiệm vụ)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Ghi nhận 1 lần làm việc. |
| `kid_id` | `UUID` | FK -> `users.id` | Bé nào thực hiện. *Index: `idx_tasklog_kid*` |
| `task_id` | `UUID` | FK -> `family_tasks.id` | Làm việc gì. |
| `status` | `VARCHAR(20)` | NOT NULL | ENUM: `'PENDING_APPROVAL'`, `'APPROVED'`, `'REJECTED'`. *Index: `idx_tasklog_status*` |
| `proof_image_url` | `VARCHAR(255)` | Nullable | Link ảnh minh chứng bé chụp. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Lúc bé bấm "Đã xong". |
| `resolved_at` | `TIMESTAMP` | Nullable | Lúc bố mẹ bấm "Duyệt" hoặc "Từ chối". |

### Bảng: `redemption_logs` (Nhật ký đổi quà - Mới bổ sung)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK |  |
| `kid_id` | `UUID` | FK -> `users.id` |  |
| `reward_id` | `UUID` | FK -> `family_rewards.id` |  |
| `status` | `VARCHAR(20)` | NOT NULL | ENUM: `'PENDING_DELIVERY'`, `'DELIVERED'`. (Chờ bố mẹ đưa quà / Đã nhận). |
| `created_at` | `TIMESTAMP` | Default `NOW()` |  |

### Bảng: `transactions` (Sổ cái bất biến - Lịch sử điểm số)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính giao dịch. |
| `kid_id` | `UUID` | FK -> `users.id` | Tài khoản biến động. *Index: `idx_trx_kid*` |
| `amount` | `BIGINT` | NOT NULL | Giá trị (+ là cộng điểm, - là trừ điểm). |
| `transaction_type` | `VARCHAR(50)` | NOT NULL | ENUM: `'TASK_COMPLETION'`, `'REWARD_REDEMPTION'`, `'PENALTY'`, `'BONUS'`. |
| `reference_id` | `UUID` | Nullable | Trỏ đến `task_logs.id` hoặc `redemption_logs.id` để đối soát. |
| `description` | `VARCHAR(255)` | NOT NULL | Diễn giải (VD: "Hoàn thành: Rửa bát"). |
| `created_at` | `TIMESTAMP` | Default `NOW()` | *Index: `idx_trx_created_at*` (Phục vụ truy vấn Leaderboard cực nhanh). |

### Bảng: `audit_logs` (Ghi vết hệ thống chi tiết)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính log. |
| `user_id` | `UUID` | FK Nullable | Người thao tác (Bố/Mẹ/Con). |
| `action` | `VARCHAR(100)` | NOT NULL | Tên hành động (VD: `'APPROVE_TASK'`). |
| `status` | `VARCHAR(20)` | NOT NULL | ENUM: `'INIT'`, `'PROCESSING'`, `'SUCCESS'`, `'FAILED'`. |
| `details` | `JSONB` | Nullable | Payload request/diff changes. |
| `request_id` | `VARCHAR(50)` | Nullable | Trace ID từ Middleware để gom nhóm log. |
| `error_message` | `TEXT` | Nullable | Lưu Stack Trace nếu lỗi. |
| `created_at` | `TIMESTAMP` | Default `NOW()` |  |

---

## 2.4. Cụm Sân chơi Cộng đồng (Social Gamification)

Phục vụ tính năng thi đua chéo giữa các gia đình (Leaderboard, Clubs) mà vẫn bảo mật thông tin nội bộ.

### Bảng: `clubs` (Câu lạc bộ / Nhóm thi đua)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính nhóm. |
| `name` | `VARCHAR(100)` | NOT NULL | Tên nhóm (VD: "Chiến binh việc nhà"). |
| `creator_family_id` | `UUID` | FK -> `families.id` | Gia đình khởi tạo (Admin nhóm). |
| `invite_code` | `VARCHAR(20)` | UNIQUE, NOT NULL | Mã chia sẻ qua Zalo/Facebook. *Index: `idx_club_invite*` |
| `is_active` | `BOOLEAN` | Default `TRUE` | Trạng thái hoạt động của nhóm. |
| `created_at` | `TIMESTAMP` | Default `NOW()` |  |

### Bảng: `club_members` (Thành viên tham gia)

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| --- | --- | --- | --- |
| `club_id` | `UUID` | FK -> `clubs.id` | Thuộc nhóm nào. |
| `kid_id` | `UUID` | FK -> `users.id` | Bé nào tham gia. |
| `joined_at` | `TIMESTAMP` | Default `NOW()` | Ngày gia nhập. |

> **Lưu ý:** Bảng `club_members` sử dụng **Composite Primary Key** gồm `(club_id, kid_id)` để đảm bảo một bé không thể tham gia trùng lặp 2 lần vào cùng một nhóm.

---

## 3. THIẾT KẾ GIAO DIỆN LẬP TRÌNH (API DESIGN)

**Công nghệ:** FastAPI (Python)
**Nguyên tắc thiết kế:** RESTful, tuân thủ ACID Transaction cho các nghiệp vụ tài chính ảo. Phân quyền thông qua JWT Token (`family_id`, `role`).

### 3.1. Nhóm API Core Gamification (Daily Life)

* `GET /api/v1/quests/daily` *(Role: PARENT/KID)*: Lấy danh sách việc cần làm trong ngày.
* `POST /api/v1/quests/{task_id}/submit` *(Role: KID)*: Bé gửi báo cáo (`proof_image_url`). Chuyển status `task_logs` -> `PENDING_APPROVAL`.
* `POST /api/v1/quests/{log_id}/verify` *(Role: PARENT)*: Bố mẹ duyệt (APPROVE/REJECT).
* *Transaction bắt buộc (Nếu APPROVE):* Update `task_logs` -> Insert `transactions` (+ Coin) -> Update `users.current_coin` AND `users.total_earned_score` (+ XP) -> Ghi `audit_logs`. Rollback nếu lỗi.


* `GET /api/v1/rewards` *(Role: PARENT/KID)*: Xem giỏ hàng phần thưởng.
* `POST /api/v1/rewards/{reward_id}/redeem` *(Role: KID)*: Bé đổi quà. Check `current_coin` >= `cost`. Transaction trừ tiền. Tạo record `redemption_logs`.
* `PUT /api/v1/rewards/delivery/{redemption_id}` *(Role: PARENT)*: Bố mẹ xác nhận "Đã đưa quà" -> Status `DELIVERED`.
* `GET /api/v1/users/{kid_id}/history` *(Role: PARENT/KID)*: Xem sao kê từ bảng `transactions`.

### 3.2. Nhóm API Social Gamification (Community)

* `POST /api/v1/clubs` *(Role: PARENT)*: Tạo nhóm, sinh `invite_code`.
* `POST /api/v1/clubs/join` *(Role: PARENT)*: Nhập `invite_code` để join các bé nhà mình vào nhóm.
* `GET /api/v1/clubs/{club_id}/leaderboard` *(Role: PARENT/KID)*: Lấy bảng xếp hạng. Tính toán dựa trên `total_earned_score` (XP) hoặc `SUM(amount)` của tuần hiện tại.

---

## 4. THIẾT KẾ KIẾN TRÚC MÃ NGUỒN (CODE DESIGN)

**Framework Backend:** FastAPI + SQLAlchemy (ORM) + Alembic (Migration).

**Cấu trúc thư mục (Monolith Modular):**

```text
kidcoin_backend/
├── app/
│   ├── api/          # Nơi chứa các Route/Endpoints (v1)
│   ├── core/         # Cấu hình hệ thống (Config, Security, JWT, DB session)
│   ├── models/       # Định nghĩa các Table SQLAlchemy (User, Task, Transaction...)
│   ├── schemas/      # Định nghĩa Pydantic Models để validate request/response (DTOs)
│   ├── services/     # Nơi chứa Logic nghiệp vụ (Fat Service).
│   ├── middleware/   # Request ID generation, Audit Log interception.
│   └── templates/    # Chứa file HTML view (nếu dùng Jinja2)
├── tests/            # Unit tests và Integration tests
├── alembic/          # Quản lý version database
├── docker-compose.yml
└── requirements.txt

```

**Nguyên tắc viết Code:**

1. **Tách biệt Interface và Logic (Fat Service, Thin Controller):** File trong thư mục `api/` chỉ nhận request và trả response. Mọi logic tính toán phải nằm trong `services/`.
2. **Middleware Audit:** Cấu hình Middleware để tự động sinh `request_id` và bắt `audit_logs` cho mọi request ghi đổi dữ liệu.
3. **Validation chặt chẽ:** Sử dụng Pydantic (`schemas/`).

---

## 5. THIẾT KẾ GIAO DIỆN NGƯỜI DÙNG (FE DESIGN)

**Nguyên tắc thiết kế (UI/UX):**

* **Visual-First:** Giao diện cho con không cần chữ, dùng Icon khổng lồ, màu sắc tươi sáng.
* **Instant Feedback:** Hiệu ứng Gamification tức thì. Khi có điểm cộng, màn hình phải nhảy số.

**Wireframe Cốt lõi (3 màn hình chính):**

1. **Dashboard (Ví Sao):** Hiển thị số Coin (Tiêu) và Level (XP).
2. **Bảng Nhiệm Vụ (Task Board):** Các thẻ (Cards) hiển thị icon công việc.
3. **Sân chơi (Leaderboard):** Bảng xếp hạng dựa trên sự chăm chỉ (XP/Score) chứ không phải độ giàu có (Coin).

---

## 6. KẾ HOẠCH TRIỂN KHAI (CI/CD DEPLOYMENT)

**Môi trường:** Oracle Cloud (Free Tier)
**Công cụ:** Docker, GitHub Actions.

1. **Môi trường Local:** Sử dụng `docker-compose` để chạy DB PostgreSQL và Backend song song khi dev.
2. **Database Migration:** Dùng Alembic.
3. **CI/CD Pipeline (.github/workflows):** Push -> Deploy.
