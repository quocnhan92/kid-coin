# Math Blast — Phân tích thị trường & chiến lược sản phẩm VN

> Bản markdown của canvas `math-blast-market-strategy.canvas.tsx`. Đánh giá khả năng tách 3 chế độ (Candy / Flappy / Arcade) thành các SKU độc lập, phân khúc khách hàng, sứ mệnh sản phẩm và lộ trình go-to-market cho thị trường tiểu học Việt Nam (Lớp 1–5, CT GDPT 2018).

---

## Tóm tắt điều hành — 5 con số nền

| Chỉ số | Giá trị |
| --- | --- |
| Học sinh tiểu học VN (Lớp 1–5) | **~9 triệu** |
| Quy mô EdTech K-12 VN 2024 | **~$3 tỷ** |
| CAGR thị trường EdTech 2025–34 | **12,3% / năm** |
| HS tham gia ViOlympic 2025–26 | **1,05 triệu** |
| Người dùng Monkey (benchmark) | **15 triệu** |

### Kết luận sớm — không nên tách thành 3 app rời rạc

Giữ **một engine + một thương hiệu "Math Blast"** nhưng đóng gói thành **3 SKU độc lập về kênh phân phối & mô hình thu**:

- **Flappy** — free + ads, kênh viral mua user.
- **Candy 300** — subscription B2C cho phụ huynh, lõi giữ chân & doanh thu.
- **Arcade Class** — B2B/B2T cho giáo viên & trung tâm.

Mỗi SKU chia sẻ `skill_id`, mastery, account và content pack — chi phí nội dung trả một lần, phục vụ 3 nhu cầu thị trường khác nhau.

---

## Mục lục

