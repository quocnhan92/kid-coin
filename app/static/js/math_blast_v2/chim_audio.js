/**
 * Chim Toán Vui — nhạc nền, ting ting khi trúng, TTS đọc đề.
 */
(function (global) {
  const BASE = '/static/audio/math_blast_v2/';
  const LS_BGM = 'mb_v2_chim_bgm';
  const LS_TTS = 'mb_v2_chim_tts';

  const FILE_CANDIDATES = {
    bgm: ['chim_bgm.mp3', 'flappy_bgm.mp3', 'flappy_bgm.ogg'],
    correct: ['chim_correct.ogg', 'chim_correct.mp3', 'flappy_correct.ogg', 'flappy_correct.mp3'],
    wrong: ['flappy_wrong_soft.ogg', 'flappy_wrong_soft.mp3'],
  };

  let audioCtx = null;
  let unlocked = false;
  let speechPrimed = false;
  let activeGrade = 1;
  let bgmEl = null;
  let bgmFadeTimer = null;
  let initPromise = null;
  let prefsInitialized = false;
  let toggleUiSynced = false;
  const sfx = {};

  function getCtx() {
    if (!audioCtx) {
      const Ctx = global.AudioContext || global.webkitAudioContext;
      if (Ctx) audioCtx = new Ctx();
    }
    return audioCtx;
  }

  function pickViVoice() {
    if (!global.speechSynthesis) return null;
    const voices = global.speechSynthesis.getVoices() || [];
    return (
      voices.find((v) => v.lang === 'vi-VN') ||
      voices.find((v) => v.lang && v.lang.startsWith('vi')) ||
      null
    );
  }

  function primeSpeech() {
    if (speechPrimed || !global.speechSynthesis) return;
    speechPrimed = true;
    const loadVoices = () => pickViVoice();
    loadVoices();
    if (!global.speechSynthesis.getVoices().length) {
      global.speechSynthesis.addEventListener('voiceschanged', loadVoices, { once: true });
    }
  }

  function mountToBody(el) {
    if (!el || el.dataset.chimMounted) return;
    el.dataset.chimMounted = '1';
    el.setAttribute('playsinline', '');
    el.preload = 'auto';
    if (!el.isConnected) {
      el.style.cssText = 'position:fixed;width:0;height:0;opacity:0;pointer-events:none';
      document.body.appendChild(el);
    }
  }

  function unlock() {
    const ctx = getCtx();
    if (ctx && ctx.state === 'suspended') {
      ctx.resume().catch(() => {});
    }
    primeSpeech();
    unlocked = true;
    if (bgmEl && getBgmEnabled()) tryPlayBgm();
  }

  function tryPlayBgm() {
    if (!bgmEl || !getBgmEnabled()) return false;
    mountToBody(bgmEl);
    bgmEl.volume = 0.28;
    bgmEl.loop = true;
    const p = bgmEl.play();
    if (p && typeof p.then === 'function') {
      p.catch((err) => {
        console.warn('[ChimAudio] nhạc nền:', err.message || err);
        if (global.MathBlastV2 && global.MathBlastV2.toast) {
          global.MathBlastV2.toast('Không phát nhạc — thử bấm lại sau khi chạm màn hình');
        }
      });
    }
    return true;
  }

  function loadFirstAvailable(names) {
    return new Promise((resolve) => {
      let i = 0;
      function tryNext() {
        if (i >= names.length) {
          resolve(null);
          return;
        }
        const url = BASE + names[i];
        const el = new Audio();
        el.preload = 'auto';
        let settled = false;
        const finish = (ok) => {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          el.removeEventListener('canplaythrough', onOk);
          el.removeEventListener('loadeddata', onOk);
          el.removeEventListener('error', onErr);
          if (ok) {
            el.src = url;
            resolve(el);
          } else {
            i += 1;
            tryNext();
          }
        };
        const onOk = () => finish(true);
        const onErr = () => finish(false);
        const timer = setTimeout(() => finish(true), 8000);
        el.addEventListener('canplaythrough', onOk, { once: true });
        el.addEventListener('loadeddata', onOk, { once: true });
        el.addEventListener('error', onErr, { once: true });
        el.src = url;
        el.load();
      }
      tryNext();
    });
  }

  function playClip(el, volume) {
    if (!el) return false;
    unlock();
    mountToBody(el);
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
    tone(880, 0.07, 'sine', 0.2, t);
    tone(1174.66, 0.09, 'sine', 0.22, t + 0.09);
    tone(1318.51, 0.06, 'sine', 0.15, t + 0.18);
  }

  function synthWrong() {
    unlock();
    const ctx = getCtx();
    if (!ctx) return;
    tone(392, 0.15, 'triangle', 0.1, ctx.currentTime);
  }

  function playSfx(key, volume, synthFn) {
    if (sfx[key] && playClip(sfx[key], volume)) return;
    synthFn();
  }

  function questionToSpeechText(item) {
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
    return `${q.trim()} bằng mấy?`;
  }

  /** Đọc đề / nhạc nền — cấu hình độc lập, không phụ thuộc lớp hay bắt đầu chơi. */
  function ensurePrefsInitialized() {
    if (prefsInitialized) return;
    if (global.localStorage.getItem(LS_TTS) == null) {
      global.localStorage.setItem(LS_TTS, '1');
    }
    if (global.localStorage.getItem(LS_BGM) == null) {
      global.localStorage.setItem(LS_BGM, '0');
    }
    prefsInitialized = true;
  }

  function getTtsEnabled() {
    ensurePrefsInitialized();
    return global.localStorage.getItem(LS_TTS) === '1';
  }

  function setTtsEnabled(on) {
    ensurePrefsInitialized();
    global.localStorage.setItem(LS_TTS, on ? '1' : '0');
  }

  function getBgmEnabled() {
    ensurePrefsInitialized();
    return global.localStorage.getItem(LS_BGM) === '1';
  }

  function setBgmEnabled(on) {
    ensurePrefsInitialized();
    global.localStorage.setItem(LS_BGM, on ? '1' : '0');
  }

  function stopSpeech() {
    if (global.speechSynthesis) global.speechSynthesis.cancel();
  }

  function speakText(text) {
    if (!text) return false;
    unlock();
    stopSpeech();
    if (global.GameUtils && typeof global.GameUtils.speak === 'function') {
      global.GameUtils.speak(text);
      return true;
    }
    if (!global.speechSynthesis) return false;
    const run = () => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'vi-VN';
      utterance.rate = 0.95;
      utterance.pitch = 1.1;
      utterance.volume = 1;
      const vi = pickViVoice();
      if (vi) utterance.voice = vi;
      try {
        global.speechSynthesis.speak(utterance);
      } catch (e) {
        console.warn('[ChimAudio] TTS:', e);
      }
    };
    setTimeout(run, 30);
    return true;
  }

  function speakQuestion(item, opts) {
    if (!getTtsEnabled() && !(opts && opts.force)) return;
    const text = questionToSpeechText(item);
    if (!text) return;
    speakText(text);
  }

  async function ensureReady() {
    if (initPromise) return initPromise;
    return init();
  }

  function startBgm() {
    if (!getBgmEnabled()) return;
    unlock();
    if (!bgmEl) {
      ensureReady().then(() => {
        if (getBgmEnabled()) tryPlayBgm();
      });
      return;
    }
    if (bgmFadeTimer) {
      clearInterval(bgmFadeTimer);
      bgmFadeTimer = null;
    }
    tryPlayBgm();
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

  function updateTtsButton(ttsBtn) {
    if (!ttsBtn) return;
    const on = getTtsEnabled();
    ttsBtn.classList.toggle('active', on);
    ttsBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    ttsBtn.textContent = on ? '🔊 Đọc đề' : '🔇 Đọc đề';
  }

  function updateBgmButton(bgmBtn) {
    if (!bgmBtn) return;
    const on = getBgmEnabled();
    bgmBtn.classList.toggle('active', on);
    bgmBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    bgmBtn.textContent = on ? '🎵 Nhạc bật' : '🎵 Nhạc tắt';
  }

  function syncToggleUiOnce() {
    if (toggleUiSynced) return;
    ensurePrefsInitialized();
    updateTtsButton(document.getElementById('chim-toggle-tts'));
    updateBgmButton(document.getElementById('chim-toggle-bgm'));
    toggleUiSynced = true;
  }

  function toastMsg(msg) {
    if (global.MathBlastV2 && global.MathBlastV2.toast) global.MathBlastV2.toast(msg);
  }

  function onTtsToggle(ttsBtn) {
    unlock();
    const next = !getTtsEnabled();
    setTtsEnabled(next);
    updateTtsButton(ttsBtn);
    if (next) {
      toastMsg('🔊 Đã bật đọc đề');
      const q = global.__chimCurrentQuestion;
      if (q) speakQuestion(q, { force: true });
      else speakText('Chim Toán Vui, sẵn sàng chơi');
    } else {
      stopSpeech();
      toastMsg('🔇 Đã tắt đọc đề');
    }
  }

  async function onBgmToggle(bgmBtn) {
    unlock();
    await ensureReady();
    const next = !getBgmEnabled();
    setBgmEnabled(next);
    updateBgmButton(bgmBtn);
    if (next) {
      if (tryPlayBgm()) toastMsg('🎵 Đã bật nhạc nền');
      else toastMsg('Đang tải nhạc… bấm Nhạc bật lại');
    } else {
      stopBgm(400);
      toastMsg('🎵 Đã tắt nhạc nền');
    }
  }

  function handleTtsClick(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    onTtsToggle(document.getElementById('chim-toggle-tts'));
  }

  async function handleBgmClick(e) {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    await onBgmToggle(document.getElementById('chim-toggle-bgm'));
  }

  function wireToggleDelegation() {
    if (global.__chimAudioDelegation) return;
    global.__chimAudioDelegation = true;
    document.addEventListener(
      'click',
      (e) => {
        const tts = e.target.closest('[data-chim-audio="tts"]');
        if (tts) {
          handleTtsClick(e);
          return;
        }
        const bgm = e.target.closest('[data-chim-audio="bgm"]');
        if (bgm) {
          handleBgmClick(e);
        }
      },
      true
    );
  }

  async function init() {
    if (initPromise) return initPromise;
    initPromise = (async () => {
      const [bgm, correct, wrong] = await Promise.all([
        loadFirstAvailable(FILE_CANDIDATES.bgm),
        loadFirstAvailable(FILE_CANDIDATES.correct),
        loadFirstAvailable(FILE_CANDIDATES.wrong),
      ]);
      if (bgm) {
        bgmEl = bgm;
        bgmEl.loop = true;
        bgmEl.volume = 0.28;
        mountToBody(bgmEl);
      } else {
        console.warn('[ChimAudio] Không tải được chim_bgm.mp3 — kiểm tra /static/audio/math_blast_v2/');
      }
      if (correct) sfx.correct = correct;
      if (wrong) sfx.wrong = wrong;
      primeSpeech();
      return { bgm: !!bgm };
    })();
    return initPromise;
  }

  function setGrade(grade) {
    const g = parseInt(grade, 10);
    activeGrade = g >= 1 && g <= 5 ? g : 1;
  }

  function playCorrect() {
    playSfx('correct', 0.8, synthCorrect);
  }

  function playWrong() {
    playSfx('wrong', 0.45, synthWrong);
  }

  global.ChimAudio = {
    init,
    ensureReady,
    unlock,
    setGrade,
    playCorrect,
    playWrong,
    speakQuestion,
    speakText,
    stopSpeech,
    startBgm,
    stopBgm,
    ensurePrefsInitialized,
    syncToggleUiOnce,
    getTtsEnabled,
    getBgmEnabled,
    isBgmLoaded: () => !!bgmEl,
    handleTtsClick,
    handleBgmClick,
  };

  wireToggleDelegation();
  ensurePrefsInitialized();

  document.addEventListener('DOMContentLoaded', () => {
    syncToggleUiOnce();
    init().catch((e) => console.warn('[ChimAudio] init', e));
  });
})();
