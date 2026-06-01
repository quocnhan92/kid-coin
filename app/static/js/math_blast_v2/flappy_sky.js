/**
 * Gà Toán — mây từ trên xuống dần, gà nhích lên ~1cm/câu đúng rồi lướt ngang giữa các tầng mây.
 */
(function () {
  const LAYER_COUNT = 9;
  const ALTITUDE_CLOUD_START = 3;
  const ALTITUDE_AMONG = 12;
  const ALTITUDE_ABOVE = 28;
  const ALTITUDE_SUN = 16;
  const BIRD_STEP_PX = 10;
  const BIRD_BASE_BOTTOM_PCT = 36;

  const LAYER_CFG = [
    { opacity: 0.22, scale: 0.44, count: 3, unlockAt: 3 },
    { opacity: 0.28, scale: 0.5, count: 4, unlockAt: 5 },
    { opacity: 0.34, scale: 0.56, count: 4, unlockAt: 8 },
    { opacity: 0.4, scale: 0.62, count: 5, unlockAt: 11 },
    { opacity: 0.46, scale: 0.7, count: 5, unlockAt: 14 },
    { opacity: 0.54, scale: 0.78, count: 6, unlockAt: 17 },
    { opacity: 0.62, scale: 0.88, count: 6, unlockAt: 20 },
    { opacity: 0.7, scale: 0.98, count: 7, unlockAt: 24 },
    { opacity: 0.78, scale: 1.1, count: 7, unlockAt: 27 },
  ];

  let backCanvas = null;
  let frontCanvas = null;
  let backCtx = null;
  let frontCtx = null;
  let stageEl = null;
  let birdEl = null;
  let width = 0;
  let height = 0;
  let altitude = 0;
  let smoothAlt = 0;
  let worldFall = 0;
  let targetFall = 0;
  let layers = [];
  let rafId = null;
  let drift = 0;
  let reducedMotion = false;
  let glideTimer = null;

  function flightPhase() {
    if (altitude < ALTITUDE_CLOUD_START) return 'ground';
    if (altitude < ALTITUDE_AMONG) return 'entering';
    if (altitude < ALTITUDE_ABOVE) return 'among';
    return 'above';
  }

  function altitudeNorm() {
    return Math.min(altitude / 42, 1);
  }

  function mulberry32(seed) {
    return function () {
      let t = (seed += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function buildClouds() {
    layers = LAYER_CFG.map((cfg, li) => {
      const rnd = mulberry32(1000 + li * 97);
      const clouds = [];
      for (let i = 0; i < cfg.count; i++) {
        clouds.push({ x: rnd() * 1.25 - 0.12, y: rnd(), wobble: rnd() * Math.PI * 2 });
      }
      return { ...cfg, index: li, clouds };
    });
  }

  function layerVis(layer) {
    if (altitude < layer.unlockAt) return 0;
    return Math.min(1, (altitude - layer.unlockAt + 1) / 4);
  }

  function birdBottomPercent() {
    return BIRD_BASE_BOTTOM_PCT + Math.min(altitude * 0.42, 24);
  }

  function birdCenterY() {
    const bottomPct = birdBottomPercent();
    return height * (1 - bottomPct / 100) - 28;
  }

  function updateBirdDom() {
    if (!birdEl) birdEl = document.getElementById('flappy-bird');
    if (!birdEl) return;
    const risePx = Math.min(altitude * BIRD_STEP_PX, 130);
    birdEl.style.bottom = `calc(${BIRD_BASE_BOTTOM_PCT}% + ${risePx}px)`;
    birdEl.style.setProperty('--bird-rise', `${risePx}px`);
  }

  function skyGradient(ctx, h, offsetY) {
    const t = altitudeNorm();
    const g = ctx.createLinearGradient(0, offsetY, 0, offsetY + h * 1.15);
    g.addColorStop(0, lerpColor('#0c4a6e', '#7dd3fc', t));
    g.addColorStop(0.4, lerpColor('#0369a1', '#bae6fd', t * 0.9));
    g.addColorStop(1, lerpColor('#38bdf8', '#e0f2fe', t * 0.55));
    return g;
  }

  function lerpColor(a, b, t) {
    const pa = hexRgb(a);
    const pb = hexRgb(b);
    return `rgb(${Math.round(pa[0] + (pb[0] - pa[0]) * t)},${Math.round(pa[1] + (pb[1] - pa[1]) * t)},${Math.round(pa[2] + (pb[2] - pa[2]) * t)})`;
  }

  function hexRgb(hex) {
    const n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }

  function drawSun(ctx, offsetY) {
    if (altitude < ALTITUDE_SUN) return;
    const t = Math.min((altitude - ALTITUDE_SUN) / 16, 1);
    const cx = width * 0.7;
    const cy = offsetY + height * 0.11;
    const r = 20 + t * 16;
    const glow = ctx.createRadialGradient(cx, cy, r * 0.1, cx, cy, r * 2.5);
    glow.addColorStop(0, `rgba(254, 240, 138, ${0.5 * t})`);
    glow.addColorStop(1, 'rgba(254, 240, 138, 0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, offsetY, width, height * 0.4);
    ctx.fillStyle = `rgba(254, 249, 195, ${0.95 * t})`;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = `rgba(253, 224, 71, ${0.9 * t})`;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.8, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawCloudPuff(ctx, cx, cy, scale, opacity) {
    const r = 18 * scale;
    ctx.fillStyle = `rgba(255,255,255,${opacity})`;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 0.88, 0, Math.PI * 2);
    ctx.arc(cx + r * 0.7, cy - r * 0.3, r * 0.8, 0, Math.PI * 2);
    ctx.arc(cx + r * 1.3, cy + r * 0.05, r * 0.75, 0, Math.PI * 2);
    ctx.closePath();
    ctx.fill();
  }

  /** Mây xuất hiện từ trên, trời trượt xuống (worldFall), rồi tụt dần xuống đáy. */
  function cloudY(layer, c, vis) {
    const spawnY = -60 - layer.index * 28;
    const amongY = height * (0.22 + layer.index * 0.065) + worldFall * 0.35;
    const aboveY = height * (0.62 + layer.index * 0.034) + worldFall * 0.12;
    const phase = flightPhase();
    let targetY = spawnY;
    if (phase === 'entering') {
      targetY = spawnY + (amongY - spawnY) * vis;
    } else if (phase === 'among') {
      targetY = amongY;
    } else if (phase === 'above') {
      targetY = amongY + (aboveY - amongY) * Math.min(1, (altitude - ALTITUDE_ABOVE) / 10);
    } else {
      targetY = spawnY;
    }
    return targetY + (reducedMotion ? 0 : Math.sin(drift * 0.2 + c.wobble) * 2);
  }

  function drawLayer(ctx, layer, slot) {
    const vis = layerVis(layer);
    if (vis <= 0) return;
    const bY = birdCenterY();
    const phase = flightPhase();
    layer.clouds.forEach((c, i) => {
      const x = ((c.x * width + drift * (3 + layer.index) + i * 34) % (width + 90)) - 45;
      const y = cloudY(layer, c, vis);
      const op = layer.opacity * vis;
      const belowBird = y > bY - 10;
      if (phase === 'entering' || phase === 'ground') {
        if (slot === 'front') return;
      } else {
        if (slot === 'back' && !belowBird) return;
        if (slot === 'front' && belowBird) return;
      }
      drawCloudPuff(ctx, x, y, layer.scale, op * (slot === 'front' ? 0.72 : 1));
      if (slot === 'back' && layer.index < 4) {
        drawCloudPuff(ctx, x + width * 0.25, y + 12, layer.scale * 0.82, op * 0.6);
      }
    });
  }

  function paintCanvas(ctx, slot) {
    if (!ctx || !width || !height) return;
    ctx.clearRect(0, 0, width, height);
    const offsetY = worldFall * 0.08;
    ctx.save();
    ctx.translate(0, offsetY);
    ctx.fillStyle = skyGradient(ctx, height, offsetY);
    ctx.fillRect(0, -offsetY, width, height + offsetY + 40);
    drawSun(ctx, -offsetY);
    layers.forEach((layer) => drawLayer(ctx, layer, slot));
    ctx.restore();
  }

  function applyStageClasses() {
    if (!stageEl) return;
    const phase = flightPhase();
    stageEl.dataset.altitude = String(altitude);
    stageEl.dataset.flight = phase;
    stageEl.classList.toggle('mb-flappy-clouds', altitude >= ALTITUDE_CLOUD_START);
    stageEl.classList.toggle('mb-flappy-sun', altitude >= ALTITUDE_SUN);
    stageEl.classList.toggle('mb-flight-ground', phase === 'ground');
    stageEl.classList.toggle('mb-flight-entering', phase === 'entering');
    stageEl.classList.toggle('mb-flight-among', phase === 'among');
    stageEl.classList.toggle('mb-flight-above', phase === 'above');
  }

  function draw() {
    smoothAlt += (altitude - smoothAlt) * 0.1;
    targetFall = Math.min(altitude * 5.5, height * 0.55);
    worldFall += (targetFall - worldFall) * 0.06;
    if (!reducedMotion) drift += 0.1;

    paintCanvas(backCtx, 'back');
    const phase = flightPhase();
    if ((phase === 'among' || phase === 'above') && frontCanvas && frontCtx) {
      paintCanvas(frontCtx, 'front');
      frontCanvas.style.opacity = '1';
    } else if (frontCanvas && frontCtx) {
      frontCtx.clearRect(0, 0, width, height);
      frontCanvas.style.opacity = '0';
    }

    updateBirdDom();
    applyStageClasses();
    rafId = requestAnimationFrame(draw);
  }

  function resize() {
    if (!stageEl) return;
    const rect = stageEl.getBoundingClientRect();
    width = Math.max(1, Math.floor(rect.width));
    height = Math.max(1, Math.floor(rect.height));
    [backCanvas, frontCanvas].forEach((c) => {
      if (!c) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      c.width = width * dpr;
      c.height = height * dpr;
      c.style.width = `${width}px`;
      c.style.height = `${height}px`;
      const ctx = c.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (c === backCanvas) backCtx = ctx;
      else frontCtx = ctx;
    });
  }

  function setAltitude(n) {
    altitude = Math.max(0, Math.floor(n));
    updateBirdDom();
  }

  function startGlide() {
    if (!birdEl) birdEl = document.getElementById('flappy-bird');
    if (!birdEl || reducedMotion) return;
    if (altitude < ALTITUDE_CLOUD_START) {
      birdEl.classList.remove('mb-bird-glide', 'mb-bird-rise');
      return;
    }
    birdEl.classList.add('mb-bird-glide');
  }

  function bump() {
    if (!birdEl) birdEl = document.getElementById('flappy-bird');
    if (!birdEl) return;
    birdEl.classList.remove('mb-bird-glide', 'mb-bird-rise', 'mb-bird-bump');
    void birdEl.offsetWidth;
    birdEl.classList.add('mb-bird-rise');
    if (glideTimer) clearTimeout(glideTimer);
    glideTimer = setTimeout(() => {
      birdEl.classList.remove('mb-bird-rise');
      startGlide();
    }, 480);
  }

  function reset() {
    altitude = 0;
    smoothAlt = 0;
    worldFall = 0;
    targetFall = 0;
    if (birdEl) {
      birdEl.classList.remove('mb-bird-glide', 'mb-bird-rise', 'mb-bird-bump');
      birdEl.style.bottom = `${BIRD_BASE_BOTTOM_PCT}%`;
    }
  }

  function init() {
    stageEl = document.getElementById('flappy-stage');
    backCanvas = document.getElementById('flappy-sky-back');
    frontCanvas = document.getElementById('flappy-sky-front');
    birdEl = document.getElementById('flappy-bird');
    if (!stageEl || !backCanvas) return false;
    reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    buildClouds();
    resize();
    window.addEventListener('resize', resize);
    if (rafId) cancelAnimationFrame(rafId);
    draw();
    startGlide();
    return true;
  }

  function destroy() {
    if (rafId) cancelAnimationFrame(rafId);
    if (glideTimer) clearTimeout(glideTimer);
    rafId = null;
    window.removeEventListener('resize', resize);
  }

  window.FlappySky = {
    init,
    destroy,
    setAltitude,
    bump,
    reset,
    LAYER_COUNT,
    ALTITUDE_ABOVE,
  };
})();
