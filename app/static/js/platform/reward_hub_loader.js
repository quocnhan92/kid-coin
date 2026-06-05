(function () {
  const GRID_SEL = '#reward-game-grid';

  function hubCard(meta) {
    const count = meta?.total_count ?? 4;
    const unlocked = meta?.unlocked_count;
    const progress =
      unlocked != null ? `${unlocked}/${count} game đã mở` : `${count} game giải trí`;
    return `
      <a href="/game/rewards" class="game-card" data-color="amber" data-game-id="reward_playground">
        <div class="card-glow"></div>
        <div class="card-banner" style="background: linear-gradient(135deg, #78350f, #be185d, #7c3aed);">
          <span class="card-emoji">🎁</span>
          <span class="card-badge">PHẦN THƯỞNG</span>
        </div>
        <div class="card-body">
          <div class="card-title">Reward Playground</div>
          <div class="card-desc">Snake, 2048, Flappy, Block Breaker — ${progress}. Nhấn để vào khu giải trí.</div>
          <div class="card-footer">
            <div class="card-meta">
              <span class="meta-item">🎮 Fun Zone</span>
              <span class="meta-item">🪙 Xu chơi</span>
            </div>
            <button type="button" class="play-btn">▶ Vào sân chơi</button>
          </div>
        </div>
      </a>`;
  }

  async function renderRewardSection() {
    const grid = document.querySelector(GRID_SEL);
    if (!grid) return;

    let meta = null;
    try {
      const res = await fetch('/api/v1/play/rewards', { credentials: 'same-origin' });
      if (res.ok) meta = await res.json();
    } catch (_) {
      /* offline — card tĩnh */
    }
    grid.innerHTML = hubCard(meta);
  }

  document.addEventListener('DOMContentLoaded', renderRewardSection);
})();
