(function () {
  const {
    MODES,
    toast,
    setActiveSkuNav,
    updateProfileBar,
    getBootstrap,
    sessionsBatch,
    eventsBatch,
    uuid,
  } = window.MathBlastV2;

  const { createSession, resolveActiveTier } = window.MathBlastQuestionGen;
  const AudioFx = window.FlappyAudio;

  let bootstrap = null;
  let sessionId = null;
  let questionSession = null;
  let activeTier = 'T1';
  let currentQuestion = null;
  let clientSeq = 0;
  let rung = 0;
  let combo = 0;
  let comboMax = 0;
  let score = 0;
  let correctCount = 0;
  let questionCount = 0;
  let timeLeft = 60;
  let timerId = null;
  let sprintActive = false;
  let pendingEvents = [];

  function updateBird() {
    const bird = document.getElementById('flappy-bird');
    if (!bird) return;
    const pct = 15 + rung * 22;
    bird.style.bottom = `${Math.min(pct, 75)}%`;
  }

  function setRunScore(n) {
    const el = document.getElementById('flappy-score');
    if (el) el.textContent = `Điểm ${n}`;
  }

  function setCombo(n) {
    const el = document.getElementById('flappy-combo');
    if (el) el.textContent = `Chuỗi x${n}`;
  }

  /** Một số kỷ lục duy nhất: max(high_score chế độ, mọi tier personal_best). */
  function getFlappyBestScore(boot) {
    if (!boot) return 0;
    let best = boot.game_stats?.high_score || 0;
    const pb = boot.flappy?.personal_best;
    if (pb && typeof pb === 'object') {
      Object.values(pb).forEach((v) => {
        if (Number.isFinite(v) && v > best) best = v;
      });
    }
    return best;
  }

  function flappyProfileExtra(boot) {
    if (sprintActive) return null;
    const best = getFlappyBestScore(boot);
    return best > 0 ? `Kỷ lục ${best}` : null;
  }

  async function refreshProfileExtra() {
    await updateProfileBar(flappyProfileExtra(bootstrap));
  }

  function renderQuestion() {
    if (!questionSession) return;
    const item = questionSession.next();
    currentQuestion = item;
    window.__flappyCurrentQuestion = item;
    const qEl = document.getElementById('flappy-question');
    const choicesEl = document.getElementById('flappy-choices');
    if (!qEl || !choicesEl) return;
    qEl.textContent = item.q;
    choicesEl.innerHTML = item.choices
      .map((c) => `<button type="button" class="mb-choice" data-val="${c}">${c}</button>`)
      .join('');
    choicesEl.querySelectorAll('.mb-choice').forEach((btn) => {
      btn.addEventListener('click', () => onAnswer(btn, item));
    });
    if (sprintActive && AudioFx) {
      AudioFx.speakQuestion(item);
    }
  }

  async function flushEvents() {
    if (!sessionId || pendingEvents.length === 0) return;
    const batch = pendingEvents.splice(0, pendingEvents.length);
    try {
      await eventsBatch(sessionId, batch);
    } catch (e) {
      console.error('events batch', e);
      pendingEvents.unshift(...batch);
    }
  }

  function queueEvent(correct, latencyMs, item, scoreDelta) {
    clientSeq += 1;
    questionCount += 1;
    if (correct) correctCount += 1;
    pendingEvents.push({
      client_seq: clientSeq,
      occurred_at: new Date().toISOString(),
      event_type: 'answer',
      skill_unit_id: item.skill,
      correct,
      latency_ms: latencyMs,
      score_delta: scoreDelta,
      context: {
        input_method: 'tap_choice_4',
        tier: activeTier,
        problem: item.q,
      },
    });
    if (pendingEvents.length >= 5) flushEvents();
  }

  async function onAnswer(btn, item) {
    if (!sprintActive) return;
    const val = Number(btn.dataset.val);
    const t0 = Date.now();
    const correct = val === item.a;
    if (correct) {
      btn.classList.add('correct');
      combo += 1;
      comboMax = Math.max(comboMax, combo);
      const delta = 10 + combo * 2;
      score += delta;
      rung = Math.min(rung + 1, 3);
      setCombo(combo);
      setRunScore(score);
      updateBird();
      if (AudioFx) {
        AudioFx.playCorrect();
        if (combo === 3 || combo === 5 || combo === 10) AudioFx.playCombo(combo);
      }
      queueEvent(true, Date.now() - t0, item, delta);
      setTimeout(renderQuestion, 400);
    } else {
      btn.classList.add('wrong');
      combo = 0;
      rung = Math.max(rung - 1, 0);
      setCombo(0);
      updateBird();
      if (AudioFx) AudioFx.playWrong();
      queueEvent(false, Date.now() - t0, item, 0);
      toast('Sai rồi — thử lại nhé!');
    }
  }

  async function endSprint() {
    sprintActive = false;
    setSprintUi(false);
    clearInterval(timerId);
    if (AudioFx) {
      AudioFx.stopSpeech();
      AudioFx.stopBgm(2000);
    }
    await flushEvents();
    const now = new Date().toISOString();
    try {
      await sessionsBatch(
        [
          {
            op: 'end',
            session_id: sessionId,
            ended_at: now,
            summary: {
              duration_s: 60 - timeLeft,
              score,
              questions_count: questionCount,
              correct_count: correctCount,
              accuracy: questionCount ? correctCount / questionCount : 0,
              summary_json: {
                tier: activeTier,
                rung_max: rung,
                combo_max: comboMax,
              },
            },
          },
        ],
        `flappy-end-${sessionId}`
      );
      bootstrap = await getBootstrap(MODES.flappy);
      applyBootstrapHud();
      toast(`Hết giờ! Điểm ${score} — đã lưu`);
    } catch (e) {
      toast(`Điểm ${score} (chưa lưu máy chủ: ${e.message})`);
    }
  }

  function tickTimer() {
    timeLeft -= 1;
    const el = document.getElementById('flappy-timer');
    if (el) el.textContent = `${timeLeft}s`;
    if (timeLeft <= 0) endSprint();
  }

  function applyBootstrapHud() {
    if (!bootstrap || sprintActive) return;
    setRunScore(0);
    refreshProfileExtra();
  }

  function setStartBusy(busy) {
    const startBtn = document.getElementById('flappy-start');
    if (!startBtn) return;
    startBtn.disabled = busy;
    startBtn.textContent = busy ? 'Đang bắt đầu…' : '▶ Bắt đầu cuộc đua';
  }

  function setSprintUi(active) {
    const startBtn = document.getElementById('flappy-start');
    if (startBtn) startBtn.hidden = active;
    const stage = document.getElementById('flappy-stage');
    if (stage) stage.classList.toggle('mb-sprint-live', active);
  }

  async function startSprint() {
    if (sprintActive) return;
    try {
      const me = await window.MathBlastV2.loadUserMe();
      if (me.role !== 'KID') {
        toast('Chọn tài khoản bé để bắt đầu cuộc đua');
        if (window.GameAuth) window.GameAuth.open();
        return;
      }
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e) && window.GameAuth) {
        window.GameAuth.openSessionExpired();
      }
      return;
    }

    sessionId = uuid();
    clientSeq = 0;
    pendingEvents = [];
    timeLeft = 60;
    score = 0;
    combo = 0;
    comboMax = 0;
    rung = 0;
    correctCount = 0;
    questionCount = 0;
    activeTier = resolveActiveTier(bootstrap?.flappy);
    if (AudioFx) {
      AudioFx.setTier(activeTier);
      AudioFx.unlock();
      AudioFx.updateToggleUi(
        document.getElementById('flappy-toggle-tts'),
        document.getElementById('flappy-toggle-bgm')
      );
    }
    questionSession = createSession(activeTier);
    const now = new Date().toISOString();
    setStartBusy(true);

    const startOp = {
      op: 'start',
      session_id: sessionId,
      game_id: 'math_blast',
      game_mode_id: MODES.flappy,
      started_at: now,
    };
    const packId = bootstrap?.profile?.active_content_pack_id;
    if (typeof packId === 'string' && packId) startOp.content_pack_id = packId;

    try {
      await sessionsBatch([startOp], `flappy-start-${sessionId}`);
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e)) {
        toast('Không bắt đầu được phiên: ' + e.message);
      }
      setStartBusy(false);
      return;
    } finally {
      setStartBusy(false);
    }

    sprintActive = true;
    setSprintUi(true);
    updateBird();
    if (AudioFx) AudioFx.startBgm();
    renderQuestion();
    setRunScore(0);
    setCombo(0);
    refreshProfileExtra();
    document.getElementById('flappy-timer').textContent = '60s';
    clearInterval(timerId);
    timerId = setInterval(tickTimer, 1000);
    toast('Cuộc đua 60 giây — bắt đầu!');
  }

  function bindBirdReplay() {
    const bird = document.getElementById('flappy-bird');
    if (!bird || bird.dataset.audioBound) return;
    bird.dataset.audioBound = '1';
    bird.addEventListener('click', () => {
      if (!AudioFx || !currentQuestion) return;
      AudioFx.unlock();
      AudioFx.speakQuestion(currentQuestion, { force: true });
    });
  }

  async function init() {
    setActiveSkuNav('flappy');
    if (AudioFx) await AudioFx.init();
    const ttsBtn = document.getElementById('flappy-toggle-tts');
    const bgmBtn = document.getElementById('flappy-toggle-bgm');
    if (AudioFx) AudioFx.bindToggles(ttsBtn, bgmBtn);
    bindBirdReplay();
    try {
      bootstrap = await getBootstrap(MODES.flappy);
      activeTier = resolveActiveTier(bootstrap?.flappy);
      if (AudioFx) {
        AudioFx.setTier(activeTier);
        AudioFx.updateToggleUi(ttsBtn, bgmBtn);
      }
      applyBootstrapHud();
      updateBird();
      if (!sprintActive) {
        questionSession = createSession(activeTier);
        renderQuestion();
      }
    } catch (e) {
      console.error(e);
    }
    const startBtn = document.getElementById('flappy-start');
    if (startBtn && !startBtn.dataset.bound) {
      startBtn.dataset.bound = '1';
      startBtn.addEventListener('click', startSprint);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const run = () => init();
    if (window.GameAuth) GameAuth.ready().then(run);
    else run();
    window.addEventListener('gameAuthRestored', () => {
      init().catch((e) => console.error(e));
    });
  });
})();
