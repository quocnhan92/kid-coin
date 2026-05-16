(function () {
  const { setActiveSkuNav, updateProfileBar, getGames, getBootstrap } = window.MathBlastV2;

  async function init() {
    setActiveSkuNav('hub');
    try {
      const [games, boot] = await Promise.all([
        getGames(),
        getBootstrap('math_blast', ''),
      ]);
      await updateProfileBar(
        boot.streak?.current != null ? `${boot.streak.current}🔥` : null
      );
      const status = document.getElementById('mb-hub-status');
      if (status) {
        const mb = games.games?.find((g) => g.id === 'math_blast');
        const modeCount = mb?.modes?.length || 0;
        status.textContent = `Đã tải danh mục · ${modeCount} chế độ Math Blast từ máy chủ`;
      }
    } catch (e) {
      console.error(e);
      const status = document.getElementById('mb-hub-status');
      if (status && !window.MathBlastV2.isAuthError(e)) {
        status.textContent = 'Đăng nhập tài khoản bé để đồng bộ tiến độ';
      }
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const run = () => init();
    if (window.GameAuth) GameAuth.ready().then(run);
    else run();
    window.addEventListener('gameAuthRestored', () => init());
  });
})();
