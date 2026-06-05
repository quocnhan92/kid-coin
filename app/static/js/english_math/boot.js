(function (global) {
  if (global.em && global.isEnglishMath) {
    global.ENGLISH_MATH = true;
  } else {
    global.ENGLISH_MATH = true;
    global.isEnglishMath = function () {
      return true;
    };
  }

  function warmup() {
    if (global.GameUtils && global.GameUtils.warmupSpeech) {
      global.GameUtils.warmupSpeech();
    } else if (global.speechSynthesis) {
      global.speechSynthesis.getVoices();
    }
  }

  document.addEventListener('pointerdown', warmup, { once: true, capture: true });
  document.addEventListener('keydown', warmup, { once: true, capture: true });
})();
