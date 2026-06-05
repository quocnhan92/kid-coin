(function () {
  let onAgain = null;

  function el(id) {
    return document.getElementById(id);
  }

  function hideGameOver() {
    const modal = el('rg-gameover');
    if (modal) modal.hidden = true;
    onAgain = null;
  }

  function restart() {
    hideGameOver();
    if (typeof window.RewardGame?.restart === 'function') {
      window.RewardGame.restart();
      return;
    }
    location.reload();
  }

  function showGameOver(message, againFn) {
    const modal = el('rg-gameover');
    const msg = el('rg-gameover-msg');
    if (!modal || !msg) return;
    msg.textContent = message || 'Game over';
    onAgain = typeof againFn === 'function' ? againFn : null;
    modal.hidden = false;
  }

  function bindUi() {
    el('rg-restart')?.addEventListener('click', restart);
    el('rg-gameover-again')?.addEventListener('click', () => {
      if (onAgain) onAgain();
      else restart();
    });
    el('rg-gameover-close')?.addEventListener('click', hideGameOver);
  }

  function pauseOnHidden(cb) {
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && typeof cb === 'function') cb();
    });
  }

  window.RewardShell = {
    setHud(primary, secondary) {
      const a = el('rg-hud-primary');
      const b = el('rg-hud-secondary');
      if (a) a.textContent = primary || '';
      if (b) b.textContent = secondary || '';
    },
    showGameOver,
    hideGameOver,
    restart,
    pauseOnHidden,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindUi);
  } else {
    bindUi();
  }
})();
