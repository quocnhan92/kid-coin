# Math Blast — Kế hoạch khởi nghiệp solo cho thị trường VN

> Tài liệu đồng hành với `math-blast-v2.md`. Gắn cụ thể với hoàn cảnh **solo founder, 1 server Ubuntu (1 CPU · 1GB RAM · 45GB)**, chiến lược **PA3 = 1 engine + 3 SKU**, và khung pháp lý thuế VN 2026.

---

## Mục lục

0. [Bối cảnh & ràng buộc của founder](#0-bối-cảnh--ràng-buộc-của-founder)
1. [Tóm tắt phân tích thị trường (kế thừa)](#1-tóm-tắt-phân-tích-thị-trường-kế-thừa)
2. [Đánh giá hạ tầng — 1 CPU / 1 GB RAM / 45 GB](#2-đánh-giá-hạ-tầng--1-cpu--1-gb-ram--45-gb)
3. [Lộ trình triển khai PA3 cho cá nhân (12–18 tháng)](#3-lộ-trình-triển-khai-pa3-cho-cá-nhân-12-18-tháng)
4. [Cách đánh giá thị trường low-cost cho solo](#4-cách-đánh-giá-thị-trường-low-cost-cho-solo)
5. [Mô hình thu phí & tối ưu thuế hợp pháp ở VN 2026](#5-mô-hình-thu-phí--tối-ưu-thuế-hợp-pháp-ở-vn-2026)
6. [Mô hình giá theo nhịp thực tế](#6-mô-hình-giá-theo-nhịp-thực-tế)
7. [Ngân sách 12 tháng cho solo (lean)](#7-ngân-sách-12-tháng-cho-solo-lean)
8. [Quyết định go/no-go theo gate](#8-quyết-định-gono-go-theo-gate)
9. [Phụ lục — stack code mẫu cho 1GB RAM](#9-phụ-lục--stack-code-mẫu-cho-1gb-ram)

---

## 0. Bối cảnh & ràng buộc của founder

| Mục | Hiện trạng |
| --- | --- |
| Đội ngũ | 1 người (full-stack solo) |
| Hạ tầng có sẵn | 1 VPS Ubuntu — 1 CPU, 1 GB RAM, 45 GB disk |
| Ngân sách năm 1 | Tự đầu tư, mục tiêu giữ < 30tr VND/năm |
| Mục tiêu thuế | Doanh thu năm 1–2 dưới ngưỡng miễn thuế VN 2026 |
| Mô hình mong muốn | PA3 — 1 engine + 3 SKU (Flappy / Candy / Arcade) |
| Mức rủi ro chấp nhận | Thấp — không vay vốn, không quit job nếu chưa có MRR |

**Hệ quả thiết kế:**

- Mọi quyết định kỹ thuật phải fit 1 GB RAM trước khi bàn upgrade.
- Mọi quyết định doanh thu phải fit ngưỡng miễn thuế VN 2026 trong năm 1.
- Mọi quyết định content phải reuse manifest §5.A & §5.B trong `math-blast-v2.md`, không build mới.
- Validation đi trước thiết kế chi tiết — pivot rẻ hơn build.

---

## 1. Tóm tắt phân tích thị trường (kế thừa)

> Phần này chỉ trích yếu tố **đầu vào quyết định** cho solo founder. Bản đầy đủ ở canvas `math-blast-market-strategy.canvas.tsx` (TAM/SAM/SOM, persona đầy đủ, đối thủ).

### 1.1 Các con số nền cần nhớ

- **EdTech VN 2024**: ~$3,64 tỷ doanh thu, K-12 chiếm 81,5% (~$2,97 tỷ).
- **CAGR**: 12,3–12,7%/năm → ~$4 tỷ K-12 năm 2026.
- **Học sinh tiểu học VN**: ~9 triệu (Lớp 1–5).
- **ViOlympic 2025–2026**: 1,05 triệu thí sinh tham gia, 32.303 giải.
- **Học thêm Toán Tiểu học**: 120–150K VND/buổi phổ thông, 250K+ trung tâm cao cấp.
- **Benchmark Monkey**: 15 triệu user toàn cầu, doanh thu subscription tăng 40%/năm.

### 1.2 PA3 nhắc lại — 1 engine, 3 SKU

| SKU | Mô hình | Vai trò |
| --- | --- | --- |
| **Flappy** (60s sprint) | Free + ads rewarded | Acquisition viral, đáy phễu |
| **Candy 300** (learning map) | Subscription B2C | Lõi giữ chân + doanh thu |
| **Arcade Class** (B2B/B2T) | License giáo viên / trường / trung tâm | Doanh thu cao, phòng thủ B2B |

Cùng dùng: `skill_id`, `learning_events`, `skill_mastery_agg`, content pack `vn_gdpt2018_*`.
Khác biệt: client UI, kênh phân phối, model thanh toán.

### 1.3 Phân khúc ưu tiên cho solo năm 1

| Persona | Quy mô VN | Tại sao ưu tiên / không ưu tiên năm 1 |
| --- | --- | --- |
| **P1 · Phụ huynh đô thị Lớp 1–3** | ~2,5tr hộ | Ưu tiên: anxiety cao, willingness-to-pay cao, dễ tiếp cận qua Facebook nhóm |
| **P3 · Trẻ 6–11 tự chơi** | ~9tr trẻ | Ưu tiên: kênh viral free, không cần bán |
| **P5 · Trung tâm dạy thêm** | hàng nghìn TT | Ưu tiên trung: ARPU cao nhưng cần demo + sales effort |
| **P2 · Phụ huynh Lớp 4–5 luyện ViOlympic** | ~1,2tr hộ | Hoãn: cần content L4–L5 đầy đủ, chi phí build lớn |
| **P4 · Giáo viên công lập** | 360K GV | Hoãn: cần dashboard lớp, license trường — chu kỳ bán dài |
| **P6 · Trường tiểu học** | 14.500 trường | Hoãn: B2B sale 6–9 tháng, không phù hợp solo |
| **P7 · Việt kiều** | ~500K trẻ | Hoãn: niche, marketing khó với solo |

**Kết luận solo năm 1**: chỉ tập trung **P1 + P3**. P5 mở thử khi có 5–10 phụ huynh ủng hộ giới thiệu trung tâm họ biết.

---

## 2. Đánh giá hạ tầng — 1 CPU / 1 GB RAM / 45 GB

### 2.1 Server này thực sự gánh được bao nhiêu user?

| Chỉ số | Ước lượng thực tế |
| --- | --- |
| RAM khả dụng cho app | ~600–700 MB sau OS + Nginx + monitoring |
| Tĩnh: HTML/CSS/JS qua Nginx | 1.000–3.000 req/s, gần như miễn phí RAM |
| API Python (FastAPI, 1 worker) | 50–150 req/s tuỳ payload |
| API Node (Fastify, 1 worker) | 80–200 req/s |
| WebSocket đồng thời | ~300–500 connection (mỗi 1–2 MB RAM) |
| SQLite WAL — đọc đồng thời | ~500 reader/s |
| SQLite WAL — ghi đồng thời | ~50–80 write/s |
| Concurrent active users (active = đang gửi event) | ~50–100 |
| **DAU lý thuyết** | **300–800** (với pattern phiên ngắn 60s + 5 phút) |

**Diễn giải cho Math Blast:**

- Một phiên **Flappy 60s** sinh ~30–60 events. Ở 800 DAU, tổng event/ngày ~40.000 → ~0,5 event/s trung bình; peak giờ vàng (19h–21h) ~3 event/s.
- Một màn **Candy** sinh ~10–15 events. Ở 800 DAU x 2 màn/ngày = ~20.000 events/ngày, peak ~2 event/s.
- **Tổng tải peak** ở 800 DAU ≈ 5–8 req/s. Server 1 GB RAM thoải mái xử lý.

→ **Trần lý thuyết: server hiện tại gánh tới ~800–1.000 DAU trước khi cần upgrade.** Đủ cho cả P0 + P1 + một phần P2 trong lộ trình §3. Cần upgrade khi: vượt 1.000 DAU, mở leaderboard public, hoặc thêm AI/ML inference.

### 2.2 Stack lean đề xuất

| Layer | Lựa chọn | Lý do |
| --- | --- | --- |
| OS | Ubuntu 24.04 LTS | Sẵn có |
| Reverse proxy + TLS | **Caddy** (không phải Nginx) | Auto HTTPS, config 5 dòng, RAM ~30 MB |
| Backend | **FastAPI + Uvicorn 1 worker** hoặc **Fastify (Node 20)** | 1 worker đủ tải dự kiến; chọn ngôn ngữ founder thạo |
| DB | **SQLite + WAL mode** | Zero ops, 1 file, backup `.db` qua rclone; đủ cho 100K rows mỗi bảng |
| Cache | **In-process LRU + ETag** | Không cần Redis ở quy mô này |
| Static assets | **Cloudflare Pages (free)** hoặc **R2** | Offload bandwidth khỏi VPS; CDN VN nhanh |
| DNS + Tunnel | **Cloudflare Tunnel (free)** | Không lộ IP, miễn phí TLS, auto reconnect |
| Email transactional | **Resend free 3.000/tháng** hoặc **Brevo 300/ngày** | Đủ năm 1 |
| Push notification | **Web Push API native** | Không phí, không SDK |
| Analytics | **Umami self-hosted** (~80 MB RAM) hoặc Plausible Cloud free | GDPR-friendly, không cần cookie banner |
| Error tracking | **Sentry free 5K events/tháng** | Đủ MVP |
| Backup | **Litestream** SQLite → R2 hoặc Backblaze B2 | Replicate liên tục, RPO < 1 phút |

**RAM budget cụ thể (1 GB):**

```
OS + kernel        ~150 MB
Caddy              ~30 MB
FastAPI 1 worker   ~120 MB (hoặc Node Fastify ~100 MB)
SQLite cache       ~64 MB
Umami              ~80 MB
Litestream         ~40 MB
Buffer + spike     ~200 MB
─────────────────
Tổng dự kiến      ~684 MB / 1024 MB → còn ~340 MB margin an toàn
```

### 2.3 Phân vùng workload trên 1 server (đến hết P2)

```
[Cloudflare CDN/Pages]  ──>  static SPA + assets (offload 80% traffic)
            │
            ▼
[Cloudflare Tunnel]  ──>  Caddy:443  ──>  FastAPI/Fastify:8000  ──>  SQLite (file)
                                                                       │
                                                                       └── Litestream ──> R2/B2 (backup)
```

- Mọi static (HTML, JS, sprite chim, audio) đẩy lên Cloudflare → server chỉ phục vụ API.
- Litestream chạy nền, replicate WAL frame mỗi giây — mất server cũng restore < 5 phút.
- Caddy + Tunnel: không phải mở port 80/443 ra Internet, ẩn IP gốc.

### 2.4 Đường nâng cấp khi vượt 1.000 DAU

| Mức tải | Action | Chi phí ước (VND/tháng) |
| --- | --- | --- |
| < 300 DAU | Server hiện tại | 0 (đã có) |
| 300–1.000 DAU | Tối ưu SQLite, bật WAL, batch writes | 0 |
| 1.000–3.000 DAU | Upgrade VPS lên 2 CPU / 4 GB | 200–400K |
| 3.000–10.000 DAU | Tách DB sang Postgres managed (Supabase/Neon free → paid) | 400K–1tr |
| 10.000+ DAU | Chia worker, queue (RabbitMQ/Redis), CDN edge cache, multi-region | 2tr+ |

**Quy tắc**: chỉ upgrade khi **đã vượt 80% capacity 7 ngày liên tiếp**, không upgrade phòng xa.

---

## 3. Lộ trình triển khai PA3 cho cá nhân (12–18 tháng)

> Mỗi giai đoạn có **mục tiêu định lượng**, **tài nguyên cần**, **gate điều kiện sang giai đoạn kế**. Solo founder phải dừng lại ở mỗi gate và quyết go/no-go.

### 3.1 P0 — Validation (Tháng 0–2): zero code, zero VND

**Mục tiêu**: chứng minh có **nhu cầu thực** trước khi viết dòng code v2 nào.

**Hành động cốt lõi:**

1. Lập 1 **landing page tĩnh** (HTML/CSS, deploy Cloudflare Pages free) giới thiệu Math Blast 3 SKU + form đăng ký quan tâm + cam kết sản phẩm.
2. Mở **Math Blast v1 hiện tại** (đã có ở `/game/math-blast`) cho công khai trên server hiện tại — dùng làm "demo sống" gắn vào landing.
3. Tham gia **20 nhóm Facebook phụ huynh tiểu học** (mẫu: "Phụ huynh Lớp 1 KNTT", "Mẹ và bé 6–10 tuổi", "Toán Tiểu học Hà Nội/TPHCM"...). Quan sát 1 tuần, post chia sẻ 2 tuần (không bán hàng).
4. Phỏng vấn **30 phụ huynh** (Zalo/voice 15–20 phút mỗi cuộc) hỏi: hiện đang dùng gì cho Toán con mình, đau chỗ nào nhất, sẵn lòng chi bao nhiêu/tháng cho app, đặc điểm app lý tưởng.
5. Phỏng vấn **5 giáo viên Tiểu học** (qua nhóm GV) hỏi: dùng tool gì giao bài, đau chỗ nào, ai mua license trường.
6. Đăng **3 video TikTok thử nghiệm** quay trẻ con bạn bè chơi v1 — đo viral coefficient (view, share, save).

**Tài nguyên:**

- Server hiện tại (đã có).
- Domain VN .vn (~750K/năm) hoặc .com (~250K/năm) — chọn .com nếu chưa chắc thương hiệu.
- Cloudflare account (free).
- Thời gian: ~80 giờ founder trong 8 tuần.

**Gate sang P1** — phải đạt **TẤT CẢ**:

- [ ] ≥ 100 sign-up từ landing page.
- [ ] ≥ 30 phụ huynh phỏng vấn xong + ≥ 50% nói "đang trả tiền cho học thêm/app Toán".
- [ ] ≥ 30% phụ huynh phỏng vấn nói "sẵn lòng trả ≥ 99K/tháng nếu sản phẩm tốt".
- [ ] ≥ 1 video TikTok đạt > 10K view organic.
- [ ] Founder vẫn còn động lực (đây là gate quan trọng nhất ai cũng quên).

**No-go**: nếu < 60 sign-up sau 2 tháng, hoặc tỉ lệ "sẵn lòng trả" < 15% → **pivot** ý tưởng (đổi môn, đổi đối tượng) thay vì lao vào build.

### 3.2 P1 — MVP vertical slice (Tháng 2–5): Flappy T1–T2 + Candy World 1

**Mục tiêu**: ra **sản phẩm chơi được** với 1 phần nhỏ content, free hoàn toàn, đo retention thật.

**Phạm vi build:**

- **Engine lõi**:
  - DB schema §7 ở mức tối thiểu: `learning_profiles`, `learning_sessions`, `learning_events`, `skill_units`, `skill_mastery_agg`, `idempotency_keys`.
  - API §8 ở mức tối thiểu: `bootstrap`, `events:batch`, `sessions/start|end`.
  - Auth: parent email + magic link (Resend), trẻ chơi qua profile của parent.
- **Flappy** chỉ Tier T1 + T2 (Lớp 1–2): 2 tier × 6–8 skill = 12–16 skill_id (đã có manifest §5.B.15).
- **Candy** chỉ World 1 (L001–L054, Lớp 1) — 9 chương, 54 màn. Bỏ World 2–5 hoàn toàn ở P1.
- **Arcade** chưa làm — hoãn sang P3.
- **Parent dashboard tối giản**: 1 trang web hiển thị streak, mastery 5 skill yếu nhất, đề xuất ngày mai.

**Hành động đi kèm:**

- Triển khai stack §2.2 trên server hiện tại.
- Mời **30–50 phụ huynh từ P0** vào beta closed (qua Zalo group riêng).
- Cập nhật build mỗi tuần, gửi changelog Zalo.
- Đo: D1, D7, D30 retention; phiên/ngày; phụ huynh có vào dashboard không.

**Tài nguyên:**

- Server hiện tại + Cloudflare free + Resend free.
- Sách giáo khoa "Kết nối tri thức với cuộc sống" Lớp 1 — 1 bộ (~150K) làm tham chiếu.
- Một KOL phụ huynh nhỏ (vài K follower) đổi đầu game free vĩnh viễn lấy 1 video review.
- Thời gian: ~300 giờ founder trong 12 tuần.
- Tổng chi tiền mặt: < 3 triệu VND.

**Gate sang P2** — phải đạt:

- [ ] **D7 retention ≥ 25%** (toàn bộ user, không chỉ KOL).
- [ ] **D30 retention ≥ 12%**.
- [ ] ≥ 30 phụ huynh active (vào dashboard ≥ 1 lần/tuần) trong 30 ngày liên tiếp.
- [ ] ≥ 5 phụ huynh **chủ động hỏi**: "Khi nào bán?" hoặc "Tôi có thể trả tiền không?".
- [ ] Server vẫn ổn định (uptime ≥ 99% theo Uptimerobot free).

**No-go**: nếu D7 < 15% — chứng tỏ sản phẩm chưa "kéo" được — quay lại P0.5 phỏng vấn lại, đừng vội thu phí.

### 3.3 P2 — Soft launch + Monetize (Tháng 5–9)

**Mục tiêu**: bắt đầu **thu phí thật** từ P1 user, validate willingness-to-pay, đạt **MRR ≥ 5tr VND/tháng** với doanh thu năm < 100tr (an toàn dưới ngưỡng thuế kể cả khi luật áp dụng cũ).

**Phạm vi build:**

- Mở rộng Candy World 2 (L055–L108, Lớp 2) — thêm 54 màn, có thể dùng AI generator + người duyệt thay vì soạn tay từng câu.
- Mở Tier T3 (Lớp 3) Flappy — cửu chương là pool khổng lồ.
- Thêm **paywall mềm**: cho free 30 màn đầu (đến L030), từ L031 trở đi cần subscribe.
- Tích hợp **VietQR + MoMo** (xem §5).
- Parent dashboard có **báo cáo hàng tuần qua Zalo**: gửi ảnh PNG render từ template.

**Marketing:**

- Mở Facebook page + Zalo OA, đăng 3 bài/tuần (tip Toán + tiến bộ user thật).
- Hợp tác 3–5 **nano-KOL phụ huynh Toán** (5K–30K follower) — đổi tài khoản Family lifetime + 200K tiền mặt/post lấy 1 video review thật.
- Chạy thử Facebook Ads với ngân sách 1–2 triệu/tháng — chỉ để học CAC, không scale.
- Mở **referral**: phụ huynh giới thiệu 1 phụ huynh trả phí → cả 2 được +30 ngày free.

**Tài nguyên:**

- Server hiện tại (đủ tải tới 800 DAU).
- Tổng chi tiền mặt 4 tháng: ~10–15 triệu VND (KOL + ads thử nghiệm + content tools + 1 buổi quay trẻ chơi).

**Gate sang P3** — phải đạt:

- [ ] ≥ 80 paid family (annual hoặc monthly đều tính).
- [ ] MRR ≥ 5 triệu VND, hoặc ARR ≥ 50 triệu VND.
- [ ] CAC < 100K VND/paid family qua organic + nano-KOL.
- [ ] Churn tháng < 10%.
- [ ] Founder thấy **muốn tiếp** (đừng coi nhẹ tín hiệu này).

**No-go**: paid < 20 family sau 4 tháng → định vị/giá có vấn đề → A/B giá hoặc đổi pitch trước khi build B2B.

### 3.4 P3 — Mở B2B nhỏ (Tháng 9–14): Arcade Class

**Mục tiêu**: mở SKU thứ 3, đa dạng nguồn thu, kiểm tra B2B fit.

**Phạm vi build:**

- **Arcade Class Teacher Free**: 1 lớp ≤30 HS, soạn quiz từ pool skill_id có sẵn, báo cáo cơ bản.
- **Arcade Class Pro** (199K/tháng): 5 lớp, custom set, báo cáo PDF gửi phụ huynh.
- Login Google for Education / SSO đơn giản.
- Tích hợp xuất Excel + PDF (server-side dùng `weasyprint` hoặc client-side `jsPDF`).

**Marketing B2B:**

- Tiếp cận **20 trung tâm dạy thêm Toán** quy mô nhỏ (1–3 chi nhánh) qua Facebook + giới thiệu phụ huynh paid.
- Tham gia **2–3 hội thảo giáo dục** ở Hà Nội / TPHCM (không cần phải đăng ký doanh nghiệp, chỉ cần đặt bàn).
- Liên hệ **5–10 hiệu trưởng Tiểu học** qua hội phụ huynh — pilot miễn phí 1 lớp 30 HS đổi feedback.

**Lưu ý cực quan trọng — B2B & ngưỡng thuế:**

- Khi 1 trung tâm trả 199K × 12 = 2,4tr/năm, **5 trung tâm = 12tr/năm** đã thêm vào doanh thu cá nhân.
- Nếu định vượt ngưỡng 200tr → **bắt buộc đăng ký hộ kinh doanh trước** (xem §5.3).
- Đối tác trung tâm/trường thường yêu cầu **hóa đơn** — chỉ có hộ kinh doanh kê khai hoặc DN mới xuất được.

**Gate sang P4** — phải đạt:

- [ ] ≥ 10 lớp Pro paid + ≥ 2 trung tâm/trường ký năm.
- [ ] Tổng doanh thu năm chạm ngưỡng 100–150tr (chuẩn bị bước qua ngưỡng 200tr).
- [ ] Hệ thống đã đăng ký hộ kinh doanh và có quy trình hoá đơn.

### 3.5 P4 — Quyết định scale/exit (Tháng 14–18)

**3 lựa chọn:**

| Hướng đi | Khi nào chọn | Ý nghĩa |
| --- | --- | --- |
| **A. Lifestyle business** | MRR 30–80tr ổn, churn thấp, founder vui | Giữ solo, không tuyển, sống bằng sản phẩm. Thu nhập ròng có thể 50–70% MRR. |
| **B. Tuyển 1–2 người + raise nhỏ** | MRR > 80tr, B2B trung tâm chứng minh được, Arcade Class scale tốt | Tuyển 1 dev + 1 content/marketing. Có thể gọi seed nhỏ 500K–2tr USD nếu thị trường mở thêm môn. |
| **C. Acquihire / sáp nhập** | Chỉ B2B chạy, B2C khó scale solo | Bán tài sản + content cho EdTech lớn (Edupia, OLM, FPT Education...) hoặc trở thành sản phẩm con của họ. |

**Quy tắc ra quyết định**: founder ngồi với bảng tài chính 12 tháng, hỏi: **"Nếu giữ nguyên trạng 3 năm nữa, mình có hạnh phúc không?"** Trả lời thật trước khi chọn B/C.

---

## 4. Cách đánh giá thị trường low-cost cho solo

> Mục tiêu: tốn càng ít tiền và thời gian càng tốt, nhưng **đủ tin cậy** để go/no-go. Ưu tiên dữ liệu định lượng > định tính > cảm tính.

### 4.1 Pre-launch validation (zero-budget tactics)

| Tactic | Chi phí | Tín hiệu thu được | Thời gian |
| --- | --- | --- | --- |
| Landing page + form sign-up | 0 (Cloudflare Pages) | Conversion rate khách → email | 1 tuần |
| Phỏng vấn Zalo/Voice 15 phút | 0 + thời gian | Insight chất lượng, willingness-to-pay | 2 tuần × 30 cuộc |
| Đăng nhóm FB phụ huynh quan sát + chia sẻ | 0 | Hiểu pain point, ngôn ngữ thật của parent | Liên tục |
| TikTok video trẻ chơi v1 | 0 + thời gian quay | Viral coefficient, audience phản ứng | 2 tuần × 5 video |
| Test landing page A/B copy | 0 (Cloudflare A/B) | Pitch nào hiệu quả: "luyện Toán" vs "tự học" vs "ViOlympic prep" | 2 tuần |
| Smoke test paywall ("đặt cọc giữ chỗ 50K") | ~0 (VietQR) | Chứng minh willingness-to-pay thật | 2 tuần |
| Đăng câu hỏi trên Cộng đồng VnExpress / Vozforum | 0 | Phản ứng phụ huynh đa thành phần | 1 tuần |
| Polling trong Zalo nhóm phụ huynh xin được vào | 0 | Multiple choice rõ ràng | 1 tuần |

**Lưu ý đặc thù VN:**

- Phụ huynh VN ít trả lời survey email; **Zalo voice call** hiệu quả hơn 5–10×.
- Nhóm Facebook phụ huynh có **quy tắc nghiêm**: không đăng quảng cáo. Phải build trust 2–4 tuần trước khi share gì có dạng bán.
- TikTok thuật toán VN ưu tiên video < 30 giây với hook 3 giây đầu — quay trẻ thật làm nhiều hơn animation.
- "Mẫu giáo lớn / chuẩn bị Lớp 1" là từ khoá nóng nhất trong giáo dục Tiểu học VN — dễ viral hơn "Lớp 2–5".

### 4.2 Tín hiệu định lượng để go/no-go

**Tham số bắc cầu (proxy metrics)** mà solo founder có thể đo trên server 1 GB:

| Metric | Cách đo | Ngưỡng "tín hiệu mạnh" |
| --- | --- | --- |
| Sign-up → Active conversion | Umami event `first_play` | ≥ 60% |
| D1 retention | `learning_sessions` user quay lại 1 ngày sau | ≥ 40% |
| D7 retention | quay lại 7 ngày sau | ≥ 25% |
| D30 retention | quay lại 30 ngày sau | ≥ 12% |
| Phiên/active user/tuần | `learning_sessions` aggregated | ≥ 4 |
| Phiên trung bình | `duration_s` trung vị | ≥ 90s (Flappy) hoặc ≥ 4 phút (Candy) |
| Parent dashboard view rate | Umami pageview `/parent/*` | ≥ 30% phụ huynh xem ≥ 1 lần/tuần |
| % phụ huynh hỏi trả phí (organic) | Đếm trong Zalo group + email | ≥ 5% sau 4 tuần |
| Smoke test paywall click | `paywall_view` → `pay_intent` | ≥ 8% |
| CAC organic (referral + KOL nano) | (chi referral + KOL) / paid mới | ≤ 100K VND |
| Viral coefficient (k) | invite gửi × accept rate | ≥ 0,3 thì rất tốt |

**Quy tắc đo lành mạnh:**

- Không dưới 30 user/cohort khi tính retention — số nhỏ dễ rơi vào nhiễu.
- Đo cohort theo **tuần đăng ký**, không phải theo ngày — phụ huynh có pattern tuần.
- Chia retention theo **lớp con** (Lớp 1 vs 2 vs 3...) — sẽ thấy lớp nào "kéo" hơn.
- Chia retention theo **kênh dẫn vào**: organic, KOL, FB ads — quyết định nên đầu tư kênh nào.

### 4.3 Tín hiệu định tính cần ghi lại

Mỗi tuần solo founder dành **1 giờ Friday** đọc lại Zalo, FB, comment, ghi vào Notion/markdown:

- 5 câu nói **đắt giá nhất** của phụ huynh tuần đó (cả khen lẫn chê).
- 3 vấn đề kỹ thuật user gặp.
- 1 ý tưởng feature **không** làm tuần này (để cuối năm review).
- Cảm giác bản thân: 1–10. Dưới 5 ba tuần liên tiếp → cảnh báo burnout.

### 4.4 Lệnh thoát — khi nào nên dừng

Solo founder cần **lệnh thoát viết sẵn** trước khi cảm xúc lấn át lý trí:

- **Sau P0 (8 tuần)**: < 60 sign-up + < 15% nói sẵn lòng trả → **thoát**: ý tưởng chưa fit.
- **Sau P1 (5 tháng)**: D7 < 15% → **thoát hoặc pivot môn**: trẻ không đủ thích.
- **Sau P2 (9 tháng)**: < 20 paid family → **thoát hoặc đổi mô hình giá**: pricing/value chưa đúng.
- **Sau P3 (14 tháng)**: 0 hợp đồng B2B nào ký → **bỏ SKU C**, giữ Flappy + Candy.
- **Bất kỳ lúc nào**: founder đánh giá bản thân < 4/10 trong 6 tuần liên tiếp → **bắt buộc nghỉ 2 tuần** trước khi quyết.

**Lệnh thoát không phải thất bại** — là cách bảo vệ năng lượng để dùng cho ý tưởng đúng tiếp theo.

---

## 5. Mô hình thu phí & tối ưu thuế hợp pháp ở VN 2026

> **Quan trọng**: phần này là **tối ưu thuế hợp pháp** (tax optimization), KHÔNG phải tránh/trốn thuế (tax evasion). Mọi phương án đề xuất đều dựa trên luật hiện hành VN. Trước khi triển khai > 50tr/năm doanh thu, **bắt buộc tham vấn 1 kế toán/luật sư VN**. Tài liệu này không thay thế tư vấn pháp lý.

### 5.1 Khung pháp lý 2026 — đọc kỹ vì có 2 cột mốc

VN 2026 có **2 mốc thay đổi** ngưỡng miễn thuế cho cá nhân/hộ kinh doanh:

| Giai đoạn | Ngưỡng miễn thuế GTGT + TNCN | Căn cứ |
| --- | --- | --- |
| Trước 01/01/2026 | ≤ 100 triệu/năm | Thông tư 40/2021/TT-BTC |
| **01/01/2026 – 30/06/2026** | **≤ 200 triệu/năm** | Luật Thuế GTGT 2024 (số 48/2024/QH15) |
| **Từ 01/07/2026** | **≤ 500 triệu/năm** | Luật Thuế TNCN 2025 (thông qua 10/12/2025) |

**Hệ quả cho solo founder:**

- Doanh thu **dưới 200tr/năm trong 6 tháng đầu 2026**: không nộp thuế GTGT + TNCN, nhưng **vẫn phải kê khai** nếu đã đăng ký hộ kinh doanh.
- Từ 01/07/2026, ngưỡng nâng lên **500tr/năm** — tức ~41,6tr/tháng doanh thu — đủ rộng cho cả P2 + đầu P3 mà không vướng thuế.
- Trên 500tr/năm: áp dụng thuế suất **15% trên thu nhập** (giống thuế TNDN) hoặc tỷ lệ trên doanh thu — chọn được.

**Quy định khác cần biết (2026):**

- **Nghị định 68/2026/NĐ-CP**: hộ kinh doanh phải thông báo cho cơ quan thuế **toàn bộ tài khoản ví điện tử** dùng cho kinh doanh (MoMo, ZaloPay...).
- **Thông tư 25/2025/TT-NHNN**: định danh tài khoản — tài khoản cá nhân nhận tiền kinh doanh thường xuyên có thể bị ngân hàng yêu cầu chuyển sang tài khoản kinh doanh.
- **Quyết định 3389/QĐ-BTC**: từ 01/01/2026 hộ kinh doanh chuyển sang **tự khai, tự nộp** (bỏ thuế khoán). Nhà nước hỗ trợ miễn phí phần mềm hóa đơn điện tử + hướng dẫn.
- Hộ kinh doanh dưới ngưỡng (200tr/500tr): **không bắt buộc dùng tài khoản ngân hàng**, kê khai 2 lần/năm.

### 5.2 Phương án A — Cá nhân không đăng ký (chỉ nửa đầu 2026 hoặc dưới 200tr/năm)

**Phù hợp khi**: doanh thu năm dự kiến rõ ràng < 200tr (P0–P1, có thể đầu P2).

**Cách làm:**

- Nhận tiền qua VietQR vào tài khoản cá nhân (không phí).
- Ghi sổ thủ công (Excel/Notion) mỗi giao dịch: ngày, người trả, số tiền, dịch vụ.
- Lưu hợp đồng/thông báo dịch vụ qua email — chứng cứ giao dịch dân sự, không phải kinh doanh đăng ký.
- Cuối năm tự đánh giá: **nếu vượt ngưỡng** → đăng ký hộ kinh doanh ngay tháng kế.

**Rủi ro & lưu ý:**

- Ngân hàng có thể "nhìn thấy" pattern nhận tiền lặp lại từ nhiều người → có thể gắn cờ "kinh doanh" theo Thông tư 25/2025. Phòng tránh: spread ra nhiều phương thức (VietQR, MoMo, chuyển khoản thường), không tất cả vào 1 tài khoản.
- **KHÔNG** ghi "thanh toán dịch vụ Math Blast" trong nội dung chuyển khoản nếu chưa đăng ký — hãy ghi "ung ho phat trien game tre em" hoặc "donate" để rõ tính chất voluntary support trong P0–P1.
- Khi có khách doanh nghiệp/trung tâm yêu cầu hóa đơn → **không đáp ứng được** → bắt buộc phải đăng ký hộ kinh doanh hoặc DN.

**Kết luận**: phương án A chỉ nên dùng **trong nửa đầu 2026** khi đang test pricing, hoặc cho thu donation. Sang P2 nên chuyển sang B.

### 5.3 Phương án B — Hộ kinh doanh kê khai (mặc định cho P2 trở đi)

**Phù hợp khi**: doanh thu dự kiến 100–500tr/năm (P2–P3), muốn xuất hóa đơn cho B2B, muốn an tâm pháp lý.

**Cách làm:**

1. **Đăng ký hộ kinh doanh** tại UBND quận/huyện (1–3 ngày làm việc):
   - Phí đăng ký: ~100K VND.
   - Mã ngành nghề: **6201 (Lập trình máy vi tính)** + **5821 (Hoạt động phát hành phần mềm trò chơi điện tử)** + **8559 (Giáo dục khác chưa được phân vào đâu)**.
   - Tên hộ: "Hộ kinh doanh [Tên bạn] — Math Blast" hoặc tên thương hiệu phù hợp.
   - Địa chỉ: nhà riêng được, không cần thuê văn phòng.
2. **Đăng ký mã số thuế** tự động sau đăng ký hộ kinh doanh.
3. **Đăng ký hóa đơn điện tử**:
   - Nhà nước hỗ trợ miễn phí phần mềm hóa đơn (VEinvoice, M-Invoice trial...) hoặc dùng **Misa eInvoice** (~500K/năm) cho đẹp.
   - Đăng ký "hóa đơn điện tử khởi tạo từ máy tính tiền" nếu bán B2C có khách yêu cầu.
4. **Mở tài khoản ngân hàng kinh doanh** (không bắt buộc nếu < 500tr/năm nhưng nên có để tách bạch).
5. **Thông báo cho cơ quan thuế** các tài khoản ví điện tử dùng kinh doanh (MoMo Storefront, ZaloPay Business — bắt buộc theo Nghị định 68/2026).
6. **Kê khai thuế 2 lần/năm** (đầu/giữa năm + cuối năm) — kể cả khi miễn thuế.

**Chi phí năm:**

| Khoản | VND/năm |
| --- | --- |
| Đăng ký hộ kinh doanh | 100K (1 lần) |
| Phần mềm hóa đơn điện tử | 0–500K |
| Phí ngân hàng kinh doanh | 0–600K |
| Kế toán dịch vụ ngoài (tuỳ chọn) | 1–3tr/năm cho khai thuế |
| **Tổng** | **0–4tr/năm** |

**Lợi ích:**

- Hợp pháp xuất hóa đơn cho trung tâm/trường — mở SKU C (Arcade Class).
- An tâm khi pattern nhận tiền lớn dần — không sợ ngân hàng/thuế gắn cờ.
- Nếu < 500tr/năm sau 01/07/2026: **vẫn miễn thuế** dù đã đăng ký.
- Khi vượt 500tr/năm có thể **chuyển đổi lên DN** (LLC) trong 1–3 tháng — đường nâng cấp rõ ràng.

### 5.4 Phương án C — Đi qua App Store / Google Play / Apple

**Phù hợp khi**: muốn 100% tự động hoá thuế, không muốn đụng giấy tờ, chấp nhận chia % cao.

**Cách làm:**

- Build app native hoặc PWA wrapper, nộp lên Apple App Store + Google Play.
- Thanh toán qua **In-App Purchase (IAP)** của Apple/Google.
- Apple/Google **trừ thẳng** VAT VN + thuế quốc gia + phí store (15% năm 1, 30% sau).
- Bạn nhận **net payout** hằng tháng vào tài khoản ngân hàng (qua Apple Connect / Google Play Console).
- Họ xuất receipt, bạn không cần xuất hóa đơn cho user cuối.

**Tax treatment:**

- Số tiền Apple/Google trả về VN **vẫn là thu nhập kinh doanh của bạn** — phải kê khai (nếu đã đăng ký hộ kinh doanh).
- Tuy nhiên Apple/Google đã **đóng VAT thay** cho user VN (theo Nghị định 91/2022 và sửa đổi 2024). Bạn không phải khấu trừ VAT đầu ra lần nữa.
- Vẫn phải tính TNCN/TNDN trên doanh thu net về (nếu vượt 500tr).

**Ưu/nhược:**

- Ưu: tự động hoá, scale toàn cầu (nếu mở thị trường khác), không lo dispute thanh toán, parental consent có sẵn.
- Nhược: mất **15–30% doanh thu**, chu kỳ xét duyệt app khắt khe (App Store đặc biệt khó với app trẻ em), khó chạy promotion VN-style (combo, voucher, family pack).

**Khuyến nghị**: làm song song với phương án B từ P3. App Store/Google Play là kênh phụ + phòng thủ thương hiệu (giữ chỗ tên app), không phải kênh chính của Math Blast cho thị trường VN.

### 5.5 Phương án D — Platform foreign (Patreon, Ko-fi, Buy Me a Coffee, Paddle)

**Phù hợp khi**: thu donation/subscription từ Việt kiều (P7) hoặc thị trường ngoài VN.

| Platform | Phí | Phù hợp gì cho Math Blast |
| --- | --- | --- |
| **Patreon** | 8–12% + transaction | Donation hàng tháng từ Việt kiều, KOL fan, không pricing rõ — "ủng hộ" model |
| **Ko-fi Gold** | 0% (chỉ phí PayPal/Stripe) | One-time tip / membership cho fan; nhẹ tay nhất |
| **Buy Me a Coffee** | 5% | Tương tự Ko-fi, brand ấm áp hơn |
| **Paddle** (Merchant of Record) | ~5% + transaction | B2B + B2C global, **Paddle tự đóng VAT** ở mọi nước → xuất hoá đơn hợp lệ; tốt cho khách Việt kiều/quốc tế |
| **Stripe** | 2,9% + 30 cent | Cần công ty offshore (Singapore/US LLC) — không khả thi cho solo VN |

**Lưu ý thuế:**

- Tiền từ platform foreign về tài khoản cá nhân VN: **vẫn là thu nhập** phải khai (nếu vượt ngưỡng).
- Donation cá nhân-cá nhân < 10tr/lần có thể coi là quà tặng (không thuế) — nhưng pattern lặp lại regular thì **không phải donation** dưới góc nhìn thuế.
- Paddle xử lý VAT cho user, nhưng số về VN vẫn là doanh thu cá nhân → vẫn áp ngưỡng 200tr/500tr.

**Khuyến nghị**: dùng **Ko-fi** ở P0–P1 cho "tip cộng đồng", tránh nhận pattern subscription qua platform foreign trong 12 tháng đầu để giữ pháp lý đơn giản.

### 5.6 Tách dòng doanh thu hợp pháp giữa 3 SKU

> Đây là phần dễ nhầm sang "trốn thuế". Đọc kỹ nguyên tắc trước khi áp dụng.

**Nguyên tắc:** một cá nhân/hộ kinh doanh có 1 mã số thuế, **mọi doanh thu cộng dồn**. Không có cách "chia cho 3" để mỗi cái dưới 500tr nếu cùng 1 chủ thể.

**Tuy nhiên các cách tách HỢP PHÁP:**

#### 5.6.1 Tách theo chủ thể pháp lý (tax entity)

- **Hộ kinh doanh chính (bạn)**: thu Candy + Arcade Class B2B. Đây là dòng "chính ngạch", có hóa đơn.
- **Tài khoản cá nhân (bạn)**: nhận donation Ko-fi, Patreon — dòng "ủng hộ" — nếu < 10tr/lần và không lặp lại với cùng người trả thì có thể coi là quà tặng.
- **Apple/Google IAP** từ Flappy: doanh thu net về tài khoản, vẫn cộng vào doanh thu hộ kinh doanh.

→ Không thực sự "chia" được, chỉ là 3 nguồn cùng đổ về 1 chủ thể.

#### 5.6.2 Cộng tác với người thân (chỉ khi vai trò THẬT)

VN cho phép **nhiều thành viên** trong một hộ kinh doanh. Nếu vợ/chồng/anh chị em **thực sự đóng góp lao động** (vd: vợ/chồng làm content, anh/em làm marketing), có thể:

- Đăng ký **hộ kinh doanh có 2 thành viên trở lên** (mỗi người được kê khai phần thu nhập của mình).
- Hoặc 1 người đăng ký hộ kinh doanh, người còn lại là **lao động thuê** — chi phí lương trừ vào thu nhập trước thuế (chỉ tính khi vượt ngưỡng 500tr).

**Cảnh báo**: nếu vai trò là giả (chia tên cho người không làm thật) → vi phạm pháp luật thuế khi bị thanh tra.

#### 5.6.3 Tách giai đoạn (timing the threshold)

Đây là **tối ưu thuế hợp pháp đơn giản nhất**:

- Nửa đầu 2026: ngưỡng 200tr → giữ doanh thu < 200tr trong 6 tháng đầu (~33tr/tháng) bằng cách:
  - Pricing thử nghiệm thấp ở P1.
  - Không push marketing mạnh trước 01/07/2026.
- Nửa sau 2026: ngưỡng 500tr → đẩy mạnh thu phí, ngân sách marketing.
- Năm 2027: doanh thu < 500tr → tiếp tục miễn thuế. Bắt đầu chuẩn bị cho năm 2028 (có thể phải lên DN nếu vượt).

#### 5.6.4 Tách thành 2 sản phẩm thực sự độc lập

Khi doanh thu đến gần 500tr/năm và muốn tiếp tục dưới ngưỡng, hợp pháp có thể:

- Cá nhân founder vận hành **Math Blast B2C** (Candy + Flappy) — 1 hộ kinh doanh.
- **Đối tác B2B** (1 đại lý / công ty bạn) license công nghệ Arcade Class → họ tự bán cho trung tâm/trường → bạn nhận **royalty** (tiền bản quyền phần mềm).
- Royalty từ pháp nhân khác cho cá nhân: thu nhập từ bản quyền, **thuế suất 5% TNCN** từ đồng đầu tiên (không có ngưỡng miễn 500tr) — nhưng đối tác chịu trách nhiệm khấu trừ.
- Lợi ích: doanh thu trực tiếp của bạn **chỉ là phần B2C** + royalty (số nhỏ hơn) → có thể giữ dưới 500tr lâu hơn.

→ Phương án này chỉ ý nghĩa khi đã có đối tác B2B đáng tin và doanh thu B2B đáng kể.

### 5.7 Cảnh báo: cách KHÔNG nên dùng

| Cách | Tại sao không nên |
| --- | --- |
| Mở 5 tài khoản cá nhân khác nhau, mỗi cái nhận tiền dưới 200tr | Vẫn là 1 mã số thuế, ngân hàng & thuế sẽ cộng dồn — không tránh được, có thể bị truy thu + phạt 0,03%/ngày + phạt 1–3 lần thuế trốn |
| Nhờ người thân không làm gì đứng tên hộ kinh doanh thứ 2 | Bị xếp là "lập hộ kinh doanh ảo" — phạt từ 5–10tr + truy thu |
| Nhận hết qua crypto (USDT) để "khỏi ngân hàng nào thấy" | Crypto chưa được công nhận là phương tiện thanh toán hợp pháp ở VN — nhận thanh toán bằng crypto vi phạm Nghị định 80/2016 |
| Nhận tiền và ghi nội dung CK là "vay nợ" | Thanh tra dễ phát hiện qua pattern; cấu thành "che giấu doanh thu" — phạt nặng |
| Không đăng ký gì, "khi nào bị hỏi mới khai" | Khi bị hỏi đã muộn — phạt + truy thu 5 năm về trước |
| Lập công ty offshore (BVI, Cayman) để chuyển tiền lòng vòng | Rất phức tạp, chi phí 30–50tr/năm, không xứng cho doanh thu < 1tr USD/năm |

**Quy tắc vàng**: **mọi đồng có thể truy được nguồn (qua bank/MoMo/store) sẽ được truy bằng AI thuế trong 5 năm tới.** Đầu tư 2–4tr/năm cho hộ kinh doanh + kế toán = rẻ hơn rất nhiều so với phạt 1 lần.

---

## 6. Mô hình giá theo nhịp thực tế

### 6.1 Pricing dưới ngưỡng miễn thuế

**Mục tiêu năm 1**: doanh thu **< 200tr (Q1–Q2)** rồi **< 500tr (từ Q3 trở đi)**.

**Phép toán đơn giản:**

| Pricing | Số paid family/năm để = 200tr | Để = 500tr |
| --- | --- | --- |
| 99K/tháng (≈ 1,2tr/năm/con) | ~167 family | ~417 family |
| 49K/tháng (≈ 588K/năm/con) | ~340 family | ~850 family |
| 599K/năm/con (1 lần) | ~334 family | ~835 family |
| 999K/năm/family (3 con) | ~200 family | ~500 family |
| 199K/tháng/lớp Pro (Arcade) | ~84 lớp | ~209 lớp |
| 5tr/năm/trường | ~40 trường | ~100 trường |

→ **Năm 1 mục tiêu khả thi cho solo**: **80–150 paid family + 5–10 lớp Pro** = 80–150tr/năm. **Ở dưới ngưỡng 200tr Q1–Q2**, tiếp tục dưới 500tr cả năm 2026.

### 6.2 Đề xuất bậc giá Math Blast (tối giản, dễ giải thích)

| Bậc | Giá VND | Ai mua | Ràng buộc tác động doanh thu |
| --- | --- | --- | --- |
| **Free Forever** | 0 | Trẻ tự chơi Flappy + 30 màn đầu Candy World 1 | 0đ — kênh viral |
| **Math Adventure Monthly** | 99K/tháng | Phụ huynh thử | Auto-renew, huỷ bất kỳ lúc nào |
| **Math Adventure Yearly** | 599K/năm (giảm 50%) | Phụ huynh tin tưởng | 1 con, đầy đủ Candy + Flappy |
| **Math Adventure Family** | 999K/năm | Family 2–3 con | Tối đa 3 profile trẻ + 1 parent dashboard |
| **Lifetime Founder** | 1.999K (1 lần) | Early adopter, KOL fan | Chỉ bán 100 suất đầu — tăng cảm giác khan hiếm + cash flow đầu kỳ |
| **Arcade Class Teacher Free** | 0 | Giáo viên 1 lớp ≤30 HS | Acquisition cho B2B |
| **Arcade Class Pro** | 199K/tháng | Giáo viên cá nhân, gia sư | Tới 5 lớp + báo cáo PDF |
| **Arcade Class Center** | 3tr+/năm/cơ sở | Trung tâm dạy thêm | Multi-class, login phụ huynh |
| **Arcade Class School** | 5–30tr/năm | Trường tiểu học | License toàn trường, BI dashboard |

**Chiến thuật bán:**

- "Lifetime Founder" làm trước **Yearly** để tạo cash đầu kỳ + xây cộng đồng founder.
- "Yearly" giảm 50% so với Monthly — đẩy ARR ổn định, giảm churn tháng.
- "Family" có **biên doanh thu/family cao hơn 1 con** vì family thường ít churn hơn (chi phí đã trả hết, không lăn tăn từng tháng).

### 6.3 Phương thức thanh toán nên hỗ trợ (theo thứ tự ưu tiên)

| Phương thức | Phí | Khi nào dùng |
| --- | --- | --- |
| **VietQR** (chuyển khoản ngân hàng có nội dung) | 0% | Mặc định cho mọi gói B2C; tiền về ngay |
| **MoMo Storefront** (cho hộ kinh doanh) | 1,1–1,5% | Khách quen MoMo, có loa báo nhận tiền |
| **ZaloPay Business** | 1,1–2,2% | Backup, ít hơn MoMo |
| **Chuyển khoản tay** + **đối soát thủ công** | 0% | P0–P1 khi chưa đăng ký hộ kinh doanh — ghi sổ tay |
| **Apple/Google IAP** | 15–30% | Khi mở app native, P3+ |
| **Paddle** (cho khách Việt kiều/quốc tế) | ~5% + transaction | Khi bán USD pricing P4+ |
| **Tiền mặt** (gặp trực tiếp B2B) | 0% | Trung tâm/trường nhỏ thanh toán theo hợp đồng tay |

**Mẹo VietQR cho solo:**

- Mỗi đơn hàng tạo nội dung CK unique (vd `MB123456`) — đối soát tự động qua API ngân hàng (MB Bank, Vietcombank đã có API miễn phí cho hộ kinh doanh từ 2025).
- Webhook **Casso** hoặc **PayOS** (~150–300K/tháng) tự động khớp giao dịch — đáng tiền khi > 30 đơn/tháng.
- Hiển thị **QR code động** trên trang thanh toán — phụ huynh quét, không phải gõ tay.

### 6.4 Refund & retention policy

- **Refund 30 ngày** không cần lý do — VN parent tin "money-back guarantee" → tăng conversion 15–25%.
- Refund qua VietQR thủ công, không tự động — solo founder làm 5 phút.
- **Pause subscription** thay vì huỷ — giảm churn 20–30%; giữ tài khoản 90 ngày trước khi xoá.
- **Email/Zalo từ chối ngày huỷ**: gửi 1 báo cáo cuối thể hiện tiến bộ con, lời cảm ơn, không bargain.

---

## 7. Ngân sách 12 tháng cho solo (lean)

> Giả định: founder không quit job, làm part-time 20h/tuần ở P0–P1, full-time từ P2 nếu có MRR.

### 7.1 Dự toán chi tiêu (VND)

| Khoản | P0 (M0–2) | P1 (M2–5) | P2 (M5–9) | P3 (M9–14) | Tổng 12 tháng |
| --- | --- | --- | --- | --- | --- |
| **Hạ tầng & dịch vụ** | | | | | |
| VPS hiện tại | 0 (đã có) | 0 | 0 | 0 | 0 |
| Domain .com + .vn | 1.000K | — | — | — | 1.000K |
| Cloudflare Pages/R2 | 0 | 0 | 0 | 0 | 0 |
| Resend / Brevo email | 0 | 0 | 0 | 200K (paid tier) | 200K |
| SGK Lớp 1–3 (Kết nối tri thức) | 450K | — | — | — | 450K |
| Hóa đơn điện tử Misa eInvoice | — | — | 500K | — | 500K |
| Casso/PayOS đối soát | — | — | 600K | 1.200K | 1.800K |
| Sentry / Uptime monitor | 0 | 0 | 0 | 200K | 200K |
| **Marketing & nội dung** | | | | | |
| Quay video TikTok (props/quà trẻ) | 500K | 500K | 1.000K | 1.000K | 3.000K |
| Nano-KOL phụ huynh (3–5 người) | — | 1.000K | 3.000K | 3.000K | 7.000K |
| Facebook Ads test | — | — | 3.000K | 3.000K | 6.000K |
| Hội thảo giáo dục (đặt bàn + travel) | — | — | — | 2.000K | 2.000K |
| **Pháp lý** | | | | | |
| Đăng ký hộ kinh doanh + công chứng | — | — | 500K | — | 500K |
| Kế toán dịch vụ ngoài (1 năm) | — | — | 1.500K | 1.500K | 3.000K |
| **Buffer (10%)** | 195K | 150K | 1.010K | 1.210K | 2.565K |
| **Tổng** | ~2,1tr | ~1,7tr | ~11tr | ~12tr | **~26,8tr** |

→ **Tổng ngân sách năm 1: ~27 triệu VND** (chưa tính lương founder).

### 7.2 Dự toán doanh thu kỳ vọng

| Quý | Tình huống realistic | Doanh thu kỳ vọng |
| --- | --- | --- |
| Q1 (M0–3) | P0 + đầu P1, free hoàn toàn | 0 |
| Q2 (M3–6) | P1 hoàn thiện, beta closed paid 10–20 founder | 5–15tr (Lifetime Founder) |
| Q3 (M6–9) | P2 soft launch, 30–60 paid family | 15–30tr |
| Q4 (M9–12) | P2 đỉnh + đầu P3, 80–150 paid family + 3–5 lớp Pro | 25–50tr |
| **Tổng năm 1** | | **45–95tr VND** |

→ **Hoà vốn năm 1: gần đạt** (chi 27tr vs thu 45–95tr → lãi gross 18–68tr).
→ Thực tế founder lao động không trả lương → quan tâm là **kiểm chứng product-market fit**, không phải ROI tài chính năm 1.
→ **Doanh thu năm 1 nằm dưới ngưỡng 200tr (Q1–Q2) và xa dưới 500tr (Q3+)** → không phát sinh nghĩa vụ thuế.

### 7.3 Năm 2 kỳ vọng

- **Doanh thu**: 200–400tr (vẫn dưới ngưỡng 500tr → miễn thuế).
- **Chi**: 60–100tr (tăng KOL, thêm 1 freelance content part-time).
- **Lãi gross**: 140–300tr/năm — đủ để founder lấy 12–25tr/tháng "lương".

### 7.4 Khi nào tuyển người đầu tiên

**Quy tắc 3-3-3**:

- Có **3 tháng MRR ≥ 30tr** liên tiếp.
- Đã làm việc **3 tuần liên tiếp > 60h/tuần** không xuể.
- Có **3 hợp đồng B2B** đang đàm phán cùng lúc.

→ Lúc đó tuyển 1 freelance content/marketing 5–10tr/tháng. Tránh tuyển dev đầu tiên (nó nói lên rằng founder đang muốn build hơn bán).

---

## 8. Quyết định go/no-go theo gate

> Bảng ngắn để in dán bàn làm việc. Mỗi cuối phase, founder ngồi 1 buổi sáng review bảng này.

| Gate | Time | Tín hiệu Go | Tín hiệu Pivot | Tín hiệu Stop |
| --- | --- | --- | --- | --- |
| **G1** sau P0 | M2 | ≥100 sign-up + ≥30% sẵn lòng trả ≥99K | < 100 sign-up nhưng ≥1 segment cụ thể quan tâm mạnh → đổi đối tượng | < 60 sign-up + < 15% sẵn lòng trả → bỏ ý tưởng |
| **G2** sau P1 | M5 | D7 ≥ 25%, D30 ≥ 12% | D7 < 25% nhưng phụ huynh khen Flappy → đổi sang chỉ Flappy/casual | D7 < 15% sau 5 phụ huynh thử → ý tưởng không kéo trẻ |
| **G3** sau P2 | M9 | ≥ 80 paid family + MRR ≥ 5tr + churn < 10% | < 30 paid → giảm giá / đổi pitch | < 10 paid sau 4 tháng → bỏ B2C, thử B2B |
| **G4** sau P3 | M14 | ≥ 10 lớp Pro + ≥ 2 trường ký + DT năm chạm 100tr | 0 hợp đồng B2B → bỏ SKU C, dồn B2C | DT chỉ ~50tr cả năm → cân nhắc lifestyle-only |
| **G5** sau P4 | M18 | MRR ≥ 30tr + B2B churn < 5% | MRR đứng yên 6 tháng → đổi mô hình giá | Founder burnout > 3 tháng → tạm dừng |

**Quy tắc cuối**: nếu founder thấy **không vui** > 6 tháng dù số liệu Go → vẫn coi là Stop. Sản phẩm cho trẻ em không thể được làm bởi 1 founder không hạnh phúc.

---

## 9. Phụ lục — stack code mẫu cho 1 GB RAM

> Đề xuất tham khảo, không bắt buộc. Mục đích: bắt đầu nhanh, tốn ít RAM, dễ đẩy lên GitHub Actions để CI miễn phí.

### 9.1 Cấu hình Caddy

```caddy
{
    email founder@mathblast.vn
    auto_https on
}

mathblast.vn, www.mathblast.vn {
    encode zstd gzip
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        root * /var/www/mathblast
        try_files {path} /index.html
        file_server
    }
}
```

### 9.2 FastAPI khởi động lean

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import sqlite3, os

DB_PATH = os.environ.get("MB_DB", "/var/lib/mathblast/mb.db")

@asynccontextmanager
async def lifespan(app):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA mmap_size=67108864;")  # 64 MB mmap
    conn.close()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=512)

# Khởi chạy: uvicorn app.main:app --workers 1 --host 127.0.0.1 --port 8000
```

### 9.3 Litestream backup config

```yaml
# /etc/litestream.yml
dbs:
  - path: /var/lib/mathblast/mb.db
    replicas:
      - type: s3
        endpoint: https://<account>.r2.cloudflarestorage.com
        bucket: mathblast-backups
        path: mb.db
        access-key-id: ${R2_KEY}
        secret-access-key: ${R2_SECRET}
        retention: 720h  # 30 ngày
```

### 9.4 systemd service (uvicorn + litestream)

```ini
# /etc/systemd/system/mathblast.service
[Unit]
Description=Math Blast API
After=network.target

[Service]
Type=simple
User=mathblast
WorkingDirectory=/opt/mathblast
ExecStart=/opt/mathblast/.venv/bin/uvicorn app.main:app --workers 1 --host 127.0.0.1 --port 8000
Restart=always
MemoryMax=400M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/litestream.service
[Unit]
Description=Litestream replication
After=network.target mathblast.service

[Service]
Type=simple
ExecStart=/usr/local/bin/litestream replicate -config /etc/litestream.yml
Restart=always
MemoryMax=80M

[Install]
WantedBy=multi-user.target
```

### 9.5 Reconcile thanh toán VietQR

```python
# Cron mỗi 5 phút: check transaction từ MB Bank API
# Nội dung CK chứa "MB<order_id>" để khớp
import re, sqlite3, requests

def reconcile():
    txns = mb_bank_get_recent_transactions(account="...")  # 50 giao dịch gần nhất
    conn = sqlite3.connect(DB_PATH)
    for t in txns:
        m = re.search(r"MB(\d+)", t["description"].upper())
        if not m: continue
        order_id = int(m.group(1))
        cur = conn.execute(
            "UPDATE orders SET paid=1, paid_at=? WHERE id=? AND paid=0 AND amount=?",
            (t["timestamp"], order_id, t["amount"])
        )
        if cur.rowcount:
            send_zalo_receipt(order_id)
    conn.commit()
```

### 9.6 Dashboard parent qua Zalo OA tuần

- Mỗi Chủ Nhật 19h, render PNG 1080×1920 từ HTML template (Pillow / Playwright headless trên server) cho mỗi family active.
- Push qua Zalo OA Broadcast API (free 4 tin/tháng/user) hoặc gửi link tới landing report.
- Nội dung: "Tuần này con học X câu, master Y kỹ năng, đề xuất 3 việc tuần sau".

---

## Phụ chú

- Tài liệu này phản ánh **luật thuế VN tại thời điểm tháng 5/2026**. Chính sách có thể thay đổi — đặc biệt Nghị định 68/2026 và Thông tư 18/2026 còn đang trong quá trình ban hành chi tiết.
- Trước khi triển khai bất kỳ phương án thuế nào với doanh thu > 50tr/năm, hãy gặp **kế toán đại lý thuế cấp 2 trở lên** ở khu vực bạn đăng ký HKD. Phí ~500K–1tr cho 1 buổi tư vấn — rẻ hơn rất nhiều so với 1 lần phạt sai.
- Mọi phương án trong §5 đều **giả định founder thật, hoạt động thật, doanh thu thật**. Không phương án nào hỗ trợ ý định kê khai gian dối.

Đồng hành với:

- `math-blast-v2.md` — đặc tả sản phẩm & kỹ thuật.
- `canvases/math-blast-market-strategy.canvas.tsx` — phân tích thị trường + persona đầy đủ.




