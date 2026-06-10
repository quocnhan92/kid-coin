/* English Shooter — Lily drag vocabulary (fun + G1/G2) */
(function () {
  const vocab = window.LilyVocab;
  if (!vocab?.MODES) {
    console.error("LilyVocab failed to load — check lily_vocab.js");
    return;
  }
  const { MODES, SECTIONS, MODE_ORDER, pickCelebrate } = vocab;
  const KE = window.KidEngagement;
  const lilyTips = {
    correct: ["Giỏi lắm bạn ơi! 🌸", "Bạn thông minh quá! ⭐", "Đúng rồi! Lily rất vui! 💕", "Hoàn hảo luôn! 🎉"],
    wrong: ["Chưa đúng rồi, thử lại nha! 🌼", "Bạn thử lại nhé, gần đúng rồi! 💪", "Không sao, thử thêm lần nữa! 🌸"],
  };
  const ROUNDS_PER_GAME = 5;
  const ITEM_SEL = ".ingredient-item,.clothing-item,.drag-item";
  let audioCtx = null;

  let mode = "bakery";
  let score = 0;
  let level = 1;
  let roundCount = 0;
  let combo = 0;
  let correctInSession = 0;
  let outfitLevel = 0;
  let currentWord = null;
  let currentOptions = [];
  let learnedWords = {};
  let dollOutfit = [];
  let dragEl = null;
  let dragSource = null;

  const $ = (id) => document.getElementById(id);
  const cfg = () => MODES[mode];

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  const isOnboard = () => new URLSearchParams(location.search).get("onboard") === "1";

  const ensureAudio = () => {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
  };

  const playDing = (high) => {
    try {
      ensureAudio();
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.type = "sine";
      o.frequency.value = high ? 880 : 660;
      g.gain.value = 0.08;
      o.connect(g);
      g.connect(audioCtx.destination);
      o.start();
      o.stop(audioCtx.currentTime + 0.12);
    } catch (_) { /* ignore */ }
  };

  const bumpCombo = () => {
    combo += 1;
    correctInSession += 1;
    const banner = $("combo-banner");
    if (!banner) return;
    if (combo >= 5) banner.textContent = `${combo} liên tiếp — Siêu sao! ⭐`;
    else if (combo >= 3) banner.textContent = `${combo} liên tiếp! 🔥`;
    else banner.textContent = "";
    banner.classList.toggle("hide", combo < 3);
    if (combo >= 5) playDing(true);
    else playDing(false);
    if (navigator.vibrate) navigator.vibrate(50);
    const pop = $("hit-pop");
    if (pop) {
      pop.classList.remove("hide");
      pop.classList.add("hit-pop-show");
      setTimeout(() => pop.classList.remove("hit-pop-show"), 320);
    }
    if (combo >= 5 && outfitLevel < 2) {
      outfitLevel = 2;
      setOutfitBadge("👩‍🍳");
    } else if (combo >= 3 && outfitLevel < 1) {
      outfitLevel = 1;
      setOutfitBadge("👒");
    }
    lilyDance();
  };

  const resetCombo = () => {
    combo = 0;
    $("combo-banner")?.classList.add("hide");
  };

  const setOutfitBadge = (emoji) => {
    const el = $("lily-outfit-badge");
    if (!el) return;
    el.textContent = emoji;
    el.hidden = false;
  };

  const lilyDance = () => {
    const wrap = $("lily-svg-wrap");
    wrap?.classList.remove("lily-dance-anim");
    void wrap?.offsetWidth;
    wrap?.classList.add("lily-dance-anim");
  };

  const runCoinBurst = (amount) => {
    const host = $("coin-burst");
    if (!host) return;
    host.innerHTML = "";
    for (let i = 0; i < 10; i += 1) {
      const c = document.createElement("span");
      c.className = "coin-particle";
      c.textContent = "🪙";
      const tx = (Math.random() - 0.5) * 120;
      const ty = -40 - Math.random() * 80;
      c.style.setProperty("--tx", `${tx}px`);
      c.style.setProperty("--ty", `${ty}px`);
      c.style.animationDelay = `${Math.random() * 0.25}s`;
      host.appendChild(c);
    }
    $("coin-reward").textContent = `+${amount} xu`;
  };

  const calcStars = () => {
    if (correctInSession >= 4) return 3;
    if (correctInSession >= 3) return 2;
    if (correctInSession >= 1) return 1;
    return 0;
  };

  const showScreen = (id) => {
    document.querySelectorAll(".screen").forEach((s) => s.classList.add("hide"));
    $(id).classList.remove("hide");
  };

  const goHome = () => showScreen("start-screen");

  const updateHUD = () => {
    $("hud-score").textContent = String(score);
    $("hud-level").textContent = `Level ${level}`;
    $("hud-stars").textContent = score >= 800 ? "⭐⭐⭐" : score >= 400 ? "⭐⭐" : "⭐";
  };

  const showToast = (emoji, msg, en, vi) => {
    $("t-emoji").textContent = emoji;
    $("t-msg").textContent = msg;
    $("t-en").textContent = en;
    $("t-vi").textContent = vi;
    $("toast").classList.add("show");
    if (emoji === "✨") setTimeout(() => $("toast").classList.remove("show"), 1800);
  };

  const speakQuestion = (word) => {
    if (!word?.vi || !window.GameUtils) return;
    GameUtils.warmupSpeech();
    GameUtils.speak(`Hãy tìm ${word.vi} cho Lily nhé!`);
  };

  const speakAnswer = (en) => {
    if (!en || !window.GameUtils) return;
    GameUtils.warmupSpeech();
    GameUtils.speakEn(en.toLowerCase());
  };

  const drawMindMap = () => {
    const c = cfg();
    const canvas = $("mm-canvas");
    const W = canvas.offsetWidth || 186;
    canvas.width = W;
    canvas.height = 180;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, W, 180);
    const cx = W / 2;
    const cy = 52;
    const rootColor = c.rootColor;
    ctx.beginPath();
    ctx.ellipse(cx, cy, 48, 20, 0, 0, Math.PI * 2);
    ctx.fillStyle = `${rootColor}55`;
    ctx.fill();
    ctx.strokeStyle = rootColor;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "#9D174D";
    ctx.font = "bold 11px Nunito,sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(c.mindRoot, cx, cy);
    const words = Object.values(learnedWords).slice(0, 10);
    if (!words.length) {
      ctx.fillStyle = "#C4A0B4";
      ctx.font = "10px Nunito,sans-serif";
      ctx.fillText("Học đúng để mở nhánh!", cx, 115);
      return;
    }
    words.forEach((w, i) => {
      const angle = (i / words.length) * Math.PI * 1.8 + Math.PI * 0.1;
      const bx = cx + Math.cos(angle) * 60;
      const by = cy + Math.sin(angle) * 60 + 22;
      ctx.strokeStyle = `${rootColor}99`;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(cx, cy + 20);
      ctx.lineTo(bx, by);
      ctx.stroke();
      ctx.beginPath();
      ctx.ellipse(bx, by, 26, 13, 0, 0, Math.PI * 2);
      ctx.fillStyle = `${rootColor}33`;
      ctx.fill();
      ctx.strokeStyle = rootColor;
      ctx.stroke();
      ctx.fillStyle = "#7C3AED";
      ctx.font = "bold 9px Nunito,sans-serif";
      ctx.fillText(`${w.emoji} ${w.en}`, bx, by);
    });
  };

  const updateChips = () => {
    const chipCls = cfg().chipClass;
    $("word-chips").innerHTML = Object.values(learnedWords).map((w) =>
      `<span class="chip${chipCls ? ` ${chipCls}` : ""}" title="${w.vi}">${w.emoji} ${w.en}</span>`
    ).join("");
  };

  const bindDragItem = (div, item, onTouchEnd) => {
    div.addEventListener("dragstart", () => {
      dragEl = div;
      dragSource = item;
      div.classList.add("dragging");
    });
    div.addEventListener("dragend", () => div.classList.remove("dragging"));
    div.addEventListener("touchstart", (e) => {
      dragEl = div;
      dragSource = item;
      e.preventDefault();
    }, { passive: false });
    div.addEventListener("touchmove", onTouchMove, { passive: false });
    div.addEventListener("touchend", onTouchEnd, { passive: false });
  };

  const makeDragItem = (item, cls, labelCls) => {
    const div = document.createElement("div");
    div.className = cls;
    div.draggable = true;
    div.dataset.en = item.en;
    div.innerHTML = `<span class="${labelCls}-emoji">${item.emoji}</span><span class="${labelCls}-label">${item.en}</span>`;
    return div;
  };

  const bindDropZone = (el, handler) => {
    el.ondragover = (e) => { e.preventDefault(); el.classList.add("over"); };
    el.ondragleave = () => el.classList.remove("over");
    el.ondrop = (e) => {
      e.preventDefault();
      el.classList.remove("over");
      handler(dragSource);
    };
  };

  const renderDrag = () => {
    const c = cfg();
    const shelf = $("ingredient-shelf");
    const dz = $("drop-zone");
    shelf.innerHTML = "";
    dz.textContent = c.dropEmoji;
    dz.classList.remove("over");
    currentOptions.forEach((item) => {
      const div = makeDragItem(item, "ingredient-item drag-item", "ii");
      bindDragItem(div, item, onTouchEndDrag);
      shelf.appendChild(div);
    });
    bindDropZone(dz, handleDragDrop);
  };

  const renderFashion = () => {
    const shelf = $("clothing-shelf");
    shelf.innerHTML = "";
    const doll = $("doll-drop");
    doll.classList.remove("over");
    currentOptions.forEach((item) => {
      const div = makeDragItem(item, "clothing-item drag-item", "ci");
      bindDragItem(div, item, onTouchEndFashion);
      shelf.appendChild(div);
    });
    bindDropZone(doll, handleFashionDrop);
  };

  const renderScene = () => {
    if (cfg().scene === "fashion") renderFashion();
    else renderDrag();
  };

  const lockItems = () => {
    document.querySelectorAll(ITEM_SEL).forEach((el) => {
      el.draggable = false;
      el.style.opacity = "0.5";
      el.style.cursor = "default";
      if (el.dataset.en === currentWord.en) {
        el.style.opacity = "1";
        el.style.border = "3px solid #22C55E";
      }
    });
  };

  const correctDrop = () => {
    score += 100 * level;
    bumpCombo();
    learnedWords[currentWord.en] = currentWord;
    speakAnswer(currentWord.en);
    showToast("✨", pick(lilyTips.correct), currentWord.en, `= ${currentWord.vi}`);
    $("lily-tip").textContent = `${pick(lilyTips.correct)} 🌸`;
    $("btn-next").style.display = "block";
    lockItems();
    updateHUD();
    drawMindMap();
    updateChips();
  };

  const wrongDrop = (en) => {
    resetCombo();
    $("lily-tip").textContent = pick(lilyTips.wrong);
    document.querySelectorAll(ITEM_SEL).forEach((el) => {
      if (el.dataset.en === en) {
        el.classList.add("wrong-shake");
        setTimeout(() => el.classList.remove("wrong-shake"), 500);
      }
    });
    showToast("💭", "Chưa đúng rồi!", en, `≠ ${currentWord.vi}`);
    setTimeout(() => $("toast").classList.remove("show"), 900);
  };

  const showCelebrate = () => {
    const hit = pickCelebrate(cfg());
    if (!hit) return;
    $("cake-icon").textContent = hit.emoji;
    $("cake-msg").textContent = hit.msg;
    $("result-cake").style.display = "block";
  };

  const handleDragDrop = (item) => {
    if (!item) return;
    if (item.en === currentWord.en) {
      correctDrop();
      $("drop-zone").textContent = currentWord.emoji;
      showCelebrate();
    } else {
      wrongDrop(item.en);
    }
  };

  const handleFashionDrop = (item) => {
    if (!item) return;
    if (item.en === currentWord.en) {
      correctDrop();
      dollOutfit.push(item.emoji);
      $("doll-outfit").innerHTML = dollOutfit.slice(-5).map((e) => `<span>${e}</span>`).join("");
      $("doll-body").setAttribute("fill", item.color || "#F9A8D4");
      $("doll-skirt").setAttribute("fill", item.color || "#F9A8D4");
    } else {
      wrongDrop(item.en);
    }
  };

  const resetTouchEl = () => {
    if (!dragEl) return;
    dragEl.style.position = "";
    dragEl.style.left = "";
    dragEl.style.top = "";
    dragEl.style.zIndex = "";
    dragEl.style.pointerEvents = "";
    dragEl.classList.remove("dragging");
  };

  const onTouchMove = (e) => {
    e.preventDefault();
    if (!dragEl) return;
    const t = e.touches[0];
    dragEl.style.position = "fixed";
    dragEl.style.left = `${t.clientX - 40}px`;
    dragEl.style.top = `${t.clientY - 40}px`;
    dragEl.style.zIndex = "999";
    dragEl.style.pointerEvents = "none";
    [$("drop-zone"), $("doll-drop")].forEach((el) => {
      if (!el) return;
      const r = el.getBoundingClientRect();
      const over = t.clientX > r.left && t.clientX < r.right && t.clientY > r.top && t.clientY < r.bottom;
      el.classList.toggle("over", over);
    });
  };

  const touchHit = (e, el, handler) => {
    const t = e.changedTouches[0];
    resetTouchEl();
    const r = el.getBoundingClientRect();
    if (t.clientX > r.left && t.clientX < r.right && t.clientY > r.top && t.clientY < r.bottom) {
      handler(dragSource);
    }
    dragEl = null;
    dragSource = null;
  };

  const onTouchEndDrag = (e) => touchHit(e, $("drop-zone"), handleDragDrop);
  const onTouchEndFashion = (e) => touchHit(e, $("doll-drop"), handleFashionDrop);

  const showResult = () => {
    const starN = calcStars();
    const stars = "⭐".repeat(starN) + "☆".repeat(3 - starN);
    const coins = Math.max(5, correctInSession * 2 + starN * 3);
    KE?.setModeStars(mode, starN);
    KE?.markFirstSessionDone();
    $("result-stars").textContent = stars;
    $("result-cheer").textContent = starN >= 2 ? "Lily vui lắm! 🌟" : "Cố thêm chút nữa nhé! 🌸";
    runCoinBurst(coins);
    playDing(true);
    lilyDance();
    showScreen("result-screen");
  };

  const nextRound = () => {
    $("btn-next").style.display = "none";
    $("result-cake").style.display = "none";
    $("toast").classList.remove("show");
    if (roundCount >= ROUNDS_PER_GAME) {
      showResult();
      return;
    }
    roundCount++;
    const pool = cfg().data;
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    currentWord = shuffled[0];
    currentOptions = [currentWord, ...shuffled.slice(1, 4)].sort(() => Math.random() - 0.5);
    $("speech-en").textContent = currentWord.en;
    $("speech-vi").innerHTML = `Hãy tìm <b>${currentWord.vi}</b> cho Lily nhé!`;
    speakQuestion(currentWord);
    renderScene();
    level = Math.floor(score / 300) + 1;
    updateHUD();
  };

  const setSceneVisible = () => {
    const c = cfg();
    const isFashion = c.scene === "fashion";
    $("bakery-scene").style.display = isFashion ? "none" : "flex";
    $("fashion-scene").style.display = isFashion ? "flex" : "none";
  };

  const startGame = (m) => {
    mode = m;
    score = 0;
    level = 1;
    roundCount = 0;
    combo = 0;
    correctInSession = 0;
    outfitLevel = 0;
    learnedWords = {};
    dollOutfit = [];
    const ob = $("lily-outfit-badge");
    if (ob) ob.hidden = true;
    $("combo-banner")?.classList.add("hide");
    const c = cfg();
    showScreen("game-screen");
    $("hud-topic").textContent = c.hud;
    $("speech-hint").textContent = c.hint;
    $("lily-tip").textContent = c.tip;
    setSceneVisible();
    updateHUD();
    drawMindMap();
    updateChips();
    nextRound();
  };

  const renderNextWorldPreview = () => {
    const el = $("lily-next-world");
    if (!el || !KE) return;
    const nextId = KE.nextLockedMode();
    if (!nextId || KE.isModeUnlocked(nextId)) {
      el.innerHTML = "";
      return;
    }
    const m = MODES[nextId];
    el.innerHTML = `
      <p class="lily-next-label">Thế giới tiếp theo</p>
      <div class="lily-next-card locked">
        <span>${m?.icon || "🔒"}</span> ${m?.title || nextId}
        <small>Mở sau 3⭐ ở màn trước</small>
      </div>`;
  };

  const buildStartScreen = () => {
    const root = $("mode-sections");
    const extra = $("lily-unlocked-modes");
    if (!root) return;
    const simple = isOnboard() || !KE?.isFirstSessionDone();
    if (simple) {
      root.innerHTML = `
        <div class="lily-feature-card">
          <div class="lily-feature-icon">🍰</div>
          <h2 class="lily-feature-title">Tiệm Bánh Lily</h2>
          <p class="lily-feature-topic">Hôm nay học: nguyên liệu làm bánh</p>
          <button type="button" class="lily-play-hero" id="btn-hero-play">▶ Chơi ngay</button>
          <p class="lily-feature-free">Miễn phí · 5 câu vui thôi!</p>
        </div>
        <div id="lily-next-world" class="lily-next-world"></div>`;
      $("btn-hero-play")?.addEventListener("click", () => startGame("bakery"));
      extra?.classList.add("hide");
      renderNextWorldPreview();
      return;
    }
    root.innerHTML = "";
    extra?.classList.remove("hide");
    const unlocked = (MODE_ORDER || []).filter((id) => KE?.isModeUnlocked(id));
    extra.innerHTML = `
      <p class="grade-label">Chọn thế giới</p>
      <div class="mode-grid">${unlocked.map((id) => {
        const m = MODES[id];
        return `<button type="button" class="mode-btn ${m.btnClass}" data-mode="${id}">
          <span class="mb-icon">${m.icon}</span>
          <div class="mb-title">${m.title}</div>
          <span class="mb-grade">${"⭐".repeat(KE.getModeStars(id))}</span>
        </button>`;
      }).join("")}</div>`;
    extra.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => startGame(btn.dataset.mode));
    });
    renderNextWorldPreview();
  };

  $("btn-mode-switch")?.addEventListener("click", goHome);
  $("btn-next")?.addEventListener("click", nextRound);
  $("btn-play-more")?.addEventListener("click", () => startGame(mode));
  $("btn-go-home")?.addEventListener("click", () => {
    if (KE?.isFirstSessionDone()) window.location.href = "/game/rewards?skip_onboard=1";
    else goHome();
  });
  window.addEventListener("resize", drawMindMap);
  buildStartScreen();
})();
