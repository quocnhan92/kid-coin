(function (global) {
  if (!global.isEnglishMath || !global.isEnglishMath()) return;

  function applyFlappyStaticUi() {
    const start = document.getElementById('flappy-start');
    if (start) start.textContent = '▶ Start Math Bird';
    const score = document.getElementById('flappy-score');
    if (score) score.textContent = 'Score 0';
    const combo = document.getElementById('flappy-combo');
    if (combo) combo.textContent = 'Combo x0';
    const timer = document.getElementById('flappy-timer');
    if (timer && !timer.closest('.mb-sprint-live')) timer.textContent = '60s';
    if (global.FlappyAudio && global.FlappyAudio.updateToggleUi) {
      global.FlappyAudio.updateToggleUi(
        document.getElementById('flappy-toggle-tts'),
        document.getElementById('flappy-toggle-bgm')
      );
    }
  }

  function afterFlappyInit() {
    applyFlappyStaticUi();
    window.dispatchEvent(new CustomEvent('em-flappy-refresh'));
    if (global.MathBlastQuestionGen && global.MathBlastQuestionGen.GRADES) {
      const EN = {
        1: { label: 'Grade 1', subtitle: 'Count, add & subtract up to 100 (no carry)' },
        2: { label: 'Grade 2', subtitle: 'Add/subtract to 100 · times tables 2–10' },
        3: { label: 'Grade 3', subtitle: 'Multiplication tables 2–9 · division facts' },
        4: { label: 'Grade 4', subtitle: 'Same-denominator fractions · decimals' },
        5: { label: 'Grade 5', subtitle: 'Decimals · simple percent · ratios' },
      };
      Object.keys(EN).forEach((g) => {
        const meta = global.MathBlastQuestionGen.GRADES[g];
        if (meta) Object.assign(meta, EN[g]);
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    applyFlappyStaticUi();
    setTimeout(afterFlappyInit, 0);
    setTimeout(afterFlappyInit, 400);
    setTimeout(afterFlappyInit, 1200);
  });
  window.addEventListener('gameAuthRestored', () => {
    setTimeout(afterFlappyInit, 100);
  });
  global.__applyEnglishFlappyUi = afterFlappyInit;
})();
