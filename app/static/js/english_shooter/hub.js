(function () {
  const { MODES, getBootstrap, updateProfileBar, toast } = window.EnglishShooter;

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
        if (!unlocked) {
          const tag = cityCard.querySelector('.es-lock-hint');
          if (tag) tag.textContent = 'Hoàn thành 1 chủ đề Thảo nguyên để mở';
        }
      }
      if (bossCard) {
        const unlocked = blocks.boss?.unlocked;
        bossCard.classList.toggle('locked', !unlocked);
        if (!unlocked) {
          const tag = bossCard.querySelector('.es-lock-hint');
          if (tag) tag.textContent = '30 câu đúng trở lên để mở Boss';
        }
      }
      await updateProfileBar(`${en.rank || 'recruit'} · ${en.lifetime_correct || 0} câu`);
      if (status) status.textContent = `${en.themes?.length || 0} chủ đề lớp ${en.last_grade || 1}`;
    } catch (e) {
      if (status) status.textContent = 'Đăng nhập để lưu tiến trình';
      if (e.message !== 'SESSION_AUTH_REQUIRED') toast(String(e.message || e));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
