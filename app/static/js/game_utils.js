/**
 * GameUtils - Voice Recognition + TTS utilities
 *
 * Yêu cầu:
 * - Trình duyệt: Google Chrome hoặc Microsoft Edge (không hỗ trợ Firefox/Brave)
 * - Giao thức: HTTPS hoặc localhost (không hỗ trợ IP LAN qua HTTP)
 */

const GameUtils = {
    _speechWarmed: false,

    warmupSpeech: () => {
        if (!window.speechSynthesis || GameUtils._speechWarmed) return;
        GameUtils._speechWarmed = true;
        window.speechSynthesis.getVoices();
        if (!GameUtils._voicesHooked) {
            GameUtils._voicesHooked = true;
            window.speechSynthesis.addEventListener('voiceschanged', () => {
                window.speechSynthesis.getVoices();
            });
        }
    },

    pickEnVoice: () => {
        const voices = window.speechSynthesis?.getVoices() || [];
        return (
            voices.find((v) => v.lang === 'en-US' && v.localService) ||
            voices.find((v) => v.lang === 'en-US') ||
            voices.find((v) => v.lang.startsWith('en')) ||
            null
        );
    },

    // ─── TTS (Text-to-Speech) ────────────────────────────────────────────────
    speak: (text, onEndCallback) => {
        if (!window.speechSynthesis) {
            if (onEndCallback) onEndCallback();
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'vi-VN';
        utterance.rate = 1.1;
        utterance.pitch = 1.2;
        utterance.volume = 1.0;

        if (onEndCallback) {
            let called = false;
            const done = () => {
                if (!called) {
                    called = true;
                    onEndCallback();
                }
            };
            utterance.onend = done;
            utterance.onerror = done;
            // Fallback đảm bảo callback luôn chạy (mobile timeout)
            setTimeout(done, Math.max(text.length * 90, 2500));
        }

        window.speechSynthesis.speak(utterance);
    },

    /** English Math — TTS en-US */
    speakEn: (text, onEndCallback) => {
        if (!window.speechSynthesis) {
            if (onEndCallback) onEndCallback();
            return;
        }
        GameUtils.warmupSpeech();
        window.speechSynthesis.cancel();
        if (window.speechSynthesis.paused) window.speechSynthesis.resume();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        utterance.pitch = 1.05;
        utterance.volume = 1.0;

        if (onEndCallback) {
            let called = false;
            const done = () => {
                if (!called) {
                    called = true;
                    onEndCallback();
                }
            };
            utterance.onend = done;
            utterance.onerror = done;
            setTimeout(done, Math.max(text.length * 110, 3500));
        }

        const run = () => {
            const voice = GameUtils.pickEnVoice();
            if (voice) utterance.voice = voice;
            window.speechSynthesis.speak(utterance);
        };
        setTimeout(run, 60);
    },

    /** Recognition language for English Math */
    recognitionLang: () =>
        (window.KidLocale && window.KidLocale.speechLang) ||
        (window.ENGLISH_MATH ? 'en-US' : 'vi-VN'),
    /**
     * Tạo recognition engine tối ưu cho cả desktop và mobile.
     *
     * @param {function} onResult       - callback(transcript: string, isFinal: boolean)
     * @param {function} onStatusChange - callback(status: 'listening'|'idle'|'error', detail?)
     * @param {boolean}  autoRestart    - tự restart khi kết thúc
     */
    createRecognition: (onResult, onStatusChange, autoRestart = true) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('[GameUtils] Trình duyệt không hỗ trợ SpeechRecognition. Hãy dùng Chrome hoặc Edge.');
            if (onStatusChange) onStatusChange('error', 'not-supported');
            return null;
        }

        // Kiểm tra giao thức – Web Speech API chỉ hoạt động trên HTTPS hoặc localhost
        const proto = location.protocol;
        const host = location.hostname;
        const isSecure = proto === 'https:' || host === 'localhost' || host === '127.0.0.1';
        if (!isSecure) {
            console.error('[GameUtils] Web Speech API yêu cầu HTTPS hoặc localhost. Hiện tại đang chạy trên:', proto + '//' + host);
            if (onStatusChange) onStatusChange('error', 'insecure-context');
            return null;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = GameUtils.recognitionLang ? GameUtils.recognitionLang() : 'vi-VN';
        recognition.continuous = false;
        recognition.interimResults = !GameUtils.isMobile(); // tắt interim trên mobile để giảm lag
        recognition.maxAlternatives = 3;

        // Flags trạng thái nội bộ
        let _running = false;
        let _starting = false;
        let _shouldRestart = false; // chỉ bật khi startListening() được gọi
        let _lastError = null;
        let _debounceTimer = null;
        let _keepAliveTimer = null;

        // Expose flags ra ngoài để kiểm tra từ bên ngoài
        recognition._isRunning = false;
        recognition._isStarting = false;
        recognition._shouldRestart = false;

        const syncFlags = () => {
            recognition._isRunning = _running;
            recognition._isStarting = _starting;
            recognition._shouldRestart = _shouldRestart;
        };

        recognition.onstart = () => {
            console.log('[GameUtils] ✅ Mic đang nghe.');
            _running = true;
            _starting = false;
            syncFlags();
            _resetKeepAlive();
            if (onStatusChange) onStatusChange('listening');
        };

        recognition.onend = () => {
            console.log('[GameUtils] 🔴 Mic kết thúc phiên.');
            _running = false;
            _starting = false;
            syncFlags();
            if (onStatusChange) onStatusChange('idle');

            if (!_shouldRestart) return;

            // Delay trước khi restart để tránh xung đột – dài hơn nếu lỗi mạng
            const delay = (_lastError === 'network') ? 3000 : 80;
            _lastError = null;

            setTimeout(() => {
                if (!_shouldRestart || _running || _starting) return;
                try {
                    _starting = true;
                    syncFlags();
                    recognition.start();
                } catch (e) {
                    _starting = false;
                    syncFlags();
                    console.warn('[GameUtils] Không thể restart mic:', e.message);
                }
            }, delay);
        };

        recognition.onerror = (event) => {
            const err = event.error;
            console.error('[GameUtils] ❌ Lỗi SpeechRecognition:', err);
            _lastError = err;

            if (err === 'aborted') {
                _starting = false;
                syncFlags();
                return; // aborted là do ta chủ động gọi abort(), không cần xử lý
            }

            if (err === 'not-allowed') {
                _shouldRestart = false;
                syncFlags();
                alert('⚠️ Vui lòng cho phép trình duyệt truy cập Microphone!');
            }

            if (err === 'network') {
                console.warn('[GameUtils] Lỗi network: Web Speech API cần Chrome/Edge trên HTTPS hoặc localhost.');
                // Không dừng lại, sẽ retry theo delay dài ở onend
            }

            if (err === 'no-speech') return; // bình thường khi yên lặng

            if (onStatusChange) onStatusChange('error', err);
        };

        recognition.onresult = (event) => {
            const results = event.results;
            const latest = results[results.length - 1];
            const isFinal = latest.isFinal;

            // Chọn transcript tốt nhất: ưu tiên cái có số, sau đó theo confidence
            let transcript = '';
            let bestConf = -1;
            for (let i = 0; i < latest.length; i++) {
                const alt = latest[i];
                if (/\d/.test(alt.transcript)) {
                    transcript = alt.transcript;
                    break;
                }
                if (alt.confidence > bestConf) {
                    bestConf = alt.confidence;
                    transcript = alt.transcript;
                }
            }

            transcript = transcript.trim();
            if (!transcript) return;

            console.log(`[GameUtils] 🎤 Nhận được: "${transcript}" (final=${isFinal})`);
            _resetKeepAlive();

            clearTimeout(_debounceTimer);

            if (isFinal) {
                if (onResult) onResult(transcript, true);
            } else {
                // Interim: phản hồi nhanh nếu có số, debounce nhẹ nếu là chữ
                if (/\d/.test(transcript)) {
                    if (onResult) onResult(transcript, false);
                } else {
                    _debounceTimer = setTimeout(() => {
                        if (onResult) onResult(transcript, false);
                    }, 150);
                }
            }
        };

        // Keep-alive: restart nếu im lặng quá 8 giây
        function _resetKeepAlive() {
            clearTimeout(_keepAliveTimer);
            if (!_shouldRestart) return;
            _keepAliveTimer = setTimeout(() => {
                if (!_shouldRestart) return;
                console.log('[GameUtils] 🔁 Mic im lặng quá lâu → restart...');
                try { recognition.abort(); } catch (e) { }
                setTimeout(() => {
                    if (_shouldRestart && !_running && !_starting) {
                        recognition.startListening();
                    }
                }, 200);
            }, 8000);
        }

        // ── Public API ──────────────────────────────────────────────────────
        recognition.startListening = async () => {
            if (window.PlayConsent) {
                const ok = await window.PlayConsent.ensureMicConsent();
                if (!ok) {
                    if (onStatusChange) onStatusChange('error', 'consent-required');
                    return;
                }
            }
            _shouldRestart = autoRestart;
            syncFlags();
            if (_running || _starting) return;
            try {
                _starting = true;
                syncFlags();
                recognition.start();
            } catch (e) {
                _starting = false;
                syncFlags();
                console.warn('[GameUtils] Không thể start mic:', e.message);
            }
        };

        recognition.stopListening = () => {
            _shouldRestart = false;
            syncFlags();
            clearTimeout(_keepAliveTimer);
            clearTimeout(_debounceTimer);
            try { recognition.stop(); } catch (e) { }
        };

        return recognition;
    },

    // ─── Text to Number (Tiếng Việt) ────────────────────────────────────────
    /**
     * Chuyển văn bản (số, chữ số rời, hoặc chữ tiếng Việt) thành số nguyên.
     *
     * Xử lý 4 dạng:
     *   1. Số thuần: "1065" → 1065
     *   2. Chữ số rời (STT hay trả về): "1 0 6 5" → 1065
     *   3. Số lẫn trong câu: "bằng 42" → 42 (lấy số cuối)
     *   4. Chữ số tiếng Việt: "một nghìn không trăm sáu mươi lăm" → 1065
     *
     * @param {string} text
     * @returns {number|null}
     */
    textToNumber: (text) => {
        if (!text) return null;

        const cleaned = text.toLowerCase()
            .trim()
            .replace(/[.,!?]/g, '')
            .replace(/\s+/g, ' ');

        // ── Dạng 1: chuỗi là số thuần ──────────────────────────────────────
        if (/^-?\d+$/.test(cleaned)) return parseInt(cleaned, 10);

        // ── Dạng 2: Chữ số rời cách nhau bởi dấu cách: "1 0 6 5" → 1065 ──
        // Nhận dạng: toàn bộ chuỗi là các chữ số đơn cách nhau (ít nhất 2 chữ số)
        if (/^(\d\s)+\d$/.test(cleaned)) {
            const joined = cleaned.replace(/\s/g, '');
            return parseInt(joined, 10);
        }

        // ── Dạng 3: chứa số trong chuỗi → lấy số cuối cùng ────────────────
        // Ưu tiên số có nhiều chữ số nhất (phòng trường hợp đề bài bị lẫn vào)
        const allNums = cleaned.match(/\b\d+\b/g);
        if (allNums) {
            // Tìm số dài nhất (nhiều chữ số nhất = đáp án khả năng cao nhất)
            const longest = allNums.reduce((a, b) => b.length >= a.length ? b : a);
            return parseInt(longest, 10);
        }

        // ── Dạng 4: số chữ tiếng Việt ──────────────────────────────────────
        const units = {
            'không': 0, 'linh': 0, 'lẻ': 0,
            'một': 1, 'mốt': 1, 'nhất': 1,
            'hai': 2, 'ba': 3, 'bốn': 4, 'tư': 4,
            'năm': 5, 'lăm': 5, 'sáu': 6,
            'bảy': 7, 'bẩy': 7, 'tám': 8, 'chín': 9,
            'mười': 10, 'mươi': 10,
        };
        const multipliers = {
            'mươi': 10, 'mười': 10,
            'trăm': 100,
            'nghìn': 1000, 'ngàn': 1000,
            'triệu': 1000000,
        };

        const words = cleaned.split(/\s+/);
        let total = 0;
        let current = 0;

        for (const w of words) {
            if (multipliers[w] !== undefined) {
                const mult = multipliers[w];
                if (current === 0) current = 1;
                current *= mult;
                if (mult >= 1000) { total += current; current = 0; }
            } else if (units[w] !== undefined) {
                const val = units[w];
                if (current > 0 && current % 10 === 0 && w !== 'mười' && w !== 'mươi') {
                    current += val;
                } else if (w === 'không' && current === 0 && total === 0 && words.length === 1) {
                    return 0;
                } else if (w !== 'không' || current > 0 || total > 0) {
                    current += val;
                }
            }
        }
        total += current;

        if (total === 0 && cleaned.includes('không')) return 0;
        if (total > 0) return total;

        if (window.ENGLISH_MATH) {
            const en = {
                zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7,
                eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14,
                fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19,
                twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70,
                eighty: 80, ninety: 90, hundred: 100,
            };
            let sum = 0;
            let hit = false;
            for (const w of words) {
                if (en[w] !== undefined) {
                    sum += en[w];
                    hit = true;
                }
            }
            if (hit) return sum;
        }

        return null;
    },

    // ─── Utility ─────────────────────────────────────────────────────────────
    isMobile: () => /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent),
};

window.GameUtils = GameUtils;

// --- Security Measures (chỉ kích hoạt trên production) ---
/* © choimahoc.io.vn - All rights reserved */
const _owner = '\u0063\u0068\u006f\u0069\u006d\u0061\u0068\u006f\u0063'; // "choimahoc"

/*
setInterval(() => {
    const start = performance.now();
    debugger;
    if (performance.now() - start > 100) {
        document.body.innerHTML = '⚠️ Không được phép!';
    }
}, 1000);

document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('keydown', e => {
    if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'i'))) {
        e.preventDefault();
    }
    if (e.ctrlKey && (e.key === 'u' || e.key === 'U')) {
        e.preventDefault();
    }
});
*/
