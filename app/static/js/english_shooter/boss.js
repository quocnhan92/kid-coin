(function () {
  const { MODES, uuid, getBootstrap, getStage, sessionsBatch, eventsBatch, updateProfileBar, toast, clearBootstrapCache } =
    window.EnglishShooter;
  const SpeechApi = window.SpeechRecognition || window.webkitSpeechRecognition;

  let bootstrap = null;
  let sessionId = null;
  let startedAt = null;
  let items = [];
  let idx = 0;
  let bossHp = 100;
  let correctCount = 0;
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
      const el = document.getElementById("es-boss-transcript");
      if (el && transcriptText) el.value = transcriptText;
      setResult(`Đã nghe: "${transcriptText}"`, true);
    };
    recognition.onerror = () => setResult("Không nhận diện được, nhập tay để tiếp tục.", false);
  }

  function norm(text) {
    return (text || "").toLowerCase().replace(/[^a-z0-9\s]/g, "").replace(/\s+/g, " ").trim();
  }

  function similarity(a, b) {
    if (!a || !b) return 0;
    const aa = norm(a).split(" ");
    const bb = norm(b).split(" ");
    const set = new Set(bb);
    const hit = aa.filter((w) => set.has(w)).length;
    return hit / Math.max(bb.length, 1);
  }

  function setResult(text, ok) {
    const el = document.getElementById("es-boss-voice-result");
    if (!el) return;
    el.textContent = text;
    el.className = ok ? "es-result-ok" : "es-result-bad";
  }

  function hud() {
    document.getElementById("es-boss-gold").textContent = `🪙 ${bootstrap?.english?.gold || 0}`;
    document.getElementById("es-boss-hp").textContent = `Boss HP ${Math.max(0, bossHp)}`;
    document.getElementById("es-boss-progress").textContent = `${idx}/${items.length}`;
  }

  function renderParagraph() {
    if (!sessionId) return;
    if (bossHp <= 0 || idx >= items.length) {
      endRun(bossHp <= 0);
      return;
    }
    const item = items[idx];
    document.getElementById("es-boss-paragraph").textContent = item.target_text || "...";
    document.getElementById("es-boss-transcript").value = "";
    transcriptText = "";
    setResult("Đọc đoạn văn rồi bấm Tấn công", false);
    hud();
  }

  async function attackBoss() {
    if (!sessionId) return;
    const item = items[idx];
    const expected = item?.target_text || "";
    const spoken = document.getElementById("es-boss-transcript").value.trim() || transcriptText;
    const ratio = similarity(spoken, expected);
    const damage = Math.round(Math.max(5, ratio * 35));
    bossHp -= damage;
    if (ratio >= 0.5) {
      correctCount += 1;
      clientSeq += 1;
      await eventsBatch(sessionId, [
        {
          client_seq: clientSeq,
          occurred_at: new Date().toISOString(),
          event_type: "speaking",
          skill_unit_id: item.id,
          correct: true,
          score_delta: damage,
        },
      ]);
      setResult(`Trúng đòn ${damage} HP (độ khớp ${(ratio * 100).toFixed(0)}%)`, true);
    } else {
      setResult(`Độ khớp thấp ${(ratio * 100).toFixed(0)}%, sát thương yếu ${damage}`, false);
    }
    idx += 1;
    clearBootstrapCache();
    bootstrap = await getBootstrap(MODES.boss);
    setTimeout(renderParagraph, 450);
  }

  async function startRun() {
    const stage = await getStage(themeId, "paragraph");
    items = stage.stage?.items || [];
    if (!items.length) {
      toast("Chưa có dữ liệu paragraph cho chủ đề này");
      return;
    }
    idx = 0;
    bossHp = 100;
    correctCount = 0;
    clientSeq = 0;
    sessionId = uuid();
    startedAt = new Date().toISOString();
    await sessionsBatch([
      {
        op: "start",
        session_id: sessionId,
        game_id: "english_shooter",
        game_mode_id: MODES.boss,
        started_at: startedAt,
        content_pack_id: "vn_english_shooter_v1",
      },
    ]);
    renderParagraph();
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
          score: Math.max(0, 100 - bossHp) * 2,
          stars: completed ? 3 : 1,
          summary_json: {
            play_mode: "boss",
            theme_id: themeId,
            grade: bootstrap?.english?.last_grade || 1,
            theme_completed: completed,
          },
        },
      },
    ]);
    sessionId = null;
    toast(completed ? "Boss bị hạ gục!" : "Boss còn sống, luyện thêm nhé");
  }

  async function init() {
    bootstrap = await getBootstrap(MODES.boss);
    const themes = bootstrap?.english?.themes || [];
    themeId = themes[0]?.id || "en_g1_family";
    hud();
    await updateProfileBar("Boss mode");
    document.getElementById("es-boss-start-btn").addEventListener("click", startRun);
    document.getElementById("es-boss-attack-btn").addEventListener("click", attackBoss);
    document.getElementById("es-boss-speak-btn").addEventListener("click", () => {
      if (!recognition) {
        setResult("Trình duyệt chưa hỗ trợ Speech API, nhập tay để chơi.", false);
        return;
      }
      recognition.start();
      setResult("Đang nghe...", true);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
