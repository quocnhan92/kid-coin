# Implementation Plan: Ad Placement Intelligence

## Overview

Pure computation layer trên analytics data hiện có. Không cần bảng DB mới. Thứ tự: slot definitions → scoring engine → report service → API router → HTML template → wiring.

## Tasks

- [ ] 1. Định nghĩa Ad Slots và Data Models
  - Tạo `app/services/ad_placement.py`
  - Định nghĩa `AD_SLOTS` constant: list 10 `AdSlotDefinition` với `slot_id`, `page_path`, `position_name`, `visibility_factor`
  - Định nghĩa Pydantic models: `SubScores`, `AdFormat`, `PeakHour`, `SlotReport`, `AdPlacementReport`
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Implement AdDataCollector
  - Trong `app/services/ad_placement.py`, implement `AdDataCollector` class
  - `collect_page_metrics(db, page_path, days)`: query `web_page_views` COUNT, AVG(duration_ms) cho path
  - `collect_session_metrics(db, days)`: query `web_sessions` AVG(page_count), COUNT sessions với page_count=1 (bounce)
  - `collect_audience_metrics(db, page_path, days)`: JOIN `web_page_views` với `users` để tính parent_ratio
  - `collect_peak_hours(db, page_path, days)`: GROUP BY EXTRACT(HOUR FROM created_at), ORDER BY count DESC
  - `collect_device_metrics(db, page_path, days)`: query `web_page_views` GROUP BY device_type
  - `collect_retention_metrics(db)`: query WAU/MAU từ `web_page_views` (COALESCE user_id, device_id)
  - Tất cả methods phải handle empty result (return zero-value objects, không raise exception)
  - _Requirements: 2.9, 7.4, 7.5_

- [ ] 3. Implement AdScoringEngine
  - Trong `app/services/ad_placement.py`, implement `AdScoringEngine` class
  - `compute_traffic_score(page_metrics, max_views)`: công thức `min(100, views/max_views*100)`
  - `compute_dwell_score(session_metrics)`: công thức `min(100, avg_duration_sec/300*100)`
  - `compute_engagement_score(session_metrics)`: weighted combination pages/session + inverse bounce rate
  - `compute_audience_score(audience_metrics)`: `parent_ratio * 100`
  - `compute_peak_score(peak_hours)`: `min(100, top3_traffic/total*300)`
  - `compute_device_score(device_metrics)`: `mobile_ratio * 100`
  - `compute_return_score(retention)`: `min(100, wau/mau*100)` với zero-division guard
  - `compute_composite(scores)`: weighted sum với trọng số cố định
  - Tất cả methods trả về float trong [0, 100]
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3_

  - [ ]* 3.1 Viết property test cho ScoringEngine
    - **Property 1: Score bounds** — Validates: Requirements 2.8, 3.2
    - Dùng `hypothesis` với `st.floats(min_value=0)` cho input metrics
    - Assert tất cả sub-scores và composite_score trong [0, 100]
    - **Property 8: Weighted sum** — Validates: Requirement 3.1
    - Assert `compute_composite(scores)` == exact weighted sum

- [ ] 4. Implement FormatRecommender và CPM Estimator
  - Trong `app/services/ad_placement.py`
  - `recommend_format(device_score, composite_score, slot_id)`: implement decision matrix + slot overrides cho `kid_bottom_nav` và `parent_sidebar`
  - `estimate_cpm(audience_score)`: trả về tuple `(min_cpm, max_cpm)` theo 3 tiers
  - `estimate_impressions(page_metrics, visibility_factor)`: `round(views_last_7d/7 * visibility_factor)`
  - `determine_confidence(data_points)`: trả về "LOW"/"MEDIUM"/"HIGH"
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4_

  - [ ]* 4.1 Viết unit tests cho FormatRecommender
    - Test 5 cases của decision matrix (composite × device combinations)
    - Test slot overrides: `kid_bottom_nav` luôn → Banner 320x50
    - Test slot overrides: `parent_sidebar` luôn → Rectangle 300x250

  - [ ]* 4.2 Viết unit tests cho CPM và confidence
    - Test 3 CPM tiers với boundary values (39, 40, 69, 70)
    - Test confidence boundaries (99, 100, 1000, 1001)
    - **Property 4: CPM range validity** — Assert `cpm[0] <= cpm[1]` và cả hai > 0

- [ ] 5. Implement AdReportService
  - Trong `app/services/ad_placement.py`, implement `AdReportService`
  - `generate_report(db, days=30)`: orchestrate DataCollector → ScoringEngine → FormatRecommender → assemble SlotReport × 10 → sort → top_3 → summary_text
  - `generate_slot_report(db, slot_id, days=30)`: single slot report
  - `generate_recommendation_text(slot, composite, format, impressions, cpm, confidence)`: Vietnamese text
  - `export_markdown(report)`: format report thành Markdown string
  - Đảm bảo không có DB write operations
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4_

  - [ ]* 5.1 Viết integration test cho generate_report
    - Seed mock `web_page_views` data, gọi `generate_report`, verify:
      - Đúng 10 SlotReport (Property 5)
      - `top_3_slots` sorted descending (Property 2)
      - Không có DB writes (Property 6)
    - Test với empty DB → all scores = 0, confidence = LOW

- [ ] 6. Checkpoint — Kiểm tra scoring và report logic
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Tạo Analytics Ad Report API Router
  - Tạo `app/api/v1/ad_report.py`
  - `GET /ad-report?days=30`: validate days [7,90] (422 nếu ngoài range), gọi `generate_report`, trả về JSON
  - `GET /ad-report/{slot_id}?days=30`: validate slot_id (404 nếu không tồn tại), gọi `generate_slot_report`
  - `GET /ad-report/export?days=30`: gọi `export_markdown`, trả về `Response(content=md, media_type="text/markdown")`
  - Auth dependency: require PARENT role (401/403)
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 7.1 Viết property test cho API auth
    - **Property 7: Auth isolation** — Validates: Requirement 9.6
    - Test mỗi endpoint: no JWT → 401, KID role → 403, PARENT → 200

- [ ] 8. Tạo HTML Dashboard Template
  - Tạo `app/templates/analytics_ad_report.html`
  - Section "Top 3 vị trí tốt nhất": cards với score badge và confidence badge
  - Section "Chi tiết từng vị trí": expandable cards với sub-score progress bars (Tailwind)
  - Hiển thị: format gợi ý, impressions/ngày, CPM range, peak hours, audience breakdown
  - Nút "Xuất Markdown" → link đến export endpoint
  - Jinja2 auto-escaping cho tất cả dynamic content
  - _Requirements: 10.1, 10.2, 10.3, 10.5_

- [ ] 9. Wiring — Đăng ký router vào main.py
  - Thêm `from app.api.v1 import ad_report as ad_report_router`
  - Thêm `app.include_router(ad_report_router.router, prefix="/api/v1/analytics", tags=["Ad Intelligence"])`
  - Thêm route `GET /analytics/ad-report` → HTML dashboard handler (với auth redirect)
  - _Requirements: 9.1, 10.1, 10.4_

- [ ] 10. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Verify không có DB writes trong generate_report (Property 6)
  - Verify tất cả scores trong [0, 100] (Property 1)

## Notes

- Tasks `*` là optional (tests), có thể bỏ qua cho MVP
- Không cần Alembic migration — không có bảng mới
- Feature này phụ thuộc vào `web-analytics-tracking` spec đã được implement trước
- GeoIP data (country/city) có thể dùng để refine audience_score sau này
- CPM estimates là ước tính tham khảo, không phải cam kết thực tế
