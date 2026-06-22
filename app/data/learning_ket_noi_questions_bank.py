"""Ngân hàng câu hỏi kiến thức SGK Kết nối tri thức — không câu meta/tên bài."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

Question = Dict[str, Any]

# textbook_ref -> ít nhất 3 câu (mỗi micro-bài lấy 3 câu theo lesson index)
BANK: Dict[str, List[Question]] = {}

def _q(prompt: str, choices: List[str], answer_index: int = 0) -> Question:
    return {"prompt": prompt, "choices": choices, "answer_index": answer_index}


def _add(ref: str, questions: List[Question]) -> None:
    BANK[ref] = questions


# --- G4 KHOA HỌC (KNTT) ---
_add("G4-KH-1", [
    _q("Nước ở thể rắn gọi là gì?", ["Đá", "Hơi nước", "Sương"], 0),
    _q("Vật liệu nào dẫn điện tốt?", ["Đồng", "Gỗ", "Nhựa"], 0),
    _q("Năng lượng mặt trời giúp cây làm gì?", ["Quang hợp", "Ngủ", "Bơi"], 0),
    _q("Sắt thuộc thể rắn, lỏng hay khí?", ["Rắn", "Lỏng", "Khí"], 0),
    _q("Pin cung cấp loại năng lượng gì?", ["Điện", "Âm thanh", "Mùi"], 0),
    _q("Không khí có thể nhìn thấy không?", ["Không", "Có, màu xanh", "Có, màu trắng"], 0),
])
_add("G4-KH-2", [
    _q("Nguồn sáng tự nhiên là?", ["Mặt trời", "Bóng đèn", "Gương"], 0),
    _q("Khi đun nước, nhiệt độ nước sẽ?", ["Tăng", "Giảm", "Không đổi"], 0),
    _q("Vật nào phát sáng tự phát?", ["Ngọn nến", "Quả bóng", "Tờ giấy"], 0),
    _q("Bóng tối xuất hiện khi vật?", ["Che ánh sáng", "Uống nước", "Bay"], 0),
    _q("Kim loại nóng lên khi đặt gần lửa vì?", ["Truyền nhiệt", "Hút nước", "Nở ra không khí"], 0),
])
_add("G4-KH-3", [
    _q("Cây xanh cần gì để sống?", ["Nước và ánh sáng", "Chỉ đất", "Chỉ gió"], 0),
    _q("Động vật ăn thực vật gọi là?", ["Động vật ăn cỏ", "Động vật ăn thịt", "Động vật bay"], 0),
    _q("Con gì có xương sống?", ["Cá", "Giun", "Sâu"], 0),
    _q("Hoa có chức năng gì với cây?", ["Tạo hạt", "Hút đất", "Giữ nước"], 0),
    _q("Ecosystem là gì?", ["Hệ sinh thái", "Loài cây", "Loài đá"], 0),
])
_add("G4-KH-4", [
    _q("Rác thải nên được?", ["Phân loại", "Vứt xuống sông", "Đốt bừa bãi"], 0),
    _q("Cây xanh giúp không khí?", ["Sạch hơn", "Nóng hơn", "Khô hơn"], 0),
    _q("Tiết kiệm nước là để?", ["Bảo vệ môi trường", "Lãng phí", "Chơi"], 0),
    _q("Động vật hoang dã cần được?", ["Bảo vệ", "Săn bắt", "Bỏ mặc"], 0),
])
_add("G4-KH-5", [
    _q("Không nên chạm tay ướt vào?", ["Ổ điện", "Sách", "Bàn"], 0),
    _q("Dây điện bị hở nên?", ["Báo người lớn", "Tự sửa", "Cắm thử"], 0),
    _q("Khi có cháy điện, nên?", ["Tắt nguồn và gọi người lớn", "Đổ nước vào ổ", "Chạy vào khói"], 0),
    _q("Thiết bị dùng điện an toàn khi?", ["Khô ráo, đúng cách", "Ướt tay", "Hỏng dây"], 0),
])
_add("G4-KH-6", [
    _q("Ba thể của nước là?", ["Rắn, lỏng, khí", "Đỏ, xanh, vàng", "Nhanh, chậm"], 0),
    _q("Nguồn năng lượng tái tạo là?", ["Năng lượng mặt trời", "Than đá hết", "Nhựa"], 0),
    _q("Cây xanh thuộc nhóm sinh vật?", ["Thực vật", "Khoáng vật", "Kim loại"], 0),
])

# G5 KHOA HỌC
_add("G5-KH-1", [
    _q("Cơ quan tuần hoàn mang máu đi khắp cơ thể là?", ["Tim", "Da", "Tóc"], 0),
    _q("Phổi giúp cơ thể?", ["Hô hấp", "Tiêu hóa", "Nghe"], 0),
    _q("Xương bảo vệ cơ quan nào?", ["Não", "Da", "Tóc"], 0),
])
_add("G5-KH-2", [
    _q("Nước đá tan thành nước lỏng là biến đổi?", ["Vật lý", "Hóa học", "Sinh học"], 0),
    _q("Sắt bị gỉ là biến đổi?", ["Hóa học", "Chỉ đổi hình", "Không đổi"], 0),
    _q("Muối tan trong nước tạo?", ["Dung dịch", "Đá", "Khí"], 0),
])
_add("G5-KH-3", [
    _q("Cây quang hợp nhờ?", ["Lá xanh", "Rễ ăn đất", "Hoa nở"], 0),
    _q("Ếch là động vật?", ["Lưỡng cư", "Thú", "Côn trùng"], 0),
    _q("Chim có lông vũ để?", ["Giữ ấm và bay", "Bơi dưới nước", "Đào đất"], 0),
])
_add("G5-KH-4", [
    _q("Trái Đất quay quanh?", ["Mặt Trời", "Mặt Trăng", "Sao Hỏa"], 0),
    _q("Ngày và đêm do?", ["Trái Đất tự quay", "Mặt Trời tắt", "Mây che"], 0),
    _q("Mùa trong năm liên quan đến?", ["Độ nghiêng Trái Đất", "Màu lá", "Gió nhẹ"], 0),
])
_add("G5-KH-5", [
    _q("Tái chế giấy giúp?", ["Giảm chặt cây", "Tăng rác", "Ô nhiễm"], 0),
    _q("Ô nhiễm không khí gây?", ["Khó thở", "Ngủ ngon", "Cao lớn"], 0),
])

# G4 LỊCH SỬ & ĐỊA LÝ
for i, qs in enumerate([
    [_q("Thủ đô Việt Nam là?", ["Hà Nội", "TP.HCM", "Đà Nẵng"], 0), _q("Việt Nam nằm ở châu lục?", ["Châu Á", "Châu Âu", "Châu Mỹ"], 0), _q("Biển Đông thuộc?", ["Việt Nam và nước láng giềng", "Châu Âu", "Châu Phi"], 0)],
    [_q("Làng quê thường có?", ["Ruộng đồng", "Nhà cao tầng", "Sân bay"], 0), _q("Thành phố đông?", ["Người và xe", "Cây cối", "Ruộng"], 0), _q("Nghề ở làng thường là?", ["Trồng trọt", "Bay lượn", "Lặn biển"], 0)],
    [_q("Vua Hùng gắn với?", ["Lịch sử nước ta", "Bóng đá", "Âm nhạc"], 0), _q("Đền Hùng ở tỉnh?", ["Phú Thọ", "Cà Mau", "Lai Châu"], 0), _q("Giỗ Tổ Hùng Vương vào tháng?", ["3 âm lịch", "12 dương", "1 dương"], 0)],
    [_q("Biển đảo Việt Nam gồm?", ["Trường Sa, Hoàng Sa", "Chỉ sông", "Chỉ núi"], 0), _q("Bảo vệ biển đảo là?", ["Bảo vệ Tổ quốc", "Không cần", "Chỉ người lớn"], 0)],
    [_q("Rừng giúp?", ["Giữ đất, khí hậu", "Làm bẩn sông", "Tăng rác"], 0), _q("Sông hồ cần?", ["Không xả rác", "Đổ hóa chất", "Đắp đập tùy tiện"], 0)],
    [_q("Bản đồ giúp ta?", ["Định hướng", "Nấu ăn", "Ngủ"], 0)],
], 1):
    _add(f"G4-LSDL-{i}", qs)

# G4 ĐẠO ĐỨC
_add("G4-DD-1", [_q("Trung thực nghĩa là?", ["Nói thật, làm đúng", "Nói dối", "Trốn học"], 0), _q("Khi làm sai nên?", ["Nhận lỗi", "Đổ lỗi", "Giấu"], 0), _q("Tự lực là?", ["Tự làm việc của mình", "Nhờ người khác", "Bỏ việc"], 0)])
_add("G4-DD-2", [_q("Luật giao thông giúp?", ["An toàn", "Chậm", "Vui"], 0), _q("Đèn đỏ nghĩa là?", ["Dừng lại", "Chạy nhanh", "Đi tùy ý"], 0)])
_add("G4-DD-3", [_q("Lao động sạch sẽ giúp?", ["Môi trường đẹp", "Bẩn", "Ồn"], 0), _q("Thu gom rác đúng nơi là?", ["Có trách nhiệm", "Không cần", "Vui thôi"], 0)])

# G1-G3 TN&XH samples
_add("G1-TNXH-1", [_q("Chúng ta dùng mắt để?", ["Nhìn", "Ngửi", "Nếm"], 0), _q("Tai giúp ta?", ["Nghe", "Đi", "Ngủ"], 0)])
_add("G2-TNXH-1", [_q("Răng giúp?", ["Nhai thức ăn", "Nghe", "Chạy"], 0), _q("Rửa tay trước ăn để?", ["Sạch sẽ", "Chơi", "Ngủ"], 0)])
_add("G3-TNXH-1", [_q("Tim nằm ở?", ["Ngực", "Đầu gối", "Tóc"], 0), _q("Vệ sinh cá nhân giúp?", ["Khỏe mạnh", "Ốm", "Mệt"], 0)])

# TIẾNG ANH G3-G5
_add("G3-NGOAI-NGU-1", [_q("'Hello' nghĩa là?", ["Xin chào", "Tạm biệt", "Cảm ơn"], 0), _q("'Thank you' nghĩa là?", ["Cảm ơn", "Xin lỗi", "Chào"], 0)])
_add("G4-NGOAI-NGU-1", [_q("'School' là?", ["Trường học", "Nhà", "Cửa hàng"], 0), _q("'Teacher' là?", ["Giáo viên", "Bác sĩ", "Đầu bếp"], 0)])

# TIN HỌC
_add("G3-TIN-HOC-1", [_q("Máy tính dùng để?", ["Học và làm việc", "Nấu cơm", "Giặt quần áo"], 0), _q("Mật khẩu nên?", ["Bí mật", "Chia sẻ", "Viết ra tường"], 0)])
_add("G4-TIN-HOC-1", [_q("Internet giúp?", ["Tìm thông tin", "Ngủ", "Ăn"], 0), _q("Không nên click link lạ vì?", ["Có thể nguy hiểm", "Vui", "Nhanh"], 0)])

# TOÁN G4 — phân số, diện tích
_add("G4-TOAN-CD4", [
    _q("1/2 + 1/2 = ?", ["1", "1/4", "2"], 0),
    _q("Phân số 3/4 có mẫu số là?", ["4", "3", "7"], 0),
    _q("1/3 của 9 là?", ["3", "6", "9"], 0),
])
_add("G4-TOAN-CD6", [
    _q("Diện tích HCN = ?", ["Chiều dài × chiều rộng", "Cộng cạnh", "Chia 2"], 0),
    _q("Hình vuông có 4 cạnh?", ["Bằng nhau", "Khác nhau", "Không có"], 0),
])


def get_bank_questions(textbook_ref: str) -> List[Question]:
    return list(BANK.get(textbook_ref, []))
