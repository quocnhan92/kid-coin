(function () {
  let selectedSubjectId = null;
  let selectedChapterId = null;

  async function adminApi(path, opts) {
    const res = await fetch('/api/v1/admin/learning' + path, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  window.loadSubjects = async function () {
    const grade = document.getElementById('filter-grade').value;
    const q = grade ? '?grade=' + grade : '';
    const rows = await adminApi('/subjects' + q);
    const el = document.getElementById('subject-list');
    el.innerHTML = rows.map(s =>
      `<div style="padding:8px;border-bottom:1px solid #eee;cursor:pointer" onclick="selectSubject('${s.id}','${s.name}')">
        <strong>${s.icon} ${s.name}</strong><br><small>Lớp ${s.id.split('-').pop()?.replace('g','') || '?'} · ${s.id}</small>
      </div>`
    ).join('') || '<p>Chưa có môn</p>';
  };

  window.selectSubject = async function (id, name) {
    selectedSubjectId = id;
    selectedChapterId = null;
    document.getElementById('sel-subject-label').textContent = '— ' + name;
    document.getElementById('sel-chapter-label').textContent = '';
    const rows = await adminApi('/subjects/' + id + '/chapters');
    document.getElementById('chapter-list').innerHTML = rows.map(c =>
      `<div style="padding:8px;border-bottom:1px solid #eee;cursor:pointer" onclick="selectChapter('${c.id}','${c.name}')">
        <strong>${c.name}</strong> ${c.is_published ? '✅' : '⏳'}<br><small>${c.subtitle || ''}</small>
      </div>`
    ).join('') || '<p>Chưa có chủ đề</p>';
    document.getElementById('lesson-list').innerHTML = '';
  };

  window.selectChapter = async function (id, name) {
    selectedChapterId = id;
    document.getElementById('sel-chapter-label').textContent = '— ' + name;
    const rows = await adminApi('/chapters/' + id + '/lessons');
    document.getElementById('lesson-list').innerHTML = rows.map(l =>
      `<div style="padding:8px;border-bottom:1px solid #eee;cursor:pointer" onclick="selectLesson('${l.id}','${l.title.replace(/'/g, "\\'")}','${l.content_type}')">
        <strong>${l.title}</strong> ${l.is_published ? '✅' : '⏳'} · ${l.duration_min}p · ${l.content_type}
      </div>`
    ).join('') || '<p>Chưa có bài</p>';
    document.getElementById('step-list').innerHTML = '';
  };

  let selectedLessonId = null;

  window.selectLesson = async function (id, name, contentType) {
    selectedLessonId = id;
    document.getElementById('sel-lesson-label').textContent = '— ' + name + ' (' + contentType + ')';
    if (contentType !== 'guided') {
      document.getElementById('step-list').innerHTML = '<p>Chỉ bài guided mới có steps.</p>';
      return;
    }
    const steps = await adminApi('/lessons/' + id + '/steps');
    document.getElementById('step-list').innerHTML = steps.map(s =>
      `<div style="padding:6px;border-bottom:1px solid #eee;font-size:13px">
        ${s.emoji_icon} #${s.sort_index} ${s.step_type}
      </div>`
    ).join('') || '<p>Chưa có bước</p>';
  };

  window.addGuidedStep = async function () {
    if (!selectedLessonId) return alert('Chọn bài guided trước');
    const step_type = document.getElementById('new-step-type').value;
    const emoji_icon = document.getElementById('new-step-emoji').value || '👀';
    let config_json = {};
    try {
      config_json = JSON.parse(document.getElementById('new-step-json').value || '{}');
    } catch (e) { return alert('JSON config không hợp lệ'); }
    const sort_index = parseInt(document.getElementById('new-step-sort').value, 10) || 0;
    await adminApi('/lessons/' + selectedLessonId + '/steps', {
      method: 'POST',
      body: JSON.stringify({ sort_index, step_type, emoji_icon, config_json }),
    });
    selectLesson(selectedLessonId, '', 'guided');
  };

  window.createSubject = async function () {
    const id = document.getElementById('new-subj-id').value.trim();
    const name = document.getElementById('new-subj-name').value.trim();
    const grade = parseInt(document.getElementById('new-subj-grade').value, 10);
    if (!id || !name) return alert('Nhập id và tên');
    await adminApi('/subjects', { method: 'POST', body: JSON.stringify({ id, name, grade }) });
    loadSubjects();
  };

  window.createChapter = async function () {
    if (!selectedSubjectId) return alert('Chọn môn trước');
    const name = document.getElementById('new-ch-name').value.trim();
    const subtitle = document.getElementById('new-ch-sub').value.trim();
    if (!name) return alert('Nhập tên chủ đề');
    await adminApi('/chapters', { method: 'POST', body: JSON.stringify({ subject_id: selectedSubjectId, name, subtitle }) });
    selectSubject(selectedSubjectId, name);
  };

  window.createLesson = async function () {
    if (!selectedChapterId) return alert('Chọn chủ đề trước');
    const title = document.getElementById('new-lesson-title').value.trim();
    let content_json = {};
    try {
      content_json = JSON.parse(document.getElementById('new-lesson-json').value || '{}');
    } catch (e) { return alert('JSON không hợp lệ'); }
    if (!title) return alert('Nhập tiêu đề');
    await adminApi('/lessons', {
      method: 'POST',
      body: JSON.stringify({ chapter_id: selectedChapterId, title, content_json, content_type: 'quiz', is_published: true }),
    });
    selectChapter(selectedChapterId, title);
  };

  window.publishChapter = async function () {
    if (!selectedChapterId) return alert('Chọn chủ đề');
    await adminApi('/chapters/' + selectedChapterId + '/publish', { method: 'POST' });
    alert('Đã publish!');
    if (selectedSubjectId) selectSubject(selectedSubjectId, '');
  };

  loadSubjects();
})();
