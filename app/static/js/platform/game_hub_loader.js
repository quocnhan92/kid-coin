(function () {
  const COLORS = ['purple', 'cyan', 'pink', 'amber', 'green', 'red'];
  const LEARNING_SEL = '#learning-game-grid';

  function cardHtml(game, idx) {
    const color = COLORS[idx % COLORS.length];
    const url = game.launch_url || '#';
    const icon = game.icon || '🎮';
    const subject = game.subject ? game.subject.toUpperCase() : 'HỌC TẬP';
    return `
      <a href="${url}" class="game-card" data-color="${color}" data-game-id="${game.id}">
        <div class="card-glow"></div>
        <div class="card-banner" style="background: linear-gradient(135deg, #1e1b4b, #312e81);">
          <span class="card-emoji">${icon}</span>
          <span class="card-badge">${subject}</span>
        </div>
        <div class="card-body">
          <div class="card-title">${game.display_name}</div>
          <div class="card-desc">${game.tagline || 'Chơi mà học — học mà chơi'}</div>
          <div class="card-footer">
            <div class="card-meta">
              <span class="meta-item">Lớp ${game.grade_min}–${game.grade_max}</span>
            </div>
            <button type="button" class="play-btn">▶ Chơi ngay</button>
          </div>
        </div>
      </a>`;
  }

  async function renderLearningGames() {
    const grid = document.querySelector(LEARNING_SEL);
    if (!grid || !window.KidCoinPlatform) return;

    try {
      await KidCoinPlatform.fetchFeatures();
      const games = await KidCoinPlatform.fetchPublicGames('learning');
      if (!games.length) return;
      grid.innerHTML = games
        .filter((g) => g.launch_url)
        .map((g, i) => cardHtml(g, i))
        .join('');
    } catch (_) {
      /* API fail — empty grid */
    }
  }

  document.addEventListener('DOMContentLoaded', renderLearningGames);
})();
