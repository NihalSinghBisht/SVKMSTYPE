// Word pool - 100 most common English words
const commonWords = [
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'
];

// Punctuation marks
const punctuationMarks = ['.', ',', '!', '?', ';', ':', '"', "'", '(', ')', '-', '—'];

// Numbers
const numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

// Configuration object
const config = {
    mode: 'words',
    wordCount: 25
};

// State object
let state = {
    words: [],
    currentWordIndex: 0,
    currentLetterIndex: 0,
    input: '',
    started: false,
    finished: false,
    startTime: null,
    correctChars: 0,
    incorrectChars: 0,
    timerInterval: null,
    focused: true,
    wordsTyped: 0
};

// DOM Elements
const wordsDiv = document.getElementById('words');
const typingInput = document.getElementById('typing-input');
const wpmSpan = document.getElementById('wpm');
const accuracySpan = document.getElementById('accuracy');
const timerSpan = document.getElementById('timer');
const resultsDiv = document.getElementById('results');
const liveStats = document.getElementById('live-stats');
const focusWarning = document.querySelector('.focus-warning');

// Initialize the application
function init() {
    generateWords();
    renderWords();
    setupEventListeners();
    typingInput.focus();
}

// Generate random words for the test
function generateWords() {
    state.words = [];
    for (let i = 0; i < config.wordCount; i++) {
        const word = commonWords[Math.floor(Math.random() * commonWords.length)];
        state.words.push({
            text: word,
            letters: []
        });
    }
}

// Render words to the DOM
function renderWords() {
    wordsDiv.innerHTML = '';
    state.words.forEach((word, wordIndex) => {
        const wordSpan = document.createElement('span');
        wordSpan.className = 'word';
        wordSpan.setAttribute('data-index', wordIndex);
        
        word.text.split('').forEach((letter, letterIndex) => {
            const letterSpan = document.createElement('span');
            letterSpan.className = 'letter';
            letterSpan.textContent = letter;
            letterSpan.setAttribute('data-letter-index', letterIndex);
            wordSpan.appendChild(letterSpan);
        });
        
        wordsDiv.appendChild(wordSpan);
    });
    
    updateCaret();
}

// Update caret position
function updateCaret() {
    document.querySelectorAll('.word').forEach(w => w.classList.remove('active'));
    document.querySelectorAll('.letter').forEach(l => l.classList.remove('current'));
    
    const currentWord = document.querySelector(`.word[data-index="${state.currentWordIndex}"]`);
    if (currentWord) {
        currentWord.classList.add('active');
        const currentLetter = currentWord.querySelector(`.letter[data-letter-index="${state.currentLetterIndex}"]`);
        if (currentLetter) {
            currentLetter.classList.add('current');
        }
    }
}

// Setup event listeners
function setupEventListeners() {
    typingInput.addEventListener('input', handleInput);
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            resetTest();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (!state.started) {
                resetTest();
            } else if (state.started && !state.finished) {
                endTest();
            }
        } else if (e.key === 'Escape') {
            e.preventDefault();
            typingInput.blur();
        }
    });

    typingInput.addEventListener('blur', () => {
        state.focused = false;
        document.body.classList.add('focus-lost');
        focusWarning.classList.add('show');
    });

    typingInput.addEventListener('focus', () => {
        state.focused = true;
        document.body.classList.remove('focus-lost');
        focusWarning.classList.remove('show');
    });

    document.addEventListener('click', () => {
        if (!state.focused && !state.finished) {
            typingInput.focus();
        }
    });
}

// Handle typing input
function handleInput(e) {
    if (state.finished) return;

    if (!state.started) {
        startTest();
    }

    const input = e.target.value;
    const currentWord = state.words[state.currentWordIndex];
    
    if (input.endsWith(' ')) {
        // Move to next word
        const typedWord = input.trim();
        checkWord(typedWord, currentWord);
        state.currentWordIndex++;
        state.currentLetterIndex = 0;
        typingInput.value = '';
        state.input = '';
        state.wordsTyped++;
        
        if (state.wordsTyped >= config.wordCount) {
            endTest();
        }
    } else {
        // Update current word
        state.input = input;
        state.currentLetterIndex = input.length;
        checkCurrentWord(input, currentWord);
    }
    
    updateCaret();
    updateStats();
    
    // Update the timer with words remaining
    timerSpan.textContent = `${config.wordCount - state.wordsTyped} words left`;
}

// Check completed word
function checkWord(typedWord, wordObj) {
    const wordSpan = document.querySelector(`.word[data-index="${state.currentWordIndex}"]`);
    const letters = wordSpan.querySelectorAll('.letter');
    
    let hasError = false;
    letters.forEach((letter, i) => {
        if (i < typedWord.length) {
            if (typedWord[i] === wordObj.text[i]) {
                letter.classList.add('correct');
                letter.classList.remove('incorrect');
                state.correctChars++;
            } else {
                letter.classList.add('incorrect');
                letter.classList.remove('correct');
                state.incorrectChars++;
                hasError = true;
            }
        }
    });
    
    if (typedWord.length > wordObj.text.length) {
        const extra = typedWord.slice(wordObj.text.length);
        extra.split('').forEach(char => {
            const extraSpan = document.createElement('span');
            extraSpan.className = 'letter extra';
            extraSpan.textContent = char;
            wordSpan.appendChild(extraSpan);
            state.incorrectChars++;
            hasError = true;
        });
    }
    
    if (typedWord.length < wordObj.text.length) {
        hasError = true;
        state.incorrectChars += (wordObj.text.length - typedWord.length);
    }
    
    if (hasError) {
        wordSpan.classList.add('error');
    }
    
    state.correctChars++; // Count space
}

