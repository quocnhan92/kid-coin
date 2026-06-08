(function () {
  const MN = window.RewardMusicNotes;
  const canvas = document.getElementById('rd-canvas');
  const ctx = canvas.getContext('2d');
  const LANES = 2;
  const BPM = 96;
  const MS = 60000 / BPM;
  const SCROLL = 2400;
  const MELODY = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1].map((lane, i) => ({
    lane,
    at: i * MS,
  }));
  let notes = [];
  let idx = 0;
  let start = 0;
  let scores = [0, 0];
  let idxNote = 0;
  let playing = false;
  let raf = 0;
  let audioCtx = null;

  function scrollMs() {
    return SCROLL;
  }

  function spawn(until) {
    while (idxNote < MELODY.length && MELODY[idxNote].at <= until) {
      notes.push({ ...MELODY[idxNote], hit: null });
      idxNote += 1;
    }
  }

  function laneX(lane) {
    const w = canvas.width / LANES;
    return w * lane + w / 2;
  }

  function hitY() {
    return canvas.height - 48;
  }

  function draw() {
    const t = performance.now() - start;
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#334155';
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.stroke();
    const scroll = scrollMs();
    notes.forEach((n) => {
      const prog = (t - (n.at - scroll)) / scroll;
      if (prog < 0 || prog > 1.05) return;
      const y = prog * hitY();
      MN.drawQuarterNote(ctx, laneX(n.lane), y, MN.LANES[n.lane].color, 0.85);
    });
    ctx.strokeStyle = '#fbbf24';
    ctx.beginPath();
    ctx.moveTo(0, hitY());
    ctx.lineTo(canvas.width, hitY());
    ctx.stroke();
    window.RewardShell?.setHud(`Green ${scores[0]}`, `Blue ${scores[1]}`);
  }

  function judge(lane) {
    const t = performance.now() - start;
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
    if (!best || bestD > 220) return;
    best.hit = true;
    scores[lane] += bestD < 120 ? 100 : 50;
    if (!audioCtx) audioCtx = new AudioContext();
    MN.playLane(audioCtx, lane === 0 ? 0 : 2, 0.2);
  }

  function tick() {
    if (!playing) return;
    const t = performance.now() - start;
    spawn(t + scrollMs());
    draw();
    if (idxNote >= MELODY.length && notes.every((n) => n.hit)) {
      playing = false;
      const msg =
        scores[0] > scores[1] ? 'Green wins!' : scores[1] > scores[0] ? 'Blue wins!' : 'Draw!';
      window.RewardShell?.showGameOver(msg, restart);
      return;
    }
    raf = requestAnimationFrame(tick);
  }

  function bindKeys() {
    document.getElementById('rd-keys')?.addEventListener('click', (e) => {
      const b = e.target.closest('[data-lane]');
      if (!b) return;
      judge(Number(b.dataset.lane));
    });
    const CT = window.RewardCoopTouch;
    if (CT?.setupTouchUi()) {
      const zL = document.getElementById('rd-zone-l');
      const zR = document.getElementById('rd-zone-r');
      const tapL = () => judge(0);
      const tapR = () => judge(1);
      zL?.addEventListener('touchstart', (e) => {
        e.preventDefault();
        tapL();
      });
      zR?.addEventListener('touchstart', (e) => {
        e.preventDefault();
        tapR();
      });
      zL?.addEventListener('click', tapL);
      zR?.addEventListener('click', tapR);
    }
  }

  function restart() {
    notes = [];
    idxNote = 0;
    scores = [0, 0];
    playing = true;
    start = performance.now();
    window.RewardShell?.hideGameOver();
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(tick);
  }

  bindKeys();
  restart();
  window.RewardGame = { restart };
})();
