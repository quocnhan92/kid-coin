# Implementation Plan: Web Analytics Tracking

## Overview

Tích hợp hệ thống analytics nội bộ vào KidCoin (FastAPI + PostgreSQL). Triển khai theo thứ tự: models → migration → services → middleware → API router → dashboard template → wiring vào main.py.

## Tasks

- [ ] 1. Thêm dependency và tạo SQLAlchemy models
  - [ ] 1.1 Thêm `user-agents==2.2.0` vào `requirements.txt`
    - Append dòng `user-agents==2.2.0` vào file `requirements.txt` hiện có
    - _Requirements: 12.1_

  - [ ] 1.2 Tạo file `app/models/analytics.py` với 3 SQLAlchemy models
    - Implement `WebPageView` với đầy đủ columns: `id`, `path`, `method`, `status_code`, `duration_ms`, `user_id`, `device_id`, `session_id`, `ip_address`, `user_agent`, `referer`, `device_type`, `os_name`, `browser`, `country`, `city`, `is_page_view`, `created_at`
    - Thêm `CheckConstraint` cho `status_code` trong range [100, 599] và `duration_ms >= 0`
    - Thêm composite indexes: `(path, created_at)`, `(user_id, created_at)`, `(status_code, created_at)`, single index `session_id`
    - Implement `WebSession` với columns: `id`, `device_id`, `user_id`, `started_at`, `last_seen_at`, `page_count`, `entry_path`, `exit_path`, `country`, `device_type`, `is_active`
    - Thêm composite index `(device_id, last_seen_at, is_active)` cho `WebSession`
    - Implement `WebDailyStat` với columns: `id`, `stat_date`, `path`, `page_views`, `unique_visitors`, `sessions`, `avg_duration_ms`, `error_count`, `updated_at`
    - Thêm `UniqueConstraint("stat_date", "path")` cho `WebDailyStat`
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [ ] 1.3 Import `WebPageView`, `WebSession`, `WebDailyStat` vào `app/models/__init__.py`
    - Đảm bảo models được đăng ký với `Base.metadata` khi `app.models` được import
    - _Requirements: 11.1_

- [ ] 2. Tạo Alembic migration cho 3 bảng analytics
  - [ ] 2.1 Tạo file `alembic/versions/002_analytics_tables.py`
    - `down_revision = '001'`, `revision = '002'`
    - `upgrade()`: tạo bảng `web_page_views` với tất cả columns, check constraints, và indexes
    - `upgrade()`: tạo bảng `web_sessions` với tất cả columns và composite index
    - `upgrade()`: tạo bảng `web_daily_stats` với tất cả columns và unique constraint
    - `downgrade()`: drop 3 bảng theo thứ tự ngược
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [ ] 3. Implement PageViewService
  - [ ] 3.1 Tạo file `app/services/analytics.py` với `PageViewService`
    - Định nghĩa dataclass/TypedDict `PageViewEvent` chứa các fields: `path`, `method`, `status_code`, `duration_ms`, `user_id`, `device_id`, `ip_address`, `user_agent`, `referer`
    - Implement `parse_user_agent(ua_string: str) -> dict` dùng thư viện `user_agents`: trả về `{device_type, os_name, browser}`, handle mọi exception, trả về null values nếu lỗi
    - Implement `resolve_geo(ip: str) -> dict`: trả về `{country, city}`, best-effort (null nếu lỗi hoặc private IP)
    - Implement `resolve_session(db, device_id, user_id) -> str`: tìm session active trong 30 phút, update nếu có, tạo mới nếu không; trả về UUID string
    - Implement `record_event(db, event: PageViewEvent) -> None`: orchestrate parse_user_agent → resolve_geo → resolve_session → INSERT WebPageView → UPSERT WebDailyStat cho path cụ thể và `"/"`, catch-all exception với logging
    - Dùng PostgreSQL `INSERT ... ON CONFLICT DO UPDATE` (SQLAlchemy `insert().on_conflict_do_update()`) cho WebDailyStat upsert
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 6.1, 6.2, 6.3, 6.4_

  - [ ]* 3.2 Viết property test cho `parse_user_agent`
    - **Property 8: UserAgentParser always returns required structure**
    - **Validates: Requirements 3.1, 3.5**
    - Dùng `hypothesis` với `st.text()` để generate arbitrary UA strings
    - Assert kết quả luôn có keys `device_type`, `os_name`, `browser` và không raise exception

  - [ ]* 3.3 Viết property test cho `resolve_geo`
    - **Property 9: GeoIPResolver never raises exceptions**
    - **Validates: Requirement 4.2**
    - Dùng `hypothesis` với `st.text()` để generate arbitrary IP strings
    - Assert kết quả luôn là dict với keys `country`, `city` và không raise exception

  - [ ]* 3.4 Viết unit tests cho `resolve_session`
    - Test session creation khi không có session active
    - Test session reuse khi `last_seen_at` trong 30 phút (Property 11)
    - Test session isolation với 2 device_id khác nhau (Property 12)
    - Test trả về UUID mới khi cả `device_id` và `user_id` đều null
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [ ]* 3.5 Viết property test cho `record_event` — upsert idempotency
    - **Property 13: WebDailyStat upsert is idempotent**
    - **Validates: Requirements 6.1, 6.2**
    - Gọi `record_event` N lần với cùng path, assert `web_daily_stats` chỉ có 1 row và `page_views = N`

  - [ ]* 3.6 Viết property test cho `record_event` — error count
    - **Property 14: Error count increments only for status_code >= 400**
    - **Validates: Requirement 6.3**
    - Dùng `hypothesis` với `st.integers(min_value=100, max_value=599)` cho status_code
    - Assert `error_count` chỉ tăng khi `status_code >= 400`

