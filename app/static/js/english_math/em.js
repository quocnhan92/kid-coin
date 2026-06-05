/** English Math pages — always English UI + separate play API game id. */
(function (g) {
  const isEmPage = () =>
    document.body?.classList.contains('em-math') ||
    /\/english-shooter\/math\b/.test(g.location?.pathname || '');

  g.isEnglishMath = () => isEmPage();
  g.ENGLISH_MATH = isEmPage();
  if (g.MathBlastT) g.MathBlastT = (en) => en;
})(window);
