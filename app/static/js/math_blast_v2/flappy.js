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
  const Stickers = window.FlappyStickers;
  const Sky = window.FlappySky;

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
  let playMode = 'sprint';
  let sessionStartedAt = null;
  let wrongStreak = 0;
  let persistentCorrectThisSession = false;
  let endedByTimer = false;

  const WRONG_MSGS = [
    'Không sao, thử lại nhé',
    'Chưa đúng — bình tĩnh chọn lại',
    'Gà con vẫn cổ vũ bé',
    'Mình làm lại câu này nhé',
  ];
  const RIGHT_MSGS = [
    'Giỏi lắm!',
    'Hay quá!',
    'Tuyệt vời!',
    'Đúng rồi!',
  ];

  function isPractice() {
    return playMode === 'practice';
  }

  function pickRandom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  function updateFlightVisual() {
    if (Sky) {
      Sky.setAltitude(correctCount);
    }
    const stage = document.getElementById('flappy-stage');
    if (stage) {
      rung = Math.min(3, Math.floor(correctCount / 4));
      stage.dataset.rung = String(rung);
    }
  }

  function setRunScore(n) {
    const el = document.getElementById('flappy-score');
    if (!el) return;
    if (isPractice() && sprintActive) {
      el.textContent = `⭐ ${n}`;
    } else {
      el.textContent = `Điểm ${n}`;
    }
  }

  function setCombo(n) {
    const el = document.getElementById('flappy-combo');
    if (!el) return;
    if (isPractice()) {
      el.textContent = `Đúng ${correctCount}`;
      el.hidden = false;
    } else {
      el.textContent = `Chuỗi x${n}`;
      el.hidden = false;
    }
  }

  function setHudForMode() {
    const comboEl = document.getElementById('flappy-combo');
    if (isPractice()) {
      setTimerLabel('Luyện tập');
      if (comboEl) comboEl.hidden = false;
    } else {
      setTimerLabel(sprintActive ? `${timeLeft}s` : '60s');
    }
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
    const pbLine = best > 0 ? `Kỷ lục ${meta.label}: ${best} điểm.` : `Chưa có kỷ lục ${meta.label} — chơi Gà Toán một lần để ghi nhận.`;
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

  function todayIsoDate() {
    return new Date().toISOString().slice(0, 10);
  }

  async function refreshProfileExtra() {
    const stickerLine = Stickers ? ` · 📒 ${Stickers.countLabel(bootstrap)}` : '';
    await updateProfileBar((flappyProfileExtra(bootstrap) || '') + stickerLine);
    if (Stickers) Stickers.updateAlbumBadge(bootstrap);
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
        play_mode: playMode,
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
      if (wrongStreak >= 2) persistentCorrectThisSession = true;
      wrongStreak = 0;
      combo += 1;
      comboMax = Math.max(comboMax, combo);
      const delta = isPractice() ? 5 : 10 + combo * 2;
      score += delta;
      rung = Math.min(rung + 1, 3);
      updateFlightVisual();
      if (Sky) Sky.bump();
      if (AudioFx) {
        AudioFx.playCorrect();
        if (!isPractice() && (combo === 3 || combo === 5 || combo === 10)) {
          AudioFx.playCombo(combo);
        }
      }
      queueEvent(true, Date.now() - t0, item, delta);
      setCombo(combo);
      setRunScore(score);
      if (isPractice() && correctCount % 3 === 0) {
        toast(pickRandom(RIGHT_MSGS));
      }
      setTimeout(renderQuestion, isPractice() ? 550 : 400);
    } else {
      btn.classList.add('wrong');
      wrongStreak += 1;
      if (!isPractice()) {
        combo = 0;
        rung = Math.max(rung - 1, 0);
        setCombo(0);
      } else {
        setCombo(combo);
      }
      updateFlightVisual();
      if (AudioFx && !isPractice()) AudioFx.playWrong();
      queueEvent(false, Date.now() - t0, item, 0);
      toast(isPractice() ? pickRandom(WRONG_MSGS) : 'Chưa đúng — thử lại nhé');
    }
  }

  async function endSprint(manualEnd) {
    const wasPractice = isPractice();
    const manual = Boolean(manualEnd);
    if (!wasPractice && !manual) endedByTimer = true;
    sprintActive = false;
    setSprintUi(false);
    clearInterval(timerId);
    setTimerLabel(wasPractice ? 'Xong' : 'Hết giờ');
    setRunScore(score);
    const stage = document.getElementById('flappy-stage');
    if (stage) {
      stage.classList.add('mb-sprint-ended');
      stage.classList.remove('mb-practice-live');
    }
    if (AudioFx) {
      AudioFx.stopSpeech();
      AudioFx.stopBgm(2000);
    }
    await flushEvents();
    const now = new Date().toISOString();
    const finishedScore = score;
    const finishedGrade = activeGrade;
    const prevBest = getFlappyBestForGrade(bootstrap, finishedGrade);
    const durationS = sessionStartedAt
      ? Math.max(1, Math.round((Date.now() - sessionStartedAt) / 1000))
      : wasPractice
        ? 60
        : 60 - timeLeft;
    let newStickers = [];
    try {
      const endResp = await sessionsBatch(
        [
          {
            op: 'end',
            session_id: sessionId,
            ended_at: now,
            summary: {
              duration_s: durationS,
              score: finishedScore,
              questions_count: questionCount,
              correct_count: correctCount,
              accuracy: questionCount ? correctCount / questionCount : 0,
              summary_json: {
                tier: activeTier,
                grade: finishedGrade,
                play_mode: playMode,
                rung_max: rung,
                altitude: correctCount,
                combo_max: comboMax,
                play_date: todayIsoDate(),
                manual_end: manual,
                persistent_correct: persistentCorrectThisSession,
                ended_by_timer: endedByTimer,
              },
            },
          },
        ],
        `flappy-end-${sessionId}`
      );
      const row = endResp?.results?.find((r) => r.session_id === sessionId) || endResp?.results?.[0];
      newStickers = row?.stickers_unlocked || [];
      await reloadBootstrapFresh();
      renderGradePicker();
      updateGradeDesc();
      await refreshProfileExtra();
      if (Stickers && newStickers.length) {
        Stickers.celebrateUnlocks(bootstrap, newStickers, toast);
      }
      if (wasPractice) {
        toast(
          `Hay lắm! ${correctCount} câu đúng — bé muốn thử cuộc đua 60 giây thì bấm nút bên dưới nhé.`
        );
      } else {
        const newBest = getFlappyBestForGrade(bootstrap, finishedGrade);
        const isNewPb = finishedScore > prevBest && finishedScore > 0 && newBest === finishedScore;
        if (isNewPb) {
          flashGradePersonalBest(finishedGrade);
          toast(`🎉 Kỷ lục ${getGradeMeta(finishedGrade).label}: ${newBest} điểm!`);
        } else {
          toast(`Hết giờ! Điểm ${finishedScore} — đã lưu`);
        }
      }
    } catch (e) {
      toast(
        wasPractice
          ? `Đã làm ${correctCount} câu đúng (chưa lưu máy chủ: ${e.message})`
          : `Điểm ${finishedScore} (chưa lưu máy chủ: ${e.message})`
      );
    }
    setHudForMode();
    wrongStreak = 0;
    persistentCorrectThisSession = false;
    endedByTimer = false;
  }

  function tickTimer() {
    timeLeft -= 1;
    const el = document.getElementById('flappy-timer');
    if (el) el.textContent = `${timeLeft}s`;
    if (timeLeft <= 0) endSprint(false);
  }

  function applyBootstrapHud() {
    if (!bootstrap || sprintActive) return;
    refreshProfileExtra();
  }

  function setPlayButtonsBusy(busy) {
    const practiceBtn = document.getElementById('flappy-practice');
    const sprintBtn = document.getElementById('flappy-sprint');
    if (practiceBtn) practiceBtn.disabled = busy;
    if (sprintBtn) sprintBtn.disabled = busy;
  }

  function setSprintUi(active) {
    const practiceBtn = document.getElementById('flappy-practice');
    const sprintBtn = document.getElementById('flappy-sprint');
    const stopBtn = document.getElementById('flappy-stop');
    const modes = document.querySelector('.mb-play-modes');
    if (modes) modes.hidden = active;
    if (practiceBtn) practiceBtn.hidden = active;
    if (sprintBtn) sprintBtn.hidden = active;
    if (stopBtn) stopBtn.hidden = !active;
    const stage = document.getElementById('flappy-stage');
    if (stage) {
      stage.classList.toggle('mb-sprint-live', active && !isPractice());
      stage.classList.toggle('mb-practice-live', active && isPractice());
    }
  }

  async function beginPlay(mode) {
    if (sprintActive) return;
    playMode = mode;
    try {
      const me = await window.MathBlastV2.loadUserMe();
      if (me.role !== 'KID') {
        toast('Chọn tài khoản bé để chơi Gà Toán');
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
    wrongStreak = 0;
    persistentCorrectThisSession = false;
    endedByTimer = false;
    sessionStartedAt = Date.now();
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
    setPlayButtonsBusy(true);

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
      setPlayButtonsBusy(false);
      return;
    } finally {
      setPlayButtonsBusy(false);
    }

    sprintActive = true;
    const stage = document.getElementById('flappy-stage');
    if (stage) stage.classList.remove('mb-sprint-ended');
    setSprintUi(true);
    updateFlightVisual();
    if (Sky) Sky.reset();
    if (AudioFx && !isPractice()) AudioFx.startBgm();
    renderQuestion();
    setRunScore(0);
    setCombo(0);
    refreshProfileExtra();
    setHudForMode();
    clearInterval(timerId);
    if (!isPractice()) {
      timerId = setInterval(tickTimer, 1000);
      toast('Gà Toán — cuộc đua 60 giây!');
    } else {
      toast('Luyện tập nhẹ — không vội, sai cũng không sao nhé');
    }
  }

  function startPractice() {
    beginPlay('practice');
  }

  function startSprint() {
    beginPlay('sprint');
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
    if (Stickers) Stickers.bindAlbumUi(() => bootstrap);
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
      if (Sky) Sky.init();
      updateFlightVisual();
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
    const practiceBtn = document.getElementById('flappy-practice');
    const sprintBtn = document.getElementById('flappy-sprint');
    const stopBtn = document.getElementById('flappy-stop');
    if (practiceBtn && !practiceBtn.dataset.bound) {
      practiceBtn.dataset.bound = '1';
      practiceBtn.addEventListener('click', startPractice);
    }
    if (sprintBtn && !sprintBtn.dataset.bound) {
      sprintBtn.dataset.bound = '1';
      sprintBtn.addEventListener('click', startSprint);
    }
    if (stopBtn && !stopBtn.dataset.bound) {
      stopBtn.dataset.bound = '1';
      stopBtn.addEventListener('click', () => endSprint(true));
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
