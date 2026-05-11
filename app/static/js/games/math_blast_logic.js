// Domain Lock
const _allowedDomains = ["choimahoc.io.vn", "localhost", "127.0.0.1"];
if (!_allowedDomains.includes(window.location.hostname)) {
    window.location.href = "https://choimahoc.io.vn";
}

const timerEl = document.getElementById('timer');
const scoreEl = document.getElementById('score');
const num1El = document.getElementById('num1');
const num2El = document.getElementById('num2');
const operatorEl = document.getElementById('operator');
const inputEl = document.getElementById('answer-input');
const gameOverEl = document.getElementById('game-over');
const finalScoreEl = document.getElementById('final-score');
const highScoreEl = document.getElementById('high-score-text');
const levelSelectionEl = document.getElementById('level-selection');
const badgeEl = document.getElementById('game-badge');

const LEVELS = {
    KIDDY: { name: 'Kiddy', time: 45, max: 10, ops: ['+', '-'], color: '#10b981' },
    STARTER: { name: 'Starter', time: 40, max: 100, ops: ['+', '-'], color: '#3b82f6' },
    EXPLORER: { name: 'Explorer', time: 35, max: 1000, ops: ['+', '-', 'x'], x_max: 5, color: '#f59e0b' },
    MASTER: { name: 'Master', time: 30, max: 1000, ops: ['+', '-', 'x', '/'], x_max: 9, color: '#ec4899' },
    GENIUS: { name: 'Genius', time: 30, max: 100000, ops: ['+', '-', 'x', '/'], x_max: 50, color: '#ef4444' }
};

let currentLevel = 'KIDDY';
let score = 0;
let timeLeft = 30;
let correctAnswer = 0;
let gameActive = false;
let timerInterval;
let recognition = null;
let _lastVoiceAnswer = null;
let _lastVoiceTime = 0;
let _canSubmit = true; // Chỉ cho phép submit 1 lần mỗi câu hỏi

function showLevelSelection() {
    gameActive = false;
    clearInterval(timerInterval);
    levelSelectionEl.style.display = 'flex';
    document.querySelector('.level-link').style.display = 'none';
    gameOverEl.style.display = 'none';
    badgeEl.style.display = 'none';
}

// Ensure functions used in HTML via onclick are exposed to global scope
window.showLevelSelection = showLevelSelection;
window.selectLevel = function(lvl) {
    currentLevel = lvl;
    levelSelectionEl.style.display = 'none';
    document.querySelector('.level-link').style.display = 'flex';

    // Set badge
    badgeEl.innerText = LEVELS[lvl].name;
    badgeEl.style.display = 'block';
    badgeEl.style.setProperty('--level-color', LEVELS[lvl].color);
    badgeEl.style.setProperty('--level-glow', LEVELS[lvl].color + '4d'); // 30% alpha

    startGame();
};

window.startGame = function() {
    const config = LEVELS[currentLevel];
    score = 0;
    timeLeft = config.time;
    gameActive = true;
    _canSubmit = true;

    scoreEl.innerText = '0';
    timerEl.innerText = timeLeft;
    timerEl.classList.remove('warning');
    gameOverEl.style.display = 'none';
    clearInput();

    generateProblem();

    // VOICE: Start listening
    startVoiceListening();

    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        timeLeft--;
        timerEl.innerText = timeLeft;
        if (timeLeft <= 5) timerEl.classList.add('warning');
        if (timeLeft <= 0) endGame();
    }, 1000);
};

function generateProblem() {
    const config = LEVELS[currentLevel];
    const op = config.ops[Math.floor(Math.random() * config.ops.length)];
    let n1, n2;

    if (op === '+' || op === '-') {
        n1 = Math.floor(Math.random() * config.max);
        n2 = Math.floor(Math.random() * config.max);
        if (op === '-' && n1 < n2) [n1, n2] = [n2, n1];
        correctAnswer = op === '+' ? n1 + n2 : n1 - n2;
    } else if (op === 'x') {
        n1 = Math.floor(Math.random() * (currentLevel === 'GENIUS' ? 100 : 20)) + 2;
        n2 = Math.floor(Math.random() * config.x_max) + 2;
        correctAnswer = n1 * n2;
    } else if (op === '/') {
        // Div logic: result * divisor = dividend
        let res = Math.floor(Math.random() * (currentLevel === 'GENIUS' ? 50 : 10)) + 2;
        let div = Math.floor(Math.random() * config.x_max) + 2;
        n1 = res * div;
        n2 = div;
        correctAnswer = res;
    }

    num1El.innerText = n1;
    num2El.innerText = n2;
    operatorEl.innerText = (op === 'x' ? '×' : (op === '/' ? '÷' : op));

    // Reset voice debounce state cho mỗi câu hỏi mới
    _lastVoiceAnswer = null;
    _lastVoiceTime = 0;
    
    // Khóa nhận đáp án trong lúc máy đọc câu hỏi (tránh xung đột / echo)
    _canSubmit = false;

    // VOICE: Speak question
    let opText = op === '+' ? 'cộng' : (op === '-' ? 'trừ' : (op === 'x' ? 'nhân' : 'chia'));
    GameUtils.speak(`${n1} ${opText} ${n2} bằng mấy?`, () => {
        console.log("[Logic] TTS finished reading question.");
        // Khởi động lại session nhận diện để xóa sạch transcript cũ (bị dính tiếng TTS)
        if (gameActive) {
            if (recognition) {
                console.log("[Logic] Aborting recognition to clear buffer.");
                try { recognition.abort(); } catch (e) {}
            }
            // Đợi mic khởi động lại xong rồi mới mở cờ
            setTimeout(() => {
                _canSubmit = true;
                console.log("[Logic] _canSubmit is now true.");
            }, 400);
        }
    });
}

