(function () {
  const canvas = document.getElementById('hex-canvas');
  const ctx = canvas.getContext('2d');
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const sides = 6;
  const laneCount = 6;
  let score = 0;
  let rotation = 0;
  let blocks = Array.from({ length: laneCount }, () => []);
  let active = null;
  let over = false;

  const colors = ['#f472b6', '#34d399', '#60a5fa', '#fbbf24', '#a78bfa'];

  function laneAngle(i) {
    return rotation + (Math.PI * 2 * i) / laneCount;
  }

  function spawn() {
    active = {
      lane: Math.floor(Math.random() * laneCount),
      dist: 0,
      color: colors[Math.floor(Math.random() * colors.length)],
      speed: 2.2,
    };
  }

  function drawHex(r, fill) {
    ctx.beginPath();
    for (let i = 0; i < sides; i += 1) {
      const a = (Math.PI * 2 * i) / sides - Math.PI / 2;
      const x = cx + Math.cos(a) * r;
      const y = cy + Math.sin(a) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    if (fill) {
      ctx.fillStyle = fill;
      ctx.fill();
    } else {
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 3;
      ctx.stroke();
    }
  }

  function drawBlock(lane, dist, color, alpha) {
    const a = laneAngle(lane);
    const r0 = 55 + dist * 18;
    const r1 = r0 + 16;
    const x0 = cx + Math.cos(a) * r0;
    const y0 = cy + Math.sin(a) * r0;
    const x1 = cx + Math.cos(a) * r1;
    const y1 = cy + Math.sin(a) * r1;
    ctx.globalAlpha = alpha ?? 1;
    ctx.strokeStyle = color;
    ctx.lineWidth = 14;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function matchLane(lane) {
    const stack = blocks[lane];
    if (stack.length < 3) return;
    const last = stack[stack.length - 1];
    let n = 1;
    for (let i = stack.length - 2; i >= 0; i -= 1) {
      if (stack[i] !== last) break;
      n += 1;
    }
    if (n >= 3) {
      blocks[lane].splice(-3);
      score += 30;
      matchLane(lane);
    }
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawHex(120, null);
    drawHex(48, '#1e293b');
    blocks.forEach((stack, lane) => {
      stack.forEach((color, i) => drawBlock(lane, i, color, 1));
    });
    if (active) drawBlock(active.lane, active.dist, active.color, 0.95);
    window.RewardShell?.setHud(`Điểm: ${score}`, 'Chạm / Space để xoay');
  }

  function step() {
    if (over) return;
    if (!active) spawn();
    active.dist += active.speed * 0.04;
    if (active.dist >= 3.2) {
      blocks[active.lane].push(active.color);
      matchLane(active.lane);
      const stack = blocks[active.lane];
      if (stack.length > 5) {
        over = true;
        window.RewardShell?.showGameOver(`Hết game! / Game over! Score: ${score}`, restartGame);
        return;
      }
      active = null;
    }
    draw();
    requestAnimationFrame(step);
  }

  function rotate() {
    rotation += (Math.PI * 2) / laneCount;
  }

  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowLeft' || e.code === 'ArrowRight') {
      e.preventDefault();
      rotate();
    }
  });
  canvas.addEventListener('click', rotate);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    rotate();
  }, { passive: false });

  requestAnimationFrame(step);

  function restartGame() {
    score = 0;
    rotation = 0;
    blocks = Array.from({ length: laneCount }, () => []);
    active = null;
    over = false;
    window.RewardShell?.hideGameOver();
    requestAnimationFrame(step);
  }
  window.RewardGame = { restart: restartGame };
})();
