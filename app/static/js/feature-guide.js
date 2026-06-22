(function (global) {
  'use strict';

  const GUIDES = {
    learning_home: {
      title: '🌟 Học theo lớp',
      subtitle: 'Bé tự chọn lớp — không cần khai báo tuổi',
      steps: [
        'Chọn <strong>Lớp 1 → 5</strong> tùy bài đang học ở trường.',
        'Xem <strong>Hôm nay: … phút</strong> để biết đã học bao nhiêu trong ngày.',
        'Bấm <strong>📅 Lịch học hôm nay</strong> để xem gợi ý tiết theo tuần.',
        'Sau khi chọn lớp → xem <strong>🎓 Giáo viên online</strong> và các môn bên dưới.',
        'Mỗi ngày học <strong>15–60 phút</strong> là vừa — nghỉ giữa các bài nhé!',
      ],
      tip: 'Cùng một máy, bé có thể đăng nhập tài khoản riêng; bố mẹ xem tiến độ ở tab Học tập.',
    },
    learning_schedule: {
      title: '📅 Lịch học hôm nay',
      subtitle: 'Gợi ý tiết theo tuần — không bắt buộc',
      steps: [
        'Xem danh sách <strong>bài gợi ý</strong> cho hôm nay.',
        'Chạm bài để vào học ngay — hoặc chọn môn khác từ menu lớp.',
        'Đã xong bài hiện <strong>✅</strong>; chưa xong hiện số thứ tự.',
        'Bấm ← để quay chọn lớp khác.',
      ],
    },
    learning_teacher: {
      title: '🎓 Giáo viên online',
      subtitle: 'Tiết 30 phút — khác bài kiểm tra nhanh',
      steps: [
        'Panel <strong>🎓 Giáo viên online</strong> — tiết 30 phút, máy đọc từng bước.',
        'Vuốt list để xem hết tiết — hiện ~5 dòng, kéo thêm bài phía dưới.',
        'Bài <strong>mờ</strong> = chưa học · <strong>đậm + sao</strong> = đã xong · viền tím = đang học.',
        'Chạm tiết để vào player 👀🎯📝👨‍👩‍👦🎁.',
        'Dưới panel là <strong>môn học</strong> — bài ngắn 5–10 phút (quiz/đọc).',
      ],
      tip: 'Tuần 1 Lớp 1: Âm a, Âm b, Số 1-2-3, Lễ phép.',
    },
    learning_subjects: {
      title: '📚 Chọn môn học',
      subtitle: 'Toán, Tiếng Việt, Khoa học…',
      steps: [
        'Phía trên: <strong>🎓 Giáo viên online</strong> — vuốt chọn tiết 30 phút.',
        'Phía dưới: chạm <strong>thẻ môn</strong> cho bài quiz/đọc ngắn.',
        'Thanh % cho biết đã hoàn thành bao nhiêu <strong>chủ đề</strong>.',
        'Bấm ← để đổi lớp khác.',
      ],
    },
    learning_map: {
      title: '🗺️ Bản đồ chủ đề',
      subtitle: 'Mỗi ngọn núi = một chủ đề SGK',
      steps: [
        'Chạm <strong>ngọn núi</strong> để vào danh sách bài.',
        'Màu xanh = đã xong · cam = đang học · xám = chưa mở.',
        'Sao ⭐ thể hiện kết quả bài học lần đầu.',
        'Đọc <strong>gợi ý</strong> phía trên bản đồ trước khi bắt đầu.',
      ],
    },
    learning_lesson: {
      title: '✏️ Làm bài học',
      subtitle: 'Quiz, đọc hiểu hoặc Giáo viên online',
      steps: [
        'Chọn bài → làm theo từng bước trên màn hình.',
        'Quiz: phải <strong>đúng hết</strong> mới hoàn thành — sai sẽ được nhắc làm lại.',
        'Bài đã xong hiện <strong>🔁 Ôn lại</strong>: học lại thoải mái, <strong>điểm lần đầu giữ nguyên</strong>.',
        'Bài có 👨‍👩‍👦: nhờ bố mẹ bấm <strong>Xác nhận</strong> trên tab Học tập.',
        'Bấm 🔊 để bật/tắt giọng đọc.',
      ],
      tip: 'Nếu kẹt ở một câu, bấm nút quay lại và thử lại — không cần nộp khi chưa chắc.',
    },
    kid_quests: {
      title: '📅 Việc nhà hôm nay',
      subtitle: 'Kiếm Coin nhà khi hoàn thành việc',
      steps: [
        'Xem danh sách <strong>việc hôm nay</strong> bố mẹ giao.',
        'Làm xong → bấm <strong>Nộp việc</strong> (chụp ảnh nếu cần).',
        'Chờ bố mẹ <strong>duyệt</strong> ở tab Chờ duyệt.',
        'Được duyệt → nhận <strong>💰 Coin nhà</strong> vào ví.',
        'Kéo ngang <strong>Gợi ý cho bé</strong> để thêm việc mới.',
      ],
      tip: 'Coin nhà dùng đổi quà trong tab Cửa hàng — khác với Xu chơi game.',
    },
    kid_shop: {
      title: '🎁 Cửa hàng quà',
      subtitle: 'Đổi Coin nhà lấy phần thưởng',
      steps: [
        'Xem số <strong>💰 Coin nhà</strong> ở đầu màn hình.',
        'Chọn quà đủ điểm → bấm <strong>Đổi quà</strong>.',
        'Bố mẹ sẽ duyệt yêu cầu đổi quà.',
        'Xem <strong>Gợi ý quà tặng</strong> để biết quà phổ biến.',
      ],
    },
    kid_avatar: {
      title: '🎭 Avatar & trang trí',
      subtitle: 'Tùy chỉnh hình đại diện',
      steps: [
        'Mua item bằng <strong>Coin nhà</strong> hoặc nhận từ sự kiện.',
        'Chọn trang phục / khung ảnh → <strong>Đeo</strong> để áp dụng.',
        'Avatar hiện ở góc màn hình và bảng xếp hạng CLB.',
      ],
    },
      title: '👥 Câu lạc bộ',
      subtitle: 'Tham gia nhóm, làm thử thách cùng bạn',
      steps: [
        'Xem CLB gia đình đã tham gia.',
        'Làm <strong>thử thách</strong> trong CLB để ghi điểm.',
        'Bảng xếp hạng chỉ mang tính vui — không so sánh gắt.',
      ],
    },
    kid_finance: {
      title: '💳 Ví & tiết kiệm',
      subtitle: 'Học quản lý tiền (nếu bố mẹ bật)',
      steps: [
        'Xem số dư và lịch sử giao dịch.',
        'Gửi tiết kiệm hoặc rút theo quy tắc gia đình.',
        'Mọi thao tác lớn cần bố mẹ xác nhận.',
      ],
    },
    kid_thinking: {
      title: '🧠 Tư duy & Teen',
      subtitle: 'Bài tập phản biện, mood check',
      steps: [
        'Làm bài <strong>tư duy</strong> ngắn theo gợi ý.',
        'Ghi <strong>cảm xúc</strong> nếu có — bố mẹ có thể xem.',
        'Không có đáp án sai tuyệt đối — quan trọng là suy nghĩ.',
      ],
    },
    parent_overview: {
      title: '📊 Tổng quan gia đình',
      subtitle: 'Nhìn nhanh toàn bộ hoạt động',
      steps: [
        'Xem <strong>Coin, việc, học tập</strong> của từng bé.',
        'Thẻ đỏ <strong>Chờ duyệt</strong> → vào tab Pending xử lý.',
        'Bấm từng bé để xem chi tiết hơn.',
      ],
    },
    parent_kids: {
      title: '👶 Quản lý các con',
      subtitle: 'Tài khoản, mật khẩu, hồ sơ',
      steps: [
        'Thêm bé mới hoặc sửa <strong>tên, avatar</strong>.',
        'Cấp <strong>mã PIN</strong> để bé đăng nhập trên thiết bị riêng.',
        'Không cần nhập tuổi — bé tự chọn lớp khi học.',
      ],
    },
      title: '📚 Theo dõi học tập',
      subtitle: 'Tiến độ tất cả lớp 1–5',
      steps: [
        'Xem <strong>phút học hôm nay / tuần</strong> của từng bé.',
        'Danh sách môn <strong>L1·Toán, L3·Tiếng Việt…</strong> — bé tự chọn lớp, không theo tuổi.',
        'Thanh % = tiến độ chủ đề đã hoàn thành.',
        'Khung vàng <strong>Chờ xác nhận</strong>: bấm <strong>Xác nhận 👍</strong> khi bé làm bài thực hành.',
        'Link <strong>Bé vào học</strong> mở trang /learning.',
      ],
    },
    parent_clubs: {
      title: '🏆 Câu lạc bộ gia đình',
      subtitle: 'Thử thách nhóm, bảng xếp hạng',
      steps: [
        'Tạo hoặc tham gia <strong>CLB</strong> với bạn bè / họ hàng.',
        'Giao <strong>thử thách</strong> tuần cho các bé trong CLB.',
        'Theo dõi điểm — khuyến khích chơi fair, không ép thi đua.',
      ],
    },
      title: '✅ Quản lý việc nhà',
      subtitle: 'Tạo, giao, duyệt nhiệm vụ',
      steps: [
        'Tạo việc mới hoặc chọn từ <strong>thư viện việc</strong>.',
        'Gán cho bé, đặt <strong>điểm thưởng Coin</strong>.',
        'Chọn loại duyệt: tự động / ảnh / bố mẹ kiểm tra.',
      ],
    },
    parent_rewards: {
      title: '🎁 Quản lý quà',
      subtitle: 'Thiết lập phần thưởng đổi Coin',
      steps: [
        'Thêm quà với <strong>giá Coin</strong> phù hợp.',
        'Duyệt yêu cầu đổi quà của bé.',
        'Tắt quà không còn dùng thay vì xóa — giữ lịch sử.',
      ],
    },
    parent_pending: {
      title: '⏳ Chờ duyệt',
      subtitle: 'Việc nhà, đổi quà, bài học',
      steps: [
        'Xem tất cả yêu cầu <strong>chưa xử lý</strong>.',
        'Việc nhà: xem ảnh bằng chứng → <strong>Duyệt / Từ chối</strong>.',
        'Học tập: xác nhận bé đã làm bài thực hành với bố mẹ.',
      ],
    },
    game_hub: {
      title: '🕹️ Kho game Chơi mà học',
      subtitle: 'Học tập + giải trí sau khi hoàn thành việc',
      steps: [
        '<strong>📚 Learning Games</strong>: game gắn bài học (toán, tiếng Anh…).',
        '<strong>🎁 Reward Playground</strong>: chơi bằng <strong>Xu sân chơi</strong> — kiếm từ việc nhà đã duyệt.',
        'Đăng nhập một lần dùng chung KidCoin + game.',
        'Mỗi game có mục <strong>Hướng dẫn chơi</strong> ngay trong trang.',
      ],
      tip: 'Xu chơi ≠ Coin nhà. Xu chỉ dùng trong sân chơi phần thưởng.',
    },
    game_reward: {
      title: '🎁 Sân chơi phần thưởng',
      subtitle: 'Chơi sau khi học / làm việc',
      steps: [
        'Vào từ Kid Dashboard khi có <strong>🎮 Xu chơi</strong>.',
        'Mỗi lượt chơi trừ Xu theo quy định.',
        'Hết Xu → quay lại làm việc nhà để kiếm thêm.',
      ],
    },
  };

  let overlayEl = null;

  function ensureDom() {
    if (overlayEl) return;
    overlayEl = document.createElement('div');
    overlayEl.className = 'fg-overlay';
    overlayEl.id = 'fg-overlay';
    overlayEl.innerHTML = `
      <div class="fg-sheet" role="dialog" aria-modal="true">
        <div class="fg-sheet-header">
          <div>
            <h2 id="fg-title"></h2>
            <p id="fg-subtitle"></p>
          </div>
          <button type="button" class="fg-close" id="fg-close" aria-label="Đóng">×</button>
        </div>
        <div class="fg-sheet-body">
          <ol class="fg-steps" id="fg-steps"></ol>
          <div class="fg-tip fg-hidden" id="fg-tip"></div>
        </div>
      </div>`;
    document.body.appendChild(overlayEl);
    overlayEl.querySelector('#fg-close').onclick = close;
    overlayEl.addEventListener('click', e => { if (e.target === overlayEl) close(); });
  }

  function open(guideId) {
    const g = GUIDES[guideId];
    if (!g) return;
    ensureDom();
    document.getElementById('fg-title').textContent = g.title;
    document.getElementById('fg-subtitle').textContent = g.subtitle || '';
    const stepsEl = document.getElementById('fg-steps');
    stepsEl.innerHTML = g.steps.map((s, i) =>
      `<li><span class="fg-step-num">${i + 1}</span><span>${s}</span></li>`
    ).join('');
    const tipEl = document.getElementById('fg-tip');
    if (g.tip) {
      tipEl.textContent = '💡 ' + g.tip;
      tipEl.classList.remove('fg-hidden');
    } else {
      tipEl.classList.add('fg-hidden');
    }
    overlayEl.classList.add('show');
  }

  function close() {
    if (overlayEl) overlayEl.classList.remove('show');
  }

  function btn(guideId, label) {
    return `<button type="button" class="fg-help-btn" onclick="FeatureGuide.open('${guideId}')" title="${label || 'Hướng dẫn'}">❓</button>`;
  }

  function mountFab(guideId) {
    if (document.getElementById('fg-fab')) return;
    const b = document.createElement('button');
    b.type = 'button';
    b.id = 'fg-fab';
    b.className = 'fg-fab';
    b.title = 'Hướng dẫn sử dụng';
    b.textContent = '❓';
    b.onclick = () => open(guideId);
    document.body.appendChild(b);
  }

  function setFabGuide(guideId) {
    const fab = document.getElementById('fg-fab');
    if (fab) fab.onclick = () => open(guideId);
  }

  global.FeatureGuide = { open, close, btn, mountFab, setFabGuide, GUIDES };
})(window);
