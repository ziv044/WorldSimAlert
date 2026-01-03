// API client for World Sim Command Center
const API_BASE = '/api';

const api = {
    // ==================== Country Data ====================
    async getCountry(code) {
        const response = await fetch(`${API_BASE}/country/${code}`);
        if (!response.ok) throw new Error(`Failed to load country: ${code}`);
        return response.json();
    },

    // ==================== Map Data ====================
    async getUnits(code) {
        const response = await fetch(`${API_BASE}/map/units/${code}`);
        if (!response.ok) throw new Error(`Failed to load units: ${code}`);
        return response.json();
    },

    async getBases(code) {
        const response = await fetch(`${API_BASE}/map/bases/${code}`);
        if (!response.ok) throw new Error(`Failed to load bases: ${code}`);
        return response.json();
    },

    async getCities(code) {
        const response = await fetch(`${API_BASE}/map/cities/${code}`);
        if (!response.ok) throw new Error(`Failed to load cities: ${code}`);
        return response.json();
    },

    async getOperations(code, activeOnly = true) {
        const url = `${API_BASE}/map/operations/${code}?active_only=${activeOnly}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Failed to load operations: ${code}`);
        return response.json();
    },

    async getMilitaryOverlay(code) {
        const response = await fetch(`${API_BASE}/map/overlay/${code}/military`);
        if (!response.ok) throw new Error(`Failed to load overlay: ${code}`);
        return response.json();
    },

    // ==================== Events ====================
    async getEvents(code) {
        const response = await fetch(`${API_BASE}/events/${code}`);
        if (!response.ok) throw new Error(`Failed to load events: ${code}`);
        return response.json();
    },

    async respondToEvent(code, eventId, responseChoice) {
        const response = await fetch(`${API_BASE}/events/${code}/respond`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId, response: responseChoice })
        });
        return response.json();
    },

    // ==================== Operations ====================
    async createOperation(code, operation) {
        const response = await fetch(`${API_BASE}/map/operations/${code}/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(operation)
        });
        return response.json();
    },

    async startOperation(code, operationId) {
        const response = await fetch(`${API_BASE}/map/operations/${code}/${operationId}/start`, {
            method: 'POST'
        });
        return response.json();
    },

    async cancelOperation(code, operationId) {
        const response = await fetch(`${API_BASE}/map/operations/${code}/${operationId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    // ==================== Unit Actions ====================
    async deployUnit(code, unitId, destination) {
        const response = await fetch(`${API_BASE}/map/units/${code}/${unitId}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                destination_lat: destination.lat,
                destination_lng: destination.lng,
                destination_name: destination.name || null
            })
        });
        return response.json();
    },

    async returnUnit(code, unitId) {
        const response = await fetch(`${API_BASE}/map/units/${code}/${unitId}/return`, {
            method: 'POST'
        });
        return response.json();
    },

    // ==================== Game Clock ====================
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

    // ==================== Budget Actions ====================
    async getBudget(code) {
        const response = await fetch(`${API_BASE}/budget/${code}`);
        if (!response.ok) throw new Error('Failed to load budget');
        return response.json();
    },

    async adjustBudget(code, data) {
        const response = await fetch(`${API_BASE}/budget/${code}/adjust`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async adjustTax(code, newRate) {
        const response = await fetch(`${API_BASE}/budget/${code}/tax`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_rate: newRate })
        });
        return response.json();
    },

    async takeDebt(code, amount) {
        const response = await fetch(`${API_BASE}/budget/${code}/debt/take`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount_billions: amount })
        });
        return response.json();
    },

    async repayDebt(code, amount) {
        const response = await fetch(`${API_BASE}/budget/${code}/debt/repay`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount_billions: amount })
        });
        return response.json();
    },

    // ==================== Sector Actions ====================
    async getSectors(code) {
        const response = await fetch(`${API_BASE}/country/${code}/sectors`);
        if (!response.ok) throw new Error('Failed to load sectors');
        return response.json();
    },

    async investInSector(code, data) {
        const response = await fetch(`${API_BASE}/sectors/${code}/invest`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async startInfrastructure(code, data) {
        const response = await fetch(`${API_BASE}/sectors/${code}/infrastructure`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async getProjects(code) {
        const response = await fetch(`${API_BASE}/sectors/${code}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');
        return response.json();
    },

    async cancelProject(code, projectId) {
        const response = await fetch(`${API_BASE}/sectors/${code}/projects/${projectId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    // ==================== Procurement Actions ====================
    async getWeaponsCatalog(category = null) {
        const url = category
            ? `${API_BASE}/procurement/catalog?category=${category}`
            : `${API_BASE}/procurement/catalog`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to load weapons catalog');
        return response.json();
    },

    async getProcurementOrders(code) {
        const response = await fetch(`${API_BASE}/procurement/${code}/orders`);
        if (!response.ok) throw new Error('Failed to load procurement orders');
        return response.json();
    },

    async checkPurchase(code, data) {
        const response = await fetch(`${API_BASE}/procurement/${code}/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async purchaseWeapon(code, data) {
        const response = await fetch(`${API_BASE}/procurement/${code}/purchase`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async sellWeapon(code, data) {
        const response = await fetch(`${API_BASE}/procurement/${code}/sell`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async cancelProcurementOrder(code, orderId) {
        const response = await fetch(`${API_BASE}/procurement/${code}/orders/${orderId}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    // ==================== Military Operations ====================
    async getOperationTypes() {
        const response = await fetch(`${API_BASE}/operations/types`);
        if (!response.ok) throw new Error('Failed to load operation types');
        return response.json();
    },

    async planOperation(code, data) {
        const response = await fetch(`${API_BASE}/operations/${code}/plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async executeOperation(code, data) {
        const response = await fetch(`${API_BASE}/operations/${code}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async setReadiness(code, level) {
        const response = await fetch(`${API_BASE}/operations/${code}/readiness?level=${level}`, {
            method: 'POST'
        });
        return response.json();
    },

    // ==================== Border Deployments ====================
    async getDeployments(code) {
        const response = await fetch(`${API_BASE}/military/deployments/${code}`);
        if (!response.ok) throw new Error('Failed to load deployments');
        return response.json();
    },

    async getDeploymentZone(code, zoneId) {
        const response = await fetch(`${API_BASE}/military/deployments/${code}/${zoneId}`);
        if (!response.ok) throw new Error('Failed to load deployment zone');
        return response.json();
    },

    async deployTroops(code, zoneId, activeTroops, reserveTroops) {
        const response = await fetch(`${API_BASE}/military/deployments/${code}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                zone_id: zoneId,
                active_troops: activeTroops,
                reserve_troops: reserveTroops
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to deploy troops');
        return data;
    },

    async withdrawTroops(code, zoneId, activeTroops, reserveTroops) {
        const response = await fetch(`${API_BASE}/military/deployments/${code}/withdraw`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                zone_id: zoneId,
                active_troops: activeTroops,
                reserve_troops: reserveTroops
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to withdraw troops');
        return data;
    },

    async setZoneAlertLevel(code, zoneId, alertLevel) {
        const response = await fetch(`${API_BASE}/military/deployments/${code}/alert`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                zone_id: zoneId,
                alert_level: alertLevel
            })
        });
        return response.json();
    },

    // ==================== Reserve Management ====================
    async callupReserves(code, count, zoneId = null) {
        const response = await fetch(`${API_BASE}/military/reserves/${code}/callup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                count: count,
                zone_id: zoneId
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to call up reserves');
        return data;
    },

    async standDownReserves(code, count) {
        const response = await fetch(`${API_BASE}/military/reserves/${code}/stand-down`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count: count })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to stand down reserves');
        return data;
    },

    async getPersonnelStatus(code) {
        const response = await fetch(`${API_BASE}/military/personnel/${code}`);
        if (!response.ok) throw new Error('Failed to load personnel status');
        return response.json();
    },

    // ==================== Save/Load ====================
    async listSaves() {
        const response = await fetch(`${API_BASE}/saves`);
        if (!response.ok) throw new Error('Failed to list saves');
        return response.json();
    },

    async getSaveDetails(slot) {
        const response = await fetch(`${API_BASE}/saves/${slot}`);
        if (!response.ok) throw new Error('Failed to get save details');
        return response.json();
    },

    async saveGame(code, data) {
        const response = await fetch(`${API_BASE}/saves/${code}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async loadGame(slot) {
        const response = await fetch(`${API_BASE}/saves/load/${slot}`, {
            method: 'POST'
        });
        return response.json();
    },

    async deleteSave(slot) {
        const response = await fetch(`${API_BASE}/saves/${slot}`, {
            method: 'DELETE'
        });
        return response.json();
    },

    async quickSave(code) {
        const response = await fetch(`${API_BASE}/saves/${code}/quick`, {
            method: 'POST'
        });
        return response.json();
    },

    async quickLoad() {
        const response = await fetch(`${API_BASE}/saves/quickload`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: '{}'
        });
        return response.json();
    }
};
