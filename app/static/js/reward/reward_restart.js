(function () {
  if (window.RewardShell?.showGameOver) return;

  let onAgain = null;

  function ensureModal() {
    if (document.getElementById('rg-gameover')) return;
    const wrap = document.createElement('div');
    wrap.innerHTML = `
      <div id="rg-gameover" class="rg-modal" hidden>
        <div class="rg-modal-card">
          <p id="rg-gameover-msg"></p>
          <div class="rg-modal-actions">
            <button type="button" id="rg-gameover-again" class="rg-btn rg-btn-primary">Play again / Chơi lại</button>
            <button type="button" id="rg-gameover-close" class="rg-btn">Close / Đóng</button>
          </div>
        </div>
      </div>
      <button type="button" id="rg-restart" class="rg-restart-fab" title="Play again / Chơi lại">↻</button>`;
    document.body.appendChild(wrap);
    document.getElementById('rg-restart')?.addEventListener('click', () => {
      if (typeof window.RewardGame?.restart === 'function') window.RewardGame.restart();
      else location.reload();
    });
    document.getElementById('rg-gameover-again')?.addEventListener('click', () => {
      if (onAgain) onAgain();
      else if (typeof window.RewardGame?.restart === 'function') window.RewardGame.restart();
      else location.reload();
      hideGameOver();
    });
    document.getElementById('rg-gameover-close')?.addEventListener('click', hideGameOver);
  }

  function hideGameOver() {
    const modal = document.getElementById('rg-gameover');
    if (modal) modal.hidden = true;
    onAgain = null;
  }

  function showGameOver(message, againFn) {
    ensureModal();
    const msg = document.getElementById('rg-gameover-msg');
    if (msg) msg.textContent = message || 'Game over';
    onAgain = typeof againFn === 'function' ? againFn : null;
    document.getElementById('rg-gameover').hidden = false;
  }

  window.RewardShell = {
    showGameOver,
    hideGameOver,
    restart() {
      if (typeof window.RewardGame?.restart === 'function') window.RewardGame.restart();
      else location.reload();
    },
    setHud() {},
  };

  ensureModal();
})();
