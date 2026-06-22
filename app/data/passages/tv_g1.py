"""Đoạn văn Tiếng Việt Lớp 1 — T1/T2, luyện tập 3×3 câu. Nội dung gốc."""

from __future__ import annotations

from typing import Dict, List, TypedDict


class TopicPassages(TypedDict):
    read_short: List[str]
    read_mid: List[str]
    practice_segments: List[List[str]]


# topic_key (lower) -> passages
BANK: Dict[str, TopicPassages] = {
    "em đến trường": {
        "read_short": [
            "Sáng sớm, mẹ dắt tay bé đi học.",
            "Bé mang cặp mới thật vui.",
            "Cô giáo cười chào bé vào lớp.",
        ],
        "read_mid": [
            "Hôm nay là ngày đầu bé đi học.",
            "Trên đường, bé gặp bạn Hoa.",
            "Hai bạn cùng bước qua cổng trường.",
            "Tiếng trống vang lên thật vui.",
        ],
        "practice_segments": [
            ["Sáng nay bé dậy sớm.", "Mẹ chuẩn bị cặp sách.", "Bố đưa bé đến trường."],
            ["Lớp học thật sạch sẽ.", "Bé ngồi ngay ngắn.", "Cô dạy bé đọc chữ."],
            ["Giờ ra chơi đến rồi.", "Bé chơi với bạn.", "Bé thích đi học mỗi ngày."],
        ],
    },
    "gia đình thân yêu": {
        "read_short": [
            "Ba đi làm sớm mỗi ngày.",
            "Mẹ nấu cơm thơm trong bếp.",
            "Bé giúp mẹ xếp bát đĩa.",
        ],
        "read_mid": [
            "Tối qua cả nhà ăn cơm cùng nhau.",
            "Ba kể chuyện vui cho bé nghe.",
            "Mẹ và bé cười thật to.",
            "Nhà bé luôn ấm và yêu thương.",
        ],
        "practice_segments": [
            ["Sáng chủ nhật ba nghỉ.", "Cả nhà dọn nhà cùng nhau.", "Bé quét lá trong sân."],
            ["Mẹ dạy bé gấp quần áo.", "Bé làm theo thật cẩn thận.", "Mẹ khen bé giỏi."],
            ["Tối đến bé ôm mẹ.", "Bé nói yêu ba mẹ.", "Cả nhà ngủ thật ngon."],
        ],
    },
    "bạn bè và trường học": {
        "read_short": [
            "Hôm nay lớp có tiết thể dục.",
            "Các bạn chạy ngoài sân.",
            "Bé và Hoa cùng nhảy dây.",
        ],
        "read_mid": [
            "Giờ ra chơi, bé xếp hàng vào lớp.",
            "Bạn Mai quên bút, bé cho mượn.",
            "Mai cảm ơn bé thật chân thành.",
            "Bé vui vì giúp được bạn.",
        ],
        "practice_segments": [
            ["Lớp bé treo tranh lên tường.", "Mỗi bạn vẽ một bông hoa.", "Lớp học thật đẹp."],
            ["Cô dạy bé hát một bài.", "Cả lớp hát thật to.", "Tiếng hát vang khắp phòng."],
            ["Bé và bạn cùng đọc sách.", "Hai bạn đọc chậm rõ ràng.", "Bé thích học với bạn."],
        ],
    },
    "thiên nhiên quanh em": {
        "read_short": [
            "Ngoài sân có cây xanh.",
            "Chim hót líu lo trên cành.",
            "Gió thổi mát thật dễ chịu.",
        ],
        "read_mid": [
            "Sau mưa, đường phố thật sạch.",
            "Cây cối xanh tươi hơn.",
            "Bé và mẹ đi dạo quanh nhà.",
            "Bé thích ngắm trời trong veo.",
        ],
        "practice_segments": [
            ["Nắng sáng chiếu qua cửa.", "Bé thấy bướm bay quanh hoa.", "Hoa nở màu hồng đẹp."],
            ["Bé tưới cây trên ban công.", "Lá cây xanh và tươi.", "Bé chăm cây mỗi ngày."],
            ["Chiều về gió mát lại.", "Bé nghe tiếng lá xào xạc.", "Bé yêu thiên nhiên quanh mình."],
        ],
    },
    "người thân trong gia đình": {
        "read_short": [
            "Ông bé hay kể chuyện xưa.",
            "Bà nấu cháo thơm sáng sớm.",
            "Bé ôm bà trước khi đi học.",
        ],
        "read_mid": [
            "Chị bé giúp bé xếp sách.",
            "Anh bé dạy bé chơi bóng.",
            "Cả nhà dọn nhà cuối tuần.",
            "Bé yêu từng người trong nhà.",
        ],
        "practice_segments": [
            ["Cuối tuần về thăm ông bà.", "Ông bà mừng rỡ đón bé.", "Bé kể chuyện trường lớp."],
            ["Bé giúp bà nhặt rau.", "Bà dạy bé tên từng loại.", "Bé học thêm điều mới."],
            ["Tối về bé vẽ ông bà.", "Bé tô màu thật cẩn thận.", "Ông bà cười rất vui."],
        ],
    },
    "cộng đồng xung quanh": {
        "read_short": [
            "Gần nhà có chợ nhỏ.",
            "Bác hàng xóm bán rau.",
            "Bé chào bác mỗi sáng.",
        ],
        "read_mid": [
            "Làng tổ chức ngày dọn phố.",
            "Bé và bạn nhặt rác sân trường.",
            "Mọi người giữ khu phố sạch.",
            "Bé hiểu cần giúp cộng đồng.",
        ],
        "practice_segments": [
            ["Bé đi chợ cùng mẹ.", "Bé xách túi nhỏ phụ mẹ.", "Bé chào các bác bán hàng."],
            ["Lớp bé quyên góp sách cũ.", "Sách được gửi tới thư viện.", "Bé vui vì chia sẻ."],
            ["Bé và bạn trồng cây sân trường.", "Cây nhỏ được tưới nước.", "Bé hứa chăm cây mỗi ngày."],
        ],
    },
    "ước mơ và hoài bão": {
        "read_short": [
            "Bé mơ làm bác sĩ.",
            "Bé muốn chữa bệnh cho mọi người.",
            "Bé học chăm mỗi ngày.",
        ],
        "read_mid": [
            "Giờ sinh hoạt, bé kể ước mơ.",
            "Bạn Mai muốn làm cô giáo.",
            "Bạn Tùng thích vẽ tranh.",
            "Cô khuyên các bé kiên trì.",
        ],
        "practice_segments": [
            ["Bé viết thư cho tương lai.", "Bé hứa đọc sách mỗi ngày.", "Bé sẽ giúp bạn khi cần."],
            ["Bé luyện viết chữ đẹp.", "Bé tập đọc to mỗi tối.", "Ba mẹ khen bé cố gắng."],
            ["Ước mơ nhỏ hôm nay.", "Sẽ mở ra ngày mai.", "Bé tin vào chính mình."],
        ],
    },
    "ôn tập học kì 1": {
        "read_short": [
            "Cuối kì lớp ôn bài đọc.",
            "Bé đọc to trước lớp.",
            "Cô khen bé cố gắng.",
        ],
        "read_mid": [
            "Bé ôn lại bài đã học.",
            "Bé nhớ đọc đúng dấu câu.",
            "Bé viết đoạn ngắn về nhà.",
            "Bé tự tin hơn khi đọc.",
        ],
        "practice_segments": [
            ["Cả lớp đọc theo nhóm.", "Mỗi nhóm đọc một đoạn.", "Bé nghe bạn và sửa lỗi."],
            ["Bé ôn từ khó trong vở.", "Bé đọc lại ba lần.", "Bé nhớ từ tốt hơn."],
            ["Ngày kiểm tra đến gần.", "Bé ngủ sớm để khỏe.", "Bé sẵn sàng làm bài."],
        ],
    },
    "mùa xuân và lễ hội": {
        "read_short": [
            "Mùa xuân, hoa đào nở.",
            "Nhà bé dọn sạch đón Tết.",
            "Bé giúp mẹ lau bàn.",
        ],
        "read_mid": [
            "Sáng mùng một bé mặc áo mới.",
            "Ông bà mừng tuổi cho bé.",
            "Bé chúc nhà an khang.",
            "Không khí Tết thật vui.",
        ],
        "practice_segments": [
            ["Bé gói bánh cùng mẹ.", "Tay bé bẩn bột thật vui.", "Bánh chưng thơm cả nhà."],
            ["Làng có hội xuân ngoài sân.", "Bé xem múa sạp cùng ba.", "Tiếng trống vang rộn ràng."],
            ["Bé viết thiệp chúc ông bà.", "Chữ bé viết thật cẩn thận.", "Ông bà ôm bé thật chặt."],
        ],
    },
    "bảo vệ môi trường": {
        "read_short": [
            "Bé không vứt rác bừa.",
            "Bé tưới cây sân trường.",
            "Bé tắt đèn khi ra ngoài.",
        ],
        "read_mid": [
            "Lớp bé phân loại rác.",
            "Bé dùng giấy nháp hai mặt.",
            "Bé nhắc bạn không bẻ cành.",
            "Môi trường sạch giúp ta khỏe.",
        ],
        "practice_segments": [
            ["Cả lớp trồng cây sau hè.", "Bé đào hố thật cẩn thận.", "Cây non được tưới nước."],
            ["Bé mang chai nước tái dùng.", "Bé không xả rác ra đường.", "Bé nhặt rác ngoài sân."],
            ["Cô dạy bé yêu cây xanh.", "Bé hứa bảo vệ môi trường.", "Bé làm việc tốt mỗi ngày."],
        ],
    },
    "ôn tập cuối năm": {
        "read_short": [
            "Cuối năm bé ôn bài đọc.",
            "Bé luyện viết chữ đẹp.",
            "Bé nhớ bài học đáng nhớ.",
        ],
        "read_mid": [
            "Bé đọc lại đoạn văn đã học.",
            "Bé kể chuyện trước lớp.",
            "Bé viết về năm học qua.",
            "Bé cảm ơn cô giáo.",
        ],
        "practice_segments": [
            ["Buổi cuối cả lớp hát.", "Bé hát to và vui.", "Tiếng hát đầy phòng học."],
            ["Bé và bạn ôn từ khó.", "Hai bạn đọc luân phiên.", "Bé đọc trôi hơn trước."],
            ["Năm học sắp kết thúc.", "Bé sẵn sàng lên lớp hai.", "Bé tự hào về bản thân."],
        ],
    },
}

CONTENT_VERSION = "tv-g1-v2"
