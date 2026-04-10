# Requirements Document

## Introduction

Web Analytics Tracking là tính năng theo dõi lượt truy cập nội bộ cho hệ thống KidCoin (FastAPI + PostgreSQL). Hệ thống ghi nhận toàn bộ page view và API call thông qua middleware bất đồng bộ (fire-and-forget), lưu trữ vào PostgreSQL, và cung cấp dashboard HTML cho PARENT role để xem thống kê chi tiết (page views, sessions, DAU/WAU/MAU, device breakdown, error rates, performance). Thiết kế không phụ thuộc external service và không làm chậm response time của ứng dụng.

---

## Glossary

- **AnalyticsMiddleware**: Starlette BaseHTTPMiddleware mới, wrap RequestContextMiddleware hiện có, intercept mọi request/response để thu thập analytics event.
- **PageViewService**: Service xử lý logic ghi nhận event, session resolution, UA parsing, geo lookup, và upsert aggregated stats.
- **AnalyticsReportService**: Service query và aggregate data từ PostgreSQL để phục vụ dashboard.
- **WebPageView**: SQLAlchemy model, bảng raw event log ghi nhận từng lượt request.
- **WebSession**: SQLAlchemy model, bảng theo dõi session người dùng với window 30 phút.
- **WebDailyStat**: SQLAlchemy model, bảng pre-aggregated stats theo ngày và path.
- **BackgroundTask**: FastAPI/Starlette BackgroundTasks — cơ chế fire-and-forget để chạy analytics sau khi response đã được trả về client.
- **Session**: Một phiên truy cập liên tục của một device, kết thúc sau 30 phút không có activity.
- **Device_ID**: Giá trị từ header `X-Device-ID`, dùng để nhận diện thiết bị.
- **PARENT**: Role người dùng trong hệ thống KidCoin, có quyền xem analytics dashboard.
- **DAU**: Daily Active Users — số lượng unique visitor trong ngày hôm nay.
- **WAU**: Weekly Active Users — số lượng unique visitor trong 7 ngày qua.
- **MAU**: Monthly Active Users — số lượng unique visitor trong 30 ngày qua.
- **Bounce Rate**: Tỷ lệ phần trăm session chỉ có 1 page view.
- **Skip_Paths**: Tập hợp các path không được ghi nhận analytics: `/static/*`, `/favicon.ico`, `/health`.
- **GeoIPResolver**: Component tra cứu country/city từ IP address (optional, best-effort).
- **UserAgentParser**: Component parse User-Agent string thành `{device_type, os_name, browser}`.

---

## Requirements

### Requirement 1: Analytics Middleware — Thu thập event bất đồng bộ

**User Story:** As a system operator, I want every HTTP request to be tracked automatically without impacting response time, so that I can collect analytics data transparently.

#### Acceptance Criteria

1. THE AnalyticsMiddleware SHALL intercept every HTTP request and response passing through the FastAPI application.
2. WHEN a request path starts with `/static/`, equals `/favicon.ico`, or equals `/health`, THE AnalyticsMiddleware SHALL skip analytics tracking for that request.
3. WHEN a request is processed, THE AnalyticsMiddleware SHALL measure `duration_ms` as the elapsed time from request receipt to response completion.
4. WHEN a response is ready to be returned to the client, THE AnalyticsMiddleware SHALL schedule analytics recording as a BackgroundTask without waiting for it to complete.
5. IF the BackgroundTask raises an exception during analytics recording, THEN THE AnalyticsMiddleware SHALL catch the exception, log a warning, and ensure the original response is still returned to the client unmodified.
6. THE AnalyticsMiddleware SHALL read the `X-Device-ID` header from each request to identify the device.
7. THE AnalyticsMiddleware SHALL decode the JWT from the `access_token` cookie to extract `user_id` when present.
8. WHEN a request path starts with `/api/`, THE AnalyticsMiddleware SHALL classify the event as an API call (`is_page_view = False`); otherwise THE AnalyticsMiddleware SHALL classify it as a page view (`is_page_view = True`).

---

### Requirement 2: PageViewService — Ghi nhận raw event

**User Story:** As a system operator, I want each tracked request to be stored as a raw event record, so that I have a complete audit trail for analytics queries.

#### Acceptance Criteria

1. WHEN `record_event` is called, THE PageViewService SHALL insert exactly one record into the `web_page_views` table.
2. THE PageViewService SHALL store `path`, `method`, `status_code`, `duration_ms`, `user_id`, `device_id`, `session_id`, `ip_address`, `user_agent`, `referer`, `device_type`, `os_name`, `browser`, `country`, `city`, and `is_page_view` in each `WebPageView` record.
3. IF `record_event` raises any exception, THEN THE PageViewService SHALL catch the exception, log the error, and return without propagating the exception to the caller.
4. WHEN `record_event` completes successfully, THE PageViewService SHALL upsert one `WebDailyStat` record for the specific path and one `WebDailyStat` record for the site-wide path `"/"`.

---

### Requirement 3: UserAgentParser — Phân tích User-Agent

