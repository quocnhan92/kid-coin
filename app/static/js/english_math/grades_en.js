(function (global) {
  if (!(global.isEnglishMath && global.isEnglishMath()) || !global.MathBlastQuestionGen) return;

  const EN = {
    1: { label: 'Grade 1', subtitle: 'Count, add & subtract up to 100 (no carry)' },
    2: { label: 'Grade 2', subtitle: 'Add/subtract to 100 · times tables 2–10' },
    3: { label: 'Grade 3', subtitle: 'Multiplication tables 2–9 · division facts' },
    4: { label: 'Grade 4', subtitle: 'Same-denominator fractions · decimals' },
    5: { label: 'Grade 5', subtitle: 'Decimals · simple percent · ratios' },
  };

  Object.keys(EN).forEach((g) => {
    const meta = global.MathBlastQuestionGen.GRADES[g];
    if (meta) {
      meta.label = EN[g].label;
      meta.subtitle = EN[g].subtitle;
    }
  });
})();
