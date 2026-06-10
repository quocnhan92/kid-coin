(function () {
  const canvas = document.getElementById('fs-canvas');
  const overlay = document.getElementById('fs-overlay');
  const overlayMsg = document.getElementById('fs-overlay-msg');
  const startBtn = document.getElementById('fs-start');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  const W = canvas.width;
  const H = canvas.height;
  const PLANE_Y_DEFAULT = H - 48;
  const FORM_DANGER_Y = H - 118;
  const SHIP_SCALE = 1.15;
  const SHIP_LOW = 36;
  const GAP = 34;
  const FLY_SZ = 26;

  const FLY_TIERS = [
    { name: 'red', body: '#ef4444', wing: '#fecaca', stroke: '#991b1b', glow: '#f87171', hp: 1 },
    { name: 'yellow', body: '#eab308', wing: '#fef08a', stroke: '#a16207', glow: '#facc15', hp: 2 },
    { name: 'green', body: '#22c55e', wing: '#bbf7d0', stroke: '#15803d', glow: '#4ade80', hp: 3 },
    { name: 'purple', body: '#a855f7', wing: '#e9d5ff', stroke: '#7e22ce', glow: '#c084fc', hp: 4 },
  ];

  const MAX_LIVES = 5;

  const DROP_DEFS = {
    star: { icon: '⭐', score: 60 },
    heart: { icon: '❤️', heal: 1 },
    rapid: { icon: '⚡', power: 'rapid', ms: 9000 },
    spread: { icon: '🔱', power: 'spread', ms: 11000 },
    laser: { icon: '💠', power: 'laser', ms: 9000 },
  };

  const MAX_LEVEL = 50;
  const WAVE_NAMES = [
    'Training', 'Swarm', 'Dive Squad', 'Egg Storm', 'Sky Raid',
    'Moon Patrol', 'Star Siege', 'Neon Raid', 'Void Swarm', 'Final Raid',
  ];
  const EXTRA_NAMES = ['Nova', 'Cosmos', 'Galaxy', 'Hyper', 'Omega'];

  function levelName(lv) {
    if (lv <= WAVE_NAMES.length) return WAVE_NAMES[lv - 1];
    const tag = EXTRA_NAMES[Math.floor((lv - 11) / 8) % EXTRA_NAMES.length];
    return `${tag} ${lv}`;
  }

  function buildLevel(lv) {
    const n = Math.max(1, Math.min(lv, MAX_LEVEL));
    const cols = Math.min(8, 4 + Math.floor((n - 1) / 6));
    const rows = Math.min(6, 3 + Math.floor((n - 1) / 8));
    const diveMin = n < 20 ? 1 : Math.min(6, 1 + Math.floor(n / 8));
    const diveMax = n < 20 ? Math.min(2, diveMin + 1) : Math.min(6, diveMin + 1 + Math.floor(n / 12));
    return {
      name: levelName(n),
      cols,
      rows,
      formSpd: 0.55 + n * 0.032,
      formDrop: Math.min(12, 8 + Math.floor(n / 7)),
      bulletSpd: 6.5 + n * 0.065,
      fireMs: Math.max(95, 380 - n * 5.5),
      eggMs: n < 2 ? 0 : Math.max(900, 4200 - n * 65),
      poopMs: n < 2 ? 0 : Math.max(2800, 6200 - n * 70),
      diveMs: n < 25 ? Math.max(3200, 9500 - n * 110) : Math.max(1800, 9000 - n * 140),
      diveN: [diveMin, diveMax],
      diveSpd: n >= 49 ? 5.6 + (n - 49) * 0.45 : Math.min(4, 2.5 + n * 0.028),
      zigzag: n >= 8,
      doubleShot: n >= 45,
    };
  }

  let planeX = W / 2;
  let planeY = PLANE_Y_DEFAULT;
  let targetX = planeX;
  let targetY = planeY;
  let bullets = [];
  let flies = [];
  let eggs = [];
  let poops = [];
  let drops = [];
  let bursts = [];
  let stars = [];
  let powerType = 'normal';
  let powerUntil = 0;
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
  let poopTimer = 0;
  let diveTimer = 0;
  let invulnMs = 0;
  let formPenaltyCd = 0;
  let slowMoMs = 0;
  let timeScale = 1;
  let keys = { left: false, right: false, up: false, down: false };

  function shipLowY() {
    return planeY + SHIP_LOW * SHIP_SCALE;
  }
  let cfg = buildLevel(1);
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

  function tierForLevel(lv) {
    if (lv <= 12) return FLY_TIERS[0];
    if (lv <= 25) return FLY_TIERS[1];
    if (lv <= 37) return FLY_TIERS[2];
    return FLY_TIERS[3];
  }

  function activePower() {
    return powerUntil > performance.now() ? powerType : 'normal';
  }

  function powerLabel() {
    const p = activePower();
    if (p === 'rapid') return '⚡';
    if (p === 'spread') return '🔱';
    if (p === 'laser') return '💠';
    return '';
  }

  function updateHud() {
    const hearts = '❤️'.repeat(lives) + '🖤'.repeat(Math.max(0, MAX_LIVES - lives));
    const boost = powerLabel();
    window.RewardShell?.setHud(
      `Score: ${score} / Điểm: ${score}${boost ? ` · ${boost}` : ''}`,
      `Lv ${level}/${MAX_LEVEL} ${cfg.name} · ${tierForLevel(level).name} fly · ${hearts}`,
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
    cfg = buildLevel(lv);
    flies = [];
    bullets = [];
    eggs = [];
    poops = [];
    drops = [];
    bursts = [];
    powerType = 'normal';
    powerUntil = 0;
    invulnMs = 0;
    formPenaltyCd = 0;
    slowMoMs = 0;
    timeScale = 1;
    formDir = 1;
    const w = cfg.cols * GAP;
    formX = (W - w) / 2;
    formY = 36;
    const tier = tierForLevel(level);
    for (let r = 0; r < cfg.rows; r += 1) {
      for (let c = 0; c < cfg.cols; c += 1) {
        flies.push({
          mode: 'grid', relX: c * GAP, relY: r * GAP,
          hp: tier.hp, maxHp: tier.hp, tier,
        });
      }
    }
    eggTimer = cfg.eggMs ? rand(1400, cfg.eggMs) : 0;
    poopTimer = cfg.poopMs ? rand(1800, cfg.poopMs) : 0;
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
    if (formPenaltyCd > 0) return;
    if (formY + cfg.rows * GAP > FORM_DANGER_Y && invulnMs <= 0) {
      formPenaltyCd = 3200;
      loseLife('formation');
      formY = 36;
      syncGridPos();
    }
  }

  function addBullet(x, kind) {
    bullets.push({
      x, y: planeY - 18, vy: -Math.abs(cfg.bulletSpd), kind: kind || 'normal',
    });
  }

  function fireGap() {
    const p = activePower();
    if (p === 'rapid') return cfg.fireMs * 0.5;
    return cfg.fireMs;
  }

  function shoot(now) {
    if (now - lastShot < fireGap()) return;
    lastShot = now;
    const p = activePower();
    const laser = p === 'laser';
    const spread = p === 'spread' || cfg.doubleShot;
    if (spread) {
      addBullet(planeX - 10, laser ? 'laser' : 'normal');
      addBullet(planeX, laser ? 'laser' : 'normal');
      addBullet(planeX + 10, laser ? 'laser' : 'normal');
    } else {
      addBullet(planeX, laser ? 'laser' : 'normal');
    }
    window.SpaceFlightAudio?.playShoot();
  }

  function tickBullets(dt) {
    bullets.forEach((b) => { b.y += b.vy * dt * 0.1; });
    bullets = bullets.filter((b) => b.y > -12 && b.y < H + 12);
  }

  function hitBox(ax, ay, ar, bx, by, br) {
    return Math.abs(ax - bx) < ar + br && Math.abs(ay - by) < ar + br;
  }

  function diveSpeedNow() {
    if (level >= 50) return cfg.diveSpd * 1.08;
    if (level >= 49) return cfg.diveSpd;
    return Math.min(cfg.diveSpd, 2.4 + level * 0.028);
  }

  function spawnDrop(x, y) {
    if (lives < MAX_LIVES && Math.random() < 0.11) {
      drops.push({
        x, y, vy: 1.2, pulse: Math.random() * Math.PI * 2, key: 'heart', ...DROP_DEFS.heart,
      });
      return;
    }
    if (Math.random() > 0.4) return;
    const roll = Math.random();
    let key = 'star';
    if (roll > 0.5 && roll <= 0.74) key = 'rapid';
    else if (roll > 0.74 && roll <= 0.9) key = 'spread';
    else if (roll > 0.9) key = 'laser';
    drops.push({
      x, y, vy: 1.4, pulse: Math.random() * Math.PI * 2, key, ...DROP_DEFS[key],
    });
  }

  function collectDrop(d) {
    if (d.heal) {
      lives = Math.min(MAX_LIVES, lives + d.heal);
      window.SpaceFlightAudio?.playPickup();
    } else if (d.score) {
      score += d.score;
      window.SpaceFlightAudio?.playPickup();
    } else if (d.power) {
      powerType = d.power;
      powerUntil = performance.now() + d.ms;
      window.SpaceFlightAudio?.playPickup();
    }
    updateHud();
  }

  function bulletHits() {
    bullets = bullets.filter((b) => {
      let consumed = false;
      for (const f of flies) {
        if (hitBox(b.x, b.y, b.kind === 'laser' ? 6 : 4, f.x, f.y, FLY_SZ / 2)) {
          const dmg = b.kind === 'laser' ? 2 : 1;
          f.hp -= dmg;
          if (f.hp <= 0) {
            score += f.maxHp * 12 + (f.mode === 'dive' ? 8 : 0);
            spawnDrop(f.x, f.y);
            flies = flies.filter((x) => x !== f);
            window.SpaceFlightAudio?.playFlyBoom();
          } else {
            window.SpaceFlightAudio?.playFlyBup();
          }
          updateHud();
          consumed = true;
          break;
        }
      }
      return !consumed;
    });
  }

  function dropEgg() {
    const pool = gridFlies();
    if (!pool.length || !cfg.eggMs) return;
    const f = pool[rand(0, pool.length - 1)];
    eggs.push({ x: f.x, y: f.y + 10, vy: 2.2 + level * 0.18 });
  }

  function dropPoop() {
    const pool = gridFlies();
    if (!pool.length || !cfg.poopMs) return;
    const f = pool[rand(0, pool.length - 1)];
    const pile = rand(2, 4);
    for (let i = 0; i < pile; i += 1) {
      poops.push({
        x: f.x + rand(-10, 10),
        y: f.y + 14 + i * 3,
        vy: 1.6 + level * 0.1 + Math.random() * 0.4,
        wobble: Math.random() * Math.PI * 2,
        size: 18 + rand(0, 4),
      });
    }
  }

  function spawnBurst(x, y) {
    for (let i = 0; i < 14; i += 1) {
      const a = (i / 14) * Math.PI * 2;
      const spd = 2 + Math.random() * 4;
      bursts.push({
        x, y, vx: Math.cos(a) * spd, vy: Math.sin(a) * spd, life: 420, max: 420,
      });
    }
  }

  function tickBursts(dt) {
    bursts.forEach((b) => {
      b.x += b.vx * dt * 0.06;
      b.y += b.vy * dt * 0.06;
      b.life -= dt;
    });
    bursts = bursts.filter((b) => b.life > 0);
  }

  function launchDive() {
    const pool = gridFlies();
    if (!pool.length) return;
    const n = rand(cfg.diveN[0], cfg.diveN[1]);
    const attackDive = level >= 49;
    for (let i = 0; i < n && pool.length; i += 1) {
      const idx = rand(0, pool.length - 1);
      const f = pool.splice(idx, 1)[0];
      f.mode = 'dive';
      f.divePhase = 'down';
      f.vy = diveSpeedNow();
      f.attack = attackDive && Math.random() < 0.55;
      f.vx = f.attack ? 0 : (planeX > f.x ? 0.45 : -0.45);
      f.zig = cfg.zigzag && !f.attack ? Math.random() * Math.PI * 2 : 0;
    }
  }

  function flyHome(f) {
    return {
      x: formX + f.relX + GAP / 2,
      y: formY + f.relY + GAP / 2,
    };
  }

  function tickDivers(dt) {
    const diveBottom = shipLowY();
    flies.forEach((f) => {
      if (f.mode !== 'dive') return;
      if (f.divePhase === 'down') {
        f.y += f.vy * dt * 0.055;
        if (f.attack) {
          f.x += (planeX - f.x) * Math.min(0.022, dt * 0.00002);
        } else if (cfg.zigzag) {
          f.zig += dt * 0.01;
          f.x += Math.sin(f.zig) * 1.6;
        } else {
          f.x += f.vx * dt * 0.045;
        }
        f.x = Math.max(14, Math.min(W - 14, f.x));
        if (f.y >= diveBottom) {
          f.y = diveBottom;
          f.divePhase = 'up';
        }
        return;
      }
      const home = flyHome(f);
      const riseTarget = Math.min(home.y, diveBottom - 30);
      const step = f.vy * dt * 0.048;
      if (f.y > riseTarget + 4) {
        f.y -= step;
        f.x = Math.max(14, Math.min(W - 14, f.x));
        return;
      }
      const dx = home.x - f.x;
      const dy = home.y - f.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 9) {
        f.mode = 'grid';
        f.divePhase = null;
        f.attack = false;
        f.x = home.x;
        f.y = home.y;
        return;
      }
      f.x += (dx / dist) * step;
      f.y += (dy / dist) * step;
      f.x = Math.max(14, Math.min(W - 14, f.x));
      f.y = Math.max(20, Math.min(H - 20, f.y));
    });
  }

  function tickEggs(dt) {
    eggs.forEach((e) => { e.y += e.vy * dt * 0.06; });
    eggs = eggs.filter((e) => e.y < H + 20);
  }

  function tickPoops(dt) {
    poops.forEach((p) => {
      p.wobble += dt * 0.01;
      p.x += Math.sin(p.wobble) * 0.35;
      p.y += p.vy * dt * 0.06;
    });
    poops = poops.filter((p) => p.y < H + 24);
  }

  function tickDrops(dt) {
    drops.forEach((d) => {
      d.pulse += dt * 0.012;
      d.y += d.vy * dt * 0.06;
    });
    drops = drops.filter((d) => d.y < H + 20);
  }

  function checkDropPickup() {
    for (const d of drops) {
      if (hitBox(planeX, planeY, 16, d.x, d.y, 14)) {
        collectDrop(d);
        drops = drops.filter((x) => x !== d);
        return;
      }
    }
  }

  function tickHazards(dt) {
    eggTimer -= dt;
    poopTimer -= dt;
    diveTimer -= dt;
    if (cfg.eggMs && eggTimer <= 0) {
      dropEgg();
      eggTimer = cfg.eggMs + rand(-350, 350);
    }
    if (cfg.poopMs && poopTimer <= 0) {
      dropPoop();
      poopTimer = cfg.poopMs + rand(-400, 400);
    }
    if (diveTimer <= 0) {
      launchDive();
      diveTimer = cfg.diveMs + rand(-500, 500);
    }
  }

  function tickRespawn(dt) {
    if (slowMoMs > 0) {
      slowMoMs -= dt;
      timeScale = 0.32;
      if (slowMoMs <= 0) timeScale = 1;
    }
    if (invulnMs > 0) invulnMs -= dt;
    if (formPenaltyCd > 0) formPenaltyCd -= dt;
  }

  function checkPlayerHits() {
    if (invulnMs > 0) return;
    for (const f of flies) {
      if (f.mode === 'dive' && f.divePhase !== 'down') continue;
      if (hitBox(planeX, planeY, 14, f.x, f.y, FLY_SZ / 2)) {
        loseLife();
        return;
      }
    }
    for (const e of eggs) {
      if (hitBox(planeX, planeY, 14, e.x, e.y, 10)) {
        eggs = eggs.filter((x) => x !== e);
        loseLife();
        return;
      }
    }
    for (const p of poops) {
      if (hitBox(planeX, planeY, 14, p.x, p.y, p.size * 0.45)) {
        poops = poops.filter((x) => x !== p);
        loseLife();
        return;
      }
    }
  }

  function loseLife() {
    if (invulnMs > 0 || !playing) return;
    window.SpaceFlightAudio?.unlock();
    window.SpaceFlightAudio?.playShipBoom();
    spawnBurst(planeX, planeY);
    lives -= 1;
    updateHud();
    if (lives <= 0) {
      endGame(false);
      return;
    }
    bullets = [];
    eggs = [];
    poops = [];
    flies = flies.filter((f) => f.mode !== 'dive');
    formY = 36;
    planeX = W / 2;
    planeY = PLANE_Y_DEFAULT;
    targetX = W / 2;
    targetY = PLANE_Y_DEFAULT;
    invulnMs = 2400;
    slowMoMs = 750;
    syncGridPos();
  }

  function levelClear() {
    playing = false;
    if (level >= MAX_LEVEL) {
      endGame(true);
      return;
    }
    const next = buildLevel(level + 1);
    showOverlay(
      `Level ${level} clear! · Next: ${next.name} / Hết màn ${level}! · Tiếp: ${next.name}`,
      '▶ Next level / Màn tiếp',
    );
  }

  function endGame(won) {
    playing = false;
    wonGame = won;
    window.SpaceFlightAudio?.stopBgm();
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
    window.__rewardBgmMode = 'cartoon';
    window.SpaceFlightAudio?.unlock();
    window.SpaceFlightAudio?.startCartoonBgm();
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
    if (keys.up) targetY -= step;
    if (keys.down) targetY += step;
    targetX = Math.max(20, Math.min(W - 20, targetX));
    targetY = Math.max(72, Math.min(H - 34, targetY));
    planeX += (targetX - planeX) * 0.22;
    planeY += (targetY - planeY) * 0.22;
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
    if (invulnMs > 0 && Math.floor(invulnMs / 110) % 2 === 0) return;
    const tilt = (targetX - planeX) * 0.004;
    window.RewardSpaceship?.draw(ctx, planeX, planeY, { tilt, scale: SHIP_SCALE, flame: true });
  }

  function drawBurst(b) {
    const a = Math.max(0, b.life / b.max);
    ctx.fillStyle = `rgba(251,191,36,${a * 0.9})`;
    ctx.beginPath();
    ctx.arc(b.x, b.y, 5 * a + 1, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = `rgba(248,113,113,${a * 0.55})`;
    ctx.beginPath();
    ctx.arc(b.x, b.y, 2.5 * a, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawPoop(p) {
    ctx.save();
    ctx.shadowColor = '#a16207';
    ctx.shadowBlur = 14;
    ctx.fillStyle = '#92400e';
    ctx.beginPath();
    ctx.ellipse(p.x, p.y + 4, p.size * 0.55, p.size * 0.35, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.font = `bold ${p.size + 4}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('💩', p.x, p.y);
    ctx.restore();
  }

  function drawFly(f) {
    const t = f.tier || FLY_TIERS[0];
    ctx.save();
    ctx.shadowColor = t.glow;
    ctx.shadowBlur = 14;
    ctx.fillStyle = t.wing;
    ctx.beginPath();
    ctx.ellipse(f.x - 13, f.y - 1, 9, 5, -0.45, 0, Math.PI * 2);
    ctx.ellipse(f.x + 13, f.y - 1, 9, 5, 0.45, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = t.body;
    ctx.strokeStyle = t.stroke;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(f.x, f.y + 1, 11, 9, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(f.x - 4, f.y - 1, 3.5, 0, Math.PI * 2);
    ctx.arc(f.x + 5, f.y - 1, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#0f172a';
    ctx.beginPath();
    ctx.arc(f.x - 3, f.y - 1, 1.8, 0, Math.PI * 2);
    ctx.arc(f.x + 6, f.y - 1, 1.8, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawEgg(e) {
    ctx.save();
    ctx.shadowColor = '#fde047';
    ctx.shadowBlur = 16;
    ctx.fillStyle = 'rgba(253,224,71,0.45)';
    ctx.beginPath();
    ctx.arc(e.x, e.y, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.font = 'bold 26px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🥚', e.x, e.y);
    ctx.restore();
  }

  function drawDrop(d) {
    const bob = Math.sin(d.pulse) * 3;
    ctx.save();
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 16;
    ctx.fillStyle = 'rgba(251,191,36,0.35)';
    ctx.beginPath();
    ctx.arc(d.x, d.y + bob, 16, 0, Math.PI * 2);
    ctx.fill();
    ctx.font = 'bold 22px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(d.icon, d.x, d.y + bob);
    ctx.restore();
  }

  function drawBullet(b) {
    const laser = b.kind === 'laser';
    const glow = ctx.createLinearGradient(b.x, b.y - 10, b.x, b.y + 4);
    if (laser) {
      glow.addColorStop(0, '#e0f2fe');
      glow.addColorStop(1, '#38bdf8');
      ctx.fillStyle = glow;
      ctx.shadowColor = '#0ea5e9';
      ctx.shadowBlur = 12;
      ctx.fillRect(b.x - 3, b.y - 12, 6, 14);
    } else {
      glow.addColorStop(0, '#fef08a');
      glow.addColorStop(1, '#f97316');
      ctx.fillStyle = glow;
      ctx.shadowColor = '#fbbf24';
      ctx.shadowBlur = 10;
      ctx.fillRect(b.x - 2, b.y - 10, 4, 12);
    }
    ctx.shadowBlur = 0;
  }

  function draw() {
    drawNightSky(skyTick || performance.now());
    poops.forEach(drawPoop);
    eggs.forEach(drawEgg);
    drops.forEach(drawDrop);
    flies.forEach(drawFly);
    bullets.forEach(drawBullet);
    bursts.forEach(drawBurst);
    drawPlane();
  }

  function loop(ts) {
    if (!playing) return;
    const rawDt = last ? ts - last : 16;
    last = ts;
    tickRespawn(rawDt);
    const dt = rawDt * timeScale;
    movePlane();
    moveFormation(dt);
    tickDivers(dt);
    tickEggs(dt);
    tickPoops(dt);
    tickDrops(dt);
    tickBursts(dt);
    tickHazards(dt);
    shoot(ts);
    tickBullets(dt);
    bulletHits();
    checkDropPickup();
    checkPlayerHits();
    draw();
    if (flies.length === 0) levelClear();
    else raf = requestAnimationFrame(loop);
  }

  function bindInput() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = true;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = true;
      if (e.key === 'ArrowUp' || e.key === 'w') keys.up = true;
      if (e.key === 'ArrowDown' || e.key === 's') keys.down = true;
    });
    window.addEventListener('keyup', (e) => {
      if (e.key === 'ArrowLeft' || e.key === 'a') keys.left = false;
      if (e.key === 'ArrowRight' || e.key === 'd') keys.right = false;
      if (e.key === 'ArrowUp' || e.key === 'w') keys.up = false;
      if (e.key === 'ArrowDown' || e.key === 's') keys.down = false;
    });
    const setPointerTarget = (e) => {
      const rect = canvas.getBoundingClientRect();
      targetX = (e.clientX - rect.left) * (W / rect.width);
      targetY = (e.clientY - rect.top) * (H / rect.height);
    };
    canvas.addEventListener('pointerdown', (e) => {
      canvas.setPointerCapture(e.pointerId);
      setPointerTarget(e);
    });
    canvas.addEventListener('pointermove', (e) => {
      if (!e.buttons) return;
      setPointerTarget(e);
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
  window.__rewardBgmMode = 'cartoon';
  window.SpaceFlightAudio?.mountToggle(canvas.closest('.fs-wrap'));
  window.RewardGame = { restart: fullRestart };
  window.RewardShell?.pauseOnHidden(() => {
    if (playing) {
      playing = false;
      window.SpaceFlightAudio?.stopBgm();
      cancelAnimationFrame(raf);
    }
  });
})();
