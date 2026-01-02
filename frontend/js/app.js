// Main application logic
let countryData = null;

async function init() {
    try {
        // Load country data
        countryData = await api.getCountry('ISR');

        // Update country info in header
        const meta = countryData.meta;
        document.getElementById('country-name').textContent = meta.name;
        document.getElementById('country-flag').textContent = meta.flag_emoji || '🏳️';

        // Set initial date from data
        gameClock.setDate(
            meta.current_date.year,
            meta.current_date.month,
            meta.current_date.day
        );

        // Render all panels
        renderAllPanels(countryData);

        // Setup clock controls
        setupClockControls();

        // Start clock
        gameClock.start();

        console.log('Game initialized successfully');

    } catch (error) {
        console.error('Failed to initialize:', error);
        document.querySelector('.dashboard').innerHTML =
            `<div class="error panel" style="grid-column: span 2; padding: 2rem; text-align: center;">
                <h2>Failed to load game</h2>
                <p>${error.message}</p>
                <p>Make sure the backend server is running on port 8000.</p>
            </div>`;
    }
}

function setupClockControls() {
    const pauseBtn = document.getElementById('btn-pause');
    const playBtn = document.getElementById('btn-play');
    const speedSelect = document.getElementById('speed-select');

    if (pauseBtn) {
        pauseBtn.addEventListener('click', async () => {
            gameClock.pause();
            await api.pause();
        });
    }

    if (playBtn) {
        playBtn.addEventListener('click', async () => {
            gameClock.resume();
            await api.resume();
        });
    }

    if (speedSelect) {
        speedSelect.addEventListener('change', async (e) => {
            const speed = parseFloat(e.target.value);
            gameClock.setSpeed(speed);
            await api.setSpeed(speed);
        });
    }

    // Set initial button state
    gameClock.updateButtonStates();
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
