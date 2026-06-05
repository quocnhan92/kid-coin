(function (global) {
  if (!global.ENGLISH_MATH || !global.EnglishMathSpeech) return;
  global.EnglishMathDisplay = {
    questionDisplayEn: (item) => global.EnglishMathSpeech.displayFromItem(item),
  };
})();
