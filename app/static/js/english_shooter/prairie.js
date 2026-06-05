(function () {
  const {
    MODES,
    uuid,
    toast,
    getBootstrap,
    getStage,
    getThemes,
    sessionsBatch,
    eventsBatch,
    updateProfileBar,
    clearBootstrapCache,
  } = window.EnglishShooter;

  const CONTENT_PACK = 'vn_english_shooter_v1';
  const SYNC_EVERY = 2;

  let bootstrap = null;
  let sessionId = null;
  let clientSeq = 0;
  let items = [];
  let itemIndex = 0;
  let score = 0;
  let correctCount = 0;
  let pendingSinceSync = 0;
  let themeId = 'en_g1_family';
  let activeGrade = 1;
  let themes = [];
  let startedAt = null;

  function speak(text) {
    if (!window.speechSynthesis || !text) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = 0.9;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  }

  function setHud() {
    const scoreEl = document.getElementById('es-score');
    const goldEl = document.getElementById('es-gold');
    const progEl = document.getElementById('es-progress');
    if (scoreEl) scoreEl.textContent = `Score ${score}`;
    if (goldEl) goldEl.textContent = `🪙 ${bootstrap?.english?.gold ?? 0}`;
    if (progEl) progEl.textContent = `${itemIndex}/${items.length}`;
  }

  function buildChoices(item) {
    const opts = item.options || {};
    const correct = item.target_text;
    const distractors = (opts.distractors || []).filter((d) => d !== correct);
    const pool = [correct, ...distractors].slice(0, 4);
    while (pool.length < 4) pool.push(`word${pool.length}`);
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    return pool;
  }

  function renderItem() {
    const stage = document.getElementById('es-prairie-stage');
    const choicesEl = document.getElementById('es-choices');
    if (!stage || !choicesEl) return;
    if (itemIndex >= items.length) {
      endRun(true);
      return;
    }
    const item = items[itemIndex];
    const opts = item.options || {};
    const emoji = opts.emoji || '🎯';
    const prompt = opts.prompt_en || `Shoot: ${item.target_text}`;
    stage.querySelector('.es-target-word').textContent = `${emoji} ${item.target_text}`;
    document.getElementById('es-prompt').textContent = prompt;
    speak(prompt);

    const choices = buildChoices(item);
    choicesEl.innerHTML = '';
    choices.forEach((word) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'es-choice-btn';
      btn.textContent = word;
      btn.addEventListener('click', () => onAnswer(btn, word, item));
      choicesEl.appendChild(btn);
    });
    setHud();
  }

  async function flushEvents() {
    if (!sessionId || pendingSinceSync < 1) return;
    const n = pendingSinceSync;
    pendingSinceSync = 0;
    const batch = [];
    for (let i = 0; i < n; i++) {
      clientSeq += 1;
      batch.push({
        client_seq: clientSeq,
        occurred_at: new Date().toISOString(),
        event_type: 'answer',
        skill_unit_id: items[Math.max(0, itemIndex - 1)]?.id,
        correct: true,
        score_delta: 1,
      });
    }
    await eventsBatch(sessionId, batch);
    clearBootstrapCache();
    bootstrap = await getBootstrap(MODES.prairie);
    setHud();
  }

  async function onAnswer(btn, word, item) {
    const correct = word === item.target_text;
    if (!correct) {
      btn.classList.add('wrong');
      toast('Try again — no HP lost (Thử lại, không mất máu)');
      setTimeout(renderItem, 600);
      return;
    }
    btn.classList.add('correct');
    score += 10;
    correctCount += 1;
    pendingSinceSync += 1;
    itemIndex += 1;
    if (pendingSinceSync >= SYNC_EVERY) await flushEvents();
    setTimeout(renderItem, 400);
  }

  async function startSession() {
    sessionId = uuid();
    startedAt = new Date().toISOString();
    await sessionsBatch([
      {
        op: 'start',
        session_id: sessionId,
        game_id: 'english_shooter',
        game_mode_id: MODES.prairie,
        started_at: startedAt,
        content_pack_id: CONTENT_PACK,
      },
    ]);
  }

  async function endRun(completed) {
    if (!sessionId) return;
    const duration = startedAt
      ? Math.max(1, Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000))
      : 30;
    if (pendingSinceSync > 0) await flushEvents();
    const goldRemain = Math.max(0, correctCount % SYNC_EVERY) * 5;
    await sessionsBatch([
      {
        op: 'end',
        session_id: sessionId,
        ended_at: new Date().toISOString(),
        summary: {
          duration_s: duration,
          questions_count: items.length,
          correct_count: correctCount,
          accuracy: items.length ? correctCount / items.length : 0,
          score,
          stars: completed ? 3 : 1,
          summary_json: {
            play_mode: 'prairie',
            theme_id: themeId,
            grade: bootstrap?.english?.last_grade || 1,
            theme_completed: completed,
            live_synced: true,
            gold_earned: goldRemain,
          },
        },
      },
    ]);
    sessionId = null;
    clearBootstrapCache();
    bootstrap = await getBootstrap(MODES.prairie);
    if (completed) toast('Theme done! Gold saved (Hoàn thành chủ đề, vàng đã lưu)');
    setHud();
    document.getElementById('es-start-overlay').style.display = 'flex';
    document.getElementById('es-prairie-play').style.display = 'none';
  }

  async function startRun() {
    document.getElementById('es-start-overlay').style.display = 'none';
    document.getElementById('es-prairie-play').style.display = 'block';
    itemIndex = 0;
    score = 0;
    correctCount = 0;
    pendingSinceSync = 0;
    clientSeq = 0;
    const res = await getStage(themeId, 'vocab');
    items = res.stage?.items || [];
    if (!items.length) {
      toast('No questions yet — run seed catalog');
      return;
    }
    await startSession();
    renderItem();
  }

  function renderGradePicker() {
    const wrap = document.getElementById('es-grade-picker');
    if (!wrap) return;
    wrap.innerHTML = [1, 2, 3]
      .map(
        (g) =>
          `<button type="button" class="es-theme-btn ${g === activeGrade ? 'active' : ''}" data-grade="${g}">Grade ${g} <span class="es-vi">(Lớp ${g})</span></button>`
      )
      .join('');
    wrap.querySelectorAll('[data-grade]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        activeGrade = Number(btn.dataset.grade);
        await loadThemesForGrade(activeGrade);
        renderGradePicker();
        renderThemes();
      });
    });
  }

  async function loadThemesForGrade(grade) {
    const res = await getThemes(grade);
    themes = res.themes || [];
    if (themes.length && !themes.some((t) => t.id === themeId)) {
      themeId = themes[0].id;
    }
  }

  function renderThemes() {
    const wrap = document.getElementById('es-theme-list');
    if (!wrap) return;
    if (!themes.length) {
      wrap.innerHTML = '<p class="es-muted">No themes yet — run alembic upgrade head</p>';
      return;
    }
    wrap.innerHTML = themes
      .map(
        (t) =>
          `<button type="button" class="es-theme-btn ${t.id === themeId ? 'active' : ''}" data-theme="${t.id}">${t.title}</button>`
      )
      .join('');
    wrap.querySelectorAll('.es-theme-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        themeId = btn.dataset.theme;
        wrap.querySelectorAll('.es-theme-btn').forEach((b) => b.classList.toggle('active', b === btn));
      });
    });
  }

  async function init() {
    try {
      bootstrap = await getBootstrap(MODES.prairie);
      activeGrade = bootstrap?.english?.last_grade || 1;
      await loadThemesForGrade(activeGrade);
      renderGradePicker();
      renderThemes();
      setHud();
      await updateProfileBar(`Prairie · 🪙${bootstrap.english?.gold || 0}`);
    } catch (e) {
      if (e.message !== 'SESSION_AUTH_REQUIRED') toast(String(e.message));
    }
    document.getElementById('es-start-btn')?.addEventListener('click', startRun);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
