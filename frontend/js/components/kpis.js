// KPI Panel Component
const KPIPanel = {
    container: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    render(countryData) {
        if (!this.container || !countryData) return;

        const { economy, demographics, indices, workforce } = countryData;

        const kpis = [
            {
                label: 'GDP',
                value: this.formatCurrency(economy?.gdp_billions_usd || 0),
                status: (economy?.gdp_growth_rate || 0) >= 0 ? 'positive' : 'negative'
            },
            {
                label: 'Treasury',
                value: this.formatCurrency(economy?.reserves?.foreign_reserves_billions || 0),
                status: 'neutral'
            },
            {
                label: 'Debt %',
                value: `${(economy?.debt?.debt_to_gdp_percent || 0).toFixed(1)}%`,
                status: (economy?.debt?.debt_to_gdp_percent || 0) > 100 ? 'negative' :
                        (economy?.debt?.debt_to_gdp_percent || 0) > 60 ? 'warning' : 'neutral'
            },
            {
                label: 'Population',
                value: this.formatNumber(demographics?.total_population || 0),
                status: 'neutral'
            },
            {
                label: 'Unemployment',
                value: `${(workforce?.unemployment_rate || 0).toFixed(1)}%`,
                status: (workforce?.unemployment_rate || 0) > 10 ? 'negative' :
                        (workforce?.unemployment_rate || 0) > 5 ? 'warning' : 'positive'
            },
            {
                label: 'Approval',
                value: `${indices?.public_trust || 0}%`,
                status: (indices?.public_trust || 0) >= 60 ? 'positive' :
                        (indices?.public_trust || 0) >= 40 ? 'warning' : 'negative'
            }
        ];

        this.container.innerHTML = kpis.map(kpi => `
            <div class="kpi-item ${kpi.status}">
                <span class="kpi-label">${kpi.label}</span>
                <span class="kpi-value">${kpi.value}</span>
            </div>
        `).join('');
    },

    formatNumber(num) {
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toLocaleString();
    },

    formatCurrency(billions) {
        return `$${billions.toFixed(1)}B`;
    },

    update(kpiData) {
        // Handle real-time KPI updates from WebSocket
        // This would merge the new data and re-render
    }
};
