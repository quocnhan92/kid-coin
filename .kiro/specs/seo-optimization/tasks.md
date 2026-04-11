# Implementation Plan: SEO Optimization

## Tasks

- [x] 1. Tạo base SEO template
  - Tạo `app/templates/base_seo.html` với Jinja2 blocks: title, description, robots, canonical, og_title, og_description, og_image, extra_head, body
  - Include: charset, viewport, theme-color, manifest, favicon links, preconnect
  - _Requirements: REQ-SEO8_

- [x] 2. Cập nhật `login.html` — trang SEO quan trọng nhất
  - Thêm đầy đủ `<title>` với primary keyword
  - Thêm `<meta name="description">` 150–160 ký tự
  - Thêm `<meta name="keywords">` với 7+ từ khóa
  - Thêm `<meta name="robots" content="index, follow">`
  - Thêm `<link rel="canonical" href="https://kidcoin.app/login">`
  - Thêm đầy đủ Open Graph tags (og:title, og:description, og:image, og:type, og:url, og:locale, og:site_name)
  - Thêm Twitter Card tags
  - Thêm JSON-LD SoftwareApplication schema
  - Thêm JSON-LD Organization schema
  - Thêm `<header>`, `<main>`, `<footer>` semantic elements
  - Thêm `<h1>KidCoin</h1>` và `<h2>` value proposition
  - Thêm preconnect links
  - Thêm favicon links
  - Thêm theme-color, manifest, apple-touch-icon
  - _Requirements: REQ-SEO1, REQ-SEO2, REQ-SEO3, REQ-SEO4, REQ-SEO6, REQ-SEO7_

- [x] 3. Cập nhật `parent_dashboard.html` — noindex
  - Thêm `<meta name="robots" content="noindex, nofollow">`
  - Cập nhật `<title>Dashboard Phụ huynh — KidCoin</title>`
  - Thêm `<html lang="vi">`
  - _Requirements: REQ-SEO1.6_

- [x] 4. Cập nhật `kid_dashboard.html` — noindex
  - Thêm `<meta name="robots" content="noindex, nofollow">`
  - Cập nhật `<title>Dashboard Bé — KidCoin</title>`
  - Thêm `<html lang="vi">`
  - _Requirements: REQ-SEO1.6_

- [x] 5. Thêm robots.txt và sitemap.xml routes vào `main.py`
  - `GET /robots.txt` → PlainTextResponse
  - `GET /sitemap.xml` → Response với media_type="application/xml"
  - _Requirements: REQ-SEO5_

- [x] 6. Tạo static SEO assets
  - Tạo `/static/og-image.png` (1200×630px) — ảnh preview khi share lên Zalo/Facebook
  - Tạo `/static/favicon-32x32.png` và `/static/favicon-16x16.png`
  - Tạo `/static/apple-touch-icon.png` (180×180px)
  - Tạo `/static/site.webmanifest` với đầy đủ fields
  - _Requirements: REQ-SEO3.2, REQ-SEO6_

- [x] 7. Cập nhật `index.html` — redirect page
  - Thêm `<meta name="robots" content="noindex">`
  - Thêm `<meta http-equiv="refresh" content="0; url=/login">` (backup redirect)
  - _Requirements: REQ-SEO2.3_

- [x] 8. Final SEO validation
  - Verify `/robots.txt` accessible và đúng format
  - Verify `/sitemap.xml` accessible và valid XML
  - Verify JSON-LD không có syntax errors
  - Verify canonical URL đúng
  - Verify og:image tồn tại

## Notes

- Chỉ `/login` cần `index, follow` — tất cả pages khác `noindex`
- OG image 1200×630px là kích thước chuẩn cho Facebook/Zalo share preview
- JSON-LD đặt trong `<head>`, không phải `<body>`
- `site.webmanifest` giúp Google nhận diện app là PWA → tăng trust signal
- Sau khi deploy, submit sitemap lên Google Search Console
