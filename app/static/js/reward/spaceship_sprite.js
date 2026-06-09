(function () {
  function drawFlame(ctx, now) {
    const flicker = Math.sin(now * 0.028) * 2.5;
    const g = ctx.createLinearGradient(0, 11, 0, 30 + flicker);
    g.addColorStop(0, '#fde047');
    g.addColorStop(0.45, '#f97316');
    g.addColorStop(1, 'rgba(249,115,22,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.moveTo(-6, 11);
    ctx.quadraticCurveTo(-3, 22 + flicker, 0, 28 + flicker);
    ctx.quadraticCurveTo(3, 22 + flicker, 6, 11);
    ctx.closePath();
    ctx.fill();
  }

  function drawWings(ctx) {
    ctx.fillStyle = '#64748b';
    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-7, 2);
    ctx.lineTo(-24, 13);
    ctx.lineTo(-20, 17);
    ctx.lineTo(-5, 9);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(7, 2);
    ctx.lineTo(24, 13);
    ctx.lineTo(20, 17);
    ctx.lineTo(5, 9);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(-22, 13, 5, 2);
    ctx.fillRect(17, 13, 5, 2);
  }

  function drawBody(ctx) {
    const g = ctx.createLinearGradient(-14, -18, 14, 14);
    g.addColorStop(0, '#94a3b8');
    g.addColorStop(0.35, '#f8fafc');
    g.addColorStop(0.7, '#cbd5e1');
    g.addColorStop(1, '#475569');
    ctx.fillStyle = g;
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, -22);
    ctx.bezierCurveTo(9, -12, 11, 4, 7, 13);
    ctx.lineTo(-7, 13);
    ctx.bezierCurveTo(-11, 4, -9, -12, 0, -22);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.moveTo(-2, -4);
    ctx.lineTo(2, -4);
    ctx.lineTo(1.5, 12);
    ctx.lineTo(-1.5, 12);
    ctx.closePath();
    ctx.fill();
  }

  function drawCockpit(ctx) {
    const g = ctx.createRadialGradient(-2, -10, 1, 0, -7, 8);
    g.addColorStop(0, '#a5f3fc');
    g.addColorStop(0.55, '#06b6d4');
    g.addColorStop(1, '#0e7490');
    ctx.fillStyle = g;
    ctx.strokeStyle = '#155e75';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.ellipse(0, -7, 5.5, 7.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,0.65)';
    ctx.beginPath();
    ctx.ellipse(-2.5, -10, 2, 3.5, -0.5, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawGuns(ctx) {
    ctx.fillStyle = '#334155';
    ctx.fillRect(-9, 6, 3, 8);
    ctx.fillRect(6, 6, 3, 8);
    ctx.fillStyle = '#facc15';
    ctx.fillRect(-8.5, 5, 2, 2);
    ctx.fillRect(6.5, 5, 2, 2);
  }

  function draw(ctx, x, y, opts) {
    const scale = opts?.scale ?? 1;
    const tilt = opts?.tilt ?? 0;
    const flame = opts?.flame !== false;
    const now = performance.now();

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(tilt);
    ctx.scale(scale, scale);
    if (flame) drawFlame(ctx, now);
    drawWings(ctx);
    drawBody(ctx);
    drawCockpit(ctx);
    drawGuns(ctx);
    ctx.restore();
  }

  window.RewardSpaceship = { draw };
})();
