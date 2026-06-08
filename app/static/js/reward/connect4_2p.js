(function () {
  const canvas = document.getElementById('c4-canvas');
  const colsEl = document.getElementById('c4-cols');
  const ctx = canvas.getContext('2d');
  const COLS = 7;
  const ROWS = 6;
  const R = 26;
  let board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
  let turn = 1;
  let over = false;

  function drop(col) {
    if (over) return;
    for (let r = ROWS - 1; r >= 0; r -= 1) {
      if (board[r][col]) continue;
      board[r][col] = turn;
      if (checkWin(r, col)) {
        over = true;
        draw();
        window.RewardShell?.showGameOver(
          turn === 1 ? 'Green wins! / Xanh lá thắng!' : 'Blue wins! / Xanh dương thắng!',
          restart
        );
        return;
      }
      turn = turn === 1 ? 2 : 1;
      draw();
      return;
    }
  }

  function checkWin(r, c) {
    const p = board[r][c];
    const dirs = [[1, 0], [0, 1], [1, 1], [1, -1]];
    return dirs.some(([dr, dc]) => {
      let n = 1;
      for (let s = 1; s < 4; s += 1) {
        const nr = r + dr * s;
        const nc = c + dc * s;
        if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS || board[nr][nc] !== p) break;
        n += 1;
      }
      for (let s = 1; s < 4; s += 1) {
        const nr = r - dr * s;
        const nc = c - dc * s;
        if (nr < 0 || nr >= ROWS || nc < 0 || nc >= COLS || board[nr][nc] !== p) break;
        n += 1;
      }
      return n >= 4;
    });
  }

  function draw() {
    ctx.fillStyle = '#1e3a8a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < ROWS; r += 1) {
      for (let c = 0; c < COLS; c += 1) {
        const x = 36 + c * (R * 2 + 8);
        const y = 36 + r * (R * 2 + 8);
        ctx.beginPath();
        ctx.arc(x, y, R, 0, Math.PI * 2);
        ctx.fillStyle = board[r][c] === 1 ? '#34d399' : board[r][c] === 2 ? '#60a5fa' : '#0f172a';
        ctx.fill();
      }
    }
    window.RewardShell?.setHud(
      turn === 1 ? 'Green turn / Lượt xanh lá' : 'Blue turn / Lượt xanh dương',
      over ? 'Game over' : 'Tap column below / Chạm cột bên dưới'
    );
  }

  function buildCols() {
    if (!colsEl) return;
    colsEl.innerHTML = '';
    for (let c = 0; c < COLS; c += 1) {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'rg-btn rg-c4-col';
      b.textContent = c + 1;
      b.addEventListener('click', () => drop(c));
      colsEl.appendChild(b);
    }
  }

  function restart() {
    board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    turn = 1;
    over = false;
    window.RewardShell?.hideGameOver();
    draw();
  }

  buildCols();
  draw();
  window.RewardGame = { restart };
})();
