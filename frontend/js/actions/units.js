// Unit Actions
const UnitActions = {
    selectedUnit: null,

    showUnitActions(unitId) {
        const unit = UnitsPanel.getUnit ? UnitsPanel.getUnit(unitId) : null;

        if (!unit) {
            console.error('Unit not found:', unitId);
            return;
        }

        const canDeploy = unit.status === 'idle';
        const canReturn = unit.status === 'deployed' || unit.status === 'moving';

        Modal.show({
            title: unit.name || 'Unit Details',
            content: this.renderUnitDetails(unit),
            buttons: [
                {
                    label: 'Deploy',
                    primary: true,
                    disabled: !canDeploy,
                    onClick: () => this.startDeploy(unit)
                },
                {
                    label: 'Return to Base',
                    disabled: !canReturn,
                    onClick: () => this.returnToBase(unit)
                },
                { label: 'Close', onClick: () => Modal.close() }
            ]
        });
    },

    renderUnitDetails(unit) {
        const statusClass = this.getStatusClass(unit.status);

        return `
            <div class="unit-details">
                <div class="unit-detail-row">
                    <span class="unit-detail-label">Type:</span>
                    <span class="unit-detail-value">${unit.unit_type || 'Unknown'}</span>
                </div>
                <div class="unit-detail-row">
                    <span class="unit-detail-label">Category:</span>
                    <span class="unit-detail-value">${unit.category || 'Unknown'}</span>
                </div>
                <div class="unit-detail-row">
                    <span class="unit-detail-label">Status:</span>
                    <span class="unit-detail-value status-badge ${statusClass}">${unit.status || 'Unknown'}</span>
                </div>
                <div class="unit-detail-row">
                    <span class="unit-detail-label">Quantity:</span>
                    <span class="unit-detail-value">${unit.quantity || 1}</span>
                </div>
                ${unit.home_base_id ? `
                    <div class="unit-detail-row">
                        <span class="unit-detail-label">Home Base:</span>
                        <span class="unit-detail-value">${unit.home_base_id}</span>
                    </div>
                ` : ''}
                ${unit.location ? `
                    <div class="unit-detail-row">
                        <span class="unit-detail-label">Location:</span>
                        <span class="unit-detail-value">${unit.location.lat?.toFixed(4)}, ${unit.location.lng?.toFixed(4)}</span>
                    </div>
                ` : ''}

                <div class="unit-stats">
                    <div class="unit-stat">
                        <div class="unit-stat-label">Health</div>
                        <div class="unit-stat-bar">
                            <div class="unit-stat-fill health" style="width: ${unit.health_percent || 100}%"></div>
                        </div>
                        <div class="unit-stat-value">${(unit.health_percent || 100).toFixed(0)}%</div>
                    </div>
                    <div class="unit-stat">
                        <div class="unit-stat-label">Readiness</div>
                        <div class="unit-stat-bar">
                            <div class="unit-stat-fill readiness" style="width: ${unit.readiness_percent || 100}%"></div>
                        </div>
                        <div class="unit-stat-value">${(unit.readiness_percent || 100).toFixed(0)}%</div>
                    </div>
                    ${unit.fuel_percent !== undefined ? `
                        <div class="unit-stat">
                            <div class="unit-stat-label">Fuel</div>
                            <div class="unit-stat-bar">
                                <div class="unit-stat-fill fuel" style="width: ${unit.fuel_percent}%"></div>
                            </div>
                            <div class="unit-stat-value">${unit.fuel_percent.toFixed(0)}%</div>
                        </div>
                    ` : ''}
                    ${unit.ammo_percent !== undefined ? `
                        <div class="unit-stat">
                            <div class="unit-stat-label">Ammo</div>
                            <div class="unit-stat-bar">
                                <div class="unit-stat-fill ammo" style="width: ${unit.ammo_percent}%"></div>
                            </div>
                            <div class="unit-stat-value">${unit.ammo_percent.toFixed(0)}%</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    },

    getStatusClass(status) {
        switch (status) {
            case 'idle': return 'status-idle';
            case 'deployed': return 'status-deployed';
            case 'moving': return 'status-moving';
            case 'engaged': return 'status-engaged';
            case 'returning': return 'status-returning';
            default: return '';
        }
    },

    startDeploy(unit) {
        this.selectedUnit = unit;
        Modal.close();

        App.showNotification('Click on the map to select deployment location', 'info');

        MapSelector.start(`Deploy ${unit.name}`, async (location) => {
            if (location) {
                await this.deployToLocation(unit, location);
            }
            this.selectedUnit = null;
        });
    },

    async deployToLocation(unit, location) {
        try {
            const result = await api.deployUnit(App.countryCode, unit.id, {
                lat: location.lat,
                lng: location.lng,
                name: location.name
            });

            if (result.success !== false) {
                App.showNotification(`${unit.name} deploying to ${location.name || 'target location'}`, 'success');
                UnitsPanel.load && UnitsPanel.load(App.countryCode);
                if (App.map) App.map.refresh();
            } else {
                Modal.showResult('Deployment Failed', result.error || 'Could not deploy unit', false);
            }
        } catch (error) {
            Modal.showResult('Error', error.message, false);
        }
    },

    async returnToBase(unit) {
        Modal.confirm(`Return ${unit.name} to base?`, async () => {
            try {
                const result = await api.returnUnit(App.countryCode, unit.id);

                if (result.success !== false) {
                    App.showNotification(`${unit.name} returning to base`, 'success');
                    UnitsPanel.load && UnitsPanel.load(App.countryCode);
                    if (App.map) App.map.refresh();
                } else {
                    Modal.showResult('Failed', result.error || 'Could not return unit', false);
                }
            } catch (error) {
                Modal.showResult('Error', error.message, false);
            }
        });
    }
};
