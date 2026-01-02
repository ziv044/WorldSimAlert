// Operation Actions
const OperationActions = {
    operationTypes: null,

    async loadOperationTypes() {
        if (!this.operationTypes) {
            const result = await api.getOperationTypes();
            this.operationTypes = result.types || [];
        }
        return this.operationTypes;
    },

    getOperationOptions() {
        if (!this.operationTypes) return [];
        return this.operationTypes.map(type => ({
            value: type,
            label: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        }));
    },

    readinessLevels: [
        { value: 'low', label: 'Low (70% cost, slower response)' },
        { value: 'normal', label: 'Normal (100% cost, standard response)' },
        { value: 'high', label: 'High (150% cost, fast response)' },
        { value: 'maximum', label: 'Maximum (200% cost, immediate response)' }
    ],

    async showPlanOperation() {
        Modal.showLoading('Loading operation types...');

        try {
            await this.loadOperationTypes();
            Modal.close();

            Modal.showForm({
                title: 'Plan Military Operation',
                size: 'large',
                fields: [
                    {
                        name: 'operation_type',
                        type: 'select',
                        label: 'Operation Type',
                        options: this.getOperationOptions()
                    },
                    {
                        name: 'target_country',
                        type: 'text',
                        label: 'Target Country Code',
                        placeholder: 'e.g., IRN, SYR, LBN'
                    },
                    {
                        name: 'target_description',
                        type: 'text',
                        label: 'Target Description',
                        placeholder: 'e.g., Military base, Nuclear facility'
                    }
                ],
                buttons: [
                    { label: 'Cancel', onClick: () => Modal.close() },
                    {
                        label: 'Plan Only',
                        onClick: async () => {
                            const form = document.getElementById(Modal.activeModal?.querySelector('form')?.id);
                            if (form) {
                                const data = Modal.getFormData(form, [
                                    { name: 'operation_type' },
                                    { name: 'target_country' },
                                    { name: 'target_description' }
                                ]);
                                await this.planOperation(data);
                            }
                        }
                    },
                    {
                        label: 'Execute',
                        primary: true,
                        onClick: async () => {
                            const form = Modal.activeModal?.querySelector('form');
                            if (form) {
                                const data = Modal.getFormData(form, [
                                    { name: 'operation_type' },
                                    { name: 'target_country' },
                                    { name: 'target_description' }
                                ]);
                                await this.executeOp(data);
                            }
                        }
                    }
                ],
                onSubmit: async (data) => {
                    await this.executeOp(data);
                }
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load operation types: ' + error.message, false);
        }
    },

    async planOperation(data) {
        try {
            const result = await api.planOperation(App.countryCode, data);
            Modal.close();

            if (result.feasible !== false) {
                Modal.show({
                    title: 'Operation Plan',
                    content: `
                        <div class="plan-result">
                            <p class="result-success">Operation is feasible</p>
                            <div class="plan-details">
                                <p><strong>Type:</strong> ${data.operation_type}</p>
                                <p><strong>Target:</strong> ${data.target_description} (${data.target_country})</p>
                                ${result.estimated_duration ? `<p><strong>Est. Duration:</strong> ${result.estimated_duration}</p>` : ''}
                                ${result.success_probability ? `<p><strong>Success Probability:</strong> ${(result.success_probability * 100).toFixed(0)}%</p>` : ''}
                                ${result.requirements ? `<p><strong>Requirements:</strong> ${JSON.stringify(result.requirements)}</p>` : ''}
                            </div>
                        </div>
                    `,
                    buttons: [
                        { label: 'Close', onClick: () => Modal.close() },
                        { label: 'Execute Now', primary: true, onClick: () => this.executeOp(data) }
                    ]
                });
            } else {
                Modal.showResult('Plan Failed', result.reason || 'Operation not feasible', false);
            }
        } catch (error) {
            Modal.showResult('Error', error.message, false);
        }
    },

    async executeOp(data) {
        try {
            const result = await api.executeOperation(App.countryCode, data);
            Modal.close();

            if (result.success !== false) {
                App.showNotification(`Operation ${data.operation_type} launched`, 'success');
                OperationsPanel.load && OperationsPanel.load(App.countryCode);
            } else {
                Modal.showResult('Execution Failed', result.reason || result.error || 'Operation failed', false);
            }
        } catch (error) {
            Modal.showResult('Error', error.message, false);
        }
    },

    async showCreateMapOperation() {
        // This is a multi-step wizard that uses map selection

        await this.loadOperationTypes();

        // Step 1: Select operation type and name
        Modal.showForm({
            title: 'Create Map Operation - Step 1',
            fields: [
                {
                    name: 'name',
                    type: 'text',
                    label: 'Operation Name',
                    placeholder: 'e.g., Operation Thunder'
                },
                {
                    name: 'operation_type',
                    type: 'select',
                    label: 'Operation Type',
                    options: this.getOperationOptions()
                },
                {
                    name: 'duration_hours',
                    type: 'number',
                    label: 'Duration (hours)',
                    min: 1,
                    max: 720,
                    step: 1,
                    defaultValue: 24
                },
                {
                    name: 'is_covert',
                    type: 'checkbox',
                    label: 'Covert Operation',
                    defaultValue: false
                }
            ],
            submitLabel: 'Next: Select Location',
            onSubmit: async (data) => {
                // Store data and move to location selection
                this.pendingOperation = data;
                Modal.close();

                App.showNotification('Click on the map to select target location', 'info');

                MapSelector.start('Click to select operation target', (location) => {
                    if (location) {
                        this.pendingOperation.target_lat = location.lat;
                        this.pendingOperation.target_lng = location.lng;
                        this.pendingOperation.target_name = location.name;
                        this.showUnitSelection();
                    }
                });
            }
        });
    },

    pendingOperation: null,

    async showUnitSelection() {
        // Step 2: Select units to assign
        const unitsResult = await api.getUnits(App.countryCode);
        const units = (unitsResult.units || []).filter(u => u.status === 'idle');

        if (units.length === 0) {
            Modal.show({
                title: 'No Available Units',
                content: '<p>No idle units available for this operation.</p>',
                buttons: [
                    { label: 'Cancel', onClick: () => { this.pendingOperation = null; Modal.close(); } }
                ]
            });
            return;
        }

        const unitOptions = units.map(u => ({
            id: u.id,
            name: `${u.name} (${u.unit_type})`,
            status: u.status,
            disabled: u.status !== 'idle'
        }));

        Modal.showForm({
            title: 'Create Map Operation - Step 2',
            fields: [
                {
                    name: 'unit_ids',
                    type: 'unit-select',
                    label: 'Assign Units',
                    options: unitOptions
                }
            ],
            submitLabel: 'Create Operation',
            cancelLabel: 'Back',
            onSubmit: async (data) => {
                if (!data.unit_ids || data.unit_ids.length === 0) {
                    throw new Error('Please select at least one unit');
                }

                const operation = {
                    ...this.pendingOperation,
                    unit_ids: data.unit_ids
                };

                const result = await api.createOperation(App.countryCode, operation);

                if (result.success !== false) {
                    App.showNotification('Operation created successfully', 'success');
                    OperationsPanel.load && OperationsPanel.load(App.countryCode);
                    if (App.map) App.map.refresh();
                    this.pendingOperation = null;
                } else {
                    throw new Error(result.error || 'Failed to create operation');
                }
            }
        });
    },

    showSetReadiness() {
        Modal.showForm({
            title: 'Set Military Readiness',
            fields: [
                {
                    name: 'level',
                    type: 'select',
                    label: 'Readiness Level',
                    options: this.readinessLevels,
                    description: 'Higher readiness means faster response but increased costs'
                }
            ],
            submitLabel: 'Set Readiness',
            onSubmit: async (data) => {
                const result = await api.setReadiness(App.countryCode, data.level);
                if (result.success) {
                    App.showNotification(`Readiness set to ${data.level}`, 'success');
                } else {
                    throw new Error(result.error || 'Failed to set readiness');
                }
            }
        });
    }
};