function startVoiceListening() {
    if (!gameActive) return;

    const indicator = document.getElementById('voice-indicator');
    const vText = document.getElementById('voice-text');

    if (!recognition) {
        recognition = GameUtils.createRecognition(
            // ⚡ Nhận cả interim (isFinal=false) để phản hồi sớm hơn ~1s
            (transcript, isFinal) => {
                if (!gameActive) return;
                // Bỏ qua kết quả quá ngắn (nhiễu)
                if (transcript.trim().length < 1) return;
                handleVoiceInput(transcript, isFinal);
            },
            (status) => {
                if (status === 'listening') indicator.classList.add('active');
                else indicator.classList.remove('active');
            },
            true // autoRestart thay thế continuous mode (hoạt động tốt hơn mobile)
        );
    }

    if (recognition) recognition.startListening();
}


function handleVoiceInput(text, isFinal) {
    console.log(`[VoiceInput] text: "${text}", isFinal: ${isFinal}, _canSubmit: ${_canSubmit}`);
    if (!_canSubmit) return;

    let num = GameUtils.textToNumber(text);
    console.log(`[VoiceInput] parsed num:`, num);
    if (num === null) return;

    const now = Date.now();
    // Debounce: cực ngắn (200ms) để phản hồi tức thì
    if (num === _lastVoiceAnswer && now - _lastVoiceTime < 200) return;

    // Interim: chỉ hiển thị lên input, chưa submit
    // Final: submit ngay
    inputEl.value = num;

    if (isFinal) {
        _lastVoiceAnswer = num;
        _lastVoiceTime = now;
        submitAnswer();
    } else {
        // Nếu interim đã khớp đáp án → submit sớm, không cần chờ final
        if (parseInt(inputEl.value) === correctAnswer) {
            _lastVoiceAnswer = num;
            _lastVoiceTime = now;
            submitAnswer();
        }
    }
}

window.addNum = function(n) {
    if (!gameActive) return;
    if (inputEl.value.length < 8) {
        inputEl.value += n;
        if (parseInt(inputEl.value) === correctAnswer) {
            handleCorrect();
        }
    }
};

window.clearInput = clearInput;
function clearInput() {
    inputEl.value = '';
    inputEl.classList.remove('correct', 'wrong');
}

window.submitAnswer = submitAnswer;
function submitAnswer() {
    if (!gameActive || inputEl.value === '' || !_canSubmit) return;
    if (parseInt(inputEl.value) === correctAnswer) handleCorrect();
    else handleWrong();
}

function handleCorrect() {
    if (!_canSubmit) return;
    _canSubmit = false; // Khóa ngay lập tức
    
    inputEl.value = ''; 
    score += 10;
    scoreEl.innerText = score;
    showFeedback('+', 'var(--success)');

    timeLeft += 1;
    timerEl.innerText = timeLeft;

    setTimeout(() => {
        clearInput();
        generateProblem();
        // _canSubmit sẽ được generateProblem mở lại sau 600ms
    }, 150);
}

function handleWrong() {
    inputEl.classList.add('wrong');
    showFeedback('❌', 'var(--error)');

    // VOICE: Feedback for wrong answer
    if (gameActive) {
        _canSubmit = false;
        GameUtils.speak("Tính lại nhé!", () => {
            if (gameActive) {
                if (recognition) {
                    try { recognition.abort(); } catch (e) {}
                }
                setTimeout(() => {
                    _canSubmit = true;
                }, 400);
            }
        });
    }

    setTimeout(clearInput, 300);
}

function showFeedback(text, color) {
    const fb = document.createElement('div');
    fb.className = 'feedback-pop';
    fb.innerText = text;
    fb.style.color = color;
    fb.style.left = (Math.random() * 40 + 30) + '%';
    fb.style.top = '45%';
    document.querySelector('.game-container').appendChild(fb);
    setTimeout(() => fb.remove(), 800);
}

function endGame() {
    gameActive = false;
    clearInterval(timerInterval);

    // VOICE: Stop listening and talking
    if (recognition) recognition.stopListening();
    window.speechSynthesis.cancel();
    document.getElementById('voice-indicator').classList.remove('active');

    finalScoreEl.innerText = score;

    // Per-level High Score
    const key = `mathBlast_highScore_${currentLevel}`;
    const highScore = localStorage.getItem(key) || 0;
    if (score > highScore) {
        localStorage.setItem(key, score);
        highScoreEl.innerText = `Kỷ lục mới Cấp độ ${LEVELS[currentLevel].name}: ${score}! 🏆`;
    } else {
        highScoreEl.innerText = `Kỷ lục (${LEVELS[currentLevel].name}): ${highScore}`;
    }

    gameOverEl.style.display = 'flex';
}

window.addEventListener('keydown', (e) => {
    if (!gameActive) return;
    if (e.key >= '0' && e.key <= '9') window.addNum(e.key);
    else if (e.key === 'Backspace' || e.key === 'c' || e.key === 'C') clearInput();
    else if (e.key === 'Enter') submitAnswer();
});

// Initialize with selection
showLevelSelection();
