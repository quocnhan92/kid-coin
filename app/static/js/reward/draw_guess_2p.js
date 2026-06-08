(function () {
  const canvas = document.getElementById('dg-canvas');
  const optsEl = document.getElementById('dg-options');
  const WORDS = [
    { en: 'cat', vi: 'mèo' },
    { en: 'dog', vi: 'chó' },
    { en: 'sun', vi: 'mặt trời' },
    { en: 'book', vi: 'sách' },
    { en: 'fish', vi: 'cá' },
    { en: 'tree', vi: 'cây' },
    { en: 'ball', vi: 'bóng' },
    { en: 'star', vi: 'sao' },
  ];
  let word = WORDS[0];
  let drawer = 1;
  let drawing = false;
  let last = null;
  let round = 0;
  let scores = [0, 0];

  function pickWord() {
    word = WORDS[Math.floor(Math.random() * WORDS.length)];
    const wrong = WORDS.filter((w) => w.en !== word.en).sort(() => Math.random() - 0.5).slice(0, 3);
    const choices = [...wrong, word].sort(() => Math.random() - 0.5);
    if (!optsEl) return;
    optsEl.innerHTML = '';
    choices.forEach((w) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'rg-btn rg-dg-opt';
      b.textContent = `${w.en} / ${w.vi}`;
      b.addEventListener('click', () => guess(w.en));
      optsEl.appendChild(b);
    });
  }

  function clearCanvas() {
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  function updateHud() {
    window.RewardShell?.setHud(
      drawer === 1 ? 'Green draws / Xanh lá vẽ' : 'Blue draws / Xanh dương vẽ',
      `G:${scores[0]} B:${scores[1]} · Round ${round + 1}`
    );
  }

  function guess(en) {
    const guesser = drawer === 1 ? 2 : 1;
    if (en === word.en) scores[guesser - 1] += 1;
    nextRound();
  }

  function nextRound() {
    round += 1;
    drawer = drawer === 1 ? 2 : 1;
    clearCanvas();
    pickWord();
    updateHud();
    if (round >= 6) {
      const msg =
        scores[0] > scores[1] ? 'Green wins!' : scores[1] > scores[0] ? 'Blue wins!' : 'Draw!';
      window.RewardShell?.showGameOver(msg, restart);
    }
  }

  function pos(e) {
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width;
    const sy = canvas.height / rect.height;
    const src = e.touches?.[0] || e;
    return { x: (src.clientX - rect.left) * sx, y: (src.clientY - rect.top) * sy };
  }

  function bindDraw() {
    const ctx = canvas.getContext('2d');
    const down = (e) => {
      if (drawer !== 1 && drawer !== 2) return;
      e.preventDefault();
      drawing = true;
      last = pos(e);
    };
    const move = (e) => {
      if (!drawing) return;
      e.preventDefault();
      const p = pos(e);
      ctx.strokeStyle = drawer === 1 ? '#34d399' : '#60a5fa';
      ctx.lineWidth = 4;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(last.x, last.y);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      last = p;
    };
    const up = () => {
      drawing = false;
    };
    canvas.addEventListener('mousedown', down);
    canvas.addEventListener('mousemove', move);
    window.addEventListener('mouseup', up);
    canvas.addEventListener('touchstart', down, { passive: false });
    canvas.addEventListener('touchmove', move, { passive: false });
    canvas.addEventListener('touchend', up);
  }

  function restart() {
    scores = [0, 0];
    round = 0;
    drawer = 1;
    window.RewardShell?.hideGameOver();
    clearCanvas();
    pickWord();
    updateHud();
  }

  bindDraw();
  restart();
  window.RewardGame = { restart };
})();
