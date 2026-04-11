# Implementation Plan: alembic-db-migration

## Overview

Thay thế toàn bộ hệ thống migration thủ công bằng Alembic. Các bước được sắp xếp theo thứ tự dependency: cấu trúc Alembic → initial migration script → migration runner → tích hợp Docker → dọn dẹp legacy code → tests.

## Tasks

- [x] 1. Khởi tạo cấu trúc Alembic và cấu hình env.py
  - Tạo thư mục `alembic/` và `alembic/versions/`
  - Tạo file `alembic.ini` với `script_location = alembic` và `sqlalchemy.url` placeholder
  - Tạo `alembic/env.py` import `Base` từ `app.core.database`, import toàn bộ models từ `app.models`, đọc `DATABASE_URL` từ `os.getenv`, set `target_metadata = Base.metadata`, cấu hình `compare_type=True` và `render_as_batch=False`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Tạo initial migration script
  - [x] 2.1 Tạo file `alembic/versions/001_initial_schema.py` với revision id, down_revision = None
    - Hàm `upgrade()`: tạo 10 PostgreSQL enum types trước, sau đó tạo 15 bảng theo đúng thứ tự dependency (families → master_tasks/master_rewards → users → family_tasks/family_rewards → clubs → club_members/club_invitations/club_tasks → task_logs/redemption_logs/transactions → family_devices → notifications → audit_logs)
    - Tạo đầy đủ tất cả indexes được định nghĩa trong models (20 indexes)
    - Tạo `CheckConstraint` `chk_one_task_source` trên `task_logs`
    - Tạo tất cả FK constraints với đúng `ondelete` behavior (CASCADE, SET NULL)
    - Hàm `downgrade()`: drop 15 bảng theo thứ tự ngược lại, sau đó drop tất cả enum types
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 2.2 Viết integration test cho upgrade/downgrade
    - Test `alembic upgrade head` trên DB trống tạo đúng 15 bảng
    - Test tất cả 20 indexes tồn tại sau upgrade
    - Test FK constraints với đúng ondelete behavior
    - Test `alembic downgrade base` xóa sạch toàn bộ schema
    - _Requirements: 2.7, 2.8_

  - [ ]* 2.3 Viết property test cho upgrade/downgrade round-trip (Property 3)
    - **Property 3: Upgrade/Downgrade round-trip**
    - **Validates: Requirements 2.6, 2.8**
    - Dùng `hypothesis` để verify: với bất kỳ fresh DB nào, sau `upgrade head` rồi `downgrade base`, schema phải trống hoàn toàn

- [x] 3. Tạo migration_runner.py
  - Tạo `app/core/migration_runner.py` với hàm `run_alembic_upgrade()`
  - Gọi `alembic upgrade head` programmatically qua `alembic.config.Config` và `alembic.command.upgrade`
  - Log thành công khi migration hoàn thành
  - Raise exception nếu migration thất bại để dừng service startup
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

  - [ ]* 3.1 Viết unit test cho migration_runner
    - Test log success khi alembic upgrade thành công (mock `alembic.command.upgrade`)
    - Test raise exception khi alembic upgrade thất bại
    - _Requirements: 3.2, 3.3_

- [x] 4. Checkpoint — Đảm bảo migration script và runner hoạt động đúng
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Cập nhật main.py — xóa legacy migration code
  - Xóa `from app.core.migrations import run_migrations`
  - Xóa khối `try: run_migrations() except ...`
  - Xóa khối `try: Base.metadata.create_all(bind=engine) except ...`
  - Import và gọi `run_alembic_upgrade` từ `app.core.migration_runner` trong startup sequence (trước khi app nhận request)
  - _Requirements: 4.3, 4.4, 4.5, 3.1_

- [x] 6. Tạo entrypoint.sh và cập nhật Dockerfile
  - [x] 6.1 Tạo `entrypoint.sh` tại root project
    - Thêm `#!/bin/bash` và `set -e`
    - Chạy `alembic upgrade head` trước `exec uvicorn main:app --host 0.0.0.0 --port 8000`
    - _Requirements: 3.4_

  - [x] 6.2 Cập nhật `Dockerfile`
    - Thêm `RUN chmod +x entrypoint.sh` sau bước COPY
    - Thay `CMD [...]` bằng `ENTRYPOINT ["./entrypoint.sh"]`
    - _Requirements: 3.5_

- [x] 7. Xóa legacy migration files
  - Xóa file `app/core/migrations.py`
  - Xóa file `migrate.py`
  - _Requirements: 4.1, 4.2_

- [ ] 8. Viết tests cho CheckConstraint và migration idempotence
  - [x] 8.1 Viết unit/integration test cho CheckConstraint enforcement
    - Test insert task_log với cả hai FK null → DB reject
    - Test insert task_log với cả hai FK có giá trị → DB reject
    - Test insert task_log với đúng một FK có giá trị → DB accept
    - _Requirements: 2.4_

  - [ ]* 8.2 Viết property test cho CheckConstraint enforcement (Property 1)
    - **Property 1: CheckConstraint enforcement trên task_logs**
    - **Validates: Requirements 2.4**
    - Dùng `hypothesis` để generate random combinations của (family_task_id, club_task_id)
    - Verify: chỉ khi đúng một trong hai có giá trị thì insert thành công

  - [ ]* 8.3 Viết property test cho migration idempotence (Property 2)
    - **Property 2: Migration idempotence**
    - **Validates: Requirements 3.6**
    - Verify: chạy `alembic upgrade head` lần thứ hai trên DB đã ở head là no-op và không có lỗi

- [x] 9. Checkpoint cuối — Đảm bảo toàn bộ tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks đánh dấu `*` là optional, có thể bỏ qua để triển khai MVP nhanh hơn
- Thứ tự tạo bảng trong migration phải đúng dependency order (xem design.md)
- `set -e` trong `entrypoint.sh` đảm bảo container dừng nếu migration thất bại
- Với DB dev đang chạy từ `create_all` cũ: dùng `alembic stamp head` để skip initial migration
- Property tests dùng `hypothesis` library (cần thêm vào requirements.txt nếu chưa có)
