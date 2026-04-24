# KidCoin Game Hub - Tài liệu Kiến trúc & Chiến lược

Tài liệu này mô tả chi tiết về cấu trúc của module Game Hub, danh mục các trò chơi dự kiến, các vị trí chèn quảng cáo và định hướng phát triển dài hạn nhằm kết nối với hệ sinh thái KidCoin.

---

## 1. Tổng quan trang Game Hub (`/game`)
Trang Game Hub được thiết kế như một Arcade Game Box trực tuyến, hoạt động hoàn toàn độc lập với hệ thống quản lý việc nhà bên trong.
- **Mục tiêu:** Cung cấp sân chơi miễn phí, an toàn cho trẻ em; đồng thời đóng vai trò là phễu Marketing (Lead Magnet) thu hút người dùng biết đến ứng dụng KidCoin.
- **Thiết kế (UI/UX):** Giao diện sử dụng phong cách Dark Mode cao cấp kết hợp với Glassmorphism và hiệu ứng Neon (Glow) để tạo sự phấn khích và hiện đại.
- **Truy cập:** Không yêu cầu đăng nhập. Người dùng vãng lai có thể chơi ngay lập tức.
- **Điều hướng:** Có các nút kêu gọi hành động (Call to Action - CTA) tinh tế hướng người dùng tải/truy cập vào "KidCoin App" hoặc "Đăng nhập".

---

## 2. Quy hoạch Vị trí Quảng cáo (Ad Slots)
Trang Game Hub đã được thiết kế sẵn các khối quảng cáo (Placeholder) để sẵn sàng cho chiến lược Monetization trong tương lai. 
*Lưu ý: Hiện tại, các vị trí này đang được **ẨN** thông qua biến điều kiện Jinja2 `{% if show_ads %}` trong mã nguồn (do chưa có dữ liệu quảng cáo thực).*

Các vị trí đã được quy hoạch bao gồm:
1. **Top Ad Banner (Dưới Hero Section, trên danh sách game):** 
   - **Kích thước dự kiến:** 728x90 px hoặc Responsive Banner.
   - **Mục đích:** Vị trí "vàng" (Above the fold), có độ hiển thị cao nhất, thu hút ánh nhìn ngay khi người dùng lướt qua phần giới thiệu.
2. **Bottom Ad Banner (Dưới cùng danh sách game, trên Footer):**
   - **Kích thước dự kiến:** 728x90 px.
   - **Mục đích:** Quảng cáo nhắc lại hoặc quảng cáo nhận diện thương hiệu, tiếp cận người dùng sau khi họ đã lướt xem hết danh mục game.
3. **In-Game Ads (Dự kiến mở rộng):**
   - **Quảng cáo xen kẽ (Interstitial Ads):** Hiển thị khi trẻ "Game Over" hoặc chuyển màn.
   - **Quảng cáo tặng thưởng (Rewarded Ads):** (Áp dụng khi liên kết với app) Xem video để nhận thêm lượt chơi hoặc nhận thêm Coin.

---

## 3. Phân loại & Danh mục Game
Các mini-game (HTML5/JS) sẽ được bổ sung dần vào Game Hub và được phân chia theo các nhóm chủ đề nhằm phát triển đa dạng kỹ năng cho trẻ.

### 🧠 3.1. Nhóm Game Tư duy & Học tập (Educational & Logic)
Giúp trẻ phát triển não bộ, rèn luyện tính toán, từ vựng và tư duy logic.
- **2048 (Đã có):** Tư duy logic, cộng dồn số liệu, lên chiến lược gộp khối.
- **Math Blast:** Trả lời nhanh các phép tính toán học (Cộng/Trừ/Nhân/Chia) trước khi hết giờ.
- **Word Scramble:** Ghép các chữ cái bị xáo trộn thành từ vựng tiếng Anh/Việt có nghĩa. Rất tốt để học từ vựng.
- **Sudoku Kids:** Phiên bản bảng nhỏ (4x4 hoặc 6x6) giúp làm quen với các con số và logic loại trừ.

### 🧩 3.2. Nhóm Game Trí nhớ (Memory)
- **Lật Bài Nhớ (Đã có):** Tìm các cặp hình giống nhau, rèn luyện trí nhớ ngắn hạn và sự tập trung cao độ.
- **Simon Says:** Trò chơi nhớ và lặp lại một chuỗi màu sắc/âm thanh theo thứ tự.

