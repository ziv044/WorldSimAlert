// Leaflet Map integration for Command Center
class CommandMap {
    constructor(containerId, countryCode) {
        this.containerId = containerId;
        this.countryCode = countryCode;
        this.map = null;
        this.markers = {
            units: new Map(),
            bases: new Map(),
            operations: new Map(),
            deployments: new Map()
        };

        // Israel default center
        this.defaultCenter = [31.5, 34.75];
        this.defaultZoom = 8;

        // Tile layers
        this.layers = {
            terrain: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors',
                maxZoom: 18
            }),
            satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '&copy; Esri',
                maxZoom: 18
            })
        };

        this.currentLayer = 'terrain';

        // Custom icons
        this.icons = this.createIcons();
    }

    createIcons() {
        const createIcon = (color, symbol) => {
            return L.divIcon({
                className: 'custom-marker',
                html: `<div style="
                    background: ${color};
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    border: 2px solid #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                ">${symbol}</div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                popupAnchor: [0, -12]
            });
        };

        return {
            aircraft: createIcon('#00ff88', '✈'),
            helicopter: createIcon('#00ff88', '🚁'),
            ground: createIcon('#ffcc00', '🛡'),
            naval: createIcon('#00aaff', '🚢'),
            air_defense: createIcon('#ff8800', '🎯'),
            missile: createIcon('#ff4444', '🚀'),
            special_ops: createIcon('#aa00ff', '👤'),
            base_air: createIcon('#00dddd', '✦'),
            base_naval: createIcon('#00aaff', '⚓'),
            base_army: createIcon('#ffcc00', '★'),
            base_default: createIcon('#00dddd', '◆'),
            operation: createIcon('#ff4444', '⚔')
        };
    }

    async init() {
        // Create map
        this.map = L.map(this.containerId, {
            center: this.defaultCenter,
            zoom: this.defaultZoom,
            zoomControl: true
        });

        // Add default layer
        this.layers.terrain.addTo(this.map);

        // Setup layer controls
        this.setupLayerControls();

        // Load initial data
        await this.loadMapData();

        console.log('Map initialized');
    }

    setupLayerControls() {
        document.querySelectorAll('.map-control-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const layer = btn.dataset.layer;
                this.switchLayer(layer);

                // Update button states
                document.querySelectorAll('.map-control-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    switchLayer(layerName) {
        if (this.currentLayer === layerName) return;

        // Remove current layer
        this.map.removeLayer(this.layers[this.currentLayer]);

        // Add new layer
        this.layers[layerName].addTo(this.map);
        this.currentLayer = layerName;
    }

    async loadMapData() {
        try {
            const [unitsData, basesData, operationsData] = await Promise.all([
                api.getUnits(this.countryCode).catch(() => ({ units: [] })),
                api.getBases(this.countryCode).catch(() => ({ bases: [] })),
                api.getOperations(this.countryCode).catch(() => ({ operations: [] }))
            ]);

            this.renderBases(basesData.bases || []);
            this.renderUnits(unitsData.units || []);
            this.renderOperations(operationsData.operations || []);
        } catch (error) {
            console.error('Failed to load map data:', error);
        }
    }

    renderUnits(units) {
        // Clear existing markers
        this.markers.units.forEach(marker => this.map.removeLayer(marker));
        this.markers.units.clear();

        units.forEach(unit => {
            if (!unit.location) return;

            const icon = this.getUnitIcon(unit.category);
            const marker = L.marker([unit.location.lat, unit.location.lng], { icon })
                .addTo(this.map)
                .bindPopup(this.createUnitPopup(unit));

            this.markers.units.set(unit.id, marker);
        });
    }

    renderBases(bases) {
        this.markers.bases.forEach(marker => this.map.removeLayer(marker));
        this.markers.bases.clear();

        bases.forEach(base => {
            if (!base.location) return;

            const icon = this.getBaseIcon(base.base_type);
            const marker = L.marker([base.location.lat, base.location.lng], { icon })
                .addTo(this.map)
                .bindPopup(this.createBasePopup(base));

            this.markers.bases.set(base.id, marker);
        });
    }

    renderOperations(operations) {
        this.markers.operations.forEach(marker => this.map.removeLayer(marker));
        this.markers.operations.clear();

        operations.forEach(op => {
            if (!op.target_location) return;

            const marker = L.marker(
                [op.target_location.lat, op.target_location.lng],
                { icon: this.icons.operation }
            )
                .addTo(this.map)
                .bindPopup(this.createOperationPopup(op));

            // Add pulsing effect for active operations
            if (op.status === 'active') {
                const circle = L.circle([op.target_location.lat, op.target_location.lng], {
                    color: '#ff4444',
                    fillColor: '#ff4444',
                    fillOpacity: 0.2,
                    radius: 5000
                }).addTo(this.map);

                // Store circle with marker for cleanup
                marker._operationCircle = circle;
            }

            this.markers.operations.set(op.id, marker);
        });
    }

    getUnitIcon(category) {
        return this.icons[category] || this.icons.ground;
    }

    getBaseIcon(baseType) {
        if (baseType === 'air_base') return this.icons.base_air;
        if (baseType === 'naval_base') return this.icons.base_naval;
        if (baseType === 'army_base') return this.icons.base_army;
        return this.icons.base_default;
    }

    createUnitPopup(unit) {
        return `
            <h3>${unit.name}</h3>
            <p><strong>Type:</strong> ${unit.unit_type}</p>
            <p><strong>Status:</strong> ${unit.status}</p>
            <p><strong>Health:</strong> ${unit.health_percent}%</p>
            <p><strong>Quantity:</strong> ${unit.quantity}</p>
        `;
    }

    createBasePopup(base) {
        return `
            <h3>${base.name}</h3>
            <p><strong>Type:</strong> ${base.base_type.replace('_', ' ')}</p>
            <p><strong>Status:</strong> ${base.status}</p>
            <p><strong>Readiness:</strong> ${base.readiness_percent}%</p>
        `;
    }

    createOperationPopup(op) {
        return `
            <h3>${op.name}</h3>
            <p><strong>Type:</strong> ${op.operation_type.replace(/_/g, ' ')}</p>
            <p><strong>Status:</strong> ${op.status}</p>
            <p><strong>Progress:</strong> ${op.progress_percent.toFixed(0)}%</p>
            ${op.target_name ? `<p><strong>Target:</strong> ${op.target_name}</p>` : ''}
        `;
    }

    // Real-time update methods
    updateUnit(unitData) {
        const marker = this.markers.units.get(unitData.unit_id);
        if (marker && unitData.location) {
            marker.setLatLng([unitData.location.lat, unitData.location.lng]);
        }
    }

    updateOperation(opData) {
        // Reload operations for now
        // Could be optimized to update single operation
        api.getOperations(this.countryCode).then(data => {
            this.renderOperations(data.operations || []);
        });
    }

    centerOn(lat, lng, zoom = null) {
        this.map.setView([lat, lng], zoom || this.map.getZoom());
    }

    refresh() {
        this.loadMapData();
    }

    // ==================== Border Deployments ====================

    /**
     * Render deployment zone markers on the map
     * @param {Array} zones - Array of deployment zone data
     */
    renderDeploymentMarkers(zones) {
        // Clear existing deployment markers
        this.markers.deployments.forEach(marker => this.map.removeLayer(marker));
        this.markers.deployments.clear();

        zones.forEach(zone => {
            if (!zone.center) return;

            const marker = this.createDeploymentMarker(zone);
            marker.addTo(this.map);
            this.markers.deployments.set(zone.id, marker);
        });
    }

    /**
     * Create a deployment marker with troop count
     * @param {Object} zone - Deployment zone data
     * @returns {L.marker} Leaflet marker
     */
    createDeploymentMarker(zone) {
        const totalTroops = zone.active_troops + zone.reserve_troops;
        const displayCount = this.formatTroopCount(totalTroops);
        const color = this.getZoneColor(zone);
        const alertClass = zone.alert_level.replace('_', '-');

        const icon = L.divIcon({
            className: 'deployment-marker',
            html: `
                <div class="deployment-marker-inner ${alertClass}" style="border-color: ${color}">
                    <div class="troop-count">${displayCount}</div>
                    <div class="zone-name">${this.getShortZoneName(zone.name)}</div>
                </div>
            `,
            iconSize: [90, 44],
            iconAnchor: [45, 22],
            popupAnchor: [0, -22]
        });

        const marker = L.marker([zone.center.lat, zone.center.lng], { icon });
        marker.bindPopup(this.createDeploymentPopup(zone));
        marker._zoneId = zone.id;

        return marker;
    }

    /**
     * Update a single deployment marker
     * @param {string} zoneId - Zone ID
     * @param {Object} data - Updated zone data
     */
    updateDeploymentMarker(zoneId, data) {
        const marker = this.markers.deployments.get(zoneId);
        if (marker) {
            // Remove old marker and create new one with updated data
            this.map.removeLayer(marker);
            const newMarker = this.createDeploymentMarker(data);
            newMarker.addTo(this.map);
            this.markers.deployments.set(zoneId, newMarker);

            // Flash animation for attention
            if (window.AnimationManager) {
                const markerEl = newMarker.getElement();
                if (markerEl) {
                    AnimationManager.flashAnimation(markerEl, '#00ffff', 500);
                }
            }
        }
    }

    /**
     * Get color based on threat level
     * @param {Object} zone - Deployment zone
     * @returns {string} CSS color
     */
    getZoneColor(zone) {
        const threat = zone.threat_level || 0;
        if (threat >= 75) return '#ff4444';  // High threat - red
        if (threat >= 50) return '#ff8800';  // Medium - orange
        if (threat >= 25) return '#ffcc00';  // Low - yellow
        return '#00ff88';  // Peaceful - green
    }

    /**
     * Format troop count for display
     * @param {number} count - Number of troops
     * @returns {string} Formatted string
     */
    formatTroopCount(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        }
        if (count >= 1000) {
            return Math.floor(count / 1000) + 'K';
        }
        return count.toString();
    }

    /**
     * Get short version of zone name
     * @param {string} name - Full zone name
     * @returns {string} Short name
     */
    getShortZoneName(name) {
        // Extract just the region name (e.g., "Northern Front - Lebanon" -> "Northern")
        const parts = name.split(' - ');
        if (parts.length > 1) {
            return parts[0].split(' ')[0];  // First word of first part
        }
        return name.substring(0, 10);
    }

    /**
     * Create popup content for deployment zone
     * @param {Object} zone - Deployment zone data
     * @returns {string} HTML content
     */
    createDeploymentPopup(zone) {
        const totalTroops = zone.active_troops + zone.reserve_troops;
        const alertDisplay = zone.alert_level.replace(/_/g, ' ').toUpperCase();

        let equipmentHtml = '';
        if (zone.equipment_summary && Object.keys(zone.equipment_summary).length > 0) {
            const items = Object.entries(zone.equipment_summary)
                .map(([type, count]) => `${count} ${type}`)
                .join(', ');
            equipmentHtml = `<p><strong>Equipment:</strong> ${items}</p>`;
        }

        return `
            <div class="deployment-popup">
                <h3>${zone.name}</h3>
                <div class="popup-stats">
                    <p><strong>Active Troops:</strong> ${zone.active_troops.toLocaleString()}</p>
                    <p><strong>Reserves:</strong> ${zone.reserve_troops.toLocaleString()}</p>
                    <p><strong>Total:</strong> ${totalTroops.toLocaleString()}</p>
                    ${equipmentHtml}
                    <p><strong>Alert Level:</strong> <span class="alert-${zone.alert_level}">${alertDisplay}</span></p>
                    <p><strong>Threat Level:</strong> ${zone.threat_level}%</p>
                    <p><strong>Readiness:</strong> ${zone.readiness_percent}%</p>
                </div>
                <button class="btn btn-sm btn-primary" onclick="MilitaryPanel.showDeployModal('${zone.id}')">
                    Manage Deployment
                </button>
            </div>
        `;
    }

    /**
     * Load deployment data from API
     */
    async loadDeployments() {
        try {
            const data = await api.getDeployments(this.countryCode);
            if (data && data.zones) {
                this.renderDeploymentMarkers(data.zones);
            }
        } catch (error) {
            console.error('Failed to load deployments:', error);
        }
    }
}

// Global map instance
let commandMap = null;

function initMap(containerId, countryCode) {
    commandMap = new CommandMap(containerId, countryCode);
    return commandMap.init().then(() => commandMap);
}

function getMap() {
    return commandMap;
}
