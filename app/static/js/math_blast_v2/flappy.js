(function () {
  const { toast, setActiveSkuNav } = window.MathBlastV2;

  const QUESTIONS = [
    { q: '3 + 5 = ?', a: 8, choices: [6, 8, 9, 7] },
    { q: '12 − 4 = ?', a: 8, choices: [8, 6, 10, 7] },
    { q: '2 × 4 = ?', a: 8, choices: [6, 8, 10, 12] },
    { q: '9 ÷ 3 = ?', a: 3, choices: [2, 3, 4, 6] },
  ];

  let rung = 0;
  let combo = 0;
  let score = 0;
  let timeLeft = 60;
  let qIndex = 0;
  let timerId = null;

  function updateBird() {
    const bird = document.getElementById('flappy-bird');
    if (!bird) return;
    const pct = 15 + rung * 22;
    bird.style.bottom = `${Math.min(pct, 75)}%`;
  }

  function renderQuestion() {
    const item = QUESTIONS[qIndex % QUESTIONS.length];
    const qEl = document.getElementById('flappy-question');
    const choicesEl = document.getElementById('flappy-choices');
    if (!qEl || !choicesEl) return;
    qEl.textContent = item.q;
    choicesEl.innerHTML = item.choices
      .map(
        (c) =>
          `<button type="button" class="mb-choice" data-val="${c}">${c}</button>`
      )
      .join('');
    choicesEl.querySelectorAll('.mb-choice').forEach((btn) => {
      btn.addEventListener('click', () => onAnswer(btn, item.a));
    });
  }

  function onAnswer(btn, correct) {
    const val = Number(btn.dataset.val);
    if (val === correct) {
      btn.classList.add('correct');
      combo += 1;
      score += 10 + combo * 2;
      rung = Math.min(rung + 1, 3);
      qIndex += 1;
      document.getElementById('flappy-combo').textContent = `Combo x${combo}`;
      document.getElementById('flappy-score').textContent = `Điểm ${score}`;
      updateBird();
      setTimeout(renderQuestion, 400);
    } else {
      btn.classList.add('wrong');
      combo = 0;
      rung = Math.max(rung - 1, 0);
      document.getElementById('flappy-combo').textContent = 'Combo x0';
      updateBird();
      toast('Sai rồi — thử lại nhé! (không trừ điểm)');
    }
  }

  function tickTimer() {
    timeLeft -= 1;
    const el = document.getElementById('flappy-timer');
    if (el) el.textContent = `${timeLeft}s`;
    if (timeLeft <= 0) {
      clearInterval(timerId);
      toast(`Hết giờ! Điểm: ${score}`);
    }
  }

  function startSprint() {
    timeLeft = 60;
    score = 0;
    combo = 0;
    rung = 0;
    qIndex = 0;
    updateBird();
    renderQuestion();
    document.getElementById('flappy-score').textContent = 'Điểm 0';
    document.getElementById('flappy-combo').textContent = 'Combo x0';
    document.getElementById('flappy-timer').textContent = '60s';
    clearInterval(timerId);
    timerId = setInterval(tickTimer, 1000);
    toast('Sprint 60s — prototype');
  }

  document.addEventListener('DOMContentLoaded', () => {
    setActiveSkuNav('flappy');
    updateBird();
    renderQuestion();
    const startBtn = document.getElementById('flappy-start');
    if (startBtn) startBtn.addEventListener('click', startSprint);
  });
})();
