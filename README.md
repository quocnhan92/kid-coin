# kid-coin
Kid Coin for Your Family

TÀI LIỆU THIẾT KẾ CƠ SỞ DỮ LIỆU - KIDCOIN (POSTGRESQL)
1. Nguyên tắc thiết kế (Design Principles)
Multi-tenancy: Mọi dữ liệu custom của người dùng đều gắn với family_id để cô lập dữ liệu giữa các gia đình.

Sổ cái bất biến (Immutable Ledger): Bảng transactions hoạt động như Core Banking, ghi nhận mọi biến động số dư. Tuyệt đối không update trực tiếp cột current_coin mà không có record đối chiếu.

Soft Deletes: Sử dụng cột is_deleted (boolean) cho các cấu hình nhiệm vụ/phần thưởng để bảo toàn lịch sử giao dịch.

2. Cụm Định danh & Phân quyền (Identity & Access)
Bảng families (Quản lý không gian gia đình)
Đóng vai trò là tenant root.

id: UUID (Primary Key)

name: VARCHAR(100) - Tên hiển thị của gia đình (VD: "Nhà Cà Rốt").

parent_pin: VARCHAR(60) - Mã PIN 4 số (đã hash) để khóa không gian của bố mẹ trên thiết bị chung.

created_at: TIMESTAMP

Bảng users (Tài khoản định danh)
Quản lý chung cả bố mẹ và con cái, phân biệt qua Role.

id: UUID (Primary Key)

family_id: UUID (Foreign Key -> families.id)

role: VARCHAR(20) - ENUM: 'PARENT', 'KID'

username: VARCHAR(100) - (Unique, Nullable) Dùng cho Parent đăng nhập (Email/SĐT).

display_name: VARCHAR(50) - Tên gọi ở nhà (VD: Bố Tuấn, Bé Bin).

avatar_url: VARCHAR(255)

current_coin: INTEGER - (Default 0). Số dư ví hiện tại của Kid.

created_at: TIMESTAMP

Index: B-Tree trên (family_id, role) để query nhanh danh sách con cái trong nhà.

3. Cụm Động cơ Nhiệm vụ & Phần thưởng (Task & Reward Engine)
Bảng master_tasks & master_rewards (Dữ liệu mồi của hệ thống)
Cung cấp sẵn các template để bố mẹ chọn bằng 1 chạm.

id: SERIAL (Primary Key)

name: VARCHAR(100) (VD: "Đánh răng", "Xem TV 30 phút")

icon_url: VARCHAR(255)

suggested_value: INTEGER - Điểm gợi ý (cộng hoặc trừ).

category: VARCHAR(50) - Phân loại (Học tập, Việc nhà, Giải trí...)

Bảng family_tasks (Nhiệm vụ custom của gia đình)
id: UUID (Primary Key)

family_id: UUID (Foreign Key -> families.id)

master_task_id: INT (Foreign Key, Nullable) - Trỏ về master nếu chọn từ template.

name: VARCHAR(100)

points_reward: INTEGER - Điểm thưởng do bố mẹ tự định giá.

is_active: BOOLEAN - (Default True). Tắt/bật nhiệm vụ trên bảng của con.

is_deleted: BOOLEAN - (Default False).

Bảng family_rewards (Phần thưởng custom của gia đình)
id: UUID (Primary Key)

family_id: UUID (Foreign Key -> families.id)

master_reward_id: INT (Foreign Key, Nullable)

name: VARCHAR(100)

points_cost: INTEGER - Giá quy đổi (VD: 50 xu).

stock_limit: INTEGER (Nullable) - Số lượng tối đa có thể đổi trong tuần.

is_active: BOOLEAN (Default True)

is_deleted: BOOLEAN (Default False)

4. Cụm Giao dịch & Nhật ký (Transaction & Logs)
Bảng task_logs (Nhật ký thực thi)
Ghi nhận trạng thái làm việc hàng ngày của các bé.

id: UUID (Primary Key)

kid_id: UUID (Foreign Key -> users.id)

task_id: UUID (Foreign Key -> family_tasks.id)

status: VARCHAR(20) - ENUM: 'PENDING_APPROVAL' (Chờ duyệt), 'APPROVED' (Đã duyệt), 'REJECTED' (Bị từ chối).

proof_image_url: VARCHAR(255) (Nullable) - Ảnh chụp minh chứng.

created_at: TIMESTAMP (Lúc con báo cáo xong)

resolved_at: TIMESTAMP (Lúc bố mẹ duyệt)

Bảng transactions (Sổ cái ví điểm - Cực kỳ quan trọng)
id: UUID (Primary Key)

kid_id: UUID (Foreign Key -> users.id)

amount: INTEGER - Số điểm biến động (+ là cộng từ nhiệm vụ, - là trừ do đổi quà).

transaction_type: VARCHAR(50) - ENUM: 'TASK_COMPLETION', 'REWARD_REDEMPTION', 'PENALTY', 'BONUS'.

reference_id: UUID - Trỏ đến task_logs.id hoặc ID của lượt đổi quà để đối soát.

description: VARCHAR(255) (VD: "Thưởng dọn đồ chơi", "Đổi 30p xem Youtube").

created_at: TIMESTAMP

5. Cụm Sân chơi Cộng đồng (Social/Clubs)
Bảng clubs (Nhóm thi đua)
id: UUID (Primary Key)

name: VARCHAR(100) (VD: "Chiến binh việc nhà Lớp 1A")

creator_family_id: UUID (Foreign Key -> families.id)

invite_code: VARCHAR(20) (Unique) - Mã định danh để share qua Zalo.

is_active: BOOLEAN (Default True)

created_at: TIMESTAMP

Bảng club_members (Thành viên nhóm)
club_id: UUID (Foreign Key -> clubs.id)

kid_id: UUID (Foreign Key -> users.id)

joined_at: TIMESTAMP

Primary Key: Composite (club_id, kid_id) để đảm bảo 1 bé không join 1 group 2 lần.

Lời khuyên khi triển khai trên FastAPI (SQLAlchemy)
Quản lý Transaction (Database Commit): Khi API duyệt nhiệm vụ (POST /tasks/approve) được gọi, bạn phải bọc 2 thao tác sau trong cùng một khối transaction của SQLAlchemy (sử dụng db.commit() ở bước cuối):

Thao tác 1: Update bảng task_logs status thành APPROVED.

Thao tác 2: Insert 1 dòng mới vào bảng transactions (+ điểm).

Thao tác 3: Update cột current_coin trong bảng users = current_coin + điểm.

Nếu 1 trong 3 thao tác lỗi, gọi db.rollback() để đảm bảo không bị tình trạng báo duyệt rồi nhưng tiền không vào ví.

Leaderboard API: Khi query bảng xếp hạng cho Club, chỉ cần tính SUM(amount) từ bảng transactions kết hợp với JOIN club_members, lọc theo khoảng thời gian created_at (tuần này, tháng này) là sẽ ra được bảng xếp hạng realtime với hiệu năng rất cao của PostgreSQL.