/**
 * Military Panel Component - Border Deployments and Personnel Management
 * Replaces the simple units list with comprehensive deployment view
 */
const MilitaryPanel = {
    container: null,
    deploymentsData: null,
    personnelData: null,
    countryCode: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    async load(countryCode) {
        this.countryCode = countryCode;
        try {
            // Load deployments and personnel in parallel
            const [deployments, personnel] = await Promise.all([
                api.getDeployments(countryCode),
                api.getPersonnelStatus(countryCode)
            ]);

            this.deploymentsData = deployments;
            this.personnelData = personnel;
            this.render();
        } catch (error) {
            console.error('Failed to load military data:', error);
            this.container.innerHTML = '<div class="error">Failed to load military data</div>';
        }
    },

    render() {
        if (!this.container) return;

        const zones = this.deploymentsData?.zones || [];
        const personnel = this.personnelData || {};

        // Sort zones by threat level (high to low)
        const sortedZones = [...zones].sort((a, b) => b.threat_level - a.threat_level);

        this.container.innerHTML = `
            ${this.renderPersonnelSummary(personnel)}
            <div class="deployment-zones-list">
                ${sortedZones.length > 0
                    ? sortedZones.map(zone => this.renderZone(zone)).join('')
                    : '<div class="empty-state">No deployment zones</div>'
                }
            </div>
        `;

        // Add click handlers for zones
        this.container.querySelectorAll('.deployment-zone-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    const zoneId = item.dataset.zoneId;
                    this.focusZoneOnMap(zoneId);
                }
            });
        });
    },

    renderPersonnelSummary(personnel) {
        const active = personnel.active_duty || {};
        const reserves = personnel.reserves || {};
        const border = personnel.border_summary || {};

        return `
            <div class="military-summary">
                <div class="military-summary-row">
                    <span class="military-summary-label">Active Duty</span>
                    <span class="military-summary-value">${(active.total || 0).toLocaleString()}</span>
                </div>
                <div class="military-summary-row">
                    <span class="military-summary-label">At Borders</span>
                    <span class="military-summary-value">${(active.deployed_to_borders || 0).toLocaleString()}</span>
                </div>
                <div class="military-summary-row">
                    <span class="military-summary-label">Reserves Called</span>
                    <span class="military-summary-value">${(reserves.called || 0).toLocaleString()}</span>
                </div>
                <div class="military-actions">
                    <button class="btn btn-sm btn-secondary" onclick="MilitaryPanel.showReservesModal()">
                        Manage Reserves
                    </button>
                </div>
            </div>
        `;
    },

    renderZone(zone) {
        const totalTroops = zone.active_troops + zone.reserve_troops;
        const threatClass = zone.threat_level >= 70 ? 'threat-high' :
                           zone.threat_level >= 40 ? 'threat-medium' : '';
        const alertDisplay = zone.alert_level.replace(/_/g, ' ');

        return `
            <div class="deployment-zone-item ${threatClass}" data-zone-id="${zone.id}">
                <div class="zone-header">
                    <div class="zone-title">
                        <span class="threat-indicator ${this.getThreatClass(zone.threat_level)}"></span>
                        ${this.getShortZoneName(zone.name)}
                    </div>
                    <div class="zone-troops">${this.formatTroopCount(totalTroops)}</div>
                </div>
                <div class="zone-details">
                    <span class="zone-neighbor">${zone.neighbor_code}</span>
                    <span class="zone-alert alert-${zone.alert_level}">${alertDisplay}</span>
                </div>
            </div>
        `;
    },

    getThreatClass(threat) {
        if (threat >= 70) return 'high';
        if (threat >= 40) return 'medium';
        return 'low';
    },

    getShortZoneName(name) {
        const parts = name.split(' - ');
        return parts[0];
    },

    formatTroopCount(count) {
        if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M';
        if (count >= 1000) return Math.floor(count / 1000) + 'K';
        return count.toString();
    },

    focusZoneOnMap(zoneId) {
        const zone = this.deploymentsData?.zones?.find(z => z.id === zoneId);
        if (zone && zone.center && window.commandMap) {
            commandMap.centerOn(zone.center.lat, zone.center.lng, 10);

            // Open the popup for this zone
            const marker = commandMap.markers.deployments.get(zoneId);
            if (marker) {
                marker.openPopup();
            }
        }
    },

    // ==================== Modals ====================

    showDeployModal(zoneId) {
        const zone = this.deploymentsData?.zones?.find(z => z.id === zoneId);
        if (!zone) return;

        const personnel = this.personnelData || {};
        const active = personnel.active_duty || {};
        const reserves = personnel.reserves || {};

        const availableActive = active.available || 0;
        const availableReserves = reserves.available_to_deploy || 0;

        const self = this;

        Modal.show({
            title: `Deploy to ${zone.name}`,
            content: `
                <div class="form-group">
                    <label>Current Deployment</label>
                    <p>Active: ${zone.active_troops.toLocaleString()} | Reserves: ${zone.reserve_troops.toLocaleString()}</p>
                </div>
                <div class="form-group">
                    <label for="deploy-active">Deploy Active Troops (Available: ${availableActive.toLocaleString()})</label>
                    <input type="range" id="deploy-active" min="0" max="${Math.min(availableActive, 10000)}" value="0" step="100">
                    <span id="deploy-active-value">0</span>
                </div>
                <div class="form-group">
                    <label for="deploy-reserves">Deploy Reserves (Available: ${availableReserves.toLocaleString()})</label>
                    <input type="range" id="deploy-reserves" min="0" max="${Math.min(availableReserves, 10000)}" value="0" step="100">
                    <span id="deploy-reserves-value">0</span>
                </div>
            `,
            buttons: [
                {
                    label: 'Cancel',
                    onClick: () => Modal.close()
                },
                {
                    label: 'Deploy',
                    primary: true,
                    onClick: async () => {
                        const activeTroops = parseInt(document.getElementById('deploy-active').value);
                        const reserveTroops = parseInt(document.getElementById('deploy-reserves').value);

                        if (activeTroops === 0 && reserveTroops === 0) {
                            Modal.close();
                            return;
                        }

                        try {
                            await api.deployTroops(self.countryCode, zoneId, activeTroops, reserveTroops);
                            Modal.close();
                            App.showNotification('Troops deployed successfully', 'success');
                            self.load(self.countryCode);
                            if (window.commandMap) {
                                commandMap.loadDeployments();
                            }
                        } catch (error) {
                            App.showNotification('Failed to deploy troops: ' + error.message, 'failure');
                        }
                    }
                }
            ]
        });

        // Setup range input handlers after modal is rendered
        setTimeout(() => {
            const activeInput = document.getElementById('deploy-active');
            const reserveInput = document.getElementById('deploy-reserves');

            activeInput?.addEventListener('input', (e) => {
                document.getElementById('deploy-active-value').textContent =
                    parseInt(e.target.value).toLocaleString();
            });

            reserveInput?.addEventListener('input', (e) => {
                document.getElementById('deploy-reserves-value').textContent =
                    parseInt(e.target.value).toLocaleString();
            });
        }, 0);
    },

    showReservesModal() {
        const personnel = this.personnelData || {};
        const reserves = personnel.reserves || {};

        const totalReserves = reserves.total || 0;
        const called = reserves.called || 0;
        const availableToCall = reserves.available_to_call || 0;

        const self = this;

        Modal.show({
            title: 'Manage Reserves',
            content: `
                <div class="form-group">
                    <label>Reserve Status</label>
                    <p>Total Reserves: ${totalReserves.toLocaleString()}</p>
                    <p>Currently Called: ${called.toLocaleString()}</p>
                    <p>Available to Call: ${availableToCall.toLocaleString()}</p>
                </div>
                <div class="form-group">
                    <label for="callup-count">Call Up Reserves</label>
                    <input type="range" id="callup-count" min="0" max="${Math.min(availableToCall, 50000)}" value="0" step="1000">
                    <span id="callup-value">0</span>
                </div>
                <hr>
                <div class="form-group">
                    <label for="standdown-count">Stand Down Reserves</label>
                    <input type="range" id="standdown-count" min="0" max="${called}" value="0" step="1000">
                    <span id="standdown-value">0</span>
                </div>
            `,
            buttons: [
                {
                    label: 'Cancel',
                    onClick: () => Modal.close()
                },
                {
                    label: 'Call Up',
                    primary: true,
                    onClick: async () => {
                        const count = parseInt(document.getElementById('callup-count').value);
                        if (count > 0) {
                            try {
                                await api.callupReserves(self.countryCode, count);
                                Modal.close();
                                App.showNotification(`${count.toLocaleString()} reserves called up`, 'success');
                                self.load(self.countryCode);
                            } catch (error) {
                                App.showNotification('Failed to call up reserves: ' + error.message, 'failure');
                            }
                        } else {
                            Modal.close();
                        }
                    }
                },
                {
                    label: 'Stand Down',
                    onClick: async () => {
                        const count = parseInt(document.getElementById('standdown-count').value);
                        if (count > 0) {
                            try {
                                await api.standDownReserves(self.countryCode, count);
                                Modal.close();
                                App.showNotification(`${count.toLocaleString()} reserves stood down`, 'success');
                                self.load(self.countryCode);
                            } catch (error) {
                                App.showNotification('Failed to stand down reserves: ' + error.message, 'failure');
                            }
                        } else {
                            Modal.close();
                        }
                    }
                }
            ]
        });

        // Setup range input handlers after modal is rendered
        setTimeout(() => {
            const callupInput = document.getElementById('callup-count');
            const standdownInput = document.getElementById('standdown-count');

            callupInput?.addEventListener('input', (e) => {
                document.getElementById('callup-value').textContent =
                    parseInt(e.target.value).toLocaleString();
            });

            standdownInput?.addEventListener('input', (e) => {
                document.getElementById('standdown-value').textContent =
                    parseInt(e.target.value).toLocaleString();
            });
        }, 0);
    },

    // ==================== WebSocket Updates ====================

    updateFromWebSocket(data) {
        // Handle deployment_updated events
        if (data.zone_id && this.deploymentsData) {
            const zone = this.deploymentsData.zones?.find(z => z.id === data.zone_id);
            if (zone) {
                zone.active_troops = data.active_troops;
                zone.reserve_troops = data.reserve_troops;
                zone.alert_level = data.alert_level;
                this.render();
            }
        }
    },

    updateZone(data) {
        this.updateFromWebSocket(data);
    },

    // ==================== Compatibility Methods ====================
    // Keep these for backward compatibility with existing code

    updateUnit(unitData) {
        // Reload on unit changes
        if (this.countryCode) {
            this.load(this.countryCode);
        }
    },

    getUnitCount() {
        return this.deploymentsData?.total_active_deployed || 0;
    }
};

// Alias for backward compatibility
const UnitsPanel = MilitaryPanel;
