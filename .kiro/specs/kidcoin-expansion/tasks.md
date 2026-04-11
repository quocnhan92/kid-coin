# Implementation Plan: KidCoin Expansion

## Overview

Triển khai theo thứ tự ưu tiên: DB schema → Gamification → Finance → Thinking → Social → Teen → Admin Panel. Mỗi nhóm độc lập, có thể deploy riêng.

## Tasks

### PHASE 1: Database & Infrastructure

- [-] 1. Alembic migration cho tất cả bảng mới
  - [x] 1.1 Migration 003: Gamification tables (`user_levels`, `user_streaks`, `avatar_items`, `user_avatar_items`)
  - [ ] 1.2 Migration 004: Finance tables (`saving_goals`, `savings_accounts`, `loan_accounts`, `charity_fund`, `charity_donations`)
  - [~] 1.3 Migration 005: Thinking tables (`task_bids`, `problem_boards`, `problem_solutions`, `weekly_reflections`)
  - [~] 1.4 Migration 006: Social tables (`wall_of_fame`, `wall_likes`, `family_challenges`, `challenge_progress`)
  - [~] 1.5 Migration 007: Teen tables (`teen_contracts`, `contract_checkins`, `personal_projects`, `project_milestone_logs`)
  - [~] 1.6 Migration 008: Admin table (`admin_users`) + extend `users` (charity_rate, is_teen_mode) + extend `families` (charity_rate, is_suspended) + extend `transactions` (new types)

- [~] 2. SQLAlchemy Models
  - [~] 2.1 `app/models/gamification.py`: UserLevel, UserStreak, AvatarItem, UserAvatarItem
  - [~] 2.2 `app/models/finance.py`: SavingGoal, SavingsAccount, LoanAccount, CharityFund, CharityDonation
  - [~] 2.3 `app/models/thinking.py`: TaskBid, ProblemBoard, ProblemSolution, WeeklyReflection
  - [~] 2.4 `app/models/social_features.py`: WallOfFame, WallLike, FamilyChallenge, ChallengeProgress
  - [~] 2.5 `app/models/teen.py`: TeenContract, ContractCheckin, PersonalProject, ProjectMilestoneLog
  - [~] 2.6 `app/models/admin.py`: AdminUser

- [~] 3. Seed data cho master tables
  - [~] 3.1 Seed `user_levels`: 10 levels (Người mới → Huyền thoại) với XP thresholds
  - [~] 3.2 Seed `avatar_items`: 20 items (frames, badges, accessories) với giá Coin
  - [~] 3.3 Cập nhật seed `master_tasks` và `master_rewards` với thêm data

- [~] 4. Cron Job Infrastructure
  - Tạo `app/core/scheduler.py` dùng APScheduler
  - Đăng ký scheduler trong `main.py` startup event
  - _Requirements: REQ-G2, REQ-F2, REQ-F3, REQ-T3, REQ-S2_

### PHASE 2: Gamification

- [~] 5. XP & Level API
  - `GET /api/v1/users/me/level` — trả về current level, XP, next level threshold
  - `GET /api/v1/users/{kid_id}/level` — cho Parent xem
  - Level-up notification khi task APPROVED và XP vượt threshold
  - _Requirements: REQ-G1_

- [~] 6. Streak System
  - `app/services/streak_service.py`: `update_streak(kid_id)`, `check_streak_bonus(kid_id)`
  - Tích hợp vào `approve_task` endpoint: sau khi APPROVE → gọi `update_streak`
  - Cron job `streak_updater` (00:05 daily): reset streak cho users không active
  - `GET /api/v1/users/me/streak` — xem streak hiện tại
  - _Requirements: REQ-G2_

- [~] 7. Avatar Shop
  - `GET /api/v1/avatar-shop` — danh sách items (filter by level, type)
  - `POST /api/v1/avatar-shop/{item_id}/buy` — mua item
  - `GET /api/v1/avatar-shop/my-items` — inventory của kid
  - `PUT /api/v1/avatar-shop/my-items/{item_id}/equip` — equip/unequip
  - _Requirements: REQ-G3_

### PHASE 3: Finance Education

- [~] 8. Saving Goals
  - `POST /api/v1/finance/goals` — tạo goal
  - `POST /api/v1/finance/goals/{id}/deposit` — gửi Coin vào
  - `DELETE /api/v1/finance/goals/{id}` — hủy goal (hoàn tiền)
  - `GET /api/v1/finance/goals` — danh sách goals của kid
  - _Requirements: REQ-F1_

- [~] 9. Savings Accounts
  - `POST /api/v1/finance/savings` — Parent tạo savings cho kid
  - `POST /api/v1/finance/savings/{id}/withdraw-early` — rút sớm
  - `GET /api/v1/finance/savings` — danh sách
  - Cron job `savings_maturity` (08:00 daily)
  - _Requirements: REQ-F2_

- [~] 10. Loan Accounts
  - `POST /api/v1/finance/loans` — Parent tạo loan
  - `GET /api/v1/finance/loans` — danh sách loans
  - Tích hợp auto-repay vào `approve_task`
  - Cron job `loan_overdue` (08:00 daily)
  - _Requirements: REQ-F3_

- [~] 11. Charity Fund
  - `GET /api/v1/finance/charity` — xem quỹ và lịch sử
  - `POST /api/v1/finance/charity/donate` — donate tự nguyện
  - `PUT /api/v1/parent/charity-rate` — Parent cấu hình tỷ lệ
  - Tích hợp auto-donate vào `approve_task`
  - _Requirements: REQ-F4_

### PHASE 4: Critical Thinking

