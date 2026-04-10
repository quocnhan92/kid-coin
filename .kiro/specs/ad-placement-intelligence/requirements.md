# Requirements Document: Ad Placement Intelligence

## Introduction

Hệ thống báo cáo gợi ý đặt quảng cáo cho KidCoin, xây dựng trên dữ liệu analytics đã có. Không cần bảng DB mới — đây là pure computation layer phân tích traffic patterns, chấm điểm 10 vị trí quảng cáo tiềm năng trên 3 màn hình (/login, /parent, /kid), và xuất báo cáo actionable cho người vận hành.

## Glossary

- **Ad Slot**: Vị trí tiềm năng để đặt quảng cáo trên một trang cụ thể (ví dụ: `parent_sidebar`).
- **SubScores**: 7 điểm thành phần (traffic, dwell, engagement, audience, peak, device, return_rate), mỗi điểm từ 0–100.
- **CompositeScore**: Điểm tổng hợp có trọng số từ 7 SubScores, từ 0–100.
- **ConfidenceLevel**: Mức độ tin cậy của báo cáo: LOW (<100 data points), MEDIUM (100–1000), HIGH (>1000).
- **CPM**: Cost Per Mille — giá ước tính per 1000 impressions (USD).
- **SlotReport**: Báo cáo đầy đủ cho một Ad Slot.
- **AdPlacementReport**: Tập hợp tất cả SlotReport + top 3 + summary.
- **visibility_factor**: Hệ số hiển thị của slot (top_banner=1.0, sidebar=0.8, between_section=0.6, footer=0.3).

---

## Requirements

### Requirement 1: Ad Slot Definitions

**User Story:** As a system operator, I want a fixed set of ad slots defined for each page, so that the scoring engine has consistent targets to evaluate.

#### Acceptance Criteria

1. THE System SHALL define exactly 10 ad slots: `login_header`, `login_below_form`, `parent_top_banner`, `parent_sidebar`, `parent_between_section`, `parent_footer`, `kid_top_banner`, `kid_between_task`, `kid_shop_section`, `kid_bottom_nav`.
2. EACH slot SHALL have a `page_path` (`/login`, `/parent`, or `/kid`), a `position_name` (human-readable tiếng Việt), and a `visibility_factor` (float in (0, 1]).
3. THE `visibility_factor` SHALL be: top_banner=1.0, sidebar=0.8, between_section=0.6, footer=0.3, bottom_nav=1.0, shop_section=0.7, between_task=0.6, below_form=0.5, header=1.0.

---

### Requirement 2: Scoring Engine — Sub-scores

**User Story:** As a system operator, I want each ad slot scored on 7 dimensions, so that the recommendation is data-driven and explainable.

#### Acceptance Criteria

1. THE ScoringEngine SHALL compute `traffic_score = min(100, page_views_last_N_days / max_views_across_pages * 100)`.
2. THE ScoringEngine SHALL compute `dwell_score = min(100, avg_session_duration_sec / 300 * 100)`.
3. THE ScoringEngine SHALL compute `engagement_score` as a weighted combination of pages-per-session (weight 0.6) and inverse bounce rate (weight 0.4), both normalized to [0, 100].
4. THE ScoringEngine SHALL compute `audience_score = parent_page_views / total_page_views * 100` for the slot's page.
5. THE ScoringEngine SHALL compute `peak_score = min(100, top_3_hours_traffic / total_traffic * 300)`.
6. THE ScoringEngine SHALL compute `device_score = mobile_page_views / total_page_views * 100`.
7. THE ScoringEngine SHALL compute `return_score = min(100, wau / mau * 100)` where `mau > 0`, else 0.
8. ALL sub-scores SHALL be in the range [0, 100] inclusive.
9. IF any input metric is unavailable or zero, THE ScoringEngine SHALL return 0 for that sub-score without raising an exception.

---

### Requirement 3: Scoring Engine — Composite Score

**User Story:** As a system operator, I want a single composite score per slot, so that I can rank slots and identify the best placement opportunities.

#### Acceptance Criteria

1. THE ScoringEngine SHALL compute `composite_score` as the weighted sum: `traffic*0.25 + dwell*0.20 + engagement*0.20 + audience*0.15 + peak*0.10 + device*0.05 + return_rate*0.05`.
2. THE `composite_score` SHALL be in the range [0, 100] inclusive.
3. THE `composite_score` SHALL be deterministic: same input metrics SHALL always produce the same score.

---

### Requirement 4: Ad Format Recommender

**User Story:** As a system operator, I want format recommendations per slot, so that I know which ad sizes and types to use.

#### Acceptance Criteria

