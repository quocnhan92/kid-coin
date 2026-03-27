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

**Luồng Đăng nhập (Device-First Auth Flow):**
1. **Check Device:** Client gửi `X-Device-ID` (UUID sinh từ localStorage) lên Server.
2. **Identify:**
   - *Đã đăng ký:* Server trả về danh sách thành viên gia đình (Avatar + Tên). Người dùng chọn Avatar để vào. (Bố mẹ cần nhập thêm PIN).
   - *Chưa đăng ký:* Server trả về `404`. Client hiện Form đăng nhập Username/Password của Bố mẹ để kích hoạt thiết bị mới.

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
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Ghi nhận 1 lần làm việc. |
| `kid_id` | `UUID` | FK -> `users.id` | Bé nào thực hiện. *Index: `idx_tasklog_kid`* |
| `family_task_id` | `UUID` | FK -> `family_tasks.id`, Nullable | Điền nếu đây là Việc nhà. |
| `club_task_id` | `UUID` | FK -> `club_tasks.id`, Nullable | Điền nếu đây là Việc của Nhóm/Lớp. |
| `status` | `VARCHAR(20)` | NOT NULL | ENUM: `'PENDING_APPROVAL'`, `'APPROVED'`, `'REJECTED'`. *Index: `idx_tasklog_status`* |
| `proof_image_url` | `VARCHAR(255)` | Nullable | Link ảnh minh chứng. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Lúc bé bấm báo cáo. |
| `resolved_at` | `TIMESTAMP` | Nullable | Lúc bố mẹ bấm "Duyệt" hoặc "Từ chối". |

> **🔥 Ràng buộc DB Toàn vẹn (Check Constraint):** > Yêu cầu Database kiểm tra bắt buộc: `CHECK (num_nonnulls(family_task_id, club_task_id) = 1)`. Một bản ghi Log chỉ được phép trỏ về đúng 1 nguồn nhiệm vụ, không được để trống cả 2 và không được điền cả 2.

### Bảng: `redemption_logs` (Nhật ký đổi quà)

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
| `ip_address` | `VARCHAR(45)` | Nullable | IP của client thực hiện. |
| `user_agent` | `VARCHAR(500)` | Nullable | Chuỗi User-Agent đầy đủ. |
| `device_info` | `JSONB` | Nullable | Snapshot thông tin thiết bị tại thời điểm gọi API (OS, Browser...). |
| `created_at` | `TIMESTAMP` | Default `NOW()` |  |

---

## 2.4. Cụm Sân chơi Cộng đồng (Social Gamification) & Quản lý Thiết bị

### Bảng: `family_devices` (Quản lý thiết bị đăng nhập)
Kiểm soát danh sách thiết bị được phép truy cập của từng gia đình, hỗ trợ thu hồi quyền (Revoke) từ xa.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK, Default `uuid_generate_v4()` | Khóa chính của thiết bị. |
| `family_id` | `UUID` | FK -> `families.id` | Thiết bị này thuộc về nhà nào. *Index: `idx_device_family_id`* |
| `device_name` | `VARCHAR(100)` | NOT NULL | Tên gợi nhớ (VD: "iPad phòng khách"). |
| `device_token` | `VARCHAR(255)` | UNIQUE, NOT NULL | Token cấp quyền cho thiết bị (Nên hash nếu lưu trữ). |
| `initial_ip_address` | `VARCHAR(45)` | Nullable | IP đăng ký lần đầu. |
| `user_agent` | `VARCHAR(500)` | Nullable | Chuỗi User-Agent đầy đủ lúc đăng ký. |
| `device_info` | `JSONB` | Nullable | Thông tin chi tiết thiết bị (OS, Model, Browser) đã parse. |
| `is_default` | `BOOLEAN` | Default `FALSE` | Đánh dấu thiết bị chính chủ của bố mẹ. Không thể bị xóa tự động. |
| `is_active` | `BOOLEAN` | Default `TRUE` | Trạng thái hoạt động (False = Bị phụ huynh thu hồi). |
| `last_active_at` | `TIMESTAMP` | Default `NOW()` | Thời điểm thiết bị gọi API lần cuối (Hỗ trợ dọn rác). |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Ngày thiết bị được cấp quyền. |

