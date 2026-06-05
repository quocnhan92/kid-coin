"""
Chương trình Tiếng Anh lớp 1–3 cho English Shooter.
Nguồn: GDD_EnglishShooter_v1.md + bộ từ Memory game (GRADE2_ENGLISH, ENGLISH_THEMES).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

CONTENT_PACK = "vn_english_shooter_v1"

# (word, translation_vi, emoji)
VocabWord = Tuple[str, str, str]
# (target_sentence, vi, prompt, choices, answer)
SentenceItem = Tuple[str, str, str, List[str], str]
# (paragraph_text, vi)
ParagraphItem = Tuple[str, str]


def _theme(
    theme_id: str,
    grade: int,
    title: str,
    vi_title: str,
    order_index: int,
    scene: str,
    boss_id: str,
    vocab: List[VocabWord],
    pool_distractors: List[str],
    sentences: List[SentenceItem],
    paragraphs: List[ParagraphItem],
) -> Dict[str, Any]:
    return {
        "theme_id": theme_id,
        "grade": grade,
        "title": title,
        "vi_title": vi_title,
        "order_index": order_index,
        "scene": scene,
        "boss_id": boss_id,
        "vocab": vocab,
        "pool_distractors": pool_distractors,
        "sentences": sentences,
        "paragraphs": paragraphs,
    }


# --- LỚP 1 (7 chủ đề, ~90 từ) ---
G1_THEMES: List[Dict[str, Any]] = [
    _theme(
        "en_g1_family",
        1,
        "My Family",
        "Gia đình của em",
        1,
        "savannah",
        "boss_g1_chicken",
        [
            ("mom", "Mẹ", "👩"),
            ("dad", "Bố", "👨"),
            ("baby", "Em bé", "👶"),
            ("sister", "Chị/em gái", "👧"),
            ("brother", "Anh/em trai", "👦"),
            ("family", "Gia đình", "👨‍👩‍👧"),
            ("grandma", "Bà", "👵"),
            ("grandpa", "Ông", "👴"),
            ("aunt", "Cô/dì", "👩"),
            ("uncle", "Chú/bác", "👨"),
            ("cousin", "Anh/chị/em họ", "🧒"),
            ("love", "Yêu thương", "❤️"),
        ],
        ["cat", "dog", "apple", "ball", "book", "tree"],
        [
            ("This is my mom.", "Đây là mẹ của tôi.", "This is my [____].", ["mom", "dad", "cat"], "mom"),
            ("I love my dad.", "Con yêu bố.", "I love my [____].", ["dad", "mom", "dog"], "dad"),
            ("This is my family.", "Đây là gia đình tôi.", "This is my [____].", ["family", "school", "car"], "family"),
        ],
        [
            ("This is my family. I love my mom and dad.", "Đây là gia đình tôi. Con yêu mẹ và bố."),
            ("I have a sister and a brother. We play together.", "Tôi có chị/em gái và anh/em trai. Chúng tôi chơi cùng nhau."),
        ],
    ),
    _theme(
        "en_g1_colors",
        1,
        "Colors",
        "Màu sắc",
        2,
        "savannah",
        "boss_g1_chicken",
        [
            ("red", "Màu đỏ", "🔴"),
            ("blue", "Màu xanh dương", "🔵"),
            ("yellow", "Màu vàng", "🟡"),
            ("green", "Màu xanh lá", "🟢"),
            ("orange", "Màu cam", "🟠"),
            ("pink", "Màu hồng", "🩷"),
            ("purple", "Màu tím", "🟣"),
            ("black", "Màu đen", "⚫"),
            ("white", "Màu trắng", "⚪"),
            ("brown", "Màu nâu", "🟤"),
            ("gray", "Màu xám", "🩶"),
            ("color", "Màu sắc", "🎨"),
        ],
        ["cat", "dog", "one", "book", "run", "big"],
        [
            ("The apple is red.", "Quả táo màu đỏ.", "The apple is [____].", ["red", "blue", "dog"], "red"),
            ("The sky is blue.", "Bầu trời màu xanh.", "The sky is [____].", ["blue", "green", "cat"], "blue"),
            ("Grass is green.", "Cỏ màu xanh lá.", "Grass is [____].", ["green", "red", "book"], "green"),
        ],
        [
            ("I see red, blue and yellow. Colors are beautiful.", "Tôi thấy đỏ, xanh và vàng. Màu sắc thật đẹp."),
        ],
    ),
    _theme(
        "en_g1_numbers",
        1,
        "Numbers 1-10",
        "Số đếm 1–10",
        3,
        "savannah",
        "boss_g1_chicken",
        [
            ("one", "Một", "1️⃣"),
            ("two", "Hai", "2️⃣"),
            ("three", "Ba", "3️⃣"),
            ("four", "Bốn", "4️⃣"),
            ("five", "Năm", "5️⃣"),
            ("six", "Sáu", "6️⃣"),
            ("seven", "Bảy", "7️⃣"),
            ("eight", "Tám", "8️⃣"),
            ("nine", "Chín", "9️⃣"),
            ("ten", "Mười", "🔟"),
            ("number", "Con số", "🔢"),
            ("count", "Đếm", "🧮"),
        ],
        ["cat", "red", "big", "run", "book", "dog"],
        [
            ("I have two cats.", "Tôi có hai con mèo.", "I have [____] cats.", ["two", "ten", "red"], "two"),
            ("One, two, three!", "Một, hai, ba!", "One, [____], three!", ["two", "five", "dog"], "two"),
            ("I can count to ten.", "Tôi đếm đến mười được.", "I can count to [____].", ["ten", "two", "cat"], "ten"),
        ],
        [
            ("One, two, three, four, five. I count every day at school.", "Một, hai, ba, bốn, năm. Tôi đếm mỗi ngày ở trường."),
        ],
    ),
    _theme(
        "en_g1_animals",
        1,
        "Animals",
        "Động vật",
        4,
        "savannah",
        "boss_g1_chicken",
        [
            ("cat", "Mèo", "🐱"),
            ("dog", "Chó", "🐶"),
            ("bird", "Chim", "🐦"),
            ("fish", "Cá", "🐟"),
            ("cow", "Bò", "🐮"),
            ("pig", "Heo", "🐷"),
            ("chicken", "Gà", "🐔"),
            ("duck", "Vịt", "🦆"),
            ("rabbit", "Thỏ", "🐰"),
            ("frog", "Ếch", "🐸"),
            ("bee", "Ong", "🐝"),
            ("butterfly", "Bướm", "🦋"),
            ("lion", "Sư tử", "🦁"),
            ("elephant", "Voi", "🐘"),
        ],
        ["apple", "book", "red", "car", "one", "run"],
        [
            ("I have a cat.", "Tôi có một con mèo.", "I have a [____].", ["cat", "book", "red"], "cat"),
            ("The dog can run.", "Con chó chạy được.", "The [____] can run.", ["dog", "apple", "blue"], "dog"),
            ("A bird can fly.", "Chim bay được.", "A [____] can fly.", ["bird", "fish", "book"], "bird"),
        ],
        [
            ("I like cats and dogs. Birds sing in the trees.", "Tôi thích mèo và chó. Chim hót trên cây."),
        ],
    ),
    _theme(
        "en_g1_fruits",
        1,
        "Fruits & Food",
        "Trái cây & thức ăn",
        5,
        "savannah",
        "boss_g1_chicken",
        [
            ("apple", "Táo", "🍎"),
            ("banana", "Chuối", "🍌"),
            ("orange", "Cam", "🍊"),
            ("grape", "Nho", "🍇"),
            ("watermelon", "Dưa hấu", "🍉"),
            ("mango", "Xoài", "🥭"),
            ("strawberry", "Dâu tây", "🍓"),
            ("pear", "Lê", "🍐"),
            ("milk", "Sữa", "🥛"),
            ("bread", "Bánh mì", "🍞"),
            ("rice", "Cơm", "🍚"),
            ("egg", "Trứng", "🥚"),
            ("cake", "Bánh ngọt", "🍰"),
            ("juice", "Nước ép", "🧃"),
        ],
        ["cat", "dog", "book", "run", "blue", "car"],
        [
            ("I like apples.", "Tôi thích táo.", "I like [____].", ["apples", "cats", "books"], "apples"),
            ("Bananas are yellow.", "Chuối màu vàng.", "[____] are yellow.", ["Bananas", "Cats", "Books"], "Bananas"),
            ("I drink milk.", "Tôi uống sữa.", "I drink [____].", ["milk", "book", "dog"], "milk"),
        ],
        [
            ("I eat an apple and a banana. Fruits are yummy and healthy.", "Tôi ăn táo và chuối. Trái cây ngon và tốt cho sức khỏe."),
        ],
    ),
    _theme(
        "en_g1_classroom",
        1,
        "My Classroom",
        "Lớp học của em",
        6,
        "savannah",
        "boss_g1_chicken",
        [
            ("book", "Sách", "📖"),
            ("pencil", "Bút chì", "✏️"),
            ("pen", "Bút mực", "🖊️"),
            ("eraser", "Tẩy", "🧽"),
            ("ruler", "Thước kẻ", "📏"),
            ("bag", "Cặp sách", "🎒"),
            ("desk", "Bàn học", "🪑"),
            ("chair", "Ghế", "💺"),
            ("school", "Trường học", "🏫"),
            ("teacher", "Cô giáo", "👩‍🏫"),
            ("student", "Học sinh", "🧒"),
            ("classroom", "Phòng học", "🏫"),
            ("crayon", "Bút màu", "🖍️"),
            ("paper", "Giấy", "📄"),
        ],
        ["cat", "dog", "apple", "run", "red", "fish"],
        [
            ("This is my book.", "Đây là sách của tôi.", "This is my [____].", ["book", "cat", "dog"], "book"),
            ("I go to school.", "Tôi đi học.", "I go to [____].", ["school", "home", "apple"], "school"),
            ("My teacher is kind.", "Cô giáo rất hiền.", "My [____] is kind.", ["teacher", "banana", "car"], "teacher"),
        ],
        [
            ("I have a book and a pencil. I love my school and my teacher.", "Tôi có sách và bút chì. Tôi yêu trường và cô giáo."),
        ],
    ),
    _theme(
        "en_g1_body",
        1,
        "My Body",
        "Cơ thể",
        7,
        "savannah",
        "boss_g1_chicken",
        [
            ("head", "Đầu", "🗣️"),
            ("eye", "Mắt", "👁️"),
            ("ear", "Tai", "👂"),
            ("nose", "Mũi", "👃"),
            ("mouth", "Miệng", "👄"),
            ("hand", "Bàn tay", "🖐️"),
            ("foot", "Bàn chân", "🦶"),
            ("arm", "Cánh tay", "💪"),
            ("leg", "Chân", "🦵"),
            ("hair", "Tóc", "💇"),
            ("tooth", "Răng", "🦷"),
            ("face", "Khuôn mặt", "😊"),
        ],
        ["cat", "book", "red", "apple", "run", "car"],
        [
            ("I wash my hands.", "Tôi rửa tay.", "I wash my [____].", ["hands", "books", "cats"], "hands"),
            ("Open your mouth.", "Hãy mở miệng.", "Open your [____].", ["mouth", "book", "dog"], "mouth"),
            ("I have two eyes.", "Tôi có hai mắt.", "I have two [____].", ["eyes", "books", "dogs"], "eyes"),
        ],
        [
            ("I have a head, two eyes and two hands. I brush my teeth every day.", "Tôi có đầu, hai mắt và hai tay. Tôi đánh răng mỗi ngày."),
        ],
    ),
]

# --- LỚP 2 (7 chủ đề) ---
G2_THEMES: List[Dict[str, Any]] = [
    _theme(
        "en_g2_pets",
        2,
        "My Pets",
        "Thú cưng của em",
        1,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("dog", "Chó", "🐶"),
            ("cat", "Mèo", "🐱"),
            ("rabbit", "Thỏ", "🐰"),
            ("fish", "Cá", "🐟"),
            ("bird", "Chim", "🐦"),
            ("turtle", "Rùa", "🐢"),
            ("hamster", "Chuột hamster", "🐹"),
            ("cute", "Dễ thương", "🥰"),
            ("playful", "Hay chơi", "🎾"),
            ("small", "Nhỏ", "🤏"),
            ("big", "To", "🐘"),
            ("pet", "Thú cưng", "🐾"),
            ("feed", "Cho ăn", "🍖"),
            ("name", "Tên", "📛"),
        ],
        ["book", "school", "red", "run", "desk", "apple"],
        [
            ("I have a cute dog.", "Tôi có chú chó dễ thương.", "I have a [____] dog.", ["cute", "big", "book"], "cute"),
            ("I have a small cat.", "Tôi có mèo nhỏ.", "I have a [____] cat.", ["small", "school", "run"], "small"),
            ("My pet is playful.", "Thú cưng hay chơi.", "My pet is [____].", ["playful", "desk", "red"], "playful"),
        ],
        [
            ("I have a small cat. Its name is Kitty. It is very playful.", "Tôi có mèo nhỏ. Tên là Kitty. Nó rất hay chơi."),
            ("I love my dog. I feed it every day.", "Tôi yêu chó của tôi. Tôi cho nó ăn mỗi ngày."),
        ],
    ),
    _theme(
        "en_g2_food",
        2,
        "Food & Drinks",
        "Đồ ăn & thức uống",
        2,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("apple", "Táo", "🍎"),
            ("banana", "Chuối", "🍌"),
            ("orange", "Cam", "🍊"),
            ("grape", "Nho", "🍇"),
            ("watermelon", "Dưa hấu", "🍉"),
            ("milk", "Sữa", "🥛"),
            ("bread", "Bánh mì", "🍞"),
            ("rice", "Cơm", "🍚"),
            ("meat", "Thịt", "🍖"),
            ("egg", "Trứng", "🥚"),
            ("cheese", "Phô mai", "🧀"),
            ("water", "Nước", "💧"),
            ("juice", "Nước ép", "🧃"),
            ("breakfast", "Bữa sáng", "🌅"),
            ("lunch", "Bữa trưa", "🍱"),
            ("dinner", "Bữa tối", "🌙"),
        ],
        ["cat", "book", "run", "car", "school", "dog"],
        [
            ("I eat rice for lunch.", "Tôi ăn cơm bữa trưa.", "I eat [____] for lunch.", ["rice", "book", "cat"], "rice"),
            ("I drink water.", "Tôi uống nước.", "I drink [____].", ["water", "dog", "run"], "water"),
            ("An apple a day is good.", "Ăn táo mỗi ngày tốt cho sức khỏe.", "An [____] a day is good.", ["apple", "book", "car"], "apple"),
        ],
        [
            ("I eat breakfast in the morning. I like bread, eggs and milk.", "Tôi ăn sáng buổi sáng. Tôi thích bánh mì, trứng và sữa."),
        ],
    ),
    _theme(
        "en_g2_home",
        2,
        "My Home",
        "Ngôi nhà của em",
        3,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("house", "Ngôi nhà", "🏠"),
            ("room", "Căn phòng", "🚪"),
            ("door", "Cửa", "🚪"),
            ("window", "Cửa sổ", "🪟"),
            ("bed", "Giường", "🛏️"),
            ("sofa", "Ghế sofa", "🛋️"),
            ("table", "Bàn", "🪑"),
            ("kitchen", "Nhà bếp", "🍳"),
            ("bathroom", "Phòng tắm", "🛁"),
            ("garden", "Vườn", "🌻"),
            ("family", "Gia đình", "👨‍👩‍👧"),
            ("home", "Nhà", "🏡"),
            ("clean", "Sạch sẽ", "✨"),
            ("sleep", "Ngủ", "😴"),
        ],
        ["cat", "school", "apple", "run", "dog", "book"],
        [
            ("This is my house.", "Đây là nhà tôi.", "This is my [____].", ["house", "cat", "book"], "house"),
            ("I sleep in my bed.", "Tôi ngủ trên giường.", "I sleep in my [____].", ["bed", "dog", "run"], "bed"),
            ("My home is clean.", "Nhà tôi sạch sẽ.", "My home is [____].", ["clean", "apple", "car"], "clean"),
        ],
        [
            ("My house has a garden. I sleep in my room. I love my home.", "Nhà tôi có vườn. Tôi ngủ trong phòng. Tôi yêu ngôi nhà."),
        ],
    ),
    _theme(
        "en_g2_clothes",
        2,
        "Clothes",
        "Quần áo",
        4,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("shirt", "Áo", "👕"),
            ("pants", "Quần", "👖"),
            ("dress", "Váy", "👗"),
            ("hat", "Mũ", "🧢"),
            ("shoes", "Giày", "👟"),
            ("socks", "Tất", "🧦"),
            ("coat", "Áo khoác", "🧥"),
            ("skirt", "Chân váy", "👗"),
            ("wear", "Mặc", "👔"),
            ("red", "Đỏ", "🔴"),
            ("blue", "Xanh dương", "🔵"),
            ("new", "Mới", "✨"),
            ("old", "Cũ", "👕"),
            ("beautiful", "Đẹp", "💐"),
        ],
        ["cat", "eat", "book", "run", "dog", "school"],
        [
            ("I wear a shirt.", "Tôi mặc áo.", "I wear a [____].", ["shirt", "cat", "book"], "shirt"),
            ("Put on your shoes.", "Hãy đi giày.", "Put on your [____].", ["shoes", "apple", "run"], "shoes"),
            ("This dress is beautiful.", "Chiếc váy này đẹp.", "This dress is [____].", ["beautiful", "dog", "desk"], "beautiful"),
        ],
        [
            ("I wear a shirt and pants to school. My new shoes are blue.", "Tôi mặc áo và quần đi học. Giày mới của tôi màu xanh."),
        ],
    ),
    _theme(
        "en_g2_nature",
        2,
        "Nature & Weather",
        "Thiên nhiên & thời tiết",
        5,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("sun", "Mặt trời", "☀️"),
            ("moon", "Mặt trăng", "🌙"),
            ("star", "Ngôi sao", "⭐"),
            ("sky", "Bầu trời", "🌤️"),
            ("cloud", "Đám mây", "☁️"),
            ("rain", "Mưa", "🌧️"),
            ("wind", "Gió", "💨"),
            ("tree", "Cây", "🌲"),
            ("flower", "Hoa", "🌸"),
            ("river", "Sông", "🏞️"),
            ("mountain", "Núi", "⛰️"),
            ("sea", "Biển", "🌊"),
            ("hot", "Nóng", "🥵"),
            ("cold", "Lạnh", "🥶"),
            ("sunny", "Nắng", "☀️"),
            ("rainy", "Mưa", "🌧️"),
        ],
        ["cat", "book", "desk", "dog", "pen", "run"],
        [
            ("The sun is hot.", "Mặt trời nóng.", "The sun is [____].", ["hot", "cold", "book"], "hot"),
            ("It is rainy today.", "Hôm nay trời mưa.", "It is [____] today.", ["rainy", "desk", "cat"], "rainy"),
            ("I see the moon at night.", "Tôi thấy trăng ban đêm.", "I see the [____] at night.", ["moon", "book", "dog"], "moon"),
        ],
        [
            ("The sun shines in the sky. Trees and flowers grow in the garden.", "Mặt trời chiếu trên trời. Cây và hoa mọc trong vườn."),
        ],
    ),
    _theme(
        "en_g2_vehicles",
        2,
        "Vehicles",
        "Phương tiện",
        6,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("car", "Ô tô", "🚗"),
            ("bus", "Xe buýt", "🚌"),
            ("bike", "Xe đạp", "🚲"),
            ("train", "Tàu hỏa", "🚂"),
            ("plane", "Máy bay", "✈️"),
            ("ship", "Tàu thủy", "🚢"),
            ("boat", "Thuyền", "⛵"),
            ("taxi", "Taxi", "🚕"),
            ("motorcycle", "Xe máy", "🏍️"),
            ("truck", "Xe tải", "🚚"),
            ("drive", "Lái xe", "🚗"),
            ("ride", "Đi (xe)", "🚴"),
            ("fast", "Nhanh", "💨"),
            ("slow", "Chậm", "🐢"),
        ],
        ["cat", "book", "apple", "run", "dog", "red"],
        [
            ("I go to school by bus.", "Tôi đi học bằng xe buýt.", "I go to school by [____].", ["bus", "apple", "cat"], "bus"),
            ("My dad drives a car.", "Bố tôi lái ô tô.", "My dad [____] a car.", ["drives", "eats", "reads"], "drives"),
            ("The train is fast.", "Tàu hỏa chạy nhanh.", "The train is [____].", ["fast", "slow", "book"], "fast"),
        ],
        [
            ("I ride my bike to the park. Planes fly high in the sky.", "Tôi đạp xe đến công viên. Máy bay bay cao trên trời."),
        ],
    ),
    _theme(
        "en_g2_body",
        2,
        "Body & Health",
        "Cơ thể & sức khỏe",
        7,
        "medieval_village",
        "boss_g2_phoenix",
        [
            ("eye", "Mắt", "👁️"),
            ("ear", "Tai", "👂"),
            ("nose", "Mũi", "👃"),
            ("mouth", "Miệng", "👄"),
            ("hand", "Tay", "🖐️"),
            ("foot", "Chân", "🦶"),
            ("arm", "Cánh tay", "💪"),
            ("leg", "Chân", "🦵"),
            ("heart", "Tim", "❤️"),
            ("healthy", "Khỏe mạnh", "💪"),
            ("sick", "Ốm", "🤒"),
            ("doctor", "Bác sĩ", "👨‍⚕️"),
            ("medicine", "Thuốc", "💊"),
            ("exercise", "Tập thể dục", "🏃"),
        ],
        ["cat", "book", "car", "apple", "run", "desk"],
        [
            ("Exercise keeps us healthy.", "Tập thể dục giúp khỏe.", "Exercise keeps us [____].", ["healthy", "sick", "book"], "healthy"),
            ("I wash my hands.", "Tôi rửa tay.", "I wash my [____].", ["hands", "books", "cars"], "hands"),
            ("The doctor helps sick people.", "Bác sĩ giúp người ốm.", "The [____] helps sick people.", ["doctor", "cat", "apple"], "doctor"),
        ],
        [
            ("I exercise every day. I eat healthy food and sleep well.", "Tôi tập thể dục mỗi ngày. Tôi ăn uống lành mạnh và ngủ đủ giấc."),
        ],
    ),
]

# --- LỚP 3 (6 chủ đề) ---
G3_THEMES: List[Dict[str, Any]] = [
    _theme(
        "en_g3_school_year",
        3,
        "Our School Year",
        "Năm học của chúng em",
        1,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("school", "Trường", "🏫"),
            ("classroom", "Lớp học", "📚"),
            ("teacher", "Giáo viên", "👩‍🏫"),
            ("student", "Học sinh", "🧒"),
            ("friend", "Bạn bè", "🤝"),
            ("lesson", "Bài học", "📖"),
            ("homework", "Bài tập về nhà", "📝"),
            ("test", "Bài kiểm tra", "📋"),
            ("holiday", "Kỳ nghỉ", "🏖️"),
            ("project", "Dự án", "🧪"),
            ("team", "Nhóm", "👥"),
            ("year", "Năm học", "📅"),
            ("learn", "Học", "📚"),
            ("study", "Ôn bài", "✏️"),
        ],
        ["cat", "apple", "dog", "run", "red", "fish"],
        [
            ("We are studying English now.", "Chúng em đang học tiếng Anh.", "We are [____] English now.", ["studying", "eating", "sleeping"], "studying"),
            ("I do my homework.", "Tôi làm bài tập.", "I do my [____].", ["homework", "breakfast", "shoes"], "homework"),
            ("My teacher is kind.", "Cô giáo rất hiền.", "My [____] is kind.", ["teacher", "banana", "car"], "teacher"),
        ],
        [
            ("In our school year, we study hard and join fun projects. I love my friends and my teacher.", "Trong năm học, chúng em học chăm và làm dự án vui. Tôi yêu bạn bè và cô giáo."),
        ],
    ),
    _theme(
        "en_g3_subjects",
        3,
        "School Subjects",
        "Các môn học",
        2,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("math", "Toán", "➕"),
            ("English", "Tiếng Anh", "🇬🇧"),
            ("art", "Mỹ thuật", "🎨"),
            ("music", "Âm nhạc", "🎵"),
            ("science", "Khoa học", "🔬"),
            ("reading", "Đọc", "📖"),
            ("writing", "Viết", "✍️"),
            ("drawing", "Vẽ", "🖍️"),
            ("sport", "Thể dục", "⚽"),
            ("history", "Lịch sử", "📜"),
            ("geography", "Địa lý", "🌍"),
            ("computer", "Tin học", "💻"),
            ("subject", "Môn học", "📘"),
            ("favorite", "Yêu thích", "⭐"),
        ],
        ["cat", "dog", "apple", "run", "bed", "car"],
        [
            ("Math is my favorite subject.", "Toán là môn tôi thích.", "[____] is my favorite subject.", ["Math", "Apple", "Dog"], "Math"),
            ("We have English today.", "Hôm nay có tiếng Anh.", "We have [____] today.", ["English", "breakfast", "shoes"], "English"),
            ("I like art and music.", "Tôi thích mỹ thuật và nhạc.", "I like [____] and music.", ["art", "cat", "run"], "art"),
        ],
        [
            ("I study math, English and science at school. Art and music are fun.", "Tôi học toán, tiếng Anh và khoa học. Mỹ thuật và nhạc rất vui."),
        ],
    ),
    _theme(
        "en_g3_school_places",
        3,
        "At School",
        "Ở trường",
        3,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("library", "Thư viện", "📚"),
            ("playground", "Sân chơi", "🛝"),
            ("canteen", "Căng tin", "🍽️"),
            ("office", "Văn phòng", "🏢"),
            ("lab", "Phòng thí nghiệm", "🧪"),
            ("gym", "Phòng gym", "🏋️"),
            ("hall", "Hội trường", "🎭"),
            ("gate", "Cổng trường", "🚧"),
            ("yard", "Sân trường", "🏫"),
            ("toilet", "Nhà vệ sinh", "🚻"),
            ("bell", "Chuông", "🔔"),
            ("line up", "Xếp hàng", "👫"),
            ("assembly", "Chào cờ", "🇻🇳"),
            ("break", "Giờ ra chơi", "⏰"),
        ],
        ["cat", "apple", "home", "dog", "red", "book"],
        [
            ("We read books in the library.", "Chúng em đọc sách ở thư viện.", "We read books in the [____].", ["library", "kitchen", "bed"], "library"),
            ("We play on the playground.", "Chúng em chơi ở sân chơi.", "We play on the [____].", ["playground", "moon", "desk"], "playground"),
            ("The bell rings at break time.", "Chuông reo giờ ra chơi.", "The [____] rings at break time.", ["bell", "apple", "cat"], "bell"),
        ],
        [
            ("We line up at the gate. We play on the playground at break time.", "Chúng em xếp hàng ở cổng. Giờ ra chơi chúng em chơi sân trường."),
        ],
    ),
    _theme(
        "en_g3_actions",
        3,
        "Actions & Verbs",
        "Động từ hành động",
        4,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("read", "Đọc", "📖"),
            ("write", "Viết", "✍️"),
            ("listen", "Nghe", "👂"),
            ("speak", "Nói", "🗣️"),
            ("draw", "Vẽ", "🖍️"),
            ("sing", "Hát", "🎤"),
            ("dance", "Nhảy", "💃"),
            ("run", "Chạy", "🏃"),
            ("jump", "Nhảy", "🦘"),
            ("swim", "Bơi", "🏊"),
            ("play", "Chơi", "⚽"),
            ("help", "Giúp đỡ", "🤝"),
            ("ask", "Hỏi", "❓"),
            ("answer", "Trả lời", "💬"),
        ],
        ["cat", "apple", "book", "red", "desk", "dog"],
        [
            ("Please listen to the teacher.", "Hãy nghe cô giáo.", "Please [____] to the teacher.", ["listen", "eat", "sleep"], "listen"),
            ("I can read and write.", "Tôi đọc và viết được.", "I can [____] and write.", ["read", "run", "swim"], "read"),
            ("We play football after school.", "Sau học chúng em đá bóng.", "We [____] football after school.", ["play", "read", "write"], "play"),
        ],
        [
            ("I read books, listen to music and play with friends. I speak English every day.", "Tôi đọc sách, nghe nhạc và chơi với bạn. Tôi nói tiếng Anh mỗi ngày."),
        ],
    ),
    _theme(
        "en_g3_daily",
        3,
        "Daily Routine",
        "Một ngày của em",
        5,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("morning", "Buổi sáng", "🌅"),
            ("afternoon", "Buổi chiều", "🌤️"),
            ("evening", "Buổi tối", "🌆"),
            ("night", "Ban đêm", "🌙"),
            ("wake up", "Thức dậy", "⏰"),
            ("brush teeth", "Đánh răng", "🪥"),
            ("get dressed", "Mặc quần áo", "👕"),
            ("go to school", "Đi học", "🏫"),
            ("have lunch", "Ăn trưa", "🍱"),
            ("go home", "Về nhà", "🏠"),
            ("do homework", "Làm bài", "📝"),
            ("watch TV", "Xem TV", "📺"),
            ("go to bed", "Đi ngủ", "🛏️"),
            ("always", "Luôn luôn", "♾️"),
            ("sometimes", "Đôi khi", "🎲"),
        ],
        ["cat", "apple", "car", "dog", "book", "run"],
        [
            ("I wake up in the morning.", "Tôi thức dậy buổi sáng.", "I [____] up in the morning.", ["wake", "go", "eat"], "wake"),
            ("I brush my teeth.", "Tôi đánh răng.", "I brush my [____].", ["teeth", "shoes", "book"], "teeth"),
            ("I go to bed at night.", "Tôi đi ngủ ban đêm.", "I go to [____] at night.", ["bed", "school", "park"], "bed"),
        ],
        [
            ("Every morning I wake up, brush my teeth and go to school. At night I do homework and go to bed.", "Mỗi sáng tôi dậy, đánh răng và đi học. Tối tôi làm bài rồi đi ngủ."),
        ],
    ),
    _theme(
        "en_g3_sports",
        3,
        "Sports & Games",
        "Thể thao & trò chơi",
        6,
        "industrial_city",
        "boss_g3_zeppelin",
        [
            ("football", "Bóng đá", "⚽"),
            ("basketball", "Bóng rổ", "🏀"),
            ("volleyball", "Bóng chuyền", "🏐"),
            ("badminton", "Cầu lông", "🏸"),
            ("swimming", "Bơi lội", "🏊"),
            ("running", "Chạy đua", "🏃"),
            ("team", "Đội", "👥"),
            ("win", "Thắng", "🏆"),
            ("lose", "Thua", "😢"),
            ("practice", "Luyện tập", "💪"),
            ("match", "Trận đấu", "🥅"),
            ("player", "Cầu thủ", "👟"),
            ("ball", "Quả bóng", "⚽"),
            ("game", "Trò chơi", "🎮"),
        ],
        ["cat", "book", "apple", "desk", "dog", "pen"],
        [
            ("We play football at school.", "Chúng em đá bóng ở trường.", "We play [____] at school.", ["football", "homework", "piano"], "football"),
            ("Our team won the match.", "Đội chúng em thắng trận.", "Our team [____] the match.", ["won", "ate", "read"], "won"),
            ("I practice swimming every week.", "Tôi tập bơi mỗi tuần.", "I practice [____] every week.", ["swimming", "reading", "sleeping"], "swimming"),
        ],
        [
            ("I love sports. I play football with my team. We practice and try to win every match.", "Tôi thích thể thao. Tôi đá bóng với đội. Chúng em luyện tập và cố gắng thắng mỗi trận."),
        ],
    ),
]

from app.data.english_boss_g123 import BOSS_PARA_CAP, THEME_BOSS_BLOCKS
from app.data.english_curriculum_g123_extra import G1_EXTRA, G2_EXTRA, G3_EXTRA

G1_THEMES.extend(G1_EXTRA)
G2_THEMES.extend(G2_EXTRA)
G3_THEMES.extend(G3_EXTRA)

ALL_G123_THEMES: List[Dict[str, Any]] = G1_THEMES + G2_THEMES + G3_THEMES

# Từ không dùng mẫu "This is a ..."
_SKIP_THIS_IS = frozenset(
    {
        "love",
        "count",
        "color",
        "study",
        "learn",
        "run",
        "jump",
        "sit",
        "stand",
        "walk",
        "play",
        "eat",
        "drink",
        "sleep",
        "sing",
        "happy",
        "sad",
        "angry",
        "tired",
        "hungry",
        "scared",
        "excited",
        "surprised",
        "proud",
        "sorry",
        "hot",
        "cold",
        "sunny",
        "rainy",
        "warm",
        "cool",
        "safe",
        "help",
        "painting",
        "dancing",
        "cooking",
        "gardening",
        "collecting",
        "cycling",
    }
)


def _join_words(words: List[str]) -> str:
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        return f"{words[0]} and {words[1]}"
    return ", ".join(words[:-1]) + f" and {words[-1]}"


def _join_vi(vis: List[str]) -> str:
    if len(vis) == 1:
        return vis[0]
    if len(vis) == 2:
        return f"{vis[0]} và {vis[1]}"
    return ", ".join(vis[:-1]) + f" và {vis[-1]}"


def _paragraph_from_block(
    grade: int,
    words: List[str],
    vis: List[str],
    subtopic_en: str,
    subtopic_vi: str,
) -> Tuple[str, str, Dict[str, str]]:
    w = _join_words(words)
    vi = _join_vi(vis)
    meta = {"subtopic_en": subtopic_en, "subtopic_vi": subtopic_vi}
    if grade == 1:
        en = f"Look! I see {w}. They are in my lesson about {subtopic_en.lower()}."
        vn = f"Nhìn kìa! Tôi thấy {vi}. Chúng ở bài học về {subtopic_vi.lower()}."
    elif grade == 2:
        en = f"Today we learn about {w}. This is the {subtopic_en.lower()} part of our theme."
        vn = f"Hôm nay chúng em học về {vi}. Đây là phần {subtopic_vi.lower()} trong chủ đề."
    else:
        en = (
            f"In our English lesson on {subtopic_en.lower()}, we read and speak about {w}. "
            f"I practice these words every day."
        )
        vn = (
            f"Trong bài tiếng Anh về {subtopic_vi.lower()}, chúng em đọc và nói về {vi}. "
            f"Tôi luyện các từ này mỗi ngày."
        )
    return en, vn, meta


def build_boss_paragraphs(spec: Dict[str, Any]) -> List[Tuple[str, str, Dict[str, str]]]:
    theme_id = spec["theme_id"]
    grade = spec["grade"]
    vi_map = {w[0]: w[1] for w in spec["vocab"]}
    out: List[Tuple[str, str, Dict[str, str]]] = []
    seen: set[str] = set()

    def _push(en: str, vi: str, meta: Dict[str, str]) -> None:
        key = en.lower().strip()
        if key in seen or len(out) >= BOSS_PARA_CAP:
            return
        seen.add(key)
        out.append((en, vi, meta))

    for en, vi in spec.get("paragraphs") or []:
        _push(en, vi, {"subtopic_en": "Story", "subtopic_vi": "Câu chuyện"})

    blocks = THEME_BOSS_BLOCKS.get(theme_id, [])
    if not blocks:
        chunk_size = 3 if grade == 1 else 4
        vocab = spec["vocab"]
        for i in range(0, len(vocab), chunk_size):
            chunk = vocab[i : i + chunk_size]
            keys = [w[0] for w in chunk]
            if len(keys) < 2:
                continue
            vis = [w[1] for w in chunk]
            n = len(out) + 1
            _push(*_paragraph_from_block(grade, keys, vis, f"Part {n}", f"Phần {n}"))
    else:
        for keys, sub_en, sub_vi in blocks:
            words = [k for k in keys if k in vi_map]
            if not words:
                continue
            vis = [vi_map[k] for k in words]
            _push(*_paragraph_from_block(grade, words, vis, sub_en, sub_vi))

    return out[:BOSS_PARA_CAP]


def enrich_theme(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Bổ sung câu điền từ + đoạn ghép từ vựng chủ đề (City/Boss)."""
    import copy

    out = copy.deepcopy(spec)
    vocab_triples = out["vocab"]
    vocab = [w[0] for w in vocab_triples]
    vi_map = {w[0]: w[1] for w in vocab_triples}
    pool = out["pool_distractors"]
    sentences: List[SentenceItem] = list(out["sentences"])
    seen = {s[0].lower() for s in sentences}

    def _add(target: str, vi: str, prompt: str, answer: str, choices: List[str]) -> None:
        if len(sentences) >= 6 or target.lower() in seen:
            return
        uniq = [answer] + [c for c in choices if c != answer]
        while len(uniq) < 3:
            uniq.append(pool[len(uniq) % max(len(pool), 1)])
        sentences.append((target, vi, prompt, uniq[:3], answer))
        seen.add(target.lower())

    for word, vi, _emoji in vocab_triples:
        if len(sentences) >= 6:
            break
        if word not in _SKIP_THIS_IS:
            _add(
                f"This is a {word}.",
                f"Đây là {vi}.",
                "This is a [____].",
                word,
                [word, pool[0] if pool else "cat", pool[1] if len(pool) > 1 else "book"],
            )
        _add(
            f"I see a {word}.",
            f"Tôi thấy {vi}.",
            "I see a [____].",
            word,
            [word, pool[0] if pool else "dog", vocab[(vocab.index(word) + 1) % len(vocab)]],
        )
        _add(
            f"I like {word}.",
            f"Tôi thích {vi}.",
            f"I like [____].",
            word,
            [word, pool[0] if pool else "book", pool[1] if len(pool) > 1 else "run"],
        )

    if len(vocab) >= 2 and len(sentences) < 6:
        w1, w2 = vocab[0], vocab[1]
        _add(
            f"I see a {w1} and a {w2}.",
            f"Tôi thấy {vi_map[w1]} và {vi_map[w2]}.",
            f"I see a {w1} and a [____].",
            w2,
            [w2, w1, pool[0] if pool else "cat"],
        )

    if len(vocab) >= 3 and len(sentences) < 6:
        w1, w2, w3 = vocab[0], vocab[1], vocab[2]
        _add(
            f"My {w1}, {w2} and {w3} are here.",
            f"{vi_map[w1]}, {vi_map[w2]} và {vi_map[w3]} của tôi ở đây.",
            f"My {w1}, {w2} and [____] are here.",
            w3,
            [w3, w1, pool[0] if pool else "dog"],
        )

    out["sentences"] = sentences[:6]

    boss_items = build_boss_paragraphs(out)
    out["boss_paragraphs"] = boss_items
    out["paragraphs"] = [(en, vi) for en, vi, _m in boss_items]
    return out


