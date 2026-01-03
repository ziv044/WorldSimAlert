// World Sim Command Center - Main Application
const App = {
    countryCode: 'ISR',
    countryData: null,
    wsClient: null,
    map: null,
    paused: true,
    speed: 1,

    async init() {
        try {
            console.log('Initializing Command Center...');

            // Initialize modal system
            Modal.init('modal-container');

            // Initialize panels
            KPIPanel.init('kpi-list');
            UnitsPanel.init('units-list');
            OperationsPanel.init('operations-list');
            EventsPanel.init('events-list');

            // Initialize action bar
            ActionBar.init('action-bar');

            // Load country data
            this.countryData = await api.getCountry(this.countryCode);
            this.updateHeader();

            // Render KPIs
            KPIPanel.render(this.countryData);

            // Load other panels
            await Promise.all([
                UnitsPanel.load(this.countryCode),
                OperationsPanel.load(this.countryCode),
                EventsPanel.load(this.countryCode)
            ]);

            // Initialize map
            this.map = await initMap('map', this.countryCode);

            // Load deployment markers on map
            await this.map.loadDeployments();

            // Initialize map selector (after map)
            MapSelector.init(this.map);

            // Initialize WebSocket
            this.wsClient = initWebSocket(this.countryCode);
            this.setupWebSocketHandlers();

            // Load action catalogs
            try {
                await Promise.all([
                    ProcurementActions.loadCatalog(),
                    OperationActions.loadOperationTypes()
                ]);
            } catch (e) {
                console.warn('Failed to preload catalogs:', e);
            }

            // Setup clock controls
            this.setupClockControls();

            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();

            // Get initial game state
            const gameState = await api.getGameState();
            this.paused = gameState.clock?.paused ?? true;
            this.speed = gameState.clock?.speed ?? 1;
            this.updateClockDisplay(gameState.clock);
            this.updateClockControls();

            console.log('Command Center initialized successfully');

        } catch (error) {
            console.error('Failed to initialize Command Center:', error);
            this.showError('Failed to initialize. Make sure the backend is running on port 8000.');
        }
    },

    updateHeader() {
        const meta = this.countryData.meta;
        document.getElementById('country-name').textContent = meta.name || 'Unknown';
        document.getElementById('country-flag').textContent = meta.flag_emoji || '';

        if (meta.current_date) {
            this.updateDateDisplay(meta.current_date);
        }
    },

    updateDateDisplay(date) {
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const dateStr = `${months[date.month - 1]} ${date.day}, ${date.year}`;
        document.getElementById('game-date').textContent = dateStr;
    },

    setupWebSocketHandlers() {
        if (!this.wsClient) return;

        // Connection events
        this.wsClient.on('connected', (data) => {
            console.log('WebSocket connected:', data);
        });

        this.wsClient.on('disconnected', () => {
            console.log('WebSocket disconnected');
        });

        // Clock updates
        this.wsClient.on('clock_tick', (data) => {
            document.getElementById('game-date').textContent = data.date;
            this.paused = data.paused;
            this.speed = data.speed;
            this.updateClockControls();
        });

        // KPI updates
        this.wsClient.on('kpi_update', (data) => {
            Object.assign(this.countryData, data);
            KPIPanel.render(this.countryData);
        });

        // Event triggers
        this.wsClient.on('event_trigger', (data) => {
            EventsPanel.addEvent(data);
            this.showNotification(`Event: ${data.event_name}`, data.severity === 'critical' ? 'failure' : 'info');

            // Auto-pause on critical events
            if (data.auto_pause) {
                this.paused = true;
                this.updateClockControls();
            }
        });

        // Event resolved
        this.wsClient.on('event_resolved', (data) => {
            EventsPanel.removeEvent(data.event_id);
        });

        // Operation updates
        this.wsClient.on('operation_update', (data) => {
            OperationsPanel.updateOperation(data);
            if (this.map) {
                this.map.updateOperation(data);
            }
        });

        // Operation completed
        this.wsClient.on('operation_completed', (data) => {
            OperationsPanel.operationCompleted(data);
            if (this.map) {
                this.map.refresh();
            }
            this.showNotification(
                `Operation ${data.success ? 'Succeeded' : 'Failed'}`,
                data.success ? 'success' : 'failure'
            );
        });

        // Unit movements
        this.wsClient.on('unit_moved', (data) => {
            UnitsPanel.updateUnit(data);
            if (this.map) {
                this.map.updateUnit(data);
            }
        });

        // Unit status changes
        this.wsClient.on('unit_status', (data) => {
            UnitsPanel.updateUnit(data);
        });

        // Game state changes
        this.wsClient.on('game_paused', (data) => {
            this.paused = true;
            this.updateClockControls();
        });

        this.wsClient.on('game_resumed', (data) => {
            this.paused = false;
            this.updateClockControls();
        });

        this.wsClient.on('speed_changed', (data) => {
            this.speed = data.speed;
            this.updateClockControls();
        });

        // Border deployment updates
        this.wsClient.on('deployment_updated', (data) => {
            MilitaryPanel.updateZone(data);
            if (this.map) {
                this.map.updateDeploymentMarker(data.zone_id, data);
            }
        });

        this.wsClient.on('reserves_called', (data) => {
            MilitaryPanel.load(this.countryCode);
            this.showNotification(`${data.called_up.toLocaleString()} reserves called up`, 'info');
        });

        this.wsClient.on('alert_level_changed', (data) => {
            MilitaryPanel.updateZone(data);
            if (this.map) {
                this.map.updateDeploymentMarker(data.zone_id, data);
            }
            if (data.new_level === 'active_defense') {
                this.showNotification(`ALERT: ${data.zone_name} - Active Defense`, 'failure');
            }
        });
    },

    setupClockControls() {
        const pauseBtn = document.getElementById('btn-pause');
        const playBtn = document.getElementById('btn-play');
        const speedBtns = document.querySelectorAll('.speed-btn');

        if (pauseBtn) {
            pauseBtn.addEventListener('click', async () => {
                await api.pause();
                this.paused = true;
                this.updateClockControls();
            });
        }

        if (playBtn) {
            playBtn.addEventListener('click', async () => {
                await api.resume();
                this.paused = false;
                this.updateClockControls();
            });
        }

        speedBtns.forEach(btn => {
            btn.addEventListener('click', async () => {
                const speed = parseInt(btn.dataset.speed);
                await api.setSpeed(speed);
                this.speed = speed;
                this.updateClockControls();
            });
        });
    },

    updateClockControls() {
        const pauseBtn = document.getElementById('btn-pause');
        const playBtn = document.getElementById('btn-play');
        const speedBtns = document.querySelectorAll('.speed-btn');

        // Update pause/play buttons
        if (pauseBtn) pauseBtn.classList.toggle('active', this.paused);
        if (playBtn) playBtn.classList.toggle('active', !this.paused);

        // Update speed buttons
        speedBtns.forEach(btn => {
            const speed = parseInt(btn.dataset.speed);
            btn.classList.toggle('active', speed === this.speed);
        });
    },

    updateClockDisplay(clock) {
        if (!clock || !clock.current_date) return;
        this.updateDateDisplay(clock.current_date);
    },

    showNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `notification notification-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    showError(message) {
        const container = document.querySelector('.main-content');
        if (container) {
            container.innerHTML = `
                <div class="error-overlay">
                    <h2>Error</h2>
                    <p>${message}</p>
                </div>
            `;
        }
    },

    async refresh() {
        this.countryData = await api.getCountry(this.countryCode);
        KPIPanel.render(this.countryData);
        await UnitsPanel.load(this.countryCode);
        await OperationsPanel.load(this.countryCode);
        await EventsPanel.load(this.countryCode);
        if (this.map) {
            this.map.refresh();
            this.map.loadDeployments();
        }
    },

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Don't trigger shortcuts when typing in inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            // Escape closes modals and cancels map selection
            if (e.key === 'Escape') {
                if (MapSelector.isActive && MapSelector.isActive()) {
                    MapSelector.cancel();
                } else if (Modal.activeModal) {
                    Modal.close();
                }
            }

            // F5 = Quick Save
            if (e.key === 'F5') {
                e.preventDefault();
                SaveActions.quickSave();
            }

            // F9 = Quick Load
            if (e.key === 'F9') {
                e.preventDefault();
                SaveActions.quickLoad();
            }

            // Space = Toggle pause
            if (e.key === ' ' && !Modal.activeModal) {
                e.preventDefault();
                if (this.paused) {
                    api.resume();
                    this.paused = false;
                } else {
                    api.pause();
                    this.paused = true;
                }
                this.updateClockControls();
            }
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
