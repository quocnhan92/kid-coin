(function (global) {
  'use strict';

  function createGuidedPlayer(deps) {
    const { api, speakText, showMascotSpeech, showModal, state } = deps;
    let playerState = {
      lessonId: null,
      steps: [],
      index: 0,
      busy: false,
      lessonStart: 0,
      checkpointId: null,
      quizAnswers: [],
      quizIndex: 0,
    };

    function progressHtml() {
      const emojis = playerState.progressEmojis || ['🍏', '🍋', '🍇', '🎁'];
      return emojis.map((e, i) =>
        `<span class="step-emoji ${i < playerState.index ? 'done' : i === playerState.index ? 'active' : ''}">${e}</span>`
      ).join('');
    }

    function renderShell(body) {
      body.innerHTML = `
        <div class="guided-progress" id="guided-progress">${progressHtml()}</div>
        <div id="player-feedback" class="player-feedback hide"></div>
        <div id="guided-step" class="guided-step"></div>
      `;
    }

    function showFeedback(text, type) {
      let fb = document.getElementById('player-feedback');
      if (!fb) return;
      fb.textContent = (type === 'wrong' ? '💪 ' : '⭐ ') + text;
      fb.classList.remove('hide');
      clearTimeout(fb._t);
      fb._t = setTimeout(() => fb.classList.add('hide'), 2500);
    }

    async function submit(interaction, payload) {
      const step = playerState.steps[playerState.index];
      if (!step) return null;
      const timeSpent = Math.max(1, Math.round((Date.now() - playerState.lessonStart) / 1000));
      return api(`/lessons/${playerState.lessonId}/steps/${step.id}/submit`, {
        method: 'POST',
        body: JSON.stringify({ interaction, payload: payload || {}, time_spent_sec: timeSpent }),
      });
    }

    function advanceOrComplete(res) {
      if (res.lesson_complete && res.completion) {
        const c = res.completion;
        const replay = c.replay;
        const stars = '⭐'.repeat(c.lesson?.stars || 0);
        showModal('🎉', replay ? 'Ôn luyện xong!' : 'Giỏi lắm!', replay
          ? 'Bé ôn lại bài rồi — điểm lần đầu vẫn giữ nguyên!'
          : `Bé đã hoàn thành bài học! ${stars}`, () => {
          if (deps.navigateAfterLesson) deps.navigateAfterLesson(true);
          else if (state.subjectId && state.subject) deps.goChapters(state.subject);
          else deps.goScreen('s4');
        });
        if (deps.loadToday) deps.loadToday();
        return;
      }
      playerState.index = res.next_step_index;
      const prog = document.getElementById('guided-progress');
      if (prog) prog.innerHTML = progressHtml();
      renderCurrentStep();
    }

    function renderObserve(step, cfg) {
      const el = document.getElementById('guided-step');
      const blocks = (cfg.display_blocks || []).map(b =>
        `<div class="read-block">${b.emoji || ''} ${b.text || ''}</div>`
      ).join('');
      el.innerHTML = `
        <div class="guided-step-title">${step.emoji_icon} Nhận biết</div>
        ${blocks}
        <button type="button" class="modal-btn guided-btn" id="guided-continue">Tiếp tục →</button>
      `;
      if (cfg.tts_text) speakText(cfg.tts_text);
      document.getElementById('guided-continue').onclick = async () => {
        if (playerState.busy) return;
        playerState.busy = true;
        const res = await submit('observe', {});
        playerState.busy = false;
        if (res) advanceOrComplete(res);
      };
      const sec = cfg.auto_advance_sec;
      if (sec) {
        setTimeout(async () => {
          if (playerState.busy) return;
          const btn = document.getElementById('guided-continue');
          if (btn) btn.click();
        }, sec * 1000);
      }
    }

    function renderChoice(step, cfg) {
      const el = document.getElementById('guided-step');
      el.innerHTML = `
        <div class="guided-step-title">${step.emoji_icon} Chọn đáp án</div>
        <div class="player-q">${cfg.prompt || ''}</div>
        <div class="player-choices" id="guided-choices"></div>
      `;
      if (cfg.tts_text) speakText(cfg.tts_text);
      const choices = document.getElementById('guided-choices');
      (cfg.choices || []).forEach((c, idx) => {
        const btn = document.createElement('button');
        btn.className = 'player-choice';
        btn.textContent = c;
        btn.onclick = async () => {
          if (playerState.busy) return;
          playerState.busy = true;
          const res = await submit('choice', { selected_index: idx });
          playerState.busy = false;
          if (!res) return;
          if (res.feedback.type === 'wrong') {
            showFeedback(res.feedback.tts_text || 'Thử lại nhé', 'wrong');
            speakText(res.feedback.tts_text || '');
            return;
          }
          advanceOrComplete(res);
        };
        choices.appendChild(btn);
      });
    }

    function renderQuiz(step, cfg) {
      const questions = cfg.questions || [];
      playerState.quizAnswers = [];
      playerState.quizIndex = 0;
      playerState.quizQuestions = questions;

      function renderOne() {
        const q = playerState.quizQuestions[playerState.quizIndex];
        const el = document.getElementById('guided-step');
        if (!q) return;
        el.innerHTML = `
          <div class="guided-step-title">${step.emoji_icon} Câu hỏi</div>
          <div class="player-q">${playerState.quizIndex + 1}/${playerState.quizQuestions.length}. ${q.prompt}</div>
          <div class="player-choices" id="guided-quiz-choices"></div>
        `;
        const box = document.getElementById('guided-quiz-choices');
        (q.choices || []).forEach((c, idx) => {
          const btn = document.createElement('button');
          btn.className = 'player-choice';
          btn.textContent = c;
          btn.onclick = async () => {
            if (playerState.busy) return;
            if (idx !== q.answer_index) {
              showFeedback('Gần đúng rồi, cố lên nhé', 'wrong');
              speakText('Gần đúng rồi, cố lên nhé');
              return;
            }
            playerState.quizAnswers[playerState.quizIndex] = { question_index: playerState.quizIndex, selected: idx };
            playerState.quizIndex++;
            if (playerState.quizIndex < playerState.quizQuestions.length) {
              renderOne();
            } else {
              playerState.busy = true;
              const res = await submit('quiz', { answers: playerState.quizAnswers });
              playerState.busy = false;
              if (res) advanceOrComplete(res);
            }
          };
          box.appendChild(btn);
        });
      }
      renderOne();
    }

    function renderCheckpoint(step, cfg) {
      const el = document.getElementById('guided-step');
      el.innerHTML = `
        <div class="guided-step-title">${step.emoji_icon} Cùng bố mẹ</div>
        <p class="checkpoint-msg">${cfg.tts_text || 'Hãy làm theo hướng dẫn cùng bố mẹ nhé!'}</p>
        <p class="checkpoint-hint">Bố/mẹ mở tab Học tập để xác nhận 👍</p>
        <button type="button" class="modal-btn guided-btn" id="checkpoint-request">Đã làm xong — nhờ bố mẹ xác nhận</button>
        <button type="button" class="guided-skip" id="checkpoint-skip">Bỏ qua (cần bố mẹ đồng ý)</button>
      `;
      if (cfg.tts_text) speakText(cfg.tts_text);
      document.getElementById('checkpoint-request').onclick = async () => {
        if (playerState.busy) return;
        playerState.busy = true;
        const res = await submit('checkpoint_request', {});
        playerState.busy = false;
        if (res && res.feedback.checkpoint_id) {
          playerState.checkpointId = res.feedback.checkpoint_id;
          showMascotSpeech('Đã gửi cho bố mẹ! Chờ xác nhận nhé 👨‍👩‍👦');
        }
      };
      document.getElementById('checkpoint-skip').onclick = async () => {
        if (playerState.busy) return;
        playerState.busy = true;
        const res = await submit('skip', {});
        playerState.busy = false;
        if (res) advanceOrComplete(res);
      };
    }

    const { api, speakText, speakKaraoke, showMascotSpeech, showModal, state } = deps;
    let listenCleanup = null;

    function cleanupListenRead() {
      if (listenCleanup) {
        listenCleanup();
        listenCleanup = null;
      }
    }

    function normVi(s) {
      return (s || '').toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').replace(/đ/g, 'd').trim();
    }

    function readingSegments(cfg) {
      const segs = cfg.display_segments || [];
      if (segs.length) return segs;
      const raw = cfg.display_text || cfg.tts_text || '';
      return [{ text: raw, emoji: '📖' }];
    }

    function readingWords(cfg) {
      return readingSegments(cfg).flatMap(s => (s.text || '').split(/\s+/).filter(Boolean));
    }

    function karaokeHtml(words, activeIdx, doneThrough, segments) {
      if (segments && segments.length > 1) {
        let gi = 0;
        return segments.map(seg => {
          const wlist = (seg.text || '').split(/\s+/).filter(Boolean);
          const inner = wlist.map(w => {
            let cls = 'karaoke-word';
            if (gi < doneThrough) cls += ' karaoke-done';
            else if (gi === activeIdx) cls += ' karaoke-active';
            gi++;
            return `<span class="${cls}">${w}</span>`;
          }).join(' ');
          return `<div class="listen-read-para"><span class="listen-read-para-emoji">${seg.emoji || ''}</span><div class="listen-read-para-text">${inner}</div></div>`;
        }).join('');
      }
      return words.map((w, i) => {
        let cls = 'karaoke-word';
        if (i < doneThrough) cls += ' karaoke-done';
        else if (i === activeIdx) cls += ' karaoke-active';
        return `<span class="${cls}">${w}</span>`;
      }).join(' ');
    }

    function wordMatchHtml(expected, spoken) {
      const exp = expected.map(normVi);
      const got = spoken.split(/\s+/).filter(Boolean).map(normVi);
      return expected.map((w, i) => {
        const ew = exp[i];
        const hit = got.some(g => g === ew || g.includes(ew) || ew.includes(g));
        return `<span class="word-match ${hit ? 'word-match--ok' : 'word-match--pending'}">${w}</span>`;
      }).join('');
    }

    function renderListenRead(step, cfg) {
      cleanupListenRead();
      const el = document.getElementById('guided-step');
      const segments = readingSegments(cfg);
      const words = readingWords(cfg);
      const displayText = words.join(' ');
      const sampleTts = cfg.tts_text || displayText;
      const multiSeg = segments.length > 1;
      const maxAttempts = cfg.max_attempts || 5;
      let attempts = 0;
      let phase = 'instruct';
      let activeWord = -1;
      let doneThrough = -1;
      let interim = '';
      let recognition = null;
      let listening = false;

      function paint() {
        const phaseLabel = phase === 'model' ? '🔊 Thầy đọc mẫu'
          : phase === 'child' ? '🎙️ Đến lượt con!'
          : phase === 'result' ? '✨ Kết quả'
          : '👂 Nghe & đọc theo thầy';
        el.innerHTML = `
          <div class="guided-step-title">${step.emoji_icon} ${phaseLabel}</div>
          <div class="listen-read-panel">
            <div class="listen-read-emoji">${(cfg.display_segments && cfg.display_segments[0] && cfg.display_segments[0].emoji) || '📖'}</div>
            <div class="listen-read-text ${multiSeg ? 'listen-read-text--multi' : ''}" id="listen-karaoke">${karaokeHtml(words, activeWord, doneThrough, segments)}</div>
            <div class="listen-read-phase" id="listen-phase-hint"></div>
            <div class="listen-stt-box ${phase === 'child' || phase === 'result' ? '' : 'hide'}" id="listen-stt-box">
              <div class="listen-stt-label">Bé vừa đọc:</div>
              <div class="listen-stt-interim" id="listen-interim">${interim || '…'}</div>
              <div class="listen-word-match" id="listen-word-match">${wordMatchHtml(words, interim)}</div>
            </div>
            <div class="listen-read-actions">
              <button type="button" class="guided-skip-btn" id="listen-replay-model">🔁 Nghe lại mẫu</button>
              <button type="button" class="modal-btn guided-btn" id="listen-primary">${phase === 'child' ? '🎙️ Xong — chấm bài' : phase === 'result' ? 'Tiếp tục →' : '▶ Bắt đầu'}</button>
            </div>
          </div>`;
        const hint = document.getElementById('listen-phase-hint');
        if (hint) {
          if (phase === 'instruct') hint.textContent = 'Bấm Bắt đầu để nghe thầy đọc mẫu nhé!';
          else if (phase === 'model') hint.textContent = 'Chú ý từ được tô sáng vàng theo giọng đọc';
          else if (phase === 'child') hint.textContent = 'Đọc to rõ ràng — thầy đang nghe con';
          else hint.textContent = '';
        }
        document.getElementById('listen-replay-model').onclick = () => runModelRead();
        document.getElementById('listen-primary').onclick = () => onPrimary();
      }

      function updateKaraoke() {
        const box = document.getElementById('listen-karaoke');
        if (box) box.innerHTML = karaokeHtml(words, activeWord, doneThrough, segments);
        const interimEl = document.getElementById('listen-interim');
        const matchEl = document.getElementById('listen-word-match');
        if (interimEl) interimEl.textContent = interim || '…';
        if (matchEl) matchEl.innerHTML = wordMatchHtml(words, interim);
      }

      function runModelRead() {
        phase = 'model';
        activeWord = -1;
        doneThrough = -1;
        paint();
        stopListening();
        const karaokeFn = deps.speakKaraoke || speakText;
        if (typeof karaokeFn === 'function' && karaokeFn.length >= 2) {
          deps.speakKaraoke(sampleTts, (idx) => {
            activeWord = idx;
            if (idx > 0) doneThrough = idx - 1;
            updateKaraoke();
          }, () => {
            doneThrough = words.length - 1;
            activeWord = -1;
            updateKaraoke();
            startChildPhase();
          });
        } else {
          speakText(sampleTts);
          let i = 0;
          const t = setInterval(() => {
            activeWord = i;
            if (i > 0) doneThrough = i - 1;
            updateKaraoke();
            i++;
            if (i >= words.length) {
              clearInterval(t);
              doneThrough = words.length - 1;
              activeWord = -1;
              updateKaraoke();
              startChildPhase();
            }
          }, 450);
          listenCleanup = () => clearInterval(t);
        }
      }

      function stopListening() {
        listening = false;
        if (recognition) {
          try { recognition.stop(); } catch (_) { /* noop */ }
          recognition = null;
        }
      }

      function startChildPhase() {
        phase = 'child';
        interim = '';
        paint();
        speakText(cfg.instruction_tts || 'Đến lượt con đọc to nhé!');
        startListening();
      }

      function startListening() {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
          showMascotSpeech('Trình duyệt chưa hỗ trợ mic — bé đọc xong bấm Xong nhé!');
          return;
        }
        stopListening();
        recognition = new SR();
        recognition.lang = 'vi-VN';
        recognition.interimResults = true;
        recognition.continuous = true;
        listening = true;
        recognition.onresult = (ev) => {
          let text = '';
          for (let i = ev.resultIndex; i < ev.results.length; i++) {
            text += ev.results[i][0].transcript;
          }
          interim = text.trim();
          updateKaraoke();
        };
        recognition.onerror = () => { listening = false; };
        recognition.onend = () => {
          if (listening) {
            try { recognition.start(); } catch (_) { listening = false; }
          }
        };
        try { recognition.start(); } catch (_) { /* noop */ }
      }

      async function submitReading() {
        if (playerState.busy) return;
        stopListening();
        playerState.busy = true;
        phase = 'result';
        paint();
        const transcript = interim || displayText;
        const res = await submit('stt', { transcript });
        playerState.busy = false;
        if (!res) return;
        if (res.feedback && res.feedback.type === 'wrong') {
          attempts++;
          showFeedback(res.feedback.tts_text || 'Nghe mẫu và thử lại nhé', 'wrong');
          speakText(res.feedback.tts_text || 'Nghe mẫu và thử lại nhé');
          if (attempts >= maxAttempts) {
            showMascotSpeech('Thử nhiều lần rồi — bố mẹ giúp con nhé!');
            const skipBtn = document.getElementById('listen-primary');
            if (skipBtn) skipBtn.textContent = 'Bỏ qua →';
          } else {
            phase = 'child';
            paint();
            runModelRead();
          }
          return;
        }
        doneThrough = words.length - 1;
        interim = transcript;
        updateKaraoke();
        showFeedback('Đọc hay quá!', 'success');
        setTimeout(() => advanceOrComplete(res), 800);
      }

      function onPrimary() {
        if (phase === 'instruct') {
          const intro = cfg.instruction_tts || 'Con nghe thầy đọc mẫu nhé!';
          speakText(intro);
          setTimeout(runModelRead, intro.length > 20 ? 2200 : 1400);
          return;
        }
        if (phase === 'child' || phase === 'result') {
          submitReading();
        }
      }

      paint();
      if (cfg.instruction_tts) speakText(cfg.instruction_tts);
      listenCleanup = () => stopListening();
    }

    function renderReward(step, cfg) {
      const el = document.getElementById('guided-step');
      const burst = (cfg.emoji_burst || ['🎉', '⭐']).join(' ');
      el.innerHTML = `
        <div class="guided-reward">${burst}</div>
        <div class="guided-step-title">${step.emoji_icon} Hoàn thành!</div>
      `;
      if (cfg.tts_text) speakText(cfg.tts_text);
      setTimeout(async () => {
        const res = await submit('observe', {});
        if (res) advanceOrComplete(res);
      }, 1500);
    }

    function renderCurrentStep() {
      const step = playerState.steps[playerState.index];
      if (!step) {
        playerState.index = 0;
        if (!playerState.steps.length) return;
        return renderCurrentStep();
      }
      const cfg = step.config || {};
      if (step.step_type === 'observe') renderObserve(step, cfg);
      else if (step.step_type === 'listen_read') renderListenRead(step, cfg);
      else if (step.step_type === 'choice') renderChoice(step, cfg);
      else if (step.step_type === 'quiz') renderQuiz(step, cfg);
      else if (step.step_type === 'family_checkpoint') renderCheckpoint(step, cfg);
      else if (step.step_type === 'reward') renderReward(step, cfg);
      else {
        const el = document.getElementById('guided-step');
        el.innerHTML = `<p>Loại bước: ${step.step_type}</p><button class="modal-btn" id="guided-fallback">Tiếp</button>`;
        document.getElementById('guided-fallback').onclick = async () => {
          const res = await submit('observe', {});
          if (res) advanceOrComplete(res);
        };
      }
    }

    return {
      async start(lessonId, body, titleEl) {
        playerState.lessonId = lessonId;
        playerState.lessonStart = Date.now();
        const data = await api(`/lessons/${lessonId}/player`);
        playerState.steps = data.steps || [];
        const resume = data.is_replay ? 0 : (data.resume_at_step_index ?? 0);
        playerState.index = resume >= playerState.steps.length ? 0 : resume;
        playerState.progressEmojis = data.lesson.progress_emojis || [];
        if (titleEl) titleEl.textContent = data.lesson.title;
        renderShell(body);
        renderCurrentStep();
      },
    };
  }

  global.LearningGuidedPlayer = { create: createGuidedPlayer };
})(window);