- [ ] 4. Checkpoint — Kiểm tra PageViewService
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement AnalyticsReportService
  - [ ] 5.1 Tạo file `app/services/analytics_report.py` với `AnalyticsReportService`
    - Định nghĩa các Pydantic response schemas: `OverviewStats`, `PageStat`, `DeviceBreakdown`, `JourneyStep`, `RetentionStats`, `ErrorStat`, `EndpointStat`
    - Implement `get_overview(db, days: int = 7) -> OverviewStats`: query `web_daily_stats` cho date range, tính `total_page_views`, `unique_visitors`, `total_sessions`, `avg_session_duration_ms`, `bounce_rate`, `top_pages`, `date_range`
    - Implement `get_page_stats(db, days: int) -> list[PageStat]`: query `web_daily_stats` group by path
    - Implement `get_device_breakdown(db, days: int) -> DeviceBreakdown`: query `web_page_views` group by `device_type`, `os_name`, `browser`
    - Implement `get_user_journey(db, days: int) -> list[JourneyStep]`: query `web_page_views` join `web_sessions` để lấy sequence of pages
    - Implement `get_retention(db) -> RetentionStats`: tính DAU/WAU/MAU dùng `COALESCE(user_id::text, device_id)`, handle division-by-zero cho ratios
    - Implement `get_error_rates(db, days: int) -> list[ErrorStat]`: query `web_page_views` group by `status_code` where `status_code >= 400`
    - Implement `get_top_endpoints(db, days: int) -> list[EndpointStat]`: query `web_page_views` where `is_page_view = False`, group by path, order by count DESC
    - Tất cả numeric fields phải >= 0; không expose `ip_address` trong bất kỳ response nào
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 4.3_

  - [ ]* 5.2 Viết property test cho `get_retention`
    - **Property 15: DAU ≤ WAU ≤ MAU invariant**
    - **Validates: Requirements 8.5, 8.6, 8.7**
    - Seed mock `WebPageView` records với arbitrary dates, assert `dau <= wau <= mau`

  - [ ]* 5.3 Viết property test cho `get_overview`
    - **Property 16: Overview numeric fields are non-negative**
    - **Validates: Requirement 7.4**
    - Dùng `hypothesis` với `st.integers(min_value=1, max_value=365)` cho `days`
    - Assert tất cả numeric fields trong `OverviewStats` >= 0

  - [ ]* 5.4 Viết property test cho `get_top_endpoints`
    - **Property 17: Top endpoints are sorted by call count descending**
    - **Validates: Requirement 8.9**
    - Seed mock data, assert list trả về có `call_count[i] >= call_count[i+1]` với mọi i

- [ ] 6. Implement AnalyticsMiddleware
  - [ ] 6.1 Tạo file `app/core/analytics_middleware.py` với `AnalyticsMiddleware`
    - Kế thừa `BaseHTTPMiddleware` từ Starlette
    - Định nghĩa `SKIP_PATHS = {"/favicon.ico", "/health"}` và prefix `/static/`
    - `dispatch()`: đo `duration_ms`, đọc `X-Device-ID` header, decode JWT từ `access_token` cookie để lấy `user_id`
    - Classify `is_page_view` dựa trên path prefix `/api/`
    - Sau khi nhận response: tạo `PageViewEvent` và schedule `BackgroundTask` với `record_event`
    - Wrap toàn bộ analytics logic trong try/except để đảm bảo response luôn được trả về
    - Tạo DB session riêng cho BackgroundTask (không dùng chung với request session)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 12.4_

  - [ ]* 6.2 Viết unit tests cho `AnalyticsMiddleware.dispatch`
    - **Property 1: Skip paths never produce analytics records** — Validates: Requirement 1.2
    - **Property 2: Analytics never delays response** — Validates: Requirements 1.4, 1.5
    - **Property 3: Page view classification is path-based** — Validates: Requirement 1.8
    - **Property 4: Device ID and user ID are propagated correctly** — Validates: Requirements 1.6, 1.7
    - Dùng `httpx.AsyncClient` với `TestClient` để test middleware behavior
    - Mock `PageViewService.record_event` để verify nó được gọi với đúng arguments
    - Test skip paths: `/static/test.js`, `/favicon.ico`, `/health` → không gọi `record_event`
    - Test `/api/v1/quests` → `is_page_view = False`; test `/parent` → `is_page_view = True`

