/* English Shooter — Lily drag vocabulary (fun + G1/G2) */
(function () {
  const vocab = window.LilyVocab;
  if (!vocab?.MODES) {
    console.error("LilyVocab failed to load — check lily_vocab.js");
    return;
  }
  const { MODES, SECTIONS, pickCelebrate } = vocab;
  const lilyTips = {
    correct: ["Giỏi lắm bạn ơi! 🌸", "Bạn thông minh quá! ⭐", "Đúng rồi! Lily rất vui! 💕", "Hoàn hảo luôn! 🎉"],
    wrong: ["Chưa đúng rồi, thử lại nha! 🌼", "Bạn thử lại nhé, gần đúng rồi! 💪", "Không sao, thử thêm lần nữa! 🌸"],
  };
  const ROUNDS_PER_GAME = 10;
  const ITEM_SEL = ".ingredient-item,.clothing-item,.drag-item";

  let mode = "bakery";
  let score = 0;
  let level = 1;
  let roundCount = 0;
  let currentWord = null;
  let currentOptions = [];
  let learnedWords = {};
  let dollOutfit = [];
  let dragEl = null;
  let dragSource = null;

  const $ = (id) => document.getElementById(id);
  const cfg = () => MODES[mode];

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

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
    const stars = score >= 800 ? "⭐⭐⭐" : score >= 400 ? "⭐⭐" : "⭐";
    const msg = score >= 800
      ? "Giỏi xuất sắc! Lily tự hào lắm! 🌟"
      : score >= 400 ? "Làm tốt lắm! Cố thêm nhé! 🌸" : "Tiếp tục cố gắng nhé! 💕";
    $("result-stars").textContent = stars;
    $("result-title").textContent = msg;
    $("res-score").textContent = String(score);
    $("res-words").textContent = String(Object.keys(learnedWords).length);
    $("res-level").textContent = String(level);
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
    learnedWords = {};
    dollOutfit = [];
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

  const buildModeButtons = () => {
    const root = $("mode-sections");
    if (!root) return;
    root.innerHTML = SECTIONS.map((sec) => {
      const btns = Object.entries(MODES)
        .filter(([, m]) => m.section === sec.key)
        .map(([id, m]) => `
          <button type="button" class="mode-btn ${m.btnClass}" data-mode="${id}">
            <span class="mb-icon">${m.icon}</span>
            <div class="mb-title">${m.title}</div>
            <div class="mb-desc">${m.desc}</div>
            ${m.grade ? `<span class="mb-grade">Lớp ${m.grade}</span>` : ""}
          </button>`).join("");
      return `<div class="grade-section"><div class="grade-label">${sec.label}</div><div class="mode-grid">${btns}</div></div>`;
    }).join("");
    root.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => startGame(btn.dataset.mode));
    });
  };

  $("btn-mode-switch")?.addEventListener("click", goHome);
  $("btn-next")?.addEventListener("click", nextRound);
  $("btn-play-again")?.addEventListener("click", goHome);
  window.addEventListener("resize", drawMindMap);
  buildModeButtons();
})();
