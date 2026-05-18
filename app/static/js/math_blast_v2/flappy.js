(function () {
  const {
    MODES,
    toast,
    setActiveSkuNav,
    updateProfileBar,
    getBootstrap,
    sessionsBatch,
    eventsBatch,
    clearBootstrapCache,
    uuid,
  } = window.MathBlastV2;

  const {
    createSession,
    resolveGrade,
    getGradeMeta,
    setStoredGrade,
    gradeToTier,
    GRADES,
  } = window.MathBlastQuestionGen;
  const AudioFx = window.FlappyAudio;

  let bootstrap = null;
  let sessionId = null;
  let questionSession = null;
  let activeGrade = 1;
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

  function setTimerLabel(text) {
    const el = document.getElementById('flappy-timer');
    if (el) el.textContent = text;
  }

  async function reloadBootstrapFresh() {
    clearBootstrapCache();
    bootstrap = await getBootstrap(MODES.flappy);
  }

  function flashGradePersonalBest(grade) {
    const btn = document.querySelector(`.mb-grade-btn[data-grade="${grade}"]`);
    if (!btn) return;
    btn.classList.add('mb-grade-btn--celebrate');
    setTimeout(() => btn.classList.remove('mb-grade-btn--celebrate'), 2400);
  }

  function getFlappyBestForGrade(boot, grade) {
    if (!boot) return 0;
    const tier = gradeToTier(grade);
    const pb = boot.flappy?.personal_best?.[tier];
    if (Number.isFinite(pb)) return pb;
    return 0;
  }

  function flappyProfileExtra(boot) {
    if (sprintActive) return null;
    const meta = getGradeMeta(activeGrade);
    const best = getFlappyBestForGrade(boot, activeGrade);
    if (best > 0) return `${meta.label} · Kỷ lục ${best}`;
    return meta.label;
  }

  function updateGradeDesc() {
    const el = document.getElementById('flappy-grade-desc');
    if (!el) return;
    const meta = getGradeMeta(activeGrade);
    const best = getFlappyBestForGrade(bootstrap, activeGrade);
    const pbLine = best > 0 ? `Kỷ lục ${meta.label}: ${best} điểm.` : `Chưa có kỷ lục ${meta.label} — chơi Chim Toán một lần để ghi nhận.`;
    el.textContent = `${meta.subtitle} ${pbLine}`;
  }

  function renderGradePicker() {
    const wrap = document.getElementById('flappy-grade-picker');
    if (!wrap) return;
    wrap.innerHTML = Object.keys(GRADES)
      .map((g) => {
        const gn = Number(g);
        const best = getFlappyBestForGrade(bootstrap, gn);
        const pbBadge =
          best > 0
            ? `<span class="mb-grade-pb" title="Kỷ lục">🏆${best}</span>`
            : '<span class="mb-grade-pb mb-grade-pb--empty" title="Chưa có kỷ lục">—</span>';
        return `
      <button type="button" class="mb-grade-btn ${gn === activeGrade ? 'active' : ''}"
        data-grade="${g}">${GRADES[g].label}${pbBadge}</button>`;
      })
      .join('');
    wrap.querySelectorAll('.mb-grade-btn').forEach((btn) => {
      btn.addEventListener('click', () => selectGrade(Number(btn.dataset.grade)));
    });
    updateGradeDesc();
  }

  function selectGrade(grade) {
    if (sprintActive) {
      toast('Không đổi lớp khi đang chơi');
      return;
    }
    activeGrade = grade;
    activeTier = gradeToTier(grade);
    setStoredGrade(grade);
    if (AudioFx) {
      AudioFx.setGrade(grade);
      AudioFx.updateToggleUi(
        document.getElementById('flappy-toggle-tts'),
        document.getElementById('flappy-toggle-bgm')
      );
    }
    renderGradePicker();
    questionSession = createSession(activeGrade);
    renderQuestion();
    refreshProfileExtra();
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
        grade: activeGrade,
        problem: item.q,
      },
    });
    if (pendingEvents.length >= 5) flushEvents();
  }

  async function onAnswer(btn, item) {
    if (!sprintActive) return;
    const val = Number(btn.dataset.val);
    const t0 = Date.now();
    const correct = val === item.a || Math.abs(val - item.a) < 0.001;
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
    setTimerLabel('Hết giờ');
    setRunScore(score);
    const stage = document.getElementById('flappy-stage');
    if (stage) stage.classList.add('mb-sprint-ended');
    if (AudioFx) {
      AudioFx.stopSpeech();
      AudioFx.stopBgm(2000);
    }
    await flushEvents();
    const now = new Date().toISOString();
    const finishedScore = score;
    const finishedGrade = activeGrade;
    const prevBest = getFlappyBestForGrade(bootstrap, finishedGrade);
    try {
      await sessionsBatch(
        [
          {
            op: 'end',
            session_id: sessionId,
            ended_at: now,
            summary: {
              duration_s: 60 - timeLeft,
              score: finishedScore,
              questions_count: questionCount,
              correct_count: correctCount,
              accuracy: questionCount ? correctCount / questionCount : 0,
              summary_json: {
                tier: activeTier,
                grade: finishedGrade,
                rung_max: rung,
                combo_max: comboMax,
              },
            },
          },
        ],
        `flappy-end-${sessionId}`
      );
      await reloadBootstrapFresh();
      renderGradePicker();
      updateGradeDesc();
      await refreshProfileExtra();
      const newBest = getFlappyBestForGrade(bootstrap, finishedGrade);
      const isNewPb = finishedScore > prevBest && finishedScore > 0 && newBest === finishedScore;
      if (isNewPb) {
        flashGradePersonalBest(finishedGrade);
        toast(`🎉 Kỷ lục ${getGradeMeta(finishedGrade).label}: ${newBest} điểm!`);
      } else {
        toast(`Hết giờ! Điểm ${finishedScore} — đã lưu`);
      }
    } catch (e) {
      toast(`Điểm ${finishedScore} (chưa lưu máy chủ: ${e.message})`);
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
    refreshProfileExtra();
  }

  function setStartBusy(busy) {
    const startBtn = document.getElementById('flappy-start');
    if (!startBtn) return;
    startBtn.disabled = busy;
    startBtn.textContent = busy ? 'Đang bắt đầu…' : '▶ Chơi Chim Toán';
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
        toast('Chọn tài khoản bé để chơi Chim Toán');
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
    activeGrade = resolveGrade(bootstrap?.flappy, bootstrap?.profile);
    activeTier = gradeToTier(activeGrade);
    if (AudioFx) {
      AudioFx.setGrade(activeGrade);
      AudioFx.unlock();
      AudioFx.updateToggleUi(
        document.getElementById('flappy-toggle-tts'),
        document.getElementById('flappy-toggle-bgm')
      );
    }
    questionSession = createSession(activeGrade);
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
    const stage = document.getElementById('flappy-stage');
    if (stage) stage.classList.remove('mb-sprint-ended');
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
    toast('Chim Toán — bắt đầu cuộc đua 60 giây!');
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
      activeGrade = resolveGrade(bootstrap?.flappy, bootstrap?.profile);
      activeTier = gradeToTier(activeGrade);
      if (AudioFx) {
        AudioFx.setGrade(activeGrade);
        AudioFx.updateToggleUi(ttsBtn, bgmBtn);
      }
      renderGradePicker();
      applyBootstrapHud();
      updateBird();
      if (!sprintActive) {
        setRunScore(0);
        setCombo(0);
        setTimerLabel('60s');
        questionSession = createSession(activeGrade);
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
