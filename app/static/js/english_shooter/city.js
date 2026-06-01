(function () {
  const { MODES, uuid, getBootstrap, getStage, sessionsBatch, eventsBatch, updateProfileBar, toast, clearBootstrapCache } =
    window.EnglishShooter;
  const SpeechApi = window.SpeechRecognition || window.webkitSpeechRecognition;

  let bootstrap = null;
  let sessionId = null;
  let startedAt = null;
  let items = [];
  let idx = 0;
  let score = 0;
  let hp = 3;
  let correctCount = 0;
  let selectedCorrectSentence = "";
  let transcriptText = "";
  let clientSeq = 0;
  let themeId = "en_g1_family";

  const recognition = SpeechApi ? new SpeechApi() : null;
  if (recognition) {
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      transcriptText = (event.results?.[0]?.[0]?.transcript || "").trim();
      const el = document.getElementById("es-city-transcript");
      if (el && transcriptText) el.value = transcriptText;
      setVoiceResult(`Đã nghe: "${transcriptText}"`, true);
    };
    recognition.onerror = () => setVoiceResult("Không nhận diện được, nhập tay để tiếp tục.", false);
  }

  function norm(text) {
    return (text || "").toLowerCase().replace(/[^a-z0-9\s]/g, "").replace(/\s+/g, " ").trim();
  }

  function setVoiceResult(text, ok) {
    const el = document.getElementById("es-city-voice-result");
    if (!el) return;
    el.textContent = text;
    el.className = ok ? "es-result-ok" : "es-result-bad";
  }

  function hud() {
    const g = bootstrap?.english?.gold || 0;
    document.getElementById("es-city-gold").textContent = `🪙 ${g}`;
    document.getElementById("es-city-score").textContent = `Điểm ${score}`;
    document.getElementById("es-city-hp").textContent = `HP ${hp}`;
    document.getElementById("es-city-progress").textContent = `${idx}/${items.length}`;
  }

  function renderQuestion() {
    if (!sessionId) return;
    if (hp <= 0 || idx >= items.length) {
      endRun(hp > 0 && idx >= items.length);
      return;
    }
    const item = items[idx];
    const opts = item.options || {};
    selectedCorrectSentence = item.target_text || "";
    document.getElementById("es-city-prompt").textContent = opts.prompt || selectedCorrectSentence;
    const wrap = document.getElementById("es-city-choices");
    wrap.innerHTML = "";
    (opts.choices || []).forEach((choice) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "es-choice-btn";
      btn.textContent = choice;
      btn.addEventListener("click", () => selectChoice(btn, choice, opts.answer));
      wrap.appendChild(btn);
    });
    setVoiceResult("Chưa ghi âm", false);
    transcriptText = "";
    document.getElementById("es-city-transcript").value = "";
    hud();
  }

  function selectChoice(btn, choice, answer) {
    if (choice === answer) {
      btn.classList.add("correct");
      score += 10;
      selectedCorrectSentence = (document.getElementById("es-city-prompt").textContent || "").replace("[____]", answer);
      setVoiceResult("Đáp án đúng. Hãy đọc lại câu để nhận bonus.", true);
      return;
    }
    btn.classList.add("wrong");
    hp -= 1;
    toast("Sai đáp án, -1 HP");
    hud();
    if (hp <= 0) endRun(false);
  }

  async function checkSpeaking() {
    if (!sessionId) return;
    const input = document.getElementById("es-city-transcript").value.trim();
    const spoken = norm(input || transcriptText);
    const expected = norm(selectedCorrectSentence);
    if (!expected) {
      setVoiceResult("Hãy chọn đáp án đúng trước.", false);
      return;
    }
    if (spoken && expected && spoken.includes(expected.slice(0, Math.max(3, expected.length - 3)))) {
      score += 20;
      correctCount += 1;
      clientSeq += 1;
      await eventsBatch(sessionId, [
        {
          client_seq: clientSeq,
          occurred_at: new Date().toISOString(),
          event_type: "answer",
          skill_unit_id: items[idx]?.id,
          correct: true,
          score_delta: 1,
        },
      ]);
      idx += 1;
      clearBootstrapCache();
      bootstrap = await getBootstrap(MODES.city);
      setVoiceResult("Speaking đạt — +20 điểm", true);
      renderQuestion();
      return;
    }
    hp -= 1;
    setVoiceResult("Speaking chưa khớp, thử lại.", false);
    hud();
    if (hp <= 0) endRun(false);
  }

  async function startRun() {
    const stage = await getStage(themeId, "sentence");
    items = stage.stage?.items || [];
    if (!items.length) {
      toast("Chưa có dữ liệu sentence cho chủ đề này");
      return;
    }
    idx = 0;
    hp = 3;
    score = 0;
    correctCount = 0;
    clientSeq = 0;
    sessionId = uuid();
    startedAt = new Date().toISOString();
    await sessionsBatch([
      {
        op: "start",
        session_id: sessionId,
        game_id: "english_shooter",
        game_mode_id: MODES.city,
        started_at: startedAt,
        content_pack_id: "vn_english_shooter_v1",
      },
    ]);
    renderQuestion();
  }

  async function endRun(completed) {
    if (!sessionId) return;
    const duration = Math.max(1, Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000));
    await sessionsBatch([
      {
        op: "end",
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
            play_mode: "city",
            theme_id: themeId,
            grade: bootstrap?.english?.last_grade || 1,
            theme_completed: completed,
          },
        },
      },
    ]);
    sessionId = null;
    toast(completed ? "Thành phố được bảo vệ!" : "Thất bại, thử lại nhé");
  }

  async function init() {
    bootstrap = await getBootstrap(MODES.city);
    const themes = bootstrap?.english?.themes || [];
    themeId = themes[0]?.id || "en_g1_family";
    hud();
    await updateProfileBar("City mode");
    document.getElementById("es-city-start-btn").addEventListener("click", startRun);
    document.getElementById("es-city-check-btn").addEventListener("click", checkSpeaking);
    document.getElementById("es-city-speak-btn").addEventListener("click", () => {
      if (!recognition) {
        setVoiceResult("Trình duyệt chưa hỗ trợ Speech API, nhập tay để chơi.", false);
        return;
      }
      recognition.start();
      setVoiceResult("Đang nghe...", true);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
