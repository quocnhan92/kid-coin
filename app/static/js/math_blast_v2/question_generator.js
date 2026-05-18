/**
 * Math Blast V2 — sinh câu hỏi theo LỚP (1–5), bám GDPT 2018 / Candy skill map.
 * Mỗi phiên không lặp cùng một phép (skill + đề + đáp án).
 */
(function (global) {
  const OP_SYM = { add: '+', sub: '−', mul: '×', div: '÷' };
  const LS_GRADE = 'mb_v2_flappy_grade';

  /** Lớp 1–5 ↔ tier API (T1…T5) */
  const GRADES = {
    1: {
      tier: 'T1',
      label: 'Lớp 1',
      subtitle: 'Đếm, cộng trừ đến 100 — không nhớ, không mượn',
      choiceCount: 3,
      skills: [
        'l1_add_no_carry_10',
        'l1_sub_no_borrow_10',
        'l1_add_no_carry_20',
        'l1_sub_no_borrow_20',
        'l1_add_no_carry_100',
        'l1_sub_no_borrow_100',
        'l1_number_bonds_10',
        'l1_compare_to_20',
      ],
    },
    2: {
      tier: 'T2',
      label: 'Lớp 2',
      subtitle: 'Cộng trừ đến 100 (có nhớ/mượn) · bảng cộng trừ · nhân 2–10',
      choiceCount: 4,
      skills: [
        'l2_add_no_carry_100',
        'l2_sub_no_borrow_100',
        'l2_add_carry_once_100',
        'l2_sub_borrow_once_100',
        'l2_add_tables_2_5_mix',
        'l2_mul_5_10',
      ],
    },
    3: {
      tier: 'T3',
      label: 'Lớp 3',
      subtitle: 'Cửu chương nhân 2–9 · chia hết trong bảng',
      choiceCount: 4,
      skills: [
        'l3_mul_table_2',
        'l3_mul_table_3',
        'l3_mul_table_4',
        'l3_mul_table_5',
        'l3_mul_table_6',
        'l3_mul_table_7',
        'l3_mul_table_8',
        'l3_mul_table_9',
        'l3_div_table_2',
        'l3_div_table_5',
        'l3_div_table_9',
      ],
    },
    4: {
      tier: 'T4',
      label: 'Lớp 4',
      subtitle: 'Phân số cùng mẫu · thập phân 1 chữ số (nhẹ)',
      choiceCount: 4,
      skills: [
        'l4_fraction_add_same_den',
        'l4_fraction_sub_same_den',
        'l4_decimal_add_1dp',
        'l4_decimal_sub_1dp',
        'l4_mul_powers_of_10',
      ],
    },
    5: {
      tier: 'T5',
      label: 'Lớp 5',
      subtitle: 'Thập phân · phần trăm chẵn · tỉ số đơn giản',
      choiceCount: 4,
      skills: [
        'l5_decimal_mul_whole',
        'l5_percent_of_number',
        'l5_ratio_intro',
        'l4_decimal_add_1dp',
      ],
    },
  };

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
    while (choices.size < count && guard < 50) {
      guard += 1;
      const delta = randInt(1, Math.max(2, spread));
      const sign = Math.random() < 0.5 ? -1 : 1;
      const c = answer + sign * delta;
      if (c >= 0 && c !== answer) choices.add(c);
    }
    while (choices.size < count) {
      choices.add(answer + choices.size);
    }
    return shuffle([...choices]).slice(0, count);
  }

  function problemKey(item) {
    return `${item.skill}|${item.q}|${item.a}`;
  }

  function pack(skill, q, a, op, choiceCount) {
    return {
      q,
      a,
      skill,
      op,
      grade: itemGrade(skill),
      choices: makeChoices(a, choiceCount, Math.max(3, Math.ceil(a / 4) + 2)),
    };
  }

  let _sessionGrade = 1;

  function itemGrade(skill) {
    const m = skill.match(/^l(\d)/);
    return m ? parseInt(m[1], 10) : _sessionGrade;
  }

  function genAddNoCarry(skill, maxSum, maxOperand) {
    const cap = maxOperand != null ? maxOperand : maxSum;
    for (let t = 0; t < 60; t += 1) {
      const a = randInt(0, Math.min(cap, maxSum));
      const b = randInt(0, Math.min(cap, maxSum - a));
      if ((a % 10) + (b % 10) >= 10) continue;
      const sum = a + b;
      if (sum > maxSum) continue;
      return pack(skill, `${a} ${OP_SYM.add} ${b} = ?`, sum, 'add', GRADES[_sessionGrade].choiceCount);
    }
    return null;
  }

  function genSubNoBorrow(skill, maxNum) {
    for (let t = 0; t < 60; t += 1) {
      let a = randInt(0, maxNum);
      let b = randInt(0, maxNum);
      if (a < b) [a, b] = [b, a];
      if ((a % 10) < (b % 10)) continue;
      return pack(skill, `${a} ${OP_SYM.sub} ${b} = ?`, a - b, 'sub', GRADES[_sessionGrade].choiceCount);
    }
    return null;
  }

  function genAddCarryOnce(skill, maxSum) {
    for (let t = 0; t < 80; t += 1) {
      const a = randInt(10, Math.min(99, maxSum - 1));
      const b = randInt(1, Math.min(99, maxSum - a));
      const ones = (a % 10) + (b % 10);
      if (ones < 10 || a + b > maxSum) continue;
      return pack(skill, `${a} ${OP_SYM.add} ${b} = ?`, a + b, 'add', GRADES[_sessionGrade].choiceCount);
    }
    return null;
  }

  function genSubBorrowOnce(skill, maxNum) {
    for (let t = 0; t < 80; t += 1) {
      const a = randInt(20, maxNum);
      const b = randInt(1, a - 1);
      if ((a % 10) >= (b % 10)) continue;
      return pack(skill, `${a} ${OP_SYM.sub} ${b} = ?`, a - b, 'sub', GRADES[_sessionGrade].choiceCount);
    }
    return null;
  }

  function genBonds10(skill) {
    const a = randInt(1, 9);
    const b = 10 - a;
    if (Math.random() < 0.5) {
      return pack(skill, `${a} + ? = 10`, b, 'add', GRADES[_sessionGrade].choiceCount);
    }
    return pack(skill, `? + ${a} = 10`, b, 'add', GRADES[_sessionGrade].choiceCount);
  }

  function genCompare(skill, maxN) {
    const a = randInt(0, maxN);
    let b = randInt(0, maxN);
    while (b === a) b = randInt(0, maxN);
    const correct = Math.max(a, b);
    return {
      q: `${a} và ${b} — số nào lớn hơn?`,
      a: correct,
      choices: makeChoices(correct, GRADES[_sessionGrade].choiceCount, 5),
      skill,
      op: 'compare',
      grade: 1,
    };
  }

  function genMulTable(skill, table) {
    const t = table || randInt(2, 9);
    const n = randInt(2, 9);
    return pack(skill, `${t} ${OP_SYM.mul} ${n} = ?`, t * n, 'mul', GRADES[_sessionGrade].choiceCount);
  }

  function genDivTable(skill, table) {
    const t = table || randInt(2, 9);
    const n = randInt(2, 9);
    const product = t * n;
    return pack(skill, `${product} ${OP_SYM.div} ${t} = ?`, n, 'div', GRADES[_sessionGrade].choiceCount);
  }

  function genMulSmall(skill) {
    const tables = [2, 5, 10];
    const t = tables[randInt(0, tables.length - 1)];
    const n = randInt(2, 9);
    return pack(skill, `${t} ${OP_SYM.mul} ${n} = ?`, t * n, 'mul', GRADES[_sessionGrade].choiceCount);
  }

  function genTableAdd(skill) {
    const base = [2, 3, 4, 5][randInt(0, 3)];
    const n = randInt(1, 9);
    return pack(skill, `${n} + ${base} = ?`, n + base, 'add', GRADES[_sessionGrade].choiceCount);
  }

  function genFractionSameDen(skill, isAdd) {
    const den = [2, 3, 4, 5, 6, 8, 10][randInt(0, 6)];
    let n1 = randInt(1, den - 1);
    let n2 = randInt(1, den - 1);
    if (!isAdd && n1 < n2) [n1, n2] = [n2, n1];
    if (isAdd && n1 + n2 > den) {
      n2 = randInt(1, den - n1);
    }
    if (!isAdd && n1 === n2) n2 = Math.max(1, n2 - 1);
    const num = isAdd ? n1 + n2 : n1 - n2;
    const op = isAdd ? OP_SYM.add : OP_SYM.sub;
    return pack(
      skill,
      `${n1}/${den} ${op} ${n2}/${den} = ?`,
      num,
      isAdd ? 'add' : 'sub',
      GRADES[_sessionGrade].choiceCount
    );
  }

  function genDecimalAddSub(skill, isAdd) {
    for (let t = 0; t < 40; t += 1) {
      const a = randInt(1, 9);
      const b = randInt(1, 9);
      const da = randInt(1, 9);
      const db = randInt(1, 9);
      const x = a + da / 10;
      const y = b + db / 10;
      let ans;
      if (isAdd) {
        if (da + db >= 10) continue;
        ans = Math.round((x + y) * 10) / 10;
      } else {
        if (x < y || da < db) continue;
        ans = Math.round((x - y) * 10) / 10;
      }
      const fmt = (v) => String(v).replace('.', ',');
      const op = isAdd ? OP_SYM.add : OP_SYM.sub;
      return {
        q: `${fmt(x)} ${op} ${fmt(y)} = ?`,
        a: ans,
        choices: makeChoices(ans, GRADES[_sessionGrade].choiceCount, 3),
        skill,
        op: isAdd ? 'add' : 'sub',
        grade: _sessionGrade,
      };
    }
    return null;
  }

  function genMulPower10(skill) {
    const n = randInt(2, 9);
    const p = [10, 100][randInt(0, 1)];
    return pack(skill, `${n} ${OP_SYM.mul} ${p} = ?`, n * p, 'mul', GRADES[_sessionGrade].choiceCount);
  }

  function genDecimalMulWhole(skill) {
    const d = randInt(1, 9);
    const n = randInt(2, 9);
    const dec = d / 10;
    const ans = Math.round(dec * n * 10) / 10;
    return {
      q: `${String(dec).replace('.', ',')} ${OP_SYM.mul} ${n} = ?`,
      a: ans,
      choices: makeChoices(ans, GRADES[_sessionGrade].choiceCount, 2),
      skill,
      op: 'mul',
      grade: 5,
    };
  }

  function genPercentOf(skill) {
    const pcts = [10, 20, 25, 50];
    const pct = pcts[randInt(0, pcts.length - 1)];
    const n = [10, 20, 40, 50, 100][randInt(0, 4)];
    const ans = (n * pct) / 100;
    return pack(skill, `${pct}% của ${n} = ?`, ans, 'mul', GRADES[_sessionGrade].choiceCount);
  }

  function genRatioIntro(skill) {
    const a = randInt(1, 4);
    const b = randInt(1, 4);
    const parts = a + b;
    const unit = randInt(2, 6);
    const total = parts * unit;
    return pack(
      skill,
      `Chia ${total} theo tỉ ${a}:${b}. Một phần bằng?`,
      unit,
      'div',
      GRADES[_sessionGrade].choiceCount
    );
  }

  function genForSkill(skill) {
    switch (skill) {
      case 'l1_add_no_carry_10':
        return genAddNoCarry(skill, 10, 9);
      case 'l1_sub_no_borrow_10':
        return genSubNoBorrow(skill, 10);
      case 'l1_add_no_carry_20':
        return genAddNoCarry(skill, 20, 19);
      case 'l1_sub_no_borrow_20':
        return genSubNoBorrow(skill, 20);
      case 'l1_add_no_carry_100':
        return genAddNoCarry(skill, 100, 99);
      case 'l1_sub_no_borrow_100':
        return genSubNoBorrow(skill, 100);
      case 'l1_number_bonds_10':
        return genBonds10(skill);
      case 'l1_compare_to_20':
        return genCompare(skill, 20);
      case 'l2_add_no_carry_100':
        return genAddNoCarry(skill, 100, 99);
      case 'l2_sub_no_borrow_100':
        return genSubNoBorrow(skill, 100);
      case 'l2_add_carry_once_100':
        return genAddCarryOnce(skill, 100);
      case 'l2_sub_borrow_once_100':
        return genSubBorrowOnce(skill, 100);
      case 'l2_add_tables_2_5_mix':
        return genTableAdd(skill);
      case 'l2_mul_5_10':
        return genMulSmall(skill);
      case 'l3_mul_table_2':
        return genMulTable(skill, 2);
      case 'l3_mul_table_3':
        return genMulTable(skill, 3);
      case 'l3_mul_table_4':
        return genMulTable(skill, 4);
      case 'l3_mul_table_5':
        return genMulTable(skill, 5);
      case 'l3_mul_table_6':
        return genMulTable(skill, 6);
      case 'l3_mul_table_7':
        return genMulTable(skill, 7);
      case 'l3_mul_table_8':
        return genMulTable(skill, 8);
      case 'l3_mul_table_9':
        return genMulTable(skill, 9);
      case 'l3_div_table_2':
        return genDivTable(skill, 2);
      case 'l3_div_table_5':
        return genDivTable(skill, 5);
      case 'l3_div_table_9':
        return genDivTable(skill, 9);
      case 'l4_fraction_add_same_den':
        return genFractionSameDen(skill, true);
      case 'l4_fraction_sub_same_den':
        return genFractionSameDen(skill, false);
      case 'l4_decimal_add_1dp':
        return genDecimalAddSub(skill, true);
      case 'l4_decimal_sub_1dp':
        return genDecimalAddSub(skill, false);
      case 'l4_mul_powers_of_10':
        return genMulPower10(skill);
      case 'l5_decimal_mul_whole':
        return genDecimalMulWhole(skill);
      case 'l5_percent_of_number':
        return genPercentOf(skill);
      case 'l5_ratio_intro':
        return genRatioIntro(skill);
      default:
        return genAddNoCarry('l1_add_no_carry_10', 10, 9);
    }
  }

  function normalizeGrade(grade) {
    const g = parseInt(grade, 10);
    if (g >= 1 && g <= 5) return g;
    return 1;
  }

  function getGradeMeta(grade) {
    return GRADES[normalizeGrade(grade)];
  }

  function getStoredGrade() {
    const raw = global.localStorage.getItem(LS_GRADE);
    if (raw != null) return normalizeGrade(raw);
    return null;
  }

  function setStoredGrade(grade) {
    global.localStorage.setItem(LS_GRADE, String(normalizeGrade(grade)));
  }

  function gradeToTier(grade) {
    return getGradeMeta(grade).tier;
  }

  function createSession(gradeOrTier, options = {}) {
    let grade = options.grade;
    if (grade == null) {
      if (typeof gradeOrTier === 'number' || /^[1-5]$/.test(String(gradeOrTier))) {
        grade = normalizeGrade(gradeOrTier);
      } else {
        const tierMap = { T1: 1, T2: 2, T3: 3, T4: 4, T5: 5, G1: 1, G2: 2, G3: 3, G4: 4, G5: 5 };
        grade = tierMap[gradeOrTier] || 1;
      }
    }
    grade = normalizeGrade(grade);
    _sessionGrade = grade;
    const meta = getGradeMeta(grade);
    const skills = options.skills || meta.skills;
    const usedKeys = new Set();
    let skillCursor = 0;

    function pickSkill() {
      const skill = skills[skillCursor % skills.length];
      skillCursor += 1;
      return skill;
    }

    function next() {
      const maxAttempts = skills.length * 100;
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

    return {
      grade,
      tier: meta.tier,
      label: meta.label,
      next,
      usedCount: () => usedKeys.size,
    };
  }

  function resolveGrade(flappyBootstrap, profile) {
    const stored = getStoredGrade();
    if (stored != null) return stored;
    const tg = profile?.target_grade || flappyBootstrap?.profile?.target_grade;
    if (tg >= 1 && tg <= 5) return normalizeGrade(tg);
    const unlocked = flappyBootstrap?.tier_unlocked;
    if (Array.isArray(unlocked) && unlocked.length) {
      const t = unlocked[unlocked.length - 1];
      const m = { T1: 1, T2: 2, T3: 3, T4: 4, T5: 5 };
      if (m[t]) return m[t];
    }
    return 1;
  }

  function resolveActiveTier(flappyBootstrap) {
    const g = resolveGrade(flappyBootstrap, null);
    return gradeToTier(g);
  }

  global.MathBlastQuestionGen = {
    GRADES,
    LS_GRADE,
    createSession,
    getGradeMeta,
    getStoredGrade,
    setStoredGrade,
    gradeToTier,
    resolveGrade,
    resolveActiveTier,
    problemKey,
    normalizeGrade,
  };
})(typeof window !== 'undefined' ? window : global);