- [~] 12. Task Bid
  - `POST /api/v1/bids` — Kid tạo bid
  - `GET /api/v1/parent/bids` — Parent xem pending bids
  - `PUT /api/v1/parent/bids/{id}/respond` — ACCEPT/REJECT/COUNTER
  - `PUT /api/v1/bids/{id}/respond-counter` — Kid respond to counter
  - _Requirements: REQ-T1_

- [~] 13. Problem Board
  - `POST /api/v1/parent/problems` — Parent đăng bài toán
  - `GET /api/v1/problems` — Kid xem danh sách
  - `POST /api/v1/problems/{id}/claim` — Kid claim solution
  - `PUT /api/v1/parent/problems/{id}/solutions/{sol_id}/verify` — Parent verify
  - Cron job `problem_board_expiry`
  - _Requirements: REQ-T2_

- [~] 14. Weekly Reflection
  - `GET /api/v1/reflections/current` — Kid xem reflection tuần này
  - `PUT /api/v1/reflections/{id}/submit` — Kid submit answers
  - `GET /api/v1/parent/reflections` — Parent xem và approve
  - `PUT /api/v1/parent/reflections/{id}/reward` — Approve + trả bonus
  - Cron job `weekly_reflection_creator` (Sunday 20:00)
  - _Requirements: REQ-T3_

### PHASE 5: Social & Family

- [~] 15. Wall of Fame
  - `POST /api/v1/wall` — Parent đăng post
  - `GET /api/v1/wall` — Xem wall của gia đình
  - `POST /api/v1/wall/{id}/like` — Like/unlike
  - _Requirements: REQ-S1_

- [~] 16. Family Challenge
  - `POST /api/v1/parent/challenges` — Tạo challenge
  - `GET /api/v1/challenges` — Xem challenges active
  - `POST /api/v1/challenges/{id}/checkin` — Check-in hàng ngày
  - Cron job `challenge_expiry`
  - _Requirements: REQ-S2_

### PHASE 6: Teen Mode

- [~] 17. Teen Mode Toggle
  - `PUT /api/v1/parent/kids/{id}/teen-mode` — Bật/tắt teen mode
  - _Requirements: REQ-TN1_

- [~] 18. Teen Contract
  - `POST /api/v1/teen/contracts` — Tạo contract (DRAFT)
  - `PUT /api/v1/teen/contracts/{id}/sign` — Ký (cả 2 bên)
  - `POST /api/v1/teen/contracts/{id}/checkin` — Teen check-in
  - `PUT /api/v1/parent/contracts/{id}/milestones/{idx}/verify` — Verify milestone
  - _Requirements: REQ-TN1_

- [~] 19. Personal Project
  - `POST /api/v1/parent/projects` — Tạo project
  - `GET /api/v1/teen/projects` — Teen xem projects
  - `POST /api/v1/teen/projects/{id}/milestones/{idx}/submit` — Submit proof
  - `PUT /api/v1/parent/projects/{id}/milestones/{idx}/verify` — Verify + release coins
  - _Requirements: REQ-TN2_

### PHASE 7: Admin Panel

- [~] 20. Admin Auth
  - `POST /admin/auth/login` — Login với admin credentials
  - `GET /admin/auth/me` — Profile
  - Admin JWT middleware (separate from user JWT)
  - _Requirements: REQ-A1_

- [~] 21. Admin Family & User Management
  - `GET /admin/families` — List với search/filter/pagination
  - `GET /admin/families/{id}` — Chi tiết
  - `PUT /admin/families/{id}/suspend` — Suspend/unsuspend
  - `PUT /admin/families/{id}/reset-pin` — Reset PIN
  - `GET /admin/users` — List users
  - `PUT /admin/users/{id}/adjust-coins` — Adjust với audit log
  - _Requirements: REQ-A2, REQ-A5_

- [~] 22. Admin Master Data CRUD
  - `GET/POST/PUT/DELETE /admin/master-tasks`
  - `GET/POST/PUT/DELETE /admin/master-rewards`
  - `GET/POST/PUT/DELETE /admin/avatar-items`
  - `GET/POST/PUT/DELETE /admin/levels`
  - _Requirements: REQ-A3_

- [~] 23. Admin Dashboard & Stats
  - `GET /admin/stats/overview` — KPIs tổng quan
  - `GET /admin/stats/daily-active` — DAU chart data
  - `GET /admin/logs/errors` — Error log viewer
  - HTML dashboard tại `/admin` (Jinja2)
  - _Requirements: REQ-A4_

- [~] 24. Admin HTML Templates
  - `app/templates/admin/layout.html` — Base layout
  - `app/templates/admin/dashboard.html` — Stats overview
  - `app/templates/admin/families.html` — Family list
  - `app/templates/admin/master_data.html` — Master data CRUD

### PHASE 8: Frontend Integration

- [~] 25. Kid Dashboard updates
  - Thêm Level badge + Streak counter vào header
  - Tab Avatar Shop
  - Tab Finance (Goals, Savings, Loans)
  - Tab Thinking (Bids, Problems, Reflection)

- [~] 26. Parent Dashboard updates
  - Thêm Finance management section
  - Problem Board creation
  - Wall of Fame section
  - Challenge creation
  - Teen mode controls

- [~] 27. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Mỗi Phase có thể deploy độc lập
- Phase 1 (DB) phải hoàn thành trước tất cả phases khác
- Cron jobs dùng APScheduler (in-process, không cần Redis/Celery)
- Admin Panel dùng separate JWT secret để tách biệt hoàn toàn
- Tất cả thay đổi Coin phải có transaction record (Coin conservation invariant)
