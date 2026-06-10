(function (global) {
  const KEY = "kidcoin_engagement_v1";
  const MODE_ORDER = [
    "bakery", "family", "animals", "fruit", "classroom", "colors",
    "pets", "food", "home", "nature", "vehicles", "fashion",
  ];

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch {
      return {};
    }
  }

  function save(data) {
    localStorage.setItem(KEY, JSON.stringify(data));
  }

  function isFirstSessionDone() {
    return Boolean(load().firstSessionDone);
  }

  function markFirstSessionDone() {
    const d = load();
    d.firstSessionDone = true;
    d.firstSessionAt = Date.now();
    save(d);
  }

  function getModeStars(modeId) {
    return Number(load().modeStars?.[modeId] || 0);
  }

  function setModeStars(modeId, stars) {
    const d = load();
    d.modeStars = d.modeStars || {};
    d.modeStars[modeId] = Math.max(Number(d.modeStars[modeId] || 0), stars);
    save(d);
  }

  function isModeUnlocked(modeId) {
    const idx = MODE_ORDER.indexOf(modeId);
    if (idx <= 0) return true;
    const prev = MODE_ORDER[idx - 1];
    return getModeStars(prev) >= 3;
  }

  function nextLockedMode() {
    return MODE_ORDER.find((id) => !isModeUnlocked(id)) || null;
  }

  global.KidEngagement = {
    MODE_ORDER,
    isFirstSessionDone,
    markFirstSessionDone,
    getModeStars,
    setModeStars,
    isModeUnlocked,
    nextLockedMode,
  };
})(typeof window !== "undefined" ? window : globalThis);
