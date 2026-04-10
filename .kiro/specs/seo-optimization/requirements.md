# Requirements Document: SEO Optimization

## Introduction

Chuẩn hóa HTML theo tiêu chuẩn SEO để Google index KidCoin sớm nhất. Tập trung vào trang `/login` (trang public duy nhất) với đầy đủ meta tags, structured data, sitemap, robots.txt và performance signals.

---

## Requirements

### REQ-SEO1: Meta Tags cơ bản
1. Trang `/login` SHALL có `<title>` chứa primary keyword "ứng dụng quản lý việc nhà trẻ em".
2. Trang `/login` SHALL có `<meta name="description">` dài 150–160 ký tự chứa ít nhất 3 primary keywords.
3. Trang `/login` SHALL có `<meta name="keywords">` với ít nhất 7 từ khóa liên quan.
4. Tất cả pages SHALL có `<html lang="vi">`.
5. Trang `/login` SHALL có `<meta name="robots" content="index, follow">`.
6. Tất cả authenticated pages (`/parent`, `/kid`, `/admin`, `/analytics`) SHALL có `<meta name="robots" content="noindex, nofollow">`.

### REQ-SEO2: Canonical & Structured URLs
1. Trang `/login` SHALL có `<link rel="canonical" href="https://kidcoin.app/login">`.
2. Canonical URLs SHALL không có trailing slash.
3. Route `GET /` SHALL redirect 301 về `/login` (đã có, cần verify).

### REQ-SEO3: Open Graph & Social
1. Trang `/login` SHALL có đầy đủ OG tags: `og:title`, `og:description`, `og:image`, `og:type`, `og:url`, `og:locale`, `og:site_name`.
2. `og:image` SHALL trỏ đến file 1200×630px tại `/static/og-image.png`.
3. `og:locale` SHALL là `vi_VN`.
4. Trang `/login` SHALL có Twitter Card tags: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`.

### REQ-SEO4: JSON-LD Structured Data
1. Trang `/login` SHALL có JSON-LD schema `SoftwareApplication` với đầy đủ fields: `name`, `applicationCategory`, `description`, `url`, `inLanguage`, `offers`, `featureList`.
2. Trang `/login` SHALL có JSON-LD schema `Organization` với `name`, `url`, `logo`.
3. JSON-LD SHALL pass Google Rich Results Test (valid schema.org).

### REQ-SEO5: Sitemap & Robots
1. `GET /sitemap.xml` SHALL trả về valid XML với Content-Type `application/xml`.
2. Sitemap SHALL chứa URL `/login` với `priority=1.0` và `changefreq=monthly`.
3. `GET /robots.txt` SHALL trả về plain text.
4. `robots.txt` SHALL Allow `/login` và `/static/`.
5. `robots.txt` SHALL Disallow `/parent`, `/kid`, `/admin`, `/api/`, `/analytics`.
6. `robots.txt` SHALL có dòng `Sitemap: https://kidcoin.app/sitemap.xml`.

### REQ-SEO6: PWA & Performance
1. Tất cả pages SHALL có `<meta name="theme-color" content="#3b82f6">`.
2. Trang `/login` SHALL có `<link rel="manifest" href="/static/site.webmanifest">`.
3. `site.webmanifest` SHALL có `name`, `short_name`, `description`, `lang: vi`, `categories`.
4. Trang `/login` SHALL có favicon links: 32×32, 16×16, apple-touch-icon.
5. Trang `/login` SHALL có `<link rel="preconnect">` cho external domains.

### REQ-SEO7: Semantic HTML
1. Trang `/login` SHALL có `<header>`, `<main>`, `<footer>` elements với role attributes.
2. Trang `/login` SHALL có `<h1>` chứa brand name "KidCoin".
3. Trang `/login` SHALL có `<h2>` mô tả value proposition.
4. Form elements SHALL có `<label>` liên kết đúng với `for` attribute.

### REQ-SEO8: Base Template
1. Hệ thống SHALL có `app/templates/base_seo.html` với Jinja2 blocks cho title, description, robots, canonical, og tags.
2. Tất cả templates SHALL extend `base_seo.html` hoặc include SEO head block.
3. Authenticated pages SHALL override `robots` block thành `noindex, nofollow`.