### Bảng: `club_tasks` (Nhiệm vụ Nhóm/Lớp)
Nhiệm vụ do Trưởng nhóm (Cô giáo/Phụ huynh tạo nhóm) "phát loa" đến toàn bộ các bé trong Club. Điểm số thực tế do bố mẹ tự duyệt và chi trả.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả & Chú mục (Index) |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | PK | Khóa chính nhiệm vụ nhóm. |
| `club_id` | `UUID` | FK -> `clubs.id` | Nhiệm vụ này thuộc nhóm nào. *Index: `idx_club_task_club_id`* |
| `creator_family_id`| `UUID` | FK -> `families.id` | Gia đình/Người tạo nhiệm vụ (VD: Cô giáo). |
| `name` | `VARCHAR(100)` | NOT NULL | Tên nhiệm vụ (VD: "Làm bài Toán trang 15"). |
| `suggested_points` | `INTEGER` | NOT NULL | Điểm 🌟 gợi ý. |
| `deadline` | `TIMESTAMP` | Nullable | Hạn chót nộp bài (Nếu có). |
| `is_active` | `BOOLEAN` | Default `TRUE` | Trạng thái hiển thị nhiệm vụ. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | |

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
| `user_id` | `UUID` | FK -> `users.id` | Thành viên tham gia (Bố/Mẹ/Con). |
| `role` | `VARCHAR` | NOT NULL | `ADMIN` hoặc `MEMBER`. Hành xử tác vụ quản lý. |
| `joined_at` | `TIMESTAMP` | Default `NOW()` | Ngày gia nhập. |

### Bảng: `club_invitations` (Lời mời vào Nhóm)
Dùng để gửi và duyệt lời mời gia nhập câu lạc bộ, đặc biệt với cơ chế "ủy quyền": Lời mời gửi đến các con (KID) sẽ tự động được điều hướng về chờ cha mẹ (PARENT) duyệt.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính của lời mời |
| `club_id` | `UUID` | FK -> `clubs.id` | Lời mời của nhóm nào. |
| `invited_user_id` | `UUID` | FK -> `users.id` | Người được mời (KID hoặc PARENT). |
| `inviter_id` | `UUID` | FK -> `users.id` | Người mời (Chỉ định ADMIN). |
| `status` | `VARCHAR(20)`| NOT NULL | `PENDING`, `ACCEPTED`, `REJECTED`. |

### Bảng: `notifications` (Hệ thống Chuông thông báo)
Lưu trữ thông báo hệ thống và lời mời, được đồng bộ qua chuông góc màn hình (`🔔Notification Bell`). Xử lý luồng: Mời con -> Gửi chuông cho Bố Mẹ để duyệt.

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| --- | --- | --- | --- |
| `id` | `UUID` | PK | Khóa chính thông báo. |
| `user_id` | `UUID` | FK -> `users.id` | Người nhận thông báo. |
| `type` | `VARCHAR(50)` | NOT NULL | `SYSTEM`, `CLUB_INVITE`, `KID_CLUB_INVITE`, `TASK_ASSIGNED`. |
| `title` & `content` | `VARCHAR` | NOT NULL | Nội dung hiển thị ngắn gọn. |
| `reference_id` | `VARCHAR` | Nullable | Lưu ID liên quan (VD: `invitation_id` để trigger hàm Duyệt). |
| `is_read` | `BOOLEAN` | Default `FALSE` | Trạng thái hiển thị chấm đỏ Unread. |
| `created_at` | `TIMESTAMP` | Default `NOW()` | Thời gian xuất bản. |

