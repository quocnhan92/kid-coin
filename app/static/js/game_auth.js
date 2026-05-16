/**
 * Game Auth — đăng ký / đăng nhập Kid Coin + Play API trên trang game
 */
(function () {
  const AUTH_API = '/api/v1/auth';
  const USER_API = '/api/v1/users/me';

  let deviceId = '';
  let currentUser = null;
  let members = [];
  let parentForPin = null;
  let pinInput = '';
  let _readyPromise = null;
  let _requireKid = true;
  let _authRequired = false;
  let _pendingRestore = false;
  const DEFAULT_TITLE = 'Chơi mà học — một tài khoản cho mọi game';

  function getDeviceId() {
    let id = localStorage.getItem('kidcoin_device_id');
    if (!id) {
      id = crypto.randomUUID ? crypto.randomUUID() : 'dev-' + Date.now();
      localStorage.setItem('kidcoin_device_id', id);
    }
    return id;
  }

  function $(id) {
    return document.getElementById(id);
  }

  function showOverlay(show) {
    const el = $('game-auth-overlay');
    if (!el) return;
    el.classList.toggle('hidden', !show);
    el.classList.toggle('ga-auth-required', show && _authRequired);
  }

  function setSessionExpiredUi(active) {
    const banner = $('ga-session-expired');
    const title = $('ga-title');
    const sub = $('ga-sub-default');
    if (banner) banner.classList.toggle('hidden', !active);
    if (title) title.textContent = active ? 'Đăng nhập lại để tiếp tục' : DEFAULT_TITLE;
    if (sub) {
      sub.style.display = active ? 'none' : '';
    }
  }

  function finishKidLogin(user) {
    const shouldRestore = _pendingRestore;
    _authRequired = false;
    _pendingRestore = false;
    setSessionExpiredUi(false);
    setNavButton();
    showOverlay(false);
    window.dispatchEvent(new CustomEvent('gameAuthReady', { detail: user }));
    if (shouldRestore) {
      window.dispatchEvent(new CustomEvent('gameAuthRestored', { detail: user }));
    }
  }

  function showView(viewId) {
    ['ga-view-loading', 'ga-view-device', 'ga-view-pick', 'ga-view-add-kid', 'ga-view-parent-pin'].forEach(
      (id) => {
        const v = $(id);
        if (v) {
          v.classList.remove('active');
          v.style.display = 'none';
        }
      }
    );
    const target = $(viewId);
    if (target) {
      target.classList.add('active');
      target.style.display = 'block';
    }
  }

  function setNavButton() {
    const btn = $('ga-nav-btn');
    if (!btn) return;
    if (currentUser && currentUser.role === 'KID') {
      btn.textContent = `🧒 ${currentUser.display_name}`;
      btn.classList.add('logged-in');
    } else {
      btn.textContent = 'Đăng nhập / Đăng ký';
      btn.classList.remove('logged-in');
    }
  }

  async function fetchAuth(url, options = {}) {
    const res = await fetch(url, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-ID': deviceId,
        ...(options.headers || {}),
      },
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = data.detail;
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail) || `HTTP ${res.status}`);
    }
    return data;
  }

  function normalizeRole(role) {
    if (!role) return '';
    if (typeof role === 'string') return role;
    return role.value || String(role);
  }

  async function checkSession() {
    try {
      const res = await fetch(USER_API, { credentials: 'include' });
      if (!res.ok) return null;
      const data = await res.json();
      data.role = normalizeRole(data.role);
      return data;
    } catch {
      return null;
    }
  }

  async function checkDevice() {
    return fetchAuth(`${AUTH_API}/device-status`, { method: 'GET' });
  }

  function renderMembers(familyName, list) {
    members = list || [];
    const nameEl = $('ga-family-name');
    if (nameEl) nameEl.textContent = familyName || '';
    const grid = $('ga-user-grid');
    if (!grid) return;
    const sorted = [...members].sort((a, b) => (a.role === 'PARENT' ? -1 : 1));
    grid.innerHTML = sorted
      .map(
        (u) => `
      <div class="ga-user-card" data-user-id="${u.id}" data-role="${u.role}">
        <img src="${u.avatar_url || ''}" alt="" />
        <span>${u.display_name}</span>
        <span class="ga-role">${u.role === 'PARENT' ? 'Bố/Mẹ' : 'Bé'}</span>
      </div>`
      )
      .join('');
    grid.querySelectorAll('.ga-user-card').forEach((card) => {
      card.addEventListener('click', () => {
        const user = members.find((m) => m.id === card.dataset.userId);
        if (user) onPickUser(user);
      });
    });
  }

  async function onPickUser(user) {
    if (user.role === 'PARENT') {
      parentForPin = user;
      pinInput = '';
      const av = $('ga-pin-avatar');
      if (av) av.src = user.avatar_url || '';
      updatePinDots();
      showView('ga-view-parent-pin');
      return;
    }
    await performQuickLogin(user.id);
  }

  function updatePinDots() {
    const row = $('ga-pin-dots');
    if (!row) return;
    row.innerHTML = [0, 1, 2, 3]
      .map((i) => `<span class="ga-pin-dot ${i < pinInput.length ? 'filled' : ''}"></span>`)
      .join('');
  }

  function buildNumpad() {
    const pad = $('ga-numpad');
    if (!pad || pad.dataset.built) return;
    pad.dataset.built = '1';
    const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'Xóa', '0', '←'];
    pad.innerHTML = keys
      .map((k) => `<button type="button" data-key="${k}">${k}</button>`)
      .join('');
    pad.addEventListener('click', (e) => {
      const btn = e.target.closest('button');
      if (!btn) return;
      const key = btn.dataset.key;
      if (key === 'Xóa') pinInput = '';
      else if (key === '←') pinInput = pinInput.slice(0, -1);
      else if (pinInput.length < 4) pinInput += key;
      updatePinDots();
      if (pinInput.length === 4 && parentForPin) {
        performQuickLogin(parentForPin.id, pinInput);
      }
    });
  }

  async function performQuickLogin(userId, pin = null) {
    const errEl = $('ga-pick-error');
    if (errEl) errEl.textContent = '';
    try {
      const stay = window.location.pathname + window.location.search;
      const data = await fetchAuth(`${AUTH_API}/quick-login`, {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          device_id: deviceId,
          pin,
          redirect_url: _requireKid ? stay : undefined,
        }),
      });
      currentUser = await checkSession();
      setNavButton();
      if (currentUser && currentUser.role === 'KID') {
        finishKidLogin(currentUser);
        if (!_requireKid && data.redirect_url) {
          window.location.href = data.redirect_url;
        }
      } else if (currentUser && currentUser.role === 'PARENT') {
        window.location.href = data.redirect_url || '/parent';
      }
    } catch (e) {
      if (errEl) errEl.textContent = e.message;
      pinInput = '';
      updatePinDots();
    }
  }

  async function bootstrap() {
    showOverlay(true);
    showView('ga-view-loading');
    deviceId = getDeviceId();
    buildNumpad();

    currentUser = await checkSession();
    if (currentUser && currentUser.role === 'PARENT' && _requireKid) {
      setNavButton();
      try {
        const device = await checkDevice();
        if (device.is_registered) {
          renderMembers(device.family_name, device.members);
          showView('ga-view-pick');
        } else {
          showView('ga-view-device');
        }
      } catch {
        showView('ga-view-device');
      }
      return null;
    }
    if (currentUser && (!_requireKid || currentUser.role === 'KID')) {
      finishKidLogin(currentUser);
      return currentUser;
    }

    try {
      const device = await checkDevice();
      if (device.is_registered) {
        renderMembers(device.family_name, device.members);
        showView('ga-view-pick');
      } else {
        showView('ga-view-device');
        setupDeviceTabs('login');
      }
    } catch (e) {
      showView('ga-view-device');
      const err = $('ga-device-error');
      if (err) err.textContent = e.message;
    }
    setNavButton();
    return null;
  }

  function setupDeviceTabs(mode) {
    document.querySelectorAll('.ga-tab').forEach((tab) => {
      tab.classList.toggle('active', tab.dataset.gaTab === mode);
    });
    document.querySelectorAll('#ga-view-device [data-ga-panel]').forEach((panel) => {
      const active = panel.dataset.gaPanel === mode;
      panel.classList.toggle('active', active);
      panel.style.display = active ? 'block' : 'none';
    });
  }

  function bindEvents() {
    document.querySelectorAll('.ga-tab').forEach((tab) => {
      tab.addEventListener('click', () => setupDeviceTabs(tab.dataset.gaTab));
    });

    $('ga-form-login')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const err = $('ga-device-error');
      if (err) err.textContent = '';
      try {
        const data = await fetchAuth(`${AUTH_API}/register-device`, {
          method: 'POST',
          body: JSON.stringify({
            username: $('ga-login-username').value.trim(),
            password: $('ga-login-pin').value,
            device_id: deviceId,
            device_name: navigator.platform + ' Browser',
          }),
        });
        renderMembers(data.family_name, data.members);
        showView('ga-view-pick');
      } catch (ex) {
        if (err) err.textContent = ex.message;
      }
    });

    $('ga-form-register')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const err = $('ga-device-error');
      if (err) err.textContent = '';
      try {
        const data = await fetchAuth(`${AUTH_API}/register-family`, {
          method: 'POST',
          body: JSON.stringify({
            family_name: $('ga-reg-family').value.trim(),
            admin_display_name: $('ga-reg-parent').value.trim(),
            admin_username: $('ga-reg-username').value.trim(),
            admin_password: $('ga-reg-pin').value,
            device_id: deviceId,
            device_name: navigator.platform + ' Browser',
          }),
        });
        renderMembers(data.family_name, data.members);
        showView('ga-view-pick');
      } catch (ex) {
        if (err) err.textContent = ex.message;
      }
    });

    $('ga-show-add-kid')?.addEventListener('click', () => showView('ga-view-add-kid'));
    $('ga-back-pick')?.addEventListener('click', () => showView('ga-view-pick'));
    $('ga-pin-back')?.addEventListener('click', () => {
      pinInput = '';
      showView('ga-view-pick');
    });

    $('ga-form-add-kid')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const err = $('ga-kid-error');
      if (err) err.textContent = '';
      try {
        const kid = await fetchAuth(`${AUTH_API}/register-kid`, {
          method: 'POST',
          body: JSON.stringify({
            device_id: deviceId,
            parent_pin: $('ga-kid-pin').value,
            display_name: $('ga-kid-name').value.trim(),
          }),
        });
        members.push(kid);
        await performQuickLogin(kid.id);
      } catch (ex) {
        if (err) err.textContent = ex.message;
      }
    });

    $('ga-close-btn')?.addEventListener('click', () => {
      if (_authRequired) return;
      showOverlay(false);
    });
    $('ga-nav-btn')?.addEventListener('click', () => {
      if (currentUser && currentUser.role === 'KID') {
        if (confirm('Đăng xuất?')) logout();
      } else {
        open();
      }
    });
  }

  async function logout() {
    await fetch(`${AUTH_API}/logout`, { method: 'POST', credentials: 'include' });
    currentUser = null;
    if (window.MathBlastV2 && window.MathBlastV2.clearBootstrapCache) {
      window.MathBlastV2.clearBootstrapCache();
    }
    setNavButton();
    open();
  }

  function open() {
    _authRequired = false;
    setSessionExpiredUi(false);
    showOverlay(true);
    bootstrap();
  }

  function openSessionExpired() {
    _authRequired = true;
    _pendingRestore = true;
    _readyPromise = null;
    currentUser = null;
    if (window.MathBlastV2 && window.MathBlastV2.clearBootstrapCache) {
      window.MathBlastV2.clearBootstrapCache();
    }
    setSessionExpiredUi(true);
    showOverlay(true);
    bootstrap();
  }

  function ready() {
    if (!_readyPromise) {
      _readyPromise = new Promise((resolve) => {
        const done = (user) => {
          resolve(user);
        };
        if (currentUser && (!_requireKid || currentUser.role === 'KID')) {
          done(currentUser);
          return;
        }
        window.addEventListener('gameAuthReady', (ev) => done(ev.detail), { once: true });
        bootstrap().then((u) => {
          if (u) done(u);
        });
      });
    }
    return _readyPromise;
  }

  window.GameAuth = {
    ready,
    open,
    openSessionExpired,
    logout,
    getUser: () => currentUser,
    isAuthRequired: () => _authRequired,
    requireKid: (v) => {
      _requireKid = v !== false;
    },
  };

  document.addEventListener('DOMContentLoaded', () => {
    bindEvents();
    deviceId = getDeviceId();
    bootstrap();
  });
})();
