# 🎮 GAME DESIGN DOCUMENT (GDD)
## **ENGLISH SHOOTER** — Xạ thủ Tiếng Anh
**Phiên bản:** 1.0 | **Đối tượng:** Học sinh Tiểu học lớp 1–5 (6–11 tuổi)
**Nền tảng:** Mobile (iOS/Android) + Web Browser
**Thể loại:** Educational Action Game — Listening & Speaking Focus

---

## MỤC LỤC

1. [Tầm nhìn & Triết lý thiết kế](#1-tầm-nhìn--triết-lý-thiết-kế)
2. [Cấu trúc tiến trình học (Scaffolding Loop)](#2-cấu-trúc-tiến-trình-học-scaffolding-loop)
3. [Ma trận Vũ khí – Lớp – Kiến thức](#3-ma-trận-vũ-khí--lớp--kiến-thức)
4. [Hệ thống 3 Chế độ chơi](#4-hệ-thống-3-chế-độ-chơi)
5. [Kịch bản 5 Đại Boss cuối cấp](#5-kịch-bản-5-đại-boss-cuối-cấp)
6. [Gameplay Loop chi tiết theo từng khối lớp](#6-gameplay-loop-chi-tiết-theo-từng-khối-lớp)
7. [Hệ thống Listening & Speaking (Speech Engine)](#7-hệ-thống-listening--speaking-speech-engine)
8. [Kiến trúc dữ liệu (DB & API)](#8-kiến-trúc-dữ-liệu-db--api)
9. [Hệ thống âm thanh & Voice Skins](#9-hệ-thống-âm-thanh--voice-skins)
10. [Hệ thống phần thưởng & tiến trình](#10-hệ-thống-phần-thưởng--tiến-trình)
11. [Yêu cầu kỹ thuật](#11-yêu-cầu-kỹ-thuật)

---

## 1. TẦM NHÌN & TRIẾT LÝ THIẾT KẾ

### 1.1 Tầm nhìn cốt lõi

> **"Biến mỗi giờ học Tiếng Anh thành một trận chiến mà trẻ MUỐN thắng."**

English Shooter không phải là app học từ vựng có thêm hình ảnh. Đây là một **game hành động chiến thuật thực thụ** — trong đó kiến thức Tiếng Anh chính là vũ khí. Trẻ không cảm thấy mình đang "làm bài tập", mà đang "giải mã mật lệnh" để nạp đạn hạ thù.

### 1.2 Ba rào cản học Tiếng Anh được tháo gỡ

| Rào cản | Vấn đề truyền thống | Giải pháp trong game |
|---|---|---|
| **Sợ nói sai** | Trẻ im lặng vì sợ phát âm lệch | Micro là cò súng — nói mới được bắn |
| **Học vẹt** | Nhớ từ riêng lẻ, không hiểu ngữ cảnh | Từ phải dùng trong câu mới có tác dụng |
| **Mất tập trung** | Bài tập tĩnh, không có phần thưởng | Vũ khí ngầu hơn, boss hoành tráng hơn theo tiến độ |

### 1.3 Giá trị cốt lõi không thay đổi theo lớp

- **Listening trước, Speaking sau**: Trẻ luôn nghe chuẩn trước khi được yêu cầu nói
- **Phản xạ tự nhiên**: Áp lực thời gian tăng dần — trả lời đúng phải nhanh như phản xạ
- **Độ ngầu của vũ khí** là phần thưởng hữu hình cho tiến bộ học tập

---

## 2. CẤU TRÚC TIẾN TRÌNH HỌC (SCAFFOLDING LOOP)

Mỗi **Chủ đề (Theme/Chapter)** là một Mini-Campaign gồm đúng 3 giai đoạn, áp dụng nguyên lý Scaffolding (Giàn giáo ngôn ngữ):

```
┌─────────────────────────────────────────────────────────┐
│  CHỦ ĐỀ: "My Family" / "Vacation" / "Life in Future"   │
│                                                          │
│  BƯỚC 1          BƯỚC 2              BƯỚC 3             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ THU THẬP │ →  │ LÊN NÒNG     │ →  │ KHAI HỎA     │   │
│  │ ĐẠN DƯỢC │    │ VÀO VỊ TRÍ  │    │ ĐẠI BOSS     │   │
│  │          │    │              │    │              │   │
│  │ Học Từ   │    │ Đặt câu/     │    │ Viết đoạn    │   │
│  │ vựng     │    │ Ngữ pháp     │    │ văn / Nói    │   │
│  │          │    │              │    │ tự do        │   │
│  │ Thảo     │    │ Bảo vệ       │    │ Trận chiến   │   │
│  │ Nguyên   │    │ Thành phố    │    │ Boss         │   │
│  └──────────┘    └──────────────┘    └──────────────┘   │
│                                                          │
│  [Không áp lực]   [Áp lực vừa]       [Áp lực cao]      │
└─────────────────────────────────────────────────────────┘
```

### Nguyên tắc tiến trình:
- **Bước 1**: Nạp từ vào não (không có đồng hồ, được nghe lại nhiều lần)
- **Bước 2**: Dùng từ trong câu có ngữ cảnh (đồng hồ bắt đầu xuất hiện)
- **Bước 3**: Kết hợp tất cả thành ngôn ngữ hoàn chỉnh (áp lực tối đa, phần thưởng lớn nhất)

---

## 3. MA TRẬN VŨ KHÍ – LỚP – KIẾN THỨC

| Lớp | Vũ khí | Kiến thức cốt lõi | Áp lực thời gian | Bối cảnh |
|---|---|---|---|---|
| **Lớp 1** | 🪃 Súng cao su gỗ (Đạn quả nấm) | Phonics, bảng chữ cái, màu sắc, số 1–10, động vật | Không giới hạn | Thảo nguyên buổi sáng |
| **Lớp 2** | 🏹 Cung tên gỗ (Vệt sáng neon) | Sight Words, danh từ số ít/nhiều, tính từ cơ bản, giao tiếp ngắn | 30 giây (rất dài) | Làng nghề trung cổ |
| **Lớp 3** | ⚙️ Nỏ bọc đồng liên thanh (Bắn 1 ra 3) | Present Simple, Present Continuous, Wh-questions, giới từ | 20 giây/câu | Thành phố công nghiệp |
| **Lớp 4** | 🔫 Súng trường công nghệ / Súng lục | Past Simple, Future Simple (Will), động từ bất quy tắc, tìm lỗi sai | 15 giây/câu | Căn cứ quân sự tương lai |
| **Lớp 5** | 🎯 Súng bắn tỉa Sniper (Tâm ngắm laser) | Perfect tenses, câu phức, đồng nghĩa/trái nghĩa, đọc hiểu nhanh | 10 giây/câu | Thành phố Cyberpunk |

> **Nguyên tắc vàng**: Lớp càng cao → vũ khí càng ngầu → áp lực thời gian càng cao → nội dung ngôn ngữ càng phức tạp → phần thưởng càng hoành tráng.

---

## 4. HỆ THỐNG 3 CHẾ ĐỘ CHƠI

### CHẾ ĐỘ 1: 🌿 THẢO NGUYÊN THANH BÌNH (Vocabulary Sandbox)

**Vai trò sư phạm**: Nạp từ vựng mới — không áp lực, chơi để khám phá.

**Cơ chế gameplay**:
- Màn hình không hiện chữ. Loa phát âm thanh 3D: *"Shoot the [Apple]!"*
- Trẻ nghe → nhận diện biểu tượng → ngắm → bắn
- Bắn trúng: từ vựng vang lên lần 2 để khắc sâu + vàng rơi ra
- Bắn sai: mục tiêu sai cười "Oops!" + tự đọc to tên của mình (học luôn từ mình bắn nhầm)
- Không có Game Over, không mất HP

**Ví dụ cụ thể (Lớp 1 – Chủ đề Animals)**:
- Loa phát: *"Shoot the duck!"*
- Màn hình: Con vịt, con mèo, con chó bay qua
- Bắn trúng con vịt → Hiệu ứng pháo hoa mini + *"DUCK! Excellent!"*
- Bắn nhầm con mèo → Con mèo nói: *"Meow! I'm a CAT!"*

**Mục tiêu kinh tế trong game**: Tích vàng mua Skin súng, Voice Skin, trang trí căn cứ.

---

### CHẾ ĐỘ 2: 🏙️ BẢO VỆ THÀNH PHỐ (Grammar Combat)

**Vai trò sư phạm**: Dùng từ vựng trong câu có ngữ cảnh, áp lực thời gian tăng dần.

**Cơ chế gameplay**:
- Quái vật / trực thăng mang theo "lỗ hổng ngôn ngữ" đang tấn công thành phố
- Câu thoại của người dân xuất hiện: *"Help! The monster [__] coming!"*
- Trẻ phải nghe câu mẫu chuẩn (phát tự động), chọn đáp án đúng VÀ nói to qua micro
- **Trả lời ĐÚNG + NÓI ĐÚNG**: Súng nạp đạn "Cạch..." → Bắn "Đoàng!" → Địch nổ tung
- **Trả lời SAI hoặc HẾT GIỜ**: Súng kẹt đạn → Địch bắn phá thành phố → Trừ 1 HP
- **Mất 3 HP**: "Thành phố mất liên lạc" → Game Over → Chơi lại từ checkpoint

**Cơ chế Speaking tích hợp**:
1. Game phát câu mẫu chuẩn bản xứ qua loa
2. Trẻ nghe → dùng tay chọn mảnh ghép theo đúng thứ tự (luyện Listening)
3. Súng vào trạng thái "Chờ kích hoạt" — hiệu ứng đèn nhấp nháy
4. Trẻ giữ nút micro → đọc to câu vừa ghép (luyện Speaking)
5. AI nhận diện ≥ 70% (Lớp 1–2) hoặc ≥ 85% (Lớp 4–5) → Súng khai hỏa

---

### CHẾ ĐỘ 3: 👑 TRẬN CHIẾN ĐẠI BOSS (Paragraph Boss Fight)

**Vai trò sư phạm**: Kết hợp tất cả kỹ năng — nghe hiểu, đặt câu, viết/nói đoạn văn hoàn chỉnh.

**Cơ chế gameplay**:
- Boss xuất hiện với thanh máu khổng lồ và hiệu ứng hoành tráng
- Mỗi đòn tấn công Boss = hoàn thành một câu trong đoạn văn
- Đọc/nói đúng câu nào → Railgun/Laser bắn phá Boss theo nhịp đọc
- **Đọc mượt mà** → Súng bắn liên thanh bão đạn
- **Đọc vấp, ngập ngừng** → Súng kẹt đạn, Boss phản công

**Cơ chế Presentation Speaking (Lớp 4–5)**:
- Trẻ không chỉ đọc văn mẫu, mà phải TỰ CHỌN từ/cụm từ từ "kho đạn" để hoàn thiện đoạn văn
- Đoạn văn kết quả được lưu vào **Commander's Journal** (Nhật ký Xạ thủ)
- Trẻ có thể chọn 2 hướng kể chuyện khác nhau (Ví dụ: kỳ nghỉ ở biển vs ở núi)

---

## 5. KỊCH BẢN 5 ĐẠI BOSS CUỐI CẤP

### 👑 LỚP 1: "KING CHICKEN" — Vua Gà Đột Biến
**Thử thách**: Phonics & Âm thanh cơ bản

**Kịch bản vào màn**:
- Mặt đất rung chuyển. Một chú gà khổng lồ đột biến trồi lên từ chuồng gà. Vương miện vàng phát sáng, đôi mắt đỏ rực nhìn thẳng vào màn hình.
- Loa phát: *"BWAAAK! I am the KING! Can you understand my EGG CODES?!"*

**Cơ chế chiến đấu**:
- Vua Gà gáy ra các quả trứng phát sáng. Mỗi trứng phát ra một âm thanh: */sh/*, */ch/*, */p/*, */b/*...
- Xung quanh Boss xuất hiện 4 rổ mang hình ảnh + chữ: **Fish, Chair, Pen, Ball**
- Trẻ nghe âm → dùng súng cao su bắn trứng vào đúng rổ có từ chứa âm đó
- Bắn ĐÚNG: Trứng biến thành đá đập vào đầu Boss, Boss choáng
- Bắn SAI: Trứng nổ, lòng đỏ phủ mờ màn hình + tiếng gà cười *"BWAK BWAK BWAK!"*

**Phase 2 (50% HP)**: Boss điên cuồng — bắn ra 2 trứng cùng lúc, tốc độ nhanh hơn

**Điều kiện thắng**: Phá hết 10 trứng đúng → Boss ngã ngửa, vương miện bay ra → Trẻ nhặt được "Egg Crown" (trang trí súng)

**Phần thưởng**: Mở khóa Cung tên gỗ cho Lớp 2 + 500 vàng

---

### 🦅 LỚP 2: "FIRE PHOENIX" — Phượng Hoàng Lửa Ma Thuật
**Thử thách**: Word Matching — Nối từ Anh–Việt theo chủ đề

**Kịch bản vào màn**:
- Bầu trời bùng cháy. Phượng Hoàng khổng lồ sải cánh bay từ mặt trời xuống.
- Loa phát: *"The Phoenix speaks FIRE! Extinguish me with your WORDS... if you dare!"*

**Cơ chế chiến đấu**:
- Phượng Hoàng tung ra 3 lá chắn lửa, mỗi lá khắc một từ tiếng Việt: **Trường học / Gia đình / Thú cưng**
- Cung tên của trẻ nạp 3 mũi tên neon mang từ tiếng Anh: **School / Family / Pet**
- Trẻ phải nghe loa đọc từ tiếng Anh → bắn mũi tên đó vào đúng lá chắn tiếng Việt
- Dập đúng 1 lá chắn: Lửa tắt, Boss mất 1/3 máu
- Bắn sai: Lửa bùng to hơn, thanh HP của thành phố phía sau giảm

**Phase 2 (33% HP còn lại)**: Phượng Hoàng tung 5 lá chắn cùng lúc, tốc độ bay tăng 50%

**Điều kiện thắng**: Dập hết 3 lá chắn → Phượng Hoàng đóng băng + rơi xuống

**Phần thưởng**: Mở khóa Nỏ liên thanh cho Lớp 3 + Voice Skin "Phoenix Roar"

---

### 🛸 LỚP 3: "ZEPPELIN FORTRESS" — Khinh Khí Cầu Pháo Đài
**Thử thách**: Hội thoại giao tiếp — Wh-questions & Present Continuous

**Kịch bản vào màn**:
- Một khinh khí cầu khổng lồ hình pháo đài bay đến che khuất bầu trời
- Loa phát: *"ATTENTION, little soldier! Answer my questions... or watch your city BURN!"*

**Cơ chế chiến đấu**:
- Khinh khí cầu thả xuống các thùng thuốc nổ có đếm ngược **20 giây**
- Trên thùng là câu hỏi giao tiếp: *"Where are you from?"* / *"What are you doing now?"*
- Xung quanh bay các mục tiêu nhỏ mang câu trả lời khác nhau
- Trẻ phải:
  1. Nghe câu hỏi (loa đọc tự động)
  2. Chọn câu trả lời đúng bằng cách ngắm bắn mục tiêu
  3. Đọc to câu trả lời qua micro để kích hoạt súng
- Bắn ĐÚNG + NÓI ĐÚNG: Nỏ liên thanh bắn dây xích kéo bom ngược lại → Nổ vào khinh khí cầu
- Hết giờ: Bom nổ → thành phố mất 1 HP

**Phase 2 (50% HP)**: 2 thùng bom rơi xuống cùng lúc, đếm ngược còn 15 giây

**Điều kiện thắng**: Phá hủy 8 thùng bom → Khinh khí cầu bốc cháy rơi xuống

**Phần thưởng**: Mở khóa Súng trường cho Lớp 4 + "Airship Captain" Voice Skin

---

### 🕷️ LỚP 4: "GRAMMAR MECHA-SPIDER" — Robot Nhện Ma Trận
**Thử thách**: Ngữ pháp — Past Simple, Future Will, Động từ bất quy tắc

**Kịch bản vào màn**:
- Mặt đất nứt vỡ. Robot Nhện cơ học khổng lồ bò ra từ lòng đất. Âm thanh kim loại, đèn đỏ chớp nháy.
- Loa phát: *"GRAMMAR ERROR DETECTED. PREPARE FOR GRAMMATICAL ELIMINATION!"*

**Cơ chế chiến đấu**:
- Robot Nhện có **6 chiếc chân** bảo vệ, mỗi chân mang một dạng động từ: *go / went / gone / going / goes / had gone*
- Trên thân nhện hiện **Mốc thời gian**: *"Yesterday, I ___ to school."*
- Loa đọc câu đầy đủ với đáp án đúng một lần (trẻ nghe trước)
- Trẻ phải dùng Súng trường ngắm bắn chính xác vào **chân mang động từ đúng** (*went*)
- Bắn ĐÚNG: Chân nhện gãy, Boss mất máu + hiệu ứng điện tóe lửa
- Bắn SAI: Súng bị giật điện, trẻ mất lượt 3 giây

**Phase 2 (4 chân còn lại)**: 8 động từ xuất hiện, thêm câu phức: *"If I had time yesterday, I ___ him."*

**Phase 3 (2 chân cuối)**: Boss di chuyển, trẻ phải bắn đúng trong lúc Boss đang chạy

**Điều kiện thắng**: Bắn gãy 6 chân → Robot sụp đổ

**Phần thưởng**: Mở khóa Súng Sniper cho Lớp 5 + "Mecha Voice" Skin

---

### 🚢 LỚP 5: "CYBER-MOTHERSHIP" — Mẫu Hạm Không Gian AI
**Thử thách**: Reading Comprehension nhanh + Speaking đoạn văn tự do

**Kịch bản vào màn**:
- Bầu trời tắt tối. Một con tàu mẹ AI khổng lồ từ từ xuất hiện trong đám mây, bao phủ cả thành phố.
- Loa phát (giọng AI lạnh lùng): *"Human language is inefficient. I will demonstrate SUPERIOR communication. Unless... you can match me."*

**Cơ chế chiến đấu — 3 Phase**:

**Phase 1 — Phá khiên (Reading Speed)**:
- Tàu mẹ bật khiên năng lượng. Màn hình bật chế độ ống nhòm Sniper
- Một đoạn văn 3–4 câu xuất hiện trên màn hình radar, hiển thị trong 15 giây
- Câu hỏi đọc hiểu xuất hiện: *"What is the main idea?"* / *"What will happen if...?"*
- 4 lõi năng lượng trên khiên mang 4 từ khóa — một từ đúng, ba từ nhiễu
- Trẻ đọc nhanh → ngắm bắn vào lõi mang từ khóa đúng
- Bắn đúng 3 lõi → Khiên nứt vỡ

**Phase 2 — Tấn công lõi (Speaking paragraph)**:
- Tàu mẹ phơi lõi năng lượng chính
- Màn hình hiện 5 ô trống trong một đoạn văn về chủ đề đã học
- "Kho đạn từ" xuất hiện bên dưới — trẻ chọn từ phù hợp để điền
- Sau khi điền đủ: Trẻ đọc to toàn bộ đoạn văn qua micro
- Đọc trôi chảy → Railgun bắn liên thanh vào lõi tàu → Boss mất 60% HP

**Phase 3 — Đòn quyết định (Free Speaking)**:
- Boss phản công. Tàu mẹ hỏi một câu hỏi mở bằng tiếng Anh: *"Do you think robots will replace humans? Tell me why."*
- Trẻ có 30 giây tự nói bằng tiếng Anh (ít nhất 2 câu)
- Hệ thống chấm điểm dựa trên: số từ tiếng Anh nhận diện được + confidence score
- Đạt ngưỡng → Siêu vũ khí Omega Railgun kích hoạt → Tàu mẹ nổ tung trong tiếng hoan hô

**Điều kiện thắng**: Hoàn thành cả 3 Phase

**Phần thưởng**: Màn hình lễ tốt nghiệp "Global Commander" — tấm bằng tiếng Anh hiện ra, súng bắn tỉa cất vào hộp nhung, nhạc lên cao trào, confetti đổ xuống. Mở khóa toàn bộ nội dung thưởng.

---

## 6. GAMEPLAY LOOP CHI TIẾT THEO TỪNG KHỐI LỚP

### 🧸 LỚP 1 — Chủ đề mẫu: "MY FAMILY"

**Bước 1 — Thảo Nguyên (Từ vựng)**:
- Loa phát: *"Shoot MOM!"* → Bắn quả táo mang hình bà mẹ
- Loa phát: *"Shoot DAD!"* → Bắn quả táo mang hình người cha
- Từ vựng mục tiêu: `mom, dad, baby, sister, brother, family`
- Không hiện chữ, chỉ có hình ảnh + âm thanh

**Bước 2 — Bảo Vệ Thành Phố (Đặt câu)**:
- Quái vật mang bảng trống: *"This is my [____]."*
- Loa đọc: *"This is my mom."*
- 3 mục tiêu bay: `mom / dad / cat` → Trẻ nghe → bắn đúng mục tiêu `mom` → Nói to: *"This is my mom"* → Súng khai hỏa

**Bước 3 — Đại Boss Vua Gà (Đoạn văn)**:
- Boss đẻ 3 trứng lớn chứa 3 câu
- Trứng 1: *"This is my family."*
- Trứng 2: *"I love my mom."*
- Trứng 3: *"I love my dad."*
- Trẻ phải nghe và bắn theo thứ tự 1→2→3 (luyện logic đoạn văn)

---

### 🧸 LỚP 2 — Chủ đề mẫu: "MY PETS"

**Bước 1 — Thảo Nguyên**:
- Các con chim mang từ bay qua, loa đọc tên từng con
- Từ vựng: `dog, cat, rabbit, cute, playful, small, big`
- Bắn đúng theo lệnh loa

**Bước 2 — Bảo Vệ Thành Phố**:
- Ghép câu: *"I / have / a / [cute] / dog."*
- Loa đọc câu mẫu: *"I have a cute dog."*
- Trẻ bắn các mảnh câu theo thứ tự đúng → Nói to câu hoàn chỉnh

**Bước 3 — Đại Boss Phượng Hoàng**:
- Boss tung ra đoạn văn bị xáo trộn vị trí các câu
- 3 câu cần sắp xếp lại:
  - *"I have a small cat."*
  - *"Its name is Kitty."*
  - *"It is very playful."*
- Bắn mũi tên neon để sắp xếp câu đúng thứ tự logic

---

### 🚀 LỚP 3 — Chủ đề mẫu: "OUR SCHOOL YEAR"

**Bước 1 — Thảo Nguyên**:
- Từ vựng chủ đề trường học: `math, English, art, reading, drawing, classroom, teacher`
- Loa phát lệnh: *"Find MATH and shoot it!"*

**Bước 2 — Bảo Vệ Thành Phố**:
- Câu cần hoàn chỉnh: *"We are [learning] English now."*
- Loa đọc câu chuẩn: *"We are learning English now."*
- Trẻ nghe → bắn mục tiêu mang `learning` (thay vì `learn / learned / learns`) → Nói to

**Bước 3 — Khinh Khí Cầu**:
- Điền từ vào đoạn văn 4 câu về một ngày ở trường
- Trả lời đúng mỗi từ khuyết = cắt đứt một thùng bom
- Toàn bộ 4 câu đúng = khinh khí cầu bị phá hủy

---

### 🚀 LỚP 4 — Chủ đề mẫu: "A WONDERFUL VACATION"

**Bước 1 — Thảo Nguyên**:
- Săn các động từ bất quy tắc: `went, ate, swam, bought, saw, met`
- Loa phát: *"In the past, we don't say GO — we say... WENT! Shoot WENT!"*

**Bước 2 — Bảo Vệ Thành Phố**:
- Tìm và bắn lỗi sai: *"Last summer, I **go** to Phu Quoc."*
- Trẻ nhìn câu → nghe câu đúng qua loa → bắn vào từ `go` → Nói: *"Last summer, I went to Phu Quoc."*

**Bước 3 — Robot Nhện**:
- Thân nhện hiện câu hỏi: *"What did he eat?"*
- 6 chân mang 6 câu từ nhật ký kỳ nghỉ
- Trẻ đọc nhanh đoạn văn → bắn vào chân chứa câu trả lời đúng

---

### 🚀 LỚP 5 — Chủ đề mẫu: "LIFE IN THE FUTURE"

**Bước 1 — Thảo Nguyên**:
- Bắn tỉa từ vựng công nghệ: `flying cars, robots, renewable energy, space travel, artificial intelligence`
- Áp lực: Từ di chuyển nhanh, có mục tiêu giả (từ sai chính tả / từ không liên quan)

**Bước 2 — Bảo Vệ Thành Phố (10 giây/câu)**:
- Câu điều kiện: *"If we have robots, they [will do] our housework."*
- Loa đọc mẫu 1 lần → Trẻ phải phản xạ ngay

**Bước 3 — Mẫu Hạm AI**:
- Phase 1: Đọc đoạn văn 4 câu về 2050 → Trả lời câu hỏi → Phá khiên
- Phase 2: Điền vào đoạn văn → Đọc to đoạn văn hoàn chỉnh
- Phase 3: Tự nói 2–3 câu về tương lai theo ý mình → Nhận Omega Railgun

---

## 7. HỆ THỐNG LISTENING & SPEAKING (SPEECH ENGINE)

### 7.1 Nguyên tắc cốt lõi
> **Nghe TRƯỚC — Nói SAU — Không bao giờ ép nói khi chưa nghe đủ.**

Mọi câu mẫu đều được phát âm bởi giọng đọc bản xứ chuẩn trước khi trẻ được yêu cầu nói.

### 7.2 Luồng xử lý giọng nói (Web Speech API)

```
Trẻ giữ nút MIC
        ↓
SpeechRecognition khởi động (lang = 'en-US')
        ↓
Trẻ nói → API trả về: transcript + confidence
        ↓
       [Lớp 1-2]              [Lớp 3-5]
  Keyword Matching        Phrase/Strict Matching
  confidence ≥ 0.50       confidence ≥ 0.82
  Chỉ cần chứa từ         Phải khớp cả câu
  khóa đúng               + từ nối
        ↓                       ↓
      ĐẠT                   ĐẠT / KHÔNG ĐẠT
   Súng khai hỏa!          Súng khai hỏa! / Kẹt đạn
```

### 7.3 Bảng cấu hình theo khối lớp

| Lớp | Thuật toán | Confidence ngưỡng | Ví dụ target | Ví dụ trẻ nói | Kết quả |
|---|---|---|---|---|---|
| 1 | Keyword | ≥ 0.50 | `apple` | *"An... áp-pờ"* → `an apple` (0.55) | ✅ ĐẠT |
| 2 | Keyword | ≥ 0.55 | `big dog` | *"big dog"* (0.60) | ✅ ĐẠT |
| 3 | Partial phrase | ≥ 0.70 | `she is reading` | *"she is reading"* (0.75) | ✅ ĐẠT |
| 4 | Phrase match | ≥ 0.80 | `I went to school` | Đọc rời rạc (0.62) | ❌ KẸT ĐẠN |
| 5 | Strict + liaison | ≥ 0.85 | `check it out` | Nối âm chuẩn (0.91) | ✅ ĐẠT |

### 7.4 "Bẫy nối âm" cho Lớp 4–5

Web Speech API được huấn luyện trên tiếng Anh bản xứ — nếu trẻ đọc rời rạc, confidence sẽ tụt thấp. Tận dụng đặc điểm này để buộc trẻ nối âm tự nhiên:

| Chủ đề | Cụm từ | Phát âm chuẩn nối âm |
|---|---|---|
| Du lịch | `pack up` | /pæk ʌp/ |
| Du lịch | `take off` | /teɪk ɒf/ |
| Công nghệ | `plug in` | /plʌɡ ɪn/ |
| Công nghệ | `think about it` | /θɪŋk əˈbaʊt ɪt/ |
| Đời sống | `wake up` | /weɪk ʌp/ |
| Đời sống | `clean up` | /kliːn ʌp/ |

### 7.5 Xử lý khi Speech API thất bại

- Nếu confidence < ngưỡng: Súng kẹt đạn + Loa phát lại câu mẫu chuẩn → Trẻ nghe lại (shadowing)
- Sau 3 lần thất bại liên tiếp: Game tự động hạ ngưỡng confidence 10% (tránh frustration)
- Nếu thiết bị không hỗ trợ micro: Chuyển sang chế độ "Tap to shoot" (chọn đáp án bằng tay) — mất điểm Speaking bonus nhưng vẫn chơi được

---

## 8. KIẾN TRÚC DỮ LIỆU (DB & API)

### 8.1 Sơ đồ cơ sở dữ liệu

```sql
-- Bảng lớp học
grades (
  id          INT PRIMARY KEY,
  name        VARCHAR(20),       -- "Lớp 1", "Lớp 5"
  weapon_id   INT FK weapons,
  bg_color    VARCHAR(7)         -- Màu chủ đạo của màn hình lớp
)

-- Bảng vũ khí
weapons (
  id            INT PRIMARY KEY,
  name          VARCHAR(50),     -- "Súng cao su gỗ"
  asset_id      VARCHAR(100),    -- Tên file sprite/3D model
  shoot_sfx_url VARCHAR(200),    -- URL âm thanh bắn súng
  reload_sfx_url VARCHAR(200)
)

-- Bảng chủ đề
themes (
  id               INT PRIMARY KEY,
  grade_id         INT FK grades,
  title            VARCHAR(100),  -- "My Family"
  order_index      INT,           -- Thứ tự chương trong lớp
  background_scene VARCHAR(50),   -- "savannah", "cyberpunk_city"
  boss_id          INT FK bosses,
  is_active        BOOLEAN DEFAULT true
)

-- Bảng boss
bosses (
  id           INT PRIMARY KEY,
  name         VARCHAR(100),    -- "King Chicken"
  asset_id     VARCHAR(100),
  intro_audio  VARCHAR(200),    -- URL lời thoại vào màn
  defeat_audio VARCHAR(200)
)

-- Bảng giai đoạn học
game_stages (
  id                   INT PRIMARY KEY,
  theme_id             INT FK themes,
  stage_type           ENUM('vocab','sentence','paragraph'),
  instruction_audio    VARCHAR(200),  -- Hướng dẫn bằng tiếng Anh
  time_limit_seconds   INT,           -- NULL = không giới hạn
  speaking_required    BOOLEAN,
  min_confidence       DECIMAL(3,2)   -- 0.50, 0.82...
)

-- Bảng nội dung chi tiết
stage_items (
  id             INT PRIMARY KEY,
  stage_id       INT FK game_stages,
  item_type      ENUM('target','distractor','keyword'),
  target_text    TEXT,          -- Từ/câu/đoạn đúng
  audio_url      VARCHAR(200),  -- Âm thanh bản xứ chuẩn
  visual_asset   VARCHAR(100),  -- Hình ảnh mục tiêu
  translation_vi VARCHAR(200),  -- Dịch tiếng Việt (tooltip)
  options_json   JSON,          -- Đáp án nhiễu
  order_index    INT            -- Thứ tự trong đoạn văn
)
```

### 8.2 API Endpoints

```
GET  /api/v1/grades                           -- Danh sách lớp
GET  /api/v1/grades/:id/themes                -- Danh sách chủ đề của lớp
GET  /api/v1/themes/:id/stages                -- 3 giai đoạn của chủ đề
GET  /api/v1/stages/:id/items                 -- Nội dung chi tiết
POST /api/v1/progress                         -- Lưu tiến độ học sinh
GET  /api/v1/students/:id/journal             -- Lấy Commander's Journal
POST /api/v1/students/:id/journal             -- Lưu đoạn văn vào journal

-- Admin endpoints (quản lý nội dung)
POST /api/v1/admin/themes                     -- Thêm chủ đề mới
PUT  /api/v1/admin/themes/:id                 -- Sửa chủ đề
POST /api/v1/admin/stage_items                -- Thêm nội dung
PUT  /api/v1/admin/stage_items/:id            -- Sửa nội dung
```

### 8.3 Mẫu JSON API Response

```json
GET /api/v1/grades/5/themes

{
  "status": "success",
  "data": {
    "grade_id": 5,
    "grade_name": "Lớp 5",
    "weapon": {
      "name": "Sniper Laser Gun",
      "asset_id": "weapon_sniper_v2",
      "shoot_sfx": "https://cdn.game.com/sfx/sniper_laser.mp3"
    },
    "themes": [
      {
        "theme_id": 501,
        "title": "Life in the Future",
        "chapter_index": 1,
        "background_scene": "cyberpunk_city",
        "boss": {
          "name": "Cyber-Mothership",
          "asset_id": "boss_mothership",
          "intro_audio": "https://cdn.game.com/audio/boss/mothership_intro.mp3"
        },
        "stages": [
          {
            "stage_id": 5011,
            "stage_type": "vocab",
            "instruction_audio": "https://cdn.game.com/audio/inst/l5_vocab.mp3",
            "time_limit_seconds": null,
            "speaking_required": false,
            "items": [
              {
                "id": 1,
                "item_type": "target",
                "target_text": "flying cars",
                "audio_url": "https://cdn.game.com/audio/vocab/flying_cars.mp3",
                "visual_asset": "target_flying_car",
                "translation_vi": "xe hơi bay"
              }
            ]
          },
          {
            "stage_id": 5012,
            "stage_type": "sentence",
            "instruction_audio": "https://cdn.game.com/audio/inst/l5_sent.mp3",
            "time_limit_seconds": 10,
            "speaking_required": true,
            "min_confidence": 0.85,
            "items": [
              {
                "id": 21,
                "item_type": "target",
                "target_text": "In 2050, we will live in flying cars.",
                "audio_url": "https://cdn.game.com/audio/sent/s501_1.mp3",
                "options_json": {
                  "scrambled": ["In 2050,", "we", "will", "live", "in", "flying cars."],
                  "distractors": ["drove", "lived", "are living"]
                }
              }
            ]
          },
          {
            "stage_id": 5013,
            "stage_type": "paragraph",
            "time_limit_seconds": 30,
            "speaking_required": true,
            "min_confidence": 0.82,
            "boss_fight": true,
            "paragraph_target": "Welcome to 2050. Robots will do our housework. Humans will travel by flying cars. We will protect the environment with renewable energy.",
            "audio_full": "https://cdn.game.com/audio/para/p501.mp3",
            "blanks": [
              { "position": 2, "keyword": "Robots", "distractors": ["Cars", "Dogs", "Ships"] },
              { "position": 3, "keyword": "flying cars", "distractors": ["trains", "buses", "boats"] },
              { "position": 4, "keyword": "renewable energy", "distractors": ["coal", "oil", "fire"] }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 9. HỆ THỐNG ÂM THANH & VOICE SKINS

### 9.1 Triết lý âm thanh

> **Trẻ phải "tắm trong tiếng Anh" một cách tự nguyện.** Mọi âm thanh trong game — từ tiếng bắn súng đến nhạc nền — đều phải kéo trẻ vào việc muốn bật loa to hơn, chứ không phải tắt đi.

### 9.2 Voice-Weapons System (Vũ khí tích hợp ngôn ngữ)

| Vũ khí | Âm thanh nạp đạn | Âm thanh bắn | Âm thanh thắng |
|---|---|---|---|
| Súng cao su (L1) | *"Pull... pull..."* (tiếng kéo dây chun) | Tiếng *"Thwack!"* + tên từ vựng: *"Great! [Apple]!"* | *"Excellent shot, Commander!"* |
| Cung tên gỗ (L2) | *"Draw... aim..."* | Tiếng rít của mũi tên + từ: *"Bullseye! [School]!"* | *"Perfect! You nailed it!"* |
| Nỏ liên thanh (L3) | Tiếng cơ khí *"Click-click-click"* | Bắn 3 mũi liên tiếp + 3 từ trong câu | *"Triple kill! Outstanding!"* |
| Súng trường (L4) | *"Locked and loaded!"* | Tiếng nổ lớn + câu ngữ pháp đúng | *"Grammar destroyed! Impressive!"* |
| Sniper (L5) | *"Target confirmed... [renewable energy]... charged!"* | Tiếng siêu thanh chấn động | *"One shot, one kill. Flawless!"* |

### 9.3 Voice Skins (Phần thưởng đổi giọng súng)

Trẻ dùng linh kiện thu được từ Boss để mở khóa và trang bị Voice Skin:

| Voice Skin | Mở khóa từ | Phong cách | Câu thoại mẫu |
|---|---|---|---|
| **Robot Transformer** | Boss Lớp 1 | Giọng robot biến hình | *"WEAPON SYSTEM: ACTIVATED. FIRE!"* |
| **Phoenix Roar** | Boss Lớp 2 | Uy nghi, ma mị | *"The Phoenix speaks! RISE!"* |
| **Airship Captain** | Boss Lớp 3 | Dũng cảm, phiêu lưu | *"Full speed ahead! FIRE THE CANNONS!"* |
| **Mecha Voice** | Boss Lớp 4 | Cơ học, lạnh lùng | *"Grammar module: ENGAGED. DESTROY."* |
| **AI Commander** | Boss Lớp 5 | Tương lai, uy quyền | *"Calculating trajectory... OBLITERATE!"* |
| **Dragon Master** | Bí mật (hoàn thành 100%) | Cổ điển, huyền bí | *"By the ancient tongue... UNLEASH!"* |

### 9.4 Nhạc nền động (Dynamic Background Music)

| Trạng thái game | Phong cách nhạc | Mô tả |
|---|---|---|
| **Menu / Căn cứ** | Acoustic nhẹ nhàng | Guitar + piano, không lời |
| **Thảo Nguyên (Vocab)** | Folk adventure | Nhịp thong thả, vui tươi, khuyến khích |
| **Bảo Vệ Thành Phố** | Action rock | Nhịp trống dồn dập, tạo áp lực phản xạ |
| **Trận Boss (Phase 1)** | Epic orchestral | Âm nhạc điện ảnh, căng thẳng |
| **Trận Boss (Phase 2-3)** | Cyberpunk orchestra | Điện tử + dàn nhạc, cực kỳ thôi thúc |
| **Thắng Boss** | Victory fanfare | Tiếng Anh hô vang: *"VICTORY! OUTSTANDING!"* |
| **Thua / Game Over** | Tĩnh lặng + tense | Nhạc thấp dần, giọng: *"Try again, Commander."* |

---

## 10. HỆ THỐNG PHẦN THƯỞNG & TIẾN TRÌNH

### 10.1 Kinh tế trong game

| Nguồn vàng | Lượng vàng |
|---|---|
| Bắn trúng trong Thảo Nguyên | +5/lần |
| Hoàn thành câu đúng trong Bảo Vệ Thành Phố | +20/câu |
| Speaking thành công (đạt confidence) | +30 bonus |
| Hoàn thành Boss Fight | +200 |
| Điểm hoàn hảo (không mất HP) | +100 bonus |

### 10.2 Commander's Journal (Nhật ký Xạ thủ)

- Mỗi đoạn văn trẻ tự viết/hoàn thiện ở Bước 3 được lưu tự động
- Trẻ có thể xem lại, nghe lại giọng đọc của mình
- Phụ huynh/giáo viên có thể truy cập để theo dõi tiến trình
- Đoạn văn có thể chia sẻ (in hoặc gửi qua email)

### 10.3 Hệ thống Rank (Cấp bậc Xạ thủ)

| Cấp bậc | Điều kiện | Hiệu ứng |
|---|---|---|
| 🥉 **Recruit** (Tân binh) | Hoàn thành Chủ đề 1 | Badge đồng trên avatar |
| 🥈 **Soldier** (Chiến sĩ) | Hoàn thành tất cả chủ đề 1 lớp | Badge bạc + khung avatar |
| 🥇 **Commander** (Chỉ huy) | Đánh bại Boss cuối cấp | Badge vàng + hiệu ứng hào quang |
| 💎 **Global Commander** | Hoàn thành tất cả Lớp 1–5 | Bằng khen tiếng Anh + Dragon Voice Skin |

### 10.4 Màn hình "Lễ Trưởng Thành" (Graduation Screen)

Khi thắng Boss cuối mỗi lớp:
1. Súng hiện tại được "cất vào hộp nhung" với hiệu ứng chậm rãi, trân trọng
2. Tấm bằng khen hiện ra với tên trẻ và cấp lớp (bằng tiếng Anh)
3. Súng mới của lớp tiếp theo tự động mở khóa với hiệu ứng tia sáng
4. Nhạc Victory fanfare vang lên

---

## 11. YÊU CẦU KỸ THUẬT

### 11.1 Stack kỹ thuật đề xuất

| Thành phần | Công nghệ | Lý do |
|---|---|---|
| **Game Engine** | Cocos Creator 3.x hoặc Phaser 3 | Tối ưu cho mobile HTML5 game |
| **Speech Recognition** | Web Speech API (SpeechRecognition) | Miễn phí, không cần server, chạy trên thiết bị |
| **Backend API** | Node.js + Express hoặc Python FastAPI | REST API nhẹ, dễ mở rộng |
| **Database** | PostgreSQL (RDBMS) | Quan hệ dữ liệu phức tạp, dễ query |
| **Audio CDN** | Cloudflare R2 hoặc AWS S3 | Phát audio nhanh, ổn định |
| **Admin CMS** | Strapi hoặc tự xây | Quản lý nội dung không cần dev |

### 11.2 Yêu cầu nền tảng cho Speech API

- **Chrome** (Android + Desktop): ✅ Hỗ trợ đầy đủ
- **Safari** (iOS): ✅ Hỗ trợ từ iOS 14.5+
- **Firefox**: ⚠️ Hỗ trợ hạn chế — cần fallback
- **Yêu cầu**: HTTPS bắt buộc, quyền truy cập micro phải được cấp

### 11.3 Xử lý offline & caching

- Tất cả audio của chủ đề hiện tại được tải sẵn (prefetch) khi vào màn chơi
- Game stages có thể chơi offline sau khi tải lần đầu
- Progress sync khi có kết nối trở lại

### 11.4 Cấu hình độ khó (Admin panel)

Giáo viên/Admin có thể điều chỉnh qua CMS:
- `time_limit_seconds`: Thời gian mỗi câu
- `min_confidence`: Ngưỡng confidence Speaking
- `hp_count`: Số HP của thành phố
- `speaking_required`: Bật/tắt tính năng Speaking cho từng stage

---

## PHỤ LỤC: BẢNG KIỂM TRA THIẾT KẾ

### ✅ Checklist trước khi xuất bản mỗi chủ đề mới

- [ ] Tất cả audio từ vựng/câu đều được đọc bởi giọng native speaker chuẩn
- [ ] Mỗi stage_item có đủ: `target_text`, `audio_url`, `visual_asset`, `translation_vi`
- [ ] Số lượng distractors ≥ 2 cho mỗi câu hỏi
- [ ] Đã test Speech API với ít nhất 5 trẻ ở đúng lớp mục tiêu
- [ ] Nhạc nền và SFX đã được mix không che giọng đọc
- [ ] Boss fight đã test đủ 3 phase, không bị softlock
- [ ] Đoạn văn Boss Fight có độ dài 3–5 câu, ngữ nghĩa logic, phù hợp độ tuổi

---

*Tài liệu này là bản sống — cần cập nhật sau mỗi vòng test với trẻ thực tế.*
*Phiên bản tiếp theo sẽ bổ sung: Multiplayer co-op mode, AI adaptive difficulty, Parent dashboard.*