### ⚡ 3.3. Nhóm Game Kỹ năng & Phản xạ (Skill & Reflex)
Rèn luyện sự phối hợp giữa tay và mắt, phản xạ nhanh nhạy.
- **Flappy Coin (Đã có):** Canh nhịp độ bay để vượt chướng ngại vật (Cột).
- **Rắn Săn Mồi (Đã có):** Điều hướng linh hoạt, căn chỉnh không gian di chuyển.
- **Dino Run:** Nhảy qua chướng ngại vật trên sa mạc, tốc độ tăng dần liên tục.
- **Whack-a-Mole (Đập chuột):** Chuột hiện ngẫu nhiên từ các lỗ, rèn luyện tốc độ phản ứng.
- **Block Breaker:** Điều khiển thanh hứng bóng để phá gạch.

### ♟️ 3.4. Nhóm Game Chiến thuật & Đầu tư (Strategy & Simulation)
Giúp trẻ làm quen với việc lên kế hoạch, phân bổ tài nguyên và tư duy tài chính cơ bản.
- **Tic-Tac-Toe (Cờ Caro 3x3):** Lập chiến thuật để thắng và chặn nước đi của máy.
- **Mini Farm (Nông trại Mini):** Mua hạt giống -> Trồng cây -> Chờ thu hoạch -> Bán lấy xu. Giúp trẻ hiểu về thời gian chờ đợi và khái niệm đầu tư sinh lời.
- **Tiệm Bánh Của Bé:** Trò chơi mô phỏng quản lý quán ăn, phục vụ khách để thu tiền nâng cấp quán.

### 🎮 3.5. Nhóm Game Giải trí ngắn (Casual / Relaxing)
- **Color Match:** Xoay khối màu hứng bóng rơi.
- **Minesweeper (Bản dễ):** Dò mìn dựa trên logic đếm số ô xung quanh.

---

## 4. Chiến lược Phát triển & Tích hợp

### 4.1. Tích hợp sâu vào Ứng dụng KidCoin (Việc nhà & Phần thưởng)
Game Hub không chỉ là nơi giải trí mà còn là động lực để trẻ làm việc nhà:
- **Mô hình "Pay to Play":** Một số game cực kỳ hấp dẫn (Premium Games) sẽ yêu cầu tiêu tốn 5-10 KidCoin cho mỗi lượt chơi. Trẻ phải hoàn thành các công việc nhà do bố mẹ giao để kiếm Coin, sau đó dùng Coin này để giải trí.
- **Mô hình "Play to Earn" (Học tập có thưởng):** Đối với các game thuộc nhóm Tư duy & Học tập (như Math Blast, Word Scramble), nếu trẻ đạt điểm cao (High Score), hệ thống có thể thưởng lại một lượng nhỏ Coin để khuyến khích việc vừa chơi vừa học.
- **Hệ thống Leaderboard:** Xếp hạng điểm số các game giữa các thành viên nhí trong gia đình hoặc mở rộng ra hệ thống Câu lạc bộ (Clubs) để tăng tính thi đua.

### 4.2. Chiến lược Kinh doanh (Monetization) & Kéo User
- **SEO & Organic Traffic:** Tối ưu hóa trang Game Hub với các từ khóa như "game vui cho bé", "game giáo dục miễn phí". Trẻ em và phụ huynh tìm thấy trang, chơi thử, và nhìn thấy quảng cáo "Tải KidCoin App để quản lý việc nhà và nhận thưởng".
- **Quảng cáo đối tác (Direct Ads):** Bán không gian quảng cáo (các Ad Slots đã chừa sẵn) cho các nhãn hàng phù hợp với tệp người dùng: Trung tâm tiếng Anh, thương hiệu đồ chơi, sách thiếu nhi, các khóa học kỹ năng sống.
- **Google AdSense:** Tích hợp mạng lưới quảng cáo tự động khi lượng Traffic (người truy cập) đạt mức ổn định.

