"""Đoạn văn Tiếng Việt Lớp 2 — T2, luyện tập 5 câu hoặc 3×3. Nội dung gốc, khác G1."""

from __future__ import annotations

from typing import Dict, List, TypedDict


class TopicPassages(TypedDict):
    read_short: List[str]
    read_mid: List[str]
    practice_segments: List[List[str]]


BANK: Dict[str, TopicPassages] = {
    "em đến trường": {
        "read_short": [
            "Buổi sáng, Minh đeo cặp đi học.",
            "Trên đường, Minh gặp bạn Linh.",
            "Hai bạn cùng bước vào sân trường.",
        ],
        "read_mid": [
            "Hôm nay là ngày khai giảng của lớp hai.",
            "Minh đứng xếp hàng ngay ngắn với các bạn.",
            "Cô hiệu trưởng phát biểu chào mừng năm học mới.",
            "Minh vỗ tay thật to cùng cả trường.",
            "Minh thấy năm học này sẽ rất thú vị.",
        ],
        "practice_segments": [
            ["Sáng thứ hai lớp học bài mới.", "Cô đọc mẫu cho cả lớp nghe.", "Minh đọc theo từng câu rõ ràng."],
            ["Giờ ra chơi, Minh chơi cầu với bạn.", "Hai bạn cười đùa ngoài sân.", "Tiếng cười làm lớp thêm vui."],
            ["Chiều về Minh kể cho mẹ nghe.", "Mẹ mỉm cười lắng nghe.", "Minh thích đến trường mỗi ngày."],
        ],
    },
    "gia đình thân yêu": {
        "read_short": [
            "Chiều nay cả nhà quây quần bên bàn.",
            "Bố kể chuyện công việc trong ngày.",
            "Linh nghe và hỏi bố thêm.",
        ],
        "read_mid": [
            "Cuối tuần, gia đình Linh về quê thăm ông bà.",
            "Ông dẫn Linh đi xem vườn rau sau nhà.",
            "Bà nấu bữa tối thật đông vui.",
            "Linh giúp rửa rau cùng chị gái.",
            "Linh cảm thấy yêu gia đình mình hơn.",
        ],
        "practice_segments": [
            ["Sáng chủ nhật mẹ dạy Linh gấp áo.", "Linh gấp từng chiếc thật cẩn thận.", "Mẹ khen Linh làm giỏi."],
            ["Bố sửa chiếc xe đạp nhỏ cho Linh.", "Linh đạp xe quanh sân.", "Cả nhà vui theo dõi."],
            ["Tối đến Linh viết nhật ký.", "Linh ghi lại ngày vui với gia đình.", "Linh ôm vở ngủ ngon."],
        ],
    },
    "bạn bè và trường học": {
        "read_short": [
            "Hôm nay lớp có tiết mỹ thuật.",
            "Các bạn vẽ tranh về trường học.",
            "Linh tô màu ngôi trường thật đẹp.",
        ],
        "read_mid": [
            "Giờ ra chơi, bạn Hùng ngã khi chạy.",
            "Linh và Nam đỡ Hùng dậy ngay.",
            "Cô y tế kiểm tra và thấy Hùng không sao.",
            "Hùng cảm ơn hai bạn thật chân thành.",
            "Linh vui vì đã giúp bạn trong lúc cần.",
        ],
        "practice_segments": [
            ["Lớp tổ chức thi kể chuyện.", "Mỗi bạn kể một câu chuyện ngắn.", "Linh kể về chuyến dã ngoại."],
            ["Cô chia nhóm làm báo tường.", "Nhóm Linh vẽ và viết chữ đẹp.", "Báo tường được treo trên hành lang."],
            ["Cuối tuần Linh gọi điện hỏi bài.", "Hai bạn cùng ôn phép cộng.", "Linh thấy học nhóm thật bổ ích."],
        ],
    },
    "thiên nhiên quanh em": {
        "read_short": [
            "Sau cơn mưa, đường phố thật trong lành.",
            "Cây cối hai bên đường xanh hơn.",
            "Linh đi bộ cùng mẹ ngắm trời.",
        ],
        "read_mid": [
            "Buổi sáng, nắng vàng rải trên sân trường.",
            "Linh nhìn thấy đàn kiến bò trên lối đi.",
            "Cô dạy các bạn không giẫm lên tổ kiến.",
            "Linh quan sát kiến kéo hạt thật chăm chỉ.",
            "Linh học được cách yêu loài vật nhỏ.",
        ],
        "practice_segments": [
            ["Lớp trồng cây hoa mai ngoài cửa.", "Mỗi bạn tưới một chậu.", "Cây con mọc lá non xanh tươi."],
            ["Linh mang hạt giống từ nhà đến.", "Cô hướng dẫn gieo hạt trong chậu.", "Linh theo dõi cây mỗi ngày."],
            ["Chiều về Linh vẽ lại cây đã trồng.", "Bức tranh có nắng và lá xanh.", "Mẹ treo tranh lên tường phòng."],
        ],
    },
    "người thân trong gia đình": {
        "read_short": [
            "Ông Linh hay dạy chữ trên sân gạch.",
            "Bà kể chuyện cổ tích trước khi ngủ.",
            "Linh thích nghe bà kể mỗi tối.",
        ],
        "read_mid": [
            "Chị gái Linh đang học lớp năm.",
            "Chị thường giúp Linh đọc bài khó.",
            "Hai chị em cùng ngồi bên bàn học.",
            "Linh cố gắng đọc đúng như chị hướng dẫn.",
            "Chị khen Linh tiến bộ từng ngày.",
        ],
        "practice_segments": [
            ["Dịp lễ, họ hàng về đông vui.", "Linh chào từng người thật lễ phép.", "Mọi người khen Linh ngoan."],
            ["Linh giúp mẹ bày mâm cỗ.", "Linh xếp đĩa và đũa ngay ngắn.", "Bữa cơm sum họp thật ấm áp."],
            ["Tối đó Linh viết về ông bà.", "Bài viết nói về tình yêu thương.", "Cô giáo đọc và khen bài hay."],
        ],
    },
    "cộng đồng xung quanh": {
        "read_short": [
            "Gần trường có thư viện nhỏ.",
            "Linh mượn sách mỗi tuần một cuốn.",
            "Cô thủ thư luôn mỉm cười đón các bạn.",
        ],
        "read_mid": [
            "Xóm Linh tổ chức ngày làm sạch khu phố.",
            "Linh và các bạn quét lá khô trên vỉa hè.",
            "Người lớn thu gom rác vào thùng đúng chỗ.",
            "Đường phố sạch sẽ hơn sau buổi lao động.",
            "Linh hiểu mỗi người đều góp phần giữ phố đẹp.",
        ],
        "practice_segments": [
            ["Lớp thăm trạm y tế xã.", "Bác sĩ kể về rửa tay đúng cách.", "Linh thực hành ngay tại lớp."],
            ["Linh và bạn góp sách cũ cho thư viện.", "Sách được sắp xếp trên kệ mới.", "Nhiều bạn được đọc thêm."],
            ["Cuối tháng lớp tổng kết việc tốt.", "Linh được khen vì giúp bạn học bài.", "Linh tự hào về bản thân."],
        ],
    },
    "ước mơ và hoài bão": {
        "read_short": [
            "Linh mơ ước trở thành nhà văn.",
            "Linh thích viết nhật ký mỗi tối.",
            "Mẹ khuyên Linh đọc thêm sách hay.",
        ],
        "read_mid": [
            "Trong giờ sinh hoạt, cô mời các bạn nói ước mơ.",
            "Bạn Tâm muốn làm phi công lái máy bay.",
            "Bạn Ngọc thích hát và mơ ước lên sân khấu.",
            "Linh kể ước mơ viết sách cho thiếu nhi.",
            "Cô khuyên các bạn kiên trì theo đuổi ước mơ.",
        ],
        "practice_segments": [
            ["Linh viết thư gửi bản thân sau năm năm.", "Linh hứa đọc sách và viết mỗi ngày.", "Linh cất thư vào hộp kỷ niệm."],
            ["Lớp vẽ tranh về nghề nghiệp tương lai.", "Linh vẽ cô giáo đang đọc sách.", "Tranh được dán trên bảng lớp."],
            ["Cuối năm Linh đọc thư của mình.", "Linh thấy mình đã tiến bộ.", "Ước mơ ngày càng rõ hơn."],
        ],
    },
    "ôn tập học kì 1": {
        "read_short": [
            "Cuối học kì một, lớp ôn tập đọc.",
            "Linh đọc to trước lớp từng đoạn.",
            "Cô ghi nhận sự cố gắng của Linh.",
        ],
        "read_mid": [
            "Linh ôn lại các bài tập đọc đã học.",
            "Linh chú ý ngắt nghỉ đúng dấu câu.",
            "Linh luyện viết đoạn văn ba câu về bạn bè.",
            "Bạn bè nghe Linh đọc và góp ý nhẹ nhàng.",
            "Linh tự tin hơn khi đọc trước đám đông.",
        ],
        "practice_segments": [
            ["Cả lớp chia nhóm thi đọc diễn cảm.", "Nhóm Linh đọc đoạn về mùa xuân.", "Giọng đọc rõ và có cảm xúc."],
            ["Linh ôn từ khó trong vở từ điển nhỏ.", "Linh viết lại từ đã tra.", "Linh nhớ chính tả tốt hơn."],
            ["Ngày kiểm tra đến gần.", "Linh ngủ đủ giấc để khỏe mạnh.", "Linh sẵn sàng làm bài thật tốt."],
        ],
    },
    "mùa xuân và lễ hội": {
        "read_short": [
            "Mùa xuân đến, cây đào nở hoa.",
            "Nhà Linh treo câu đố đỏ hai bên cửa.",
            "Linh giúp mẹ gói bánh chưng.",
        ],
        "read_mid": [
            "Sáng mùng một, Linh mặc áo dài mới.",
            "Cả nhà đi chúc Tết ông bà nội.",
            "Ông bà mừng tuổi và chúc Linh học giỏi.",
            "Linh chúc ông bà luôn mạnh khỏe.",
            "Không khí Tết làm Linh thấy ấm lòng.",
        ],
        "practice_segments": [
            ["Làng tổ chức hội xuân ngoài sân đình.", "Các bạn múa sạp và đánh trống.", "Linh xem và vỗ tay theo nhịp."],
            ["Linh viết thiệp chúc thầy cô.", "Chữ viết thẳng hàng và đẹp.", "Thầy cô mỉm cười nhận thiệp."],
            ["Tối rẓi Linh ngắm pháo hoa từ xa.", "Bầu trời đầy màu sắc.", "Linh ước năm mới nhiều niềm vui."],
        ],
    },
    "bảo vệ môi trường": {
        "read_short": [
            "Linh không vứt rác ra sân trường.",
            "Linh nhắc bạn bỏ rác đúng thùng.",
            "Lớp học sạch sẽ nhờ mọi người cùng giữ.",
        ],
        "read_mid": [
            "Cô dạy lớp phân loại rác tại chỗ.",
            "Linh bỏ giấy vào thùng màu xanh.",
            "Vỏ chai được rửa sạch trước khi tái chế.",
            "Linh dùng bình nước thay ly nhựa dùng một lần.",
            "Linh hiểu hành động nhỏ cũng giúp môi trường.",
        ],
        "practice_segments": [
            ["Cả lớp trồng thêm cây xanh sau tường trường.", "Linh đào hố và đặt cây cẩn thận.", "Cây được tưới nước đều đặn."],
            ["Linh thu gom giấy vụn trong lớp.", "Giấy được bán để tái chế.", "Tiền góp vào quỹ cây xanh."],
            ["Cuối tuần Linh đi bộ thay vì xe máy.", "Đường phố ít khói hơn.", "Linh thấy không khí trong lành hơn."],
        ],
    },
    "ôn tập cuối năm": {
        "read_short": [
            "Cuối năm học, Linh ôn lại bài đọc.",
            "Linh luyện viết chữ nghiêng đẹp.",
            "Linh nhớ những ngày vui ở trường.",
        ],
        "read_mid": [
            "Linh đọc lại các đoạn văn yêu thích.",
            "Linh kể chuyện mình thích nhất trước lớp.",
            "Linh viết vài câu cảm ơn cô giáo.",
            "Cô đọc bài và mắt cô ánh lên hài lòng.",
            "Linh cảm thấy mình đã lớn hơn so với đầu năm.",
        ],
        "practice_segments": [
            ["Buổi học cuối, cả lớp hát bài tập thể.", "Giọng hát vang khắp phòng.", "Linh hát to và vui vẻ."],
            ["Linh và bạn ôn lại từ khó cả năm.", "Hai bạn đọc luân phiên từng đoạn.", "Linh đọc trôi chảy hơn trước."],
            ["Năm học sắp khép lại.", "Linh sẵn sàng bước sang lớp ba.", "Linh tự tin vào bản thân."],
        ],
    },
}

CONTENT_VERSION = "tv-g2-v2"
