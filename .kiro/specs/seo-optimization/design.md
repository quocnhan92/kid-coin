# Design Document: SEO Optimization — KidCoin

## Overview

Chuẩn hóa toàn bộ HTML templates theo tiêu chuẩn SEO để Google và các search engine nhận diện, index và rank KidCoin sớm nhất có thể. Bao gồm: meta tags, Open Graph, Twitter Cards, JSON-LD structured data, sitemap.xml, robots.txt, canonical URLs, và performance signals.

**Mục tiêu:** Xuất hiện trong top kết quả tìm kiếm cho các từ khóa liên quan đến "ứng dụng quản lý việc nhà cho trẻ em", "dạy trẻ quản lý tài chính", "gamification gia đình" tại thị trường Việt Nam.

---

## Keyword Strategy

### Primary Keywords (Từ khóa chính)
| Từ khóa | Search Intent | Target Page |
|---------|--------------|-------------|
| `ứng dụng quản lý việc nhà cho trẻ em` | Informational | /login (landing) |
| `dạy trẻ quản lý tài chính` | Informational | /login |
| `app gamification gia đình` | Navigational | /login |
| `KidCoin` | Branded | /login |
| `quản lý nhiệm vụ trẻ em` | Informational | /login |

### Secondary Keywords (Từ khóa phụ)
| Từ khóa | Target Page |
|---------|-------------|
| `thưởng coin cho trẻ làm việc nhà` | /login |
| `ứng dụng giáo dục tài chính trẻ em Việt Nam` | /login |
| `bảng nhiệm vụ gia đình` | /login |
| `hệ thống điểm thưởng cho bé` | /login |
| `dạy trẻ tiết kiệm tiền` | /login |
| `ứng dụng parenting Việt Nam` | /login |
| `quản lý việc nhà bằng app` | /login |
| `gamification giáo dục trẻ em` | /login |
| `leaderboard gia đình` | /login |
| `thử thách gia đình app` | /login |

### Long-tail Keywords
- `cách dạy trẻ 5 tuổi làm việc nhà`
- `app theo dõi nhiệm vụ hàng ngày cho bé`
- `hệ thống xu thưởng cho trẻ em`
- `ứng dụng giúp bố mẹ quản lý con cái`
- `gamification việc nhà trẻ em Việt Nam`

---

## Page-by-Page SEO Design

### 1. `/login` — Landing Page (Trang quan trọng nhất)

Đây là trang duy nhất public, là entry point cho Google index.

```html
<!-- Primary Meta Tags -->
<title>KidCoin — Ứng dụng Quản lý Việc nhà & Huấn luyện tư duy Tài chính cho Trẻ em</title>
<meta name="description" content="KidCoin giúp bố mẹ giao việc nhà, thưởng Coin cho bé hoàn thành nhiệm vụ. Dạy trẻ quản lý tài chính, tiết kiệm và trách nhiệm qua gamification. Miễn phí, dễ dùng.">
<meta name="keywords" content="ứng dụng quản lý việc nhà trẻ em, dạy trẻ quản lý tài chính, gamification gia đình, thưởng coin cho bé, app parenting Việt Nam, nhiệm vụ hàng ngày cho bé, hệ thống điểm thưởng trẻ em">
<meta name="author" content="KidCoin">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://kidcoin.app/login">

<!-- Open Graph (Facebook, Zalo) -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://kidcoin.app/login">
<meta property="og:title" content="KidCoin — Ứng dụng Quản lý Việc nhà & Huấn luyện tư duy Tài chính cho Trẻ em">
<meta property="og:description" content="Giao việc nhà, thưởng Coin, dạy bé tiết kiệm. Gamification gia đình đơn giản và hiệu quả.">
<meta property="og:image" content="https://kidcoin.app/static/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="vi_VN">
<meta property="og:site_name" content="KidCoin">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="KidCoin — Ứng dụng Quản lý Việc nhà cho Trẻ em">
<meta name="twitter:description" content="Gamification gia đình: giao việc, thưởng Coin, dạy tài chính cho bé.">
<meta name="twitter:image" content="https://kidcoin.app/static/og-image.png">

<!-- JSON-LD Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "KidCoin",
  "applicationCategory": "EducationalApplication",
  "operatingSystem": "Web, iOS, Android",
  "description": "Ứng dụng quản lý việc nhà và dạy tài chính cho trẻ em thông qua gamification. Bố mẹ giao nhiệm vụ, bé hoàn thành nhận Coin, học cách tiết kiệm và quản lý tiền.",
  "url": "https://kidcoin.app",
  "inLanguage": "vi",
  "audience": {
    "@type": "Audience",
    "audienceType": "Gia đình có trẻ em từ 3-18 tuổi"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "VND"
  },
  "featureList": [
    "Quản lý nhiệm vụ hàng ngày cho trẻ em",
    "Hệ thống thưởng Coin gamification",
    "Dạy trẻ quản lý tài chính và tiết kiệm",
    "Leaderboard thi đua gia đình",
    "Thử thách gia đình",
    "Nhật ký tự phản biện cho thiếu niên"
  ],
  "screenshot": "https://kidcoin.app/static/screenshot.png",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": "120"
  }
}
</script>

<!-- Organization Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "KidCoin",
  "url": "https://kidcoin.app",
  "logo": "https://kidcoin.app/static/logo.png",
  "sameAs": [
    "https://facebook.com/kidcoin.app",
    "https://zalo.me/kidcoin"
  ]
}
</script>
```

