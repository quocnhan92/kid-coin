(function () {
  const canvas = document.getElementById('td-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const PATH = [
    { x: 20, y: 200 }, { x: 180, y: 200 }, { x: 180, y: 80 },
    { x: 400, y: 80 }, { x: 400, y: 280 }, { x: 620, y: 280 },
  ];
  let gold = 80;
  let wave = 0;
  let enemies = [];
  let towers = [];
  let spawning = false;
  let spawnLeft = 0;
  let lives = 5;
  let over = false;
  let gameOverShown = false;

  function resetGame() {
    gold = 80;
    wave = 0;
    enemies = [];
    towers = [];
    lives = 5;
    over = false;
    spawning = false;
    spawnLeft = 0;
    gameOverShown = false;
    window.RewardShell?.hideGameOver();
  }

  function showGameOverModal() {
    if (gameOverShown) return;
    gameOverShown = true;
    window.RewardShell?.showGameOver(`Game over! Wave ${wave} / Thua ở đợt ${wave}`, resetGame);
  }

  function dist(a, b) {
    return Math.hypot(a.x - b.x, a.y - b.y);
  }

  function pathPoint(t) {
    const segs = [];
    let total = 0;
    for (let i = 0; i < PATH.length - 1; i += 1) {
      const d = dist(PATH[i], PATH[i + 1]);
      segs.push({ a: PATH[i], b: PATH[i + 1], d, start: total });
      total += d;
    }
    const pos = (t % total);
    const seg = segs.find((s) => pos < s.start + s.d) || segs[segs.length - 1];
    const local = pos - seg.start;
    const ratio = local / seg.d;
    return {
      x: seg.a.x + (seg.b.x - seg.a.x) * ratio,
      y: seg.a.y + (seg.b.y - seg.a.y) * ratio,
    };
  }

  function spawnWave() {
    if (spawning || over) return;
    wave += 1;
    spawning = true;
    spawnLeft = 4 + wave;
  }

  function placeTower(x, y) {
    if (over || gold < 25) return;
    if (towers.some((t) => dist(t, { x, y }) < 36)) return;
    const nearPath = PATH.some((p) => dist(p, { x, y }) < 50);
    if (!nearPath) return;
    gold -= 25;
    towers.push({ x, y, cd: 0 });
  }

  function updateEnemies() {
    enemies.forEach((e) => { e.t += e.speed; });
    enemies = enemies.filter((e) => {
      if (e.t >= 680) {
        lives -= 1;
        if (lives <= 0) {
          over = true;
          showGameOverModal();
        }
        return false;
      }
      return true;
    });
  }

  function shootTowers() {
    towers.forEach((t) => {
      t.cd -= 1;
      if (t.cd > 0) return;
      let best = null;
      let bestD = 90;
      enemies.forEach((e) => {
        const p = pathPoint(e.t);
        const d = dist(t, p);
        if (d < bestD) { bestD = d; best = e; }
      });
      if (!best) return;
      best.hp -= 1;
      t.cd = 18;
      if (best.hp <= 0) {
        gold += 12;
        enemies = enemies.filter((x) => x !== best);
      }
    });
  }

  function step() {
    if (spawning && spawnLeft > 0 && Math.random() < 0.04) {
      enemies.push({ t: 0, speed: 1.1 + wave * 0.08, hp: 2 + Math.floor(wave / 2) });
      spawnLeft -= 1;
      if (spawnLeft <= 0) spawning = false;
    }
    updateEnemies();
    shootTowers();
    draw();
    requestAnimationFrame(step);
  }

  function draw() {
    ctx.fillStyle = '#1c1917';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#78716c';
    ctx.lineWidth = 28;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(PATH[0].x, PATH[0].y);
    PATH.slice(1).forEach((p) => ctx.lineTo(p.x, p.y));
    ctx.stroke();
    towers.forEach((t) => {
      ctx.fillStyle = '#f59e0b';
      ctx.beginPath();
      ctx.arc(t.x, t.y, 14, 0, Math.PI * 2);
      ctx.fill();
    });
    enemies.forEach((e) => {
      const p = pathPoint(e.t);
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(p.x, p.y, 10, 0, Math.PI * 2);
      ctx.fill();
    });
    window.RewardShell?.setHud(
      `🪙 ${gold} · Wave ${wave} · ❤️ ${lives}`,
      over ? 'Game over' : 'Tap path to build (25g)'
    );
  }

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (W / rect.width);
    const y = (e.clientY - rect.top) * (H / rect.height);
    placeTower(x, y);
  });
  document.getElementById('td-wave')?.addEventListener('click', spawnWave);
  document.getElementById('td-reset')?.addEventListener('click', resetGame);
  draw();
  requestAnimationFrame(step);
  window.RewardGame = { restart: resetGame };
})();
