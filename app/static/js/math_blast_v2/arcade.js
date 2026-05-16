(function () {
  const { toast, setActiveSkuNav } = window.MathBlastV2;

  const LEVELS = [
    { id: 'kiddy', name: 'Kiddy', meta: 'Cộng trừ 1–10', color: '#10b981' },
    { id: 'starter', name: 'Starter', meta: 'Cộng trừ 1–20', color: '#3b82f6' },
    { id: 'explorer', name: 'Explorer', meta: 'Nhân chia cơ bản', color: '#f59e0b' },
    { id: 'master', name: 'Master', meta: 'Hỗn hợp', color: '#ec4899' },
    { id: 'genius', name: 'Genius', meta: 'Thử thách', color: '#ef4444' },
  ];

  let selected = 'starter';
  let mode = 'free';

  function renderLevels() {
    const grid = document.getElementById('arcade-level-grid');
    if (!grid) return;
    grid.innerHTML = LEVELS.map(
      (lv) => `
      <button type="button" class="mb-arcade-level ${lv.id === selected ? 'selected' : ''}"
        data-id="${lv.id}" style="border-color:${lv.id === selected ? lv.color : ''}">
        <div class="lvl-name">${lv.name}</div>
        <div class="lvl-meta">${lv.meta}</div>
      </button>`
    ).join('');
    grid.querySelectorAll('.mb-arcade-level').forEach((btn) => {
      btn.addEventListener('click', () => {
        selected = btn.dataset.id;
        renderLevels();
        const panel = document.getElementById('arcade-play-panel');
        const title = document.getElementById('arcade-selected-title');
        const lv = LEVELS.find((l) => l.id === selected);
        if (title && lv) title.textContent = `${lv.name} — ${lv.meta}`;
        if (panel) panel.classList.remove('hidden');
      });
    });
  }

  function initModeTabs() {
    document.querySelectorAll('[data-arcade-mode]').forEach((tab) => {
      tab.addEventListener('click', () => {
        mode = tab.dataset.arcadeMode;
        document.querySelectorAll('[data-arcade-mode]').forEach((t) => {
          t.classList.toggle('active', t.dataset.arcadeMode === mode);
        });
        const classPanel = document.getElementById('arcade-class-panel');
        if (classPanel) classPanel.classList.toggle('hidden', mode !== 'class');
        toast(mode === 'class' ? 'Chế độ lớp GV (mock)' : 'Arcade free — chọn level');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setActiveSkuNav('arcade');
    renderLevels();
    initModeTabs();
    const playBtn = document.getElementById('arcade-play-btn');
    if (playBtn) {
      playBtn.addEventListener('click', () => {
        toast(`Bắt đầu ${selected} (${mode}) — prototype`);
      });
    }
  });
})();
