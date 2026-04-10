# Requirements Document: KidCoin Expansion

## Introduction

Mở rộng KidCoin với 6 nhóm tính năng mới (Gamification, Tài chính, Tư duy, Gắn kết, Teen Mode) và Admin Panel quản trị hệ thống. Tất cả tính năng được thiết kế phù hợp với server 1GB RAM/1CPU.

---

## Nhóm 1: Gamification

### REQ-G1: XP & Level System
1. Hệ thống SHALL tính level hiện tại của user dựa trên `total_earned_score` và bảng `user_levels`.
2. Level SHALL được tính on-the-fly (không lưu trong `users`): `MAX(level) WHERE xp_required <= total_earned_score`.
3. Khi user đạt level mới, hệ thống SHALL gửi notification chúc mừng.
4. Bảng `user_levels` SHALL có ít nhất 10 levels với titles tiếng Việt phù hợp lứa tuổi.

### REQ-G2: Streak System
1. Hệ thống SHALL theo dõi số ngày liên tiếp có task APPROVED trong `user_streaks`.
2. Cron job SHALL chạy lúc 00:05 hàng ngày để cập nhật streak.
3. WHEN streak >= 7 ngày, hệ thống SHALL nhân đôi Coin cho task đầu tiên được APPROVED trong ngày đó.
4. `longest_streak` SHALL luôn >= `current_streak`.
5. WHEN user miss 1 ngày (không có task APPROVED), `current_streak` SHALL reset về 0.

### REQ-G3: Avatar Shop
1. Kid SHALL có thể mua avatar items bằng Coin từ catalog `avatar_items`.
2. WHEN mua item, hệ thống SHALL trừ Coin, insert `user_avatar_items`, tạo transaction type `AVATAR_PURCHASE`.
3. Kid SHALL chỉ mua được item có `min_level <= current_level`.
4. Mỗi item chỉ mua được 1 lần (UNIQUE constraint).
5. Kid SHALL có thể equip/unequip items đã mua.

---

## Nhóm 2: Giáo dục Tài chính

### REQ-F1: Saving Goals (Heo đất)
1. Kid SHALL có thể tạo saving goal với `name`, `target_amount`, `icon_url`, `deadline` (optional).
2. Kid SHALL có thể gửi Coin vào goal: trừ `current_coin`, cộng `current_amount`.
3. WHEN `current_amount >= target_amount`, status SHALL tự động chuyển COMPLETED và trả Coin về wallet.
4. Kid SHALL có thể hủy goal (CANCELLED): Coin được hoàn trả.
5. Dashboard SHALL hiển thị % tiến độ = `current_amount / target_amount * 100`.

### REQ-F2: Savings Account (Gửi kỳ hạn)
1. Parent SHALL có thể tạo savings account cho kid với `principal`, `interest_rate`, `end_date`.
2. `matured_amount = principal * (1 + interest_rate/100)`.
3. Cron job SHALL kiểm tra hàng ngày: WHEN `end_date <= today` AND status=ACTIVE → status=MATURED, cộng `matured_amount` vào wallet.
4. WHEN kid rút sớm (status=ACTIVE), trả `principal * (1 - early_withdraw_penalty/100)`.
5. Tất cả thay đổi Coin SHALL có transaction record.

### REQ-F3: Loan Account (Vay nợ)
1. Parent SHALL có thể tạo loan cho kid: cộng `loan_amount` vào wallet, tạo `loan_accounts`.
2. `total_owed = loan_amount * (1 + interest_rate/100)`.
3. WHEN kid có loan ACTIVE và task được APPROVED, hệ thống SHALL tự động trừ một phần Coin vào `repaid_amount` (tỷ lệ cấu hình per family).
4. WHEN `repaid_amount >= total_owed`, status SHALL chuyển REPAID.
5. Cron job SHALL đánh dấu OVERDUE khi quá `due_date`.

### REQ-F4: Charity Fund (Quỹ sẻ chia)
1. Mỗi family SHALL có 1 `charity_fund`.
2. WHEN task APPROVED, hệ thống SHALL tự động trích `charity_rate`% Coin vào `charity_fund.balance`.
3. `charity_rate` SHALL cấu hình được per family (default 5%, range 0–20%).
4. Kid SHALL có thể tự nguyện donate thêm vào quỹ.
5. Parent SHALL có thể xem lịch sử donations.