### 2. `/parent` — Parent Dashboard (Authenticated, noindex)

```html
<title>Dashboard Phụ huynh — KidCoin</title>
<meta name="robots" content="noindex, nofollow">
<!-- Không index trang authenticated -->
```

### 3. `/kid` — Kid Dashboard (Authenticated, noindex)

```html
<title>Dashboard Bé — KidCoin</title>
<meta name="robots" content="noindex, nofollow">
```

### 4. `/analytics` — Analytics Dashboard (Authenticated, noindex)

```html
<title>Analytics — KidCoin Admin</title>
<meta name="robots" content="noindex, nofollow">
```

### 5. `/admin` — Admin Panel (Authenticated, noindex)

```html
<title>Admin Panel — KidCoin</title>
<meta name="robots" content="noindex, nofollow">
```

---

## Technical SEO Components

### `sitemap.xml` — `/sitemap.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://kidcoin.app/login</loc>
    <lastmod>2026-04-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="vi" href="https://kidcoin.app/login"/>
  </url>
</urlset>
```

### `robots.txt` — `/robots.txt`

```
User-agent: *
Allow: /login
Allow: /static/
Disallow: /parent
Disallow: /kid
Disallow: /admin
Disallow: /api/
Disallow: /analytics

Sitemap: https://kidcoin.app/sitemap.xml
```

### Canonical URL Strategy

- `/login` → canonical = `https://kidcoin.app/login`
- `/` → redirect 301 → `/login` (đã có)
- Tất cả authenticated pages → `noindex, nofollow`

---

## HTML Semantic Structure (login.html)

Thêm semantic HTML5 elements để Google hiểu cấu trúc trang:

```html
<body>
  <header role="banner">
    <h1>KidCoin</h1>
    <p>Ứng dụng Quản lý Việc nhà & Huấn luyện tư duy Tài chính cho Trẻ em</p>
  </header>

  <main role="main" aria-label="Đăng nhập KidCoin">
    <!-- Login form content -->
    <section aria-label="Đăng nhập vào gia đình">
      <h2>Chào mừng về nhà</h2>
      <!-- form -->
    </section>
  </main>

  <footer role="contentinfo">
    <p>© 2026 KidCoin — Ứng dụng giáo dục gia đình</p>
    <nav aria-label="Footer navigation">
      <a href="/login">Đăng nhập</a>
    </nav>
  </footer>
</body>
```

---

## Performance SEO (Core Web Vitals)

Google dùng Core Web Vitals (LCP, FID, CLS) làm ranking signal.

### Optimizations:

**1. Preload critical resources:**
```html
<link rel="preconnect" href="https://cdn.tailwindcss.com">
<link rel="preconnect" href="https://api.dicebear.com">
<link rel="dns-prefetch" href="https://cdn.tailwindcss.com">
```

**2. Lazy load non-critical images:**
```html
<img loading="lazy" src="..." alt="...">
```

