(function () {
  const SIZE = 5;
  let cells = [];
  let rowHints = [];
  let colHints = [];
  const boardEl = document.getElementById('ohh1-board');
  const checkBtn = document.getElementById('ohh1-check');
  const resetBtn = document.getElementById('ohh1-reset');

  function genPuzzle() {
    const sol = Array.from({ length: SIZE }, () =>
      Array.from({ length: SIZE }, () => (Math.random() < 0.42 ? 1 : 0))
    );
    rowHints = sol.map((row) => row.reduce((a, b) => a + b, 0));
    colHints = Array.from({ length: SIZE }, (_, c) => sol.reduce((a, row) => a + row[c], 0));
    cells = Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
  }

  function rowSum(r) {
    return cells[r].reduce((a, b) => a + b, 0);
  }

  function colSum(c) {
    return cells.reduce((a, row) => a + row[c], 0);
  }

  function solved() {
    for (let r = 0; r < SIZE; r += 1) if (rowSum(r) !== rowHints[r]) return false;
    for (let c = 0; c < SIZE; c += 1) if (colSum(c) !== colHints[c]) return false;
    return true;
  }

  function render() {
    boardEl.innerHTML = '';
    boardEl.style.gridTemplateColumns = `32px repeat(${SIZE}, 36px)`;
    boardEl.appendChild(document.createElement('div'));
    colHints.forEach((h) => {
      const el = document.createElement('div');
      el.className = 'oh-hint';
      el.textContent = h;
      boardEl.appendChild(el);
    });
    for (let r = 0; r < SIZE; r += 1) {
      const rh = document.createElement('div');
      rh.className = 'oh-hint';
      rh.textContent = rowHints[r];
      boardEl.appendChild(rh);
      for (let c = 0; c < SIZE; c += 1) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'rg-cell oh-cell';
        if (cells[r][c]) {
          btn.classList.add('oh-on');
          btn.textContent = '';
        }
        btn.addEventListener('click', () => {
          cells[r][c] = cells[r][c] ? 0 : 1;
          render();
        });
        boardEl.appendChild(btn);
      }
    }
    window.RewardShell?.setHud('0h h1', solved() ? '✓ Done!' : 'Fill rows & cols');
  }

  checkBtn?.addEventListener('click', () => {
    if (solved()) window.RewardShell?.showGameOver('Correct! / Đúng rồi!', () => { genPuzzle(); render(); });
    else window.RewardShell?.showGameOver('Not yet / Chưa đúng — xem gợi ý', null);
  });
  resetBtn?.addEventListener('click', () => { genPuzzle(); render(); window.RewardShell?.hideGameOver(); });
  genPuzzle();
  render();
  window.RewardGame = { restart: () => { genPuzzle(); render(); window.RewardShell?.hideGameOver(); } };
})();
