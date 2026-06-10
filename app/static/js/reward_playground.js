(function () {
  const API = '/api/v1/play/rewards';
  let skipRewardSpend = false;
  let hideWalletUi = false;

  const BANNERS = {
    green: 'linear-gradient(135deg, #064e3b, #065f46)',
    amber: 'linear-gradient(135deg, #78350f, #92400e)',
    cyan: 'linear-gradient(135deg, #0c4a6e, #075985)',
    yellow: 'linear-gradient(135deg, #713f12, #854d0e)',
    red: 'linear-gradient(135deg, #450a0a, #991b1b)',
    pink: 'linear-gradient(135deg, #500724, #831843)',
    purple: 'linear-gradient(135deg, #3b0764, #581c87)',
    lime: 'linear-gradient(135deg, #14532d, #166534)',
    slate: 'linear-gradient(135deg, #1e293b, #334155)',
    sky: 'linear-gradient(135deg, #0c4a6e, #0369a1)',
    rose: 'linear-gradient(135deg, #4c0519, #881337)',
    stone: 'linear-gradient(135deg, #292524, #44403c)',
    indigo: 'linear-gradient(135deg, #1e1b4b, #312e81)',
    orange: 'linear-gradient(135deg, #7c2d12, #c2410c)',
    violet: 'linear-gradient(135deg, #2e1065, #5b21b6)',
    fuchsia: 'linear-gradient(135deg, #4a044e, #86198f)',
  };

  function shouldOnboardLily() {
    const KE = window.KidEngagement;
    if (!KE?.isFirstSessionDone()) return true;
    const p = new URLSearchParams(window.location.search);
    return p.get('onboard') === '1';
  }

  function renderMetrics(m, wallet, testAll) {
    const el = document.getElementById('rp-metrics');
    if (!el) return;
    if (hideWalletUi) {
      el.textContent = 'Chào bé! Chọn game để chơi nhé 🎮';
      return;
    }
    if (testAll) {
      el.textContent = 'Test mode — all games unlocked';
      return;
    }
    if (skipRewardSpend) {
      el.textContent = 'Chơi miễn phí — tận hưởng sân chơi!';
      return;
    }
    const bal = wallet ? ` · ${wallet.available_balance} coins to spend` : '';
    if (!m) {
      el.textContent = `Sign in to track progress${bal}`;
      return;
    }
    const mastery = m.skills_mastered_count ?? 0;
    const avg = Math.round((m.avg_mastery_score ?? 0) * 100);
    el.textContent =
      `${mastery} mastery skills · ${avg}% avg · ${m.english_themes_done || 0} EN themes` +
      ` · ${m.math_sessions_3star || 0} Math ★★★${bal}`;
  }

  function statusBadge(g) {
    if (g.rollout_status === 'draft') {
      return '<span class="card-badge rp-badge-draft">Draft</span>';
    }
    if (g.rollout_status === 'beta') {
      return '<span class="card-badge rp-badge-beta">Beta</span>';
    }
    return '';
  }

  function playLabel(g) {
    if (!g.unlocked) return 'Locked';
    if (skipRewardSpend || hideWalletUi) return 'Chơi ngay';
    return `Play (${g.play_cost || 0} coins)`;
  }

  function cardHtml(g) {
    const banner = BANNERS[g.color] || BANNERS.cyan;
    const lock = g.unlocked
      ? '<span class="card-badge rp-badge-open">Open</span>'
      : '<span class="card-badge rp-badge-locked">Locked</span>';
    const coOp = g.co_op_parent
      ? '<span class="card-badge rp-badge-coop">With parents</span>'
      : '';
    const body = `
      <div class="card-glow"></div>
      <div class="card-banner" style="background:${banner};">
        <span class="card-emoji">${g.emoji}</span>
        ${lock}${statusBadge(g)}${coOp}
      </div>
      <div class="card-body">
        <div class="card-title">${g.title}</div>
        <div class="card-desc">${g.desc_en}</div>
        ${g.unlocked ? '' : `<div class="rp-hint">${g.unlock_hint}</div>`}
        <div class="card-footer">
          <button type="button" class="play-btn" data-game-id="${g.id}" data-route="${g.route}"
            data-cost="${g.play_cost || 0}" ${g.unlocked ? '' : 'disabled'}>
            ${playLabel(g)}
          </button>
        </div>
      </div>`;
    return `<div class="game-card ${g.unlocked ? '' : 'is-locked'}" data-color="${g.color}" data-game-id="${g.id}">${body}</div>`;
  }

  function renderSections(sections, games, container) {
    if (!container) return;
    const byId = Object.fromEntries((games || []).map((g) => [g.id, g]));
    const html = (sections || [])
      .map((sec) => {
        const cards = (sec.game_ids || [])
          .map((id) => byId[id])
          .filter(Boolean)
          .map(cardHtml)
          .join('');
        if (!cards) return '';
        return `
          <section class="rp-section" data-section="${sec.key}">
            <h2 class="rp-section-title">${sec.title_en}</h2>
            <div class="rp-grid">${cards}</div>
          </section>`;
      })
      .join('');
    container.innerHTML =
      html ||
      `<div class="rp-grid">${(games || []).map(cardHtml).join('')}</div>`;
  }

  function renderStarterHub(games, container, starterIds) {
    const byId = Object.fromEntries((games || []).map((g) => [g.id, g]));
    const starters = (starterIds || []).map((id) => byId[id]).filter(Boolean);
    const lilyCard = `
      <a href="/game/english-shooter/lily?onboard=1" class="rp-feature-card">
        <span class="rp-feature-icon">🧚</span>
        <h2>Lily — Tiệm Bánh</h2>
        <p>Hôm nay học: đồ ăn ngon</p>
        <span class="rp-feature-cta">▶ Chơi ngay</span>
        <span class="rp-feature-free">Miễn phí · không cần xu</span>
      </a>`;
    const arcade = starters.map(cardHtml).join('');
    container.innerHTML = `
      <section class="rp-onboard">
        ${lilyCard}
        <h3 class="rp-section-title">Thử thêm arcade</h3>
        <div class="rp-grid">${arcade}</div>
      </section>`;
  }

  async function spendAndPlay(gameId, route, cost) {
    if (skipRewardSpend || hideWalletUi) {
      window.location.href = route;
      return;
    }
    const res = await fetch('/api/v1/play/wallet/spend-reward-play', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reward_game_id: gameId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert(err.detail || `Need ${cost} coins`);
      return;
    }
    window.location.href = route;
  }

  function bindPlayButtons(root) {
    root.querySelectorAll('.play-btn:not([disabled])').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        spendAndPlay(btn.dataset.gameId, btn.dataset.route, Number(btn.dataset.cost || 0));
      });
    });
  }

  async function init() {
    if (shouldOnboardLily() && !window.location.search.includes('skip_onboard')) {
      window.location.replace('/game/english-shooter/lily?onboard=1');
      return;
    }

    const main = document.getElementById('rp-main');
    const status = document.getElementById('rp-status');
    const hero = document.querySelector('.rp-hero');
    try {
      const res = await fetch(API, { credentials: 'include' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      skipRewardSpend = Boolean(data.skip_reward_spend);
      hideWalletUi = Boolean(data.onboarding?.hide_wallet_ui)
        || !window.KidEngagement?.isFirstSessionDone();
      if (hideWalletUi && hero) hero.classList.add('rp-hero-onboard');
      renderMetrics(data.metrics, data.wallet, data.test_unlock_all);
      if (status) {
        if (hideWalletUi) {
          status.textContent = 'Sân chơi đã mở — chơi thử nhé!';
        } else if (data.wallet) {
          status.textContent = `${data.unlocked_count}/${data.total_count} open · Balance ${data.wallet.available_balance}`;
        } else {
          status.textContent = `${data.unlocked_count}/${data.total_count} games open`;
        }
      }
      if (main) {
        if (hideWalletUi && data.onboarding?.starter_game_ids?.length) {
          renderStarterHub(data.games, main, data.onboarding.starter_game_ids);
        } else {
          renderSections(data.sections, data.games, main);
        }
        bindPlayButtons(main);
      }
    } catch (e) {
      if (status) status.textContent = 'Could not load rewards';
      console.error(e);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
