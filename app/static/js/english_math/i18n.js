(function (g) {
  if (!(g.isEnglishMath && g.isEnglishMath())) return;
  g.MathBlastT = (en) => en;
  if (g.MathBlastV2 && g.MathBlastV2.MODE_LABELS) {
    Object.assign(g.MathBlastV2.MODE_LABELS, {
      candy: 'Candy Map',
      flappy: 'Math Bird',
      arcade: 'Arcade',
    });
  }
})();
