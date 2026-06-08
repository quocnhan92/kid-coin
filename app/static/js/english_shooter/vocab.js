/* English Shooter — Vocab mode (learning pace, slower than arcade) */
(function () {
  const LEARN = {
    waveInterval: 400,
    alienSpeed: 0.32,
    bulletVy: -10,
    shootCooldown: 18,
    wobble: 0.5,
  };

  (function starsBg() {
    const c = document.getElementById("stars");
    const ctx = c.getContext("2d");
    const resize = () => {
      c.width = window.innerWidth;
      c.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);
    const stars = Array.from({ length: 180 }, () => ({
      x: Math.random() * c.width,
      y: Math.random() * c.height,
      r: Math.random() * 1.5 + 0.3,
      s: Math.random() * 0.2 + 0.03,
    }));
    const draw = () => {
      ctx.clearRect(0, 0, c.width, c.height);
      stars.forEach((s) => {
        s.y += s.s;
        if (s.y > c.height) s.y = 0;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${0.3 + s.r * 0.3})`;
        ctx.fill();
      });
    };
    setInterval(draw, 40);
  })();

  const topics = {
    Animals: { icon: "🐾", color: "#34d399", words: [
      { en: "CAT", vi: "con mèo" }, { en: "DOG", vi: "con chó" }, { en: "BIRD", vi: "con chim" },
      { en: "FISH", vi: "con cá" }, { en: "COW", vi: "con bò" }, { en: "PIG", vi: "con lợn" },
      { en: "HEN", vi: "con gà mái" }, { en: "DUCK", vi: "con vịt" }, { en: "FROG", vi: "con ếch" },
      { en: "BEAR", vi: "con gấu" }, { en: "LION", vi: "sư tử" }, { en: "DEER", vi: "con hươu" },
    ]},
    Colors: { icon: "🎨", color: "#f472b6", words: [
      { en: "RED", vi: "màu đỏ" }, { en: "BLUE", vi: "màu xanh dương" }, { en: "GREEN", vi: "màu xanh lá" },
      { en: "YELLOW", vi: "màu vàng" }, { en: "PINK", vi: "màu hồng" }, { en: "WHITE", vi: "màu trắng" },
      { en: "BLACK", vi: "màu đen" }, { en: "ORANGE", vi: "màu cam" }, { en: "PURPLE", vi: "màu tím" },
      { en: "BROWN", vi: "màu nâu" }, { en: "GRAY", vi: "màu xám" }, { en: "GOLD", vi: "màu vàng kim" },
    ]},
    Numbers: { icon: "🔢", color: "#60a5fa", words: [
      { en: "ONE", vi: "số một" }, { en: "TWO", vi: "số hai" }, { en: "THREE", vi: "số ba" },
      { en: "FOUR", vi: "số bốn" }, { en: "FIVE", vi: "số năm" }, { en: "SIX", vi: "số sáu" },
      { en: "SEVEN", vi: "số bảy" }, { en: "EIGHT", vi: "số tám" }, { en: "NINE", vi: "số chín" },
      { en: "TEN", vi: "số mười" }, { en: "ZERO", vi: "số không" }, { en: "ELEVEN", vi: "số mười một" },
    ]},
    Family: { icon: "👨‍👩‍👧", color: "#fb923c", words: [
      { en: "MOM", vi: "mẹ" }, { en: "DAD", vi: "bố" }, { en: "BABY", vi: "em bé" },
      { en: "SIS", vi: "chị/em gái" }, { en: "BRO", vi: "anh/em trai" }, { en: "AUNT", vi: "cô/dì" },
      { en: "UNCLE", vi: "chú/bác" }, { en: "GRAN", vi: "bà" }, { en: "GRANDPA", vi: "ông" },
      { en: "WIFE", vi: "vợ" }, { en: "SON", vi: "con trai" }, { en: "GIRL", vi: "con gái" },
    ]},
    School: { icon: "🏫", color: "#a78bfa", words: [
      { en: "PEN", vi: "cái bút" }, { en: "BOOK", vi: "quyển sách" }, { en: "DESK", vi: "cái bàn" },
      { en: "CHAIR", vi: "cái ghế" }, { en: "BAG", vi: "cái túi" }, { en: "MAP", vi: "bản đồ" },
      { en: "RULER", vi: "cái thước" }, { en: "CLASS", vi: "lớp học" }, { en: "BELL", vi: "tiếng chuông" },
      { en: "DRAW", vi: "vẽ tranh" }, { en: "READ", vi: "đọc sách" }, { en: "WRITE", vi: "viết" },
    ]},
    Food: { icon: "🍎", color: "#fbbf24", words: [
      { en: "RICE", vi: "cơm/gạo" }, { en: "CAKE", vi: "bánh ngọt" }, { en: "MILK", vi: "sữa" },
      { en: "EGG", vi: "quả trứng" }, { en: "MEAT", vi: "thịt" }, { en: "SOUP", vi: "món canh" },
      { en: "BREAD", vi: "bánh mì" }, { en: "APPLE", vi: "quả táo" }, { en: "MANGO", vi: "quả xoài" },
      { en: "CORN", vi: "bắp ngô" }, { en: "PEAR", vi: "quả lê" }, { en: "PLUM", vi: "quả mận" },
    ]},
  };

  const topicKeys = Object.keys(topics);
  let topicIdx = 0;
  let score = 0;
  let lives = 3;
  let level = 1;
  let combo = 1;
  let correctCount = 0;
  let gameRunning = false;
  let aliens = [];
  let bullets = [];
  let particles = [];
  let shipX = 0;
  let currentQ = null;
  let learned = {};
  let waveTimer = 0;
  let waveInterval = LEARN.waveInterval;
  let alienSpeed = LEARN.alienSpeed;
  let shootCooldown = 0;
  let mouseX = 0;
  let animId = null;
  let lastTime = 0;

  const speakQuestion = () => {
    if (!currentQ) return;
    const text = `${currentQ.correct.vi}. Tiếng Anh là gì?`;
    if (window.GameUtils) {
      GameUtils.warmupSpeech();
      GameUtils.speak(text);
    }
  };

  const speakWord = (en) => {
    if (!en) return;
    if (window.GameUtils) {
      GameUtils.warmupSpeech();
      GameUtils.speakEn(en.toLowerCase());
    }
  };

  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  const mmCanvas = document.getElementById("mm-canvas");
  const mmCtx = mmCanvas.getContext("2d");

  const resize = () => {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    shipX = canvas.width / 2;
  };
  resize();
  window.addEventListener("resize", resize);

  const pickQuestion = () => {
    const t = topics[topicKeys[topicIdx]];
    const correct = t.words[Math.floor(Math.random() * t.words.length)];
    const pool = [];
    topicKeys.forEach((k) => {
      topics[k].words.forEach((w) => {
        if (w.en !== correct.en) pool.push(w);
      });
    });
    pool.sort(() => Math.random() - 0.5);
    const wrongs = pool.slice(0, 3);
    const opts = [correct, ...wrongs].sort(() => Math.random() - 0.5);
    return { correct, opts, topic: topicKeys[topicIdx] };
  };

  const spawnWave = () => {
    if (!currentQ) currentQ = pickQuestion();
    const q = currentQ;
    const cw = canvas.width;
    const cols = q.opts.length;
    const gap = cw / (cols + 1);
    speakQuestion();
    q.opts.forEach((w, i) => {
      aliens.push({
        x: gap * (i + 1),
        y: -60,
        word: w.en,
        isCorrect: w.en === q.correct.en,
        color: w.en === q.correct.en ? topics[q.topic].color : "#ef4444",
        hp: 1,
        dead: false,
        vy: alienSpeed,
        // vy: alienSpeed + level * 0.08, // arcade: tăng tốc theo level
        angle: Math.random() * 0.3 - 0.15,
        pulse: Math.random() * Math.PI * 2,
      });
    });
  };

  const spawnExplosion = (x, y, color, count = 18) => {
    for (let i = 0; i < count; i++) {
      const ang = Math.random() * Math.PI * 2;
      const spd = Math.random() * 5 + 2;
      particles.push({
        x, y,
        vx: Math.cos(ang) * spd,
        vy: Math.sin(ang) * spd,
        life: 1,
        color,
        r: Math.random() * 4 + 2,
      });
    }
  };

  const drawShip = (x, y) => {
    ctx.save();
    ctx.translate(x, y);
    ctx.beginPath();
    ctx.moveTo(0, -28);
    ctx.lineTo(-18, 14);
    ctx.lineTo(-6, 8);
    ctx.lineTo(0, 16);
    ctx.lineTo(6, 8);
    ctx.lineTo(18, 14);
    ctx.closePath();
    ctx.fillStyle = "#7c3aed";
    ctx.fill();
    ctx.strokeStyle = "#a78bfa";
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.beginPath();
    ctx.ellipse(0, -10, 6, 10, 0, 0, Math.PI * 2);
    ctx.fillStyle = "#c4b5fd";
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(-10, 14, 5, 3, 0, 0, Math.PI * 2);
    ctx.fillStyle = "#f59e0b";
    ctx.globalAlpha = 0.8;
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(10, 14, 5, 3, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.restore();
  };

  const drawAlien = (a) => {
    a.pulse += 0.06;
    const glow = Math.sin(a.pulse) * 0.3 + 0.7;
    ctx.save();
    ctx.translate(a.x, a.y);
    ctx.beginPath();
    ctx.ellipse(0, 0, 34, 14, 0, 0, Math.PI * 2);
    ctx.fillStyle = a.isCorrect ? "rgba(52,211,153,0.15)" : "rgba(239,68,68,0.12)";
    ctx.fill();
    ctx.strokeStyle = a.color;
    ctx.lineWidth = 2 * glow;
    ctx.stroke();
    ctx.beginPath();
    ctx.ellipse(0, -8, 18, 12, 0, 0, Math.PI * 2);
    ctx.fillStyle = a.isCorrect ? "rgba(52,211,153,0.3)" : "rgba(239,68,68,0.2)";
    ctx.fill();
    ctx.strokeStyle = a.color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${a.word.length > 5 ? 11 : 13}px Orbitron,monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.shadowColor = a.color;
    ctx.shadowBlur = 8 * glow;
    ctx.fillText(a.word, 0, 0);
    ctx.shadowBlur = 0;
    ctx.restore();
  };

  const shoot = () => {
    if (shootCooldown > 0) return;
    bullets.push({ x: mouseX, y: canvas.height - 60, vy: LEARN.bulletVy, trail: [] });
    shootCooldown = LEARN.shootCooldown;
  };

  const drawMindMap = () => {
    const t = topicKeys[topicIdx];
    const topic = topics[t];
    const W = mmCanvas.offsetWidth || 196;
    mmCanvas.width = W;
    mmCanvas.height = 200;
    mmCtx.clearRect(0, 0, W, 200);
    const cx = W / 2;
    const cy = 38;
    mmCtx.fillStyle = "rgba(127,119,221,0.18)";
    mmCtx.beginPath();
    mmCtx.ellipse(cx, cy, 46, 18, 0, 0, Math.PI * 2);
    mmCtx.fill();
    mmCtx.strokeStyle = topic.color;
    mmCtx.lineWidth = 2;
    mmCtx.beginPath();
    mmCtx.ellipse(cx, cy, 46, 18, 0, 0, Math.PI * 2);
    mmCtx.stroke();
    mmCtx.fillStyle = "#fff";
    mmCtx.font = "bold 11px Nunito,sans-serif";
    mmCtx.textAlign = "center";
    mmCtx.textBaseline = "middle";
    mmCtx.fillText(`${topic.icon} ${t}`, cx, cy);
    const learnedForTopic = Object.entries(learned).filter(([, v]) => v.topic === t).slice(0, 8);
    const total = Math.max(learnedForTopic.length, 3);
    learnedForTopic.forEach(([en], i) => {
      const angle = (i / total) * Math.PI * 1.6 + Math.PI * 0.2;
      const bx = cx + Math.cos(angle) * 70;
      const by = cy + Math.sin(angle) * 58 + 30;
      mmCtx.strokeStyle = `${topic.color}88`;
      mmCtx.lineWidth = 1.5;
      mmCtx.beginPath();
      mmCtx.moveTo(cx, cy + 18);
      mmCtx.lineTo(bx, by);
      mmCtx.stroke();
      mmCtx.fillStyle = "rgba(127,119,221,0.2)";
      mmCtx.beginPath();
      mmCtx.ellipse(bx, by, 28, 13, 0, 0, Math.PI * 2);
      mmCtx.fill();
      mmCtx.strokeStyle = topic.color;
      mmCtx.lineWidth = 1;
      mmCtx.beginPath();
      mmCtx.ellipse(bx, by, 28, 13, 0, 0, Math.PI * 2);
      mmCtx.stroke();
      mmCtx.fillStyle = "#fff";
      mmCtx.font = "bold 9px Nunito,sans-serif";
      mmCtx.fillText(en, bx, by);
    });
    if (learnedForTopic.length === 0) {
      mmCtx.fillStyle = "#6b7280";
      mmCtx.font = "11px Nunito,sans-serif";
      mmCtx.fillText("Bắn đúng để mở nhánh!", cx, 110);
    }
  };

  const updateLearnedList = () => {
    const el = document.getElementById("learned-list");
    const items = Object.entries(learned).slice(-8).reverse();
    el.innerHTML = items.map(([en, v]) =>
      `<div class="learned-item"><span class="learned-en">${en}</span><span class="learned-vi">${v.vi}</span></div>`
    ).join("");
  };

  const updateHUD = () => {
    document.getElementById("score-el").textContent = String(score).padStart(6, "0");
    const livesEl = document.getElementById("lives-el");
    livesEl.innerHTML = Array.from({ length: 3 }, (_, i) =>
      `<span class="heart">${i < lives ? "❤️" : "🖤"}</span>`
    ).join("");
    document.getElementById("level-el").textContent = level;
    document.getElementById("combo-el").textContent = `x${combo}`;
    const t = topicKeys[topicIdx];
    document.getElementById("topic-el").textContent = `${topics[t].icon} ${t}`;
    if (currentQ) {
      document.getElementById("q-word").textContent = currentQ.correct.vi.toUpperCase();
      document.getElementById("q-meaning").textContent = "→ Tiếng Anh là gì?";
    }
  };

  const showCombo = (pts) => {
    const el = document.createElement("div");
    el.className = "combo-badge";
    el.textContent = combo > 2 ? `COMBO x${combo}! +${pts}` : `+${pts}`;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 700);
  };

  const onCorrectHit = (a) => {
    const pts = 100 * combo;
    score += pts;
    correctCount++;
    combo++;
    learned[a.word] = { vi: currentQ.correct.vi, topic: topicKeys[topicIdx] };
    speakWord(a.word);
    spawnExplosion(a.x, a.y, topics[topicKeys[topicIdx]].color, 30);
    showCombo(pts);
    aliens.filter((x) => !x.dead).forEach((x) => {
      if (!x.isCorrect) x.dead = true;
    });
    currentQ = pickQuestion();
    waveTimer = waveInterval - 60;
    level = Math.floor(score / 1200) + 1;
    // alienSpeed = LEARN.alienSpeed + level * 0.12; // arcade: tăng tốc dần
    updateLearnedList();
    drawMindMap();
  };

  const onWrongHit = (a) => {
    combo = Math.max(1, combo - 1);
    spawnExplosion(a.x, a.y, "#ef4444", 12);
    document.getElementById("hint-el").textContent =
      `❌ "${a.word}" không đúng! Từ đúng là "${currentQ.correct.en}" = ${currentQ.correct.vi}`;
  };

  const handleAlienBottom = (a) => {
    a.dead = true;
    if (a.isCorrect) {
      lives--;
      combo = 1;
      spawnExplosion(a.x, a.y, "#ef4444", 25);
      if (lives <= 0) {
        endGame();
        return;
      }
      currentQ = pickQuestion();
      spawnWave();
      waveTimer = 0;
    } else {
      spawnExplosion(a.x, a.y, "#6b7280", 8);
    }
    updateHUD();
  };

  const loop = (ts) => {
    if (!gameRunning) return;
    lastTime = ts;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    waveTimer++;
    if (waveTimer >= waveInterval && aliens.length === 0) {
      waveTimer = 0;
      topicIdx = (topicIdx + 1) % topicKeys.length;
      currentQ = pickQuestion();
      spawnWave();
      drawMindMap();
      updateHUD();
    }

    shootCooldown = Math.max(0, shootCooldown - 1);
    bullets.forEach((b) => {
      b.trail.push({ x: b.x, y: b.y });
      if (b.trail.length > 10) b.trail.shift();
      b.y += b.vy;
    });

    bullets.forEach((b) => {
      b.trail.forEach((p, i) => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 3 * (i / b.trail.length), 0, Math.PI * 2);
        ctx.fillStyle = `rgba(251,191,36,${(i / b.trail.length) * 0.8})`;
        ctx.fill();
      });
      ctx.beginPath();
      ctx.arc(b.x, b.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#fbbf24";
      ctx.shadowColor = "#f59e0b";
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    aliens.forEach((a) => {
      if (a.dead) return;
      a.y += a.vy;
      a.x += Math.sin(a.angle * a.y * 0.02) * LEARN.wobble;
      drawAlien(a);
      if (a.y > canvas.height - 40) handleAlienBottom(a);
    });

    bullets.forEach((b) => {
      if (b.dead) return;
      aliens.forEach((a) => {
        if (a.dead || b.dead) return;
        if (Math.abs(b.x - a.x) < 38 && Math.abs(b.y - a.y) < 20) {
          b.dead = true;
          a.dead = true;
          if (a.isCorrect) onCorrectHit(a);
          else onWrongHit(a);
          updateHUD();
        }
      });
    });

    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.15;
      p.life -= 0.04;
      p.vx *= 0.95;
    });
    particles.forEach((p) => {
      if (p.life <= 0) return;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * p.life, 0, Math.PI * 2);
      ctx.fillStyle = p.color + Math.floor(p.life * 255).toString(16).padStart(2, "0");
      ctx.fill();
    });

    bullets = bullets.filter((b) => !b.dead && b.y > -20);
    aliens = aliens.filter((a) => !a.dead);
    particles = particles.filter((p) => p.life > 0);

    ctx.strokeStyle = "rgba(127,119,221,0.3)";
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(0, canvas.height - 44);
    ctx.lineTo(canvas.width, canvas.height - 44);
    ctx.stroke();
    ctx.setLineDash([]);

    drawShip(mouseX, canvas.height - 54);
    ctx.strokeStyle = "rgba(251,191,36,0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(mouseX, canvas.height - 82);
    ctx.lineTo(mouseX, 0);
    ctx.stroke();

    animId = requestAnimationFrame(loop);
  };

  const setAimX = (clientX) => {
    const r = canvas.getBoundingClientRect();
    mouseX = Math.max(22, Math.min(canvas.width - 22, clientX - r.left));
  };

  canvas.addEventListener("mousemove", (e) => setAimX(e.clientX));
  canvas.addEventListener("touchmove", (e) => {
    e.preventDefault();
    if (e.touches[0]) setAimX(e.touches[0].clientX);
  }, { passive: false });
  canvas.addEventListener("click", () => { if (gameRunning) shoot(); });
  canvas.addEventListener("touchend", (e) => {
    if (gameRunning && e.changedTouches[0]) {
      setAimX(e.changedTouches[0].clientX);
      shoot();
    }
  });

  const startGame = () => {
    score = 0;
    lives = 3;
    level = 1;
    combo = 1;
    correctCount = 0;
    topicIdx = 0;
    aliens = [];
    bullets = [];
    particles = [];
    learned = {};
    waveTimer = waveInterval;
    alienSpeed = LEARN.alienSpeed;
    currentQ = pickQuestion();
    gameRunning = true;
    updateHUD();
    drawMindMap();
    updateLearnedList();
    document.getElementById("hint-el").textContent = "Nhìn vào mind map để nhớ từ vựng theo nhóm!";
    mouseX = canvas.width / 2;
    lastTime = performance.now();
    animId = requestAnimationFrame(loop);
  };

  const endGame = () => {
    gameRunning = false;
    cancelAnimationFrame(animId);
    document.getElementById("final-score").textContent = String(score).padStart(6, "0");
    document.getElementById("stat-correct").textContent = correctCount;
    document.getElementById("stat-learned").textContent = Object.keys(learned).length;
    document.getElementById("stat-level").textContent = level;
    document.getElementById("over-screen").style.display = "flex";
  };

  document.getElementById("btn-start").onclick = () => {
    document.getElementById("start-screen").style.display = "none";
    startGame();
  };
  document.getElementById("btn-restart").onclick = () => {
    document.getElementById("over-screen").style.display = "none";
    startGame();
  };
})();
