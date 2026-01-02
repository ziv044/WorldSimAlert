// Action Bar Component - Category dropdowns for player actions
const ActionBar = {
    container: null,
    activeMenu: null,

    categories: [
        {
            id: 'budget',
            icon: '💰',
            label: 'Budget',
            actions: [
                { id: 'adjust-allocation', label: 'Adjust Allocation', icon: '📊', handler: () => BudgetActions.showAdjustBudget() },
                { id: 'adjust-tax', label: 'Adjust Tax Rate', icon: '📈', handler: () => BudgetActions.showAdjustTax() },
                { id: 'take-debt', label: 'Take Debt', icon: '🏦', handler: () => BudgetActions.showTakeDebt() },
                { id: 'repay-debt', label: 'Repay Debt', icon: '💳', handler: () => BudgetActions.showRepayDebt() }
            ]
        },
        {
            id: 'sectors',
            icon: '🏭',
            label: 'Sectors',
            actions: [
                { id: 'invest-sector', label: 'Invest in Sector', icon: '📈', handler: () => SectorActions.showInvest() },
                { id: 'infrastructure', label: 'Start Infrastructure', icon: '🏗️', handler: () => SectorActions.showInfrastructure() },
                { id: 'view-projects', label: 'View Projects', icon: '📋', handler: () => SectorActions.showProjects() }
            ]
        },
        {
            id: 'procurement',
            icon: '🛒',
            label: 'Procurement',
            actions: [
                { id: 'buy-weapons', label: 'Buy Weapons', icon: '🛡️', handler: () => ProcurementActions.showPurchase() },
                { id: 'sell-weapons', label: 'Sell Weapons', icon: '💵', handler: () => ProcurementActions.showSell() },
                { id: 'active-orders', label: 'Active Orders', icon: '📦', handler: () => ProcurementActions.showOrders() }
            ]
        },
        {
            id: 'operations',
            icon: '⚔️',
            label: 'Operations',
            actions: [
                { id: 'plan-operation', label: 'Plan Operation', icon: '📍', handler: () => OperationActions.showPlanOperation() },
                { id: 'create-map-op', label: 'Create Map Operation', icon: '🗺️', handler: () => OperationActions.showCreateMapOperation() },
                { id: 'set-readiness', label: 'Set Readiness', icon: '⚡', handler: () => OperationActions.showSetReadiness() }
            ]
        },
        {
            id: 'saves',
            icon: '💾',
            label: 'Save/Load',
            actions: [
                { id: 'save-game', label: 'Save Game', icon: '💾', handler: () => SaveActions.showSaveGame() },
                { id: 'load-game', label: 'Load Game', icon: '📂', handler: () => SaveActions.showLoadGame() },
                { id: 'quick-save', label: 'Quick Save', icon: '⚡', shortcut: 'F5', handler: () => SaveActions.quickSave() },
                { id: 'quick-load', label: 'Quick Load', icon: '🔄', shortcut: 'F9', handler: () => SaveActions.quickLoad() }
            ]
        }
    ],

    init(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Action bar container not found:', containerId);
            return;
        }

        this.render();
        this.setupGlobalClickHandler();
    },

    render() {
        this.container.innerHTML = this.categories.map(cat => `
            <div class="action-category" data-category="${cat.id}">
                <button class="action-category-btn">
                    <span class="action-category-icon">${cat.icon}</span>
                    <span class="action-category-label">${cat.label}</span>
                    <span class="action-category-arrow">▼</span>
                </button>
                <div class="action-menu">
                    ${cat.actions.map(action => `
                        <div class="action-menu-item" data-action="${action.id}">
                            <span class="action-menu-item-icon">${action.icon}</span>
                            <span class="action-menu-item-label">${action.label}</span>
                            ${action.shortcut ? `<span class="action-menu-item-shortcut">${action.shortcut}</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');

        // Wire up click handlers
        this.container.querySelectorAll('.action-category').forEach(catEl => {
            const categoryId = catEl.dataset.category;
            const btn = catEl.querySelector('.action-category-btn');
            const menu = catEl.querySelector('.action-menu');

            // Toggle menu on button click
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMenu(catEl, menu);
            });

            // Handle action clicks
            menu.querySelectorAll('.action-menu-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.handleAction(categoryId, item.dataset.action);
                    this.hideAllMenus();
                });
            });
        });
    },

    toggleMenu(categoryEl, menu) {
        const isOpen = menu.classList.contains('show');

        // Close all menus first
        this.hideAllMenus();

        if (!isOpen) {
            menu.classList.add('show');
            categoryEl.querySelector('.action-category-btn').classList.add('active');
            this.activeMenu = menu;
        }
    },

    hideAllMenus() {
        this.container.querySelectorAll('.action-menu').forEach(menu => {
            menu.classList.remove('show');
        });
        this.container.querySelectorAll('.action-category-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        this.activeMenu = null;
    },

    setupGlobalClickHandler() {
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.hideAllMenus();
            }
        });
    },

    handleAction(categoryId, actionId) {
        const category = this.categories.find(c => c.id === categoryId);
        if (!category) return;

        const action = category.actions.find(a => a.id === actionId);
        if (!action || !action.handler) return;

        try {
            action.handler();
        } catch (error) {
            console.error('Action handler error:', error);
            App.showNotification('Action failed: ' + error.message, 'failure');
        }
    },

    // Public method to trigger action by ID (for keyboard shortcuts)
    triggerAction(categoryId, actionId) {
        this.handleAction(categoryId, actionId);
    }
};
