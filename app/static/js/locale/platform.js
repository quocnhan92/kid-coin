/**
 * KidCoin client i18n — init from window.__KIDCOIN_LOCALE__ (injected by server).
 */
(function (g) {
  const cfg = g.__KIDCOIN_LOCALE__ || {};
  const messages = cfg.messages || {};

  function format(template, params) {
    if (!params) return template;
    return template.replace(/\{(\w+)\}/g, (_, k) =>
      params[k] !== undefined ? String(params[k]) : `{${k}}`
    );
  }

  function t(key, params, defaultText) {
    const raw = messages[key] ?? defaultText ?? key;
    return format(raw, params);
  }

  function isEnglishUi() {
    const loc = KidLocale.locale || '';
    return loc === 'en' || loc.startsWith('en-');
  }

  const KidLocale = {
    locale: cfg.locale || 'vi-VN',
    market: cfg.market || 'vn',
    speechLang: cfg.speechLang || 'vi-VN',
    rtl: !!cfg.rtl,
    markets: cfg.markets || [],
    locales: cfg.locales || [],
    messages,
    t,
    isEnglishUi,
    /** @deprecated use isEnglishUi — math English clone */
    isEnglishMath: () => KidLocale.market === 'en' || isEnglishUi(),
  };

  g.KidLocale = KidLocale;
  g.isEnglishMath = () => KidLocale.isEnglishMath();
  g.ENGLISH_MATH = KidLocale.isEnglishMath();

  g.MathBlastT = (en, vi) => (KidLocale.isEnglishUi() ? en : vi);
})();
