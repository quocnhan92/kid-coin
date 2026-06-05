/**
 * Math Blast v2 — Play API client (/api/v1/play)
 */
(function () {
  const PLAY_API = '/api/v1/play';
  const USER_API = '/api/v1/users/me';

  const GAME_ID = 'math_blast';
  /** Tên hiển thị chế độ (API id giữ nguyên math_blast:flappy) */
  const MODE_LABELS = {
    candy: 'Bản đồ Kẹo',
    flappy: 'Gà Toán',
    arcade: 'Giải trí',
  };

  const MODES = {
    candy: 'math_blast:candy',
    flappy: 'math_blast:flappy',
    arcade: 'math_blast:arcade_free',
    arcadeClass: 'math_blast:arcade_class',
  };

  function resolveGameId(override) {
    if (override) return override;
    return window.MathBlastV2?.GAME_ID || GAME_ID;
  }

  let _bootstrapCache = {};
  let _userMe = null;

  function uuid() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }

  function toast(msg, duration = 2200) {
    let el = document.getElementById('mb-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'mb-toast';
      el.className = 'mb-toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), duration);
  }

  function setActiveSkuNav(sku) {
    document.querySelectorAll('.mb-sku-tab').forEach((tab) => {
      tab.classList.toggle('active', tab.dataset.sku === sku);
    });
  }

  function formatApiDetail(detail) {
    if (!detail) return '';
    if (typeof detail === 'string') {
      if (detail.includes('dictionary or object to extract fields')) {
        return 'Lỗi gửi dữ liệu lên server — hãy tải lại trang (Ctrl+Shift+R)';
      }
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (typeof item === 'string') return item;
          if (item && item.msg) {
            if (item.msg.includes('dictionary or object to extract fields')) {
              return 'Dữ liệu phiên không đúng định dạng';
            }
            return item.msg;
          }
          return JSON.stringify(item);
        })
        .join('; ');
    }
    return JSON.stringify(detail);
  }

  const AUTH_ERROR = 'SESSION_AUTH_REQUIRED';

  function isAuthError(err) {
    if (!err) return false;
    return err.message === AUTH_ERROR || err.message === 'Unauthorized';
  }

  function handleApiAuthError(status, detail) {
    if (status === 401) {
      clearBootstrapCache();
      if (window.GameAuth && window.GameAuth.openSessionExpired) {
        window.GameAuth.openSessionExpired();
      } else if (window.GameAuth) {
        window.GameAuth.open();
      }
      throw new Error(AUTH_ERROR);
    }
    if (status === 403) {
      clearBootstrapCache();
      const msg =
        formatApiDetail(detail) ||
        'Hãy chọn tài khoản bé trên màn hình đăng nhập để bắt đầu chơi';
      if (window.GameAuth) window.GameAuth.open();
      throw new Error(AUTH_ERROR);
    }
    if (status === 404) {
      toast(
        window.ENGLISH_MATH
          ? 'Cannot reach server — restart the app'
          : 'Không kết nối được máy chủ — hãy khởi động lại ứng dụng'
      );
      throw new Error('Not Found');
    }
  }

  function clearBootstrapCache() {
    _bootstrapCache = {};
    _userMe = null;
  }

  async function fetchJson(url, options = {}) {
    const { headers: optHeaders, ...rest } = options;
    const res = await fetch(url, {
      credentials: 'include',
      ...rest,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        ...(optHeaders || {}),
      },
    });
    if (res.status === 401 || res.status === 403 || res.status === 404) {
      const err = await res.json().catch(() => ({}));
      handleApiAuthError(res.status, err.detail);
    }
    if (res.status === 304) return { _notModified: true };
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const msg = formatApiDetail(err.detail) || `HTTP ${res.status}`;
      throw new Error(msg);
    }
    if (res.status === 204) return null;
    return res.json();
  }

  async function loadUserMe() {
    if (_userMe) return _userMe;
    _userMe = await fetchJson(USER_API);
    return _userMe;
  }

  function englishProfileExtra(extra) {
    if (!extra || !(window.isEnglishMath && window.isEnglishMath())) return extra;
    return extra
      .replace(/Lớp (\d)/g, 'Grade $1')
      .replace(/Kỷ lục/g, 'Best')
      .replace(/điểm/g, 'pts')
      .replace(/ngày liên tiếp/g, 'day streak');
  }

  async function updateProfileBar(extra) {
    const label = document.getElementById('mb-profile-label');
    if (!label) return;
    const extraEn = englishProfileExtra(extra);
    try {
      const me = await loadUserMe();
      let text = me.display_name || (window.isEnglishMath && window.isEnglishMath() ? 'Player' : 'Bé');
      if (extraEn) text += ` · ${extraEn}`;
      else if (me.current_coin != null) text += ` · ${me.current_coin}🪙`;
      label.textContent = text;
    } catch (e) {
      label.textContent = extraEn || (window.isEnglishMath && window.isEnglishMath() ? 'Sign in to play' : 'Đăng nhập để chơi');
    }
  }

  async function getGames() {
    return fetchJson(`${PLAY_API}/games`);
  }

  async function getLevels(gameModeId) {
    return fetchJson(`${PLAY_API}/levels?game_mode_id=${encodeURIComponent(gameModeId)}`);
  }

  async function getBootstrap(gameModeId, gameId) {
    const gid = resolveGameId(gameId);
    const key = `${gid}:${gameModeId || ''}`;
    const headers = {};
    const cached = _bootstrapCache[key];
    if (cached && cached.etag) headers['If-None-Match'] = cached.etag;

    const res = await fetch(
      `${PLAY_API}/bootstrap?game_id=${encodeURIComponent(gid)}&game_mode_id=${encodeURIComponent(gameModeId || '')}`,
      { credentials: 'include', headers }
    );
    if (res.status === 401 || res.status === 403 || res.status === 404) {
      const err = await res.json().catch(() => ({}));
      handleApiAuthError(res.status, err.detail);
    }
    if (res.status === 304 && cached) return cached.data;
    if (!res.ok) throw new Error(`bootstrap ${res.status}`);
    const data = await res.json();
    const etag = res.headers.get('ETag');
    _bootstrapCache[key] = { data, etag };
    return data;
  }

  function cleanSessionOp(op) {
    if (!op || typeof op !== 'object' || Array.isArray(op)) {
      throw new Error('Dữ liệu phiên không hợp lệ');
    }
    const out = {};
    Object.keys(op).forEach((key) => {
      const val = op[key];
      if (val !== undefined && val !== null) out[key] = val;
    });
    if (!out.op) throw new Error('Thiếu loại phiên (start/end)');
    return out;
  }

  function flattenSessionOps(sessions) {
    let list = Array.isArray(sessions) ? sessions : [sessions];
    if (list.length === 1 && Array.isArray(list[0])) {
      list = list[0];
    }
    return list;
  }

  async function sessionsBatch(sessions, idempotencyKey) {
    const list = flattenSessionOps(sessions);
    const payload = list.filter(Boolean).map(cleanSessionOp);
    if (!payload.length) {
      throw new Error('Thiếu dữ liệu phiên chơi (sessions)');
    }
    const headers = {};
    if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;
    return fetchJson(`${PLAY_API}/sessions/batch`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ sessions: payload }),
    });
  }

  async function eventsBatch(sessionId, events) {
    return fetchJson(`${PLAY_API}/events/batch`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, events }),
    });
  }

  function progressMap(bootstrap) {
    const map = {};
    (bootstrap.level_progress || []).forEach((p) => {
      map[p.level_id] = p;
    });
    return map;
  }

  function mergeCandyLevels(catalogLevels, bootstrap) {
    const prog = progressMap(bootstrap);
    let currentSet = false;
    return catalogLevels.map((lv) => {
      const p = prog[lv.id];
      const stars = p ? p.stars : 0;
      const unlocked = p ? p.is_unlocked : lv.id === 'L001';
      const locked = !unlocked;
      const current = !locked && !currentSet && stars < 3;
      if (current) currentSet = true;
      return {
        id: lv.id,
        title: lv.title,
        sub: lv.is_boss ? 'Thử thách cuối chương' : '3 sao để mở màn tiếp',
        locked,
        current,
        stars,
        boss: lv.is_boss,
        icon: lv.is_boss ? '👑' : locked ? '🔒' : '⭐',
      };
    });
  }

  window.MathBlastV2 = {
    PLAY_API,
    GAME_ID,
    resolveGameId,
    MODES,
    MODE_LABELS,
    AUTH_ERROR,
    uuid,
    toast,
    setActiveSkuNav,
    fetchJson,
    formatApiDetail,
    isAuthError,
    clearBootstrapCache,
    loadUserMe,
    updateProfileBar,
    getGames,
    getLevels,
    getBootstrap,
    sessionsBatch,
    eventsBatch,
    progressMap,
    mergeCandyLevels,
  };
})();
