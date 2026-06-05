/**
 * Math Blast V2 Flappy — âm thanh & TTS
 *
 * Thêm file vào: app/static/audio/math_blast_v2/
 *   flappy_bgm.mp3          — nhạc nền (loop ~90s)
 *   flappy_correct.ogg      — đúng (hoặc .mp3)
 *   flappy_wrong_soft.ogg   — sai nhẹ (hoặc .mp3)
 *   flappy_combo_3.ogg      — combo ≥3 (tuỳ chọn)
 *   flappy_combo_5.ogg      — combo ≥5 (tuỳ chọn)
 *
 * Thiếu file → dùng tiếng tổng hợp Web Audio (vẫn chơi được).
 */
(function (global) {
  const BASE = '/static/audio/math_blast_v2/';
  const LS_BGM = 'mb_v2_flappy_bgm';
  const LS_TTS = 'mb_v2_flappy_tts';
  const LS_TTS_EM = 'em_math_flappy_tts';

  const FILE_CANDIDATES = {
    bgm: ['flappy_bgm.mp3', 'flappy_bgm.ogg'],
    correct: ['flappy_correct.ogg', 'flappy_correct.mp3'],
    wrong: ['flappy_wrong_soft.ogg', 'flappy_wrong_soft.mp3'],
    combo3: ['flappy_combo_3.ogg', 'flappy_combo_3.mp3'],
    combo5: ['flappy_combo_5.ogg', 'flappy_combo_5.mp3'],
  };

  let audioCtx = null;
  let unlocked = false;
  let activeTier = 'T1';
  let activeGrade = 1;
  let bgmEl = null;
  let bgmFadeTimer = null;
  const sfx = {};

  function getCtx() {
    if (!audioCtx) {
      const Ctx = global.AudioContext || global.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    return audioCtx;
  }

  function unlock() {
    if (unlocked) return;
    unlocked = true;
    const ctx = getCtx();
    if (ctx && ctx.state === 'suspended') ctx.resume();
    if (bgmEl) {
      bgmEl.play().catch(() => {});
      if (!getBgmEnabled()) bgmEl.pause();
    }
  }

  function loadFirstAvailable(names) {
    return new Promise((resolve) => {
      let i = 0;
      function tryNext() {
        if (i >= names.length) {
          resolve(null);
          return;
        }
        const el = new Audio(BASE + names[i]);
        el.preload = 'auto';
        const onOk = () => {
          el.removeEventListener('canplaythrough', onOk);
          el.removeEventListener('error', onErr);
          resolve(el);
        };
        const onErr = () => {
          el.removeEventListener('canplaythrough', onOk);
          el.removeEventListener('error', onErr);
          i += 1;
          tryNext();
        };
        el.addEventListener('canplaythrough', onOk);
        el.addEventListener('error', onErr);
        el.load();
      }
      tryNext();
    });
  }

  function playClip(el, volume) {
    if (!el) return false;
    unlock();
    try {
      el.volume = volume;
      el.currentTime = 0;
      el.play().catch(() => {});
      return true;
    } catch (e) {
      return false;
    }
  }

  function tone(freq, duration, type, gain, when) {
    const ctx = getCtx();
    if (!ctx) return;
    const t0 = when || ctx.currentTime;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type || 'sine';
    osc.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain, t0 + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + duration);
    osc.connect(g);
    g.connect(ctx.destination);
    osc.start(t0);
    osc.stop(t0 + duration + 0.05);
  }

  function synthCorrect() {
    unlock();
    const ctx = getCtx();
    if (!ctx) return;
    const t = ctx.currentTime;
    tone(523.25, 0.08, 'sine', 0.22, t);
    tone(659.25, 0.12, 'sine', 0.2, t + 0.07);
  }

  function synthWrong() {
    unlock();
    const ctx = getCtx();
    if (!ctx) return;
    const t = ctx.currentTime;
    tone(330, 0.18, 'triangle', 0.12, t);
  }

  function synthCombo() {
    unlock();
    const ctx = getCtx();
    if (!ctx) return;
    const t = ctx.currentTime;
    tone(587.33, 0.1, 'sine', 0.18, t);
    tone(739.99, 0.1, 'sine', 0.16, t + 0.08);
    tone(880, 0.14, 'sine', 0.14, t + 0.16);
  }

  function playSfx(key, volume, synthFn) {
    if (sfx[key] && playClip(sfx[key], volume)) return;
    synthFn();
  }

  function questionToSpeechText(item) {
    if ((global.isEnglishMath && global.isEnglishMath()) && global.EnglishMathSpeech) {
      return global.EnglishMathSpeech.speechFromItem(item) || '';
    }
    if (!item || !item.q) return '';
    let q = item.q.trim();
    if (q.includes('? +')) {
      const m = q.match(/\? \+ (\d+) = (\d+)/);
      if (m) return `Mấy cộng ${m[1]} bằng ${m[2]}?`;
    }
    if (q.includes('+ ?')) {
      const m = q.match(/(\d+) \+ \? = (\d+)/);
      if (m) return `${m[1]} cộng mấy bằng ${m[2]}?`;
    }
    q = q.replace(/\s*=\s*\?$/u, '');
    q = q
      .replace(/\+/g, ' cộng ')
      .replace(/−|-/g, ' trừ ')
      .replace(/×/g, ' nhân ')
      .replace(/÷/g, ' chia ');
    if (q.includes('lớn hơn')) return q.replace('—', ',').replace('?', '');
    if (q.includes('Chia') && q.includes('tỉ')) return q;
    return `${q.trim()} bằng mấy?`;
  }

  function ttsStorageKey() {
    return global.isEnglishMath && global.isEnglishMath() ? LS_TTS_EM : LS_TTS;
  }

  function getTtsEnabled() {
    if (global.isEnglishMath && global.isEnglishMath()) {
      const stored = global.localStorage.getItem(LS_TTS_EM);
      if (stored === '0') return false;
      return true;
    }
    const stored = global.localStorage.getItem(LS_TTS);
    if (stored === '1') return true;
    if (stored === '0') return false;
    return activeGrade <= 2;
  }

  function setTtsEnabled(on) {
    global.localStorage.setItem(ttsStorageKey(), on ? '1' : '0');
  }

  function getBgmEnabled() {
    return global.localStorage.getItem(LS_BGM) === '1';
  }

  function setBgmEnabled(on) {
    global.localStorage.setItem(LS_BGM, on ? '1' : '0');
  }

  function stopSpeech() {
    if (global.speechSynthesis) global.speechSynthesis.cancel();
  }

  function speakQuestion(item, opts) {
    const em = global.isEnglishMath && global.isEnglishMath();
    if (!getTtsEnabled() && !(opts && opts.force)) return;
    let text = questionToSpeechText(item);
    if (!text && item && item.q) {
      text = em ? `What is ${item.q.replace(/\s*=\s*\?/u, '').trim()}?` : '';
    }
    if (!text) return;
    stopSpeech();
    unlock();
    if (global.GameUtils && global.GameUtils.warmupSpeech) global.GameUtils.warmupSpeech();
    if (em && global.GameUtils && global.GameUtils.speakEn) {
      global.GameUtils.speakEn(text);
      return;
    }
    if (global.EnglishMathSpeech) {
      global.EnglishMathSpeech.speak(text);
      return;
    }
    if (global.GameUtils && global.GameUtils.speak) {
      global.GameUtils.speak(text);
    }
  }

  function startBgm() {
    if (!getBgmEnabled() || !bgmEl) return;
    unlock();
    if (bgmFadeTimer) {
      clearInterval(bgmFadeTimer);
      bgmFadeTimer = null;
    }
    bgmEl.volume = 0.28;
    bgmEl.loop = true;
    bgmEl.play().catch(() => {});
  }

  function stopBgm(fadeMs) {
    if (!bgmEl) return;
    if (bgmFadeTimer) clearInterval(bgmFadeTimer);
    if (!fadeMs || fadeMs <= 0) {
      bgmEl.pause();
      bgmEl.currentTime = 0;
      return;
    }
    const steps = 20;
    const step = bgmEl.volume / steps;
    let n = 0;
    bgmFadeTimer = setInterval(() => {
      n += 1;
      bgmEl.volume = Math.max(0, bgmEl.volume - step);
      if (n >= steps) {
        clearInterval(bgmFadeTimer);
        bgmFadeTimer = null;
        bgmEl.pause();
        bgmEl.currentTime = 0;
        bgmEl.volume = 0.28;
      }
    }, fadeMs / steps);
  }

  function updateToggleUi(ttsBtn, bgmBtn) {
    const em = global.isEnglishMath && global.isEnglishMath();
    const ttsOn = getTtsEnabled();
    if (ttsBtn) {
      ttsBtn.classList.toggle('active', ttsOn);
      ttsBtn.setAttribute('aria-pressed', ttsOn ? 'true' : 'false');
      ttsBtn.textContent = em
        ? (ttsOn ? '🔊 Read aloud' : '🔇 Read aloud off')
        : (ttsOn ? '🔊 Đọc đề' : '🔇 Đọc đề');
    }
    if (bgmBtn) {
      const bgmOn = getBgmEnabled();
      bgmBtn.classList.toggle('active', bgmOn);
      bgmBtn.setAttribute('aria-pressed', bgmOn ? 'true' : 'false');
      bgmBtn.textContent = em
        ? (bgmOn ? '🎵 Music on' : '🎵 Music off')
        : (bgmOn ? '🎵 Nhạc bật' : '🎵 Nhạc tắt');
    }
    const bird = document.getElementById('flappy-bird');
    if (bird) {
      bird.classList.toggle('mb-bird-speak', ttsOn);
      bird.title = ttsOn
        ? (em ? 'Tap bird to hear again' : 'Chạm chim để nghe lại câu hỏi')
        : '';
    }
  }

  function bindToggles(ttsBtn, bgmBtn) {
    if (ttsBtn && !ttsBtn.dataset.bound) {
      ttsBtn.dataset.bound = '1';
      ttsBtn.addEventListener('click', () => {
        unlock();
        setTtsEnabled(!getTtsEnabled());
        updateToggleUi(ttsBtn, bgmBtn);
        if (getTtsEnabled()) {
          const q = global.__flappyCurrentQuestion;
          if (q) speakQuestion(q, { force: true });
        } else {
          stopSpeech();
        }
      });
    }
    if (bgmBtn && !bgmBtn.dataset.bound) {
      bgmBtn.dataset.bound = '1';
      bgmBtn.addEventListener('click', () => {
        unlock();
        const next = !getBgmEnabled();
        setBgmEnabled(next);
        updateToggleUi(ttsBtn, bgmBtn);
        if (next) startBgm();
        else stopBgm(400);
      });
    }
    updateToggleUi(ttsBtn, bgmBtn);
  }

  async function init() {
    const [bgm, correct, wrong, combo3, combo5] = await Promise.all([
      loadFirstAvailable(FILE_CANDIDATES.bgm),
      loadFirstAvailable(FILE_CANDIDATES.correct),
      loadFirstAvailable(FILE_CANDIDATES.wrong),
      loadFirstAvailable(FILE_CANDIDATES.combo3),
      loadFirstAvailable(FILE_CANDIDATES.combo5),
    ]);
    if (bgm) {
      bgmEl = bgm;
      bgmEl.loop = true;
    }
    if (correct) sfx.correct = correct;
    if (wrong) sfx.wrong = wrong;
    if (combo3) sfx.combo3 = combo3;
    if (combo5) sfx.combo5 = combo5;
  }

  function setTier(tier) {
    activeTier = tier || 'T1';
  }

  function setGrade(grade) {
    const g = parseInt(grade, 10);
    activeGrade = g >= 1 && g <= 5 ? g : 1;
    activeTier = `T${activeGrade}`;
  }

  function playCorrect() {
    playSfx('correct', 0.75, synthCorrect);
  }

  function playWrong() {
    playSfx('wrong', 0.55, synthWrong);
  }

  function playCombo(combo) {
    if (combo >= 5 && sfx.combo5) playClip(sfx.combo5, 0.65);
    else if (combo >= 3 && sfx.combo3) playClip(sfx.combo3, 0.65);
    else if (combo >= 5 || combo >= 3) synthCombo();
  }

  global.FlappyAudio = {
    init,
    unlock,
    setTier,
    setGrade,
    getTtsEnabled,
    setTtsEnabled,
    getBgmEnabled,
    setBgmEnabled,
    speakQuestion,
    stopSpeech,
    questionToSpeechText,
    playCorrect,
    playWrong,
    playCombo,
    startBgm,
    stopBgm,
    bindToggles,
    updateToggleUi,
  };
})(typeof window !== 'undefined' ? window : global);