def apply_theme_to_session(db, spec: Dict[str, Any]) -> None:
    """Insert one theme + stages + items (caller handles delete)."""
    from app.models.play.english_catalog import (
        PlayEnglishTheme,
        PlayEnglishStage,
        PlayEnglishStageItem,
    )

    theme_id = spec["theme_id"]
    db.add(
        PlayEnglishTheme(
            id=theme_id,
            grade=spec["grade"],
            title=spec["title"],
            order_index=spec["order_index"],
            background_scene=spec["scene"],
            boss_id=spec["boss_id"],
            content_pack_id=CONTENT_PACK,
            is_active=True,
            meta_json={"vi_title": spec["vi_title"], "curriculum": "gdpt2018_g123"},
        )
    )
    db.flush()
    stage_vocab = f"{theme_id}_vocab"
    stage_sent = f"{theme_id}_sentence"
    stage_para = f"{theme_id}_paragraph"
    for sid, stype, limit, speak, conf in [
        (stage_vocab, "vocab", None, False, None),
        (stage_sent, "sentence", 30, True, 0.55 if spec["grade"] <= 2 else 0.60),
        (stage_para, "paragraph", None, True, 0.55 if spec["grade"] <= 2 else 0.65),
    ]:
        db.add(
            PlayEnglishStage(
                id=sid,
                theme_id=theme_id,
                stage_type=stype,
                time_limit_seconds=limit,
                speaking_required=speak,
                min_confidence=conf,
                config_json={"boss_fight": stype == "paragraph"},
            )
        )
    db.flush()

    pool = spec["pool_distractors"]
    for idx, (word, vi, emoji) in enumerate(spec["vocab"]):
        distractors = [d for d in pool if d.lower() != word.lower()][:3]
        db.add(
            PlayEnglishStageItem(
                id=f"{stage_vocab}_{word.replace(' ', '_')}",
                stage_id=stage_vocab,
                item_type="target",
                target_text=word,
                visual_asset=f"en_vocab_{word.replace(' ', '_')}",
                translation_vi=vi,
                options_json={
                    "emoji": emoji,
                    "prompt_en": f"Shoot the word: {word}!",
                    "distractors": distractors,
                },
                order_index=idx,
                skill_unit_id=f"{theme_id}_vocab_{word.replace(' ', '_')}",
            )
        )

    for sidx, (target, vi, prompt, choices, answer) in enumerate(spec["sentences"]):
        db.add(
            PlayEnglishStageItem(
                id=f"{stage_sent}_q{sidx + 1}",
                stage_id=stage_sent,
                item_type="target",
                target_text=target,
                translation_vi=vi,
                options_json={
                    "prompt": prompt,
                    "choices": choices,
                    "answer": answer,
                    "vocab_theme": [w[0] for w in spec["vocab"][:8]],
                },
                order_index=sidx,
                skill_unit_id=f"{theme_id}_sentence_q{sidx + 1}",
            )
        )

    boss_items = spec.get("boss_paragraphs")
    if not boss_items:
        boss_items = [(p[0], p[1], {}) for p in spec["paragraphs"]]

    for pidx, item in enumerate(boss_items):
        if len(item) == 3:
            para, vi, meta = item
        else:
            para, vi = item[0], item[1]
            meta = {}
        db.add(
            PlayEnglishStageItem(
                id=f"{stage_para}_q{pidx + 1}",
                stage_id=stage_para,
                item_type="target",
                target_text=para,
                translation_vi=vi,
                options_json={
                    "prompt": "Read aloud to defeat the boss",
                    "answer_hint": para,
                    "vocab_theme": [w[0] for w in spec["vocab"][:10]],
                    "subtopic_en": meta.get("subtopic_en", f"Part {pidx + 1}"),
                    "subtopic_vi": meta.get("subtopic_vi", f"Phần {pidx + 1}"),
                    "boss_round": pidx + 1,
                    "boss_rounds_total": len(boss_items),
                },
                order_index=pidx,
                skill_unit_id=f"{theme_id}_paragraph_q{pidx + 1}",
            ),
        )


