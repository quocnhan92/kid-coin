# Design Document: Ad System — Hệ thống Quảng cáo KidCoin

## Overview

Hệ thống quảng cáo "xương sống" cho KidCoin theo mô hình **Dynamic Configuration**: Admin bật/tắt và gán nội dung cho các slot trong App mà không cần sửa code. Thanh toán thực hiện offline — hệ thống chỉ quản lý **Ad Inventory** (vị trí) và **Creative** (nội dung).

**Ràng buộc:** Server 1GB RAM/1CPU — dùng in-memory cache, ảnh lưu trên Cloudinary/Imgur (chỉ lưu URL), API trả JSON tối giản.

**Triết lý:** "Quảng cáo như không quảng cáo" — ưu tiên dạng Sponsored Challenge tích hợp vào gameplay thay vì banner rác.

---

## Architecture

```mermaid
graph TD
    subgraph "Admin Layer"
        ADMIN_UI[/admin/ads<br/>Jinja2 Dashboard]
        ADMIN_API[Admin Ad API<br/>/admin/ads/*]
    end

    subgraph "Cache Layer"
        CACHE[In-Memory Cache<br/>Dict[slot_key → AdResponse]]
        INVALIDATE[Cache Invalidator<br/>on any admin write]
    end

    subgraph "Client API"
        PUB_API[Public Ad API<br/>GET /api/v1/ads/{slot_key}]
    end

    subgraph "Database"
        SLOTS[(ad_slots)]
        CAMPAIGNS[(ad_campaigns)]
        IMPRESSIONS[(ad_impressions)]
        CLICKS[(ad_clicks)]
    end

    ADMIN_UI --> ADMIN_API
    ADMIN_API --> SLOTS
    ADMIN_API --> CAMPAIGNS
    ADMIN_API --> INVALIDATE
    INVALIDATE --> CACHE
    PUB_API --> CACHE
    CACHE -->|cache miss| SLOTS
    CACHE -->|cache miss| CAMPAIGNS
    PUB_API --> IMPRESSIONS
    PUB_API --> CLICKS
```

**Luồng chính:**
1. Admin tạo/sửa campaign → cache bị invalidate
2. App gọi `GET /api/v1/ads/{slot_key}` → trả từ cache (không query DB)
3. App ghi nhận impression/click → insert async (fire-and-forget)

---

## Ad Slots Định nghĩa

| slot_key | name | Đối tượng | Loại nội dung phù hợp |
|----------|------|-----------|----------------------|
| `HOME_BANNER_TOP` | Banner đầu trang chủ | Cả nhà | Sản phẩm giáo dục, đồ chơi, sữa |
| `HOME_BANNER_BOTTOM` | Banner cuối trang chủ | Cả nhà | Sản phẩm gia đình |
| `REWARD_LIST` | Phần Quà tặng Gợi ý | Trẻ em | Đồ chơi, khu vui chơi (sponsored) |
| `PARENT_ZONE` | Khu vực Phụ huynh | Bố mẹ | Khóa học, bảo hiểm, sản phẩm gia đình |
| `SPLASH_SCREEN` | Màn hình chờ khi mở app | Cả nhà | Thương hiệu lớn (3–5 giây) |
| `SPONSORED_CHALLENGE` | Thử thách tài trợ | Cả nhà | Tích hợp vào gameplay (xem mục 5) |
| `PUSH_NOTIFICATION` | Thông báo đẩy tài trợ | Cả nhà | Khuyến mãi, sự kiện giáo dục |

---

## Data Models

### Bảng: `ad_slots`