**User Story:** As a system operator, I want device, OS, and browser information extracted from User-Agent strings, so that I can analyze traffic by device type.

#### Acceptance Criteria

1. WHEN `parse_user_agent` is called with a User-Agent string, THE UserAgentParser SHALL return a result containing `device_type`, `os_name`, and `browser` fields.
2. WHEN a User-Agent string identifies a mobile device, THE UserAgentParser SHALL set `device_type` to `"mobile"`.
3. WHEN a User-Agent string identifies a tablet device, THE UserAgentParser SHALL set `device_type` to `"tablet"`.
4. WHEN a User-Agent string identifies a desktop device, THE UserAgentParser SHALL set `device_type` to `"desktop"`.
5. IF a User-Agent string is malformed or unrecognizable, THEN THE UserAgentParser SHALL set `device_type`, `os_name`, and `browser` to `null` without raising an exception.

---

### Requirement 4: GeoIPResolver — Tra cứu địa lý

**User Story:** As a system operator, I want IP addresses resolved to country and city, so that I can analyze geographic distribution of users.

#### Acceptance Criteria

1. WHEN `resolve_geo` is called with a valid public IP address, THE GeoIPResolver SHALL return `country` (ISO 3166-1 alpha-2 code) and `city` fields.
2. IF `resolve_geo` fails for any reason (private IP, IPv6 not supported, DB unavailable), THEN THE GeoIPResolver SHALL return `{country: null, city: null}` without raising an exception.
3. THE GeoIPResolver SHALL NOT expose raw IP addresses through any analytics API response or dashboard display.

---

### Requirement 5: SessionResolver — Quản lý session

**User Story:** As a system operator, I want user visits grouped into sessions, so that I can measure engagement metrics like session duration and page count.

#### Acceptance Criteria

1. WHEN `resolve_session` is called with a `device_id` or `user_id`, THE SessionResolver SHALL search for an active `WebSession` where `last_seen_at > NOW() - 30 minutes` and `is_active = True`.
2. WHEN an active session is found, THE SessionResolver SHALL update `last_seen_at` to the current time, increment `page_count` by 1, update `exit_path`, and return the existing `session_id`.
3. WHEN no active session is found, THE SessionResolver SHALL create a new `WebSession` record with a new UUID, set `started_at` and `last_seen_at` to the current time, set `page_count` to 1, and return the new `session_id`.
4. WHEN both `device_id` and `user_id` are `null`, THE SessionResolver SHALL return a new UUID without creating a `WebSession` record.
5. WHEN two requests arrive with different `device_id` values, THE SessionResolver SHALL assign them different `session_id` values.
6. WHEN two requests arrive with the same `device_id` within 30 minutes, THE SessionResolver SHALL assign them the same `session_id`.

---

### Requirement 6: WebDailyStat — Aggregated statistics

**User Story:** As a system operator, I want pre-aggregated daily statistics, so that the analytics dashboard can query efficiently without scanning the full raw event table.

#### Acceptance Criteria

