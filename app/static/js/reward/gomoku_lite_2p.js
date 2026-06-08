(function () {
  const canvas = document.getElementById('gm-canvas');
  const ctx = canvas.getContext('2d');
  const N = 9;
  const cell = canvas.width / N;
  let board = Array.from({ length: N }, () => Array(N).fill(0));
  let turn = 1;
  let over = false;
  let undoLeft = 1;

  function checkWin(r, c) {
    const p = board[r][c];
    const dirs = [[1, 0], [0, 1], [1, 1], [1, -1]];
    return dirs.some(([dr, dc]) => {
      let n = 1;
      for (let s = 1; s < 5; s += 1) {
        const nr = r + dr * s;
        const nc = c + dc * s;
        if (nr < 0 || nr >= N || nc < 0 || nc >= N || board[nr][nc] !== p) break;
        n += 1;
      }
      for (let s = 1; s < 5; s += 1) {
        const nr = r - dr * s;
        const nc = c - dc * s;
        if (nr < 0 || nr >= N || nc < 0 || nc >= N || board[nr][nc] !== p) break;
        n += 1;
      }
      return n >= 5;
    });
  }

  function draw() {
    ctx.fillStyle = '#fef3c7';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < N; r += 1) {
      for (let c = 0; c < N; c += 1) {
        ctx.strokeStyle = '#92400e';
        ctx.strokeRect(c * cell, r * cell, cell, cell);
        if (board[r][c] === 1) {
          ctx.fillStyle = '#34d399';
          ctx.beginPath();
          ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.38, 0, Math.PI * 2);
          ctx.fill();
        } else if (board[r][c] === 2) {
          ctx.fillStyle = '#1e293b';
          ctx.beginPath();
          ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.38, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }
    window.RewardShell?.setHud(
      turn === 1 ? 'Green / Xanh lá' : 'Blue / Xanh dương',
      `Undo left: ${undoLeft}`
    );
  }

  let lastMove = null;

  function tap(e) {
    if (over) return;
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    const c = Math.floor(((src.clientX - rect.left) * sx) / cell);
    const r = Math.floor(((src.clientY - rect.top) * sy) / cell);
    if (r < 0 || c < 0 || r >= N || c >= N || board[r][c]) return;
    board[r][c] = turn;
    lastMove = [r, c, turn];
    if (checkWin(r, c)) {
      over = true;
      draw();
      window.RewardShell?.showGameOver(
        turn === 1 ? 'Green wins!' : 'Blue wins!',
        restart
      );
      return;
    }
    turn = turn === 1 ? 2 : 1;
    draw();
  }

  document.getElementById('gm-undo')?.addEventListener('click', () => {
    if (!undoLeft || !lastMove || over) return;
    const [r, c] = lastMove;
    board[r][c] = 0;
    turn = lastMove[2];
    lastMove = null;
    undoLeft -= 1;
    draw();
  });

  function restart() {
    board = Array.from({ length: N }, () => Array(N).fill(0));
    turn = 1;
    over = false;
    undoLeft = 1;
    lastMove = null;
    window.RewardShell?.hideGameOver();
    draw();
  }

  canvas.addEventListener('click', tap);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    tap(e);
  }, { passive: false });
  draw();
  window.RewardGame = { restart };
})();
