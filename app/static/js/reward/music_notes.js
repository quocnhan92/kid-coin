(function (global) {
  const LANES = [
    { key: 'A', sol: 'Do', en: 'C', freq: 261.63, color: '#f472b6' },
    { key: 'S', sol: 'Re', en: 'D', freq: 293.66, color: '#34d399' },
    { key: 'E', sol: 'Mi', en: 'E', freq: 329.63, color: '#60a5fa' },
    { key: 'F', sol: 'Fa', en: 'F', freq: 349.23, color: '#fbbf24' },
  ];

  function drawQuarterNote(ctx, x, y, color, scale) {
    const s = scale || 1;
    ctx.save();
    ctx.translate(x, y);
    ctx.fillStyle = color;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5 * s;
    ctx.beginPath();
    ctx.ellipse(0, 0, 9 * s, 7 * s, -0.35, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(7 * s, -2 * s);
    ctx.lineTo(7 * s, -28 * s);
    ctx.stroke();
    ctx.restore();
  }

  function drawEighthNote(ctx, x, y, color, scale) {
    const s = scale || 1;
    drawQuarterNote(ctx, x, y, color, s);
    ctx.save();
    ctx.translate(x, y);
    ctx.strokeStyle = color;
    ctx.lineWidth = 2 * s;
    ctx.beginPath();
    ctx.moveTo(7 * s, -28 * s);
    ctx.quadraticCurveTo(18 * s, -18 * s, 12 * s, -8 * s);
    ctx.stroke();
    ctx.restore();
  }

  function playTone(audioCtx, freq, dur, vol) {
    if (!audioCtx) return;
    const t0 = audioCtx.currentTime;
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = 'triangle';
    o.frequency.value = freq;
    g.gain.setValueAtTime(vol || 0.12, t0);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    o.connect(g);
    g.connect(audioCtx.destination);
    o.start(t0);
    o.stop(t0 + dur);
  }

  function playLane(audioCtx, lane, dur) {
    const L = LANES[lane];
    if (L) playTone(audioCtx, L.freq, dur || 0.22, 0.14);
  }

  global.RewardMusicNotes = {
    LANES,
    drawQuarterNote,
    drawEighthNote,
    playTone,
    playLane,
  };
})(window);
