(function () {
  const SIZE = 8;
  const EMPTY = 0;
  const GREEN = 1;
  const BLUE = 2;
  const DIRS = [
    [-1, 0], [1, 0], [0, -1], [0, 1],
    [-1, -1], [-1, 1], [1, -1], [1, 1],
  ];
  let board = [];
  let turn = GREEN;
  let over = false;
  const canvas = document.getElementById('rev-canvas');
  const ctx = canvas.getContext('2d');
  const cell = canvas.width / SIZE;

  function initBoard() {
    board = Array.from({ length: SIZE }, () => Array(SIZE).fill(EMPTY));
    board[3][3] = BLUE;
    board[3][4] = GREEN;
    board[4][3] = GREEN;
    board[4][4] = BLUE;
    turn = GREEN;
    over = false;
  }

  function inBounds(r, c) {
    return r >= 0 && r < SIZE && c >= 0 && c < SIZE;
  }

  function flipsFor(r, c, player) {
    if (board[r][c] !== EMPTY) return [];
    const opp = player === GREEN ? BLUE : GREEN;
    const all = [];
    DIRS.forEach(([dr, dc]) => {
      const line = [];
      let nr = r + dr;
      let nc = c + dc;
      while (inBounds(nr, nc) && board[nr][nc] === opp) {
        line.push([nr, nc]);
        nr += dr;
        nc += dc;
      }
      if (line.length && inBounds(nr, nc) && board[nr][nc] === player) {
        all.push(...line);
      }
    });
    return all;
  }

  function validMoves(player) {
    const moves = [];
    for (let r = 0; r < SIZE; r += 1) {
      for (let c = 0; c < SIZE; c += 1) {
        if (flipsFor(r, c, player).length) moves.push([r, c]);
      }
    }
    return moves;
  }

  function applyMove(r, c) {
    const flips = flipsFor(r, c, turn);
    if (!flips.length) return false;
    board[r][c] = turn;
    flips.forEach(([fr, fc]) => { board[fr][fc] = turn; });
    return true;
  }

  function count(p) {
    return board.flat().filter((x) => x === p).length;
  }

  function nextTurn() {
    turn = turn === GREEN ? BLUE : GREEN;
    if (!validMoves(turn).length) {
      const other = turn === GREEN ? BLUE : GREEN;
      if (!validMoves(other).length) {
        over = true;
        const g = count(GREEN);
        const b = count(BLUE);
        const msg = g > b ? 'Green wins!' : b > g ? 'Blue wins!' : 'Draw!';
        window.RewardShell?.showGameOver(`${msg} (${g}-${b})`, restartGame);
        return;
      }
      turn = other;
    }
    draw();
  }

  function draw() {
    ctx.fillStyle = '#14532d';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let r = 0; r < SIZE; r += 1) {
      for (let c = 0; c < SIZE; c += 1) {
        ctx.strokeStyle = '#166534';
        ctx.strokeRect(c * cell, r * cell, cell, cell);
        const v = board[r][c];
        if (!v) continue;
        ctx.beginPath();
        ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.38, 0, Math.PI * 2);
        ctx.fillStyle = v === GREEN ? '#34d399' : '#60a5fa';
        ctx.fill();
      }
    }
    const moves = validMoves(turn);
    moves.forEach(([r, c]) => {
      ctx.fillStyle = 'rgba(251, 191, 36, 0.35)';
      ctx.beginPath();
      ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.12, 0, Math.PI * 2);
      ctx.fill();
    });
    const who = turn === GREEN ? 'Xanh lá' : 'Xanh dương';
    window.RewardShell?.setHud(`${who} đi`, `${count(GREEN)} - ${count(BLUE)}`);
  }

  canvas.addEventListener('click', (e) => {
    if (over) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const c = Math.floor(((e.clientX - rect.left) * scaleX) / cell);
    const r = Math.floor(((e.clientY - rect.top) * scaleY) / cell);
    if (!applyMove(r, c)) return;
    nextTurn();
  });

  initBoard();
  draw();

  function restartGame() {
    initBoard();
    draw();
    window.RewardShell?.hideGameOver();
  }
  window.RewardGame = { restart: restartGame };
})();
