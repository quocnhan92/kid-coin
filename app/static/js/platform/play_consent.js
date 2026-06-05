(function (global) {
  let cached = null;

  async function fetchMicStatus() {
    if (cached) return cached;
    try {
      const res = await fetch('/api/v1/play/consent/mic', { credentials: 'include' });
      if (!res.ok) return { required: true, granted: false, policy_url: '/privacy-play' };
      cached = await res.json();
      return cached;
    } catch (_) {
      return { required: true, granted: false, policy_url: '/privacy-play' };
    }
  }

  function showConsentModal(status) {
    return new Promise((resolve) => {
      const wrap = document.createElement('div');
      wrap.className = 'play-consent-overlay';
      wrap.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.7);display:flex;align-items:center;justify-content:center;z-index:9999;padding:16px;';
      wrap.innerHTML = `
        <div class="play-consent-box" style="background:#1e1b4b;border-radius:16px;padding:24px;max-width:400px;color:#fff;">
          <h3>🎤 Cần đồng ý phụ huynh</h3>
          <p>Bé cần mic để trả lời bằng giọng nói. Phụ huynh vui lòng đọc
            <a href="${status.policy_url || '/privacy-play'}" target="_blank" rel="noopener">chính sách quyền riêng tư</a>
            và đồng ý trên tài khoản phụ huynh.</p>
          <p class="play-consent-hint">Đăng nhập phụ huynh → bấm «Đồng ý mic» trên dashboard hoặc tại đây.</p>
          <div class="play-consent-actions">
            <button type="button" class="play-consent-cancel">Để sau</button>
            <button type="button" class="play-consent-grant">Phụ huynh đồng ý</button>
          </div>
        </div>`;
      document.body.appendChild(wrap);
      wrap.querySelector('.play-consent-cancel').onclick = () => {
        wrap.remove();
        resolve(false);
      };
      wrap.querySelector('.play-consent-grant').onclick = async () => {
        try {
          const res = await fetch('/api/v1/play/consent/mic', {
            method: 'POST',
            credentials: 'include',
          });
          if (res.ok) {
            cached = await res.json();
            wrap.remove();
            resolve(true);
            return;
          }
        } catch (_) {}
        alert('Cần đăng nhập phụ huynh để đồng ý mic.');
      };
    });
  }

  async function ensureMicConsent() {
    const st = await fetchMicStatus();
    if (!st.required || st.granted) return true;
    return showConsentModal(st);
  }

  global.PlayConsent = { ensureMicConsent, fetchMicStatus };
})(window);
