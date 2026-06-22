# ĐẶC TẢ CƠ CHẾ VẬN HÀNH HỆ THỐNG (SYSTEM SPECIFICATION)
## DỰ ÁN: NỀN TẢNG GIÁO VIÊN ONLINE CHO TRẺ LỚP 1
### (Tích hợp Khung giáo án 12 tuần và Kịch bản tương tác thông minh)

---

## I. KIẾN TRÚC TỔNG QUAN CỦA TRANG BÀI HỌC (LESSON PAGE UI/UX)

Mỗi bài học 30 phút trong khung 12 tuần[cite: 1] khi tải lên cấu trúc Web sẽ chia làm 3 phân vùng hiển thị chính:
1. **Phân vùng Tiến trình (ProgressBar):** Hiển thị bằng chuỗi Emoji (ví dụ: 🍏 -> 🍋 -> 🍇 -> 🎁). Bé hoàn thành đến đâu, Emoji tương ứng sẽ sáng lên kèm hiệu ứng chuyển động.
2. **Phân vùng Nội dung chính (Core Content):** Nơi hiển thị văn bản phối hợp Emoji Tự do (Free Emoji) để tiết kiệm tài nguyên hệ thống.
3. **Phân vùng Bảng điều khiển Trợ năng:** Nút loa phóng thanh to, nút Micro thu âm và bảng vẽ cảm ứng.

---

## II. ĐẶC TẢ CHI TIẾT CÁC CƠ CHẾ TƯƠNG TÁC CỐT LÕI

### 1. Cơ chế Đọc tự động và Đồng bộ chữ (Text-To-Speech & Karaoke Text)
*   **Công nghệ tích hợp:** Sử dụng Web Speech API hoặc các dịch vụ bên thứ ba (như FPT AI, Viettel AI) với cấu hình giọng đọc trẻ em/giọng đọc ấm áp, tốc độ phát từ **0.7x đến 0.8x** so với người lớn, có khoảng nghỉ ngắt câu rõ ràng.
*   **Luồng vận hành:**
    *   Hệ thống phân tách nội dung bài học thành từng phân đoạn thẻ HTML (`<span>` hoặc `<p>`).
    *   Khi công cụ TTS phát âm thanh đến thẻ nào (bắt theo `timestamp` hoặc sự kiện kết thúc từ), hệ thống tự động kích hoạt Class CSS `.highlight` để làm sáng dòng chữ đó lên (đổi màu nền vàng, tăng kích thước chữ 120%).
    *   **Bổ sung rào cản:** Đầu mỗi dòng chữ bắt buộc đính kèm 1 Emoji hành động đại diện cho kỹ năng (ví dụ: 👀 - Nhìn, 👂 - Nghe) để hỗ trợ các bé chưa biết chữ ở những tuần đầu tiên[cite: 1].

### 2. Cơ chế Chấm điểm nhận diện Giọng nói (Speech-To-Text - STT Interactive)
*   **Kịch bản UI:** Khi máy đọc xong lệnh hướng dẫn, Phân vùng Tương tác sẽ phát sáng nhấp nháy, hiển thị Emoji chiếc Micro lớn 🎙️ để bé nhận biết cần đọc to.
*   **Quy trình xử lý Logic Chấm điểm:**
    1.  Hệ thống mở luồng ghi âm thông qua trình duyệt, lưu file âm thanh tạm thời.
    2.  Chuyển đổi âm thanh thành văn bản dạng Text thông qua AI STT Engine.
    3.  **Thuật toán so khớp (String Similarity):** Sử dụng thuật toán *Levenshtein Distance* để tính toán tỷ lệ phần trăm giống nhau giữa Text bé đọc và Text yêu cầu của bài học.
*   **Kịch bản rẽ nhánh kết quả:**
    *   **Trường hợp Đạt (Tỷ lệ tương thích $\ge$ 80%):** 
        *   Hệ thống kích hoạt hiệu ứng bắn pháo hoa bằng Emoji (🎉 🥳 🌟), phát âm thanh tiếng vỗ tay.
        *   Máy nói: *"Xuất sắc quá! Con được thưởng 1 ngôi sao ⭐️!"* -> Tự động load nội dung tiếp theo.
    *   **Trường hợp Chưa đạt (Tỷ lệ tương thích < 80%):**
        *   Máy phát âm thanh động viên nhẹ nhàng: *"Gần đạt rồi, cố lên nào!"*.
        *   **Cơ chế hỗ trợ:** Máy tự động **phát lại âm thanh mẫu chuẩn** của từ đó 1 lần nữa để bé bắt chước.
        *   Hệ thống mở lại micro cho phép bé đọc lại. **Giới hạn số lần thử: Từ 3 đến 5 lần.**
        *   *Lối thoát bảo vệ tâm lý trẻ:* Nếu sau 5 lần vẫn dưới 80%, hệ thống tự động mở nút "Bố mẹ bấm bỏ qua để học tiếp" hoặc máy tự động nói: *"Hôm nay con đã rất cố gắng rồi, chúng ta cùng đi tiếp nào!"* để tránh gây ức chế cho trẻ.
    *   **Lưu ý kỹ thuật cho Lập trình viên:** Đối với các tuần học từ tuần 1 đến tuần 4 (khi trẻ chỉ học âm đơn như a, b, c, d, e...)[cite: 1], cấu hình AI chỉ cần nhận diện đúng **Từ khóa chính (Keyword)**, không bắt lỗi ngữ điệu hay các âm bồi của môi trường xung quanh.

