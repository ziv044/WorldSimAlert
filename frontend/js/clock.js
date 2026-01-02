// Game clock component
class GameClock {
    constructor() {
        this.currentDate = new Date(2024, 0, 1);
        this.paused = true;
        this.speed = 1;
        this.intervalId = null;
        this.listeners = [];
    }

    start() {
        if (this.intervalId) return;

        this.intervalId = setInterval(() => {
            if (!this.paused) {
                this.tick();
            }
        }, 1000 / this.speed);
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    tick() {
        this.currentDate.setDate(this.currentDate.getDate() + 1);
        this.notifyListeners();
        this.updateDisplay();
    }

    pause() {
        this.paused = true;
        this.updateButtonStates();
    }

    resume() {
        this.paused = false;
        this.updateButtonStates();
    }

    setSpeed(speed) {
        this.speed = speed;
        if (this.intervalId) {
            this.stop();
            this.start();
        }
    }

    updateDisplay() {
        const dateEl = document.getElementById('game-date');
        if (dateEl) {
            dateEl.textContent = this.currentDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }

    updateButtonStates() {
        const pauseBtn = document.getElementById('btn-pause');
        const playBtn = document.getElementById('btn-play');

        if (pauseBtn && playBtn) {
            pauseBtn.classList.toggle('active', this.paused);
            playBtn.classList.toggle('active', !this.paused);
        }
    }

    addListener(callback) {
        this.listeners.push(callback);
    }

    notifyListeners() {
        this.listeners.forEach(cb => cb(this.currentDate));
    }

    setDate(year, month, day) {
        this.currentDate = new Date(year, month - 1, day);
        this.updateDisplay();
    }
}

const gameClock = new GameClock();
