# Implementation Plan: KidCoin Expansion

## Overview

Triển khai theo thứ tự ưu tiên: DB schema → Gamification → Finance → Thinking → Social → Teen → Admin Panel. Mỗi nhóm độc lập, có thể deploy riêng.

## Tasks

### PHASE 1: Database & Infrastructure

- [x] 1. Alembic migration cho tất cả bảng mới (Đã verify Migration chain và cấu trúc)
  - [x] 1.1 Migration 003: Gamification tables (`user_levels`, `user_streaks`, `avatar_items`, `user_avatar_items`)
  - [x] 1.2 Migration 004: Finance tables (`saving_goals`, `savings_accounts`, `loan_accounts`, `charity_fund`, `charity_donations`)
  - [x] 1.3 Migration 005: Thinking tables (`task_bids`, `problem_boards`, `problem_solutions`, `weekly_reflections`)
  - [x] 1.4 Migration 006: Social tables (`wall_of_fame`, `wall_likes`, `family_challenges`, `challenge_progress`)
  - [x] 1.5 Migration 007: Teen tables (`teen_contracts`, `contract_checkins`, `personal_projects`, `project_milestone_logs`)
  - [x] 1.6 Migration 008: Admin table (`admin_users`) + extend `users` (charity_rate, is_teen_mode) + extend `families` (charity_rate, is_suspended) + extend `transactions` (new types)

- [x] 2. SQLAlchemy Models (Đã verify Import, Relationships và Schema parity)
  - [x] 2.1 `app/models/gamification.py`: UserLevel, UserStreak, AvatarItem, UserAvatarItem
  - [x] 2.2 `app/models/finance.py`: SavingGoal, SavingsAccount, LoanAccount, CharityFund, CharityDonation
  - [x] 2.3 `app/models/thinking.py`: TaskBid, ProblemBoard, ProblemSolution, WeeklyReflection
  - [x] 2.4 `app/models/social.py`: WallOfFame, WallLike, FamilyChallenge, ChallengeProgress (Integrated into social.py)
  - [x] 2.5 `app/models/teen.py`: TeenContract, ContractCheckin, PersonalProject, ProjectMilestoneLog
  - [x] 2.6 `app/models/admin.py`: AdminUser

- [x] 3. Seed data cho master tables (Đã nạp 10 level, 20 items và đồng bộ model)
  - [x] 3.1 Seed `user_levels`: 10 levels (Người mới → Huyền thoại) với XP thresholds
  - [x] 3.2 Seed `avatar_items`: 20 items (frames, badges, accessories) với giá Coin
  - [x] 3.3 Cập nhật seed `master_tasks` và `master_rewards` với thêm data

- [x] 4. Cron Job Infrastructure (Đã verify APScheduler initialization và job registration)
  - [x] Tạo `app/core/scheduler.py` dùng APScheduler
  - [x] Đăng ký scheduler trong `main.py` startup event
  - _Requirements: REQ-G2, REQ-F2, REQ-F3, REQ-T3, REQ-S2_

### PHASE 2: Gamification

- [x] 5. XP & Level API
  - [x] `GET /api/v1/gamification/me/level` — trả về current level, XP, next level threshold
  - [x] Level-up logic tích hợp khi task APPROVED (Đã verify logic trong gamification_service.py)
  - _Requirements: REQ-G1_

- [x] 6. Streak System
  - [x] `app/services/streak_service.py`: `update_streak(kid_id)`, `reset_expired_streaks()`
  - [x] Tích hợp vào `approve_task` endpoint (Đã verify manual audit)
  - [x] Cron job `streak_updater` (00:05 daily)
  - [x] `GET /api/v1/gamification/me/streak` — xem streak hiện tại
  - _Requirements: REQ-G2_

- [x] 7. Avatar Shop
  - [x] `GET /api/v1/gamification/shop` — danh sách items (Đã verify logic mua & trang bị)
  - [x] `POST /api/v1/gamification/shop/buy/{item_id}` — mua item
  - [x] `GET /api/v1/gamification/inventory` — inventory của kid
  - [x] `POST /api/v1/gamification/inventory/equip/{ua_id}` — equip/unequip
  - _Requirements: REQ-G3_

