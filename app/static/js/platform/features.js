(function (global) {
  const CACHE_MS = 60 * 1000;
  let cache = { at: 0, flags: {}, apiVersion: '1' };

  async function fetchFeatures() {
    const now = Date.now();
    if (now - cache.at < CACHE_MS && Object.keys(cache.flags).length) {
      return cache;
    }
    try {
      const res = await fetch('/api/v1/system/features', { credentials: 'same-origin' });
      if (!res.ok) return cache;
      const data = await res.json();
      cache = {
        at: now,
        flags: data.flags || {},
        apiVersion: data.api_version || '1',
        minClientVersion: data.min_client_version || '1.0.0',
      };
      global.__KIDCOIN_FEATURES__ = cache.flags;
    } catch (_) {
      /* offline — keep cache */
    }
    return cache;
  }

  function isEnabled(key, defaultValue = true) {
    if (!cache.flags || !(key in cache.flags)) return defaultValue;
    return !!cache.flags[key];
  }

  async function fetchPublicGames(zone = 'learning', grade = null) {
    let url = `/api/v1/system/public-games?zone=${encodeURIComponent(zone)}`;
    if (grade != null) url += `&grade=${grade}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const data = await res.json();
    return data.games || [];
  }

  global.KidCoinPlatform = {
    fetchFeatures,
    isEnabled,
    fetchPublicGames,
    clientVersion: '1.0.0',
  };
})(window);
