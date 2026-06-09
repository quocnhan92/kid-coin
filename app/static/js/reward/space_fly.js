(function () {
  const canvas = document.getElementById('space-canvas');
  const hint = document.getElementById('space-tap-hint');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const W = canvas.width;
  const H = canvas.height;
  const PLANE_W = 36;
  const PLANE_H = 32;
  const PLANE_Y = H - 56;

  let planeX = W / 2;
  let targetX = planeX;
  let rocks = [];
  let pickups = [];
  let bgStars = [];
  let score = 0;
  let dist = 0;
  let speed = 2.2;
  let spawnT = 0;
  let starT = 0;
  let playing = false;
  let raf = 0;
  let keys = { left: false, right: false };

  function rand(min, max) {
    return min + Math.random() * (max - min);
  }

  function initBg() {
    bgStars = Array.from({ length: 60 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.5 + 0.5,
      spd: rand(0.3, 1.2),
    }));
  }

  function updateHud() {
    window.RewardShell?.setHud(
      `Score: ${score} / Điểm: ${score}`,
      `Distance: ${Math.floor(dist)}m`,
    );
  }

  function spawnRock() {
    const r = rand(14, 28);
    rocks.push({
      x: rand(r, W - r),
      y: -r,
      r,
      rot: Math.random() * Math.PI,
      spin: rand(-0.04, 0.04),
    });
  }

  function spawnStar() {
    pickups.push({
      x: rand(20, W - 20),
      y: -16,
      r: 10,
      pulse: 0,
    });
  }

  function reset() {
    cancelAnimationFrame(raf);
    planeX = W / 2;
    targetX = planeX;
    rocks = [];
    pickups = [];
    score = 0;
    dist = 0;
    speed = 2.2;
    spawnT = 0;
    starT = 0;
    playing = true;
    hint?.classList.add('hidden');
    window.RewardShell?.hideGameOver();
    updateHud();
    loop();
  }

  function endGame() {
    playing = false;
    cancelAnimationFrame(raf);
    const msg = `Crashed! Score: ${score} · Distance: ${Math.floor(dist)}m / Va chạm! Điểm: ${score} · ${Math.floor(dist)}m`;
    window.RewardShell?.showGameOver(msg, reset);
  }

  function movePlane() {
    const step = keys.left || keys.right ? 5.5 : 4;
    if (keys.left) targetX -= step;
    if (keys.right) targetX += step;
    targetX = Math.max(PLANE_W / 2, Math.min(W - PLANE_W / 2, targetX));
    planeX += (targetX - planeX) * 0.18;
  }

  function tickEntities(dt) {
    spawnT += dt;
    starT += dt;
    const spawnGap = Math.max(420, 900 - dist * 0.4);
    if (spawnT > spawnGap) {
      spawnRock();
      spawnT = 0;
    }
    if (starT > 2200) {
      spawnStar();
      starT = 0;
    }
    rocks.forEach((r) => {
      r.y += speed * dt * 0.06;
      r.rot += r.spin;
    });
    pickups.forEach((s) => {
      s.y += speed * dt * 0.055;
      s.pulse += dt * 0.008;
    });
    rocks = rocks.filter((r) => r.y < H + r.r + 10);
    pickups = pickups.filter((s) => s.y < H + 20);
  }

  function hitCircle(ax, ay, ar, bx, by, br) {
    const dx = ax - bx;
    const dy = ay - by;
    return dx * dx + dy * dy < (ar + br) * (ar + br);
  }

  function checkHits() {
    const px = planeX;
    const py = PLANE_Y;
    const pr = 14;
    for (const r of rocks) {
      if (hitCircle(px, py, pr, r.x, r.y, r.r * 0.85)) {
        endGame();
        return;
      }
    }
    pickups = pickups.filter((s) => {
      if (hitCircle(px, py, pr + 4, s.x, s.y, s.r)) {
        score += 25;
        updateHud();
        return false;
      }
      return true;
    });
  }

  function tickScore(dt) {
    dist += speed * dt * 0.01;
    score += Math.floor(dt * 0.04);
    speed = Math.min(6.5, 2.2 + dist * 0.008);
    updateHud();
  }

  function drawBg() {
    ctx.fillStyle = '#050510';
    ctx.fillRect(0, 0, W, H);
    bgStars.forEach((s) => {
      s.y += s.spd;
      if (s.y > H) {
        s.y = 0;
        s.x = Math.random() * W;
      }
      ctx.fillStyle = `rgba(200,210,255,${0.4 + s.r * 0.3})`;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawRock(r) {
    ctx.save();
    ctx.translate(r.x, r.y);
    ctx.rotate(r.rot);
    ctx.fillStyle = '#6b7280';
    ctx.strokeStyle = '#9ca3af';
    ctx.lineWidth = 2;
    ctx.beginPath();
    const n = 7;
    for (let i = 0; i < n; i += 1) {
      const a = (i / n) * Math.PI * 2;
      const rad = r.r * (0.75 + Math.sin(i * 2.1) * 0.25);
      const px = Math.cos(a) * rad;
      const py = Math.sin(a) * rad;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  function drawStar(s) {
    const glow = 0.6 + Math.sin(s.pulse) * 0.3;
    ctx.save();
    ctx.translate(s.x, s.y);
    ctx.fillStyle = `rgba(250,204,21,${glow})`;
    ctx.font = `${s.r * 2}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('⭐', 0, 0);
    ctx.restore();
  }

  function drawPlane() {
    const tilt = (targetX - planeX) * 0.004;
    window.RewardSpaceship?.draw(ctx, planeX, PLANE_Y, { tilt, scale: 1.05, flame: true });
  }

  function draw() {
    drawBg();
    rocks.forEach(drawRock);
    pickups.forEach(drawStar);
    drawPlane();
  }

  let last = 0;
  function loop(ts) {
    if (!playing) return;
    const dt = last ? ts - last : 16;
    last = ts;
    movePlane();
    tickEntities(dt);
    checkHits();
    tickScore(dt);
    draw();
    raf = requestAnimationFrame(loop);
  }

  function setTarget(clientX) {
    const rect = canvas.getBoundingClientRect();
    const scale = W / rect.width;
    targetX = (clientX - rect.left) * scale;
    if (!playing) reset();
  }

  function bindInput() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
      if (!playing && (keys.left || keys.right)) reset();
    });
    window.addEventListener('keyup', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
    });
    canvas.addEventListener('pointerdown', (e) => {
      canvas.setPointerCapture(e.pointerId);
      setTarget(e.clientX);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (e.buttons) setTarget(e.clientX);
    });
    canvas.addEventListener('click', () => {
      if (!playing) reset();
    });
  }

  initBg();
  bindInput();
  draw();
  window.RewardGame = { restart: reset };
  window.RewardShell?.pauseOnHidden(() => {
    if (!playing) return;
    playing = false;
    cancelAnimationFrame(raf);
    last = 0;
  });
})();