### PHASE 3: Finance Education

- [x] 8. Saving Goals
  - [x] `POST /api/v1/finance/goals` — tạo goal (Triển khai trong finance.py)
  - [x] `GET /api/v1/finance/goals` — danh sách goals của kid
  - _Requirements: REQ-F1_

- [x] 9. Savings Accounts
  - [x] `POST /api/v1/finance/savings` — Parent tạo savings cho kid
  - [x] `GET /api/v1/finance/savings` — danh sách
  - [x] Cron job `savings_maturity` (08:00 daily)
  - _Requirements: REQ-F2_

- [x] 10. Loan Accounts
  - [x] `GET /api/v1/finance/loans` — danh sách loans
  - [x] Tích hợp auto-repay và trả nợ thủ công (`/loans/repay`)
  - [x] Cron job `loan_overdue` (08:00 daily)
  - _Requirements: REQ-F3_

- [x] 11. Charity Fund
  - [x] `GET /api/v1/finance/charity` — xem quỹ và lịch sử
  - [x] Tích hợp auto-donate vào `approve_task` (finance_service.process_income)
  - _Requirements: REQ-F4_

### PHASE 4: Critical Thinking

- [x] 12. Task Bid
  - [x] `POST /api/v1/thinking/bids` — Kid tạo đề xuất thương lượng
  - [x] `GET /api/v1/parent/thinking/bids` — Parent xem danh sách
  - [x] `POST /api/v1/parent/thinking/bids/{id}/respond` — ACCEPT/REJECT/COUNTER
  - _Requirements: REQ-T1_

- [x] 13. Problem Board
  - [x] `POST /api/v1/parent/thinking/problems` — Parent đăng bài toán
  - [x] `GET /api/v1/thinking/problems` — Kid xem danh sách
  - [x] `POST /api/v1/thinking/problems/{id}/solutions` — Kid gửi lời giải
  - [x] `POST /api/v1/parent/thinking/solutions/{id}/verify` — Parent verify & thưởng
  - [x] Cron job `maintenance_cleanup` để đóng bài toán hết hạn
  - _Requirements: REQ-T2_

- [x] 14. Weekly Reflection
  - [x] `GET /api/v1/thinking/reflections/me` — Kid xem reflection hiện tại
  - [x] `PUT /api/v1/thinking/reflections/{id}/submit` — Kid gửi câu trả lời
  - [x] `GET /api/v1/parent/thinking/reflections` — Parent xem danh sách chờ
  - [x] `POST /api/v1/parent/thinking/reflections/{id}/reward` — Approve + tặng bonus coin
  - [x] Cron job `weekly_reflection_creator_job` (Sunday 20:00)
  - _Requirements: REQ-T3_

### PHASE 5: Social & Family

- [x] 15. Wall of Fame
  - [x] `POST /api/v1/parent/social/wall` — Parent đăng post vinh danh
  - [x] `GET /api/v1/social/wall` — Xem bảng tin của gia đình
  - [x] `POST /api/v1/social/wall/{id}/like` — Thả tim bài viết
  - _Requirements: REQ-S1_

- [x] 16. Family Challenge
  - [x] `POST /api/v1/parent/social/challenges` — Tạo thử thách gia đình
  - [x] `GET /api/v1/social/challenges` — Xem danh sách thử thách đang chạy
  - [x] `POST /api/v1/social/challenges/{id}/checkin` — Điểm danh mỗi ngày
  - [x] Tự động tặng thưởng khi hoàn thành mục tiêu (`social_service.complete_challenge`)
  - [x] Cron job `maintenance_cleanup_job` xử lý quá hạn
  - _Requirements: REQ-S2_

### PHASE 6: Teen Mode

- [x] 17. Teen Mode Toggle
  - [x] `PUT /api/v1/parent/kids/{id}/teen-mode` — Bật/tắt chế độ Teen Mode
  - _Requirements: REQ-TN1_

