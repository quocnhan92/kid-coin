(function () {
  const canvas = document.getElementById('ttt-canvas');
  const ctx = canvas.getContext('2d');
  const SIZE = 3;
  const cell = canvas.width / SIZE;
  let board = Array(9).fill(0);
  let turn = 1;
  let over = false;

  function lines() {
    return [
      [0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6],
    ];
  }

  function winner() {
    for (const [a, b, c] of lines()) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) return board[a];
    }
    return board.every(Boolean) ? -1 : 0;
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 4;
    for (let i = 1; i < SIZE; i += 1) {
      ctx.beginPath();
      ctx.moveTo(i * cell, 0);
      ctx.lineTo(i * cell, canvas.height);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(0, i * cell);
      ctx.lineTo(canvas.width, i * cell);
      ctx.stroke();
    }
    board.forEach((v, i) => {
      const x = (i % SIZE) * cell + cell / 2;
      const y = Math.floor(i / SIZE) * cell + cell / 2;
      ctx.font = 'bold 48px Nunito,sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = v === 1 ? '#34d399' : '#60a5fa';
      ctx.fillText(v === 1 ? 'X' : v === 2 ? 'O' : '', x, y);
    });
    window.RewardShell?.setHud(
      over ? 'Done' : turn === 1 ? 'Green (X)' : 'Blue (O)',
      'Tap a cell / Chạm ô trống'
    );
  }

  function tap(e) {
    if (over) return;
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    const cx = (src.clientX - rect.left) * sx;
    const cy = (src.clientY - rect.top) * sy;
    const col = Math.floor(cx / cell);
    const row = Math.floor(cy / cell);
    const i = row * SIZE + col;
    if (board[i]) return;
    board[i] = turn;
    const w = winner();
    if (w !== 0) {
      over = true;
      draw();
      const msg =
        w === -1
          ? 'Draw! / Hòa!'
          : w === 1
            ? 'Green wins! / Xanh lá thắng!'
            : 'Blue wins! / Xanh dương thắng!';
      window.RewardShell?.showGameOver(msg, restart);
      return;
    }
    turn = turn === 1 ? 2 : 1;
    draw();
  }

  function restart() {
    board = Array(9).fill(0);
    turn = 1;
    over = false;
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
