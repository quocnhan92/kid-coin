"""
Big Boss paragraphs — grouped by small subtopics per theme (grades 1–3).
Each entry: (word_keys, subtopic_en, subtopic_vi)
Paragraphs are built from theme vocab at seed time.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

BossBlock = Tuple[List[str], str, str]

THEME_BOSS_BLOCKS: Dict[str, List[BossBlock]] = {
    # --- Grade 1 ---
    "en_g1_family": [
        (["mom", "dad", "love"], "My parents", "Bố mẹ"),
        (["sister", "brother", "family"], "Siblings", "Anh chị em"),
        (["grandma", "grandpa", "aunt"], "Grandparents & aunt", "Ông bà & cô"),
        (["uncle", "cousin", "family"], "More family", "Họ hàng"),
    ],
    "en_g1_colors": [
        (["red", "blue", "yellow"], "Primary colors", "Màu cơ bản"),
        (["green", "orange", "pink"], "More colors", "Thêm màu"),
        (["purple", "black", "white"], "Dark & light", "Tối & sáng"),
        (["brown", "gray", "color"], "All colors", "Màu sắc"),
    ],
    "en_g1_numbers": [
        (["one", "two", "three"], "Numbers 1–3", "Số 1–3"),
        (["four", "five", "six"], "Numbers 4–6", "Số 4–6"),
        (["seven", "eight", "nine"], "Numbers 7–9", "Số 7–9"),
        (["ten", "number", "count"], "Count to ten", "Đếm đến 10"),
    ],
    "en_g1_animals": [
        (["cat", "dog", "bird"], "Pets", "Thú cưng"),
        (["fish", "rabbit", "frog"], "Small animals", "Động vật nhỏ"),
        (["cow", "pig", "chicken"], "Farm animals", "Trang trại"),
        (["duck", "bee", "butterfly"], "More animals", "Thêm động vật"),
        (["lion", "elephant"], "Big animals", "Động vật lớn"),
    ],
    "en_g1_fruits": [
        (["apple", "banana", "orange"], "Sweet fruits", "Trái ngọt"),
        (["grape", "watermelon", "mango"], "Summer fruits", "Trái mùa hè"),
        (["strawberry", "pear"], "More fruits", "Thêm trái cây"),
        (["milk", "bread", "rice"], "Food & meals", "Thức ăn"),
        (["egg", "cake", "juice"], "Breakfast", "Bữa sáng"),
    ],
    "en_g1_classroom": [
        (["book", "pencil", "pen"], "School things", "Đồ dùng học"),
        (["eraser", "ruler", "crayon"], "More tools", "Dụng cụ"),
        (["desk", "chair", "bag"], "In the classroom", "Trong lớp"),
        (["school", "teacher", "student"], "At school", "Ở trường"),
        (["classroom", "paper"], "My classroom", "Lớp học"),
    ],
    "en_g1_body": [
        (["head", "face", "hair"], "Head & face", "Đầu & mặt"),
        (["eye", "ear", "nose"], "On my face", "Trên mặt"),
        (["mouth", "tooth"], "Mouth & teeth", "Miệng & răng"),
        (["hand", "arm", "foot"], "Arms & hands", "Tay & chân"),
        (["leg"], "My legs", "Chân"),
    ],
    "en_g1_toys": [
        (["ball", "doll", "kite"], "Fun toys", "Đồ chơi vui"),
        (["balloon", "teddy", "toy"], "My toys", "Đồ chơi của em"),
        (["block", "puzzle", "car"], "Building toys", "Xếp hình"),
        (["robot"], "Robot toy", "Rô-bốt"),
    ],
    "en_g1_weather": [
        (["sun", "sky", "day"], "Sun & sky", "Mặt trời & trời"),
        (["cloud", "rain", "wind"], "Rain & wind", "Mưa & gió"),
        (["hot", "cold", "sunny"], "Hot & cold", "Nóng & lạnh"),
        (["rainy"], "Rainy day", "Ngày mưa"),
    ],
    "en_g1_actions": [
        (["run", "jump", "walk"], "Moving", "Di chuyển"),
        (["sit", "stand", "play"], "Play time", "Giờ chơi"),
        (["eat", "drink", "sleep"], "Eat & rest", "Ăn & nghỉ"),
        (["sing"], "Sing", "Hát"),
    ],
    # --- Grade 2 ---
    "en_g2_pets": [
        (["dog", "cat", "rabbit"], "My pets", "Thú cưng"),
        (["fish", "bird", "turtle"], "More pets", "Thêm thú cưng"),
        (["hamster", "pet", "name"], "Pet care", "Chăm thú cưng"),
        (["cute", "playful", "small"], "Pet words", "Tính từ"),
        (["big", "feed"], "Feed my pet", "Cho ăn"),
    ],
    "en_g2_food": [
        (["apple", "banana", "orange"], "Fruits", "Trái cây"),
        (["grape", "watermelon"], "More fruits", "Thêm trái"),
        (["milk", "water", "juice"], "Drinks", "Đồ uống"),
        (["bread", "rice", "egg"], "Main food", "Món chính"),
        (["meat", "cheese", "breakfast"], "Meals", "Bữa ăn"),
        (["lunch", "dinner"], "Lunch & dinner", "Trưa & tối"),
    ],
    "en_g2_home": [
        (["house", "home", "family"], "My home", "Ngôi nhà"),
        (["room", "bed", "sleep"], "My room", "Phòng ngủ"),
        (["door", "window", "sofa"], "In the house", "Trong nhà"),
        (["table", "kitchen", "bathroom"], "Rooms", "Các phòng"),
        (["garden", "clean"], "Garden", "Vườn"),
    ],
    "en_g2_clothes": [
        (["shirt", "pants", "dress"], "Clothes", "Quần áo"),
        (["hat", "shoes", "socks"], "Hat & shoes", "Mũ & giày"),
        (["coat", "skirt", "wear"], "Wear clothes", "Mặc đồ"),
        (["red", "blue", "new"], "Colors & new", "Màu & mới"),
        (["old", "beautiful"], "Nice clothes", "Đồ đẹp"),
    ],
    "en_g2_nature": [
        (["sun", "moon", "star"], "Sky", "Bầu trời"),
        (["sky", "cloud", "rain"], "Weather", "Thời tiết"),
        (["wind", "hot", "cold"], "Hot & cold", "Nóng lạnh"),
        (["tree", "flower", "river"], "Plants & water", "Cây & sông"),
        (["mountain", "sea", "sunny"], "Land & sea", "Núi & biển"),
        (["rainy"], "Rainy days", "Ngày mưa"),
    ],
    "en_g2_vehicles": [
        (["car", "bus", "bike"], "On the road", "Trên đường"),
        (["train", "plane", "ship"], "Long trips", "Đi xa"),
        (["boat", "taxi", "motorcycle"], "More vehicles", "Thêm xe"),
        (["truck", "drive", "ride"], "Drive & ride", "Lái & đi"),
        (["fast", "slow"], "Fast or slow", "Nhanh chậm"),
    ],
    "en_g2_body": [
        (["eye", "ear", "nose"], "Face", "Khuôn mặt"),
        (["mouth", "hand", "foot"], "Body parts", "Bộ phận"),
        (["arm", "leg", "heart"], "Arms & heart", "Tay & tim"),
        (["healthy", "sick", "doctor"], "Health", "Sức khỏe"),
        (["medicine", "exercise"], "Stay healthy", "Giữ khỏe"),
    ],
    "en_g2_school": [
        (["notebook", "chalk", "board"], "In class", "Trong lớp"),
        (["classmate", "lesson", "question"], "Learning", "Học bài"),
        (["answer", "library", "playground"], "School places", "Nơi ở trường"),
        (["canteen"], "Canteen", "Căng tin"),
    ],
    "en_g2_feelings": [
        (["happy", "sad", "angry"], "Strong feelings", "Cảm xúc mạnh"),
        (["tired", "hungry", "scared"], "How I feel", "Cảm giác"),
        (["excited", "surprised", "proud"], "Good feelings", "Cảm giác tốt"),
        (["sorry"], "Say sorry", "Xin lỗi"),
    ],
    "en_g2_jobs": [
        (["doctor", "nurse", "teacher"], "Help people", "Giúp mọi người"),
        (["farmer", "chef", "driver"], "Work places", "Nơi làm việc"),
        (["police", "firefighter", "worker"], "Community jobs", "Nghề cộng đồng"),
        (["singer"], "Be a singer", "Ca sĩ"),
    ],
    # --- Grade 3 ---
    "en_g3_school_year": [
        (["school", "classroom", "teacher"], "School people", "Người ở trường"),
        (["student", "friend", "team"], "Friends & team", "Bạn & nhóm"),
        (["lesson", "homework", "test"], "Study hard", "Học chăm"),
        (["project", "holiday", "year"], "School year", "Năm học"),
        (["learn", "study"], "Learn every day", "Học mỗi ngày"),
    ],
    "en_g3_subjects": [
        (["math", "English", "science"], "Main subjects", "Môn chính"),
        (["art", "music", "sport"], "Fun subjects", "Môn vui"),
        (["reading", "writing", "drawing"], "Read & write", "Đọc viết"),
        (["history", "geography", "computer"], "More subjects", "Thêm môn"),
        (["subject", "favorite"], "Favorite subject", "Môn yêu thích"),
    ],
    "en_g3_school_places": [
        (["library", "playground", "canteen"], "Fun places", "Nơi vui"),
        (["office", "lab", "gym"], "Special rooms", "Phòng đặc biệt"),
        (["hall", "gate", "yard"], "School yard", "Sân trường"),
        (["bell", "line up", "assembly"], "School rules", "Nội quy"),
        (["break", "toilet"], "Break time", "Giờ ra chơi"),
    ],
    "en_g3_actions": [
        (["read", "write", "listen"], "In class", "Trong lớp học"),
        (["speak", "ask", "answer"], "Talk in English", "Nói tiếng Anh"),
        (["draw", "sing", "dance"], "Creative actions", "Sáng tạo"),
        (["run", "jump", "swim"], "Sports actions", "Vận động"),
        (["play", "help"], "Play & help", "Chơi & giúp"),
    ],
    "en_g3_daily": [
        (["morning", "wake up", "brush teeth"], "Morning", "Buổi sáng"),
        (["get dressed", "go to school", "have lunch"], "Daytime", "Ban ngày"),
        (["afternoon", "go home", "do homework"], "After school", "Sau học"),
        (["evening", "watch TV", "go to bed"], "Evening", "Buổi tối"),
        (["night", "always", "sometimes"], "Every day", "Mỗi ngày"),
    ],
    "en_g3_sports": [
        (["football", "basketball", "volleyball"], "Ball sports", "Bóng"),
        (["badminton", "swimming", "running"], "More sports", "Thêm môn"),
        (["team", "player", "ball"], "My team", "Đội của em"),
        (["practice", "match", "win"], "Practice & win", "Luyện & thắng"),
        (["lose", "game"], "Win or lose", "Thắng thua"),
    ],
    "en_g3_seasons": [
        (["spring", "summer", "flower"], "Spring & summer", "Xuân & hè"),
        (["autumn", "winter", "leaf"], "Autumn & winter", "Thu & đông"),
        (["warm", "cool", "snow"], "Warm & cold", "Ấm & lạnh"),
        (["season"], "Four seasons", "Bốn mùa"),
    ],
    "en_g3_hobbies": [
        (["painting", "drawing", "music"], "Art hobbies", "Nghệ thuật"),
        (["dancing", "singing", "chess"], "Fun hobbies", "Sở thích vui"),
        (["cooking", "gardening", "fishing"], "Outdoor hobbies", "Ngoài trời"),
        (["collecting", "photography", "cycling"], "More hobbies", "Thêm sở thích"),
    ],
    "en_g3_community": [
        (["hospital", "market", "bank"], "Places in town", "Nơi trong phố"),
        (["post office", "street", "traffic"], "Streets", "Đường phố"),
        (["neighbor", "community", "help"], "Neighbors", "Hàng xóm"),
        (["safe"], "Stay safe", "An toàn"),
    ],
    "en_g3_world": [
        (["country", "city", "village"], "Places to live", "Nơi ở"),
        (["river", "lake", "ocean"], "Water", "Nước"),
        (["island", "forest", "desert"], "Landforms", "Địa hình"),
        (["earth"], "Our earth", "Trái đất"),
    ],
}

BOSS_PARA_CAP = 6
