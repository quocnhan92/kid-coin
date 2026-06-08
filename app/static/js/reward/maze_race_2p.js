(function () {
  const canvas = document.getElementById('mr-canvas');
  const ctx = canvas.getContext('2d');
  const N = 9;
  const cell = canvas.width / (N * 2 + 1);
  const p1 = { r: 1, c: 1, color: '#34d399' };
  const p2 = { r: N - 2, c: N - 2, color: '#60a5fa' };
  let m1 = [];
  let m2 = [];
  let over = false;

  function genMaze(seed) {
    const g = Array.from({ length: N }, () => Array(N).fill(1));
    function carve(r, c) {
      g[r][c] = 0;
      const dirs = [[-2, 0], [2, 0], [0, -2], [0, 2]].sort(() => Math.random() - 0.5);
      dirs.forEach(([dr, dc]) => {
        const nr = r + dr;
        const nc = c + dc;
        if (nr > 0 && nr < N - 1 && nc > 0 && nc < N - 1 && g[nr][nc] === 1) {
          g[r + dr / 2][c + dc / 2] = 0;
          carve(nr, nc);
        }
      });
    }
    carve(1, 1);
    g[N - 2][N - 2] = 0;
    return g;
  }

  function drawMaze(maze, ox, oy, player, goal) {
    for (let r = 0; r < N; r += 1) {
      for (let c = 0; c < N; c += 1) {
        ctx.fillStyle = maze[r][c] ? '#1e293b' : '#0f172a';
        ctx.fillRect(ox + c * cell, oy + r * cell, cell - 1, cell - 1);
      }
    }
    ctx.fillStyle = '#fbbf24';
    ctx.fillRect(ox + goal.c * cell, oy + goal.r * cell, cell - 1, cell - 1);
    ctx.fillStyle = player.color;
    ctx.beginPath();
    ctx.arc(ox + player.c * cell + cell / 2, oy + player.r * cell + cell / 2, cell * 0.35, 0, Math.PI * 2);
    ctx.fill();
  }

  function draw() {
    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawMaze(m1, cell, cell, p1, { r: N - 2, c: N - 2 });
    drawMaze(m2, cell * (N + 1), cell, p2, { r: N - 2, c: N - 2 });
    window.RewardShell?.setHud('Race! / Đua!', 'D-pad below / Nút mũi tên dưới');
  }

  function tryMove(p, maze, dr, dc) {
    const nr = p.r + dr;
    const nc = p.c + dc;
    if (nr < 0 || nc < 0 || nr >= N || nc >= N || maze[nr][nc]) return;
    p.r = nr;
    p.c = nc;
    if (nr === N - 2 && nc === N - 2) {
      over = true;
      const win = p === p1 ? 'Green wins!' : 'Blue wins!';
      window.RewardShell?.showGameOver(win, restart);
    }
  }

  function bindTouch() {
    const CT = window.RewardCoopTouch;
    if (!CT?.setupTouchUi()) return;
    CT.bindDualDpad(
      document.querySelector('.rg-coop-dpad-wrap'),
      (dx, dy) => {
        if (!over) tryMove(p1, m1, dy, dx);
        draw();
      },
      (dx, dy) => {
        if (!over) tryMove(p2, m2, dy, dx);
        draw();
      }
    );
  }

  function restart() {
    m1 = genMaze(1);
    m2 = genMaze(2);
    p1.r = 1;
    p1.c = 1;
    p2.r = N - 2;
    p2.c = N - 2;
    over = false;
    window.RewardShell?.hideGameOver();
    draw();
  }

  bindTouch();
  restart();
  window.RewardGame = { restart };
})();
