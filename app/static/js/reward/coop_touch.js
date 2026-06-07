(function (global) {
  function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  }

  function canvasPoint(canvas, clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    return {
      x: (clientX - r.left) * (canvas.width / r.width),
      y: (clientY - r.top) * (canvas.height / r.height),
      left: clientX - r.left < r.width / 2,
    };
  }

  function bindTouchDrag(el, onRatio) {
    const knob = el.querySelector('.rg-coop-knob');
    const handle = (clientY) => {
      const r = el.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (clientY - r.top) / r.height));
      onRatio(ratio);
      if (knob) knob.style.top = `${ratio * 100}%`;
    };
    el.addEventListener(
      'touchstart',
      (e) => {
        e.preventDefault();
        handle(e.changedTouches[0].clientY);
      },
      { passive: false }
    );
    el.addEventListener(
      'touchmove',
      (e) => {
        e.preventDefault();
        handle(e.changedTouches[0].clientY);
      },
      { passive: false }
    );
    el.addEventListener('mousedown', (e) => {
      handle(e.clientY);
      const onMove = (ev) => handle(ev.clientY);
      const onUp = () => {
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
      };
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    });
  }

  function bindCanvasSplit(canvas, onLeft, onRight) {
    const handle = (e) => {
      e.preventDefault();
      const list = e.touches || [e];
      for (let i = 0; i < list.length; i += 1) {
        const t = list[i];
        const p = canvasPoint(canvas, t.clientX, t.clientY);
        if (p.left) onLeft(p.x, p.y);
        else onRight(p.x, p.y);
      }
    };
    canvas.addEventListener('touchstart', handle, { passive: false });
    canvas.addEventListener('touchmove', handle, { passive: false });
  }

  function bindDualDpad(root, onP1, onP2) {
    if (!root) return;
    const dirs = {
      up: [0, -1],
      down: [0, 1],
      left: [-1, 0],
      right: [1, 0],
    };
    root.querySelectorAll('[data-player][data-dir]').forEach((btn) => {
      const fire = (e) => {
        e.preventDefault();
        const [dx, dy] = dirs[btn.dataset.dir] || [0, 0];
        if (btn.dataset.player === '1') onP1(dx, dy);
        else onP2(dx, dy);
      };
      btn.addEventListener('touchstart', fire, { passive: false });
      btn.addEventListener('click', fire);
    });
  }

  function revealTouchUi() {
    document.querySelectorAll('.rg-coop-touch-ui').forEach((el) => {
      el.hidden = false;
    });
    document.querySelectorAll('.rg-coop-keys-desktop').forEach((el) => {
      el.hidden = true;
    });
    document.querySelectorAll('.rg-coop-canvas-wrap').forEach((el) => {
      el.classList.add('rg-coop-watch-only');
    });
  }

  function setupTouchUi() {
    if (!isTouchDevice()) return false;
    revealTouchUi();
    return true;
  }

  global.RewardCoopTouch = {
    isTouchDevice,
    canvasPoint,
    bindTouchDrag,
    bindCanvasSplit,
    bindDualDpad,
    setupTouchUi,
  };
})(window);