- [ ] 7. Tạo Analytics API Router
  - [ ] 7.1 Tạo file `app/api/v1/analytics.py` với 7 JSON endpoints + 1 HTML endpoint
    - Định nghĩa `router = APIRouter()` (không có prefix, sẽ được set trong main.py)
    - Implement auth dependency: verify JWT cookie, check `role == PARENT`, raise 401/403 tương ứng
    - `GET /overview?days=7`: validate `days` trong [1, 365] (422 nếu ngoài range), gọi `AnalyticsReportService.get_overview`
    - `GET /pages?days=7`: gọi `get_page_stats`
    - `GET /devices?days=7`: gọi `get_device_breakdown`
    - `GET /journey?days=7`: gọi `get_user_journey`
    - `GET /retention`: gọi `get_retention`
    - `GET /errors?days=7`: gọi `get_error_rates`
    - `GET /endpoints?days=7`: gọi `get_top_endpoints`
    - `GET /` (HTML): verify PARENT role, redirect `/login` nếu không hợp lệ, render `analytics.html` với tất cả stats
    - Không expose `ip_address` trong bất kỳ response nào
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5, 4.3_

  - [ ]* 7.2 Viết property test cho analytics API auth
    - **Property 18: Analytics endpoints require PARENT role**
    - **Validates: Requirements 9.2, 9.3**
    - Test mỗi endpoint với: không có JWT → 401; JWT với role KID → 403; JWT với role PARENT → 200

- [ ] 8. Tạo analytics dashboard template
  - [ ] 8.1 Tạo file `app/templates/analytics.html`
    - Template Jinja2 kế thừa style từ `parent_dashboard.html` hiện có
    - Hiển thị overview stats: total page views, unique visitors, sessions, bounce rate
    - Hiển thị retention metrics: DAU, WAU, MAU và ratios
    - Hiển thị top pages table: path, views, avg duration
    - Hiển thị device breakdown: mobile/desktop/tablet counts
    - Hiển thị error rates: status code distribution
    - Hiển thị top API endpoints table
    - Sử dụng Jinja2 auto-escaping (`{{ value }}` không dùng `| safe`) cho tất cả user-generated content
    - Thêm `?days=` selector (7/30/90 ngày) với form GET
    - _Requirements: 10.1, 10.4, 10.5_

  - [ ]* 8.2 Viết unit test cho dashboard XSS escaping
    - **Property 19: Dashboard escapes user-generated content**
    - **Validates: Requirement 10.5**
    - Seed `WebPageView` với `user_agent = "<script>alert(1)</script>"`
    - Request `GET /analytics`, assert response HTML chứa `&lt;script&gt;` không phải `<script>`

- [ ] 9. Wiring — Đăng ký middleware và router vào main.py
  - [ ] 9.1 Import và đăng ký `AnalyticsMiddleware` trong `main.py`
    - Thêm `from app.core.analytics_middleware import AnalyticsMiddleware`
    - Thêm `app.add_middleware(AnalyticsMiddleware)` sau dòng `app.add_middleware(RequestContextMiddleware)`
    - _Requirements: 12.4_

  - [ ] 9.2 Import và đăng ký analytics router trong `main.py`
    - Thêm `from app.api.v1 import analytics as analytics_router`
    - Thêm `app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["Analytics"])` cho JSON endpoints
    - Thêm route `GET /analytics` trỏ đến HTML dashboard handler trong analytics router
    - _Requirements: 9.1, 10.1_

  - [ ] 9.3 Import analytics models trong `alembic/env.py`
    - Thêm `from app.models.analytics import WebPageView, WebSession, WebDailyStat  # noqa: F401` vào `alembic/env.py`
    - Đảm bảo `app/models/__init__.py` export 3 models mới để `import app.models` đã có trong env.py tự động pick up
    - _Requirements: 11.1_

- [ ] 10. Final checkpoint — Đảm bảo tích hợp hoàn chỉnh
  - Ensure all tests pass, ask the user if questions arise.
  - Verify `record_event` không raise exception ra ngoài (Property 6)
  - Verify `WebDailyStat` upsert không tạo duplicate rows (Property 13)
  - Verify `ip_address` không xuất hiện trong bất kỳ API response nào (Property 10)

## Notes

- Tasks đánh dấu `*` là optional, có thể bỏ qua để triển khai MVP nhanh hơn
- Mỗi task tham chiếu requirements cụ thể để đảm bảo traceability
- Checkpoints ở task 4 và 10 để validate incremental progress
- Property tests dùng thư viện `hypothesis` (đã có trong Python ecosystem, thêm vào dev dependencies nếu chưa có)
- GeoIP lookup là best-effort: nếu không có MaxMind DB file thì `country/city = null`, không lỗi
- BackgroundTask tạo DB session riêng (không share với request) để tránh session conflict
