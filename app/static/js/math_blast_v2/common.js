/**
 * Math Blast v2 — shared UI helpers (prototype, mock data)
 */
(function () {
  const MOCK_PROFILE = {
    name: 'Bé Minh',
    coins: 128,
    streak: 3,
    currentSku: null,
  };

  const CANDY_WORLDS = [
    { id: 'w1', name: 'Thế giới 1', chapter: 'Cộng trừ cơ bản', levels: 18 },
    { id: 'w2', name: 'Thế giới 2', chapter: 'Nhân chia', levels: 18 },
    { id: 'w3', name: 'Thế giới 3', chapter: 'Hỗn hợp', levels: 18 },
  ];

  function toast(msg, duration = 2200) {
    let el = document.getElementById('mb-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'mb-toast';
      el.className = 'mb-toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), duration);
  }

  function setActiveSkuNav(sku) {
    document.querySelectorAll('.mb-sku-tab').forEach((tab) => {
      tab.classList.toggle('active', tab.dataset.sku === sku);
    });
  }

  function buildCandyLevels(worldIndex, count = 12) {
    const nodes = [];
    const base = worldIndex * 18;
    for (let i = 0; i < count; i++) {
      const n = base + i + 1;
      const id = `L${String(n).padStart(3, '0')}`;
      const locked = n > base + 4;
      const stars = locked ? 0 : Math.floor(Math.random() * 4);
      const isBoss = (i + 1) % 6 === 0;
      nodes.push({
        id,
        title: isBoss ? `Boss ${id}` : `Màn ${n}`,
        sub: isBoss ? 'Thử thách cuối chương' : '3 sao để mở màn tiếp',
        locked,
        current: n === base + 3,
        stars,
        boss: isBoss,
        icon: isBoss ? '👑' : locked ? '🔒' : '⭐',
      });
    }
    return nodes;
  }

  window.MathBlastV2 = {
    MOCK_PROFILE,
    CANDY_WORLDS,
    toast,
    setActiveSkuNav,
    buildCandyLevels,
  };
})();