### 4.3. Đa nền tảng và Tích hợp hệ thống thứ 3
- **Mini-App đa nền tảng:** Có thể đóng gói toàn bộ trang Game Hub này thành các Mini-App chạy trên Zalo, MoMo, hoặc Telegram. Điều này giúp tiếp cận nguồn user khổng lồ có sẵn trên các siêu ứng dụng này và kéo họ về tải app KidCoin chính thức.
- **API Mở (Open Platform):** Trong tương lai, KidCoin có thể mở API để các nhà phát triển game bên thứ 3 (đặc biệt là game giáo dục) đưa game của họ lên Game Hub, chia sẻ doanh thu từ quảng cáo hoặc từ số KidCoin mà trẻ em chi trả để chơi.
- **Cross-Promotion (Quảng cáo chéo):** Bắt tay hợp tác với các ứng dụng giáo dục khác. Đặt banner của họ trên Game Hub và ngược lại, họ giới thiệu KidCoin trên ứng dụng của họ.

---

## 5. Hệ thống Tracking & Phân tích Dữ liệu (Analytics)
Để phục vụ hiệu quả cho chiến lược kinh doanh và quảng cáo sau này, việc theo dõi (tracking) hành vi người dùng trên Game Hub và từng game nhỏ là yêu cầu bắt buộc. Hệ thống dữ liệu này sẽ giúp định giá quảng cáo, tối ưu hóa vị trí hiển thị và cá nhân hóa trải nghiệm.

### 5.1. Các chỉ số cần Tracking (Key Metrics)
- **Page Views & Unique Visitors:** Lượt truy cập và số lượng người dùng duy nhất vào trang chủ Game Hub (`/game`) và từng game cụ thể (`/game/snake`, `/game/2048`...).
- **Play Time (Session Duration):** Thời gian trung bình người dùng lưu lại trên trang và thời gian chơi thực tế của mỗi session game.
- **Event Tracking (Tương tác):** Tần suất nhấn nút "Chơi", tỷ lệ "Game Over" và "Chơi lại", cũng như số lần nhấn vào các vị trí banner quảng cáo (CTR - Click Through Rate).
- **Phễu chuyển đổi (Conversion Funnel):** Tỷ lệ người chơi vãng lai click vào nút "Đăng nhập" hoặc "Tải App KidCoin" sau khi trải nghiệm game.

### 5.2. Giải pháp Kiến trúc & Công nghệ (Architecture)
- **Tích hợp Third-party Tools (Frontend):**
  - Gắn mã theo dõi **Google Analytics 4 (GA4)**, **Mixpanel** hoặc **Amplitude**.
  - Thiết lập các Custom Events: `view_game_hub`, `start_game`, `finish_game`, `click_ad_banner`, `click_download_app`.
  - Phù hợp để track người dùng vãng lai (Anonymous Users) không cần đăng nhập.
- **Xây dựng Custom Backend Tracking (FastAPI):**
  - Thiết kế module `AnalyticsService` cung cấp endpoint `/api/v1/analytics/track`.
  - Frontend sẽ gửi ping (telemetry data) ngầm định kỳ (VD: mỗi 30s) hoặc khi trigger sự kiện (sử dụng `navigator.sendBeacon` hoặc fetch background).
  - Backend sử dụng Background Tasks (hoặc Message Queue như Redis/RabbitMQ/Kafka nếu scale lớn) để lưu log vào database (bảng `GameAnalytics`) mà không làm nghẽn luồng xử lý chính.
  - Phục vụ chặt chẽ cho người dùng nội bộ (trẻ em dùng Coin để chơi): Track để trừ/cộng Coin chính xác, chống gian lận (Anti-cheat) khi đạt High Score.

### 5.3. Ứng dụng dữ liệu vào Định hướng Kinh doanh
- **Báo giá Quảng cáo theo Traffic:** Phân luồng Traffic để biết game nào "hot" nhất. Banner ở các game top 1, top 2 sẽ có giá thuê cao nhất (Định giá theo CPM - Cost per 1000 Impressions).
- **Targeting (Nhắm mục tiêu) Quảng cáo:** Dựa trên thể loại game trẻ hay chơi để phân phối quảng cáo phù hợp (Ví dụ: trẻ chơi Math Blast nhiều sẽ hiển thị banner các ứng dụng học Toán, tiếng Anh).
- **Định hướng Phát triển Nội dung:** Phân tích `Bounce Rate` (tỷ lệ thoát) và `Play Time` để quyết định nên đầu tư thêm vào thể loại game nào tiếp theo (Logic, Phản xạ, hay Chiến thuật) để giữ chân người dùng lâu nhất.
