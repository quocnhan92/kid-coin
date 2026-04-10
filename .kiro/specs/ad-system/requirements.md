# Requirements Document: Ad System

## Introduction

Hệ thống quảng cáo Dynamic Configuration cho KidCoin. Admin quản lý Ad Slots và Campaigns qua dashboard. App lấy quảng cáo qua API cache-first. Thanh toán offline. Tối ưu cho server 1GB RAM.

---

## Requirements

### REQ-AD1: Ad Slot Management
1. Hệ thống SHALL định nghĩa sẵn 7 slots: `HOME_BANNER_TOP`, `HOME_BANNER_BOTTOM`, `REWARD_LIST`, `PARENT_ZONE`, `SPLASH_SCREEN`, `SPONSORED_CHALLENGE`, `PUSH_NOTIFICATION`.
2. Admin SHALL bật/tắt từng slot ngay lập tức (toggle `is_active`).
3. WHEN slot `is_active = FALSE`, API SHALL trả về empty list cho slot đó.
4. Slot toggle SHALL invalidate cache ngay lập tức.

### REQ-AD2: Campaign Management
1. Admin SHALL tạo campaign với: `slot_id`, `title`, `image_url`, `target_url`, `cta_text`, `start_date`, `end_date`, `priority`.
2. `image_url` SHALL là external URL (Cloudinary/Imgur) — server không lưu binary.
3. Admin SHALL cài đặt `start_date` và `end_date` để campaign tự động hiện/ẩn.
4. WHEN nhiều campaigns cùng slot, hệ thống SHALL trả về campaign có `priority` cao nhất.
5. Admin SHALL preview campaign trước khi publish.
6. Tạo/sửa/xóa campaign SHALL invalidate cache của slot tương ứng.

### REQ-AD3: Public Ad API
1. `GET /api/v1/ads/{slot_key}` SHALL trả về campaign active (không cần auth).
2. API SHALL đọc từ in-memory cache trước khi query DB.
3. Cache TTL SHALL là 5 phút.
4. Response SHALL chỉ chứa: `campaign_id`, `title`, `image_url`, `target_url`, `cta_text`, `ad_type`, `challenge` (nullable).
5. WHEN không có campaign active, API SHALL trả về `{"campaign": null}`.

### REQ-AD4: Impression & Click Tracking
1. App SHALL gọi `POST /api/v1/ads/{campaign_id}/impression` sau khi hiển thị ad.
2. Impression tracking SHALL dùng BackgroundTask (không block response).
3. App SHALL gọi `POST /api/v1/ads/{campaign_id}/click` khi user click.
4. `total_impressions` và `total_clicks` trong `ad_campaigns` SHALL được cập nhật.
5. CTR SHALL được tính: `total_clicks / total_impressions * 100`.

### REQ-AD5: Sponsored Challenge
1. Campaign với `ad_type = NATIVE` SHALL có thêm fields: `challenge_title`, `challenge_desc`, `bonus_coins`, `challenge_duration`.
2. Kid SHALL có thể tham gia sponsored challenge (tạo `sponsored_challenge_progress`).
3. WHEN kid hoàn thành challenge (`checkin_count >= challenge_duration`), hệ thống SHALL cộng `bonus_coins` vào wallet và tạo transaction.
4. Mỗi kid chỉ tham gia 1 lần per campaign (UNIQUE constraint).

### REQ-AD6: Admin Dashboard
1. Admin SHALL xem danh sách tất cả slots với trạng thái active/inactive.
2. Admin SHALL xem danh sách campaigns với filter (slot, status, date range).
3. Admin SHALL xem stats: impressions, clicks, CTR per campaign.
4. Dashboard SHALL tại `/admin/ads` (Jinja2 HTML).
5. Tất cả `/admin/ads/*` SHALL require admin JWT.

### REQ-AD7: Performance
1. Server SHALL không lưu binary image — chỉ lưu URL.
2. Admin form SHALL validate image URL (không validate content, chỉ validate format URL).
3. Impression table SHALL được cleanup: xóa records > 90 ngày (cron job monthly).
4. In-memory cache SHALL không vượt quá 10MB (giới hạn số slots × campaigns).