---

## 3. THIẾT KẾ GIAO DIỆN LẬP TRÌNH (API DESIGN)

**Công nghệ:** FastAPI (Python)
**Nguyên tắc thiết kế:** RESTful, tuân thủ ACID Transaction cho các nghiệp vụ tài chính ảo. Phân quyền thông qua JWT Token (`family_id`, `role`).

### 3.1. Nhóm API Authentication (Device-First)

* `GET /api/v1/auth/device-status`: Kiểm tra `X-Device-ID`. Trả về danh sách thành viên nếu đã đăng ký.
* `POST /api/v1/auth/register-device`: Login lần đầu bằng `username/password` của Parent để cấp quyền cho thiết bị. Lưu IP, UserAgent.
* `POST /api/v1/auth/quick-login`: Đăng nhập nhanh bằng Avatar. Yêu cầu PIN nếu là Parent.

### 3.2. Nhóm API Core Gamification (Daily Life)

* `GET /api/v1/quests/daily` *(Role: PARENT/KID)*: Lấy danh sách việc cần làm trong ngày.
* `POST /api/v1/quests/{task_id}/submit` *(Role: KID)*: Bé gửi báo cáo (`proof_image_url`). Chuyển status `task_logs` -> `PENDING_APPROVAL`.
* `POST /api/v1/quests/{log_id}/verify` *(Role: PARENT)*: Bố mẹ duyệt (APPROVE/REJECT).
* *Transaction bắt buộc (Nếu APPROVE):* Update `task_logs` -> Insert `transactions` (+ Coin) -> Update `users.current_coin` AND `users.total_earned_score` (+ XP) -> Ghi `audit_logs`. Rollback nếu lỗi.


* `GET /api/v1/rewards` *(Role: PARENT/KID)*: Xem giỏ hàng phần thưởng.
* `POST /api/v1/rewards/{reward_id}/redeem` *(Role: KID)*: Bé đổi quà. Check `current_coin` >= `cost`. Transaction trừ tiền. Tạo record `redemption_logs`.
* `PUT /api/v1/rewards/delivery/{redemption_id}` *(Role: PARENT)*: Bố mẹ xác nhận "Đã đưa quà" -> Status `DELIVERED`.
* `GET /api/v1/users/{kid_id}/history` *(Role: PARENT/KID)*: Xem sao kê từ bảng `transactions`.

### 3.3. Nhóm API Social Gamification (Community)

* `POST /api/v1/clubs` *(Role: PARENT)*: Tạo nhóm, sinh `invite_code`.
* `POST /api/v1/clubs/join` *(Role: PARENT)*: Nhập `invite_code` để join các bé nhà mình vào nhóm.
* `POST /api/v1/clubs/{club_id}/invite` *(Role: ADMIN)*: Mời User bất kỳ trong hệ thống. Nếu là KID, hệ thống tạo Ticket thông báo chờ PARENT duyệt.
* `PUT /api/v1/clubs/{club_id}/invitations/{invitation_id}/respond` *(Role: PARENT)*: Phụ huynh quyết định `ACCEPT` hoặc `REJECT` thay cho con cái.
* `GET /api/v1/clubs/{club_id}/leaderboard` *(Role: PARENT/KID)*: Lấy bảng xếp hạng. Sắp xếp theo `total_earned_score` để đối chiếu thi đua.

### 3.4. Nhóm API Giao tiếp & Thông báo (Notifications)
* `GET /api/v1/notifications` *(Role: PARENT/KID)*: Tải dữ liệu đẩy (Polling) cho giao diện Dropdown Chuông 🔔.
* `PUT /api/v1/notifications/{id}/read` *(Role: PARENT/KID)*: Đánh dấu đã đọc một thông báo.
* `PUT /api/v1/notifications/read-all` *(Role: PARENT/KID)*: Làm sạch số lượng báo đỏ.

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