1. WHEN upserting a `WebDailyStat` record, THE PageViewService SHALL use PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` to ensure no duplicate row exists for the same `(stat_date, path)` combination.
2. WHEN a new page view is recorded, THE PageViewService SHALL increment `page_views` by 1 in the corresponding `WebDailyStat` row.
3. WHEN a request with `status_code >= 400` is recorded, THE PageViewService SHALL increment `error_count` by 1 in the corresponding `WebDailyStat` row.
4. THE PageViewService SHALL update `avg_duration_ms` in `WebDailyStat` using a rolling average calculation.

---

### Requirement 7: AnalyticsReportService — Báo cáo tổng quan

**User Story:** As a parent, I want to see an overview of site traffic, so that I can understand how the family uses the KidCoin application.

#### Acceptance Criteria

1. WHEN `get_overview` is called with a `days` parameter, THE AnalyticsReportService SHALL return `total_page_views`, `unique_visitors`, `total_sessions`, `avg_session_duration_ms`, `bounce_rate`, `top_pages`, and `date_range` for the specified date range.
2. WHEN `get_overview` is called, THE AnalyticsReportService SHALL set `date_range` to `[today - days, today]`.
3. THE AnalyticsReportService SHALL accept `days` values in the range [1, 365].
4. WHEN `get_overview` is called, THE AnalyticsReportService SHALL return all numeric fields with values >= 0.

---

### Requirement 8: AnalyticsReportService — Báo cáo chi tiết

**User Story:** As a parent, I want detailed breakdowns of page traffic, device usage, user journeys, retention, errors, and API endpoints, so that I can monitor application health and usage patterns.

#### Acceptance Criteria

1. WHEN `get_page_stats` is called, THE AnalyticsReportService SHALL return a list of `PageStat` objects, each containing `path`, `views`, and `avg_duration_ms` for the specified date range.
2. WHEN `get_device_breakdown` is called, THE AnalyticsReportService SHALL return counts grouped by `device_type`, `os_name`, and `browser` for the specified date range.
3. WHEN `get_user_journey` is called, THE AnalyticsReportService SHALL return a list of `JourneyStep` objects representing the sequence of pages visited within sessions.
4. WHEN `get_retention` is called, THE AnalyticsReportService SHALL return `dau`, `wau`, `mau`, `dau_wau_ratio`, and `wau_mau_ratio`.
5. WHEN `get_retention` is called, THE AnalyticsReportService SHALL ensure `dau <= wau` and `wau <= mau`.
6. WHEN `get_retention` is called and `wau = 0`, THE AnalyticsReportService SHALL return `dau_wau_ratio = 0` without raising a division-by-zero error.
7. WHEN `get_retention` is called and `mau = 0`, THE AnalyticsReportService SHALL return `wau_mau_ratio = 0` without raising a division-by-zero error.
8. WHEN `get_error_rates` is called, THE AnalyticsReportService SHALL return a list of `ErrorStat` objects grouped by `status_code` with counts for the specified date range.
9. WHEN `get_top_endpoints` is called, THE AnalyticsReportService SHALL return a list of `EndpointStat` objects sorted by call count descending for the specified date range.

---

### Requirement 9: Analytics API Endpoints

**User Story:** As a parent, I want to access analytics data through REST API endpoints, so that the dashboard can fetch and display statistics dynamically.

#### Acceptance Criteria

1. THE Analytics_Router SHALL expose the following endpoints: `GET /api/v1/analytics/overview`, `GET /api/v1/analytics/pages`, `GET /api/v1/analytics/devices`, `GET /api/v1/analytics/journey`, `GET /api/v1/analytics/retention`, `GET /api/v1/analytics/errors`, `GET /api/v1/analytics/endpoints`.
2. WHEN a request to any `/api/v1/analytics/*` endpoint is received without a valid JWT cookie, THE Analytics_Router SHALL return HTTP 401.
3. WHEN a request to any `/api/v1/analytics/*` endpoint is received with a valid JWT but the user role is not PARENT, THE Analytics_Router SHALL return HTTP 403.
4. WHEN a valid PARENT user requests `GET /api/v1/analytics/overview`, THE Analytics_Router SHALL return a JSON response conforming to the `OverviewStats` schema.
5. WHEN a valid PARENT user requests any analytics endpoint with a `days` query parameter outside [1, 365], THE Analytics_Router SHALL return HTTP 422.

---

### Requirement 10: Analytics Dashboard HTML

**User Story:** As a parent, I want a web dashboard at `/analytics`, so that I can view all analytics reports in a single visual interface.

#### Acceptance Criteria

1. THE Analytics_Router SHALL serve an HTML dashboard at `GET /analytics` rendered with Jinja2.
2. WHEN a request to `GET /analytics` is received without a valid JWT cookie, THE Analytics_Router SHALL redirect to `/login`.
3. WHEN a request to `GET /analytics` is received with a valid JWT but the user role is not PARENT, THE Analytics_Router SHALL redirect to `/login`.
4. WHEN a valid PARENT user accesses `GET /analytics`, THE Analytics_Router SHALL render the dashboard with overview stats, page stats, device breakdown, retention metrics, error rates, and top endpoints.
5. WHEN rendering the analytics dashboard, THE Analytics_Router SHALL use Jinja2 auto-escaping for all user-generated content including `user_agent` strings.

---

### Requirement 11: Database Models và Migration

**User Story:** As a developer, I want the three analytics tables created via Alembic migration, so that the schema is version-controlled and reproducible.

#### Acceptance Criteria

1. THE System SHALL create an Alembic migration that adds tables `web_page_views`, `web_sessions`, and `web_daily_stats` to the PostgreSQL database.
2. THE `web_page_views` table SHALL have composite indexes on `(path, created_at)`, `(user_id, created_at)`, `(status_code, created_at)`, and a single-column index on `session_id`.
3. THE `web_sessions` table SHALL have a composite index on `(device_id, last_seen_at, is_active)` to support efficient session lookup.
4. THE `web_daily_stats` table SHALL have a unique constraint on `(stat_date, path)` to enforce the upsert invariant.
5. THE `WebPageView` model SHALL enforce that `status_code` is in the range [100, 599] via a check constraint.
6. THE `WebPageView` model SHALL enforce that `duration_ms >= 0` via a check constraint when the value is not null.

---

### Requirement 12: Dependency Integration

**User Story:** As a developer, I want the analytics feature to integrate cleanly with existing dependencies and add only the necessary new libraries, so that the project remains maintainable.

#### Acceptance Criteria

1. THE System SHALL add `user-agents==2.2.0` to `requirements.txt` for User-Agent parsing.
2. WHERE GeoIP lookup is enabled, THE System SHALL use `geoip2` library with a local MaxMind GeoLite2 database file.
3. WHERE GeoIP lookup is disabled or the database file is unavailable, THE System SHALL fall back to returning `{country: null, city: null}` without error.
4. THE AnalyticsMiddleware SHALL reuse the existing `RequestContextMiddleware` by wrapping it, without modifying the existing middleware code.
