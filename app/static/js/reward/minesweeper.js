(function () {
  const ROWS = 10;
  const COLS = 10;
  const MINES = 12;
  let board = [];
  let revealed = 0;
  let flagMode = false;
  let over = false;
  let started = false;

  const boardEl = document.getElementById('ms-board');
  const flagBtn = document.getElementById('ms-flag-mode');
  const resetBtn = document.getElementById('ms-reset');

  const NUM_COLORS = ['', '#60a5fa', '#34d399', '#f87171', '#a78bfa', '#fbbf24', '#22d3ee'];

  function neighbors(r, c) {
    const out = [];
    for (let dr = -1; dr <= 1; dr += 1) {
      for (let dc = -1; dc <= 1; dc += 1) {
        if (!dr && !dc) continue;
        const nr = r + dr;
        const nc = c + dc;
        if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) out.push([nr, nc]);
      }
    }
    return out;
  }

  function countAdj(r, c) {
    return neighbors(r, c).filter(([nr, nc]) => board[nr][nc].mine).length;
  }

  function buildBoard(safeR, safeC) {
    board = Array.from({ length: ROWS }, () =>
      Array.from({ length: COLS }, () => ({ mine: false, open: false, flag: false, n: 0 }))
    );
    let placed = 0;
    while (placed < MINES) {
      const r = Math.floor(Math.random() * ROWS);
      const c = Math.floor(Math.random() * COLS);
      if (board[r][c].mine) continue;
      if (Math.abs(r - safeR) <= 1 && Math.abs(c - safeC) <= 1) continue;
      board[r][c].mine = true;
      placed += 1;
    }
    for (let r = 0; r < ROWS; r += 1) {
      for (let c = 0; c < COLS; c += 1) {
        if (!board[r][c].mine) board[r][c].n = countAdj(r, c);
      }
    }
    revealed = 0;
    over = false;
  }

  function updateHud() {
    if (!started) {
      window.RewardShell?.setHud('Tap a cell / Chạm ô để bắt đầu', '');
      return;
    }
    const flags = board.flat().filter((c) => c.flag).length;
    window.RewardShell?.setHud(`Mines: ${MINES}`, `Flags: ${flags}`);
  }

  function paintCell(btn, cell) {
    if (cell.open) {
      btn.classList.add('revealed');
      btn.disabled = true;
      if (cell.mine) {
        btn.textContent = '💥';
        btn.style.background = '#dc2626';
      } else if (cell.n > 0) {
        btn.textContent = String(cell.n);
        btn.style.color = NUM_COLORS[cell.n] || '#f1f0ff';
      } else {
        btn.textContent = '';
      }
      return;
    }
    btn.classList.toggle('flagged', cell.flag);
    btn.textContent = '';
  }

  function render() {
    boardEl.innerHTML = '';
    boardEl.style.gridTemplateColumns = `repeat(${COLS}, 1fr)`;
    for (let r = 0; r < ROWS; r += 1) {
      for (let c = 0; c < COLS; c += 1) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'rg-cell';
        btn.setAttribute('aria-label', `cell ${r + 1}-${c + 1}`);
        if (started) paintCell(btn, board[r][c]);
        btn.addEventListener('click', () => onCell(r, c));
        boardEl.appendChild(btn);
      }
    }
    updateHud();
  }

  function flood(r, c) {
    const stack = [[r, c]];
    while (stack.length) {
      const [cr, cc] = stack.pop();
      const cell = board[cr][cc];
      if (cell.open || cell.flag) continue;
      cell.open = true;
      revealed += 1;
      if (cell.n === 0) neighbors(cr, cc).forEach(([nr, nc]) => stack.push([nr, nc]));
    }
  }

  function winCheck() {
    if (revealed === ROWS * COLS - MINES) {
      over = true;
      window.RewardShell?.showGameOver('You win! / Bạn thắng!', reset);
    }
  }

  function onCell(r, c) {
    if (over) return;

    if (flagMode) {
      if (!started) return;
      const flagged = board[r][c];
      if (!flagged.open) flagged.flag = !flagged.flag;
      render();
      return;
    }

    if (!started) {
      buildBoard(r, c);
      started = true;
    }

    const cell = board[r][c];

    if (cell.flag || cell.open) return;

    if (cell.mine) {
      over = true;
      board.forEach((row) => row.forEach((x) => { x.open = true; }));
      render();
      window.RewardShell?.showGameOver('Boom! / Trúng mìn!', reset);
      return;
    }

    flood(r, c);
    render();
    winCheck();
  }

  function reset() {
    board = [];
    revealed = 0;
    over = false;
    started = false;
    flagMode = false;
    if (flagBtn) {
      flagBtn.textContent = 'Flag / Cờ: OFF';
      flagBtn.classList.remove('rg-btn-primary');
    }
    render();
  }

  flagBtn?.addEventListener('click', () => {
    flagMode = !flagMode;
    flagBtn.textContent = flagMode ? 'Flag / Cờ: ON' : 'Flag / Cờ: OFF';
    flagBtn.classList.toggle('rg-btn-primary', flagMode);
  });
  resetBtn?.addEventListener('click', reset);
  reset();
  window.RewardGame = { restart: reset };
})();
