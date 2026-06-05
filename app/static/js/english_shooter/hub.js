(function () {
  const { MODES, getBootstrap, updateProfileBar, toast } = window.EnglishShooter;

  const RANK_LABELS = {
    recruit: 'Recruit (Tân binh)',
    soldier: 'Soldier (Chiến sĩ)',
    commander: 'Commander (Chỉ huy)',
    global_commander: 'Global Commander',
  };

  async function init() {
    const status = document.getElementById('es-hub-status');
    const goldEl = document.getElementById('es-hub-gold');
    try {
      const boot = await getBootstrap(MODES.prairie);
      const en = boot.english || {};
      if (goldEl) goldEl.textContent = `🪙 ${en.gold || 0}`;
      const blocks = en.blocks || {};
      const cityCard = document.getElementById('es-mode-city');
      const bossCard = document.getElementById('es-mode-boss');
      if (cityCard) {
        const unlocked = blocks.city?.unlocked;
        cityCard.classList.toggle('locked', !unlocked);
        const tag = cityCard.querySelector('.es-lock-hint');
        if (tag) {
          tag.textContent = unlocked ? 'Open' : 'Finish 1 Prairie theme (Hoàn thành 1 chủ đề Thảo nguyên)';
        }
      }
      if (bossCard) {
        const unlocked = blocks.boss?.unlocked;
        bossCard.classList.toggle('locked', !unlocked);
        const tag = bossCard.querySelector('.es-lock-hint');
        if (tag) {
          tag.textContent = unlocked ? 'Open' : '30+ correct answers (30 câu đúng trở lên)';
        }
      }
      await updateProfileBar(`${RANK_LABELS[en.rank] || en.rank || 'Recruit'} · ${en.lifetime_correct || 0} correct`);
      if (status) status.textContent = `${en.themes?.length || 0} themes · Grade ${en.last_grade || 1}`;
    } catch (e) {
      if (status) status.textContent = 'Sign in to save progress (Đăng nhập để lưu tiến trình)';
      if (e.message !== 'SESSION_AUTH_REQUIRED') toast(String(e.message || e));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