1. WHEN `composite_score >= 70` AND `device_score >= 60`, THE FormatRecommender SHALL recommend `Banner 320x50` as primary format.
2. WHEN `composite_score >= 70` AND `device_score < 60`, THE FormatRecommender SHALL recommend `Rectangle 300x250` as primary format.
3. WHEN `40 <= composite_score < 70` AND `device_score >= 60`, THE FormatRecommender SHALL recommend `Banner 320x50` as primary format.
4. WHEN `40 <= composite_score < 70` AND `device_score < 60`, THE FormatRecommender SHALL recommend `Banner 728x90` as primary format.
5. WHEN `composite_score < 40`, THE FormatRecommender SHALL recommend `Text/Native Ad` as primary format.
6. THE slot `kid_bottom_nav` SHALL always recommend `Banner 320x50` regardless of scores.
7. THE slot `parent_sidebar` SHALL always recommend `Rectangle 300x250` regardless of scores.

---

### Requirement 5: CPM Estimation

**User Story:** As a system operator, I want CPM range estimates per slot, so that I can set realistic pricing expectations for advertisers.

#### Acceptance Criteria

1. WHEN `audience_score >= 70`, THE System SHALL return `cpm_range = (3.0, 8.0)`.
2. WHEN `40 <= audience_score < 70`, THE System SHALL return `cpm_range = (1.5, 4.0)`.
3. WHEN `audience_score < 40`, THE System SHALL return `cpm_range = (0.5, 2.0)`.
4. THE `estimated_daily_impressions` SHALL be computed as `round(page_views_last_7d / 7 * visibility_factor)`.
5. THE `cpm_range` SHALL always satisfy `cpm_range[0] <= cpm_range[1]` and both values SHALL be > 0.

---

### Requirement 6: Confidence Level

**User Story:** As a system operator, I want a confidence indicator per slot, so that I know how reliable the recommendations are.

#### Acceptance Criteria

1. WHEN `data_points < 100`, THE System SHALL set `confidence_level = "LOW"`.
2. WHEN `100 <= data_points <= 1000`, THE System SHALL set `confidence_level = "MEDIUM"`.
3. WHEN `data_points > 1000`, THE System SHALL set `confidence_level = "HIGH"`.
4. THE `data_points` SHALL equal the total `web_page_views` count for the slot's page in the analysis period.

---

### Requirement 7: Report Generation

**User Story:** As a system operator, I want a complete ad placement report, so that I have all information needed to make placement decisions.

#### Acceptance Criteria

1. THE `AdReportService.generate_report()` SHALL return an `AdPlacementReport` containing exactly 10 `SlotReport` objects.
2. THE `top_3_slots` field SHALL contain the 3 slot IDs with the highest `composite_score`, sorted descending.
3. THE `summary_text` SHALL be a human-readable Vietnamese summary naming the top slot and its key metrics.
4. THE `generate_report()` SHALL NOT execute any INSERT, UPDATE, or DELETE against the database.
5. WHEN no analytics data exists, THE System SHALL return a report with all scores = 0, confidence = "LOW", and `recommendation_text` indicating no data is available.

---

### Requirement 8: Recommendation Text

**User Story:** As a system operator, I want human-readable Vietnamese recommendations per slot, so that I can share the report with non-technical stakeholders.

#### Acceptance Criteria

1. EACH `SlotReport` SHALL include a `recommendation_text` in Vietnamese.
2. THE `recommendation_text` SHALL include: slot position name, page path, recommended format, estimated impressions/day, CPM range, and confidence note.
3. WHEN `confidence_level = "LOW"`, THE `recommendation_text` SHALL include a warning: "⚠️ chưa đủ dữ liệu, chỉ mang tính tham khảo".
4. WHEN `confidence_level = "MEDIUM"`, THE `recommendation_text` SHALL include a note: "cần thêm dữ liệu để xác nhận".

---

### Requirement 9: API Endpoints

**User Story:** As a system operator, I want REST API endpoints for the ad report, so that I can integrate the data into other tools.

#### Acceptance Criteria

1. THE System SHALL expose `GET /api/v1/analytics/ad-report?days=30` returning JSON `AdPlacementReport`.
2. THE System SHALL expose `GET /api/v1/analytics/ad-report/{slot_id}?days=30` returning JSON `SlotReport`.
3. THE System SHALL expose `GET /api/v1/analytics/ad-report/export?days=30` returning `text/markdown`.
4. WHEN `days` is outside [7, 90], THE System SHALL return HTTP 422.
5. WHEN `slot_id` does not match any defined slot, THE System SHALL return HTTP 404.
6. ALL ad-report endpoints SHALL require a valid JWT cookie with PARENT role; otherwise return HTTP 401 or 403.

---

### Requirement 10: HTML Dashboard

**User Story:** As a parent/operator, I want an HTML dashboard at `/analytics/ad-report`, so that I can view the ad placement report visually.

#### Acceptance Criteria

1. THE System SHALL serve `GET /analytics/ad-report` as a Jinja2 HTML page.
2. THE dashboard SHALL display: top 3 slots with scores, full slot list with sub-score bars, recommended formats, estimated impressions, CPM ranges, and confidence badges.
3. THE dashboard SHALL include a "Xuất Markdown" button linking to the export endpoint.
4. WHEN accessed without a valid PARENT JWT, THE System SHALL redirect to `/login`.
5. THE dashboard SHALL use Jinja2 auto-escaping for all dynamic content.
