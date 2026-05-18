(function () {
  const {
    MODES,
    toast,
    setActiveSkuNav,
    updateProfileBar,
    getBootstrap,
    sessionsBatch,
    uuid,
  } = window.MathBlastV2;

  const LEVELS = [
    { id: 'kiddy', name: 'Bé nhỏ', meta: 'Cộng trừ 1–10', color: '#10b981' },
    { id: 'starter', name: 'Khởi đầu', meta: 'Cộng trừ 1–20', color: '#3b82f6' },
    { id: 'explorer', name: 'Khám phá', meta: 'Nhân chia cơ bản', color: '#f59e0b' },
    { id: 'master', name: 'Cao thủ', meta: 'Hỗn hợp', color: '#ec4899' },
    { id: 'genius', name: 'Thiên tài', meta: 'Thử thách', color: '#ef4444' },
  ];

  let selected = 'starter';
  let mode = 'free';
  let bootstrap = null;
  let gameModeId = MODES.arcade;

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
        gameModeId = mode === 'class' ? MODES.arcadeClass : MODES.arcade;
        document.querySelectorAll('[data-arcade-mode]').forEach((t) => {
          t.classList.toggle('active', t.dataset.arcadeMode === mode);
        });
        const classPanel = document.getElementById('arcade-class-panel');
        if (classPanel) classPanel.classList.toggle('hidden', mode !== 'class');
        loadBootstrap();
      });
    });
  }

  async function loadBootstrap() {
    try {
      bootstrap = await getBootstrap(gameModeId);
      const hs = bootstrap.game_stats?.high_score ?? 0;
      await updateProfileBar(`Điểm cao ${hs}`);
    } catch (e) {
      console.error(e);
    }
  }

  async function playSelected() {
    const sid = uuid();
    const now = new Date().toISOString();
    const lv = LEVELS.find((l) => l.id === selected);
    try {
      await sessionsBatch(
        [
          {
            op: 'start',
            session_id: sid,
            game_id: 'math_blast',
            game_mode_id: gameModeId,
            started_at: now,
          },
          {
            op: 'end',
            session_id: sid,
            ended_at: now,
            summary: {
              duration_s: 1,
              score: 0,
              questions_count: 0,
              correct_count: 0,
              summary_json: { preset: selected, ui: 'arcade_launch' },
            },
          },
        ],
        `arcade-${sid}`
      );
      toast(`Mở ${lv?.name || selected} — chuyển sang game V1`);
      window.location.href = `/game/math-blast?level=${encodeURIComponent(selected)}`;
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e)) {
        toast(e.message || 'Lỗi kết nối');
        window.location.href = '/game/math-blast';
      }
    }
  }

  async function init() {
    setActiveSkuNav('arcade');
    renderLevels();
    initModeTabs();
    await loadBootstrap();
    const playBtn = document.getElementById('arcade-play-btn');
    if (playBtn) playBtn.addEventListener('click', playSelected);
  }

  document.addEventListener('DOMContentLoaded', () => {
    const run = () => init();
    if (window.GameAuth) GameAuth.ready().then(run);
    else run();
    window.addEventListener('gameAuthRestored', () => init());
  });
})();
