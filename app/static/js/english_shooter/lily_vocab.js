/* Lily — vocabulary packs (G1/G2 curriculum + fun modes) */
(function (global) {
  const w = (en, vi, emoji, color) => ({
    en: en.toUpperCase(),
    vi,
    emoji,
    color: color || "#F9A8D4",
  });

  const bakeryData = [
    w("butter", "bơ", "🧈", "#FDE68A"),
    w("egg", "trứng", "🥚", "#FEF3C7"),
    w("milk", "sữa", "🥛", "#fff"),
    w("flour", "bột mì", "🌾", "#FCD34D"),
    w("honey", "mật ong", "🍯", "#F59E0B"),
    w("sugar", "đường", "🍬", "#FCA5A5"),
    w("cream", "kem tươi", "🍦", "#fff"),
    w("berry", "dâu rừng", "🫐", "#C4B5FD"),
    w("lemon", "chanh", "🍋", "#FEF08A"),
    w("cocoa", "ca cao", "🍫", "#78350F"),
    w("apple", "táo", "🍎", "#FCA5A5"),
    w("salt", "muối", "🧂", "#E2E8F0"),
  ];

  const fashionData = [
    w("dress", "váy", "👗", "#F9A8D4"),
    w("hat", "mũ", "👒", "#FDE68A"),
    w("shoes", "giày", "👠", "#FCA5A5"),
    w("bag", "túi xách", "👜", "#C4B5FD"),
    w("bow", "nơ", "🎀", "#F9A8D4"),
    w("scarf", "khăn quàng", "🧣", "#A5B4FC"),
    w("skirt", "chân váy", "🩱", "#6EE7B7"),
    w("coat", "áo khoác", "🧥", "#93C5FD"),
    w("crown", "vương miện", "👑", "#FDE68A"),
    w("glove", "găng tay", "🧤", "#FCA5A5"),
    w("socks", "tất", "🧦", "#C4B5FD"),
    w("ring", "nhẫn", "💍", "#FDE68A"),
  ];

  const g1Family = [
    w("mom", "mẹ", "👩"), w("dad", "bố", "👨"), w("baby", "em bé", "👶"),
    w("sister", "chị/em gái", "👧"), w("brother", "anh/em trai", "👦"),
    w("family", "gia đình", "👨‍👩‍👧"), w("grandma", "bà", "👵"), w("grandpa", "ông", "👴"),
    w("aunt", "cô/dì", "👩"), w("uncle", "chú/bác", "👨"), w("cousin", "anh/chị/em họ", "🧒"),
    w("love", "yêu thương", "❤️", "#FCA5A5"),
  ];

  const g1Colors = [
    w("red", "màu đỏ", "🔴"), w("blue", "màu xanh dương", "🔵"),
    w("yellow", "màu vàng", "🟡"), w("green", "màu xanh lá", "🟢"),
    w("orange", "màu cam", "🟠"), w("pink", "màu hồng", "🩷"),
    w("purple", "màu tím", "🟣"), w("black", "màu đen", "⚫"),
    w("white", "màu trắng", "⚪"), w("brown", "màu nâu", "🟤"),
    w("gray", "màu xám", "🩶"), w("color", "màu sắc", "🎨", "#C4B5FD"),
  ];

  const g1Animals = [
    w("cat", "mèo", "🐱"), w("dog", "chó", "🐶"), w("bird", "chim", "🐦"),
    w("fish", "cá", "🐟"), w("cow", "bò", "🐮"), w("pig", "heo", "🐷"),
    w("chicken", "gà", "🐔"), w("duck", "vịt", "🦆"), w("rabbit", "thỏ", "🐰"),
    w("frog", "ếch", "🐸"), w("bee", "ong", "🐝"), w("butterfly", "bướm", "🦋"),
    w("lion", "sư tử", "🦁"), w("elephant", "voi", "🐘"),
  ];

  const g1Fruits = [
    w("apple", "táo", "🍎"), w("banana", "chuối", "🍌"), w("orange", "cam", "🍊"),
    w("grape", "nho", "🍇"), w("watermelon", "dưa hấu", "🍉"), w("mango", "xoài", "🥭"),
    w("strawberry", "dâu tây", "🍓"), w("pear", "lê", "🍐"), w("milk", "sữa", "🥛"),
    w("bread", "bánh mì", "🍞"), w("rice", "cơm", "🍚"), w("egg", "trứng", "🥚"),
    w("cake", "bánh ngọt", "🍰"), w("juice", "nước ép", "🧃"),
  ];

  const g1Classroom = [
    w("book", "sách", "📖"), w("pencil", "bút chì", "✏️"), w("pen", "bút mực", "🖊️"),
    w("eraser", "tẩy", "🧽"), w("ruler", "thước kẻ", "📏"), w("bag", "cặp sách", "🎒"),
    w("desk", "bàn học", "🪑"), w("chair", "ghế", "💺"), w("school", "trường học", "🏫"),
    w("teacher", "cô giáo", "👩‍🏫"), w("student", "học sinh", "🧒"),
    w("classroom", "phòng học", "🏫"), w("crayon", "bút màu", "🖍️"), w("paper", "giấy", "📄"),
  ];

  const g2Pets = [
    w("dog", "chó", "🐶"), w("cat", "mèo", "🐱"), w("rabbit", "thỏ", "🐰"),
    w("fish", "cá", "🐟"), w("bird", "chim", "🐦"), w("turtle", "rùa", "🐢"),
    w("hamster", "chuột hamster", "🐹"), w("cute", "dễ thương", "🥰"),
    w("playful", "hay chơi", "🎾"), w("small", "nhỏ", "🤏"), w("big", "to", "🐘"),
    w("pet", "thú cưng", "🐾"), w("feed", "cho ăn", "🍖"), w("name", "tên", "📛"),
  ];

  const g2Food = [
    w("apple", "táo", "🍎"), w("banana", "chuối", "🍌"), w("orange", "cam", "🍊"),
    w("grape", "nho", "🍇"), w("watermelon", "dưa hấu", "🍉"), w("milk", "sữa", "🥛"),
    w("bread", "bánh mì", "🍞"), w("rice", "cơm", "🍚"), w("meat", "thịt", "🍖"),
    w("egg", "trứng", "🥚"), w("cheese", "phô mai", "🧀"), w("water", "nước", "💧"),
    w("juice", "nước ép", "🧃"), w("breakfast", "bữa sáng", "🌅"),
    w("lunch", "bữa trưa", "🍱"), w("dinner", "bữa tối", "🌙"),
  ];

  const g2Home = [
    w("house", "ngôi nhà", "🏠"), w("room", "căn phòng", "🚪"), w("door", "cửa", "🚪"),
    w("window", "cửa sổ", "🪟"), w("bed", "giường", "🛏️"), w("sofa", "ghế sofa", "🛋️"),
    w("table", "bàn", "🪑"), w("kitchen", "nhà bếp", "🍳"), w("bathroom", "phòng tắm", "🛁"),
    w("garden", "vườn", "🌻"), w("family", "gia đình", "👨‍👩‍👧"), w("home", "nhà", "🏡"),
    w("clean", "sạch sẽ", "✨"), w("sleep", "ngủ", "😴"),
  ];

  const g2Nature = [
    w("sun", "mặt trời", "☀️"), w("moon", "mặt trăng", "🌙"), w("star", "ngôi sao", "⭐"),
    w("sky", "bầu trời", "🌤️"), w("cloud", "đám mây", "☁️"), w("rain", "mưa", "🌧️"),
    w("wind", "gió", "💨"), w("tree", "cây", "🌲"), w("flower", "hoa", "🌸"),
    w("river", "sông", "🏞️"), w("mountain", "núi", "⛰️"), w("sea", "biển", "🌊"),
    w("hot", "nóng", "🥵"), w("cold", "lạnh", "🥶"), w("sunny", "nắng", "☀️"),
    w("rainy", "mưa", "🌧️"),
  ];

  const g2Vehicles = [
    w("car", "ô tô", "🚗"), w("bus", "xe buýt", "🚌"), w("bike", "xe đạp", "🚲"),
    w("train", "tàu hỏa", "🚂"), w("plane", "máy bay", "✈️"), w("ship", "tàu thủy", "🚢"),
    w("boat", "thuyền", "⛵"), w("taxi", "taxi", "🚕"), w("motorcycle", "xe máy", "🏍️"),
    w("truck", "xe tải", "🚚"), w("drive", "lái xe", "🚗"), w("ride", "đi (xe)", "🚴"),
    w("fast", "nhanh", "💨"), w("slow", "chậm", "🐢"),
  ];

  const cakeResults = [
    { emoji: "🎂", msg: "Bánh sinh nhật tuyệt vời!" },
    { emoji: "🧁", msg: "Cupcake siêu dễ thương!" },
    { emoji: "🥧", msg: "Bánh pie thơm lừng!" },
    { emoji: "🍰", msg: "Bánh kem ngọt ngào!" },
  ];

  const MODES = {
    bakery: {
      grade: 0, section: "fun", scene: "bakery", btnClass: "bakery",
      title: "Tiệm Bánh Lily", hud: "🍰 Tiệm Bánh", icon: "🍰",
      desc: "Chọn nguyên liệu đúng để nướng bánh thật ngon!",
      data: bakeryData, mindRoot: "🍰 Bánh", rootColor: "#F9A8D4", chipClass: "",
      hint: "Kéo đúng nguyên liệu vào bát ✨", dropEmoji: "🥣",
      tip: "Chào bạn! Hãy kéo nguyên liệu vào bát nhé 🌸",
      celebrate: { type: "cake", pool: cakeResults },
    },
    fashion: {
      grade: 0, section: "fun", scene: "fashion", btnClass: "fashion",
      title: "Tủ Đồ Thần Kỳ", hud: "👗 Tủ Đồ", icon: "👗",
      desc: "Kéo trang phục đúng để mặc cho Lily thật xinh!",
      data: fashionData, mindRoot: "👗 Thời Trang", rootColor: "#C4B5FD", chipClass: "fashion-chip",
      hint: "Kéo đúng trang phục cho Lily 💕", dropEmoji: "👗",
      tip: "Hãy chọn trang phục xinh cho Lily nhé! 💕",
    },
    family: {
      grade: 1, section: "g1", scene: "drag", btnClass: "grade1",
      title: "Gia Đình Lily", hud: "👨‍👩‍👧 Gia Đình", icon: "👨‍👩‍👧",
      desc: "Gặp gỡ mọi người trong gia đình — từ vựng lớp 1!",
      data: g1Family, mindRoot: "👨‍👩‍👧 Gia Đình", rootColor: "#F9A8D4", chipClass: "g1-chip",
      hint: "Kéo đúng người vào khung ảnh gia đình ✨", dropEmoji: "🖼️",
      tip: "Cùng Lily học từ vựng gia đình nhé! 🌸",
      celebrate: { type: "emoji", pool: [{ emoji: "💕", msg: "Gia đình sum vầy!" }] },
    },
    animals: {
      grade: 1, section: "g1", scene: "drag", btnClass: "grade1",
      title: "Vườn Thú", hud: "🐾 Vườn Thú", icon: "🦁",
      desc: "Đưa thú vào chuồng — học tên con vật lớp 1!",
      data: g1Animals, mindRoot: "🐾 Động Vật", rootColor: "#6EE7B7", chipClass: "g1-chip",
      hint: "Kéo đúng con vật vào chuồng 🌿", dropEmoji: "🏡",
      tip: "Ruồi Lily thích động vật lắm! 🦋",
      celebrate: { type: "emoji", pool: [{ emoji: "🎉", msg: "Chú thú về chuồng rồi!" }] },
    },
    fruit: {
      grade: 1, section: "g1", scene: "drag", btnClass: "grade1",
      title: "Chợ Trái Cây", hud: "🍎 Chợ Trái Cây", icon: "🍊",
      desc: "Chọn trái cây & thức ăn đúng — từ vựng lớp 1!",
      data: g1Fruits, mindRoot: "🍎 Trái Cây", rootColor: "#FDE68A", chipClass: "g1-chip",
      hint: "Kéo đúng món vào giỏ hàng 🧺", dropEmoji: "🧺",
      tip: "Mua trái cây tươi cùng Lily nhé! 🍓",
      celebrate: { type: "emoji", pool: [{ emoji: "😋", msg: "Ngon quá đi!" }] },
    },
    classroom: {
      grade: 1, section: "g1", scene: "drag", btnClass: "grade1",
      title: "Lớp Học", hud: "🏫 Lớp Học", icon: "📚",
      desc: "Xếp đồ dùng học tập đúng chỗ — lớp 1!",
      data: g1Classroom, mindRoot: "🏫 Lớp Học", rootColor: "#93C5FD", chipClass: "g1-chip",
      hint: "Kéo đồ học tập lên bàn 📖", dropEmoji: "🪑",
      tip: "Chuẩn bị đi học cùng Lily nào! ✏️",
      celebrate: { type: "emoji", pool: [{ emoji: "⭐", msg: "Sẵn sàng học giỏi!" }] },
    },
    colors: {
      grade: 1, section: "g1", scene: "drag", btnClass: "grade1",
      title: "Bảng Màu", hud: "🎨 Bảng Màu", icon: "🌈",
      desc: "Phối màu đúng — học colors lớp 1!",
      data: g1Colors, mindRoot: "🎨 Màu Sắc", rootColor: "#C4B5FD", chipClass: "g1-chip",
      hint: "Kéo màu lên bảng phối màu 🎨", dropEmoji: "🎨",
      tip: "Lily thích vẽ tranh nhiều màu! 🌈",
      celebrate: { type: "emoji", pool: [{ emoji: "🌈", msg: "Đẹp quá đi!" }] },
    },
    pets: {
      grade: 2, section: "g2", scene: "drag", btnClass: "grade2",
      title: "Thú Cưng", hud: "🐾 Thú Cưng", icon: "🐹",
      desc: "Chăm sóc thú cưng — từ vựng lớp 2!",
      data: g2Pets, mindRoot: "🐾 Thú Cưng", rootColor: "#F9A8D4", chipClass: "g2-chip",
      hint: "Kéo thú cưng vào nhà nhỏ 🏠", dropEmoji: "🏠",
      tip: "Thú cưng của bạn tên gì? 🐶",
      celebrate: { type: "emoji", pool: [{ emoji: "🥰", msg: "Dễ thương quá!" }] },
    },
    food: {
      grade: 2, section: "g2", scene: "drag", btnClass: "grade2",
      title: "Bữa Ăn Ngon", hud: "🍱 Bữa Ăn", icon: "🍽️",
      desc: "Chọn món ăn & thức uống — lớp 2!",
      data: g2Food, mindRoot: "🍽️ Đồ Ăn", rootColor: "#FDE68A", chipClass: "g2-chip",
      hint: "Kéo món ăn lên bàn ăn 🍽️", dropEmoji: "🍽️",
      tip: "Ăn uống đủ chất nhé! 🥛",
      celebrate: { type: "emoji", pool: [{ emoji: "😋", msg: "Bữa ăn ngon lành!" }] },
    },
    home: {
      grade: 2, section: "g2", scene: "drag", btnClass: "grade2",
      title: "Ngôi Nhà", hud: "🏠 Ngôi Nhà", icon: "🏡",
      desc: "Sắp xếp đồ trong nhà — từ vựng lớp 2!",
      data: g2Home, mindRoot: "🏠 Ngôi Nhà", rootColor: "#93C5FD", chipClass: "g2-chip",
      hint: "Kéo đồ vào phòng trong nhà 🏡", dropEmoji: "🏡",
      tip: "Nhà của Lily ấm cúng lắm! ✨",
      celebrate: { type: "emoji", pool: [{ emoji: "🏡", msg: "Nhà xinh quá!" }] },
    },
    nature: {
      grade: 2, section: "g2", scene: "drag", btnClass: "grade2",
      title: "Công Viên", hud: "🌳 Thiên Nhiên", icon: "🌸",
      desc: "Khám phá thiên nhiên & thời tiết — lớp 2!",
      data: g2Nature, mindRoot: "🌳 Thiên Nhiên", rootColor: "#6EE7B7", chipClass: "g2-chip",
      hint: "Kéo vào khung cảnh thiên nhiên 🌤️", dropEmoji: "🌳",
      tip: "Ra ngoài hít thở không khí trong lành! 🌿",
      celebrate: { type: "emoji", pool: [{ emoji: "☀️", msg: "Trời đẹp quá!" }] },
    },
    vehicles: {
      grade: 2, section: "g2", scene: "drag", btnClass: "grade2",
      title: "GaRa Xe", hud: "🚗 Phương Tiện", icon: "🚂",
      desc: "Chọn xe đúng — vehicles lớp 2!",
      data: g2Vehicles, mindRoot: "🚗 Xe Cộ", rootColor: "#A5B4FC", chipClass: "g2-chip",
      hint: "Kéo phương tiện vào ga-ra 🛣️", dropEmoji: "🅿️",
      tip: "Bạn thích đi xe gì nhất? 🚲",
      celebrate: { type: "emoji", pool: [{ emoji: "🚀", msg: "Xe chạy bon bon!" }] },
    },
  };

  const SECTIONS = [
    { key: "fun", label: "Vui cùng Lily" },
    { key: "g1", label: "Lớp 1 — Chương trình học" },
    { key: "g2", label: "Lớp 2 — Chương trình học" },
  ];

  global.LilyVocab = { MODES, SECTIONS, pickCelebrate(cfg) {
    const c = cfg?.celebrate;
    if (!c?.pool?.length) return null;
    return c.pool[Math.floor(Math.random() * c.pool.length)];
  }};
})(typeof window !== "undefined" ? window : globalThis);
