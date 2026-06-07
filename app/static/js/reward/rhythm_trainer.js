(function () {
  const MN = window.RewardMusicNotes;
  const LANES = MN.LANES.length;
  const BPM = 108;
  const MS_BEAT = 60000 / BPM;
  const SCROLL_BASE = 1800;
  const SPEED_START = 0.5;
  const SPEED_STEP = 0.1;
  const SPEED_EVERY = 10;
  const PERFECT = 120;
  const GOOD = 220;
  const MELODY = [
    0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 3, 2, 1, 0,
    0, 0, 1, 1, 2, 2, 3, 3, 2, 1, 0, 3, 2, 1,
    1, 2, 3, 2, 1, 0, 1, 2, 3, 0, 1, 2, 3, 2,
  ].map((lane, i) => ({ lane, at: i * MS_BEAT, eighth: i % 2 === 1 }));

  const canvas = document.getElementById('rhythm-canvas');
  const ctx = canvas.getContext('2d');
  let audioCtx = null;
  let notes = [];
  let idx = 0;
  let startAt = 0;
  let score = 0;
  let combo = 0;
  let maxCombo = 0;
  let hearts = 5;
  let playing = false;
  let raf = 0;
  let flash = 0;
  let beatFlash = 0;
  let speedMult = SPEED_START;
  let hitsOk = 0;

  function scrollMs() {
    return SCROLL_BASE / speedMult;
  }

  function nowMs() {
    return performance.now();
  }

  function laneX(lane) {
    return (canvas.width / LANES) * lane + canvas.width / LANES / 2;
  }

  function hitY() {
    return canvas.height - 72;
  }

  function ensureAudio() {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  }

  function spawnNotes(until) {
    while (idx < MELODY.length && MELODY[idx].at <= until) {
      const m = MELODY[idx];
      notes.push({ lane: m.lane, at: m.at, eighth: m.eighth, hit: null });
      idx += 1;
    }
  }

  function updateHud() {
    const tier = Math.floor(hitsOk / SPEED_EVERY);
    window.RewardShell?.setHud(
      `Score: ${score} · Combo: ${combo}`,
      `♥ ${hearts} · Lv ${tier + 1} · speed ${speedMult.toFixed(1)} · ${idx}/${MELODY.length} nốt`
    );
  }

  function bumpSpeed() {
    hitsOk += 1;
    if (hitsOk > 0 && hitsOk % SPEED_EVERY === 0) {
      speedMult += SPEED_STEP;
    }
  }

  function endGame(won) {
    playing = false;
    cancelAnimationFrame(raf);
    const msg = won
      ? `Hay lắm! ${score} điểm · Combo cao nhất ${maxCombo}`
      : `Hết tim — ${score} điểm`;
    window.RewardShell?.showGameOver(msg, startRound);
  }

  function judge(lane) {
    if (!playing) return;
    const t = nowMs() - startAt;
    let best = null;
    let bestD = Infinity;
    notes.forEach((n) => {
      if (n.lane !== lane || n.hit) return;
      const d = Math.abs(t - n.at);
      if (d < bestD) {
        bestD = d;
        best = n;
      }
    });
    if (!best || bestD > GOOD) {
      hearts -= 1;
      combo = 0;
      MN.playTone(audioCtx, 140, 0.1, 0.08);
      flash = 6;
      updateHud();
      if (hearts <= 0) endGame(false);
      return;
    }
    if (bestD <= PERFECT) {
      best.hit = 'perfect';
      score += 100 + combo * 5;
    } else {
      best.hit = 'good';
      score += 50 + combo * 2;
    }
    combo += 1;
    maxCombo = Math.max(maxCombo, combo);
    bumpSpeed();
    MN.playLane(audioCtx, lane, 0.28);
    flash = 3;
    updateHud();
  }

  function missOldNotes(t) {
    notes.forEach((n) => {
      if (n.hit || t - n.at < GOOD) return;
      n.hit = 'miss';
      hearts -= 1;
      combo = 0;
      if (hearts <= 0) endGame(false);
    });
  }

  function drawLaneLabels() {
    const w = canvas.width / LANES;
    ctx.textAlign = 'center';
    ctx.font = 'bold 11px Nunito, sans-serif';
    for (let i = 0; i < LANES; i += 1) {
      const L = MN.LANES[i];
      ctx.fillStyle = L.color;
      ctx.fillText(`${L.sol} · ${L.en}`, w * i + w / 2, 18);
    }
  }

  function drawNote(n, t) {
    const scroll = scrollMs();
    const prog = (t - (n.at - scroll)) / scroll;
    if (prog < 0 || prog > 1.05) return;
    const y = prog * hitY();
    const x = laneX(n.lane);
    const col = n.hit === 'miss' ? '#64748b' : MN.LANES[n.lane].color;
    if (n.eighth) MN.drawEighthNote(ctx, x, y, col, 0.95);
    else MN.drawQuarterNote(ctx, x, y, col, 0.95);
  }

  function draw() {
    const t = nowMs() - startAt;
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width / LANES;
    for (let i = 0; i < LANES; i += 1) {
      ctx.fillStyle = `${MN.LANES[i].color}14`;
      ctx.fillRect(i * w, 0, w - 2, canvas.height);
    }
    drawLaneLabels();
    ctx.strokeStyle = '#fbbf24';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, hitY());
    ctx.lineTo(canvas.width, hitY());
    ctx.stroke();
    notes.forEach((n) => drawNote(n, t));
    if (flash > 0) {
      ctx.fillStyle = `rgba(251,191,36,${flash * 0.04})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      flash -= 1;
    }
    if (beatFlash > 0) {
      ctx.fillStyle = `rgba(255,255,255,${beatFlash * 0.03})`;
      ctx.fillRect(0, hitY() - 4, canvas.width, 8);
      beatFlash -= 1;
    }
  }

  function tickBeat(t) {
    const beat = Math.floor(t / MS_BEAT);
    if (tickBeat.last !== beat) {
      tickBeat.last = beat;
      beatFlash = 4;
      if (playing) MN.playTone(audioCtx, 880, 0.04, 0.03);
    }
  }
  tickBeat.last = -1;

  function tick() {
    if (!playing) return;
    const t = nowMs() - startAt;
    spawnNotes(t + scrollMs());
    missOldNotes(t);
    tickBeat(t);
    draw();
    updateHud();
    if (idx >= MELODY.length && notes.every((n) => n.hit)) endGame(true);
    else raf = requestAnimationFrame(tick);
  }

  function bindInput() {
    document.getElementById('rhythm-keys')?.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-lane]');
      if (!btn) return;
      ensureAudio();
      judge(Number(btn.dataset.lane));
    });
    window.addEventListener('keydown', (e) => {
      const map = { a: 0, s: 1, d: 2, f: 3 };
      const lane = map[e.key.toLowerCase()];
      if (lane === undefined) return;
      e.preventDefault();
      ensureAudio();
      judge(lane);
    });
  }

  function startRound() {
    window.RewardShell?.hideGameOver();
    notes = [];
    idx = 0;
    score = 0;
    combo = 0;
    maxCombo = 0;
    hearts = 5;
    speedMult = SPEED_START;
    hitsOk = 0;
    playing = true;
    startAt = nowMs();
    tickBeat.last = -1;
    updateHud();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(tick);
  }

  window.RewardGame = { restart: startRound };
  window.RewardShell?.pauseOnHidden(() => {
    if (playing) endGame(false);
  });
  bindInput();
  startRound();
})();
