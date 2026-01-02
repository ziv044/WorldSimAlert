// API client for communicating with the backend
const API_BASE = '/api';

const api = {
    async getCountry(code) {
        const response = await fetch(`${API_BASE}/country/${code}`);
        if (!response.ok) throw new Error(`Failed to load country: ${code}`);
        return response.json();
    },

    async getGameState() {
        const response = await fetch(`${API_BASE}/game/state`);
        return response.json();
    },

    async pause() {
        const response = await fetch(`${API_BASE}/game/pause`, { method: 'POST' });
        return response.json();
    },

    async resume() {
        const response = await fetch(`${API_BASE}/game/resume`, { method: 'POST' });
        return response.json();
    },

    async setSpeed(speed) {
        const response = await fetch(`${API_BASE}/game/speed?speed=${speed}`, { method: 'POST' });
        return response.json();
    },

    async controlClock(action, speed = 1.0) {
        const response = await fetch(`${API_BASE}/game/clock?action=${action}&speed=${speed}`, {
            method: 'POST'
        });
        return response.json();
    }
};
