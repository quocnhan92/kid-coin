/* English Shooter — Lily Bakery & Fashion (drag vocabulary) */
(function () {
  const bakeryData = [
    { en: "BUTTER", vi: "bơ", emoji: "🧈", color: "#FDE68A" },
    { en: "EGG", vi: "trứng", emoji: "🥚", color: "#FEF3C7" },
    { en: "MILK", vi: "sữa", emoji: "🥛", color: "#fff" },
    { en: "FLOUR", vi: "bột mì", emoji: "🌾", color: "#FCD34D" },
    { en: "HONEY", vi: "mật ong", emoji: "🍯", color: "#F59E0B" },
    { en: "SUGAR", vi: "đường", emoji: "🍬", color: "#FCA5A5" },
    { en: "CREAM", vi: "kem tươi", emoji: "🍦", color: "#fff" },
    { en: "BERRY", vi: "dâu rừng", emoji: "🫐", color: "#C4B5FD" },
    { en: "LEMON", vi: "chanh", emoji: "🍋", color: "#FEF08A" },
    { en: "COCOA", vi: "ca cao", emoji: "🍫", color: "#78350F" },
    { en: "APPLE", vi: "táo", emoji: "🍎", color: "#FCA5A5" },
    { en: "SALT", vi: "muối", emoji: "🧂", color: "#E2E8F0" },
  ];
  const fashionData = [
    { en: "DRESS", vi: "váy", emoji: "👗", color: "#F9A8D4" },
    { en: "HAT", vi: "mũ", emoji: "👒", color: "#FDE68A" },
    { en: "SHOES", vi: "giày", emoji: "👠", color: "#FCA5A5" },
    { en: "BAG", vi: "túi xách", emoji: "👜", color: "#C4B5FD" },
    { en: "BOW", vi: "nơ", emoji: "🎀", color: "#F9A8D4" },
    { en: "SCARF", vi: "khăn quàng", emoji: "🧣", color: "#A5B4FC" },
    { en: "SKIRT", vi: "chân váy", emoji: "🩱", color: "#6EE7B7" },
    { en: "COAT", vi: "áo khoác", emoji: "🧥", color: "#93C5FD" },
    { en: "CROWN", vi: "vương miện", emoji: "👑", color: "#FDE68A" },
    { en: "GLOVE", vi: "găng tay", emoji: "🧤", color: "#FCA5A5" },
    { en: "SOCKS", vi: "tất", emoji: "🧦", color: "#C4B5FD" },
    { en: "RING", vi: "nhẫn", emoji: "💍", color: "#FDE68A" },
  ];
  const cakeResults = [
    { emoji: "🎂", msg: "Bánh sinh nhật tuyệt vời!" },
    { emoji: "🧁", msg: "Cupcake siêu dễ thương!" },
    { emoji: "🥧", msg: "Bánh pie thơm lừng!" },
    { emoji: "🍰", msg: "Bánh kem ngọt ngào!" },
  ];
  const lilyTips = {
    correct: ["Giỏi lắm bạn ơi! 🌸", "Bạn thông minh quá! ⭐", "Đúng rồi! Lily rất vui! 💕", "Hoàn hảo luôn! 🎉"],
    wrong: ["Chưa đúng rồi, thử lại nha! 🌼", "Bạn thử lại nhé, gần đúng rồi! 💪", "Không sao, thử thêm lần nữa! 🌸"],
  };
  const ROUNDS_PER_GAME = 10;

  let mode = "bakery";
  let score = 0;
  let level = 1;
  let correctCount = 0;
  let roundCount = 0;
  let currentWord = null;
  let currentOptions = [];
  let learnedWords = {};
  let dollOutfit = [];
  let dragEl = null;
  let dragSource = null;

  const $ = (id) => document.getElementById(id);

  const speakQuestion = (word) => {
    if (!word || !window.GameUtils) return;
    GameUtils.warmupSpeech();
    GameUtils.speak(`Hãy tìm ${word.vi} cho Lily nhé!`);
  };

  const speakAnswer = (en) => {
    if (!en || !window.GameUtils) return;
    GameUtils.warmupSpeech();
    GameUtils.speakEn(en.toLowerCase());
  };

  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  const showScreen = (id) => {
    document.querySelectorAll(".screen").forEach((s) => s.classList.add("hide"));
    $(id).classList.remove("hide");
  };

  const goHome = () => showScreen("start-screen");

  const updateHUD = () => {
    $("hud-score").textContent = String(score);
    $("hud-level").textContent = `Level ${level}`;
    const stars = score >= 800 ? "⭐⭐⭐" : score >= 400 ? "⭐⭐" : "⭐";
    $("hud-stars").textContent = stars;
  };

  const showToast = (emoji, msg, en, vi) => {
    $("t-emoji").textContent = emoji;
    $("t-msg").textContent = msg;
    $("t-en").textContent = en;
    $("t-vi").textContent = vi;
    $("toast").classList.add("show");
    if (emoji === "✨") setTimeout(() => $("toast").classList.remove("show"), 1800);
  };

  const drawMindMap = () => {
    const canvas = $("mm-canvas");
    const W = canvas.offsetWidth || 186;
    canvas.width = W;
    canvas.height = 180;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, W, 180);
    const cx = W / 2;
    const cy = 52;
    const isBakery = mode === "bakery";
    const rootColor = isBakery ? "#F9A8D4" : "#C4B5FD";
    const rootText = isBakery ? "🍰 Bánh" : "👗 Thời Trang";
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
    ctx.fillText(rootText, cx, cy);
    const words = Object.values(learnedWords).slice(0, 10);
    if (words.length === 0) {
      ctx.fillStyle = "#C4A0B4";
      ctx.font = "10px Nunito,sans-serif";
      ctx.fillText("Học đúng để mở nhánh!", cx, 115);
      return;
    }
    words.forEach((w, i) => {
      const angle = (i / words.length) * Math.PI * 1.8 + Math.PI * 0.1;
      const r = 60;
      const bx = cx + Math.cos(angle) * r;
      const by = cy + Math.sin(angle) * r + 22;
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
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = "#7C3AED";
      ctx.font = "bold 9px Nunito,sans-serif";
      ctx.fillText(`${w.emoji} ${w.en}`, bx, by);
    });
  };

  const updateChips = () => {
    const isFashion = mode === "fashion";
    $("word-chips").innerHTML = Object.values(learnedWords).map((w) =>
      `<span class="chip${isFashion ? " fashion-chip" : ""}" title="${w.vi}">${w.emoji} ${w.en}</span>`
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

  const renderBakery = () => {
    const shelf = $("ingredient-shelf");
    shelf.innerHTML = "";
    const dz = $("drop-zone");
    dz.textContent = "🥣";
    dz.classList.remove("over");
    currentOptions.forEach((item) => {
      const div = document.createElement("div");
      div.className = "ingredient-item";
      div.draggable = true;
      div.dataset.en = item.en;
      div.innerHTML = `<span class="ii-emoji">${item.emoji}</span><span class="ii-label">${item.en}</span>`;
      bindDragItem(div, item, onTouchEndBakery);
      shelf.appendChild(div);
    });
    dz.ondragover = (e) => { e.preventDefault(); dz.classList.add("over"); };
    dz.ondragleave = () => dz.classList.remove("over");
    dz.ondrop = (e) => {
      e.preventDefault();
      dz.classList.remove("over");
      handleBakeryDrop(dragSource);
    };
  };

  const renderFashion = () => {
    const shelf = $("clothing-shelf");
    shelf.innerHTML = "";
    const doll = $("doll-drop");
    doll.classList.remove("over");
    currentOptions.forEach((item) => {
      const div = document.createElement("div");
      div.className = "clothing-item";
      div.draggable = true;
      div.dataset.en = item.en;
      div.innerHTML = `<span class="ci-emoji">${item.emoji}</span><span class="ci-label">${item.en}</span>`;
      bindDragItem(div, item, onTouchEndFashion);
      shelf.appendChild(div);
    });
    doll.ondragover = (e) => { e.preventDefault(); doll.classList.add("over"); };
    doll.ondragleave = () => doll.classList.remove("over");
    doll.ondrop = (e) => {
      e.preventDefault();
      doll.classList.remove("over");
      handleFashionDrop(dragSource);
    };
  };

  const correctDrop = () => {
    score += 100 * level;
    correctCount++;
    learnedWords[currentWord.en] = currentWord;
    speakAnswer(currentWord.en);
    showToast("✨", pick(lilyTips.correct), currentWord.en, `= ${currentWord.vi}`);
    $("lily-tip").textContent = `${pick(lilyTips.correct)} 🌸`;
    $("btn-next").style.display = "block";
    document.querySelectorAll(".ingredient-item,.clothing-item").forEach((el) => {
      el.draggable = false;
      el.style.opacity = "0.5";
      el.style.cursor = "default";
    });
    document.querySelectorAll(".ingredient-item,.clothing-item").forEach((el) => {
      if (el.dataset.en === currentWord.en) {
        el.style.opacity = "1";
        el.style.border = "3px solid #22C55E";
      }
    });
    updateHUD();
    drawMindMap();
    updateChips();
  };

  const wrongDrop = (en) => {
    $("lily-tip").textContent = pick(lilyTips.wrong);
    document.querySelectorAll(".ingredient-item,.clothing-item").forEach((el) => {
      if (el.dataset.en === en) {
        el.classList.add("wrong-shake");
        setTimeout(() => el.classList.remove("wrong-shake"), 500);
      }
    });
    showToast("💭", "Chưa đúng rồi!", en, `≠ ${currentWord.vi}`);
    setTimeout(() => $("toast").classList.remove("show"), 900);
  };

  const handleBakeryDrop = (item) => {
    if (!item) return;
    if (item.en === currentWord.en) {
      correctDrop();
      const cake = pick(cakeResults);
      $("cake-icon").textContent = cake.emoji;
      $("cake-msg").textContent = cake.msg;
      $("result-cake").style.display = "block";
      $("drop-zone").textContent = currentWord.emoji;
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
    [ $("drop-zone"), $("doll-drop") ].forEach((el) => {
      if (!el) return;
      const r = el.getBoundingClientRect();
      const over = t.clientX > r.left && t.clientX < r.right && t.clientY > r.top && t.clientY < r.bottom;
      el.classList.toggle("over", over);
    });
  };

  const onTouchEndBakery = (e) => {
    const t = e.changedTouches[0];
    resetTouchEl();
    const dz = $("drop-zone");
    const r = dz.getBoundingClientRect();
    if (t.clientX > r.left && t.clientX < r.right && t.clientY > r.top && t.clientY < r.bottom) {
      handleBakeryDrop(dragSource);
    }
    dragEl = null;
    dragSource = null;
  };

  const onTouchEndFashion = (e) => {
    const t = e.changedTouches[0];
    resetTouchEl();
    const dd = $("doll-drop");
    const r = dd.getBoundingClientRect();
    if (t.clientX > r.left && t.clientX < r.right && t.clientY > r.top && t.clientY < r.bottom) {
      handleFashionDrop(dragSource);
    }
    dragEl = null;
    dragSource = null;
  };

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
    const pool = mode === "bakery" ? bakeryData : fashionData;
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    currentWord = shuffled[0];
    currentOptions = [currentWord, ...shuffled.slice(1, 4)].sort(() => Math.random() - 0.5);
    $("speech-en").textContent = currentWord.en;
    $("speech-vi").innerHTML = `Hãy tìm <b>${currentWord.vi}</b> cho Lily nhé!`;
    speakQuestion(currentWord);
    if (mode === "bakery") renderBakery();
    else renderFashion();
    level = Math.floor(score / 300) + 1;
    updateHUD();
  };

  const startGame = (m) => {
    mode = m;
    score = 0;
    level = 1;
    correctCount = 0;
    roundCount = 0;
    learnedWords = {};
    dollOutfit = [];
    showScreen("game-screen");
    $("hud-topic").textContent = m === "bakery" ? "🍰 Tiệm Bánh" : "👗 Tủ Đồ";
    $("bakery-scene").style.display = m === "bakery" ? "flex" : "none";
    $("fashion-scene").style.display = m === "fashion" ? "flex" : "none";
    $("speech-hint").textContent = m === "bakery"
      ? "Kéo đúng nguyên liệu vào bát ✨"
      : "Kéo đúng trang phục cho Lily 💕";
    updateHUD();
    drawMindMap();
    updateChips();
    nextRound();
  };

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.addEventListener("click", () => startGame(btn.dataset.mode));
  });
  $("btn-mode-switch").addEventListener("click", goHome);
  $("btn-next").addEventListener("click", nextRound);
  $("btn-play-again").addEventListener("click", goHome);
  window.addEventListener("resize", drawMindMap);
})();
