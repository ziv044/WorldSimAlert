// Sector Actions
const SectorActions = {
    sectors: [
        { value: 'technology', label: 'Technology' },
        { value: 'agriculture', label: 'Agriculture' },
        { value: 'manufacturing', label: 'Manufacturing' },
        { value: 'services', label: 'Services' },
        { value: 'energy', label: 'Energy' },
        { value: 'mining', label: 'Mining' },
        { value: 'tourism', label: 'Tourism' },
        { value: 'finance', label: 'Finance' }
    ],

    infrastructureTypes: [
        { value: 'highway', label: 'Highway' },
        { value: 'rail', label: 'Railway' },
        { value: 'port', label: 'Sea Port' },
        { value: 'airport', label: 'Airport' },
        { value: 'power_plant', label: 'Power Plant' },
        { value: 'water_treatment', label: 'Water Treatment' },
        { value: 'telecom', label: 'Telecom Network' },
        { value: 'hospital', label: 'Hospital' },
        { value: 'school', label: 'School/University' }
    ],

    showInvest() {
        Modal.showForm({
            title: 'Invest in Sector',
            fields: [
                {
                    name: 'sector_name',
                    type: 'select',
                    label: 'Sector',
                    options: this.sectors
                },
                {
                    name: 'investment_billions',
                    type: 'number',
                    label: 'Investment (Billions $)',
                    min: 0.1,
                    max: 50,
                    step: 0.1,
                    defaultValue: 1,
                    description: 'Amount to invest from treasury'
                },
                {
                    name: 'target_improvement',
                    type: 'range',
                    label: 'Target Improvement',
                    min: 1,
                    max: 20,
                    step: 1,
                    defaultValue: 5,
                    suffix: '%',
                    description: 'Expected sector output improvement'
                }
            ],
            submitLabel: 'Invest',
            onSubmit: async (data) => {
                const result = await api.investInSector(App.countryCode, data);
                if (result.success) {
                    App.showNotification(`Invested $${data.investment_billions}B in ${data.sector_name}`, 'success');
                    KPIPanel.load && KPIPanel.load(App.countryCode);
                } else {
                    throw new Error(result.error || result.message || 'Investment failed');
                }
            }
        });
    },

    showInfrastructure() {
        Modal.showForm({
            title: 'Start Infrastructure Project',
            fields: [
                {
                    name: 'project_type',
                    type: 'select',
                    label: 'Project Type',
                    options: this.infrastructureTypes
                },
                {
                    name: 'custom_name',
                    type: 'text',
                    label: 'Project Name',
                    required: false,
                    placeholder: 'Optional custom name...'
                }
            ],
            submitLabel: 'Start Project',
            onSubmit: async (data) => {
                const result = await api.startInfrastructure(App.countryCode, data);
                if (result.success) {
                    App.showNotification(`Started ${data.project_type} project`, 'success');
                } else {
                    throw new Error(result.error || result.message || 'Failed to start project');
                }
            }
        });
    },

    async showProjects() {
        Modal.showLoading('Loading projects...');

        try {
            const result = await api.getProjects(App.countryCode);
            const projects = result.projects || [];

            Modal.close();

            if (projects.length === 0) {
                Modal.show({
                    title: 'Active Projects',
                    content: '<p class="empty-state">No active projects.</p>',
                    size: 'small',
                    buttons: [
                        { label: 'Close', onClick: () => Modal.close() }
                    ]
                });
                return;
            }

            Modal.show({
                title: 'Active Projects',
                content: this.renderProjectsList(projects),
                size: 'large',
                buttons: [
                    { label: 'Close', onClick: () => Modal.close() }
                ]
            });

            // Wire up cancel buttons
            document.querySelectorAll('.project-cancel-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const projectId = e.target.dataset.projectId;
                    this.cancelProject(projectId);
                });
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load projects: ' + error.message, false);
        }
    },

    renderProjectsList(projects) {
        return `
            <div class="projects-list">
                ${projects.map(project => `
                    <div class="project-item">
                        <div class="project-info">
                            <div class="project-name">${project.name || project.project_type || 'Unknown'}</div>
                            <div class="project-type">${project.project_type || 'Project'}</div>
                            <div class="project-progress-container">
                                <div class="project-progress-bar">
                                    <div class="project-progress-fill" style="width: ${project.progress || 0}%"></div>
                                </div>
                                <span class="project-progress-text">${(project.progress || 0).toFixed(0)}%</span>
                            </div>
                            ${project.eta ? `<div class="project-eta">ETA: ${project.eta}</div>` : ''}
                        </div>
                        <button class="btn btn-danger btn-sm project-cancel-btn" data-project-id="${project.id}">
                            Cancel
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    },

    async cancelProject(projectId) {
        Modal.confirm('Cancel this project? Investment will be partially refunded.', async () => {
            try {
                const result = await api.cancelProject(App.countryCode, projectId);
                if (result.success) {
                    App.showNotification('Project cancelled', 'success');
                    this.showProjects(); // Refresh list
                } else {
                    throw new Error(result.error || 'Failed to cancel project');
                }
            } catch (error) {
                Modal.showResult('Error', error.message, false);
            }
        });
    }
};