def delete_grades_1_2_3(db) -> None:
    from app.models.play.english_catalog import (
        PlayEnglishTheme,
        PlayEnglishStage,
        PlayEnglishStageItem,
    )

    theme_ids = [
        t.id for t in db.query(PlayEnglishTheme).filter(PlayEnglishTheme.grade.in_([1, 2, 3])).all()
    ]
    if not theme_ids:
        return
    stage_ids = [
        s.id for s in db.query(PlayEnglishStage.id).filter(PlayEnglishStage.theme_id.in_(theme_ids)).all()
    ]
    if stage_ids:
        db.query(PlayEnglishStageItem).filter(PlayEnglishStageItem.stage_id.in_(stage_ids)).delete(
            synchronize_session=False
        )
        db.query(PlayEnglishStage).filter(PlayEnglishStage.id.in_(stage_ids)).delete(synchronize_session=False)
    db.query(PlayEnglishTheme).filter(PlayEnglishTheme.id.in_(theme_ids)).delete(synchronize_session=False)


def seed_english_curriculum_g123(db) -> int:
    """Xóa và nạp lại toàn bộ chủ đề lớp 1–3. Trả về số chủ đề."""
    delete_grades_1_2_3(db)
    db.flush()
    for spec in ALL_G123_THEMES:
        apply_theme_to_session(db, enrich_theme(spec))
        db.flush()
    return len(ALL_G123_THEMES)
