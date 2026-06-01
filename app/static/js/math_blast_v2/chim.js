/**
 * Chim Toán Vui — Thảo nguyên Lớp 1–2 (MVP), khung block L3–5.
 */
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

  const AudioFx = window.ChimAudio;
  const CHIM_MODE = MODES.chim || 'math_blast:chim';
  const PRAIRIE_GRADES = [1, 2];
  const LS_GRADE = 'mb_v2_chim_grade';

  let bootstrap = null;
  let sessionId = null;
  let questionSession = null;
  let activeGrade = 1;
  let activeTier = 'T1';
  let currentQuestion = null;
  let clientSeq = 0;
  let score = 0;
  let goldSession = 0;
  let correctCount = 0;
  let starCount = 0;
  let questionCount = 0;
  let playing = false;
  let pendingEvents = [];
  let sessionStartedAt = null;
  let goldSyncedOnServer = 0;
  let correctSinceSync = 0;
  let finalizing = false;
  const CORRECT_SYNC_EVERY = 2;
  const GOLD_PER_CORRECT = 2;

  function chimExtra() {
    return bootstrap?.chim?.extra || {};
  }

  function getBestForGrade(grade) {
    const tier = gradeToTier(grade);
    return chimExtra().prairie_best_by_tier?.[tier] || 0;
  }

  function profileLine() {
    const meta = getGradeMeta(activeGrade);
    const gold = chimExtra().gold || 0;
    const best = getBestForGrade(activeGrade);
    return `${meta.label} · 🪙${gold}${best > 0 ? ` · Kỷ ${best}` : ''}`;
  }

  function renderBlocks() {
    const wrap = document.getElementById('chim-blocks');
    if (!wrap) return;
    const blocks = chimExtra().blocks || {};
    const items = [
      { key: 'prairie', label: 'Thảo nguyên', grades: '1–2', unlocked: true, href: '#play' },
      { key: 'T3', label: blocks.T3?.label || 'Rừng sương', grades: '3', unlocked: !!blocks.T3?.unlocked },
      { key: 'T4', label: blocks.T4?.label || 'Ngoại ô', grades: '4', unlocked: !!blocks.T4?.unlocked },
      { key: 'T5', label: blocks.T5?.label || 'Thành phố', grades: '5', unlocked: !!blocks.T5?.unlocked },
    ];
    wrap.innerHTML = items
      .map((b) => {
        const lock = b.unlocked ? '' : ' is-locked';
        const hint = b.unlocked
          ? b.key === 'prairie'
            ? 'Đang chơi'
            : 'Sắp ra mắt'
          : 'Luyện Lớp 2 đủ 30 điểm hoặc 50 câu đúng tổng';
        return `
        <div class="chim-block${lock}" data-block="${b.key}">
          <span class="chim-block-grade">Lớp ${b.grades}</span>
          <strong>${b.label}</strong>
          <span class="chim-block-hint">${hint}</span>
        </div>`;
      })
      .join('');
  }

  function renderGradePicker() {
    const wrap = document.getElementById('chim-grade-picker');
    if (!wrap) return;
    wrap.innerHTML = PRAIRIE_GRADES.map((g) => {
      const best = getBestForGrade(g);
      return `
      <button type="button" class="mb-grade-btn ${g === activeGrade ? 'active' : ''}" data-grade="${g}">
        ${GRADES[g].label}
        <span class="mb-grade-pb">${best > 0 ? `🏆${best}` : '—'}</span>
      </button>`;
    }).join('');
    wrap.querySelectorAll('.mb-grade-btn').forEach((btn) => {
      btn.addEventListener('click', () => selectGrade(Number(btn.dataset.grade)));
    });
    const desc = document.getElementById('chim-grade-desc');
    if (desc) {
      const meta = getGradeMeta(activeGrade);
      desc.textContent = `${meta.subtitle} Súng cao su — không thua, sai thì chim bay đi nhé.`;
    }
  }

  async function selectGrade(grade) {
    if (playing) {
      await finalizeSession({ quiet: true });
    }
    activeGrade = grade;
    activeTier = gradeToTier(grade);
    localStorage.setItem(LS_GRADE, String(grade));
    renderGradePicker();
    questionSession = createSession(activeGrade);
    renderQuestionPreview();
    updateProfileBar(profileLine());
  }

  function spawnTarget() {
    const el = document.getElementById('chim-target');
    if (!el) return;
    const icons = activeGrade === 1 ? ['🐥', '🐣', '🥚'] : ['🐦', '🕊️', '🐤'];
    el.textContent = icons[Math.floor(Math.random() * icons.length)];
    el.classList.remove('chim-target-hit', 'chim-target-miss');
    el.style.left = `${15 + Math.random() * 55}%`;
    el.style.bottom = `${28 + Math.random() * 22}%`;
  }

  function renderQuestionPreview() {
    const qEl = document.getElementById('chim-question');
    const choicesEl = document.getElementById('chim-choices');
    if (!playing) {
      if (qEl) qEl.textContent = 'Bấm Bắt đầu chơi trong khung';
      if (choicesEl) choicesEl.innerHTML = '';
      return;
    }
    renderQuestion();
  }

  function bindChoices(item) {
    const choicesEl = document.getElementById('chim-choices');
    if (!choicesEl) return;
    choicesEl.innerHTML = item.choices
      .map((c) => `<button type="button" class="mb-choice" data-val="${c}">${c}</button>`)
      .join('');
    choicesEl.querySelectorAll('.mb-choice').forEach((btn) => {
      btn.addEventListener('click', () => onAnswer(btn, item));
    });
  }

  function renderQuestion(presetItem, opts) {
    if (!questionSession) return;
    const item = presetItem || questionSession.next();
    currentQuestion = item;
    window.__chimCurrentQuestion = item;
    const qEl = document.getElementById('chim-question');
    if (qEl) qEl.textContent = item.q;
    spawnTarget();
    bindChoices(item);
    if (playing && AudioFx && !(opts && opts.skipSpeak)) {
      AudioFx.unlock();
      AudioFx.speakQuestion(item);
    }
  }

  function showHitFx() {
    const fx = document.getElementById('chim-fx');
    const target = document.getElementById('chim-target');
    if (!fx || !target) return;
    const rect = target.getBoundingClientRect();
    const stage = document.getElementById('chim-stage');
    const stageRect = stage ? stage.getBoundingClientRect() : rect;
    const left = rect.left - stageRect.left + rect.width / 2;
    const top = rect.top - stageRect.top + rect.height / 2;

    const star = document.createElement('span');
    star.className = 'chim-fx-star';
    star.textContent = '⭐';
    star.style.left = `${left}px`;
    star.style.top = `${top}px`;
    fx.appendChild(star);
    setTimeout(() => star.remove(), 900);

    const pop = document.createElement('span');
    pop.className = 'chim-fx-score';
    pop.textContent = '+10';
    pop.style.left = `${left}px`;
    pop.style.top = `${top - 20}px`;
    fx.appendChild(pop);
    setTimeout(() => pop.remove(), 800);

    const ting = document.createElement('span');
    ting.className = 'chim-fx-ting';
    ting.textContent = 'ting!';
    ting.style.left = `${left + 24}px`;
    ting.style.top = `${top - 8}px`;
    fx.appendChild(ting);
    setTimeout(() => ting.remove(), 700);
  }

  function fireShot(hit) {
    const shot = document.getElementById('chim-shot');
    const sling = document.getElementById('chim-sling');
    const target = document.getElementById('chim-target');
    if (shot) {
      shot.classList.remove('chim-shot-fly', 'chim-shot-miss');
      void shot.offsetWidth;
      shot.classList.add(hit ? 'chim-shot-fly' : 'chim-shot-miss');
    }
    if (sling) {
      sling.classList.add('chim-sling-pop');
      setTimeout(() => sling.classList.remove('chim-sling-pop'), 200);
    }
    if (target) {
      target.classList.add(hit ? 'chim-target-hit' : 'chim-target-miss');
    }
  }

  async function onAnswer(btn, item) {
    if (!playing) return;
    if (AudioFx) AudioFx.unlock();
    const val = Number(btn.dataset.val);
    const correct = val === item.a || Math.abs(val - item.a) < 0.001;
    const t0 = Date.now();
    questionCount += 1;
    clientSeq += 1;
    pendingEvents.push({
      client_seq: clientSeq,
      occurred_at: new Date().toISOString(),
      event_type: 'answer',
      skill_unit_id: item.skill,
      correct,
      latency_ms: Date.now() - t0,
      score_delta: correct ? 10 : 0,
      context: { grade: activeGrade, play_mode: 'prairie', weapon: 'slingshot' },
    });

    if (correct) {
      btn.classList.add('correct');
      correctCount += 1;
      starCount += 1;
      score += 10;
      goldSession += 2;
      fireShot(true);
      if (AudioFx) AudioFx.playCorrect();
      showHitFx();
      updateHud();
      toast('⭐ +1 · +10 điểm');
      correctSinceSync += 1;
      if (correctSinceSync >= CORRECT_SYNC_EVERY) {
        syncProgressAfterCorrectStreak();
      }
      setTimeout(renderQuestion, 750);
    } else {
      btn.classList.add('wrong');
      fireShot(false);
      if (AudioFx) AudioFx.playWrong();
      toast('Chưa trúng — chim bay đi rồi, thử câu mới!');
      setTimeout(renderQuestion, 900);
    }
  }

  function updateHud() {
    const s = document.getElementById('chim-score');
    const g = document.getElementById('chim-gold');
    const st = document.getElementById('chim-stars');
    if (s) {
      s.textContent = `Điểm ${score}`;
      s.classList.remove('chim-hud-bump');
      void s.offsetWidth;
      s.classList.add('chim-hud-bump');
    }
    if (g) g.textContent = `🪙 ${(chimExtra().gold || 0) + goldSession}`;
    if (st) {
      st.textContent = `⭐ ${starCount}`;
      st.classList.remove('chim-hud-bump');
      void st.offsetWidth;
      st.classList.add('chim-hud-bump');
    }
  }

  async function flushEvents() {
    if (!sessionId || !pendingEvents.length) return;
    const batch = pendingEvents.splice(0, pendingEvents.length);
    try {
      await eventsBatch(sessionId, batch);
      return batch;
    } catch (e) {
      console.error(e);
      pendingEvents.unshift(...batch);
      return null;
    }
  }

  async function syncProgressAfterCorrectStreak() {
    if (!sessionId || !playing) return;
    const nCorrect = correctSinceSync;
    const batch = await flushEvents();
    if (!batch) return;
    const syncedCorrect = batch.filter((ev) => ev.correct).length || nCorrect;
    goldSyncedOnServer += syncedCorrect * GOLD_PER_CORRECT;
    correctSinceSync = 0;
    try {
      clearBootstrapCache();
      bootstrap = await getBootstrap(CHIM_MODE);
      updateProfileBar(profileLine());
      updateHud();
      if (syncedCorrect > 0) {
        toast(`🪙 Đã lưu (+${syncedCorrect * GOLD_PER_CORRECT} vàng)`);
      }
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e)) {
        console.warn('sync bootstrap', e);
      }
    }
  }

  async function finalizeSession(opts) {
    const quiet = !!(opts && opts.quiet);
    if (finalizing) return;
    if (!sessionId) {
      playing = false;
      setPlayUi(false);
      return;
    }
    finalizing = true;
    const sid = sessionId;
    playing = false;
    setPlayUi(false);
    if (AudioFx) AudioFx.stopBgm(quiet ? 600 : 1500);
    const lastBatch = await flushEvents();
    if (lastBatch) {
      const c = lastBatch.filter((ev) => ev.correct).length;
      goldSyncedOnServer += c * GOLD_PER_CORRECT;
    }
    sessionId = null;
    if (questionCount <= 0) {
      renderQuestionPreview();
      finalizing = false;
      return;
    }
    const now = new Date().toISOString();
    const durationS = sessionStartedAt
      ? Math.max(1, Math.round((Date.now() - sessionStartedAt) / 1000))
      : 60;
    try {
      await sessionsBatch(
        [
          {
            op: 'end',
            session_id: sid,
            ended_at: now,
            summary: {
              duration_s: durationS,
              score,
              questions_count: questionCount,
              correct_count: correctCount,
              accuracy: questionCount ? correctCount / questionCount : 0,
              summary_json: {
                tier: activeTier,
                grade: activeGrade,
                play_mode: 'prairie',
                gold_earned: 0,
                weapon: 'slingshot',
              },
            },
          },
        ],
        `chim-end-${sid}`
      );
      clearBootstrapCache();
      bootstrap = await getBootstrap(CHIM_MODE);
      renderBlocks();
      renderGradePicker();
      if (!quiet) {
        toast(`Đã lưu! ${correctCount} câu đúng · 🪙${chimExtra().gold || 0}`);
      }
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e) && !quiet) {
        toast('Chưa lưu máy chủ: ' + e.message);
      }
    }
    updateProfileBar(profileLine());
    updateHud();
    renderQuestionPreview();
    finalizing = false;
  }

  async function startPrairie() {
    if (playing) return;
    if (sessionId && (playing || questionCount > 0)) {
      await finalizeSession({ quiet: true });
    } else if (sessionId) {
      sessionId = null;
    }
    focusPlayArea();
    activeGrade = gradeForSession();
    activeTier = gradeToTier(activeGrade);
    questionSession = createSession(activeGrade);
    const firstItem = questionSession.next();
    currentQuestion = firstItem;
    window.__chimCurrentQuestion = firstItem;
    if (AudioFx) {
      AudioFx.ensurePrefsInitialized();
      AudioFx.unlock();
      if (AudioFx.getTtsEnabled()) AudioFx.speakQuestion(firstItem, { force: true });
    }

    try {
      const me = await window.MathBlastV2.loadUserMe();
      if (me.role !== 'KID') {
        toast('Chọn tài khoản bé để chơi');
        if (window.GameAuth) window.GameAuth.open();
        return;
      }
    } catch (e) {
      if (window.GameAuth) window.GameAuth.openSessionExpired();
      return;
    }

    sessionId = uuid();
    score = 0;
    goldSession = 0;
    goldSyncedOnServer = 0;
    correctSinceSync = 0;
    correctCount = 0;
    starCount = 0;
    questionCount = 0;
    clientSeq = 0;
    pendingEvents = [];
    sessionStartedAt = Date.now();
    if (AudioFx) {
      await AudioFx.ensureReady();
      if (AudioFx.getBgmEnabled()) AudioFx.startBgm();
    }

    const now = new Date().toISOString();
    const startOp = {
      op: 'start',
      session_id: sessionId,
      game_id: 'math_blast',
      game_mode_id: CHIM_MODE,
      started_at: now,
    };
    const packId = bootstrap?.profile?.active_content_pack_id;
    if (packId) startOp.content_pack_id = packId;

    try {
      await sessionsBatch([startOp], `chim-start-${sessionId}`);
    } catch (e) {
      if (!window.MathBlastV2.isAuthError(e)) toast('Không bắt đầu phiên: ' + e.message);
      return;
    }

    if (AudioFx) {
      AudioFx.unlock();
      await AudioFx.ensureReady();
    }

    playing = true;
    setPlayUi(true);
    renderQuestion(firstItem, { skipSpeak: true });
    updateHud();
    focusPlayArea();
    toast('Thảo nguyên — bắn trúng khi chọn đúng!');
  }

  function resolveGradeFromBootstrap() {
    const last = chimExtra().last_grade;
    if (last && PRAIRIE_GRADES.includes(last)) return last;
    const stored = Number(localStorage.getItem(LS_GRADE));
    if (PRAIRIE_GRADES.includes(stored)) return stored;
    return resolveGrade(null, bootstrap?.profile);
  }

  function gradeForSession() {
    const stored = Number(localStorage.getItem(LS_GRADE));
    if (PRAIRIE_GRADES.includes(stored)) return stored;
    if (PRAIRIE_GRADES.includes(activeGrade)) return activeGrade;
    return resolveGradeFromBootstrap();
  }

  function focusPlayArea() {
    const panel = document.getElementById('chim-game-panel');
    if (!panel) return;
    panel.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });
    requestAnimationFrame(() => {
      try {
        panel.focus({ preventScroll: true });
      } catch (e) {
        panel.focus();
      }
    });
  }

  function setPlayUi(on) {
    const startWrap = document.getElementById('chim-start-wrap');
    const stage = document.getElementById('chim-stage');
    const panel = document.getElementById('chim-game-panel');
    if (startWrap) startWrap.hidden = on;
    if (stage) stage.classList.toggle('chim-stage-live', on);
    if (panel) panel.classList.toggle('chim-game-panel-live', on);
  }

  function bindSlingReplay() {
    const sling = document.getElementById('chim-sling');
    if (!sling || sling.dataset.bound) return;
    sling.dataset.bound = '1';
    sling.addEventListener('click', () => {
      if (!AudioFx || !currentQuestion) return;
      AudioFx.unlock();
      AudioFx.speakQuestion(currentQuestion, { force: true });
    });
  }

  async function init() {
    setActiveSkuNav('chim');
    if (AudioFx) {
      AudioFx.ensurePrefsInitialized();
      AudioFx.syncToggleUiOnce();
      AudioFx.init().catch((e) => console.warn(e));
    }
    bindSlingReplay();
    try {
      bootstrap = await getBootstrap(CHIM_MODE);
      activeGrade = resolveGradeFromBootstrap();
      activeTier = gradeToTier(activeGrade);
      renderBlocks();
      renderGradePicker();
      questionSession = createSession(activeGrade);
      renderQuestionPreview();
      spawnTarget();
      updateProfileBar(profileLine());
      updateHud();
    } catch (e) {
      console.error(e);
    }

    const startBtn = document.getElementById('chim-start');
    if (startBtn && !startBtn.dataset.bound) {
      startBtn.dataset.bound = '1';
      startBtn.addEventListener('click', () => {
        if (AudioFx) AudioFx.unlock();
        focusPlayArea();
        startPrairie();
      });
    }
    bindAutoSave();
  }

  function bindAutoSave() {
    if (window.__chimAutoSaveBound) return;
    window.__chimAutoSaveBound = true;
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden' && playing && sessionId) {
        finalizeSession({ quiet: true });
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (AudioFx) {
      AudioFx.ensurePrefsInitialized();
      AudioFx.syncToggleUiOnce();
    }
    bindAutoSave();
    const run = () => init();
    if (window.GameAuth) GameAuth.ready().then(run);
    else run();
    window.addEventListener('gameAuthRestored', () => init().catch(console.error));
  });
})();
