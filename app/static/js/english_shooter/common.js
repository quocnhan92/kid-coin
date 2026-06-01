/**
 * English Shooter — Play API client
 */
(function () {
  const PLAY_API = '/api/v1/play';
  const USER_API = '/api/v1/users/me';
  const GAME_ID = 'english_shooter';
  const MODES = {
    prairie: 'english_shooter:prairie',
    city: 'english_shooter:city',
    boss: 'english_shooter:boss',
  };

  let _bootstrapCache = {};

  function uuid() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function toast(msg, duration = 2200) {
    let el = document.getElementById('es-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'es-toast';
      el.className = 'es-toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), duration);
  }

  function clearBootstrapCache() {
    _bootstrapCache = {};
  }

  const AUTH_ERROR = 'SESSION_AUTH_REQUIRED';

  function handleApiAuthError(status) {
    if (status === 401 || status === 403) {
      clearBootstrapCache();
      if (window.GameAuth) window.GameAuth.open();
      throw new Error(AUTH_ERROR);
    }
  }

  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      credentials: 'include',
      ...options,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    if (res.status === 401 || res.status === 403) {
      handleApiAuthError(res.status);
    }
    if (res.status === 304) return { _notModified: true };
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  async function getBootstrap(gameModeId) {
    const key = `${GAME_ID}:${gameModeId || ''}`;
    const headers = {};
    const cached = _bootstrapCache[key];
    if (cached && cached.etag) headers['If-None-Match'] = cached.etag;

    const res = await fetch(
      `${PLAY_API}/bootstrap?game_id=${encodeURIComponent(GAME_ID)}&game_mode_id=${encodeURIComponent(gameModeId || '')}`,
      { credentials: 'include', headers }
    );
    if (res.status === 401 || res.status === 403) handleApiAuthError(res.status);
    if (res.status === 304 && cached) return cached.data;
    if (!res.ok) throw new Error(`bootstrap ${res.status}`);
    const data = await res.json();
    _bootstrapCache[key] = { data, etag: res.headers.get('ETag') };
    return data;
  }

  async function getStage(themeId, stageType) {
    return fetchJson(
      `${PLAY_API}/english/themes/${encodeURIComponent(themeId)}/stages/${encodeURIComponent(stageType)}`
    );
  }

  async function sessionsBatch(sessions) {
    return fetchJson(`${PLAY_API}/sessions/batch`, {
      method: 'POST',
      body: JSON.stringify({ sessions }),
    });
  }

  async function eventsBatch(sessionId, events) {
    return fetchJson(`${PLAY_API}/events/batch`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, events }),
    });
  }

  async function updateProfileBar(extra) {
    const label = document.getElementById('es-profile-label');
    if (!label) return;
    try {
      const me = await fetchJson(USER_API);
      let text = me.display_name || 'Bé';
      if (extra) text += ` · ${extra}`;
      label.textContent = text;
    } catch {
      label.textContent = extra || 'Đăng nhập để chơi';
    }
  }

  window.EnglishShooter = {
    GAME_ID,
    MODES,
    uuid,
    toast,
    getBootstrap,
    getStage,
    sessionsBatch,
    eventsBatch,
    updateProfileBar,
    clearBootstrapCache,
  };
})();
