/**
 * Gà Toán — album sticker (luyện tập + cuộc đua).
 */
(function () {
  const GROUP_LABELS = {
    practice: 'Luyện tập nhẹ',
    sprint: 'Cuộc đua 60 giây',
    both: 'Cả hai chế độ',
  };

  function metaList(bootstrap) {
    return bootstrap?.flappy?.sticker_meta || [];
  }

  function unlockedSet(bootstrap) {
    return new Set(bootstrap?.flappy?.stickers_unlocked || []);
  }

  function stickerById(bootstrap, id) {
    return metaList(bootstrap).find((s) => s.id === id);
  }

  function countLabel(bootstrap) {
    const total = bootstrap?.flappy?.sticker_total || metaList(bootstrap).length || 0;
    const n = (bootstrap?.flappy?.stickers_unlocked || []).length;
    return `${n}/${total}`;
  }

  function renderAlbum(bootstrap) {
    const grid = document.getElementById('flappy-sticker-grid');
    const countEl = document.getElementById('flappy-sticker-count');
    if (!grid) return;
    const unlocked = unlockedSet(bootstrap);
    const items = metaList(bootstrap);
    if (countEl) countEl.textContent = countLabel(bootstrap);

    const groups = ['practice', 'sprint', 'both'];
    grid.innerHTML = groups
      .map((group) => {
        const rows = items.filter((s) => s.group === group);
        if (!rows.length) return '';
        const cells = rows
          .map((s) => {
            const has = unlocked.has(s.id);
            return `
          <div class="mb-sticker-cell ${has ? 'is-unlocked' : 'is-locked'}" data-id="${s.id}" title="${s.hint}">
            ${has ? '' : '<span class="mb-sticker-lock" aria-hidden="true">🔒</span>'}
            <span class="mb-sticker-emoji" aria-hidden="true">${s.emoji}</span>
            <span class="mb-sticker-name">${s.name}</span>
            <span class="mb-sticker-hint">${has ? 'Đã có!' : s.hint}</span>
          </div>`;
          })
          .join('');
        return `
        <section class="mb-sticker-group">
          <h3 class="mb-sticker-group-title">${GROUP_LABELS[group] || group}</h3>
          <div class="mb-sticker-group-grid">${cells}</div>
        </section>`;
      })
      .join('');
  }

  function openAlbum(bootstrap) {
    const modal = document.getElementById('flappy-sticker-modal');
    if (!modal) return;
    renderAlbum(bootstrap);
    modal.hidden = false;
    document.body.classList.add('mb-sticker-modal-open');
  }

  function closeAlbum() {
    const modal = document.getElementById('flappy-sticker-modal');
    if (!modal) return;
    modal.hidden = true;
    document.body.classList.remove('mb-sticker-modal-open');
  }

  function bindAlbumUi(getBootstrap) {
    const openBtn = document.getElementById('flappy-sticker-album');
    const modal = document.getElementById('flappy-sticker-modal');
    if (openBtn && !openBtn.dataset.bound) {
      openBtn.dataset.bound = '1';
      openBtn.addEventListener('click', () => {
        const boot = typeof getBootstrap === 'function' ? getBootstrap() : null;
        openAlbum(boot);
      });
    }
    if (modal && !modal.dataset.bound) {
      modal.dataset.bound = '1';
      modal.querySelectorAll('[data-close-sticker]').forEach((el) => {
        el.addEventListener('click', closeAlbum);
      });
    }
    updateAlbumBadge(getBootstrap?.());
  }

  function updateAlbumBadge(bootstrap) {
    const badge = document.getElementById('flappy-sticker-badge');
    if (!badge || !bootstrap?.flappy) return;
    badge.textContent = countLabel(bootstrap);
  }

  function celebrateUnlocks(bootstrap, ids, toastFn) {
    if (!ids?.length || !toastFn) return;
    ids.forEach((id, i) => {
      const s = stickerById(bootstrap, id);
      const label = s ? `${s.emoji} Sticker mới: ${s.name}` : `Sticker mới: ${id}`;
      setTimeout(() => toastFn(label), i * 900);
    });
    updateAlbumBadge(bootstrap);
    const modal = document.getElementById('flappy-sticker-modal');
    if (modal && !modal.hidden) renderAlbum(bootstrap);
  }

  window.FlappyStickers = {
    metaList,
    unlockedSet,
    stickerById,
    countLabel,
    renderAlbum,
    openAlbum,
    closeAlbum,
    bindAlbumUi,
    updateAlbumBadge,
    celebrateUnlocks,
  };
})();
