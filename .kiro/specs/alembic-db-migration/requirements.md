# Requirements Document

## Introduction

Feature này thay thế toàn bộ hệ thống migration thủ công hiện tại (`app/core/migrations.py` và `migrate.py`) bằng Alembic — công cụ migration chuẩn cho SQLAlchemy. Mục tiêu là tạo một initial migration script bao gồm toàn bộ schema hiện tại (15 bảng), đảm bảo Alembic tự động chạy khi service khởi động, và hỗ trợ môi trường Docker. Đây là bước chuẩn bị cho lần golive đầu tiên với DB sạch hoàn toàn.

## Glossary

- **Alembic**: Thư viện migration database cho SQLAlchemy, hỗ trợ versioning, auto-detect diff, và rollback.
- **Migration_Runner**: Module Python chịu trách nhiệm gọi `alembic upgrade head` khi service khởi động.
- **Initial_Migration**: File migration Alembic đầu tiên chứa toàn bộ DDL schema của dự án KidCoin.
- **Alembic_Env**: File `alembic/env.py` cấu hình kết nối DB và import toàn bộ models.
- **Base**: SQLAlchemy `declarative_base()` được import từ `app.core.database`, là nguồn metadata cho Alembic autogenerate.
- **entrypoint.sh**: Shell script trong Docker container, chạy `alembic upgrade head` trước khi khởi động uvicorn.
- **Legacy_Migration**: Code migration cũ trong `app/core/migrations.py` và `migrate.py` cần được xóa bỏ.

## Requirements

### Requirement 1: Khởi tạo cấu trúc Alembic

**User Story:** As a developer, I want to have a proper Alembic project structure, so that I can manage database migrations with versioning and rollback support.

#### Acceptance Criteria

1. THE Alembic_Env SHALL import toàn bộ SQLAlchemy models từ `app.models` để Alembic có thể detect schema.
2. THE Alembic_Env SHALL đọc `DATABASE_URL` từ biến môi trường, với fallback về `postgresql://kidcoin_user:kidcoin_password@localhost:5432/kidcoin_db`.
3. THE Alembic_Env SHALL sử dụng `Base.metadata` từ `app.core.database` làm `target_metadata` cho autogenerate.
4. THE Alembic_Env SHALL cấu hình `compare_type=True` để detect thay đổi kiểu dữ liệu cột.
5. THE Alembic_Env SHALL cấu hình `render_as_batch=False` vì PostgreSQL hỗ trợ ALTER TABLE trực tiếp.

---

### Requirement 2: Initial Migration Script

**User Story:** As a developer, I want an initial migration that creates the entire database schema from scratch, so that a fresh golive deployment can build the DB without any manual steps.

#### Acceptance Criteria

1. THE Initial_Migration SHALL tạo đầy đủ 15 bảng: `families`, `users`, `master_tasks`, `family_tasks`, `master_rewards`, `family_rewards`, `task_logs`, `redemption_logs`, `transactions`, `clubs`, `club_members`, `club_invitations`, `club_tasks`, `family_devices`, `notifications`, `audit_logs`.
2. THE Initial_Migration SHALL tạo tất cả các Enum types trước khi tạo bảng phụ thuộc vào chúng.
3. THE Initial_Migration SHALL tạo tất cả các Index được định nghĩa trong models (ví dụ: `idx_family_name`, `idx_user_family_role`, `idx_task_log_status`).
4. THE Initial_Migration SHALL tạo `CheckConstraint` `chk_one_task_source` trên bảng `task_logs` đảm bảo `num_nonnulls(family_task_id, club_task_id) = 1`.
5. THE Initial_Migration SHALL tạo tất cả Foreign Key constraints với đúng `ondelete` behavior (CASCADE, SET NULL) như định nghĩa trong models.
6. THE Initial_Migration SHALL có hàm `downgrade()` thực hiện drop tất cả bảng theo thứ tự ngược lại để hỗ trợ rollback hoàn toàn.
7. WHEN `alembic upgrade head` được chạy trên DB trống, THE Initial_Migration SHALL tạo toàn bộ schema thành công mà không có lỗi.
8. WHEN `alembic downgrade base` được chạy sau upgrade, THE Initial_Migration SHALL xóa toàn bộ schema thành công mà không có lỗi.

---

### Requirement 3: Tự động chạy Migration khi Service Khởi động

**User Story:** As a DevOps engineer, I want migrations to run automatically before the application starts, so that every deployment is always in sync with the latest schema without manual intervention.

#### Acceptance Criteria

1. THE Migration_Runner SHALL gọi `alembic upgrade head` trước khi FastAPI application nhận request đầu tiên.
2. WHEN `alembic upgrade head` thành công, THE Migration_Runner SHALL log thông báo thành công và cho phép service tiếp tục khởi động.
3. IF `alembic upgrade head` thất bại, THEN THE Migration_Runner SHALL log lỗi chi tiết và dừng quá trình khởi động service (raise exception).
4. THE entrypoint.sh SHALL chạy `alembic upgrade head` trước lệnh `uvicorn` trong môi trường Docker.
5. THE Dockerfile SHALL sử dụng `entrypoint.sh` làm ENTRYPOINT thay vì CMD trực tiếp.
6. WHEN DB đã ở phiên bản mới nhất, THE Migration_Runner SHALL hoàn thành ngay lập tức mà không thực hiện thay đổi nào (idempotent).

---

### Requirement 4: Dọn dẹp Legacy Migration Code

**User Story:** As a developer, I want to remove the old manual migration scripts, so that there is a single source of truth for database schema management.

#### Acceptance Criteria

1. THE System SHALL xóa file `app/core/migrations.py` khỏi codebase.
2. THE System SHALL xóa file `migrate.py` khỏi codebase.
3. THE System SHALL xóa import `from app.core.migrations import run_migrations` khỏi `main.py`.
4. THE System SHALL xóa lời gọi `run_migrations()` và khối try/except liên quan khỏi `main.py`.
5. THE System SHALL xóa lời gọi `Base.metadata.create_all(bind=engine)` và khối try/except liên quan khỏi `main.py`, vì Alembic đã quản lý schema.

---

### Requirement 5: Hỗ trợ Workflow Phát triển

**User Story:** As a developer, I want clear commands to create and apply new migrations during development, so that I can evolve the schema safely.

#### Acceptance Criteria

1. THE Alembic_Env SHALL hỗ trợ lệnh `alembic revision --autogenerate -m "description"` để tự động tạo migration script từ diff giữa models và DB hiện tại.
2. THE Alembic_Env SHALL hỗ trợ lệnh `alembic upgrade head` để apply tất cả migration chưa được apply.
3. THE Alembic_Env SHALL hỗ trợ lệnh `alembic downgrade -1` để rollback migration gần nhất.
4. THE Alembic_Env SHALL hỗ trợ lệnh `alembic history` để xem lịch sử các migration đã apply.
5. WHERE môi trường Docker được sử dụng, THE Alembic_Env SHALL có thể chạy các lệnh Alembic từ bên trong container thông qua `docker-compose exec web alembic <command>`.
