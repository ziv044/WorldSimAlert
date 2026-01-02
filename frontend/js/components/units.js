// Military Units Panel Component
const UnitsPanel = {
    container: null,
    unitsData: null,
    countryCode: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    async load(countryCode) {
        this.countryCode = countryCode;
        try {
            this.unitsData = await api.getUnits(countryCode);
            this.render();
        } catch (error) {
            console.error('Failed to load units:', error);
            this.container.innerHTML = '<div class="error">Failed to load units</div>';
        }
    },

    render() {
        if (!this.container) return;

        if (!this.unitsData || !this.unitsData.units || this.unitsData.units.length === 0) {
            this.container.innerHTML = '<div class="empty-state">No military units</div>';
            return;
        }

        // Group units by category
        const grouped = this.groupByCategory(this.unitsData.units);

        const categoryConfig = {
            aircraft: { icon: '✈️', label: 'Fighter Jets' },
            helicopter: { icon: '🚁', label: 'Helicopters' },
            ground: { icon: '🛡️', label: 'Ground Forces' },
            naval: { icon: '🚢', label: 'Naval Ships' },
            air_defense: { icon: '🎯', label: 'Air Defense' },
            missile: { icon: '🚀', label: 'Missiles' },
            special_ops: { icon: '👤', label: 'Special Ops' }
        };

        this.container.innerHTML = Object.entries(grouped).map(([category, units]) => {
            const config = categoryConfig[category] || { icon: '•', label: category };
            const totalCount = units.reduce((sum, u) => sum + (u.quantity || 0), 0);
            const activeCount = units.filter(u => u.status === 'idle' || u.status === 'deployed').length;

            return `
                <div class="unit-category" data-category="${category}">
                    <div class="unit-category-header">
                        <span>
                            <span class="unit-category-icon">${config.icon}</span>
                            <span class="unit-category-name">${config.label}</span>
                        </span>
                        <span class="unit-category-count">${totalCount}</span>
                    </div>
                </div>
            `;
        }).join('');

        // Add click handlers for expanding categories
        this.container.querySelectorAll('.unit-category-header').forEach(header => {
            header.addEventListener('click', () => {
                const category = header.parentElement.dataset.category;
                this.toggleCategory(category);
            });
        });
    },

    groupByCategory(units) {
        return units.reduce((acc, unit) => {
            const cat = unit.category || 'unknown';
            if (!acc[cat]) acc[cat] = [];
            acc[cat].push(unit);
            return acc;
        }, {});
    },

    toggleCategory(category) {
        const element = this.container.querySelector(`[data-category="${category}"]`);
        if (element) {
            element.classList.toggle('expanded');
        }
    },

    updateUnit(unitData) {
        // Handle real-time unit updates
        // Reload all units for simplicity
        if (this.countryCode) {
            this.load(this.countryCode);
        }
    },

    getUnitCount() {
        if (!this.unitsData || !this.unitsData.units) return 0;
        return this.unitsData.units.reduce((sum, u) => sum + (u.quantity || 0), 0);
    },

    getUnit(unitId) {
        if (!this.unitsData || !this.unitsData.units) return null;
        return this.unitsData.units.find(u => u.id === unitId);
    },

    getAllUnits() {
        return this.unitsData?.units || [];
    },

    getIdleUnits() {
        return this.getAllUnits().filter(u => u.status === 'idle');
    }
};
