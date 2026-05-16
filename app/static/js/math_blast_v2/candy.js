(function () {
  const { CANDY_WORLDS, buildCandyLevels, toast, setActiveSkuNav } = window.MathBlastV2;
  let worldIndex = 0;

  function renderMap() {
    const path = document.getElementById('candy-map-path');
    if (!path) return;
    const levels = buildCandyLevels(worldIndex);
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
      btn.addEventListener('click', () => {
        toast(`Mở màn ${btn.dataset.id} — prototype UI`);
      });
    });
  }

  function initWorldTabs() {
    document.querySelectorAll('.mb-world-tab').forEach((tab, i) => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.mb-world-tab').forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        worldIndex = i;
        const w = CANDY_WORLDS[i];
        const sub = document.getElementById('candy-chapter-sub');
        if (sub) sub.textContent = `${w.chapter} · ${w.levels} màn`;
        renderMap();
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setActiveSkuNav('candy');
    initWorldTabs();
    renderMap();
  });
})();
