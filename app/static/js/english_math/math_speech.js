/**
 * English Math — read math problems aloud in English (TTS).
 * Used by cloned Math Blast V1/V2 under /game/english-shooter/math/*
 */
(function (global) {
  const OP_WORD = {
    add: 'plus',
    sub: 'minus',
    mul: 'times',
    div: 'divided by',
    compare: 'which is bigger',
  };

  const SYM_TO_OP = {
    '+': 'add',
    '-': 'sub',
    '−': 'sub',
    '×': 'mul',
    'x': 'mul',
    '*': 'mul',
    '÷': 'div',
    '/': 'div',
  };

  function n(v) {
    return String(v).replace(',', '.');
  }

  /** V1: num1, operator char (+ - x /), num2 */
  function speakProblem(num1, opChar, num2, onEnd) {
    const op = SYM_TO_OP[opChar] || 'add';
    return speakFromOperands(num1, op, num2, { missing: 'result' }, onEnd);
  }

  function speakFromOperands(a, op, b, opts, onEnd) {
    const text = buildFromOperands(a, op, b, opts);
    return speak(text, onEnd);
  }

  function buildFromOperands(a, op, b, opts) {
    const missing = (opts && opts.missing) || 'result';
    const ow = OP_WORD[op] || String(op);
    const left = n(a);
    const right = n(b);
    if (missing === 'result') {
      return `What is ${left} ${ow} ${right}?`;
    }
    if (missing === 'second') {
      return `What number ${ow} ${right} equals ${left}?`;
    }
    if (missing === 'first') {
      return `${right} ${ow} what equals ${left}?`;
    }
    return `What is ${left} ${ow} ${right}?`;
  }

  function parseQuestionText(q) {
    if (!q) return null;
    const s = q.trim();

    let m = s.match(/^\?\s*\+\s*(\d+(?:[.,]\d+)?)\s*=\s*(\d+(?:[.,]\d+)?)/);
    if (m) {
      return { a: m[2], b: m[1], op: 'add', missing: 'first' };
    }
    m = s.match(/^(\d+(?:[.,]\d+)?)\s*\+\s*\?\s*=\s*(\d+(?:[.,]\d+)?)/);
    if (m) {
      return { a: m[2], b: m[1], op: 'add', missing: 'second' };
    }

    m = s.match(/^(\d+(?:[.,]\d+)?)\s*([+−\-×÷x*/])\s*(\d+(?:[.,]\d+)?)\s*=\s*\?/);
    if (m) {
      const op = SYM_TO_OP[m[2]] || 'add';
      return { a: m[1], b: m[3], op, missing: 'result' };
    }

    m = s.match(/^(\d+)\s*(?:và|and)\s*(\d+)/i);
    if (m && /lớn hơn|bigger/i.test(s)) {
      return { type: 'compare', a: m[1], b: m[2] };
    }

    m = s.match(/^(\d+)\/(\d+)\s*([+−\-])\s*(\d+)\/(\d+)\s*=\s*\?/);
    if (m) {
      const op = SYM_TO_OP[m[3]] || 'add';
      return {
        type: 'fraction',
        text: `What is ${m[1]} over ${m[2]} ${OP_WORD[op]} ${m[4]} over ${m[5]}?`,
      };
    }

    m = s.match(/^([\d,]+)\s*([+−\-])\s*([\d,]+)\s*=\s*\?/);
    if (m && /,/.test(s)) {
      const op = SYM_TO_OP[m[2]] || 'add';
      return {
        type: 'decimal',
        text: `What is ${m[1].replace(',', ' point ')} ${OP_WORD[op]} ${m[3].replace(',', ' point ')}?`,
      };
    }

    m = s.match(/^(\d+)\s*×\s*(\d+)\s*=\s*\?/);
    if (m) {
      return { a: m[1], b: m[2], op: 'mul', missing: 'result' };
    }

    m = s.match(/^(\d+)\s*÷\s*(\d+)\s*=\s*\?/);
    if (m) {
      return { text: `What is ${m[1]} divided by ${m[2]}?` };
    }

    m = s.match(/Chia\s*(\d+)\s*cho\s*(\d+)\s*—\s*tỉ\s*(\d+)\s*:\s*(\d+)/i);
    if (m) {
      return { text: `Divide ${m[1]} by ${m[2]}. What is the ratio ${m[3]} to ${m[4]}?` };
    }

    return null;
  }

  function speechFromParsed(parsed) {
    if (!parsed) return '';
    if (parsed.text) return parsed.text;
    if (parsed.type === 'compare') {
      return `Which is bigger, ${parsed.a} or ${parsed.b}?`;
    }
    return buildFromOperands(parsed.a, parsed.op, parsed.b, { missing: parsed.missing });
  }

  function speechFromItem(item) {
    if (!item) return '';
    if (item.speechEn) return item.speechEn;
    if (item.a != null && item.op) {
      const left = item.q && item.q.match(/^(\d+)/);
      const right = item.q && item.q.match(/(\d+)\s*=\s*\?/);
      if (left && right) {
        return buildFromOperands(left[1], item.op, right[1], { missing: 'result' });
      }
    }
    return speechFromParsed(parseQuestionText(item.q));
  }

  function displayFromItem(item) {
    if (!item) return '';
    if (item.qEn) return item.qEn;
    let q = item.q || '';
    if (q.includes('số nào lớn hơn')) {
      return q.replace('và', 'and').replace('— số nào lớn hơn?', ' — which is bigger?');
    }
    if (/Chia.*tỉ/.test(q)) {
      return q.replace('Chia', 'Divide').replace('cho', 'by').replace('tỉ', 'ratio');
    }
    return q;
  }

  function enrichItem(item) {
    if (!item) return item;
    const speech = speechFromItem(item);
    if (speech) item.speechEn = speech;
    item.qEn = displayFromItem(item);
    return item;
  }

  function speak(text, onEnd) {
    if (!text) {
      if (onEnd) onEnd();
      return;
    }
    if (global.GameUtils && global.GameUtils.speakEn) {
      global.GameUtils.speakEn(text, onEnd);
      return;
    }
    if (!global.speechSynthesis) {
      if (onEnd) onEnd();
      return;
    }
    if (global.GameUtils && global.GameUtils.warmupSpeech) global.GameUtils.warmupSpeech();
    global.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US';
    u.rate = 0.92;
    u.pitch = 1.05;
    if (global.GameUtils && global.GameUtils.pickEnVoice) {
      const voice = global.GameUtils.pickEnVoice();
      if (voice) u.voice = voice;
    }
    if (onEnd) {
      let done = false;
      const finish = () => {
        if (!done) {
          done = true;
          onEnd();
        }
      };
      u.onend = finish;
      u.onerror = finish;
      setTimeout(finish, Math.max(text.length * 100, 3000));
    }
    setTimeout(() => global.speechSynthesis.speak(u), 30);
  }

  global.EnglishMathSpeech = {
    OP_WORD,
    speak,
    speakProblem,
    speakFromOperands,
    buildFromOperands,
    parseQuestionText,
    speechFromParsed,
    speechFromItem,
    displayFromItem,
    enrichItem,
  };
})();