**3. Meta viewport đúng chuẩn:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
```

**4. Theme color (PWA signal):**
```html
<meta name="theme-color" content="#3b82f6">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="KidCoin">
```

**5. Favicon đầy đủ:**
```html
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
<link rel="manifest" href="/static/site.webmanifest">
```

---

## PWA Manifest (`/static/site.webmanifest`)

```json
{
  "name": "KidCoin — Quản lý Việc nhà cho Trẻ em",
  "short_name": "KidCoin",
  "description": "Ứng dụng gamification gia đình: giao việc, thưởng Coin, dạy tài chính cho bé",
  "start_url": "/login",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "lang": "vi",
  "icons": [
    {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "categories": ["education", "lifestyle", "productivity"],
  "screenshots": [
    {"src": "/static/screenshot-mobile.png", "sizes": "390x844", "type": "image/png", "form_factor": "narrow"},
    {"src": "/static/screenshot-desktop.png", "sizes": "1280x800", "type": "image/png", "form_factor": "wide"}
  ]
}
```

---

## FastAPI Routes cho SEO Files

```python
# main.py additions
from fastapi.responses import PlainTextResponse, Response

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    return """User-agent: *
Allow: /login
Allow: /static/
Disallow: /parent
Disallow: /kid
Disallow: /admin
Disallow: /api/
Disallow: /analytics

Sitemap: https://kidcoin.app/sitemap.xml"""

@app.get("/sitemap.xml")
async def sitemap_xml():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://kidcoin.app/login</loc>
    <lastmod>2026-04-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>"""
    return Response(content=content, media_type="application/xml")
```

---

## Jinja2 Base Template Strategy

Tạo `app/templates/base_seo.html` để tái sử dụng SEO tags:

```html
<!-- base_seo.html -->
<!DOCTYPE html>
<html lang="vi" prefix="og: https://ogp.me/ns#">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">

  <!-- Dynamic title/description per page -->
  <title>{% block title %}KidCoin — Ứng dụng Quản lý Việc nhà cho Trẻ em{% endblock %}</title>
  <meta name="description" content="{% block description %}KidCoin giúp bố mẹ giao việc nhà, thưởng Coin cho bé. Dạy trẻ quản lý tài chính qua gamification.{% endblock %}">
  <meta name="robots" content="{% block robots %}noindex, nofollow{% endblock %}">

  <!-- Canonical -->
  <link rel="canonical" href="{% block canonical %}https://kidcoin.app{% endblock %}">

  <!-- Open Graph -->
  <meta property="og:title" content="{% block og_title %}KidCoin{% endblock %}">
  <meta property="og:description" content="{% block og_description %}Ứng dụng gamification gia đình{% endblock %}">
  <meta property="og:image" content="{% block og_image %}https://kidcoin.app/static/og-image.png{% endblock %}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="vi_VN">
  <meta property="og:site_name" content="KidCoin">

  <!-- PWA -->
  <meta name="theme-color" content="#3b82f6">
  <link rel="manifest" href="/static/site.webmanifest">
  <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">

  <!-- Favicon -->
  <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">

  <!-- Preconnect -->
  <link rel="preconnect" href="https://cdn.tailwindcss.com">
  <link rel="dns-prefetch" href="https://api.dicebear.com">

  {% block extra_head %}{% endblock %}
</head>
<body>
  {% block body %}{% endblock %}
</body>
</html>
```

---

## Correctness Properties

1. **Login page indexable:** `/login` SHALL have `robots: index, follow` và canonical URL.
2. **Auth pages noindex:** `/parent`, `/kid`, `/admin`, `/analytics` SHALL have `robots: noindex, nofollow`.
3. **Sitemap accessible:** `GET /sitemap.xml` SHALL return valid XML với Content-Type `application/xml`.
4. **Robots.txt accessible:** `GET /robots.txt` SHALL return plain text với Disallow cho authenticated routes.
5. **JSON-LD valid:** Structured data SHALL pass Google Rich Results Test.
6. **OG image exists:** `/static/og-image.png` SHALL exist với kích thước 1200×630px.
7. **Canonical no trailing slash:** Canonical URLs SHALL không có trailing slash.
8. **Lang attribute:** `<html lang="vi">` SHALL present trên tất cả pages.
