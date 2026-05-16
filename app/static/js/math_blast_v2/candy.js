(function () {
  const {
    MODES,
    toast,
    setActiveSkuNav,
    updateProfileBar,
    getLevels,
    getBootstrap,
    mergeCandyLevels,
    sessionsBatch,
    uuid,
  } = window.MathBlastV2;

  let catalogLevels = [];
  let bootstrap = null;

  function renderMap() {
    const path = document.getElementById('candy-map-path');
    if (!path || !bootstrap) return;
    const levels = mergeCandyLevels(catalogLevels, bootstrap);
    path.innerHTML = levels
      .map(
        (lv) => `
      <button type="button" class="mb-level-node ${lv.locked ? 'locked' : ''} ${lv.current ? 'current' : ''} ${lv.boss ? 'boss' : ''}"
        data-id="${lv.id}" ${lv.locked ? 'disabled' : ''}>
        <span class="node-icon">${lv.icon}</span>
        <span class="node-info">
          <div class="node-title">${lv.title}</div>
          <div class="node-sub">${lv.sub}</div>
        </span>
        <span class="mb-stars">${'★'.repeat(lv.stars)}${'☆'.repeat(3 - lv.stars)}</span>
      </button>`
      )
      .join('');

    path.querySelectorAll('.mb-level-node:not(.locked)').forEach((btn) => {
      btn.addEventListener('click', () => openLevel(btn.dataset.id));
    });
  }

  async function openLevel(levelId) {
    const sid = uuid();
    const now = new Date().toISOString();
    try {
      toast('Đang mở màn…');
      await sessionsBatch(
        [
          {
            op: 'start',
            session_id: sid,
            game_id: 'math_blast',
            game_mode_id: MODES.candy,
            started_at: now,
            content_pack_id: bootstrap.profile.active_content_pack_id,
          },
          {
            op: 'end',
            session_id: sid,
            ended_at: now,
            summary: {
              duration_s: 90,
              level_id: levelId,
              stars: 2,
              accuracy: 0.85,
              questions_count: 10,
              correct_count: 8,
              summary_json: { ui: 'candy_map_tap' },
            },
          },
        ],
        `candy-open-${sid}`
      );
      bootstrap = await getBootstrap(MODES.candy);
      renderMap();
      const sub = document.getElementById('candy-api-status');
      if (sub) sub.textContent = `Đã lưu phiên màn ${levelId} · đồng bộ máy chủ`;
      toast(`Màn ${levelId} — đã ghi lên máy chủ`);
    } catch (e) {
      console.error(e);
      if (!window.MathBlastV2.isAuthError(e)) {
        toast(e.message || 'Lỗi lưu phiên');
      }
    }
  }

  async function init() {
    setActiveSkuNav('candy');
    try {
      const [levelsRes, boot] = await Promise.all([
        getLevels(MODES.candy),
        getBootstrap(MODES.candy),
      ]);
      catalogLevels = levelsRes.levels || [];
      bootstrap = boot;
      const streak = boot.streak?.current;
      await updateProfileBar(streak != null ? `${streak}🔥 ngày liên tiếp` : null);
      const sub = document.getElementById('candy-chapter-sub');
      if (sub) {
        const cleared = (boot.level_progress || []).filter((p) => p.stars >= 1).length;
        sub.textContent = `Thế giới 1 · ${catalogLevels.length} màn · đã qua ${cleared}`;
      }
      renderMap();
    } catch (e) {
      console.error(e);
      const path = document.getElementById('candy-map-path');
      if (path) path.innerHTML = '<p style="text-align:center;color:var(--mb-muted)">Không tải được dữ liệu. Đăng nhập tài khoản bé rồi thử lại.</p>';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const run = () => init();
    if (window.GameAuth) GameAuth.ready().then(run);
    else run();
    window.addEventListener('gameAuthRestored', () => init());
  });
})();
