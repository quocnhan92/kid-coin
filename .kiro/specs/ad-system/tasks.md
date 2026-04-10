# Implementation Plan: Ad System

## Tasks

- [ ] 1. Database & Models
  - [ ] 1.1 Alembic migration: tạo `ad_slots`, `ad_campaigns`, `ad_impressions`, `ad_clicks`, `sponsored_challenge_progress`
  - [ ] 1.2 SQLAlchemy models trong `app/models/ads.py`: AdSlot, AdCampaign, AdImpression, AdClick, SponsoredChallengeProgress
  - [ ] 1.3 Seed 7 ad slots mặc định vào DB
  - _Requirements: REQ-AD1, REQ-AD2_

- [ ] 2. In-Memory Cache
  - Tạo `app/core/ad_cache.py`: `get_cached_ads()`, `set_cache()`, `invalidate_cache()`
  - TTL 5 phút, dict-based, thread-safe
  - _Requirements: REQ-AD3_

- [ ] 3. Ad Service
  - Tạo `app/services/ad_service.py`
  - `get_active_campaign(db, slot_key)`: cache-first, filter date + is_active, sort by priority
  - `record_impression(db, campaign_id, ...)`: async update counter
  - `record_click(db, campaign_id, ...)`: update counter
  - `join_sponsored_challenge(db, campaign_id, kid_id)`: tạo progress record
  - `checkin_challenge(db, campaign_id, kid_id)`: tăng checkin_count, check completion
  - _Requirements: REQ-AD3, REQ-AD4, REQ-AD5_

- [ ] 4. Public Ad API
  - Tạo `app/api/v1/ads.py`
  - `GET /api/v1/ads/{slot_key}` — cache-first, no auth required
  - `POST /api/v1/ads/{campaign_id}/impression` — BackgroundTask
  - `POST /api/v1/ads/{campaign_id}/click`
  - `POST /api/v1/ads/{campaign_id}/challenge/join` — KID role
  - `POST /api/v1/ads/{campaign_id}/challenge/checkin` — KID role
  - Đăng ký router trong `main.py`
  - _Requirements: REQ-AD3, REQ-AD4, REQ-AD5_

- [ ] 5. Admin Ad API
  - Tạo `app/api/v1/admin_ads.py` (hoặc thêm vào admin router hiện có)
  - `GET /admin/ads/slots` — list slots
  - `PUT /admin/ads/slots/{id}/toggle` — bật/tắt + invalidate cache
  - `GET /admin/ads/campaigns` — list với filter
  - `POST /admin/ads/campaigns` — tạo mới + invalidate cache
  - `PUT /admin/ads/campaigns/{id}` — sửa + invalidate cache
  - `DELETE /admin/ads/campaigns/{id}` — xóa + invalidate cache
  - `GET /admin/ads/stats` — impressions, clicks, CTR
  - _Requirements: REQ-AD2, REQ-AD6_

- [ ] 6. Admin HTML Dashboard
  - Tạo `app/templates/admin/ads.html`
  - Slot list với toggle buttons
  - Campaign list với stats (impressions, clicks, CTR)
  - Campaign create/edit form (image URL input, date pickers, priority)
  - Preview section
  - Route `GET /admin/ads` → render template
  - _Requirements: REQ-AD6_

- [ ] 7. Cron Job: Impression Cleanup
  - Thêm job `ad_impression_cleanup` vào APScheduler (monthly)
  - Xóa `ad_impressions` records > 90 ngày
  - _Requirements: REQ-AD7_

- [ ] 8. Frontend Integration (Kid & Parent Dashboard)
  - Kid Dashboard: hiển thị `HOME_BANNER_TOP` và `SPONSORED_CHALLENGE` card
  - Parent Dashboard: hiển thị `PARENT_ZONE` banner
  - Gọi impression API sau khi render, click API khi user tap
  - _Requirements: REQ-AD3, REQ-AD4_

- [ ] 9. Final checkpoint
  - Verify cache invalidation hoạt động đúng
  - Verify inactive slot trả về empty
  - Verify date filtering đúng
  - Ensure all tests pass

## Notes

- Không cần payment integration — thanh toán offline
- Image luôn là external URL — không upload lên server
- Cache dict không cần Redis — Python dict đủ cho 1GB RAM
- Sponsored Challenge tích hợp với transaction system hiện có (cộng Coin)
