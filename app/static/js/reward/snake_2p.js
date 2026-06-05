(function () {
  const canvas = document.getElementById('sn2-canvas');
  const ctx = canvas.getContext('2d');
  const cols = 26;
  const rows = 26;
  const TICK_EVERY = 18;
  const cell = canvas.width / cols;
  let food = { x: 13, y: 13 };
  let tick = 0;
  let over = false;

  const p1 = {
    body: [{ x: 6, y: 13 }],
    dir: { x: 1, y: 0 },
    next: { x: 1, y: 0 },
    color: '#34d399',
    score: 0,
    keys: { up: 'KeyW', down: 'KeyS', left: 'KeyA', right: 'KeyD' },
  };
  const p2 = {
    body: [{ x: 19, y: 13 }],
    dir: { x: -1, y: 0 },
    next: { x: -1, y: 0 },
    color: '#60a5fa',
    score: 0,
    keys: { up: 'ArrowUp', down: 'ArrowDown', left: 'ArrowLeft', right: 'ArrowRight' },
  };

  function spawnFood() {
    let tries = 0;
    do {
      food = {
        x: Math.floor(Math.random() * cols),
        y: Math.floor(Math.random() * rows),
      };
      tries += 1;
    } while (
      tries < 80 &&
      (p1.body.some((s) => s.x === food.x && s.y === food.y) ||
        p2.body.some((s) => s.x === food.x && s.y === food.y))
    );
  }

  function setDir(p, dx, dy) {
    if (p.dir.x === -dx && p.dir.y === -dy) return;
    p.next = { x: dx, y: dy };
  }

  document.addEventListener('keydown', (e) => {
    [p1, p2].forEach((p) => {
      if (e.code === p.keys.up) setDir(p, 0, -1);
      if (e.code === p.keys.down) setDir(p, 0, 1);
      if (e.code === p.keys.left) setDir(p, -1, 0);
      if (e.code === p.keys.right) setDir(p, 1, 0);
    });
  });

  function hitWall(x, y) {
    return x < 0 || y < 0 || x >= cols || y >= rows;
  }

  function moveSnake(p, other) {
    p.dir = { ...p.next };
    const head = { x: p.body[0].x + p.dir.x, y: p.body[0].y + p.dir.y };
    if (hitWall(head.x, head.y)) return false;
    const hitSelf = p.body.some((s) => s.x === head.x && s.y === head.y);
    const hitOther = other.body.some((s) => s.x === head.x && s.y === head.y);
    if (hitSelf || hitOther) return false;
    p.body.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      p.score += 1;
      spawnFood();
    } else {
      p.body.pop();
    }
    return true;
  }

  function drawGrid() {
    ctx.strokeStyle = 'rgba(51, 65, 85, 0.35)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= cols; i += 1) {
      ctx.beginPath();
      ctx.moveTo(i * cell, 0);
      ctx.lineTo(i * cell, canvas.height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cell);
      ctx.lineTo(canvas.width, i * cell);
      ctx.stroke();
    }
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawGrid();
    ctx.fillStyle = '#fbbf24';
    ctx.fillRect(food.x * cell + 1, food.y * cell + 1, cell - 2, cell - 2);
    [p1, p2].forEach((p) => {
      ctx.fillStyle = p.color;
      p.body.forEach((s, i) => {
        ctx.globalAlpha = i === 0 ? 1 : 0.75;
        ctx.fillRect(s.x * cell + 1, s.y * cell + 1, cell - 2, cell - 2);
      });
      ctx.globalAlpha = 1;
    });
    window.RewardShell?.setHud(`Xanh lá ${p1.score}`, `Xanh dương ${p2.score}`);
  }

  function step() {
    if (over) return;
    tick += 1;
    if (tick % TICK_EVERY !== 0) {
      requestAnimationFrame(step);
      return;
    }
    const ok1 = moveSnake(p1, p2);
    const ok2 = moveSnake(p2, p1);
    if (!ok1 || !ok2) {
      over = true;
      const win = !ok1 && ok2
        ? 'Blue wins! / Xanh dương thắng!'
        : !ok2 && ok1
          ? 'Green wins! / Xanh lá thắng!'
          : 'Draw! / Hòa!';
      window.RewardShell?.showGameOver(win, restartGame);
      return;
    }
    draw();
    requestAnimationFrame(step);
  }

  function restartGame() {
    p1.body = [{ x: 6, y: 13 }];
    p1.dir = { x: 1, y: 0 };
    p1.next = { x: 1, y: 0 };
    p1.score = 0;
    p2.body = [{ x: 19, y: 13 }];
    p2.dir = { x: -1, y: 0 };
    p2.next = { x: -1, y: 0 };
    p2.score = 0;
    tick = 0;
    over = false;
    spawnFood();
    draw();
    window.RewardShell?.hideGameOver();
    requestAnimationFrame(step);
  }

  spawnFood();
  requestAnimationFrame(step);
  window.RewardGame = { restart: restartGame };
})();
