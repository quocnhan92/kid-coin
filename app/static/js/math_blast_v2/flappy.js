(function () {
  const {
    MODES,
    resolveGameId,
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

  const em = () => (window.isEnglishMath ? window.isEnglishMath() : !!window.ENGLISH_MATH);
  const t = (en, vi) => (em() ? en : vi);
  const showQ = (item) =>
    em() && window.EnglishMathSpeech ? window.EnglishMathSpeech.displayFromItem(item) : item.q;

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
    if (el) el.textContent = t(`Score ${n}`, `Điểm ${n}`);
  }

  function setCombo(n) {
    const el = document.getElementById('flappy-combo');
    if (el) el.textContent = t(`Combo x${n}`, `Chuỗi x${n}`);
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
    if (best > 0) return `${meta.label} · ${t('Best', 'Kỷ lục')} ${best}`;
    return `${meta.label}`;
  }

  function updateGradeDesc() {
    const el = document.getElementById('flappy-grade-desc');
    if (!el) return;
    const meta = getGradeMeta(activeGrade);
    const best = getFlappyBestForGrade(bootstrap, activeGrade);
    const pbLine = best > 0
      ? t(`Best ${meta.label}: ${best} pts.`, `Kỷ lục ${meta.label}: ${best} điểm.`)
      : t(
          `No best score for ${meta.label} yet — play once!`,
          `Chưa có kỷ lục ${meta.label} — chơi Gà Toán một lần để ghi nhận.`
        );
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
            ? `<span class="mb-grade-pb" title="${t('Best', 'Kỷ lục')}">🏆${best}</span>`
            : `<span class="mb-grade-pb mb-grade-pb--empty" title="${t('No record yet', 'Chưa có kỷ lục')}">—</span>`;
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
      toast(t('Cannot change grade during play', 'Không đổi lớp khi đang chơi'));
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
    qEl.textContent = showQ(item);
    choicesEl.innerHTML = item.choices
      .map((c) => `<button type="button" class="mb-choice" data-val="${c}">${c}</button>`)
      .join('');
    choicesEl.querySelectorAll('.mb-choice').forEach((btn) => {
      btn.addEventListener('click', () => onAnswer(btn, item));
    });
    if (sprintActive && AudioFx && (em() || AudioFx.getTtsEnabled())) {
      const speak = () => AudioFx.speakQuestion(item, em() ? { force: true } : undefined);
      requestAnimationFrame(() => setTimeout(speak, 80));
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
      toast(t('Wrong — try again!', 'Sai rồi — thử lại nhé!'));
    }
  }

  async function endSprint() {
    sprintActive = false;
    setSprintUi(false);
    clearInterval(timerId);
    setTimerLabel(t('Time up', 'Hết giờ'));
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
        toast(t(`🎉 New best ${getGradeMeta(finishedGrade).label}: ${newBest}!`, `🎉 Kỷ lục ${getGradeMeta(finishedGrade).label}: ${newBest} điểm!`));
      } else {
        toast(t(`Time up! Score ${finishedScore} — saved`, `Hết giờ! Điểm ${finishedScore} — đã lưu`));
      }
    } catch (e) {
      toast(t(`Score ${finishedScore} (not saved: ${e.message})`, `Điểm ${finishedScore} (chưa lưu máy chủ: ${e.message})`));
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
    startBtn.textContent = busy ? t('Starting…', 'Đang bắt đầu…') : t('▶ Start Math Bird', '▶ Chơi Gà Toán');
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
        toast(t('Pick a kid account to play Math Bird', 'Chọn tài khoản bé để chơi Gà Toán'));
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
      game_id: resolveGameId(),
      game_mode_id: MODES.flappy,
      started_at: now,
    };
    const packId = bootstrap?.profile?.active_content_pack_id;
    if (typeof packId === 'string' && packId) startOp.content_pack_id = packId;

    try {
      await sessionsBatch([startOp], `flappy-start-${sessionId}`);
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e)) {
        toast(t('Could not start session: ', 'Không bắt đầu được phiên: ') + e.message);
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
    if (window.GameUtils && window.GameUtils.warmupSpeech) window.GameUtils.warmupSpeech();
    if (AudioFx) {
      AudioFx.unlock();
      if (em() && AudioFx.setTtsEnabled) AudioFx.setTtsEnabled(true);
      AudioFx.startBgm();
    }
    renderQuestion();
    setRunScore(0);
    setCombo(0);
    refreshProfileExtra();
    document.getElementById('flappy-timer').textContent = '60s';
    clearInterval(timerId);
    timerId = setInterval(tickTimer, 1000);
    toast(t('Math Bird — 60 second race!', 'Gà Toán — bắt đầu cuộc đua 60 giây!'));
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
      }
      if (em()) {
        renderGradePicker();
        updateGradeDesc();
        refreshProfileExtra();
        if (typeof window.__applyEnglishFlappyUi === 'function') window.__applyEnglishFlappyUi();
      }
    } catch (e) {
      console.error(e);
    }

    // Always render grade picker even if bootstrap fails.
    // This prevents blank UI and allows interaction.
    if (!sprintActive) {
      renderGradePicker();
      updateGradeDesc();
      refreshProfileExtra();
      applyFlappyStaticUiLocal();
      if (typeof window.__applyEnglishFlappyUi === 'function') window.__applyEnglishFlappyUi();
    }

    const startBtn = document.getElementById('flappy-start');
    if (startBtn && !startBtn.dataset.bound) {
      startBtn.dataset.bound = '1';
      startBtn.addEventListener('click', startSprint);
    }
  }

  window.addEventListener('em-flappy-refresh', () => {
    if (!em()) return;
    renderGradePicker();
    updateGradeDesc();
    refreshProfileExtra();
    applyFlappyStaticUiLocal();
  });

  function applyFlappyStaticUiLocal() {
    const start = document.getElementById('flappy-start');
    if (start && !sprintActive) start.textContent = t('▶ Start Math Bird', '▶ Chơi Gà Toán');
    setRunScore(score);
    setCombo(combo);
    if (!sprintActive) setTimerLabel('60s');
    if (AudioFx) {
      AudioFx.updateToggleUi(
        document.getElementById('flappy-toggle-tts'),
        document.getElementById('flappy-toggle-bgm')
      );
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