```sql
CREATE TABLE ad_slots (
    id          SERIAL PRIMARY KEY,
    slot_key    VARCHAR(50) UNIQUE NOT NULL,  -- 'HOME_BANNER_TOP'
    name        VARCHAR(100) NOT NULL,         -- "Banner đầu trang chủ"
    description VARCHAR(500),                  -- Mô tả vị trí, audience
    platform    VARCHAR(20) DEFAULT 'ALL',     -- 'IOS', 'ANDROID', 'ALL', 'WEB'
    ad_type     VARCHAR(20) DEFAULT 'BANNER',  -- 'BANNER', 'SPLASH', 'NATIVE', 'PUSH'
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `ad_campaigns`

```sql
CREATE TABLE ad_campaigns (
    id          SERIAL PRIMARY KEY,
    slot_id     INTEGER REFERENCES ad_slots(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    image_url   VARCHAR(500),           -- Cloudinary/Imgur URL (không lưu file local)
    target_url  VARCHAR(500),           -- Link khi click (shopee, website...)
    cta_text    VARCHAR(50),            -- "Xem ngay", "Tìm hiểu thêm"
    
    -- Sponsored Challenge fields (nullable, chỉ dùng khi ad_type = NATIVE)
    challenge_title     VARCHAR(200),   -- "Thử thách từ [Brand X]"
    challenge_desc      VARCHAR(500),   -- Mô tả thử thách
    bonus_coins         INTEGER,        -- Coin thưởng khi hoàn thành
    challenge_duration  INTEGER,        -- Số ngày thử thách
    
    -- Scheduling
    start_date  TIMESTAMP NOT NULL,
    end_date    TIMESTAMP NOT NULL,
    priority    INTEGER DEFAULT 0,      -- Cao hơn = ưu tiên hơn khi nhiều campaign cùng slot
    
    -- Status
    is_active   BOOLEAN DEFAULT TRUE,
    
    -- Tracking
    total_impressions   INTEGER DEFAULT 0,
    total_clicks        INTEGER DEFAULT 0,
    
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### Bảng: `ad_impressions` (lightweight tracking)

```sql
CREATE TABLE ad_impressions (
    id              BIGSERIAL PRIMARY KEY,
    campaign_id     INTEGER REFERENCES ad_campaigns(id),
    slot_key        VARCHAR(50) NOT NULL,
    user_id         UUID,               -- Nullable (anonymous)
    family_id       UUID,
    device_type     VARCHAR(20),        -- 'mobile', 'desktop'
    created_at      TIMESTAMP DEFAULT NOW()
);
-- Partition by month để tránh bảng quá lớn
```

### Bảng: `ad_clicks`

```sql
CREATE TABLE ad_clicks (
    id              BIGSERIAL PRIMARY KEY,
    campaign_id     INTEGER REFERENCES ad_campaigns(id),
    impression_id   BIGINT,             -- Liên kết với impression
    user_id         UUID,
    family_id       UUID,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

---

## Cache Strategy

**In-memory cache** dùng Python dict (không cần Redis — tiết kiệm RAM):

```python
# app/core/ad_cache.py
_cache: dict[str, AdCacheEntry] = {}

class AdCacheEntry:
    data: list[AdResponse]   # Danh sách campaigns active cho slot
    cached_at: datetime
    ttl_seconds: int = 300   # 5 phút TTL

def get_cached_ads(slot_key: str) -> list[AdResponse] | None:
    entry = _cache.get(slot_key)
    if entry and (datetime.now() - entry.cached_at).seconds < entry.ttl_seconds:
        return entry.data
    return None  # cache miss

def set_cache(slot_key: str, data: list[AdResponse]) -> None:
    _cache[slot_key] = AdCacheEntry(data=data, cached_at=datetime.now())

def invalidate_cache(slot_key: str | None = None) -> None:
    if slot_key:
        _cache.pop(slot_key, None)
    else:
        _cache.clear()  # Invalidate all khi admin thay đổi
```

**Cache invalidation:** Mỗi khi Admin tạo/sửa/xóa campaign → gọi `invalidate_cache(slot_key)`.

**Cache miss flow:** Query DB → filter `is_active=True AND start_date <= NOW() <= end_date` → sort by priority DESC → set cache → return.

---

## API Design

### Public API (App gọi)

```
GET /api/v1/ads/{slot_key}
    → Trả về campaign active cho slot (từ cache)
    → Không cần auth (anonymous OK)
    → Response: AdResponse JSON

POST /api/v1/ads/{campaign_id}/impression
    → Ghi nhận impression (fire-and-forget BackgroundTask)
    → Body: {user_id?, family_id?, device_type?}

POST /api/v1/ads/{campaign_id}/click
    → Ghi nhận click
    → Body: {user_id?, impression_id?}
```

**AdResponse schema:**
```json
{
  "campaign_id": 1,
  "slot_key": "HOME_BANNER_TOP",
  "title": "Sữa Vinamilk cho bé",
  "image_url": "https://res.cloudinary.com/...",
  "target_url": "https://vinamilk.com.vn",
  "cta_text": "Xem ngay",
  "ad_type": "BANNER",
  "challenge": null
}
```

**Sponsored Challenge response:**
```json
{
  "campaign_id": 5,
  "slot_key": "SPONSORED_CHALLENGE",
  "title": "Thử thách từ Sữa Cô Gái Hà Lan",
  "image_url": "https://...",
  "ad_type": "NATIVE",
  "challenge": {
    "title": "Con uống đủ sữa 7 ngày liên tiếp",
    "description": "Uống đủ 1 ly sữa mỗi ngày trong 7 ngày để nhận thưởng!",
    "bonus_coins": 20,
    "duration_days": 7
  }
}
```

### Admin API

```
GET    /admin/ads/slots              -- Danh sách slots
PUT    /admin/ads/slots/{id}/toggle  -- Bật/tắt slot
GET    /admin/ads/campaigns          -- Danh sách campaigns (filter by slot, status)
POST   /admin/ads/campaigns          -- Tạo campaign mới
PUT    /admin/ads/campaigns/{id}     -- Sửa campaign
DELETE /admin/ads/campaigns/{id}     -- Xóa campaign
GET    /admin/ads/campaigns/{id}/preview  -- Preview campaign
GET    /admin/ads/stats              -- CTR, impressions, clicks per campaign
GET    /admin/ads                    -- HTML Dashboard
```

---

## Admin Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  📢 QUẢN LÝ QUẢNG CÁO                                   │
│                                                         │
│  📍 AD SLOTS                                            │
│  ┌─────────────────────────────────────────────────┐   │
│  │ HOME_BANNER_TOP    "Banner đầu trang"  [ON ✅]  │   │
│  │ REWARD_LIST        "Quà tài trợ"       [ON ✅]  │   │
│  │ PARENT_ZONE        "Khu phụ huynh"     [OFF ⭕] │   │
│  │ SPLASH_SCREEN      "Màn hình chờ"      [ON ✅]  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  📋 CAMPAIGNS ĐANG CHẠY                                 │
│  ┌─────────────────────────────────────────────────┐   │
│  │ [Ảnh] Sữa Vinamilk | HOME_BANNER_TOP            │   │
│  │        Impressions: 1,234 | Clicks: 45 | CTR: 3.6%│ │
│  │        01/04 → 30/04  Priority: 10  [Sửa][Xóa]  │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ [Ảnh] Thử thách Cô Gái Hà Lan | SPONSORED       │   │
│  │        Impressions: 890 | Clicks: 120 | CTR: 13.5%│ │
│  │        05/04 → 20/04  Priority: 5   [Sửa][Xóa]  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [+ Tạo Campaign Mới]                                   │
└─────────────────────────────────────────────────────────┘
```

**Campaign Form:**
```
┌─────────────────────────────────────────────────────────┐
│  TẠO CAMPAIGN MỚI                                       │
│                                                         │
│  Slot:        [HOME_BANNER_TOP ▼]                       │
│  Tiêu đề:     [Sữa Vinamilk cho bé                    ] │
│  URL ảnh:     [https://cloudinary.com/...             ] │
│               ⚠️ Dùng Cloudinary/Imgur, max 200KB       │
│  Link đích:   [https://vinamilk.com.vn                ] │
│  CTA:         [Xem ngay                               ] │
│  Từ ngày:     [01/04/2026] Đến ngày: [30/04/2026]       │
│  Ưu tiên:     [10]                                      │
│                                                         │
│  ── Sponsored Challenge (tùy chọn) ──                   │
│  Tiêu đề:     [Thử thách uống sữa 7 ngày             ] │
│  Mô tả:       [Uống đủ 1 ly sữa mỗi ngày...         ] │
│  Thưởng Coin: [20]  Số ngày: [7]                        │
│                                                         │
│  [Preview] [Lưu]                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Sponsored Challenge Integration

Đây là tính năng "quảng cáo như không quảng cáo" — tích hợp brand vào gameplay:

**Flow:**
1. Admin tạo campaign với `ad_type = NATIVE` và điền `challenge_*` fields
2. App gọi `GET /api/v1/ads/SPONSORED_CHALLENGE` → nhận challenge data
3. App hiển thị challenge card trong Kid Dashboard (giống Family Challenge nhưng có brand logo)
4. Kid tham gia → check-in hàng ngày → nhận `bonus_coins` khi hoàn thành
5. Completion event → ghi nhận conversion (click)

**Bảng `sponsored_challenge_progress`** (lightweight):
```sql
CREATE TABLE sponsored_challenge_progress (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id     INTEGER REFERENCES ad_campaigns(id),
    kid_id          UUID REFERENCES users(id),
    start_date      DATE NOT NULL,
    checkin_count   INTEGER DEFAULT 0,
    completed       BOOLEAN DEFAULT FALSE,
    coins_awarded   INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, kid_id)
);
```

---

## Performance Optimizations

**1. Cache-first serving:**
- Mọi `GET /api/v1/ads/*` đều đọc từ `_cache` dict trước
- DB chỉ được query khi cache miss hoặc TTL hết (5 phút)
- Ước tính: 1000 requests/ngày → chỉ ~288 DB queries/ngày (mỗi 5 phút 1 lần)

**2. Async impression tracking:**
- `POST /impression` dùng FastAPI `BackgroundTask` — không block response
- Batch update `total_impressions` counter mỗi 5 phút thay vì mỗi request

**3. Image hosting:**
- Không lưu ảnh trên server — chỉ lưu URL (Cloudinary free: 25GB storage, 25GB bandwidth/tháng)
- Giới hạn upload: 200KB per image trong Admin form validation

**4. Impression table cleanup:**
- Cron job monthly: xóa impressions > 90 ngày (chỉ giữ aggregated stats trong campaigns)

---

## Stats & Reporting

**Per campaign metrics:**
- `total_impressions`: tổng lượt hiển thị
- `total_clicks`: tổng lượt click
- `CTR = total_clicks / total_impressions * 100`

**Admin stats endpoint:**
```json
GET /admin/ads/stats
{
  "campaigns": [
    {
      "id": 1,
      "title": "Sữa Vinamilk",
      "slot_key": "HOME_BANNER_TOP",
      "impressions": 1234,
      "clicks": 45,
      "ctr": 3.65,
      "status": "ACTIVE",
      "days_remaining": 15
    }
  ],
  "total_active_campaigns": 3,
  "total_impressions_today": 456
}
```

---

## Correctness Properties

1. **Cache consistency:** Sau khi Admin sửa campaign, lần gọi API tiếp theo (sau cache miss) SHALL trả về data mới.
2. **Slot isolation:** `GET /api/v1/ads/{slot_key}` SHALL chỉ trả về campaigns thuộc slot đó.
3. **Date filtering:** Campaigns với `end_date < NOW()` hoặc `start_date > NOW()` SHALL không được trả về.
4. **Inactive slot:** WHEN `ad_slots.is_active = FALSE`, `GET /api/v1/ads/{slot_key}` SHALL trả về empty list.
5. **Priority ordering:** Khi nhiều campaigns cùng slot, SHALL trả về campaign có `priority` cao nhất.
6. **Image URL only:** Server SHALL không lưu binary image data — chỉ lưu URL string.
7. **Impression async:** Impression tracking SHALL NOT block ad response (BackgroundTask).
8. **Admin auth:** Tất cả `/admin/ads/*` endpoints SHALL require admin JWT.
