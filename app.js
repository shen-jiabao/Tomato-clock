class PomodoroTimer {
    constructor() {
        this.settings = {
            workTime: 25 * 60,
            shortBreakTime: 5 * 60,
            longBreakTime: 15 * 60,
            pomodorosBeforeLongBreak: 4,
            autoStartBreaks: true,
            soundEnabled: true
        };

        this.state = {
            mode: 'work',
            timeLeft: this.settings.workTime,
            totalTime: this.settings.workTime,
            isRunning: false,
            completedPomodoros: 0,
            intervalId: null
        };

        this.circumference = 2 * Math.PI * 90;

        this.init();
    }

    init() {
        this.loadSettings();
        this.cacheDOMElements();
        this.bindEvents();
        this.updateDisplay();
        this.updateProgressRing();
    }

    cacheDOMElements() {
        this.minutesEl = document.getElementById('minutes');
        this.secondsEl = document.getElementById('seconds');
        this.startPauseBtn = document.getElementById('startPauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.completedCountEl = document.getElementById('completedCount');
        this.progressRing = document.querySelector('.progress-ring-progress');
        this.timerDisplay = document.querySelector('.timer-display');
        this.modeBtns = document.querySelectorAll('.mode-btn');
        this.modeLabel = document.getElementById('modeLabel');
        this.pomodoroDots = document.getElementById('pomodoroDots');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.openSettingsBtn = document.getElementById('openSettings');
        this.closeSettingsBtn = document.getElementById('closeSettings');
        this.saveSettingsBtn = document.getElementById('saveSettings');
    }

    bindEvents() {
        this.startPauseBtn.addEventListener('click', () => this.toggleTimer());
        this.resetBtn.addEventListener('click', () => this.resetTimer());

        this.modeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => this.switchMode(e.target.dataset.mode));
        });

        this.openSettingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());

        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this.toggleTimer();
            } else if (e.code === 'KeyR') {
                this.resetTimer();
            }
        });
    }

    toggleTimer() {
        if (this.state.isRunning) {
            this.pause();
        } else {
            this.start();
        }
    }

    start() {
        this.state.isRunning = true;
        this.startPauseBtn.textContent = '暂停';
        this.timerDisplay.classList.add('running');

        this.state.intervalId = setInterval(() => {
            this.state.timeLeft--;
            this.updateDisplay();
            this.updateProgressRing();

            if (this.state.timeLeft <= 0) {
                this.complete();
            }
        }, 1000);
    }

    pause() {
        this.state.isRunning = false;
        this.startPauseBtn.textContent = '继续';
        this.timerDisplay.classList.remove('running');
        clearInterval(this.state.intervalId);
    }

    resetTimer() {
        this.pause();
        this.state.timeLeft = this.getCurrentModeTime();
        this.state.totalTime = this.getCurrentModeTime();
        this.startPauseBtn.textContent = '开始';
        this.updateDisplay();
        this.updateProgressRing();
    }

    complete() {
        clearInterval(this.state.intervalId);
        this.state.isRunning = false;
        this.timerDisplay.classList.remove('running');

        this.playSound();

        if (typeof window.electronAPI !== 'undefined') {
            if (this.state.mode === 'work') {
                window.electronAPI.showNotification('番茄钟', '专注时间完成！休息一下吧 🎉');
            } else {
                window.electronAPI.showNotification('番茄钟', '休息结束！开始新的专注吧 💪');
            }
        }

        if (this.state.mode === 'work') {
            this.state.completedPomodoros++;
            this.completedCountEl.textContent = this.state.completedPomodoros;
            this.updatePomodoroDots();

            if (this.state.completedPomodoros % this.settings.pomodorosBeforeLongBreak === 0) {
                this.switchMode('longBreak', this.settings.autoStartBreaks);
            } else {
                this.switchMode('shortBreak', this.settings.autoStartBreaks);
            }
        } else {
            this.switchMode('work', false);
        }
    }

    skipToNext() {
        this.pause();
        if (this.state.mode === 'work') {
            this.switchMode('shortBreak', false);
        } else {
            this.switchMode('work', false);
        }
    }

    switchMode(mode, autoStart = false) {
        this.pause();
        this.state.mode = mode;
        this.state.timeLeft = this.getCurrentModeTime();
        this.state.totalTime = this.getCurrentModeTime();
        this.startPauseBtn.textContent = '开始';

        this.updateModeButtons();
        this.updateModeLabel();
        this.updatePomodoroDots();
        this.updateDisplay();
        this.updateProgressRing();
        this.updateThemeColors();

        if (autoStart) {
            setTimeout(() => this.start(), 500);
        }
    }

    getCurrentModeTime() {
        switch (this.state.mode) {
            case 'work':
                return this.settings.workTime;
            case 'shortBreak':
                return this.settings.shortBreakTime;
            case 'longBreak':
                return this.settings.longBreakTime;
            default:
                return this.settings.workTime;
        }
    }

    updateDisplay() {
        const minutes = Math.floor(this.state.timeLeft / 60);
        const seconds = this.state.timeLeft % 60;

        this.minutesEl.textContent = String(minutes).padStart(2, '0');
        this.secondsEl.textContent = String(seconds).padStart(2, '0');

        document.title = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')} - 番茄钟`;
    }

    updateProgressRing() {
        const progress = this.state.timeLeft / this.state.totalTime;
        const offset = this.circumference * progress;
        this.progressRing.style.strokeDasharray = this.circumference;
        this.progressRing.style.strokeDashoffset = this.circumference - offset;
    }

    updateModeButtons() {
        this.modeBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === this.state.mode);
        });
    }

    updateModeLabel() {
        const labels = { work: '工作时间', shortBreak: '短休息', longBreak: '长休息' };
        this.modeLabel.textContent = labels[this.state.mode];
        this.modeLabel.dataset.mode = this.state.mode;
    }

    updatePomodoroDots() {
        const dots = this.pomodoroDots.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            const isFilled = index < (this.state.completedPomodoros % this.settings.pomodorosBeforeLongBreak || (this.state.completedPomodoros > 0 && this.state.completedPomodoros % this.settings.pomodorosBeforeLongBreak === 0 ? this.settings.pomodorosBeforeLongBreak : 0));
            dot.classList.toggle('filled', isFilled);
            dot.dataset.mode = this.state.mode;
        });
    }

    updateThemeColors() {
        const root = document.documentElement;
        if (this.state.mode === 'work') {
            root.style.setProperty('--primary-color', '#F25F78');
            root.style.setProperty('--secondary-color', '#4ECDC4');
        } else {
            root.style.setProperty('--primary-color', '#4ECDC4');
            root.style.setProperty('--secondary-color', '#F25F78');
        }
    }

    playSound() {
        if (!this.settings.soundEnabled) return;

        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(440, audioContext.currentTime + 0.5);

        gainNode.gain.setValueAtTime(0.5, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);

        setTimeout(() => {
            const osc2 = audioContext.createOscillator();
            const gain2 = audioContext.createGain();
            osc2.connect(gain2);
            gain2.connect(audioContext.destination);
            osc2.type = 'sine';
            osc2.frequency.setValueAtTime(880, audioContext.currentTime);
            gain2.gain.setValueAtTime(0.5, audioContext.currentTime);
            gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
            osc2.start(audioContext.currentTime);
            osc2.stop(audioContext.currentTime + 0.3);
        }, 600);
    }

    openSettings() {
        this.settingsPanel.classList.add('active');
        this.loadSettingsToForm();
    }

    closeSettings() {
        this.settingsPanel.classList.remove('active');
    }

    loadSettingsToForm() {
        document.getElementById('workTime').value = this.settings.workTime / 60;
        document.getElementById('shortBreakTime').value = this.settings.shortBreakTime / 60;
        document.getElementById('longBreakTime').value = this.settings.longBreakTime / 60;
        document.getElementById('pomodorosBeforeLongBreak').value = this.settings.pomodorosBeforeLongBreak;
        document.getElementById('autoStartBreaks').checked = this.settings.autoStartBreaks;
        document.getElementById('soundEnabled').checked = this.settings.soundEnabled;
    }

    saveSettings() {
        const workTime = parseInt(document.getElementById('workTime').value);
        const shortBreakTime = parseInt(document.getElementById('shortBreakTime').value);
        const longBreakTime = parseInt(document.getElementById('longBreakTime').value);
        const pomodorosBeforeLongBreak = parseInt(document.getElementById('pomodorosBeforeLongBreak').value);

        if (this.validateSettings(workTime, shortBreakTime, longBreakTime, pomodorosBeforeLongBreak)) {
            this.settings.workTime = workTime * 60;
            this.settings.shortBreakTime = shortBreakTime * 60;
            this.settings.longBreakTime = longBreakTime * 60;
            this.settings.pomodorosBeforeLongBreak = pomodorosBeforeLongBreak;
            this.settings.autoStartBreaks = document.getElementById('autoStartBreaks').checked;
            this.settings.soundEnabled = document.getElementById('soundEnabled').checked;

            this.saveSettingsToStorage();
            this.resetTimer();
            this.closeSettings();
        }
    }

    validateSettings(work, shortBreak, longBreak, pomodorosBeforeLongBreak) {
        if (work < 1 || work > 60) {
            alert('专注时长必须在 1-60 分钟之间');
            return false;
        }
        if (shortBreak < 1 || shortBreak > 30) {
            alert('短休息必须在 1-30 分钟之间');
            return false;
        }
        if (longBreak < 1 || longBreak > 60) {
            alert('长休息必须在 1-60 分钟之间');
            return false;
        }
        if (pomodorosBeforeLongBreak < 1 || pomodorosBeforeLongBreak > 10) {
            alert('长休息前的番茄数必须在 1-10 之间');
            return false;
        }
        return true;
    }

    saveSettingsToStorage() {
        try {
            localStorage.setItem('pomodoroSettings', JSON.stringify(this.settings));
        } catch (e) {
            console.warn('无法保存设置到本地存储:', e);
        }
    }

    loadSettings() {
        try {
            const saved = localStorage.getItem('pomodoroSettings');
            if (saved) {
                const parsed = JSON.parse(saved);
                this.settings = { ...this.settings, ...parsed };
            }
        } catch (e) {
            console.warn('无法加载本地设置:', e);
        }

        this.state.timeLeft = this.settings.workTime;
        this.state.totalTime = this.settings.workTime;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.pomodoroTimer = new PomodoroTimer();

    if (typeof window.electronAPI !== 'undefined') {
        window.electronAPI.onToggleTimer(() => {
            window.pomodoroTimer.toggleTimer();
        });

        window.electronAPI.onResetTimer(() => {
            window.pomodoroTimer.resetTimer();
        });

        const originalUpdateDisplay = window.pomodoroTimer.updateDisplay.bind(window.pomodoroTimer);
        window.pomodoroTimer.updateDisplay = function() {
            originalUpdateDisplay();
            const minutes = Math.floor(this.state.timeLeft / 60);
            const seconds = this.state.timeLeft % 60;
            const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            const modeStr = this.state.mode === 'work' ? '专注' : '休息';
            const statusStr = this.state.isRunning ? '⏱️' : '⏸️';
            window.electronAPI.updateTrayTooltip(`${statusStr} ${modeStr} ${timeStr}`);
        };
    }
});
