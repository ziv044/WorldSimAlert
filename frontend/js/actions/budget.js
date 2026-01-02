// Budget Actions
const BudgetActions = {
    budgetCategories: [
        { value: 'defense', label: 'Defense' },
        { value: 'healthcare', label: 'Healthcare' },
        { value: 'education', label: 'Education' },
        { value: 'infrastructure', label: 'Infrastructure' },
        { value: 'welfare', label: 'Welfare' },
        { value: 'administration', label: 'Administration' },
        { value: 'science', label: 'Science & Research' }
    ],

    fundingSources: [
        { value: 'rebalance', label: 'Rebalance (from other categories)' },
        { value: 'debt', label: 'Take Debt' },
        { value: 'reserves', label: 'Use Reserves' }
    ],

    async showAdjustBudget() {
        // Load current budget to show context
        let currentBudget = null;
        try {
            currentBudget = await api.getBudget(App.countryCode);
        } catch (e) {
            console.warn('Could not load current budget:', e);
        }

        Modal.showForm({
            title: 'Adjust Budget Allocation',
            fields: [
                {
                    name: 'category',
                    type: 'select',
                    label: 'Category',
                    options: this.budgetCategories
                },
                {
                    name: 'new_percent',
                    type: 'range',
                    label: 'New Allocation',
                    min: 0,
                    max: 50,
                    step: 0.5,
                    defaultValue: 15,
                    suffix: '%',
                    description: 'Percentage of total budget'
                },
                {
                    name: 'funding_source',
                    type: 'select',
                    label: 'Funding Source',
                    options: this.fundingSources
                },
                {
                    name: 'preview',
                    type: 'display',
                    label: 'Current Budget',
                    defaultValue: currentBudget ? this.formatBudgetPreview(currentBudget) : 'Loading...'
                }
            ],
            submitLabel: 'Apply Changes',
            onSubmit: async (data) => {
                const result = await api.adjustBudget(App.countryCode, data);
                if (result.success) {
                    App.showNotification('Budget adjusted successfully', 'success');
                    KPIPanel.load && KPIPanel.load(App.countryCode);
                } else {
                    throw new Error(result.error || result.message || 'Failed to adjust budget');
                }
            }
        });
    },

    formatBudgetPreview(budget) {
        if (!budget || !budget.allocation) return 'No data';

        const items = Object.entries(budget.allocation || {})
            .map(([key, val]) => `${key}: ${(val * 100).toFixed(1)}%`)
            .join(', ');

        return items || 'No allocation data';
    },

    showAdjustTax() {
        Modal.showForm({
            title: 'Adjust Tax Rate',
            fields: [
                {
                    name: 'new_rate',
                    type: 'range',
                    label: 'Tax Rate',
                    min: 5,
                    max: 60,
                    step: 0.5,
                    defaultValue: 25,
                    suffix: '%',
                    description: 'Higher taxes increase revenue but reduce growth and public approval'
                }
            ],
            submitLabel: 'Apply',
            onSubmit: async (data) => {
                // Convert percentage to decimal
                const rate = data.new_rate / 100;
                const result = await api.adjustTax(App.countryCode, rate);
                if (result.success) {
                    App.showNotification('Tax rate adjusted', 'success');
                    KPIPanel.load && KPIPanel.load(App.countryCode);
                } else {
                    throw new Error(result.error || result.message || 'Failed to adjust tax rate');
                }
            }
        });
    },

    showTakeDebt() {
        Modal.showForm({
            title: 'Take On Debt',
            fields: [
                {
                    name: 'amount_billions',
                    type: 'number',
                    label: 'Amount (Billions $)',
                    min: 0.1,
                    max: 100,
                    step: 0.1,
                    defaultValue: 5,
                    description: 'Taking debt increases treasury but adds to national debt and interest payments'
                }
            ],
            submitLabel: 'Borrow',
            onSubmit: async (data) => {
                const result = await api.takeDebt(App.countryCode, data.amount_billions);
                if (result.success) {
                    App.showNotification(`Borrowed $${data.amount_billions}B`, 'success');
                    KPIPanel.load && KPIPanel.load(App.countryCode);
                } else {
                    throw new Error(result.error || result.message || 'Failed to take debt');
                }
            }
        });
    },

    showRepayDebt() {
        Modal.showForm({
            title: 'Repay Debt',
            fields: [
                {
                    name: 'amount_billions',
                    type: 'number',
                    label: 'Amount (Billions $)',
                    min: 0.1,
                    max: 100,
                    step: 0.1,
                    defaultValue: 5,
                    description: 'Repaying debt reduces interest payments and improves credit rating'
                }
            ],
            submitLabel: 'Repay',
            onSubmit: async (data) => {
                const result = await api.repayDebt(App.countryCode, data.amount_billions);
                if (result.success) {
                    App.showNotification(`Repaid $${data.amount_billions}B`, 'success');
                    KPIPanel.load && KPIPanel.load(App.countryCode);
                } else {
                    throw new Error(result.error || result.message || 'Failed to repay debt');
                }
            }
        });
    }
};