### 3. Cơ chế Tương tác Nhập liệu và Viết tay (Input & Handwriting Recognition)
Cơ chế này tự động nhận diện thiết bị đầu cuối của người dùng thông qua thuộc tính `User-Agent` để hiển thị giao diện phù hợp:
*   **Trường hợp 1: Thiết bị di động / Máy tính bảng (Touch Devices - Smartphone, Tablet)**
    *   Hệ thống hiển thị một khung Canvas vẽ tự do lớn trên màn hình.
    *   **Bổ sung bắt buộc:** Bên dưới khung vẽ luôn có các nét chữ/số đứt mờ (Guideline) tương ứng với nội dung bài học (ví dụ: Tập viết số 1, 2, 3 ở tuần 1[cite: 1]).
    *   Bé sử dụng ngón tay để đồ theo nét đứt mờ này. Hệ thống tính điểm dựa trên tỷ lệ diện tích nét vẽ của bé đè trùng khớp lên tọa độ của nét đứt mờ có sẵn.
*   **Trường hợp 2: Máy tính để bàn / Laptop (Desktop Devices)**
    *   Tuyệt đối không bắt trẻ sử dụng bàn phím vật lý để gõ ký tự ở giai đoạn đầu học chữ[cite: 1].
    *   Hệ thống tự động hiển thị một **Bàn phím ảo trực quan (Virtual Keyboard)** kích thước lớn ngay trên màn hình web. Trên bàn phím này chỉ chứa các chữ cái hoặc chữ số là đáp án lựa chọn của bài học đó (Ví dụ: Bài học số 4, 5 ở tuần 2[cite: 1] thì bàn phím ảo chỉ hiện các ô số từ 0 đến 5).
    *   Bé tương tác bằng cách di chuột và Click chọn vào ô đáp án đúng trên màn hình.

### 4. Cơ chế Kết nối Đồng hành (Học cùng Bố mẹ và Bạn bè)
Để hiện thực hóa mục tiêu học tập có sự đồng hành, hệ thống tích hợp các **Trạm kiểm tra gia đình (Family Checkpoints)**:
*   Đối với các môn học mang tính thực hành, kết nối hành vi như Đạo đức, Tự nhiên Xã hội hay Hoạt động Trải nghiệm[cite: 1]: Hệ thống không thể chấm điểm tự động bằng công nghệ AI.
*   **Luồng xử lý:** Hệ thống hiển thị một bảng thông báo lớn kèm Emoji gia đình 👨‍👩‍👦:
    *   *Ví dụ ở bài Đạo đức Tuần 1:* Máy phát loa đọc yêu cầu: *"Bé hãy quay sang khoanh tay chào hỏi bố mẹ thật lễ phép nào!"*[cite: 1].
    *   Giao diện xuất hiện nút bấm lớn dành riêng cho phụ huynh: `[ Bố/Mẹ Xác Nhận Bé Đã Hoàn Thành 👍 ]`.
    *   Hệ thống chỉ chuyển bài khi có sự tương tác bấm nút vật lý này từ phụ huynh ngồi cạnh con.

---

## III. QUY TRÌNH QUẢN LÝ DỮ LIỆU & TÀI NGUYÊN (DATA & RESOURCE MANAGEMENT)

*   **Tối ưu hóa tài nguyên bằng Free Emoji:** 
    *   Toàn bộ hình ảnh minh họa cho các danh từ trong bài học (con gà 🐓, cái bàn  bàn 🪵, quả táo 🍎) đều được cấu hình bằng font mã hóa ký tự Emoji chuẩn UTF-8 của hệ điều hành. 
    *   *Ưu điểm:* Tốc độ tải trang web đạt mức dưới 1 giây, giảm dung lượng băng thông máy chủ xuống tối đa vì không cần lưu trữ và xử lý tệp tin hình ảnh nặng (.png, .jpg).
*   **Hệ thống Phần thưởng (Gamification Data):** 
    *   Mỗi lượt tương tác thành công sẽ cộng điểm trực tiếp vào tài khoản của bé dưới dạng số lượng Ngôi sao ⭐️ tích lũy. Số lượng sao này được lưu trữ trong `localStorage` của trình duyệt hoặc đồng bộ về Database hệ thống phục vụ tính năng đổi quà khuyến khích cuối tuần học.