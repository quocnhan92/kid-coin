(function () {
  const canvas = document.getElementById('fs-canvas');
  const overlay = document.getElementById('fs-overlay');
  const overlayMsg = document.getElementById('fs-overlay-msg');
  const startBtn = document.getElementById('fs-start');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const W = canvas.width;
  const H = canvas.height;
  const PLANE_Y = H - 48;
  const GAP = 34;
  const FLY_SZ = 26;

  const LEVELS = [
    { name: 'Training', cols: 4, rows: 3, hp: 1, formSpd: 0.6, formDrop: 8, bulletSpd: 6.5, fireMs: 380, eggMs: 0, diveMs: 9000, diveN: [1, 1], diveSpd: 2.8 },
    { name: 'Swarm', cols: 5, rows: 3, hp: 1, formSpd: 0.85, formDrop: 9, bulletSpd: 7, fireMs: 340, eggMs: 4200, diveMs: 7000, diveN: [1, 2], diveSpd: 3.2 },
    { name: 'Dive Squad', cols: 5, rows: 4, hp: 1, formSpd: 1.0, formDrop: 10, bulletSpd: 7.5, fireMs: 300, eggMs: 3800, diveMs: 5500, diveN: [2, 3], diveSpd: 3.8 },
    { name: 'Egg Storm', cols: 6, rows: 4, hp: 2, formSpd: 1.15, formDrop: 10, bulletSpd: 8, fireMs: 270, eggMs: 2800, diveMs: 4800, diveN: [2, 4], diveSpd: 4.2 },
    { name: 'Sky Raid', cols: 6, rows: 5, hp: 2, formSpd: 1.35, formDrop: 11, bulletSpd: 8.5, fireMs: 230, eggMs: 2200, diveMs: 4000, diveN: [3, 4], diveSpd: 4.8 },
    { name: 'Moon Patrol', cols: 6, rows: 4, hp: 2, formSpd: 1.5, formDrop: 12, bulletSpd: 8.8, fireMs: 210, eggMs: 2000, diveMs: 3600, diveN: [3, 4], diveSpd: 5.1 },
    { name: 'Star Siege', cols: 7, rows: 4, hp: 2, formSpd: 1.62, formDrop: 12, bulletSpd: 9, fireMs: 195, eggMs: 1750, diveMs: 3300, diveN: [3, 5], diveSpd: 5.4 },
    { name: 'Neon Raid', cols: 7, rows: 5, hp: 2, formSpd: 1.75, formDrop: 13, bulletSpd: 9.2, fireMs: 180, eggMs: 1500, diveMs: 3000, diveN: [4, 5], diveSpd: 5.7, zigzag: true },
    { name: 'Void Swarm', cols: 7, rows: 5, hp: 3, formSpd: 1.9, formDrop: 14, bulletSpd: 9.5, fireMs: 165, eggMs: 1300, diveMs: 2700, diveN: [4, 6], diveSpd: 6, zigzag: true },
    { name: 'Final Raid', cols: 8, rows: 6, hp: 3, formSpd: 2.1, formDrop: 15, bulletSpd: 9.8, fireMs: 150, eggMs: 1100, diveMs: 2400, diveN: [4, 6], diveSpd: 6.5, zigzag: true, doubleShot: true },
  ];

  let planeX = W / 2;
  let targetX = planeX;
  let bullets = [];
  let flies = [];
  let eggs = [];
  let stars = [];
  let formX = 0;
  let formY = 36;
  let formDir = 1;
  let level = 1;
  let score = 0;
  let lives = 3;
  let playing = false;
  let raf = 0;
  let last = 0;
  let lastShot = 0;
  let eggTimer = 0;
  let diveTimer = 0;
  let keys = { left: false, right: false };
  let cfg = LEVELS[0];
  let wonGame = false;
  let skyTick = 0;

  function rand(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
  }

  function initStars() {
    stars = Array.from({ length: 90 }, () => ({
      x: Math.random() * W,
      y: Math.random() * H * 0.88,
      r: Math.random() * 1.6 + 0.35,
      phase: Math.random() * Math.PI * 2,
      speed: 0.0015 + Math.random() * 0.003,
      layer: Math.random() < 0.3 ? 2 : 1,
    }));
  }

  function gridFlies() {
    return flies.filter((f) => f.mode === 'grid');
  }

  function updateHud() {
    const hearts = '❤️'.repeat(lives) + '🖤'.repeat(Math.max(0, 3 - lives));
    window.RewardShell?.setHud(
      `Score: ${score} / Điểm: ${score}`,
      `Lv ${level}/${LEVELS.length} ${cfg.name} · ${hearts}`,
    );
  }

  function showOverlay(msg, btn) {
    overlayMsg.textContent = msg;
    startBtn.textContent = btn || '▶ Continue / Tiếp';
    overlay.classList.remove('hidden');
  }

  function hideOverlay() {
    overlay.classList.add('hidden');
  }

  function spawnLevel(lv) {
    level = lv;
    cfg = LEVELS[Math.min(lv - 1, LEVELS.length - 1)];
    flies = [];
    bullets = [];
    eggs = [];
    formDir = 1;
    const w = cfg.cols * GAP;
    formX = (W - w) / 2;
    formY = 36;
    for (let r = 0; r < cfg.rows; r += 1) {
      for (let c = 0; c < cfg.cols; c += 1) {
        flies.push({
          mode: 'grid', relX: c * GAP, relY: r * GAP, hp: cfg.hp, maxHp: cfg.hp,
        });
      }
    }
    eggTimer = cfg.eggMs ? rand(1400, cfg.eggMs) : 0;
    diveTimer = rand(2000, cfg.diveMs);
    updateHud();
  }

  function syncGridPos() {
    flies.forEach((f) => {
      if (f.mode !== 'grid') return;
      f.x = formX + f.relX + GAP / 2;
      f.y = formY + f.relY + GAP / 2;
    });
  }

  function moveFormation(dt) {
    const spd = cfg.formSpd * dt * 0.04;
    formX += formDir * spd;
    const w = cfg.cols * GAP;
    if (formX <= 8 || formX + w >= W - 8) {
      formDir *= -1;
      formY += cfg.formDrop || 10;
    }
    syncGridPos();
    if (formY + cfg.rows * GAP > PLANE_Y - 40) loseLife('flies reached you');
  }

  function addBullet(x) {
    bullets.push({ x, y: PLANE_Y - 16, vy: -cfg.bulletSpd });
  }

  function shoot(now) {
    if (now - lastShot < cfg.fireMs) return;
    lastShot = now;
    if (cfg.doubleShot) {
      addBullet(planeX - 9);
      addBullet(planeX + 9);
    } else {
      addBullet(planeX);
    }
  }

  function tickBullets() {
    bullets.forEach((b) => { b.y += b.vy; });
    bullets = bullets.filter((b) => b.y > -8);
  }

  function hitBox(ax, ay, ar, bx, by, br) {
    return Math.abs(ax - bx) < ar + br && Math.abs(ay - by) < ar + br;
  }

  function bulletHits() {
    bullets = bullets.filter((b) => {
      for (const f of flies) {
        if (hitBox(b.x, b.y, 4, f.x, f.y, FLY_SZ / 2)) {
          f.hp -= 1;
          if (f.hp <= 0) {
            score += f.mode === 'dive' ? 15 : 10;
            flies = flies.filter((x) => x !== f);
          }
          updateHud();
          return false;
        }
      }
      return true;
    });
  }

  function dropEgg() {
    const pool = gridFlies();
    if (!pool.length || !cfg.eggMs) return;
    const f = pool[rand(0, pool.length - 1)];
    eggs.push({ x: f.x, y: f.y + 10, vy: 2.2 + level * 0.18 });
  }

  function launchDive() {
    const pool = gridFlies();
    if (!pool.length) return;
    const n = rand(cfg.diveN[0], cfg.diveN[1]);
    for (let i = 0; i < n && pool.length; i += 1) {
      const idx = rand(0, pool.length - 1);
      const f = pool.splice(idx, 1)[0];
      f.mode = 'dive';
      f.vy = cfg.diveSpd;
      f.vx = planeX > f.x ? 0.9 : -0.9;
      f.zig = cfg.zigzag ? Math.random() * Math.PI * 2 : 0;
    }
  }

  function tickDivers(dt) {
    flies.forEach((f) => {
      if (f.mode !== 'dive') return;
      f.y += f.vy * dt * 0.06;
      if (cfg.zigzag) {
        f.zig += dt * 0.012;
        f.x += Math.sin(f.zig) * 2.2;
      } else {
        f.x += f.vx * dt * 0.05;
      }
    });
    flies = flies.filter((f) => f.mode !== 'dive' || f.y < H + 30);
  }

  function tickEggs(dt) {
    eggs.forEach((e) => { e.y += e.vy * dt * 0.06; });
    eggs = eggs.filter((e) => e.y < H + 20);
  }

  function tickHazards(dt) {
    eggTimer -= dt;
    diveTimer -= dt;
    if (cfg.eggMs && eggTimer <= 0) {
      dropEgg();
      eggTimer = cfg.eggMs + rand(-350, 350);
    }
    if (diveTimer <= 0) {
      launchDive();
      diveTimer = cfg.diveMs + rand(-500, 500);
    }
  }

  function checkPlayerHits() {
    for (const f of flies) {
      if (hitBox(planeX, PLANE_Y, 14, f.x, f.y, FLY_SZ / 2)) {
        loseLife('hit by fly');
        return;
      }
    }
    for (const e of eggs) {
      if (hitBox(planeX, PLANE_Y, 14, e.x, e.y, 10)) {
        eggs = eggs.filter((x) => x !== e);
        loseLife('hit by egg');
        return;
      }
    }
  }

  function loseLife() {
    lives -= 1;
    updateHud();
    if (lives <= 0) {
      endGame(false);
      return;
    }
    bullets = [];
    eggs = [];
    flies = flies.filter((f) => f.mode !== 'dive');
    formY = Math.max(36, formY - 20);
    syncGridPos();
  }

  function levelClear() {
    playing = false;
    if (level >= LEVELS.length) {
      endGame(true);
      return;
    }
    const next = LEVELS[level];
    showOverlay(
      `Level ${level} clear! · Next: ${next.name} / Hết màn ${level}! · Tiếp: ${next.name}`,
      '▶ Next level / Màn tiếp',
    );
  }

  function endGame(won) {
    playing = false;
    wonGame = won;
    cancelAnimationFrame(raf);
    const msg = won
      ? `You win! Score: ${score} / Chiến thắng! Điểm: ${score}`
      : `Game over! Score: ${score} · Level ${level} / Hết game! Điểm: ${score} · Màn ${level}`;
    window.RewardShell?.showGameOver(msg, fullRestart);
    showOverlay(won ? 'Victory! / Chiến thắng!' : 'Game over / Hết game', '▶ Play again / Chơi lại');
  }

  function fullRestart() {
    score = 0;
    lives = 3;
    wonGame = false;
    spawnLevel(1);
    beginPlay();
  }

  function beginPlay() {
    hideOverlay();
    playing = true;
    last = 0;
    window.RewardShell?.hideGameOver();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(loop);
  }

  function nextLevel() {
    spawnLevel(level + 1);
    beginPlay();
  }

  function movePlane() {
    const step = 5;
    if (keys.left) targetX -= step;
    if (keys.right) targetX += step;
    targetX = Math.max(20, Math.min(W - 20, targetX));
    planeX += (targetX - planeX) * 0.22;
  }

  function drawNightSky(ts) {
    skyTick = ts;
    const g = ctx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, '#020617');
    g.addColorStop(0.45, '#0f172a');
    g.addColorStop(0.75, '#1e1b4b');
    g.addColorStop(1, '#312e81');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    const mx = W - 52;
    const my = 56;
    const moonG = ctx.createRadialGradient(mx, my, 4, mx, my, 36);
    moonG.addColorStop(0, 'rgba(254,249,195,0.95)');
    moonG.addColorStop(0.5, 'rgba(253,224,71,0.35)');
    moonG.addColorStop(1, 'rgba(253,224,71,0)');
    ctx.fillStyle = moonG;
    ctx.beginPath();
    ctx.arc(mx, my, 36, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#fef9c3';
    ctx.beginPath();
    ctx.arc(mx, my, 22, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#1e1b4b';
    ctx.beginPath();
    ctx.arc(mx + 10, my - 4, 18, 0, Math.PI * 2);
    ctx.fill();

    stars.forEach((s) => {
      const tw = 0.45 + Math.sin(ts * s.speed + s.phase) * 0.35;
      const drift = s.layer === 2 ? ts * 0.008 : ts * 0.003;
      let sx = (s.x + drift) % W;
      if (sx < 0) sx += W;
      ctx.fillStyle = `rgba(255,255,255,${tw * (s.layer === 2 ? 0.9 : 0.65)})`;
      ctx.beginPath();
      ctx.arc(sx, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawPlane() {
    const tilt = (targetX - planeX) * 0.004;
    window.RewardSpaceship?.draw(ctx, planeX, PLANE_Y, { tilt, scale: 1.15, flame: true });
  }

  function drawFly(f) {
    ctx.save();
    ctx.shadowColor = 'rgba(167,139,250,0.5)';
    ctx.shadowBlur = 6;
    ctx.font = `${FLY_SZ}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🪰', f.x, f.y);
    ctx.restore();
    if (f.maxHp > 1) {
      ctx.fillStyle = '#f87171';
      ctx.font = 'bold 10px Nunito,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${f.hp}`, f.x + 12, f.y - 12);
    }
  }

  function drawEgg(e) {
    ctx.font = '18px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🥚', e.x, e.y);
  }

  function drawBullet(b) {
    const glow = ctx.createLinearGradient(b.x, b.y - 8, b.x, b.y + 4);
    glow.addColorStop(0, '#fef08a');
    glow.addColorStop(1, '#f97316');
    ctx.fillStyle = glow;
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 8;
    ctx.fillRect(b.x - 2, b.y - 10, 4, 12);
    ctx.shadowBlur = 0;
  }

  function draw() {
    drawNightSky(skyTick || performance.now());
    eggs.forEach(drawEgg);
    flies.forEach(drawFly);
    bullets.forEach(drawBullet);
    drawPlane();
  }

  function loop(ts) {
    if (!playing) return;
    const dt = last ? ts - last : 16;
    last = ts;
    movePlane();
    moveFormation(dt);
    tickDivers(dt);
    tickEggs(dt);
    tickHazards(dt);
    shoot(ts);
    tickBullets();
    bulletHits();
    checkPlayerHits();
    draw();
    if (flies.length === 0) levelClear();
    else raf = requestAnimationFrame(loop);
  }

  function bindInput() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
    });
    window.addEventListener('keyup', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
    });
    canvas.addEventListener('pointerdown', (e) => {
      canvas.setPointerCapture(e.pointerId);
      const rect = canvas.getBoundingClientRect();
      targetX = (e.clientX - rect.left) * (W / rect.width);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!e.buttons) return;
      const rect = canvas.getBoundingClientRect();
      targetX = (e.clientX - rect.left) * (W / rect.width);
    });
    startBtn?.addEventListener('click', () => {
      if (wonGame || lives <= 0) fullRestart();
      else if (!playing && flies.length === 0) nextLevel();
      else if (!playing) beginPlay();
    });
  }

  initStars();
  spawnLevel(1);
  syncGridPos();
  draw();
  bindInput();
  window.RewardGame = { restart: fullRestart };
  window.RewardShell?.pauseOnHidden(() => {
    if (playing) {
      playing = false;
      cancelAnimationFrame(raf);
    }
  });
})();
