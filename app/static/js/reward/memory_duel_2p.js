(function () {
  const canvas = document.getElementById('md-canvas');
  const ctx = canvas.getContext('2d');
  const PAIRS = 8;
  const COLS = 4;
  const cell = canvas.width / COLS;
  const ROWS = 4;
  const emojis = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼'];
  let cards = [];
  let open = [];
  let turn = 1;
  let scores = [0, 0];
  let lock = false;

  function shuffle(a) {
    for (let i = a.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function build() {
    const deck = shuffle([...emojis, ...emojis]);
    cards = deck.map((e, i) => ({ id: i, e, up: false, matched: false }));
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    cards.forEach((c, i) => {
      const x = (i % COLS) * cell;
      const y = Math.floor(i / COLS) * cell;
      ctx.fillStyle = c.matched ? '#1e293b' : c.up ? '#334155' : '#475569';
      ctx.fillRect(x + 4, y + 4, cell - 8, cell - 8);
      if (c.up || c.matched) {
        ctx.font = `${cell * 0.45}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(c.e, x + cell / 2, y + cell / 2);
      }
    });
    window.RewardShell?.setHud(
      turn === 1 ? 'Green turn / Lượt xanh lá' : 'Blue turn / Lượt xanh dương',
      `Green ${scores[0]} · Blue ${scores[1]}`
    );
  }

  function flip(i) {
    if (lock || cards[i].up || cards[i].matched) return;
    cards[i].up = true;
    open.push(i);
    draw();
    if (open.length < 2) return;
    lock = true;
    const [a, b] = open;
    if (cards[a].e === cards[b].e) {
      cards[a].matched = cards[b].matched = true;
      scores[turn - 1] += 1;
      open = [];
      lock = false;
      if (cards.every((c) => c.matched)) {
        const msg =
          scores[0] > scores[1]
            ? 'Green wins!'
            : scores[1] > scores[0]
              ? 'Blue wins!'
              : 'Draw! / Hòa!';
        window.RewardShell?.showGameOver(msg, restart);
      }
      draw();
      return;
    }
    setTimeout(() => {
      cards[a].up = cards[b].up = false;
      open = [];
      turn = turn === 1 ? 2 : 1;
      lock = false;
      draw();
    }, 700);
  }

  function tap(e) {
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    const cx = (src.clientX - rect.left) * sx;
    const cy = (src.clientY - rect.top) * sy;
    const col = Math.floor(cx / cell);
    const row = Math.floor(cy / cell);
    if (row < 0 || row >= ROWS || col < 0 || col >= COLS) return;
    flip(row * COLS + col);
  }

  function restart() {
    build();
    open = [];
    turn = 1;
    scores = [0, 0];
    lock = false;
    window.RewardShell?.hideGameOver();
    draw();
  }

  canvas.addEventListener('click', tap);
  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    tap(e);
  }, { passive: false });
  build();
  draw();
  window.RewardGame = { restart };
})();