1. [Bối cảnh thị trường EdTech tiểu học VN (2026)](#1-bối-cảnh-thị-trường-edtech-tiểu-học-vn-2026)
2. [Có nên tách 3 chế độ thành 3 game độc lập?](#2-có-nên-tách-3-chế-độ-thành-3-game-độc-lập)
3. [Định nghĩa 3 SKU & nhiệm vụ chiến lược](#3-định-nghĩa-3-sku--nhiệm-vụ-chiến-lược)
4. [Phân khúc khách hàng mục tiêu (persona + sizing)](#4-phân-khúc-khách-hàng-mục-tiêu-persona--sizing)
5. [Định vị cạnh tranh](#5-định-vị-cạnh-tranh)
6. [Sứ mệnh & nguyên tắc bất biến](#6-sứ-mệnh--nguyên-tắc-bất-biến)
7. [Mô hình kinh doanh tổng hợp](#7-mô-hình-kinh-doanh-tổng-hợp)
8. [Lộ trình go-to-market theo giai đoạn](#8-lộ-trình-go-to-market-theo-giai-đoạn)
9. [Rủi ro chính & cách giảm thiểu](#9-rủi-ro-chính--cách-giảm-thiểu)
10. [Khuyến nghị chiến lược cuối](#10-khuyến-nghị-chiến-lược-cuối)

---

## 1. Bối cảnh thị trường EdTech tiểu học VN (2026)

### 1.1. Cơ cấu chi tiêu EdTech VN 2024 (theo phân khúc)

| Phân khúc | % thị trường | Doanh thu 2024 |
| --- | --- | --- |
| Pre-K & K-12 (mầm non + phổ thông) | **81,5%** | $2,97 tỷ |
| Đại học & sau ĐH | 11,5% | $0,42 tỷ |
| Học tiếng Anh & kỹ năng | 7,0% | $0,25 tỷ |
| **Tổng** | 100% | **$3,64 tỷ** |

*Nguồn: GlobalData VN EdTech 2024.*

### 1.2. Chi "học thêm" Toán của phụ huynh (VND/buổi)

| Hình thức | VND/buổi |
| --- | --- |
| Gia sư tại nhà (cấp 1) | 120K |
| Trung tâm phổ thông | 150K |
| Trung tâm cao cấp | 250K |
| Tiền tiểu học VIP | 500K |
| App học toán subscription (quy đổi) | 25K |

*Nguồn: tổng hợp Thanh Niên, VTC News, Gia Sư Sư Phạm 2025–26. App ~25K/buổi = 300K/tháng quy đổi từ gói năm.*

### 1.3. Động lực thuận lợi

- CT GDPT 2018 còn "mới" → phụ huynh lo lắng tìm công cụ luyện theo chuẩn.
- Smartphone phổ cập >80%; trẻ tiếp cận device sớm, parent-controlled time là norm.
- Văn hoá thi cử: ViOlympic, Toán Quốc tế (Kangaroo, IMC) — phụ huynh sẵn sàng chi.
- Chuyển đổi số giáo dục là chính sách quốc gia → trường công mở cửa cho app.

### 1.4. Áp lực & rào cản

- Monkey, OLM, Edupia, ELSA đã chiếm "top of mind" phụ huynh đô thị.
- Phụ huynh khó tin "game = học" — cần bằng chứng tiến bộ rõ ràng.
- Quy định mới về dạy thêm 2025 + lo ngại screen time đẩy phụ huynh cẩn trọng hơn.
- Lợi nhuận ads/IAP cho trẻ <13 bị COPPA & các quy định nội địa siết chặt.

### 1.5. Khoảng trống thị trường

- Sản phẩm "Toán đơn môn, bám CT GDPT 2018, free-to-try, có leaderboard family" còn ít. Monkey nặng tiếng Anh + mầm non.
- Công cụ **giáo viên Tiểu học tự tạo bài tập 1 phút** hầu như chưa có sản phẩm VN hoá tốt.
- Phân khúc 6–8 tuổi **không biết đọc nhanh** — cần TTS bài Toán, đa số app coi nhẹ.

---

## 2. Có nên tách 3 chế độ thành 3 game độc lập?

So sánh ba phương án triển khai. Ưu tiên đánh giá: chi phí nội dung, tốc độ ra mắt, hiệu quả mua user, khả năng đa dạng hoá doanh thu, độ chịu rủi ro của team nhỏ.

| Tiêu chí | PA1 · 1 app duy nhất 3 mode | PA2 · 3 app hoàn toàn tách rời | **PA3 · 1 engine + 3 SKU (đề xuất)** |
| --- | --- | --- | --- |
| Chi phí phát triển ban đầu | Thấp (1 codebase, 1 backend) | Cao 2,3–2,8× (3 storefront, 3 UA funnel) | Thấp–TB (1 core + 3 shell client) |
| Chi phí nội dung (300 màn + pool kỹ năng) | 1× (dùng chung) | 3× nếu không tái sử dụng manifest | 1× (content pack chung, §5.A.7 & §5.B.15) |
| Tốc độ ra MVP | Nhanh (đã có v1) | Chậm — 3 lần phê duyệt store, 3 ASO | Nhanh — Flappy trước, Candy nối, Arcade sau |
| Khả năng mua user (CAC) | Mức TB — phải bán "3-in-1" khó định vị | Cao — mỗi app có thị trường riêng nhưng phải xây 3 brand | **Thấp nhất** — Flappy = hook viral free, Candy = retention paid |
| Đa dạng mô hình doanh thu | Khó kết hợp ads + subscription trong 1 app cho trẻ <13 | Dễ tách: app ads / app subscription / app B2B | Tách rõ — mỗi SKU 1 model, không xung đột chính sách store |
| Vận hành (DevOps, support) | Đơn giản nhất | Phức tạp gấp 3 | Trung bình — 1 backend, 3 binary |
| Đo lường & học dữ liệu chéo (cross-mode mastery §5.B.13) | Tự động OK | Phải xây bridge phức tạp | OK — chia sẻ skill_id, mastery, account |
| Rủi ro thương hiệu (1 SKU sự cố kéo các SKU khác) | Cao — 1 review xấu kéo toàn bộ | Thấp — cô lập | Trung bình — brand chung nhưng SKU độc lập trên store |
| Phù hợp team nhỏ (<5 dev) | Tốt | Quá tải | **Tốt nhất, đi từng giai đoạn** |

### 2.1. Tại sao 1 engine + 3 SKU thắng

1. Chi phí biên của SKU thứ 2 và thứ 3 chủ yếu là **vỏ client + ASO**; lõi nội dung, mastery, API là một (§5.B.13 cross-mode mastery đã sẵn).
2. Mỗi SKU phục vụ **một "job to be done"** khác nhau — khó nhồi cả 3 vào một câu pitch mà phụ huynh, trẻ, giáo viên cùng hiểu.
3. Chính sách Google Play / App Store cho trẻ <13: **ads + IAP + leaderboard public** không thể đặt cùng 1 app "Designed for Families". Tách SKU = tách compliance.
4. Tách kênh phân phối: Flappy đẩy TikTok / Facebook Reels (viral), Candy đẩy Zalo/Facebook Group phụ huynh + KOL Toán, Arcade đi B2B trực tiếp đến trường & trung tâm — 3 funnel khác nhau hoàn toàn.

---

## 3. Định nghĩa 3 SKU & nhiệm vụ chiến lược

### 3.1. SKU-A · Flappy Math Blast (free + ads)

**Tag:** Acquisition hook · Sprint 60s · Lớp 1–5

- **Vai trò trong portfolio**: cửa ngõ tiếp cận trẻ + viral marketing. Free, có quảng cáo bound by parental consent, không IAP. KPI chính: D1/D7 retention, viral coefficient, conversion sang Candy.
- **Mô hình thu**: ads rewarded (xem 15s → +1 Magic Feather), CPM ước tính 0,3–0,8 USD ở VN, target ARPDAU 0,01–0,03 USD. Năm 1: 50–80% là kênh dẫn user, không phải kênh lợi nhuận.
- **Khách hàng mục tiêu**: trẻ 6–11 tự chơi trên điện thoại bố mẹ; phụ huynh tò mò muốn "thử nhanh"; KOL TikTok thử thách Sprint 60s.

### 3.2. SKU-B · Math Adventure 300 — Candy (subscription)

**Tag:** Lõi doanh thu · 300 màn CT GDPT · Parent dashboard

- **Vai trò trong portfolio**: cạnh tranh trực diện Monkey Math + OLM Toán. Là sản phẩm "học thay học thêm online" cho phụ huynh. KPI chính: % trial → paid, MRR, churn 3-tháng, parent-NPS.
- **Mô hình thu**: 3 tier — tháng 99K / năm 599K / family 3 con 999K VND. Free trial 7 ngày + freemium 30 màn đầu (đến L030 hết World 1). Mục tiêu LTV / CAC ≥ 3.
- **Khách hàng mục tiêu**: phụ huynh đô thị 28–42 tuổi, con Lớp 1–3 là trọng tâm (anxiety cao nhất), Lớp 4–5 pre-cấp 2 + ViOlympic prep.

### 3.3. SKU-C · Math Arcade Class (B2B/B2T)

**Tag:** B2B / B2T · Giáo viên & trung tâm · Bài tập tùy chỉnh

- **Vai trò trong portfolio**: mở mặt trận B2B doanh thu cao và phòng thủ trước đối thủ chỉ làm B2C. KPI chính: số lớp/tháng, số bài giao, license renewal.
- **Mô hình thu**: free cho giáo viên 1 lớp ≤30 HS (acquisition). Pro 199K/tháng cho 5 lớp; bản Trường 5–15tr/năm theo headcount; bản Trung tâm 3tr+ theo chi nhánh. Add-on báo cáo PDF cho phụ huynh.
- **Khách hàng mục tiêu**: ~360.000 giáo viên Tiểu học VN, ~14.500 trường Tiểu học, hàng nghìn trung tâm dạy thêm Toán & gia sư 1-1.

### 3.4. So sánh 3 SKU theo khía cạnh vận hành

| Khía cạnh | SKU-A · Flappy | SKU-B · Candy 300 | SKU-C · Arcade Class |
| --- | --- | --- | --- |
| Job to be done | Giải trí + luyện phản xạ | Học bài bản theo chương trình | Giao bài & đánh giá |
| Người ra quyết định cài đặt | Trẻ + phụ huynh thoáng | Phụ huynh | Giáo viên / quản lý trung tâm |
| Độ dài phiên trung bình | 60 giây | 5–10 phút | 10–20 phút |
| Mức cảm xúc cần dopamine | Cao (vui) | Vừa (tiến bộ) | Thấp (chính xác) |
| Yêu cầu compliance | Ads cho trẻ <13, GDPR/COPPA-K | Subscription quản lý, thông tin trẻ | B2B contract, dữ liệu lớp |
| Kênh phân phối chính | App store, TikTok, Reels, YouTube Shorts | Zalo, Facebook nhóm phụ huynh, KOL Toán | Trực tiếp gặp BGH trường, hội thảo, đại lý vùng |
| Đối thủ trực tiếp | Prodigy, Khan Kids, hyper-casual maths | Monkey Math, OLM Toán, Edupia Toán | ClassPoint, Quizizz, Azota, Vio.edu.vn |
| KPI ưu tiên | DAU, viral, CAC ≈ 0 | MRR, paid conversion, churn | Số trường ký, MAU giáo viên, NRR |
| Năm 1 % doanh thu kỳ vọng | 5–10% | 55–65% | 25–35% |

---

## 4. Phân khúc khách hàng mục tiêu (persona + sizing)

Mỗi persona kèm dung lượng thị trường lý thuyết (TAM), nhu cầu cốt lõi, mode phù hợp và mức sẵn lòng chi trả tại thị trường VN 2026.

| Persona | Quy mô VN | Nhu cầu cốt lõi | Mode phù hợp | Willingness to pay | Ưu tiên |
| --- | --- | --- | --- | --- | --- |
| **P1** · Phụ huynh đô thị có con Lớp 1–3 | ~2,5 triệu hộ | Lo CT GDPT 2018 mới, cần tool luyện hàng ngày, có báo cáo tiến bộ | Candy (chính) + Flappy (mồi) | 300K–1tr / năm / con | ★★★★★ |
| **P2** · Phụ huynh con Lớp 4–5 luyện ViOlympic / lên cấp 2 | ~1,2 triệu hộ | Luyện tốc độ & câu khó, prep thi, ôn cửu chương + PS/TP | Candy challenge L271–L300 + Flappy T4–T5 | 500K–2tr / năm / con | ★★★★ |
| **P3** · Trẻ 6–11 tự chơi (intrinsic motivation) | ~9 triệu trẻ | Vui, leaderboard, skin chim, sprint ngắn | Flappy 60s (chính) | Free; ads dung sai cao | ★★★★★ (kênh viral) |
| **P4** · Giáo viên Tiểu học công lập | ~360.000 GV | Bài tập 5–10 phút mở đầu/kết thúc tiết, dữ liệu lớp, không tốn chuẩn bị | Arcade Class + Candy single-skill mode | Cá nhân 0–200K/tháng | ★★★★ |
| **P5** · Trung tâm dạy thêm & gia sư 1-1 | Hàng chục nghìn TT + ~hàng trăm nghìn gia sư | Bài luyện theo cấp HS, đo tiến bộ, in báo cáo gửi phụ huynh | Arcade Class Pro + Candy report | 200K–500K/tháng/cơ sở | ★★★★ |
| **P6** · Trường Tiểu học (B2B school license) | ~14.500 trường | Chuyển đổi số môn Toán, app dùng chung toàn trường, đáp ứng chỉ tiêu Sở GD | Arcade Class School + Candy school edition | 5–30tr / năm / trường | ★★★ (sales-cycle dài) |
| **P7** · Người Việt ở nước ngoài (Việt kiều) | ~5 triệu người, ~500K trẻ Lớp 1–5 | Giữ tiếng Việt + theo CT GDPT để con nắm Toán khi về thăm nhà | Candy bản tiếng Việt + TTS rõ ràng | USD pricing, sẵn lòng chi 30–80 USD/năm | ★★ (niche, biên cao) |
| **P8** · Phụ huynh nông thôn / tỉnh lẻ | ~3 triệu hộ có smartphone | Toán bám SGK, ít data, offline khi cần, giá rẻ | Flappy free + Candy gói nhỏ 30K/tháng | 30K–150K / năm / con | ★★★ (volume play) |
| **P9** · Trẻ học chuyên biệt / SEN (chậm phát triển, tự kỷ nhẹ) | ~3–5% học sinh tiểu học | Phiên cực ngắn, dopamine an toàn, không shame, TTS, accessibility | Candy đầu World 1 + Flappy T1 (nhịp chậm) | Phụ huynh chi cao 1–3tr/năm | ★★ (chứng chỉ đạo đức brand) |

### 4.1. Ước lượng TAM / SAM / SOM năm 3

- **TAM** — Toàn bộ chi tiêu của 9 triệu HS tiểu học VN cho học Toán bổ trợ (offline + online): ước **~30.000 tỷ VND/năm**.
- **SAM** — Phần có thể đi đường digital app (đô thị + có smartphone, chấp nhận thanh toán online): ~3 triệu hộ × 400K trung bình ≈ **1.200 tỷ VND/năm (~$50M)**.
- **SOM năm 3** — Mục tiêu chiếm 2–4% SAM = **24–48 tỷ VND doanh thu/năm (~$1–2M ARR)**. Khả thi nếu đạt 80–150K paid family + 1.500 trường & trung tâm.

### 4.2. Vùng địa lý ưu tiên (năm 1–2)

| Tỉnh / Thành | Mức ưu tiên (1–10) |
| --- | --- |
| Hà Nội | 10 |
| TP.HCM | 10 |
| Đà Nẵng | 7 |
| Hải Phòng | 6 |
| Cần Thơ | 5 |
| Tỉnh khác | 4 |

*Ưu tiên theo: GDP per capita, tỉ lệ smartphone, dung lượng KOL phụ huynh, kết quả ViOlympic (Hà Nội 7.733 / HP 4.396 thí sinh đoạt giải 2025–26).*

---

## 5. Định vị cạnh tranh

| Đối thủ | Tập trung | Điểm mạnh | Điểm yếu (cơ hội cho Math Blast) | Mode Math Blast đối đầu |
| --- | --- | --- | --- | --- |
| **Monkey Math** (VN) | Mầm non + Lớp 1–2, song ngữ Anh | Brand top, marketing mạnh, ARPU cao | Lệch CT GDPT 2018 VN, nội dung Lớp 3–5 mỏng, chủ yếu tiếng Anh, giá cao | Candy 300 (Lớp 1–5 thuần VN, bám SGK) |
| **OLM.vn** | K-12, môn rộng, miễn phí + Pro | Có sẵn cộng đồng giáo viên, content rộng | UI cũ, không gamification kid-friendly, web-first | Candy 300 + Arcade Class |
| **ViOlympic / Vio.edu.vn** | Thi đấu Toán + tiếng Anh trực tuyến | 1 triệu thí sinh/năm, brand quốc dân | Là arena thi, không phải tool luyện hàng ngày | Tích hợp (làm "luyện thi ViOlympic") thay vì cạnh tranh |
| **Edupia Toán / Math** | Lớp 1–5, video bài giảng | Video, phụ huynh dễ hiểu "con đang học gì" | Tương tác thấp, không có loop chơi ngắn | Candy + Flappy (game-first) |
| **Khan Academy Kids** (free) | Free, đa môn, đa ngôn ngữ | Miễn phí, chất lượng cao | Không bám CT GDPT 2018, giọng/ngôn ngữ Tây | Candy 300 (bám SGK & TTS giọng VN) |
| **Prodigy Math** | RPG toán Bắc Mỹ | Gameplay sâu, mạnh viral | Không có ở VN, không bám SGK VN | Flappy + Candy (game-first thuần VN) |
| **Quizizz / Azota** | Tool giáo viên giao bài | Hệ sinh thái giáo viên có sẵn | Không Toán-first, không kid game | Arcade Class (Toán + game-feel) |
| **Hyper-casual maths trên CH Play** | Free + ads, không bám SGK | Viral mạnh, CAC thấp | Không tin cậy, nhanh chán, không có lộ trình | Flappy (lấy độ vui + thêm chuẩn CT GDPT) |

### 5.1. Định vị chốt — một câu cho mỗi đối tượng

- **Cho phụ huynh:** "300 màn Toán bám SGK Lớp 1–5, có lộ trình & báo cáo tiến bộ — như học thêm Toán nhưng 25K/ngày, con tự ngồi 10 phút."
- **Cho trẻ:** "Bay 3 nấc mỗi câu đúng — sprint 60 giây, chơi 1 phút giải lao, đứng top bảng gia đình."
- **Cho giáo viên:** "Soạn bài luyện 60 giây trong 30 giây — giao cho cả lớp, có báo cáo tự động, dùng làm mở đầu/kết thúc tiết."

---

## 6. Sứ mệnh & nguyên tắc bất biến

### 6.1. Tuyên ngôn sứ mệnh

> **"Giúp mỗi học sinh tiểu học Việt Nam yêu Toán — bằng những phiên chơi ngắn, an toàn tâm lý, bám sát Chương trình GDPT 2018, đồng hành cùng cha mẹ và thầy cô."**

Sứ mệnh cụ thể hoá thành **4 cam kết bất biến** không đổi qua mọi thế hệ tính năng:

1. **Bám chuẩn**: mọi content phải truy được về chuẩn năng lực CT GDPT 2018 (Thông tư 32/2018) và có thể fork pack cho từng bộ SGK.
2. **Tôn trọng trẻ em**: không loot box, không variable-ratio reward, không leaderboard public ở MVP, không "lose streak" cross-session ép trẻ quay lại (§5.B.12).
3. **Minh bạch tiến bộ**: phụ huynh & giáo viên luôn có dashboard số liệu — mastery, decay, đề xuất ôn — không chỉ điểm số mơ hồ.
4. **Tiết kiệm & bền vững**: hạ tầng nhẹ (§9), 1 engine cho 3 SKU, content pack tái sử dụng — giảm chi phí biên để phục vụ cả phụ huynh nông thôn 30K/tháng.

### 6.2. Hứa hẹn với 3 đối tượng

**Hứa hẹn với trẻ em:**
> "Mỗi phiên 60 giây hoặc một màn vài phút, con luôn được khen. Sai cũng không bị trừng phạt — chỉ tụt nhẹ, được Lông Vũ Phép cứu. Mỗi tuần con khoá thêm một skin chim, leo thêm một nấc tri thức."

**Hứa hẹn với phụ huynh:**
> "Ba báo cáo / tuần qua Zalo: con đã master kỹ năng nào, đang kẹt ở đâu, gợi ý 10 phút hôm nay. Không cần tự kiểm tra bài — Math Blast làm thay."

**Hứa hẹn với giáo viên:**
> "Giao bài luyện 1 phút trong 30 giây. Biết ngay học sinh nào yếu phép cộng, ai cần ôn nhân chia. Dạy chậm — Math Blast luyện nhanh."

---

## 7. Mô hình kinh doanh tổng hợp

### 7.1. Cơ cấu doanh thu kỳ vọng năm 3

| Nguồn | Tỷ trọng |
| --- | --- |
| Subscription B2C (Candy 300) | **60%** |
| B2B trường + trung tâm (Arcade Class) | **25%** |
| Ads & rewarded (Flappy) | 8% |
| Việt kiều & xuất khẩu pack | 5% |
| Phần thưởng & merchandise nhỏ | 2% |

*Cơ cấu lành mạnh: 1 nguồn lõi (subscription) + 2 nguồn cân bằng + 2 niche.*

### 7.2. Giá kế hoạch (VND)

| Gói | Giá | Bao gồm |
| --- | --- | --- |
| Flappy free | 0 | Tất cả Tier, ads rewarded, không leaderboard public |
| Candy trial | 0 · 7 ngày | Toàn bộ World 1 (L001–L054) |
| Candy Monthly | 99K / tháng | 1 con, mọi mode, parent dashboard |
| Candy Yearly | 599K / năm | 1 con, tiết kiệm 50% |
| Candy Family | 999K / năm | Tối đa 3 con, share progress |
| Arcade Teacher Free | 0 | 1 lớp ≤30 HS, báo cáo cơ bản |
| Arcade Teacher Pro | 199K / tháng | 5 lớp, báo cáo PDF, custom set |
| Arcade School | 5–30tr / năm | License toàn trường, BI dashboard |
| Arcade Tutoring Center | 3tr+ / chi nhánh / năm | Multi-class, phụ huynh login riêng |

### 7.3. KPI tài chính nền

| Chỉ số | Mục tiêu |
| --- | --- |
| Giá năm 1 con · Candy yearly | **600K VND** |
| ARPU/tháng Candy quy đổi | ~$5 |
| Mục tiêu LTV / CAC | **3–5×** |
| Gross margin năm 2 kỳ vọng | **35–45%** |

---

## 8. Lộ trình go-to-market theo giai đoạn

| Giai đoạn | Tháng | Hành động chính | SKU chủ lực | KPI gate |
| --- | --- | --- | --- | --- |
| **P0** · Validate | 0–2 | Pilot 100 phụ huynh Hà Nội + TP.HCM với MVP Candy World 1 + Flappy T1–T2 | Candy MVP | ≥40% phụ huynh sẵn sàng trả 99K/tháng |
| **P1** · Acquisition | 2–5 | Mở Flappy public, đẩy TikTok/Reels, KOL Toán; thu user free; chuẩn bị paywall Candy | Flappy | 10K DAU, viral coeff ≥0,3, CAC < 30K/install |
| **P2** · Monetize B2C | 5–9 | Tung Candy Yearly + Family, parent dashboard, báo cáo Zalo, tích hợp ViOlympic prep | Candy 300 | 5.000 paid family, MRR ≥ 500tr VND |
| **P3** · Mở B2B | 9–14 | Arcade Class Teacher Free; landed-and-expand 50 trường + 200 trung tâm | Arcade Class | 200 lớp Pro + 20 trường ký năm |
| **P4** · Scale | 14–24 | Mở pack SGK Cánh Diều / Chân Trời, mở leaderboard public anonymized, mở bản Việt kiều USD | Cả 3 SKU | ARR ≥ $1M, churn < 6%/tháng |
| **P5** · Expand | 24–36 | Mở pack môn 2 (Tiếng Việt hoặc Khoa học); thử thị trường Indonesia/Philippines bản hoá | Math Blast platform | Pilot pack môn 2 đạt 1.000 paid |

### 8.1. Quyết định lùi thứ tự — vì sao Flappy ra trước Candy bản đầy đủ

Mặc dù Candy là sản phẩm tạo doanh thu chính, **Flappy nên ra mắt trước 1 nhịp** vì:

1. Chi phí mua user của một game free + viral < 1/10 của một app subscription.
2. Flappy reuse §5.B.15 manifest gọn — 4–6 tuần dev là đủ.
3. Data Flappy giúp **pre-fill mastery** cho user khi convert sang Candy → cảm giác "app hiểu con tôi từ đầu" — yếu tố quan trọng để phụ huynh trả tiền.

> **Lưu ý**: số liệu 10K DAU + 5.000 paid family ở bảng trên là target lý tưởng cho team có vốn. Solo founder VPS 1GB → tham khảo lộ trình hiệu chỉnh ở `math-blast-startup-plan.md` §3.

---

## 9. Rủi ro chính & cách giảm thiểu

| Rủi ro | Mức độ | Giảm thiểu |
| --- | --- | --- |
| CT GDPT 2018 thay đổi / có bản cập nhật giữa lộ trình | Trung bình | Manifest content pack tách rời engine (§5.A.7), cho phép fork không đụng code |
| Phụ huynh không tin "game = học Toán nghiêm túc" | **Cao** | Báo cáo Zalo định kỳ + chứng nhận ViOlympic prep + endorsement giáo viên tiểu học có tiếng |
| Lệ thuộc App Store / Google Play (chính sách trẻ <13 siết) | **Cao** | Có bản PWA độc lập + landing zalo mini-app, không phụ thuộc 100% store |
| Cạnh tranh Monkey hạ giá / tung Monkey Math VN sâu hơn | **Cao** | Tận dụng 3 ngách Monkey yếu: Lớp 3–5, B2B trường, bám SGK thuần VN; ký hợp đồng độc quyền với KOL phụ huynh sớm |
| Trung tâm dạy thêm bị siết quy định | Trung bình | Pivot B2B sang trường công + bản gia đình tự học (P1, P2) — sẵn lộ trình thay thế |
| Trẻ chán nhanh / churn trong 14 ngày đầu | **Cao** | Bám pedagogy ngắn (60s + màn ngắn), Magic Feather + Soaring, time-cap soft 6 phiên/ngày — đầu tư mạnh §5.B.12 |
| Doanh thu ads thấp ở VN cho audience <13 | Trung bình | Coi Flappy là kênh acquisition (cost center), không phải profit center; ngân sách Flappy nằm trong CAC của Candy |
| Bảo mật & dữ liệu trẻ em | **Cao** | HMAC + idempotency (§9 doc), không lưu PII trẻ, parent là chủ tài khoản; sẵn nội dung cho audit pháp lý |

---

## 10. Khuyến nghị chiến lược cuối

### 10.1. Việc nên làm ngay (next 30 ngày)

1. Chốt định vị 3 SKU dưới một thương hiệu "Math Blast" — đăng ký trademark, mua tên miền cho từng SKU.
2. Phỏng vấn sâu 20 phụ huynh + 10 giáo viên + 10 trung tâm — verify willingness-to-pay và 3 lý do từ chối hàng đầu.
3. Quyết định content pack đầu là **"Kết nối tri thức với cuộc sống"** (đã ghi trong §3.2 của `math-blast-v2.md`) và lập manifest L001–L054 hoàn chỉnh để pilot.
4. Build Flappy T1–T2 vertical slice (4 tuần) để có công cụ đo virality trước khi đốt ngân sách Candy.
5. Lên kế hoạch hợp tác 2–3 KOL phụ huynh Toán + 1 hiệu trưởng tiểu học cho endorsement sớm.

### 10.2. Việc không nên làm

- **Không** tung 3 app ngay từ đầu — vượt năng lực vận hành, loãng marketing budget.
- **Không** cạnh tranh trực diện Monkey ở mầm non — họ quá mạnh ở đó, lợi thế Math Blast là Lớp 3–5 và B2B.
- **Không** mở leaderboard public hay loot box trong 12 tháng đầu — rủi ro brand & pháp lý cao.
- **Không** kéo dài tính năng vô tận trong MVP Candy — phải dừng ở World 1 + Flappy T1–T2 để pilot, không build 300 màn rồi mới ra mắt.
- **Không** hứa "tăng điểm thi cụ thể" — vi phạm quảng cáo giáo dục VN; chỉ hứa mastery rõ ràng theo skill_id.

### 10.3. Hướng đi chiến lược tổng quát

- **Định vị**: Math Blast là *nền tảng học và chơi Toán Tiểu học Việt Nam, bám chuẩn CT GDPT 2018*, không phải "game maths quốc tế dịch sang tiếng Việt".
- **Sản phẩm**: một engine + ba SKU phân tuyến rõ — Flappy (viral hook), Candy 300 (lõi subscription), Arcade Class (B2B).
- **Tài chính**: năm 1 hoà vốn vận hành, năm 2 dương biên, năm 3 đạt $1M ARR — đường lên dựa trên Candy + B2B chứ không phải ads.
- **Sứ mệnh**: giúp trẻ em VN yêu Toán — bằng phiên ngắn, an toàn, minh bạch tiến bộ, đồng hành cha mẹ & thầy cô. Mọi quyết định tính năng phải kiểm tra ngược lại 4 cam kết bất biến ở §6.

---

## Phụ chú

- Tài liệu phân tích đính kèm tham chiếu `math-blast-v2.md` các mục §3, §5.A, §5.B, §6, §9.
- Số liệu thị trường: GlobalData VN EdTech 2024, IMARC 2025, Tuổi Trẻ / VietnamPlus ViOlympic 2025–26, Thanh Niên / VTC News chi phí học thêm 2025–26.
- Bản canvas tương tác đặt tại `~/.cursor/projects/.../canvases/math-blast-market-strategy.canvas.tsx` — render thành dashboard cạnh chat.

**Đồng hành với:**

- `math-blast-v2.md` — đặc tả sản phẩm & kỹ thuật.
- `math-blast-startup-plan.md` — kế hoạch khởi nghiệp solo cho VPS 1GB + tối ưu thuế VN 2026.



