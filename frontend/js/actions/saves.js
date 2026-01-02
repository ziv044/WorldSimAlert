// Save/Load Actions
const SaveActions = {
    async showSaveGame() {
        Modal.showForm({
            title: 'Save Game',
            fields: [
                { name: 'slot_name', type: 'text', label: 'Save Name', placeholder: 'Enter save name...' },
                { name: 'description', type: 'textarea', label: 'Description', required: false, placeholder: 'Optional description...' }
            ],
            submitLabel: 'Save',
            onSubmit: async (data) => {
                const result = await api.saveGame(App.countryCode, data);
                if (result.success !== false) {
                    App.showNotification('Game saved successfully', 'success');
                } else {
                    throw new Error(result.error || 'Failed to save game');
                }
            }
        });
    },

    async showLoadGame() {
        Modal.showLoading('Loading saves...');

        try {
            const result = await api.listSaves();
            const saves = result.saves || [];

            Modal.close();

            if (saves.length === 0) {
                Modal.show({
                    title: 'Load Game',
                    content: '<p class="empty-state">No saved games found.</p>',
                    size: 'small',
                    buttons: [
                        { label: 'Close', onClick: () => Modal.close() }
                    ]
                });
                return;
            }

            Modal.show({
                title: 'Load Game',
                content: this.renderSavesList(saves),
                size: 'large',
                buttons: [
                    { label: 'Close', onClick: () => Modal.close() }
                ]
            });

            // Wire up save item click handlers
            document.querySelectorAll('.save-item').forEach(item => {
                const slot = item.dataset.slot;

                item.querySelector('.save-load-btn')?.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.loadSave(slot);
                });

                item.querySelector('.save-delete-btn')?.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.deleteSave(slot);
                });
            });

        } catch (error) {
            Modal.close();
            Modal.showResult('Error', 'Failed to load saves: ' + error.message, false);
        }
    },

    renderSavesList(saves) {
        return `
            <div class="saves-list">
                ${saves.map(save => `
                    <div class="save-item" data-slot="${save.slot_name}">
                        <div class="save-info">
                            <div class="save-name">${save.slot_name}</div>
                            <div class="save-meta">
                                <span class="save-date">${this.formatDate(save.saved_at)}</span>
                                ${save.description ? `<span class="save-desc">${save.description}</span>` : ''}
                            </div>
                            ${save.country_code ? `<div class="save-country">Country: ${save.country_code}</div>` : ''}
                        </div>
                        <div class="save-actions">
                            <button class="btn btn-primary btn-sm save-load-btn">Load</button>
                            <button class="btn btn-danger btn-sm save-delete-btn">Delete</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch {
            return dateStr;
        }
    },

    async loadSave(slot) {
        Modal.confirm(`Load save "${slot}"? Current progress will be lost.`, async () => {
            try {
                const result = await api.loadGame(slot);
                if (result.success !== false) {
                    App.showNotification('Game loaded successfully', 'success');
                    Modal.close();
                    await App.refresh();
                } else {
                    throw new Error(result.error || 'Failed to load game');
                }
            } catch (error) {
                Modal.showResult('Error', error.message, false);
            }
        });
    },

    async deleteSave(slot) {
        Modal.confirm(`Delete save "${slot}"? This cannot be undone.`, async () => {
            try {
                const result = await api.deleteSave(slot);
                if (result.success !== false) {
                    App.showNotification('Save deleted', 'success');
                    // Refresh the list
                    this.showLoadGame();
                } else {
                    throw new Error(result.error || 'Failed to delete save');
                }
            } catch (error) {
                Modal.showResult('Error', error.message, false);
            }
        });
    },

    async quickSave() {
        try {
            const result = await api.quickSave(App.countryCode);
            if (result.success !== false) {
                App.showNotification('Quick saved!', 'success');
            } else {
                App.showNotification('Quick save failed', 'failure');
            }
        } catch (error) {
            App.showNotification('Quick save failed: ' + error.message, 'failure');
        }
    },

    async quickLoad() {
        Modal.confirm('Quick load? Current progress will be lost.', async () => {
            try {
                const result = await api.quickLoad();
                if (result.success !== false) {
                    App.showNotification('Quick loaded!', 'success');
                    await App.refresh();
                } else {
                    App.showNotification('No quick save found', 'failure');
                }
            } catch (error) {
                App.showNotification('Quick load failed: ' + error.message, 'failure');
            }
        });
    }
};
