(function () {
  const canvas = document.getElementById('bp-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  let bubbles = [];
  let scores = [0, 0];
  let left = 60;
  let over = false;

  function spawn() {
    const side = Math.random() > 0.5 ? 1 : 2;
    bubbles.push({
      side,
      x: side === 1 ? 40 + Math.random() * (W / 2 - 80) : W / 2 + 40 + Math.random() * (W / 2 - 80),
      y: 40 + Math.random() * (H - 120),
      r: 14 + Math.random() * 10,
      color: side === 1 ? '#34d399' : '#60a5fa',
    });
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#334155';
    ctx.beginPath();
    ctx.moveTo(W / 2, 0);
    ctx.lineTo(W / 2, H);
    ctx.stroke();
    ctx.fillStyle = 'rgba(52,211,153,0.08)';
    ctx.fillRect(0, 0, W / 2, H);
    ctx.fillStyle = 'rgba(96,165,250,0.08)';
    ctx.fillRect(W / 2, 0, W / 2, H);
    bubbles.forEach((b) => {
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
      ctx.fillStyle = b.color;
      ctx.fill();
    });
    window.RewardShell?.setHud(`Green ${scores[0]} · Blue ${scores[1]}`, `Time ${left}s`);
  }

  function popAt(x, y) {
    const side = x < W / 2 ? 1 : 2;
    for (let i = bubbles.length - 1; i >= 0; i -= 1) {
      const b = bubbles[i];
      if (b.side !== side) continue;
      if (Math.hypot(b.x - x, b.y - y) <= b.r + 8) {
        bubbles.splice(i, 1);
        scores[side - 1] += 1;
        return;
      }
    }
  }

  function tick() {
    if (over) return;
    if (Math.random() < 0.08) spawn();
    draw();
    requestAnimationFrame(tick);
  }

  setInterval(() => {
    if (over) return;
    left -= 1;
    if (left <= 0) {
      over = true;
      const msg =
        scores[0] > scores[1]
          ? 'Green wins!'
          : scores[1] > scores[0]
            ? 'Blue wins!'
            : 'Draw! / Hòa!';
      window.RewardShell?.showGameOver(msg, restart);
    }
  }, 1000);

  function tap(e) {
    if (over) return;
    const rect = canvas.getBoundingClientRect();
    const sx = W / rect.width;
    const sy = H / rect.height;
    const src = e.touches?.[0] || e;
    popAt((src.clientX - rect.left) * sx, (src.clientY - rect.top) * sy);
    draw();
  }

  function restart() {
    bubbles = [];
    scores = [0, 0];
    left = 60;
    over = false;
    window.RewardShell?.hideGameOver();
    draw();
    requestAnimationFrame(tick);
  }

  canvas.addEventListener('click', tap);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    tap(e);
  }, { passive: false });
  restart();
  window.RewardGame = { restart };
})();
