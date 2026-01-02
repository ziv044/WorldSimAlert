// Operations Panel Component
const OperationsPanel = {
    container: null,
    operations: [],
    countryCode: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    async load(countryCode) {
        this.countryCode = countryCode;
        try {
            const data = await api.getOperations(countryCode);
            this.operations = data.operations || [];
            this.render();
        } catch (error) {
            console.error('Failed to load operations:', error);
            this.container.innerHTML = '<div class="error">Failed to load operations</div>';
        }
    },

    render() {
        if (!this.container) return;

        if (this.operations.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No active operations</div>';
            return;
        }

        this.container.innerHTML = this.operations.map(op => {
            const statusClass = op.status || 'planning';
            const progress = op.progress_percent || 0;
            const opType = (op.operation_type || 'unknown').replace(/_/g, ' ');

            return `
                <div class="operation-item ${statusClass}" data-id="${op.id}">
                    <div class="operation-name">${op.name || 'Unnamed Operation'}</div>
                    <div class="operation-type">${opType}</div>
                    <div class="operation-status">
                        <span class="status-badge ${statusClass}">${statusClass}</span>
                    </div>
                    <div class="operation-progress">
                        <div class="operation-progress-bar" style="width: ${progress}%"></div>
                    </div>
                    <div class="operation-progress-text">${progress.toFixed(0)}%</div>
                </div>
            `;
        }).join('');

        // Add click handlers
        this.container.querySelectorAll('.operation-item').forEach(item => {
            item.addEventListener('click', () => {
                this.showOperationDetails(item.dataset.id);
            });
        });
    },

    showOperationDetails(operationId) {
        const op = this.operations.find(o => o.id === operationId);
        if (!op) return;

        // For now, just center map on operation
        const map = getMap();
        if (map && op.target_location) {
            map.centerOn(op.target_location.lat, op.target_location.lng);
        }
    },

    updateOperation(opData) {
        const { operation_id, status, progress } = opData;
        const opEl = this.container?.querySelector(`[data-id="${operation_id}"]`);

        if (opEl) {
            // Update status badge
            const badge = opEl.querySelector('.status-badge');
            if (badge) {
                badge.textContent = status;
                badge.className = `status-badge ${status}`;
            }

            // Update progress bar
            const progressBar = opEl.querySelector('.operation-progress-bar');
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }

            // Update progress text
            const progressText = opEl.querySelector('.operation-progress-text');
            if (progressText) {
                progressText.textContent = `${progress.toFixed(0)}%`;
            }

            // Update item class
            opEl.className = `operation-item ${status}`;
        }
    },

    operationCompleted(opData) {
        // Reload operations list
        if (this.countryCode) {
            this.load(this.countryCode);
        }
    },

    getOperationCount() {
        return this.operations.length;
    }
};