// Check current word being typed
function checkCurrentWord(input, wordObj) {
    const wordSpan = document.querySelector(`.word[data-index="${state.currentWordIndex}"]`);
    const letters = wordSpan.querySelectorAll('.letter:not(.extra)');
    
    letters.forEach((letter, i) => {
        letter.classList.remove('correct', 'incorrect');
    });
    
    const extras = wordSpan.querySelectorAll('.letter.extra');
    extras.forEach(e => e.remove());
    
    for (let i = 0; i < input.length; i++) {
        if (i < wordObj.text.length) {
            if (input[i] === wordObj.text[i]) {
                letters[i].classList.add('correct');
            } else {
                letters[i].classList.add('incorrect');
            }
        } else {
            const extraSpan = document.createElement('span');
            extraSpan.className = 'letter extra';
            extraSpan.textContent = input[i];
            wordSpan.appendChild(extraSpan);
        }
    }
}

// Start the test
function startTest() {
    state.started = true;
    state.startTime = Date.now();
    timerSpan.textContent = `${config.wordCount} words left`;
}

// Update live statistics
function updateStats() {
    const timeElapsed = (Date.now() - state.startTime) / 1000 / 60;
    const wpm = Math.round((state.correctChars / 5) / timeElapsed) || 0;
    const totalChars = state.correctChars + state.incorrectChars;
    const accuracy = totalChars > 0 ? Math.round((state.correctChars / totalChars) * 100) : 100;
    
    wpmSpan.textContent = wpm;
    accuracySpan.textContent = accuracy + '%';
}

// End the test and show results
function endTest() {
    if (!state.finished) {  // Prevent multiple submissions
        state.finished = true;
        
        const timeElapsed = (Date.now() - state.startTime) / 1000 / 60;
        const wpm = Math.round((state.correctChars / 5) / timeElapsed) || 0;
        const totalChars = state.correctChars + state.incorrectChars;
        const accuracy = totalChars > 0 ? Math.round((state.correctChars / totalChars) * 100) : 100;
        const rawWpm = Math.round(totalChars / 5 / timeElapsed) || 0;
        
        document.getElementById('final-wpm').textContent = wpm;
        document.getElementById('final-accuracy').textContent = accuracy + '%';
        document.getElementById('final-raw').textContent = rawWpm;
        document.getElementById('final-chars').textContent = `${state.correctChars}/${state.incorrectChars}`;
        
        wordsDiv.style.display = 'none';
        liveStats.style.display = 'none';
        resultsDiv.classList.add('show');
        
        // Submit test results to the server
        const userEmail = JSON.parse(localStorage.getItem('userData')).email;
        fetch('/submit_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: userEmail,
                wpm: wpm,
                accuracy: accuracy,
                raw_wpm: rawWpm
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('view-leaderboard').style.display = 'inline-block';
                document.getElementById('share-btn').style.display = 'inline-block';
            }
        })
        .catch(error => console.error('Error submitting results:', error));
    }
}

// Reset test to initial state
function resetTest() {
    state = {
        words: [],
        currentWordIndex: 0,
        currentLetterIndex: 0,
        input: '',
        started: false,
        finished: false,
        startTime: null,
        correctChars: 0,
        incorrectChars: 0,
        focused: true,
        wordsTyped: 0
    };
    
    typingInput.value = '';
    wpmSpan.textContent = '0';
    accuracySpan.textContent = '100%';
    timerSpan.textContent = `${config.wordCount} words left`;
    
    wordsDiv.style.display = 'block';
    liveStats.style.display = 'flex';
    resultsDiv.classList.remove('show');
    
    // Hide result buttons
    document.getElementById('view-leaderboard').style.display = 'none';
    document.getElementById('share-btn').style.display = 'none';
    
    generateWords();
    renderWords();
    typingInput.focus();
}

// Set test duration
function setDuration(duration) {
    config.mode = 'time';
    config.duration = duration;
    state.timeRemaining = duration;
    timerSpan.textContent = duration;
    
    document.querySelectorAll('.config-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    resetTest();
}

// Set word count
function setWordCount(count) {
    config.mode = 'words';
    config.wordCount = count;
    
    document.querySelectorAll('.config-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    resetTest();
}

// Toggle punctuation/numbers mode
function setMode(mode) {
    if (mode === 'punctuation') {
        config.punctuation = !config.punctuation;
    } else if (mode === 'numbers') {
        config.numbers = !config.numbers;
    }
    event.target.classList.toggle('active');
    
    // Regenerate words with new settings
    generateWords();
    renderWords();
}

// Initialize on page load
init();

// Load user data and check authentication
function loadUserData() {
    const userData = localStorage.getItem('userData');
    
    if (!userData) {
        // No user data found, redirect to login
        window.location.href = 'login.html';
        return;
    }
    
    try {
        const user = JSON.parse(userData);
        document.getElementById('user-name').textContent = user.name;
        document.getElementById('user-college').textContent = user.college;
    } catch (error) {
        console.error('Error parsing user data:', error);
        window.location.href = 'login.html';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('userData');
    window.location.href = '/logout';
}

// Load user data when page loads
loadUserData();