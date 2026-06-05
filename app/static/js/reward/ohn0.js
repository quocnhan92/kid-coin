(function () {
  const SIZE = 5;
  let cells = [];
  let rowHints = [];
  let colHints = [];
  const boardEl = document.getElementById('ohn0-board');
  const checkBtn = document.getElementById('ohn0-check');
  const resetBtn = document.getElementById('ohn0-reset');

  function hasTriple(line) {
    for (let i = 0; i <= line.length - 3; i += 1) {
      if (line[i] && line[i + 1] && line[i + 2]) return true;
    }
    return false;
  }

  function validPlacement() {
    for (let r = 0; r < SIZE; r += 1) if (hasTriple(cells[r])) return false;
    for (let c = 0; c < SIZE; c += 1) {
      const col = cells.map((row) => row[c]);
      if (hasTriple(col)) return false;
    }
    return true;
  }

  function genPuzzle() {
    for (let attempt = 0; attempt < 200; attempt += 1) {
      const sol = Array.from({ length: SIZE }, () =>
        Array.from({ length: SIZE }, () => (Math.random() < 0.35 ? 1 : 0))
      );
      cells = sol.map((row) => [...row]);
      if (!validPlacement()) continue;
      rowHints = cells.map((row) => row.reduce((a, b) => a + b, 0));
      colHints = Array.from({ length: SIZE }, (_, c) => cells.reduce((a, row) => a + row[c], 0));
      cells = Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
      return;
    }
    rowHints = [1, 2, 1, 2, 1];
    colHints = [1, 2, 1, 2, 1];
    cells = Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
  }

  function solved() {
    if (!validPlacement()) return false;
    for (let r = 0; r < SIZE; r += 1) {
      if (cells[r].reduce((a, b) => a + b, 0) !== rowHints[r]) return false;
    }
    for (let c = 0; c < SIZE; c += 1) {
      if (cells.reduce((a, row) => a + row[c], 0) !== colHints[c]) return false;
    }
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
        if (cells[r][c]) btn.classList.add('oh-mark');
        btn.addEventListener('click', () => {
          cells[r][c] = cells[r][c] ? 0 : 1;
          if (!validPlacement()) {
            cells[r][c] = cells[r][c] ? 0 : 1;
            alert('No 3 in a row! / Không được 3 ô liên tiếp!');
            return;
          }
          render();
        });
        boardEl.appendChild(btn);
      }
    }
    window.RewardShell?.setHud('0h n0', solved() ? '✓ Done!' : 'No triples');
  }

  checkBtn?.addEventListener('click', () => {
    if (solved()) window.RewardShell?.showGameOver('Correct! / Đúng rồi!', () => { genPuzzle(); render(); });
    else window.RewardShell?.showGameOver('Keep trying / Thử tiếp nhé', null);
  });
  resetBtn?.addEventListener('click', () => { genPuzzle(); render(); window.RewardShell?.hideGameOver(); });
  genPuzzle();
  render();
  window.RewardGame = { restart: () => { genPuzzle(); render(); window.RewardShell?.hideGameOver(); } };
})();