- [x] 18. Teen Contract
  - [x] `POST /api/v1/teen/contracts` — Tạo hợp đồng (Draft)
  - [x] `POST /api/v1/teen/contracts/{id}/sign` — Ký kích hoạt hợp đồng
  - [x] `POST /api/v1/teen/contracts/{id}/checkin` — Điểm danh hàng ngày
  - [x] `GET /api/v1/parent/teen/contracts` — Parent xem và duyệt
  - _Requirements: REQ-TN1_

- [x] 19. Personal Project
  - [x] `POST /api/v1/parent/teen/projects` — Tạo dự án cá nhân cho con
  - [x] `GET /api/v1/teen/projects` — Xem danh sách dự án
  - [x] `POST /api/v1/teen/projects/{id}/milestones/{idx}/submit` — Gửi minh chứng hoàn thành mốc
  - [x] `POST /api/v1/parent/teen/projects/{id}/milestones/{idx}/verify` — Xác minh và giải ngân Coin
  - _Requirements: REQ-TN2_

### PHASE 7: Admin Panel

- [x] 20. Admin Auth
  - [x] `POST /api/v1/admin/auth/login` — Đăng nhập Admin (Bcrypt) (Đã verify trong test_admin_flow)
  - [x] `GET /api/v1/admin/auth/me` — Profile Admin
  - [x] Specialized Admin JWT Middleware
  - _Requirements: REQ-A1_

- [x] 21. Admin Family & User Management
  - [x] `GET /api/v1/admin/families` — Liệt kê toàn bộ gia đình (Đã verify trong admin_service.py)
  - [x] `PUT /api/v1/admin/users/{id}/adjust-coins` — Điều chỉnh số dư Admin (kèm log)
  - _Requirements: REQ-A2, REQ-A5_

- [x] 22. Admin Master Data CRUD
  - [x] `GET/POST/PUT/DELETE /admin/master-tasks` (Đã verify trong test_admin_flow)
  - [x] `GET/POST/PUT/DELETE /admin/master-rewards` (Đã verify trong test_admin_flow)
  - [x] `GET/POST/PUT/DELETE /admin/avatar-items` (Đã verify trong test_admin_flow)
  - [x] `GET/POST/PUT/DELETE /admin/levels` (Đã verify trong test_admin_flow)
  - _Requirements: REQ-A3_

- [x] 23. Admin Dashboard & Stats
  - [x] `GET /api/v1/admin/analytics/dashboard` — KPIs tổng quan (Đã verify trong test_admin_flow)
  - [x] `GET /admin/stats/daily-active` (Đã verify trong test_admin_flow)
  - [x] `GET /admin/logs/errors` — Error log viewer (Đã lọc từ Audit logs thất bại)
  - [x] HTML dashboard tại `/admin` (Sử dụng Jinja2 + Chart.js)
  - _Requirements: REQ-A4_

- [x] 24. Admin HTML Templates
  - [x] `app/templates/admin/layout.html` — Base layout với sidebar hiện đại
  - [x] `app/templates/admin/dashboard.html` — Stats overview với Charts
  - [x] `app/templates/admin/families.html` — Family list với tính năng Adjust
  - [x] `app/templates/admin/master_data.html` — Master data CRUD với thiết kế Tabs

### PHASE 8: Frontend Integration

- [x] 25. Kid Dashboard updates
  - [x] Thêm Level badge + Streak counter vào header
  - [x] Tab Avatar Shop
  - [x] Tab Finance (Goals, Savings, Loans)
  - [x] Tab Thinking (Bids, Problems, Reflection)

- [ ] 26. Parent Dashboard updates
  - Thêm Finance management section
  - Problem Board creation
  - Wall of Fame section
  - Challenge creation
  - Teen mode controls

- [ ] 27. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Mỗi Phase có thể deploy độc lập
- Phase 1 (DB) phải hoàn thành trước tất cả phases khác
- Cron jobs dùng APScheduler (in-process, không cần Redis/Celery)
- Admin Panel dùng separate JWT secret để tách biệt hoàn toàn
- Tất cả thay đổi Coin phải có transaction record (Coin conservation invariant)
