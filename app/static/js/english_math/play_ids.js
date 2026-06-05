/** English Math — tách game_id khỏi Math Blast VN (math_blast). */
(function (g) {
  if (!g.MathBlastV2) return;
  g.MathBlastV2.GAME_ID = 'english_math';
  g.MathBlastV2.FLAPPY_GRADE_LS_KEY = 'english_math_flappy_grade';
  Object.assign(g.MathBlastV2.MODES, {
    candy: 'english_math:candy',
    flappy: 'english_math:flappy',
    arcade: 'english_math:arcade_free',
    arcadeClass: 'english_math:arcade_class',
  });
  if (typeof g.MathBlastV2.clearBootstrapCache === 'function') {
    g.MathBlastV2.clearBootstrapCache();
  }
})(window);
