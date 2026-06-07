(function () {
  const MN = window.RewardMusicNotes;
  const COLORS = [
    '#ef4444', '#f97316', '#fbbf24', '#84cc16', '#22c55e',
    '#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899',
    '#f1f0ff', '#1e293b',
  ];
  const STAMPS = [
    { id: 'quarter', label: '♩', draw: (ctx, x, y, c, s) => MN.drawQuarterNote(ctx, x, y, c, s) },
    { id: 'eighth', label: '♪', draw: (ctx, x, y, c, s) => MN.drawEighthNote(ctx, x, y, c, s) },
    { id: 'beam', label: '♫', draw: (ctx, x, y, c) => {
      MN.drawEighthNote(ctx, x - 10, y, c, 0.85);
      MN.drawEighthNote(ctx, x + 10, y, c, 0.85);
    }},
    { id: 'rest', label: '𝄽', draw: (ctx, x, y, c) => {
      ctx.save();
      ctx.fillStyle = c;
      ctx.font = 'bold 28px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('𝄽', x, y);
      ctx.restore();
    }},
  ];

  const canvas = document.getElementById('paint-canvas');
  const ctx = canvas.getContext('2d');
  const swatchEl = document.getElementById('paint-swatches');
  const stampEl = document.getElementById('paint-stamps');
  const sizeEl = document.getElementById('paint-size');
  const eraserBtn = document.getElementById('paint-eraser');
  const brushBtn = document.getElementById('paint-brush');
  const clearBtn = document.getElementById('paint-clear');

  let color = COLORS[0];
  let mode = 'brush';
  let stampId = 'quarter';
  let drawing = false;
  let last = null;
  let audioCtx = null;

  function ensureAudio() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  }

  function fillBg() {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  function brushSize() {
    return Number(sizeEl?.value || 8);
  }

  function updateHud() {
    const labels = { brush: 'Brush / Bút', eraser: 'Eraser / Tẩy', stamp: 'Note stamp / Dấu nốt' };
    window.RewardShell?.setHud(labels[mode] || mode, `Size ${brushSize()}px`);
  }

  function posFromEvent(e) {
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    return {
      x: (src.clientX - rect.left) * sx,
      y: (src.clientY - rect.top) * sy,
    };
  }

  function placeStamp(p) {
    const stamp = STAMPS.find((s) => s.id === stampId) || STAMPS[0];
    const scale = Math.max(0.6, brushSize() / 12);
    stamp.draw(ctx, p.x, p.y, color, scale);
    ensureAudio();
    const lane = STAMPS.indexOf(stamp) % MN.LANES.length;
    MN.playLane(audioCtx, lane, 0.18);
  }

  function strokeTo(p) {
    if (!last) {
      last = p;
      return;
    }
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = brushSize();
    ctx.strokeStyle = mode === 'eraser' ? '#ffffff' : color;
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
    last = p;
  }

  function onPointerDown(e) {
    e.preventDefault();
    const p = posFromEvent(e);
    if (mode === 'stamp') {
      placeStamp(p);
      return;
    }
    drawing = true;
    last = null;
    strokeTo(p);
  }

  function onPointerMove(e) {
    if (mode === 'stamp' || !drawing) return;
    e.preventDefault();
    strokeTo(posFromEvent(e));
  }

  function onPointerUp() {
    drawing = false;
    last = null;
  }

  function setMode(next) {
    mode = next;
    eraserBtn?.classList.toggle('active', mode === 'eraser');
    brushBtn?.classList.toggle('active', mode === 'brush');
    stampEl?.querySelectorAll('.rg-paint-stamp').forEach((el) => {
      el.classList.toggle('active', mode === 'stamp' && el.dataset.stamp === stampId);
    });
    updateHud();
  }

  function buildSwatches() {
    if (!swatchEl) return;
    swatchEl.innerHTML = '';
    COLORS.forEach((c) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'rg-paint-swatch';
      b.style.background = c;
      b.addEventListener('click', () => {
        color = c;
        swatchEl.querySelectorAll('.rg-paint-swatch').forEach((el) => {
          el.classList.toggle('active', el === b);
        });
        updateHud();
      });
      if (c === color) b.classList.add('active');
      swatchEl.appendChild(b);
    });
  }

  function buildStamps() {
    if (!stampEl) return;
    stampEl.innerHTML = '';
    STAMPS.forEach((s) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'rg-paint-stamp';
      b.dataset.stamp = s.id;
      b.textContent = s.label;
      b.title = s.id;
      b.addEventListener('click', () => {
        stampId = s.id;
        setMode('stamp');
      });
      stampEl.appendChild(b);
    });
  }

  function bindUi() {
    canvas.addEventListener('mousedown', onPointerDown);
    canvas.addEventListener('mousemove', onPointerMove);
    window.addEventListener('mouseup', onPointerUp);
    canvas.addEventListener('touchstart', onPointerDown, { passive: false });
    canvas.addEventListener('touchmove', onPointerMove, { passive: false });
    canvas.addEventListener('touchend', onPointerUp);
    sizeEl?.addEventListener('input', updateHud);
    brushBtn?.addEventListener('click', () => setMode('brush'));
    eraserBtn?.addEventListener('click', () => setMode('eraser'));
    clearBtn?.addEventListener('click', () => {
      fillBg();
      updateHud();
    });
  }

  function restart() {
    fillBg();
    setMode('brush');
    updateHud();
  }

  window.RewardGame = { restart };
  buildSwatches();
  buildStamps();
  bindUi();
  restart();
})();
