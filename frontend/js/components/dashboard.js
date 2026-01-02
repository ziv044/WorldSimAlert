// Dashboard render functions for all KPI panels

function formatNumber(num) {
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toLocaleString();
}

function formatPercent(num) {
    return num.toFixed(1) + '%';
}

function formatCurrency(billions) {
    return '$' + billions.toFixed(1) + 'B';
}

function getProgressClass(value, thresholds = [33, 66]) {
    if (value < thresholds[0]) return 'low';
    if (value < thresholds[1]) return 'medium';
    return 'high';
}

function renderOverview(data) {
    const el = document.getElementById('overview-content');
    if (!el) return;

    const { economy, demographics, indices, military, meta } = data;

    el.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-item">
                <span class="kpi-label">GDP</span>
                <span class="kpi-value">${formatCurrency(economy.gdp_billions_usd)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Population</span>
                <span class="kpi-value">${formatNumber(demographics.total_population)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">GDP/Capita</span>
                <span class="kpi-value">$${formatNumber(economy.gdp_per_capita_usd)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Stability</span>
                <span class="kpi-value">${indices.stability}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Military Strength</span>
                <span class="kpi-value">${military.strength_index}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Happiness</span>
                <span class="kpi-value">${indices.happiness}</span>
            </div>
        </div>
    `;
}

function renderEconomy(data) {
    const el = document.getElementById('economy-content');
    if (!el) return;

    const { economy } = data;

    el.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-item">
                <span class="kpi-label">GDP</span>
                <span class="kpi-value">${formatCurrency(economy.gdp_billions_usd)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Growth</span>
                <span class="kpi-value ${economy.gdp_growth_rate >= 0 ? 'positive' : 'negative'}">
                    ${economy.gdp_growth_rate >= 0 ? '+' : ''}${formatPercent(economy.gdp_growth_rate)}
                </span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Inflation</span>
                <span class="kpi-value">${formatPercent(economy.inflation_rate)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Debt/GDP</span>
                <span class="kpi-value">${formatPercent(economy.debt.debt_to_gdp_percent)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Reserves</span>
                <span class="kpi-value">${formatCurrency(economy.reserves.foreign_reserves_billions)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Credit Rating</span>
                <span class="kpi-value">${economy.debt.credit_rating}</span>
            </div>
        </div>
    `;
}

function renderBudget(data) {
    const el = document.getElementById('budget-content');
    if (!el) return;

    const { budget } = data;

    const allocations = Object.entries(budget.allocation)
        .sort((a, b) => b[1].percent_of_budget - a[1].percent_of_budget)
        .slice(0, 6);

    el.innerHTML = `
        <div class="kpi-grid" style="margin-bottom: 1rem;">
            <div class="kpi-item">
                <span class="kpi-label">Revenue</span>
                <span class="kpi-value">${formatCurrency(budget.total_revenue_billions)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Expenditure</span>
                <span class="kpi-value">${formatCurrency(budget.total_expenditure_billions)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Deficit</span>
                <span class="kpi-value ${budget.deficit_billions > 0 ? 'negative' : 'positive'}">
                    ${formatCurrency(Math.abs(budget.deficit_billions))}
                </span>
            </div>
        </div>
        <div class="sector-list">
            ${allocations.map(([name, alloc]) => `
                <div class="sector-item">
                    <span class="sector-name">${name.replace(/_/g, ' ')}</span>
                    <div class="sector-bar">
                        <div class="fill" style="width: ${alloc.percent_of_budget}%"></div>
                    </div>
                    <span class="sector-value">${formatPercent(alloc.percent_of_budget)}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderDemographics(data) {
    const el = document.getElementById('demographics-content');
    if (!el) return;

    const { demographics } = data;

    el.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-item">
                <span class="kpi-label">Population</span>
                <span class="kpi-value">${formatNumber(demographics.total_population)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Median Age</span>
                <span class="kpi-value">${demographics.median_age}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Life Expectancy</span>
                <span class="kpi-value">${demographics.life_expectancy}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Growth Rate</span>
                <span class="kpi-value">${formatPercent(demographics.population_growth_rate)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Urbanization</span>
                <span class="kpi-value">${formatPercent(demographics.urbanization_percent)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Labor Force</span>
                <span class="kpi-value">${formatNumber(demographics.active_labor_force)}</span>
            </div>
        </div>
    `;
}

function renderWorkforce(data) {
    const el = document.getElementById('workforce-content');
    if (!el) return;

    const { workforce } = data;

    // Show top expertise pools
    const topPools = Object.entries(workforce.expertise_pools)
        .sort((a, b) => b[1].available - a[1].available)
        .slice(0, 6);

    el.innerHTML = `
        <div class="kpi-grid" style="margin-bottom: 1rem;">
            <div class="kpi-item">
                <span class="kpi-label">Employed</span>
                <span class="kpi-value">${formatNumber(workforce.total_employed)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Unemployment</span>
                <span class="kpi-value">${formatPercent(workforce.unemployment_rate)}</span>
            </div>
        </div>
        <div class="sector-list">
            ${topPools.map(([name, pool]) => `
                <div class="sector-item">
                    <span class="sector-name">${name.replace(/_/g, ' ')}</span>
                    <div class="sector-bar">
                        <div class="fill" style="width: ${pool.quality_index}%"></div>
                    </div>
                    <span class="sector-value">${formatNumber(pool.available)}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderSectors(data) {
    const el = document.getElementById('sectors-content');
    if (!el) return;

    const { sectors } = data;

    const sectorList = Object.entries(sectors)
        .sort((a, b) => b[1].level - a[1].level);

    el.innerHTML = `
        <div class="sector-list">
            ${sectorList.map(([name, sector]) => `
                <div class="sector-item">
                    <span class="sector-name">${name.replace(/_/g, ' ')}</span>
                    <div class="sector-bar">
                        <div class="fill" style="width: ${sector.level}%"></div>
                    </div>
                    <span class="sector-value">${sector.level}/100</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderInfrastructure(data) {
    const el = document.getElementById('infrastructure-content');
    if (!el) return;

    const { infrastructure } = data;

    const items = [
        { name: 'Energy', level: infrastructure.energy.level },
        { name: 'Transport', level: infrastructure.transportation.level },
        { name: 'Digital', level: infrastructure.digital.level },
        { name: 'Water', level: infrastructure.water.level },
        { name: 'Industrial', level: infrastructure.industrial_facilities.level },
        { name: 'Healthcare', level: infrastructure.healthcare_facilities.level },
        { name: 'Education', level: infrastructure.education_facilities.level },
    ];

    el.innerHTML = `
        <div class="sector-list">
            ${items.map(item => `
                <div class="sector-item">
                    <span class="sector-name">${item.name}</span>
                    <div class="sector-bar">
                        <div class="fill" style="width: ${item.level}%"></div>
                    </div>
                    <span class="sector-value">${item.level}/100</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderMilitary(data) {
    const el = document.getElementById('military-content');
    if (!el) return;

    const { military } = data;

    el.innerHTML = `
        <div class="kpi-grid">
            <div class="kpi-item">
                <span class="kpi-label">Active Personnel</span>
                <span class="kpi-value">${formatNumber(military.personnel.active_duty)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Reserves</span>
                <span class="kpi-value">${formatNumber(military.personnel.reserves)}</span>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Readiness</span>
                <span class="kpi-value">${military.readiness.overall}%</span>
                <div class="progress-bar">
                    <div class="fill ${getProgressClass(military.readiness.overall)}"
                         style="width: ${military.readiness.overall}%"></div>
                </div>
            </div>
            <div class="kpi-item">
                <span class="kpi-label">Strength Index</span>
                <span class="kpi-value">${military.strength_index}</span>
            </div>
        </div>
    `;
}

function renderInventory(data) {
    const el = document.getElementById('inventory-content');
    if (!el) return;

    const { military_inventory: inv } = data;

    el.innerHTML = `
        <div class="inventory-category">
            <h3>Aircraft</h3>
            <table class="inventory-table">
                <tr><th>Type</th><th>Model</th><th>Qty</th><th>Ready</th></tr>
                ${(inv.aircraft?.fighters || []).slice(0, 3).map(a => `
                    <tr>
                        <td>${a.type}</td>
                        <td>${a.model}</td>
                        <td>${a.quantity}</td>
                        <td>${a.readiness_percent}%</td>
                    </tr>
                `).join('')}
            </table>
        </div>

        <div class="inventory-category">
            <h3>Ground Forces</h3>
            <table class="inventory-table">
                <tr><th>Type</th><th>Model</th><th>Qty</th><th>Ready</th></tr>
                ${(inv.ground_forces?.tanks || []).slice(0, 3).map(a => `
                    <tr>
                        <td>${a.type}</td>
                        <td>${a.model}</td>
                        <td>${a.quantity}</td>
                        <td>${a.readiness_percent}%</td>
                    </tr>
                `).join('')}
            </table>
        </div>

        <div class="inventory-category">
            <h3>Air Defense</h3>
            <table class="inventory-table">
                <tr><th>System</th><th>Batteries</th><th>Coverage</th></tr>
                ${(inv.air_defense?.systems || []).slice(0, 3).map(a => `
                    <tr>
                        <td>${a.model}</td>
                        <td>${a.batteries || a.quantity}</td>
                        <td>${a.coverage_radius_km || '-'} km</td>
                    </tr>
                `).join('')}
            </table>
        </div>
    `;
}

function renderRelations(data) {
    const el = document.getElementById('relations-content');
    if (!el) return;

    const { relations } = data;

    const FLAGS = {
        USA: '🇺🇸', DEU: '🇩🇪', EGY: '🇪🇬', IRN: '🇮🇷',
        CHN: '🇨🇳', RUS: '🇷🇺', SAU: '🇸🇦', JOR: '🇯🇴'
    };

    const getRelationClass = (score) => {
        if (score <= -50) return 'hostile';
        if (score <= -10) return 'tense';
        if (score <= 30) return 'neutral';
        if (score <= 70) return 'friendly';
        return 'ally';
    };

    const sortedRelations = Object.entries(relations)
        .sort((a, b) => b[1].score - a[1].score);

    el.innerHTML = `
        <div class="relations-list">
            ${sortedRelations.map(([code, rel]) => `
                <div class="relation-item">
                    <span class="relation-flag">${FLAGS[code] || '🏳️'}</span>
                    <span class="relation-country">${rel.country_name || code}</span>
                    <div class="relation-bar">
                        <div class="fill ${getRelationClass(rel.score)}"
                             style="width: ${Math.min(100, Math.abs(rel.score))}%"></div>
                    </div>
                    <span class="relation-score">${rel.score > 0 ? '+' : ''}${rel.score}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderIndices(data) {
    const el = document.getElementById('indices-content');
    if (!el) return;

    const { indices } = data;

    const items = [
        { name: 'Happiness', value: indices.happiness },
        { name: 'HDI', value: (indices.hdi * 100).toFixed(0) },
        { name: 'Stability', value: indices.stability },
        { name: 'Public Trust', value: indices.public_trust },
        { name: 'Corruption', value: 100 - indices.corruption, label: `${indices.corruption} (lower=better)` },
        { name: 'Inequality', value: (1 - indices.inequality_gini) * 100, label: indices.inequality_gini.toFixed(2) },
    ];

    el.innerHTML = `
        <div class="sector-list">
            ${items.map(item => `
                <div class="sector-item">
                    <span class="sector-name">${item.name}</span>
                    <div class="sector-bar">
                        <div class="fill ${getProgressClass(item.value)}"
                             style="width: ${item.value}%"></div>
                    </div>
                    <span class="sector-value">${item.label || item.value}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Render all panels with country data
function renderAllPanels(countryData) {
    renderOverview(countryData);
    renderEconomy(countryData);
    renderBudget(countryData);
    renderDemographics(countryData);
    renderWorkforce(countryData);
    renderSectors(countryData);
    renderInfrastructure(countryData);
    renderMilitary(countryData);
    renderInventory(countryData);
    renderRelations(countryData);
    renderIndices(countryData);
}
