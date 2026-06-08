(function () {
  const canvas = document.getElementById('cc-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const padL = { y: H / 2, w: 80, h: 14 };
  const padR = { y: H / 2, w: 80, h: 14 };
  let stars = [];
  let score = 0;
  let missed = 0;
  let tick = 0;

  function spawn() {
    stars.push({ x: 40 + Math.random() * (W - 80), y: -10, r: 8 + Math.random() * 6, vy: 1.2 + Math.random() * 1.5 });
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#34d399';
    ctx.fillRect(24, padL.y - padL.h / 2, padL.w, padL.h);
    ctx.fillStyle = '#60a5fa';
    ctx.fillRect(W - 24 - padR.w, padR.y - padR.h / 2, padR.w, padR.h);
    ctx.fillStyle = '#fbbf24';
    stars.forEach((s) => {
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    });
    window.RewardShell?.setHud(`Team score: ${score}`, `Missed: ${missed}/10`);
  }

  function step() {
    tick += 1;
    if (tick % 45 === 0) spawn();
    stars = stars.filter((s) => {
      s.y += s.vy;
      const hitL = s.y > padL.y - 20 && s.y < padL.y + 20 && s.x > 24 && s.x < 24 + padL.w;
      const hitR = s.y > padR.y - 20 && s.y < padR.y + 20 && s.x > W - 24 - padR.w && s.x < W - 24;
      if (hitL || hitR) {
        score += 1;
        return false;
      }
      if (s.y > H + 20) {
        missed += 1;
        return false;
      }
      return true;
    });
    if (missed >= 10) {
      window.RewardShell?.showGameOver(`Team caught ${score} stars! / Bắt được ${score} sao!`, restart);
      return;
    }
    draw();
    requestAnimationFrame(step);
  }

  function setPadY(pad, ratio) {
    pad.y = 30 + ratio * (H - 60);
  }

  function bindTouch() {
    const CT = window.RewardCoopTouch;
    if (!CT?.setupTouchUi()) return;
    const zL = document.getElementById('cc-zone-l');
    const zR = document.getElementById('cc-zone-r');
    if (zL) CT.bindTouchDrag(zL, (r) => setPadY(padL, r));
    if (zR) CT.bindTouchDrag(zR, (r) => setPadY(padR, r));
  }

  function restart() {
    stars = [];
    score = 0;
    missed = 0;
    tick = 0;
    padL.y = H / 2;
    padR.y = H / 2;
    window.RewardShell?.hideGameOver();
    requestAnimationFrame(step);
  }

  bindTouch();
  restart();
  window.RewardGame = { restart };
})();
