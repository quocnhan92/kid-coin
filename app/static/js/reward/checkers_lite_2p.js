(function () {
  const canvas = document.getElementById('ck-canvas');
  const ctx = canvas.getContext('2d');
  const N = 6;
  const cell = canvas.width / N;
  let board = [];
  let turn = 1;
  let sel = null;
  let over = false;

  function initBoard() {
    board = Array.from({ length: N }, (_, r) =>
      Array.from({ length: N }, (_, c) => {
        if (r < 3) return c % 2 === r % 2 ? 2 : 0;
        if (r > 2) return c % 2 === r % 2 ? 1 : 0;
        return 0;
      })
    );
  }

  function inBounds(r, c) {
    return r >= 0 && c >= 0 && r < N && c < N;
  }

  function moves(r, c, p) {
    const out = [];
    const dirs = p === 1 ? [[1, -1], [1, 1]] : [[-1, -1], [-1, 1]];
    dirs.forEach(([dr, dc]) => {
      const nr = r + dr;
      const nc = c + dc;
      if (!inBounds(nr, nc)) return;
      if (board[nr][nc] === 0) out.push([nr, nc, null]);
      else if (board[nr][nc] !== p) {
        const jr = nr + dr;
        const jc = nc + dc;
        if (inBounds(jr, jc) && board[jr][jc] === 0) out.push([jr, jc, [nr, nc]]);
      }
    });
    return out;
  }

  function count(p) {
    return board.flat().filter((x) => x === p).length;
  }

  function draw() {
    ctx.fillStyle = '#422006';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < N; r += 1) {
      for (let c = 0; c < N; c += 1) {
        const x = c * cell;
        const y = r * cell;
        ctx.fillStyle = (r + c) % 2 ? '#78350f' : '#92400e';
        ctx.fillRect(x, y, cell, cell);
        if (board[r][c] === 1) {
          ctx.fillStyle = '#34d399';
          ctx.beginPath();
          ctx.arc(x + cell / 2, y + cell / 2, cell * 0.32, 0, Math.PI * 2);
          ctx.fill();
        } else if (board[r][c] === 2) {
          ctx.fillStyle = '#60a5fa';
          ctx.beginPath();
          ctx.arc(x + cell / 2, y + cell / 2, cell * 0.32, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
    window.RewardShell?.setHud(
      turn === 1 ? 'Green / Xanh lá' : 'Blue / Xanh dương',
      `G:${count(1)} B:${count(2)}`
    );
  }

  function endIfDone() {
    const g = count(1);
    const b = count(2);
    if (g && b) return;
    over = true;
    window.RewardShell?.showGameOver(g ? 'Green wins!' : 'Blue wins!', restart);
  }

  function tap(e) {
    if (over) return;
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    const c = Math.floor(((src.clientX - rect.left) * sx) / cell);
    const r = Math.floor(((src.clientY - rect.top) * sy) / cell);
    if (!inBounds(r, c)) return;
    if (!sel) {
      if (board[r][c] !== turn) return;
      if (!moves(r, c, turn).length) return;
      sel = [r, c];
      draw();
      return;
    }
    const [sr, sc] = sel;
    const mv = moves(sr, sc, turn).find(([tr, tc]) => tr === r && tc === c);
    if (!mv) {
      sel = board[r][c] === turn ? [r, c] : null;
      draw();
      return;
    }
    board[r][c] = turn;
    board[sr][sc] = 0;
    if (mv[2]) board[mv[2][0]][mv[2][1]] = 0;
    sel = null;
    turn = turn === 1 ? 2 : 1;
    draw();
    endIfDone();
  }

  function restart() {
    initBoard();
    turn = 1;
    sel = null;
    over = false;
    window.RewardShell?.hideGameOver();
    draw();
  }

  canvas.addEventListener('click', tap);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    tap(e);
  }, { passive: false });
  initBoard();
  draw();
  window.RewardGame = { restart };
})();