---

## Nhóm 3: Tư duy Logic

### REQ-T1: Task Bid (Đề xuất ngược)
1. Kid SHALL có thể tạo bid: `title`, `description`, `proof_image_url`, `proposed_coins`.
2. Parent SHALL có thể ACCEPT (trả `proposed_coins`), REJECT, hoặc COUNTER (đề xuất giá khác).
3. WHEN COUNTER, kid SHALL có thể ACCEPT hoặc REJECT counter offer.
4. WHEN ACCEPT, hệ thống SHALL cộng `final_coins` vào kid wallet và tạo transaction.

### REQ-T2: Problem Board (Bảng tin bài toán)
1. Parent SHALL có thể đăng problem board với `title` (dạng câu hỏi mở), `reward_coins`, `deadline`.
2. Kid SHALL có thể claim solutions (tự chọn cách giải quyết).
3. WHEN tất cả solutions VERIFIED, reward SHALL chia đều cho các kids tham gia.
4. WHEN `deadline` qua mà chưa hoàn thành, status SHALL chuyển EXPIRED.

### REQ-T3: Weekly Reflection (Nhật ký tự phản biện)
1. Cron job SHALL tạo `weekly_reflections` record cho tất cả kids vào Chủ Nhật 20:00.
2. Kid SHALL trả lời 3 câu hỏi cố định trong tuần.
3. WHEN submit, Parent SHALL review và approve để kid nhận `bonus_coins`.
4. Mỗi kid chỉ có 1 reflection per tuần (UNIQUE constraint).

---

## Nhóm 4: Gắn kết

### REQ-S1: Wall of Fame
1. Parent SHALL có thể đăng ảnh + lời khen lên Wall of Fame.
2. Tất cả thành viên gia đình SHALL có thể xem và like posts.
3. Post SHALL liên kết được với task_log cụ thể (optional).

### REQ-S2: Family Challenge
1. Parent SHALL có thể tạo challenge với `title`, `target_count`, `duration_days`, `reward_coins`.
2. Mỗi thành viên SHALL check-in hàng ngày với proof (optional).
3. WHEN thành viên đạt đủ `target_count` check-ins, họ SHALL nhận `reward_coins`.
4. Challenge SHALL tự động EXPIRED khi qua `end_date`.

---

## Nhóm 5: Teen Mode

### REQ-TN1: Teen Contract
1. Teen mode SHALL được bật per user bởi Parent (`is_teen_mode = TRUE`).
2. Parent và teen SHALL có thể tạo contract với milestones và `salary_coins`.
3. Contract SHALL có status DRAFT cho đến khi cả 2 bên đồng ý (signed_at).
4. Teen SHALL check-in hàng ngày/tuần theo contract.
5. WHEN tất cả milestones VERIFIED, `salary_coins` SHALL được trả vào wallet.

### REQ-TN2: Personal Project
1. Parent SHALL có thể tạo personal project cho teen với milestones và budget.
2. Mỗi milestone SHALL có `coins` riêng, được trả khi Parent verify.
3. Teen SHALL upload proof cho từng milestone.

---

## Nhóm 6: Admin Panel

### REQ-A1: Admin Authentication
1. Admin SHALL đăng nhập qua `/admin/auth/login` với username/password.
2. Admin JWT SHALL dùng secret key khác với user JWT.
3. Admin JWT SHALL không dùng được cho user endpoints.

### REQ-A2: Family Management
1. Admin SHALL xem danh sách tất cả families với search/filter.
2. Admin SHALL suspend/unsuspend family (suspended family không thể login).
3. Admin SHALL reset PIN cho family.

### REQ-A3: Master Data Management
1. Admin SHALL CRUD `master_tasks`, `master_rewards`, `avatar_items`, `user_levels`.
2. Tất cả thay đổi master data SHALL được ghi vào audit_logs.

### REQ-A4: System Stats
1. Admin dashboard SHALL hiển thị: tổng families, users, tasks completed hôm nay, active sessions.
2. Admin SHALL xem error logs (audit_logs với status=FAILED).

### REQ-A5: Coin Integrity
1. Mọi thay đổi `current_coin` SHALL có transaction record tương ứng.
2. Admin adjust coins SHALL tạo transaction type `ADMIN_ADJUSTMENT` với audit log.
