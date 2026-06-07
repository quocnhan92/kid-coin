(function () {
  const canvas = document.getElementById('ah-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const keys = {};
  let scoreL = 0;
  let scoreR = 0;

  const PUCK_SPEED_X = 2.5;
  const PUCK_SPEED_Y = 1.25;
  const MALLET_SPEED = 3;
  const BOUNCE_MULT = 1.02;
  const MAX_PUCK_SPEED = 3.5;

  const puck = { x: W / 2, y: H / 2, vx: PUCK_SPEED_X, vy: PUCK_SPEED_Y, r: 10 };
  const malletL = { x: 70, y: H / 2, r: 28 };
  const malletR = { x: W - 70, y: H / 2, r: 28 };

  function capPuckSpeed() {
    const sp = Math.hypot(puck.vx, puck.vy);
    if (sp <= MAX_PUCK_SPEED) return;
    puck.vx = (puck.vx / sp) * MAX_PUCK_SPEED;
    puck.vy = (puck.vy / sp) * MAX_PUCK_SPEED;
  }

  function resetPuck(toRight) {
    puck.x = W / 2;
    puck.y = H / 2;
    puck.vx = (toRight ? 1 : -1) * PUCK_SPEED_X;
    puck.vy = (Math.random() > 0.5 ? 1 : -1) * PUCK_SPEED_Y;
  }

  function drawTable() {
    ctx.fillStyle = '#1e3a5f';
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 4;
    ctx.strokeRect(8, 8, W - 16, H - 16);
    ctx.beginPath();
    ctx.arc(W / 2, H / 2, 40, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = 'rgba(52, 211, 153, 0.85)';
    ctx.beginPath();
    ctx.arc(malletL.x, malletL.y, malletL.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'rgba(96, 165, 250, 0.85)';
    ctx.beginPath();
    ctx.arc(malletR.x, malletR.y, malletR.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#f8fafc';
    ctx.beginPath();
    ctx.arc(puck.x, puck.y, puck.r, 0, Math.PI * 2);
    ctx.fill();
    window.RewardShell?.setHud(`Xanh lá ${scoreL}`, `Xanh dương ${scoreR}`);
  }

  function collideMallet(m) {
    const dx = puck.x - m.x;
    const dy = puck.y - m.y;
    const dist = Math.hypot(dx, dy);
    if (dist > m.r + puck.r) return;
    const nx = dx / (dist || 1);
    const ny = dy / (dist || 1);
    puck.x = m.x + nx * (m.r + puck.r);
    puck.y = m.y + ny * (m.r + puck.r);
    const speed = Math.hypot(puck.vx, puck.vy) * BOUNCE_MULT;
    puck.vx = nx * speed;
    puck.vy = ny * speed;
    capPuckSpeed();
  }

  function step() {
    if (keys.KeyW) malletL.y -= MALLET_SPEED;
    if (keys.KeyS) malletL.y += MALLET_SPEED;
    if (keys.ArrowUp) malletR.y -= MALLET_SPEED;
    if (keys.ArrowDown) malletR.y += MALLET_SPEED;
    malletL.y = Math.max(40, Math.min(H - 40, malletL.y));
    malletR.y = Math.max(40, Math.min(H - 40, malletR.y));
    puck.x += puck.vx;
    puck.y += puck.vy;
    if (puck.y < puck.r + 10 || puck.y > H - puck.r - 10) puck.vy *= -1;
    collideMallet(malletL);
    collideMallet(malletR);
    if (puck.x < 0) {
      scoreR += 1;
      resetPuck(true);
    }
    if (puck.x > W) {
      scoreL += 1;
      resetPuck(false);
    }
    drawTable();
    requestAnimationFrame(step);
  }

  document.addEventListener('keydown', (e) => { keys[e.code] = true; });
  document.addEventListener('keyup', (e) => { keys[e.code] = false; });

  function clampMallet(m, isLeft) {
    if (isLeft) {
      m.x = Math.max(40, Math.min(W / 2 - 24, m.x));
    } else {
      m.x = Math.max(W / 2 + 24, Math.min(W - 40, m.x));
    }
    m.y = Math.max(40, Math.min(H - 40, m.y));
  }

  function bindTouch() {
    const CT = window.RewardCoopTouch;
    if (!CT?.setupTouchUi()) return;
    const zL = document.getElementById('ah-zone-l');
    const zR = document.getElementById('ah-zone-r');
    if (zL) {
      CT.bindTouchDrag(zL, (ratio) => {
        malletL.y = 40 + ratio * (H - 80);
        clampMallet(malletL, true);
      });
    }
    if (zR) {
      CT.bindTouchDrag(zR, (ratio) => {
        malletR.y = 40 + ratio * (H - 80);
        clampMallet(malletR, false);
      });
    }
  }
  bindTouch();
  resetPuck(true);
  requestAnimationFrame(step);

  function restartGame() {
    scoreL = 0;
    scoreR = 0;
    malletL.y = H / 2;
    malletR.y = H / 2;
    resetPuck(true);
    window.RewardShell?.hideGameOver();
  }
  window.RewardGame = { restart: restartGame };
})();
