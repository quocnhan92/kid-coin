(function (global) {
  const LS_BGM = 'reward_space_bgm';
  const LS_SFX = 'reward_space_sfx';
  let ctx = null;
  let bgmNodes = null;
  let bgmOn = false;
  let bgmMode = 'ambient';
  let bgmTimer = null;
  let bgmStep = 0;
  let unlocked = false;

  function getCtx() {
    if (!ctx) {
      const Ctx = global.AudioContext || global.webkitAudioContext;
      if (Ctx) ctx = new Ctx();
    }
    return ctx;
  }

  function getBgmEnabled() {
    return global.localStorage.getItem(LS_BGM) !== '0';
  }

  function getSfxEnabled() {
    return global.localStorage.getItem(LS_SFX) !== '0';
  }

  function unlock() {
    if (unlocked) return;
    unlocked = true;
    const c = getCtx();
    if (c?.state === 'suspended') c.resume();
  }

  function tone(freq, dur, type, gain, when) {
    const c = getCtx();
    if (!c || !getSfxEnabled()) return;
    const t0 = when ?? c.currentTime;
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = type || 'sine';
    osc.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(Math.max(gain, 0.0002), t0 + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    osc.connect(g);
    g.connect(c.destination);
    osc.start(t0);
    osc.stop(t0 + dur + 0.04);
  }

  function playShoot() {
    playPew();
  }

  function playPew() {
    unlock();
    const c = getCtx();
    if (!c || !getSfxEnabled()) return;
    const t = c.currentTime;
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(1680, t);
    osc.frequency.exponentialRampToValueAtTime(420, t + 0.07);
    g.gain.setValueAtTime(0.07, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
    osc.connect(g);
    g.connect(c.destination);
    osc.start(t);
    osc.stop(t + 0.1);
    tone(990, 0.04, 'triangle', 0.035, t);
  }

  function playFlyBup() {
    unlock();
    const c = getCtx();
    if (!c || !getSfxEnabled()) return;
    const t = c.currentTime;
    tone(196, 0.055, 'sine', 0.11, t);
    tone(247, 0.055, 'sine', 0.09, t + 0.065);
  }

  function playFlyBoom() {
    unlock();
    const c = getCtx();
    if (!c || !getSfxEnabled()) return;
    const t = c.currentTime;
    const len = Math.floor(c.sampleRate * 0.18);
    const buf = c.createBuffer(1, len, c.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < len; i += 1) ch[i] = Math.random() * 2 - 1;
    const src = c.createBufferSource();
    src.buffer = buf;
    const nf = c.createBiquadFilter();
    nf.type = 'bandpass';
    nf.frequency.setValueAtTime(900, t);
    nf.frequency.exponentialRampToValueAtTime(180, t + 0.16);
    const ng = c.createGain();
    ng.gain.setValueAtTime(0.14, t);
    ng.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
    src.connect(nf);
    nf.connect(ng);
    ng.connect(c.destination);
    src.start(t);
    src.stop(t + 0.2);
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(320, t);
    osc.frequency.exponentialRampToValueAtTime(55, t + 0.2);
    g.gain.setValueAtTime(0.09, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.22);
    osc.connect(g);
    g.connect(c.destination);
    osc.start(t);
    osc.stop(t + 0.24);
  }

  function playHit() {
    playFlyBoom();
  }

  function playHurt() {
    playShipBoom();
  }

  function playShipBoom() {
    unlock();
    const c = getCtx();
    if (!c || !getSfxEnabled()) return;
    if (c.state === 'suspended') c.resume();
    const t = c.currentTime;
    tone(52, 0.4, 'sine', 0.32, t);
    tone(95, 0.22, 'square', 0.2, t + 0.03);
    const len = Math.floor(c.sampleRate * 0.32);
    const buf = c.createBuffer(1, len, c.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < len; i += 1) ch[i] = Math.random() * 2 - 1;
    const src = c.createBufferSource();
    src.buffer = buf;
    const nf = c.createBiquadFilter();
    nf.type = 'bandpass';
    nf.frequency.setValueAtTime(1400, t);
    nf.frequency.exponentialRampToValueAtTime(90, t + 0.28);
    const ng = c.createGain();
    ng.gain.setValueAtTime(0.38, t);
    ng.gain.exponentialRampToValueAtTime(0.0001, t + 0.32);
    src.connect(nf);
    nf.connect(ng);
    ng.connect(c.destination);
    src.start(t);
    src.stop(t + 0.34);
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(220, t);
    osc.frequency.exponentialRampToValueAtTime(35, t + 0.35);
    g.gain.setValueAtTime(0.24, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.36);
    osc.connect(g);
    g.connect(c.destination);
    osc.start(t);
    osc.stop(t + 0.38);
  }

  function playPickup() {
    unlock();
    const c = getCtx();
    if (!c) return;
    const t = c.currentTime;
    tone(784, 0.07, 'sine', 0.09, t);
    tone(988, 0.1, 'sine', 0.07, t + 0.07);
  }

  function stopBgm() {
    if (bgmTimer) {
      clearInterval(bgmTimer);
      bgmTimer = null;
    }
    if (!bgmNodes) {
      bgmOn = false;
      return;
    }
    try {
      bgmNodes.osc?.forEach((o) => o.stop());
      bgmNodes.lfo?.stop();
      bgmNodes.noise?.stop();
    } catch (_) { /* already stopped */ }
    bgmNodes = null;
    bgmOn = false;
    bgmMode = 'ambient';
  }

  function startAmbientBgm() {
    if (!getBgmEnabled() || (bgmOn && bgmMode === 'ambient')) return;
    unlock();
    const c = getCtx();
    if (!c) return;
    stopBgm();
    const master = c.createGain();
    master.gain.value = 0.035;
    const filter = c.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 520;
    filter.Q.value = 0.6;
    const lfo = c.createOscillator();
    const lfoG = c.createGain();
    lfo.frequency.value = 0.08;
    lfoG.gain.value = 120;
    lfo.connect(lfoG);
    lfoG.connect(filter.frequency);
    const osc = [
      { type: 'sine', f: 55 },
      { type: 'triangle', f: 82.5 },
      { type: 'sine', f: 110 },
    ].map((s) => {
      const o = c.createOscillator();
      o.type = s.type;
      o.frequency.value = s.f;
      o.connect(filter);
      o.start();
      return o;
    });
    filter.connect(master);
    master.connect(c.destination);
    lfo.start();
    bgmNodes = { osc, lfo, master, filter };
    bgmOn = true;
    bgmMode = 'ambient';
  }

  function startBgm() {
    if (global.__rewardBgmMode === 'cartoon') startCartoonBgm();
    else startAmbientBgm();
  }

  const CARTOON_ARP = [392, 440, 523.25, 659.25, 587.33, 493.88, 440, 349.23];

  function playCartoonArpNote() {
    const c = getCtx();
    if (!c || !getBgmEnabled() || bgmMode !== 'cartoon') return;
    const freq = CARTOON_ARP[bgmStep % CARTOON_ARP.length];
    bgmStep += 1;
    const t = c.currentTime;
    const osc = c.createOscillator();
    const g = c.createGain();
    osc.type = 'triangle';
    osc.frequency.value = freq;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.045, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.22);
    osc.connect(g);
    g.connect(bgmNodes.master);
    osc.start(t);
    osc.stop(t + 0.25);
  }

  function startCartoonBgm() {
    if (!getBgmEnabled() || (bgmOn && bgmMode === 'cartoon')) return;
    unlock();
    const c = getCtx();
    if (!c) return;
    stopBgm();
    bgmStep = 0;
    const master = c.createGain();
    master.gain.value = 0.9;
    const engine = c.createOscillator();
    engine.type = 'sawtooth';
    engine.frequency.value = 73;
    const engG = c.createGain();
    engG.gain.value = 0.018;
    const engF = c.createBiquadFilter();
    engF.type = 'lowpass';
    engF.frequency.value = 280;
    engine.connect(engF);
    engF.connect(engG);
    engG.connect(master);
    engine.start();
    const hum = c.createOscillator();
    hum.type = 'sine';
    hum.frequency.value = 146;
    const humG = c.createGain();
    humG.gain.value = 0.012;
    hum.connect(humG);
    humG.connect(master);
    hum.start();
    const lfo = c.createOscillator();
    const lfoG = c.createGain();
    lfo.frequency.value = 0.35;
    lfoG.gain.value = 40;
    lfo.connect(lfoG);
    lfoG.connect(engF.frequency);
    lfo.start();
    const nLen = Math.floor(c.sampleRate * 2);
    const nBuf = c.createBuffer(1, nLen, c.sampleRate);
    const nCh = nBuf.getChannelData(0);
    for (let i = 0; i < nLen; i += 1) nCh[i] = Math.random() * 2 - 1;
    const noise = c.createBufferSource();
    noise.buffer = nBuf;
    noise.loop = true;
    const nF = c.createBiquadFilter();
    nF.type = 'bandpass';
    nF.frequency.value = 420;
    nF.Q.value = 0.8;
    const nG = c.createGain();
    nG.gain.value = 0.006;
    noise.connect(nF);
    nF.connect(nG);
    nG.connect(master);
    noise.start();
    master.connect(c.destination);
    bgmNodes = { osc: [engine, hum], lfo, noise, master };
    bgmOn = true;
    bgmMode = 'cartoon';
    playCartoonArpNote();
    bgmTimer = setInterval(playCartoonArpNote, 340);
  }

  function mountToggle(parent) {
    if (!parent || parent.querySelector('.sf-audio-bar')) return;
    const bar = document.createElement('div');
    bar.className = 'sf-audio-bar';
    bar.innerHTML = `
      <button type="button" class="sf-audio-btn" data-kind="bgm" aria-pressed="true">🎵 BGM</button>
      <button type="button" class="sf-audio-btn" data-kind="sfx" aria-pressed="true">🔊 FX</button>`;
    parent.appendChild(bar);
    const sync = (btn) => {
      const on = btn.dataset.kind === 'bgm' ? getBgmEnabled() : getSfxEnabled();
      btn.classList.toggle('off', !on);
      btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    };
    bar.querySelectorAll('.sf-audio-btn').forEach((btn) => {
      sync(btn);
      btn.addEventListener('click', () => {
        unlock();
        if (btn.dataset.kind === 'bgm') {
          const next = !getBgmEnabled();
          global.localStorage.setItem(LS_BGM, next ? '1' : '0');
          if (next) startBgm();
          else stopBgm();
        } else {
          global.localStorage.setItem(LS_SFX, getSfxEnabled() ? '0' : '1');
        }
        sync(btn);
        bar.querySelectorAll('.sf-audio-btn').forEach(sync);
      });
    });
  }

  global.SpaceFlightAudio = {
    unlock,
    startBgm,
    startCartoonBgm,
    stopBgm,
    playShoot,
    playPew,
    playFlyBup,
    playFlyBoom,
    playShipBoom,
    playHit,
    playHurt,
    playPickup,
    mountToggle,
    getBgmEnabled,
    getSfxEnabled,
  };
})(typeof window !== 'undefined' ? window : globalThis);
