(function () {
  'use strict';

  const API = '/api/v1/learning';
  let state = {
    grade: 1,
    color: '#E85D24',
    bg: '#FAECE7',
    dark: '#993C1D',
    subject: null,
    subjectId: '',
    chapterId: null,
    chapters: [],
    lessonId: null,
    lessonStart: 0,
    returnScreen: 's4',
    soundOn: true,
    player: { questions: [], index: 0, answers: [], type: 'quiz' },
  };

  async function api(path, opts) {
    const res = await fetch(API + path, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...(opts && opts.headers) },
      ...opts,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  function $(id) { return document.getElementById(id); }

  function goScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    $(id).classList.add('active');
    const msgs = { s0: 'Lịch học hôm nay! 📅', s1: 'Chọn lớp nha! 🌟', s2: 'Chọn môn học! 📚', s3: 'Chọn chủ đề! 🎯', s4: 'Chọn bài học! 📖', s5: 'Cùng làm bài nào! ✏️' };
    showMascotSpeech(msgs[id] || 'Cùng học vui! 🎉');
    const guideMap = { s0: 'learning_schedule', s1: 'learning_home', s2: 'learning_subjects', s3: 'learning_map', s4: 'learning_map', s5: 'learning_lesson' };
    if (window.FeatureGuide && guideMap[id]) FeatureGuide.setFabGuide(guideMap[id]);
    requestAnimationFrame(layoutLearningViewport);
  }

  const REF_VIEWPORT = { w: 390, h: 844 };

  function layoutLearningViewport() {
    const vv = window.visualViewport;
    const vw = Math.round(vv?.width ?? window.innerWidth);
    const vh = Math.round(vv?.height ?? window.innerHeight);
    const root = document.documentElement;
    const frame = document.querySelector('.phone-frame');
    const narrow = vw <= 480;

    const scaleW = vw / REF_VIEWPORT.w;
    const scaleH = vh / REF_VIEWPORT.h;
    const scale = Math.max(0.78, Math.min(1.1, Math.min(scaleW, scaleH)));

    const pageEl = document.querySelector('.learning-page');
    const availW = pageEl?.clientWidth ?? vw;
    const availH = pageEl?.clientHeight ?? vh;

    const pagePad = narrow ? 0 : Math.round(10 * scale);
    const frameW = narrow ? availW : Math.min(420, availW);
    const frameH = Math.max(320, availH);

    root.style.setProperty('--lv-scale', String(scale));
    root.style.setProperty('--lv-vw', vw + 'px');
    root.style.setProperty('--lv-vh', vh + 'px');
    root.style.setProperty('--lv-page-pad', pagePad + 'px');
    root.style.setProperty('--lv-frame-w', frameW + 'px');
    root.style.setProperty('--lv-frame-h', frameH + 'px');
    root.style.setProperty('--lv-radius-frame', narrow ? '0px' : Math.round(28 * scale) + 'px');
    root.style.setProperty('--lv-touch', Math.max(40, Math.round(44 * scale)) + 'px');

    if (frame) {
      frame.style.width = frameW + 'px';
      frame.style.height = frameH + 'px';
    }

    if ($('s3')?.classList.contains('active') && state.chapters?.length) {
      drawConnectors(state.chapters);
    }
    layoutTeacherPanel();
    if ($('s1')?.classList.contains('active')) layoutGradeGrid();
  }

  function layoutGradeGrid() {
    const grid = $('grade-grid');
    if (!grid) return;
    const items = [...grid.querySelectorAll('.grade-btn')];
    const n = items.length;
    if (!n) return;

    const frameW = grid.clientWidth || window.innerWidth;
    let cols = 3;
    if (n <= 2) cols = n;
    else if (n >= 10 && frameW >= 340) cols = 4;

    grid.style.setProperty('--grade-cols', String(cols));
    items.forEach(btn => { btn.style.gridColumn = ''; });

    const remainder = n % cols;
    if (remainder > 0) {
      const lastItems = items.slice(-remainder);
      if (remainder === 1) {
        lastItems[0].style.gridColumn = String(Math.ceil(cols / 2));
      } else if (remainder === 2 && cols >= 3) {
        lastItems[0].style.gridColumn = '1';
        lastItems[1].style.gridColumn = String(cols);
      } else {
        const start = Math.floor((cols - remainder) / 2) + 1;
        lastItems.forEach((btn, i) => { btn.style.gridColumn = String(start + i); });
      }
    }

    requestAnimationFrame(() => {
      grid.classList.toggle('grade-grid--scroll', grid.scrollHeight > grid.clientHeight + 2);
    });
  }

  function speakText(text) {
    if (!state.soundOn || !window.speechSynthesis) return null;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'vi-VN';
    u.rate = 0.9;
    speechSynthesis.speak(u);
    return u;
  }

  function speakKaraoke(text, onWordIndex, onEnd) {
    if (!state.soundOn || !window.speechSynthesis) {
      if (onEnd) onEnd();
      return null;
    }
    speechSynthesis.cancel();
    const words = (text || '').trim().split(/\s+/).filter(Boolean);
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'vi-VN';
    u.rate = 0.82;
    let wi = 0;
    let ended = false;
    const finish = () => {
      if (ended) return;
      ended = true;
      clearInterval(timer);
      if (onWordIndex) onWordIndex(words.length);
      if (onEnd) onEnd();
    };
    u.onboundary = (ev) => {
      if (ev.name === 'word' && onWordIndex) {
        onWordIndex(Math.min(wi, words.length - 1));
        wi++;
      }
    };
    u.onend = finish;
    u.onerror = finish;
    const timer = setInterval(() => {
      if (wi < words.length && onWordIndex) {
        onWordIndex(wi);
        wi++;
      }
    }, 420);
    speechSynthesis.speak(u);
    return u;
  }

  function showMascotSpeech(text) {
    const b = $('mascot-speech');
    if (!b) return;
    b.textContent = text;
    b.classList.add('show');
    clearTimeout(b._t);
    b._t = setTimeout(() => b.classList.remove('show'), 3000);
  }

  function showModal(emoji, title, desc, onOk) {
    $('modal-emoji').textContent = emoji;
    $('modal-title').textContent = title;
    $('modal-desc').textContent = desc;
    $('modal').classList.add('show');
    $('modal-ok').onclick = () => { closeModal(); if (onOk) onOk(); };
  }

  function closeModal() { $('modal').classList.remove('show'); }

  const statusMap = {
    done: { badge: 'badge-done', label: 'Đã xong', fill: '#4CAF50', stroke: '#2E7D32' },
    partial: { badge: 'badge-partial', label: 'Đang học', fill: '#FFB74D', stroke: '#E65100' },
    empty: { badge: 'badge-empty', label: 'Chưa học', fill: '#B0BEC5', stroke: '#78909C' },
  };

  function lessonTypeLabel(les) {
    if (les.content_type === 'guided') return '🎓 Giáo viên online';
    if (les.content_type === 'read') return '📖 Đọc hiểu';
    return '📝 Bài kiểm tra';
  }

  function teacherStatusClass(les) {
    if (les.status === 'completed') return 'teacher-item--completed';
    if (les.status === 'in_progress') return 'teacher-item--in_progress';
    return 'teacher-item--not_started';
  }

  function teacherStatusBadge(les) {
    if (les.already_completed) return '🔁 Ôn lại';
    if (les.status === 'completed') return '✅ Xong';
    if (les.status === 'in_progress') return '▶ Đang học';
    return '';
  }

  const VISIBLE_TEACHER_ROWS = 5;

  function layoutTeacherPanel() {
    const s2 = $('s2');
    const panel = $('teacher-panel');
    const list = $('teacher-panel-list');
    if (!s2?.classList.contains('active') || !panel || !list || panel.classList.contains('hide')) return;

    const frame = document.querySelector('.phone-frame');
    if (!frame) return;

    const vh = window.visualViewport?.height || window.innerHeight;
    const frameH = frame.getBoundingClientRect().height;

    const topNav = document.querySelector('.learning-top-nav');
    const topBar = s2.querySelector('.top-bar');
    const panelHead = panel.querySelector('.teacher-panel-head');
    const subjectSection = s2.querySelector('.subject-section');
    const subjectGrid = $('subject-grid');
    const cardCount = subjectGrid?.querySelectorAll('.subject-card').length || 6;

    const scale = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--lv-scale')) || 1;
    const cardEstH = Math.round(72 * scale);
    const subjectRows = Math.ceil(cardCount / 2);
    const labelH = subjectSection?.querySelector('.subject-section-label')?.offsetHeight || Math.round(28 * scale);
    const subjectNeed = labelH + subjectRows * cardEstH + Math.max(0, subjectRows - 1) * 10 + 12;
    const subjectReserve = Math.max(Math.round(140 * scale), Math.min(subjectNeed, Math.round(frameH * 0.48)));

    const chrome =
      (topNav?.offsetHeight || 0) +
      (topBar?.offsetHeight || 0) +
      (panelHead?.offsetHeight || 0) +
      20;

    const sample = list.querySelector('.teacher-item');
    const rowH = sample ? sample.offsetHeight + 8 : Math.round(56 * scale);
    const idealList = rowH * VISIBLE_TEACHER_ROWS - 8;
    const maxFromFrame = frameH - chrome - subjectReserve;
    const maxFromViewport = Math.round(vh * 0.34);

    const listH = Math.max(96, Math.min(idealList, maxFromFrame, maxFromViewport));
    list.style.maxHeight = listH + 'px';
    document.documentElement.style.setProperty('--teacher-list-h', listH + 'px');
  }

  function teacherLessonMeta(les) {
    const ctype = les.content_type || 'quiz';
    let typeLabel = `📝 ${les.step_count || 3} câu`;
    if (ctype === 'guided') typeLabel = `🎓 ${les.step_count || 0} bước`;
    else if (ctype === 'read') typeLabel = '📖 đọc hiểu';
    return `${les.subject_icon} ${les.subject_name} · ${typeLabel} · ⏱ ${les.duration_min} phút`;
  }

  function renderTeacherPanel(lessons) {
    const panel = $('teacher-panel');
    const list = $('teacher-panel-list');
    const hint = $('teacher-scroll-hint');
    if (!panel || !list) return;

    if (!lessons.length) {
      panel.classList.add('hide');
      return;
    }

    panel.classList.remove('hide');
    list.innerHTML = '';
    let scrollTarget = null;

    lessons.forEach(les => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'teacher-item ' + teacherStatusClass(les);
      const stars = les.stars ? `<span class="teacher-item-stars">${'⭐'.repeat(les.stars)}</span>` : '';
      const badge = teacherStatusBadge(les);
      btn.innerHTML = `
        <span class="teacher-item-emoji">${les.progress_emoji || '🎓'}</span>
        <span class="teacher-item-body">
          <div class="teacher-item-title">${les.title} ${stars}</div>
          <div class="teacher-item-meta">${teacherLessonMeta(les)}</div>
        </span>
        ${badge ? `<span class="teacher-item-badge">${badge}</span>` : ''}`;
      btn.onclick = () => startLesson({ id: les.id, title: les.title, content_type: les.content_type || 'quiz' });
      if (les.status === 'in_progress' && !scrollTarget) scrollTarget = btn;
      list.appendChild(btn);
    });

    if (lessons.length > 5 && hint) {
      hint.classList.remove('hide');
      setTimeout(() => hint.classList.add('hide'), 3000);
    } else if (hint) {
      hint.classList.add('hide');
    }

    if (scrollTarget) {
      requestAnimationFrame(() => scrollTarget.scrollIntoView({ block: 'nearest', behavior: 'smooth' }));
    }
    requestAnimationFrame(layoutLearningViewport);
  }

  async function loadTeacherLessons(grade) {
    const panel = $('teacher-panel');
    const list = $('teacher-panel-list');
    if (!panel || !list) return;
    panel.classList.remove('hide');
    list.innerHTML = '<p class="teacher-loading">Đang tải tiết…</p>';
    try {
      const data = await api('/grades/' + grade + '/teacher-lessons');
      const lessons = data.lessons || [];
      const sub = document.querySelector('.teacher-panel-sub');
      if (sub && data.total > 0) {
        sub.textContent = `${data.total} bài — vuốt xem hết danh sách`;
      } else if (sub) {
        sub.textContent = 'Tiết 30 phút — máy đọc, bé làm theo từng bước';
      }
      renderTeacherPanel(lessons);
    } catch (_) {
      list.innerHTML = '<p class="teacher-loading">Không tải được. Thử lại sau nhé!</p>';
    }
  }

  async function loadGrades() {
    try {
      const data = await api('/grades');
      const grid = $('grade-grid');
      grid.innerHTML = '';
      data.grades.forEach(g => {
        const btn = document.createElement('button');
        btn.className = 'grade-btn';
        btn.style.borderColor = g.color_bg;
        btn.innerHTML = `<span class="grade-num" style="color:${g.color_primary}">${g.grade}</span><span class="grade-label">${g.label}</span><span class="grade-stars">${g.stars_hint}</span>`;
        btn.onclick = () => goSubjects(g);
        grid.appendChild(btn);
      });
      layoutGradeGrid();
    } catch (e) {
      $('grade-grid').innerHTML = '<p style="text-align:center;padding:1rem;color:#993C1D">Không tải được dữ liệu. Đăng nhập lại hoặc chạy migration 024.</p>';
      $('daily-badge').textContent = 'Lỗi kết nối API';
    }
  }

  async function loadToday() {
    try {
      const t = await api('/me/today');
      $('daily-badge').textContent = `Hôm nay: ${t.minutes_studied}/${t.goal_min}–${t.goal_max} phút · ${t.lessons_completed} bài`;
    } catch (_) { /* guest */ }
  }

  async function goSubjects(g) {
    state.grade = g.grade;
    state.color = g.color_primary;
    state.bg = g.color_bg;
    state.dark = g.color_dark;
    $('s2-title').textContent = 'Lớp ' + g.grade;
    const badge = $('s2-badge');
    badge.textContent = 'Lớp ' + g.grade;
    badge.style.background = g.color_bg;
    badge.style.color = g.color_dark;

    const data = await api('/grades/' + g.grade + '/subjects');
    const grid = $('subject-grid');
    grid.innerHTML = '';
    data.subjects.forEach(s => {
      const card = document.createElement('div');
      card.className = 'subject-card';
      card.style.borderTop = '3px solid ' + s.color_primary;
      card.innerHTML = `
        <div class="subject-card-top">
          <span class="subject-icon">${s.icon}</span>
          <span class="subject-name">${s.name}</span>
        </div>
        <div class="subject-desc">${s.description || ''}</div>
        <div class="subject-card-foot">
          <span class="subject-tag tag-required">${s.is_required ? '✓ Bắt buộc' : 'Tự chọn'}</span>
          <span class="subject-progress">${s.chapters_done}/${s.chapters_total} · ${s.progress_pct}%</span>
        </div>`;
      card.onclick = () => { speakText('Môn ' + s.name); goChapters(s); };
      grid.appendChild(card);
    });
    loadTeacherLessons(g.grade);
    goScreen('s2');
    requestAnimationFrame(layoutTeacherPanel);
  }

  async function goChapters(subject) {
    state.subject = subject;
    state.subjectId = subject.id;
    state.color = subject.color_primary;
    state.bg = subject.color_bg;
    state.dark = subject.color_dark;

    const data = await api('/subjects/' + subject.id + '/map');
    const sub = data.subject;
    $('s3-title').textContent = sub.name;
    $('s3-breadcrumb').textContent = `Lớp ${sub.grade} → ${sub.name}`;
    $('s3-icon-title').textContent = sub.icon + ' ' + sub.name;
    $('s3-desc').textContent = sub.description || '';
    const badge = $('s3-badge');
    badge.textContent = 'Lớp ' + sub.grade;
    badge.style.background = sub.color_bg;
    badge.style.color = sub.color_dark;

    $('overall-fill').style.width = data.overall.progress_pct + '%';
    $('overall-fill').style.background = sub.color_primary;
    $('progress-label').textContent = `${data.overall.done}/${data.overall.total} chủ đề hoàn thành` +
      (data.overall.partial ? ` (${data.overall.partial} đang học)` : '');

    state.chapters = data.chapters;
    renderMap(data.chapters);
    goScreen('s3');
  }

  function renderMap(chapters) {
    const list = $('chapter-list');
    list.innerHTML = '';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'connector');
    svg.id = 'connector-svg';
    list.appendChild(svg);

    chapters.forEach((ch, i) => {
      const st = statusMap[ch.status] || statusMap.empty;
      const stars = ch.stars > 0 ? '⭐'.repeat(ch.stars) + '☆'.repeat(3 - ch.stars) : '☆☆☆';
      const row = document.createElement('div');
      row.className = 'waypoint-row ' + (i % 2 === 0 ? 'odd' : 'even');
      row.innerHTML = `
        <div class="waypoint-marker"><svg viewBox="0 0 40 40"><polygon points="20,4 36,34 4,34" fill="${st.fill}" stroke="${st.stroke}" stroke-width="2"/><text x="20" y="28" text-anchor="middle" fill="white" font-size="12" font-weight="bold">${i + 1}</text></svg></div>
        <div class="waypoint-label"><div class="chapter-name">${ch.name}</div><div class="chapter-sub">${ch.subtitle || ''}</div>
        <div style="margin-top:4px"><span class="chapter-status-badge ${st.badge}">${st.label}</span> <span>${stars}</span></div></div>`;
      row.onclick = () => { speakText(ch.name); openChapter(ch); };
      list.appendChild(row);
    });
    requestAnimationFrame(() => drawConnectors(chapters));
  }

  function drawConnectors(chapters) {
    const svg = $('connector-svg');
    const container = $('chapter-list');
    if (!svg || !container) return;
    const cr = container.getBoundingClientRect();
    const rows = container.querySelectorAll('.waypoint-row');
    svg.innerHTML = '';
    for (let i = 0; i < rows.length - 1; i++) {
      const m1 = rows[i].querySelector('.waypoint-marker');
      const m2 = rows[i + 1].querySelector('.waypoint-marker');
      if (!m1 || !m2) continue;
      const r1 = m1.getBoundingClientRect();
      const r2 = m2.getBoundingClientRect();
      const x1 = r1.left + r1.width / 2 - cr.left;
      const y1 = r1.top + r1.height / 2 - cr.top;
      const x2 = r2.left + r2.width / 2 - cr.left;
      const y2 = r2.top + r2.height / 2 - cr.top;
      const done = chapters[i].status === 'done' && chapters[i + 1].status === 'done';
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', `M ${x1} ${y1} C ${x1} ${(y1 + y2) / 2}, ${x2} ${(y1 + y2) / 2}, ${x2} ${y2}`);
      path.setAttribute('stroke', done ? '#4CAF50' : '#B0BEC5');
      path.setAttribute('stroke-width', '3');
      path.setAttribute('fill', 'none');
      if (!done) path.setAttribute('stroke-dasharray', '6,4');
      svg.appendChild(path);
    }
  }

  async function openChapter(ch) {
    state.chapterId = ch.id;
    $('s4-title').textContent = ch.name;
    const data = await api('/chapters/' + ch.id + '/lessons');
    const list = $('lesson-list');
    list.innerHTML = '';
    data.lessons.forEach((les, i) => {
      const el = document.createElement('div');
      const isGuided = les.content_type === 'guided';
      el.className = 'lesson-item' + (les.status === 'completed' ? ' done' : '') + (isGuided ? ' guided' : '');
      el.innerHTML = `<div class="lesson-num">${isGuided ? '🎓' : i + 1}</div><div class="lesson-meta">${isGuided ? '<span class="teacher-badge">Giáo viên online</span>' : ''}<div class="lesson-title">${les.title}</div><div class="lesson-dur">⏱ ${les.duration_min} phút · ${lessonTypeLabel(les)} · ${les.already_completed ? '🔁 Ôn lại' : les.status === 'completed' ? '✅ Xong' : '▶ Học'}</div></div><span>${les.stars ? '⭐'.repeat(les.stars) : ''}</span>`;
      el.onclick = () => startLesson(les);
      list.appendChild(el);
    });
    goScreen('s4');
  }

  let guidedPlayer = null;

  async function goTodaySchedule() {
    state.grade = state.grade || 1;
    $('s0-title').textContent = 'Lớp ' + state.grade + ' — Hôm nay';
    try {
      const data = await api('/schedule/today?grade=' + state.grade);
      $('schedule-badge').textContent = `${data.week_label} · ${data.daily_goal.completed}/${data.daily_goal.target_lessons} tiết`;
      const list = $('schedule-list');
      list.innerHTML = '';
      (data.slots || []).forEach(sl => {
        const les = sl.lesson;
        const done = les && les.status === 'completed';
        const el = document.createElement('div');
        el.className = 'schedule-slot' + (done ? ' done' : '');
        const sessionLabel = sl.session === 'morning' ? 'Buổi sáng' : 'Buổi chiều';
        el.innerHTML = `
          <div class="slot-session">${sessionLabel} · ${sl.subject.icon} ${sl.subject.name}${les && les.content_type === 'guided' ? ' · 🎓 GV online' : ''}</div>
          <div class="slot-title">${les ? les.title : 'Chưa có bài'}</div>
          <div class="lesson-dur">${les ? '⏱ ' + les.duration_min + ' phút · ' + (les.content_type === 'guided' ? '🎓 ' : '') + (done ? '✅' : '▶') : ''}</div>`;
        if (les) el.onclick = () => startLesson({ id: les.id, title: les.title, content_type: les.content_type });
        list.appendChild(el);
      });
      goScreen('s0');
    } catch (e) {
      showMascotSpeech('Chưa có lịch hôm nay, chọn lớp trước nhé!');
    }
  }
  window.goTodaySchedule = goTodaySchedule;

  function initGuidedPlayer() {
    if (guidedPlayer || !window.LearningGuidedPlayer) return;
    guidedPlayer = window.LearningGuidedPlayer.create({
      api, speakText, speakKaraoke, showMascotSpeech, showModal, state,
      goScreen, goChapters, loadToday, navigateAfterLesson,
    });
  }

  async function navigateAfterLesson(refreshList) {
    const target = state.returnScreen || 's4';
    if (target === 's2') {
      goScreen('s2');
      if (refreshList !== false && state.grade) await loadTeacherLessons(state.grade);
      requestAnimationFrame(layoutLearningViewport);
      return;
    }
    if (target === 's0') {
      goScreen('s0');
      return;
    }
    if (target === 's4' && state.chapterId) {
      const ch = (state.chapters || []).find(c => c.id === state.chapterId);
      if (ch) {
        await openChapter(ch);
        return;
      }
      goScreen('s4');
      return;
    }
    if (state.subjectId && state.subject && target === 's3') {
      goChapters(state.subject);
      return;
    }
    goScreen(target);
  }

  function backFromLesson() {
    navigateAfterLesson(false);
  }

  async function startLesson(les) {
    try {
      const activeScreen = document.querySelector('.screen.active');
      state.returnScreen = activeScreen?.id || 's4';
      state.lessonId = les.id;
      state.lessonStart = Date.now();
      const data = await api('/lessons/' + les.id);
      $('s5-title').textContent = data.title;
      const body = $('player-body');
      body.innerHTML = '<div id="player-feedback" class="player-feedback hide"></div>';
      $('finish-lesson-btn').style.display = 'none';

      if (data.content_type === 'guided') {
        initGuidedPlayer();
        if (guidedPlayer) {
          if (data.is_replay) showMascotSpeech('Ôn lại bài nhé — điểm lần đầu vẫn giữ! 🔁');
          state.player = { type: 'guided' };
          await guidedPlayer.start(les.id, body, $('s5-title'));
          goScreen('s5');
          return;
        }
      }

      const content = data.content || {};

      if (data.content_type === 'read' && (content.blocks || content.passage)) {
        const readQs = content.questions || (content.check_question ? [content.check_question] : []);
        state.player = { type: 'read', questions: readQs, index: 0, answers: [], busy: false };
        if (content.passage && content.passage.length) {
          const passageEl = document.createElement('div');
          passageEl.className = 'read-passage';
          const title = content.passage_title || '';
          if (title) {
            const h = document.createElement('div');
            h.className = 'read-passage-title';
            h.textContent = '«' + title + '»';
            passageEl.appendChild(h);
          }
          const segments = content.passage_segments;
          if (segments && segments.length) {
            segments.forEach(seg => {
              const para = document.createElement('div');
              para.className = 'read-passage-para';
              seg.forEach(sent => {
                const p = document.createElement('p');
                p.className = 'read-passage-sentence';
                p.textContent = sent;
                para.appendChild(p);
              });
              passageEl.appendChild(para);
            });
          } else {
            content.passage.forEach(sent => {
              const p = document.createElement('p');
              p.className = 'read-passage-sentence';
              p.textContent = sent;
              passageEl.appendChild(p);
            });
          }
          body.appendChild(passageEl);
        }
        (content.blocks || []).forEach(b => {
          const d = document.createElement('div');
          d.className = 'read-block';
          d.textContent = (b.emoji || '') + ' ' + b.text;
          body.appendChild(d);
        });
        if (readQs.length) renderQuizStep();
        else body.innerHTML += '<p style="text-align:center;margin-top:1rem">Đọc xong rồi! Nhấn Hoàn thành nhé.</p>';
        $('finish-lesson-btn').style.display = readQs.length ? 'none' : 'inline-block';
      } else {
        state.player = { type: 'quiz', questions: content.questions || [], index: 0, answers: [], busy: false };
        $('finish-lesson-btn').style.display = 'none';
        if (!state.player.questions.length) {
          body.innerHTML += '<p style="text-align:center;margin-top:1rem;color:#993C1D">Bài học chưa có nội dung câu hỏi.</p>';
        } else {
          renderQuizStep();
        }
      }
      if (data.is_replay) showMascotSpeech('Ôn lại bài nhé — điểm lần đầu vẫn giữ! 🔁');
      goScreen('s5');
    } catch (e) {
      showMascotSpeech('Không mở được bài học. Thử lại nhé! 😅');
      console.error(e);
    }
  }

  function renderQuizStep() {
    const body = $('player-body');
    const q = state.player.questions[state.player.index];
    if (!q) { finishLesson(); return; }
    const existing = body.querySelector('.player-quiz-wrap');
    if (existing) existing.remove();
    const wrap = document.createElement('div');
    wrap.className = 'player-quiz-wrap';
    wrap.innerHTML = `<div class="player-q">${state.player.index + 1}/${state.player.questions.length}. ${q.prompt}</div><div class="player-choices" id="choices"></div>`;
    body.appendChild(wrap);
    const choices = $('choices');
    (q.choices || []).forEach((c, idx) => {
      const btn = document.createElement('button');
      btn.className = 'player-choice';
      btn.textContent = c;
      btn.onclick = () => selectAnswer(idx, q.answer_index, btn);
      choices.appendChild(btn);
    });
  }

  function renderQuestion(q) {
    const body = $('player-body');
    const wrap = document.createElement('div');
    wrap.innerHTML = `<div class="player-q">${q.prompt}</div><div class="player-choices" id="choices"></div>`;
    body.appendChild(wrap);
    const choices = $('choices');
    (q.choices || []).forEach((c, idx) => {
      const btn = document.createElement('button');
      btn.className = 'player-choice';
      btn.textContent = c;
      btn.onclick = () => selectAnswer(idx, q.answer_index, btn);
      choices.appendChild(btn);
    });
  }

  function showWrongFeedback() {
    const msg = 'Gần đúng rồi, cố lên nhé';
    showMascotSpeech(msg + '! 💪');
    speakText(msg);
    let fb = $('player-feedback');
    if (!fb) {
      fb = document.createElement('div');
      fb.id = 'player-feedback';
      fb.className = 'player-feedback';
      const body = $('player-body');
      if (body) body.insertBefore(fb, body.firstChild);
    }
    fb.textContent = '💪 ' + msg + '!';
    fb.classList.remove('hide');
    clearTimeout(fb._t);
    fb._t = setTimeout(() => fb.classList.add('hide'), 2500);
  }

  function setChoicesLocked(locked) {
    document.querySelectorAll('.player-choice').forEach(btn => {
      btn.disabled = locked;
      btn.style.pointerEvents = locked ? 'none' : '';
      btn.style.opacity = locked ? '0.6' : '';
    });
  }

  function selectAnswer(selected, correct, btnEl) {
    if (state.player.busy) return;
    const sel = Number(selected);
    const cor = Number(correct);
    if (sel !== cor) {
      state.player.busy = true;
      if (btnEl) {
        btnEl.classList.add('wrong');
        setTimeout(() => btnEl.classList.remove('wrong'), 600);
      }
      setChoicesLocked(true);
      showWrongFeedback();
      setTimeout(() => {
        setChoicesLocked(false);
        state.player.busy = false;
      }, 700);
      return;
    }
    state.player.busy = true;
    setChoicesLocked(true);
    if (btnEl) btnEl.classList.add('correct');
    state.player.answers[state.player.index] = { question_index: state.player.index, selected: sel };
    const fb = $('player-feedback');
    if (fb) fb.classList.add('hide');
    if (state.player.type === 'quiz') {
      state.player.index++;
      if (state.player.index < state.player.questions.length) {
        setTimeout(() => renderQuizStep(), 400);
      } else {
        state.player.busy = false;
        finishLesson();
      }
    } else if (state.player.type === 'read') {
      state.player.index++;
      if (state.player.index < state.player.questions.length) {
        setTimeout(() => renderQuizStep(), 400);
      } else {
        state.player.busy = false;
        finishLesson();
      }
    }
  }

  async function finishLesson() {
    const qs = state.player.questions;
    if (qs.length) {
      const allCorrect = qs.every((q, i) => {
        const a = state.player.answers[i];
        return a && a.selected === q.answer_index;
      });
      if (!allCorrect) {
        showMascotSpeech('Làm đúng hết các câu mới xong nhé! 📖');
        return;
      }
    }
    const score = 100;
    const timeSpent = Math.max(30, Math.round((Date.now() - state.lessonStart) / 1000));
    try {
      const res = await api('/lessons/' + state.lessonId + '/complete', {
        method: 'POST',
        body: JSON.stringify({ score, time_spent_sec: timeSpent, answers: state.player.answers }),
      });
      const stars = '⭐'.repeat(res.lesson.stars);
      const title = res.replay ? 'Ôn luyện xong!' : 'Giỏi lắm!';
      const desc = res.replay
        ? 'Bé ôn lại bài rồi — điểm lần đầu vẫn giữ nguyên nhé!'
        : `Bé đã làm đúng hết ${qs.length || 1} câu! ${stars}`;
      showModal('🎉', title, desc, () => navigateAfterLesson(true));
      loadToday();
    } catch (e) {
      showModal('😅', 'Lỗi', 'Không lưu được kết quả. Thử lại nhé!');
    }
  }

  window.goScreen = goScreen;
  window.backFromLesson = backFromLesson;
  window.toggleSound = function (btn) {
    state.soundOn = !state.soundOn;
    btn.textContent = state.soundOn ? '🔊' : '🔇';
    showMascotSpeech(state.soundOn ? 'Âm thanh bật! 🔊' : 'Âm thanh tắt! 🔇');
  };
  window.speakMascot = function () {
    const msgs = ['Cố lên bé ơi! 💪', 'Học vui quá! 🎉', 'Bé giỏi lắm! 🌟'];
    showMascotSpeech(msgs[Math.floor(Math.random() * msgs.length)]);
  };
  window.closeModal = closeModal;
  window.finishLessonManual = function () {
    if (state.player.questions && state.player.questions.length > 0) {
      showMascotSpeech('Làm đúng hết các câu mới xong nhé! 📖');
      return;
    }
    finishLesson();
  };

  $('modal').addEventListener('click', e => { if (e.target.id === 'modal') closeModal(); });
  window.addEventListener('resize', layoutLearningViewport);
  window.addEventListener('orientationchange', () => setTimeout(layoutLearningViewport, 120));
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', layoutLearningViewport);
    window.visualViewport.addEventListener('scroll', layoutLearningViewport);
  }

  layoutLearningViewport();
  loadGrades().then(loadToday);
  setTimeout(() => showMascotSpeech('Chào bé, cùng học nào! 🐱'), 800);
  if (window.FeatureGuide) {
    FeatureGuide.mountFab('learning_home');
    FeatureGuide.setFabGuide('learning_home');
  }
})();
