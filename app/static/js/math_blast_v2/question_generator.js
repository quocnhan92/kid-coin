/**
 * Math Blast V2 — procedural question generation per sprint session.
 * Avoids repeating the same fact (skill + operands) within one session.
 */
(function (global) {
  const TIER_SKILLS = {
    T1: [
      'l1_add_within_10',
      'l1_sub_within_10',
      'l1_add_within_20',
      'l1_sub_within_20',
      'l1_number_bonds_10',
    ],
    T2: [
      'l2_add_carry_once_100',
      'l2_sub_borrow_once_100',
      'l2_add_tables_2_5_mix',
      'l2_mul_5_10',
    ],
    T3: [
      'l3_mul_table_2',
      'l3_mul_table_3',
      'l3_mul_table_4',
      'l3_mul_table_5',
      'l3_div_table_2',
    ],
  };

  const OP_SYM = { add: '+', sub: '−', mul: '×', div: '÷' };

  function randInt(min, max) {
    return min + Math.floor(Math.random() * (max - min + 1));
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function makeChoices(answer, count, spread) {
    const choices = new Set([answer]);
    let guard = 0;
    while (choices.size < count && guard < 40) {
      guard += 1;
      const delta = randInt(1, spread);
      const sign = Math.random() < 0.5 ? -1 : 1;
      const c = answer + sign * delta;
      if (c >= 0 && c !== answer) choices.add(c);
    }
    while (choices.size < count) {
      choices.add(answer + choices.size);
    }
    return shuffle([...choices]);
  }

  function problemKey(item) {
    return `${item.skill}|${item.q}|${item.a}`;
  }

  function genAddSub(skill, maxSum) {
    const isAdd = skill.includes('_add_');
    let a = randInt(0, maxSum);
    let b = randInt(0, maxSum);
    if (!isAdd && a < b) [a, b] = [b, a];
    const answer = isAdd ? a + b : a - b;
    if (answer < 0 || (isAdd && answer > maxSum)) return null;
    const op = isAdd ? 'add' : 'sub';
    return {
      q: `${a} ${OP_SYM[op]} ${b} = ?`,
      a: answer,
      choices: makeChoices(answer, 4, Math.max(3, Math.ceil(maxSum / 4))),
      skill,
      op,
    };
  }

  function genBonds10(skill) {
    const a = randInt(1, 9);
    const b = 10 - a;
    if (Math.random() < 0.5) {
      return {
        q: `${a} + ? = 10`,
        a: b,
        choices: makeChoices(b, 4, 3),
        skill,
        op: 'add',
      };
    }
    return {
      q: `? + ${a} = 10`,
      a: b,
      choices: makeChoices(b, 4, 3),
      skill,
      op: 'add',
    };
  }

  function genMul(skill, tableMax) {
    const t = randInt(2, tableMax);
    const n = randInt(2, 9);
    const answer = t * n;
    return {
      q: `${t} ${OP_SYM.mul} ${n} = ?`,
      a: answer,
      choices: makeChoices(answer, 4, Math.max(4, Math.ceil(answer / 3))),
      skill,
      op: 'mul',
    };
  }

  function genDiv(skill, tableMax) {
    const t = randInt(2, tableMax);
    const n = randInt(2, 9);
    const product = t * n;
    return {
      q: `${product} ${OP_SYM.div} ${t} = ?`,
      a: n,
      choices: makeChoices(n, 4, 4),
      skill,
      op: 'div',
    };
  }

  function genForSkill(skill) {
    if (skill === 'l1_add_within_10') return genAddSub(skill, 10);
    if (skill === 'l1_sub_within_10') return genAddSub(skill, 10);
    if (skill === 'l1_add_within_20') return genAddSub(skill, 20);
    if (skill === 'l1_sub_within_20') return genAddSub(skill, 20);
    if (skill === 'l1_number_bonds_10') return genBonds10(skill);
    if (skill.startsWith('l2_add') || skill.startsWith('l2_sub')) return genAddSub(skill, 100);
    if (skill.includes('mul')) return genMul(skill, 10);
    if (skill.includes('div')) return genDiv(skill, 9);
    if (skill.startsWith('l3_mul')) return genMul(skill, 9);
    if (skill.startsWith('l3_div')) return genDiv(skill, 9);
    return genAddSub('l1_add_within_10', 10);
  }

  function createSession(tier, options = {}) {
    const tierKey = TIER_SKILLS[tier] ? tier : 'T1';
    const skills = options.skills || TIER_SKILLS[tierKey];
    const usedKeys = new Set();
    let skillCursor = 0;

    function pickSkill() {
      const skill = skills[skillCursor % skills.length];
      skillCursor += 1;
      return skill;
    }

    function next() {
      const maxAttempts = skills.length * 80;
      for (let i = 0; i < maxAttempts; i += 1) {
        const skill = pickSkill();
        const item = genForSkill(skill);
        if (!item) continue;
        const key = problemKey(item);
        if (usedKeys.has(key)) continue;
        usedKeys.add(key);
        return item;
      }
      usedKeys.clear();
      return next();
    }

    return { tier: tierKey, next, usedCount: () => usedKeys.size };
  }

  function resolveActiveTier(flappyBootstrap) {
    const unlocked = flappyBootstrap?.tier_unlocked;
    if (Array.isArray(unlocked) && unlocked.length) {
      return unlocked[unlocked.length - 1];
    }
    return 'T1';
  }

  global.MathBlastQuestionGen = {
    TIER_SKILLS,
    createSession,
    resolveActiveTier,
    problemKey,
  };
})(typeof window !== 'undefined' ? window : global);
