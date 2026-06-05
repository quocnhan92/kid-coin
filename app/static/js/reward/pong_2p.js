(function () {
  const canvas = document.getElementById('pong-canvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const keys = {};
  let scoreL = 0;
  let scoreR = 0;

  const BALL_SPEED_X = 2.4;
  const BALL_SPEED_Y = 1.8;
  const BOUNCE_MULT = 1.02;
  const ball = { x: W / 2, y: H / 2, vx: BALL_SPEED_X, vy: BALL_SPEED_Y, r: 8 };
  const padL = { x: 16, y: H / 2 - 40, w: 12, h: 80, vy: 0 };
  const padR = { x: W - 28, y: H / 2 - 40, w: 12, h: 80, vy: 0 };

  function capBallSpeed() {
    const maxX = 3.2;
    const maxY = 2.4;
    ball.vx = Math.max(-maxX, Math.min(maxX, ball.vx));
    ball.vy = Math.max(-maxY, Math.min(maxY, ball.vy));
  }

  function resetBall(toRight) {
    ball.x = W / 2;
    ball.y = H / 2;
    ball.vx = (toRight ? 1 : -1) * BALL_SPEED_X;
    ball.vy = (Math.random() > 0.5 ? 1 : -1) * BALL_SPEED_Y;
  }

  function draw() {
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, W, H);
    ctx.setLineDash([6, 8]);
    ctx.strokeStyle = '#334155';
    ctx.beginPath();
    ctx.moveTo(W / 2, 0);
    ctx.lineTo(W / 2, H);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#34d399';
    ctx.fillRect(padL.x, padL.y, padL.w, padL.h);
    ctx.fillStyle = '#60a5fa';
    ctx.fillRect(padR.x, padR.y, padR.w, padR.h);
    ctx.fillStyle = '#fbbf24';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fill();
    window.RewardShell?.setHud(`Xanh lá ${scoreL}`, `Xanh dương ${scoreR}`);
  }

  function step() {
    padL.y += padL.vy;
    padR.y += padR.vy;
    padL.y = Math.max(0, Math.min(H - padL.h, padL.y));
    padR.y = Math.max(0, Math.min(H - padR.h, padR.y));
    ball.x += ball.vx;
    ball.y += ball.vy;
    if (ball.y < ball.r || ball.y > H - ball.r) ball.vy *= -1;
    if (ball.x < ball.r) {
      scoreR += 1;
      resetBall(true);
    }
    if (ball.x > W - ball.r) {
      scoreL += 1;
      resetBall(false);
    }
    if (
      ball.x - ball.r < padL.x + padL.w &&
      ball.y > padL.y &&
      ball.y < padL.y + padL.h &&
      ball.vx < 0
    ) {
      ball.vx *= -BOUNCE_MULT;
      capBallSpeed();
      ball.x = padL.x + padL.w + ball.r;
    }
    if (
      ball.x + ball.r > padR.x &&
      ball.y > padR.y &&
      ball.y < padR.y + padR.h &&
      ball.vx > 0
    ) {
      ball.vx *= -BOUNCE_MULT;
      capBallSpeed();
      ball.x = padR.x - ball.r;
    }
    draw();
    requestAnimationFrame(step);
  }

  document.addEventListener('keydown', (e) => {
    keys[e.code] = true;
    padL.vy = keys.KeyW ? -6 : keys.KeyS ? 6 : 0;
    padR.vy = keys.ArrowUp ? -6 : keys.ArrowDown ? 6 : 0;
  });
  document.addEventListener('keyup', (e) => {
    keys[e.code] = false;
    padL.vy = keys.KeyW ? -6 : keys.KeyS ? 6 : 0;
    padR.vy = keys.ArrowUp ? -6 : keys.ArrowDown ? 6 : 0;
  });

  resetBall(Math.random() > 0.5);
  requestAnimationFrame(step);

  function restartGame() {
    scoreL = 0;
    scoreR = 0;
    padL.y = H / 2 - 40;
    padR.y = H / 2 - 40;
    resetBall(Math.random() > 0.5);
    window.RewardShell?.hideGameOver();
  }
  window.RewardGame = { restart: restartGame };
})();
