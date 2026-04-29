const GameUtils = {
    speak: (text) => {
        if (!window.speechSynthesis) {
            console.warn("Trình duyệt không hỗ trợ speechSynthesis.");
            return;
        }
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'vi-VN';
        utterance.rate = 0.9;
        utterance.pitch = 1.2;

        window.speechSynthesis.speak(utterance);
    },

    createRecognition: (onResult, onStatusChange, continuous = false) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("Trình duyệt không hỗ trợ SpeechRecognition.");
            return null;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'vi-VN';
        recognition.continuous = continuous;
        recognition.interimResults = false;

        recognition.onstart = () => {
            if (onStatusChange) onStatusChange('listening');
        };

        recognition.onend = () => {
            if (onStatusChange) onStatusChange('idle');
        };

        recognition.onerror = (event) => {
            console.error("Lỗi nhận diện giọng nói:", event.error);
            if (onStatusChange) onStatusChange('error', event.error);
        };

        recognition.onresult = (event) => {
            const results = event.results;
            const transcript = results[results.length - 1][0].transcript;
            console.log("Dữ liệu giọng nói nhận được:", transcript);
            if (onResult) onResult(transcript);
        };

        return recognition;
    },

    textToNumber: (text) => {
        if (!text) return null;
        const lowerText = text.toLowerCase().trim();

        if (!isNaN(lowerText)) return parseInt(lowerText);

        const numberMap = {
            'không': 0, 'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'năm': 5, 'lăm': 5,
            'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9, 'mười': 10, 'mươi': 10, 'mốt': 1
        };

        const words = lowerText.split(/\s+/);
        let total = 0;
        let current = 0;

        for (let word of words) {
            if (numberMap[word] !== undefined) {
                let val = numberMap[word];
                if (word === 'mười' || word === 'mươi') {
                    if (current === 0) current = 10;
                    else current *= 10;
                } else {
                    current += val;
                }
            }
        }
        total = current;

        return total > 0 || lowerText.includes('không') ? total : null;
    }
};

window.GameUtils = GameUtils;
