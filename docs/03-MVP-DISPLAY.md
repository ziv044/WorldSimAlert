# 03 - MVP Display Plan

## Goal

**Get KPIs visible on screen as fast as possible.**

No game logic, no tick processing, no events - just load data and display it beautifully. The clock ticks but doesn't affect anything yet.

---

## MVP Scope

### In Scope ✓

- Load country data from JSON
- Display all KPI categories in a dashboard
- Running game clock (visual only)
- Pause/resume clock
- Speed control (1x, 2x, 5x, 10x)
- Clean, readable UI
- One country (Israel as test case)

### Out of Scope ✗

- Tick processing (KPIs don't change)
- Player actions
- Events
- Multiple countries
- AI/CPU players
- Military operations
- Trade/diplomacy actions

---

## Implementation Order

### Phase 1: Backend Foundation (Day 1)

```
Step 1.1: Create data models (Pydantic)
Step 1.2: Create DB service (JSON read/write)
Step 1.3: Create seed script with Israel data
Step 1.4: Create FastAPI endpoints for reading data
Step 1.5: Verify with curl/browser
```

### Phase 2: Frontend Shell (Day 1-2)

```
Step 2.1: Create index.html with layout structure
Step 2.2: Create CSS for dark theme dashboard
Step 2.3: Create API client (fetch wrapper)
Step 2.4: Create clock component (display only)
Step 2.5: Verify clock ticks visually
```

### Phase 3: KPI Components (Day 2-3)

```
Step 3.1: Overview panel (country name, flag, date)
Step 3.2: Economy panel
Step 3.3: Demographics panel
Step 3.4: Workforce panel (summary view)
Step 3.5: Infrastructure panel (summary view)
Step 3.6: Sectors panel (bar chart style)
Step 3.7: Military panel (summary)
Step 3.8: Military inventory panel (detailed)
Step 3.9: Relations panel (list with scores)
Step 3.10: Indices panel
```

### Phase 4: Polish (Day 3)

```
Step 4.1: Loading states
Step 4.2: Error handling
Step 4.3: Responsive layout
Step 4.4: Clock speed controls
Step 4.5: Pause/resume
```

---

## Backend Implementation

### Step 1.1: Simplified Models for MVP

For MVP, we don't need full Pydantic validation. Start simple:

```python
# backend/models/country.py
from pydantic import BaseModel
from typing import Dict, Any

class CountryState(BaseModel):
    """Full country state - loaded from JSON as-is for MVP"""
    meta: Dict[str, Any]
    demographics: Dict[str, Any]
    workforce: Dict[str, Any]
    infrastructure: Dict[str, Any]
    economy: Dict[str, Any]
    budget: Dict[str, Any]
    sectors: Dict[str, Any]
    military: Dict[str, Any]
    military_inventory: Dict[str, Any]
    relations: Dict[str, Any]
    indices: Dict[str, Any]
    
    class Config:
        extra = "allow"  # Allow additional fields
```

### Step 1.2: DB Service

```python
# backend/services/db_service.py
import json
from pathlib import Path
from typing import Optional
from backend.config import config

class DBService:
    def __init__(self):
        self.db_path = config.DB_PATH
    
    def load_country(self, country_code: str) -> dict:
        """Load country state from JSON file"""
        file_path = self.db_path / "countries" / f"{country_code}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Country {country_code} not found")
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def save_country(self, country_code: str, data: dict) -> None:
        """Save country state to JSON file"""
        file_path = self.db_path / "countries" / f"{country_code}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_game_state(self) -> dict:
        """Load global game state"""
        file_path = self.db_path / "game_state.json"
        if not file_path.exists():
            return {"selected_country": None, "paused": True}
        
        with open(file_path, "r") as f:
            return json.load(f)
    
    def save_game_state(self, data: dict) -> None:
        """Save global game state"""
        file_path = self.db_path / "game_state.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

db_service = DBService()
```

### Step 1.3: Seed Script

Create `scripts/seed_database.py` with Israel data (see separate seed file).

### Step 1.4: API Endpoints

```python
# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.services.db_service import db_service

app = FastAPI(title="Country Sim Game API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return {"status": "running", "game": "Country Sim"}

@app.get("/api/country/{country_code}")
async def get_country(country_code: str):
    """Get full country state"""
    try:
        data = db_service.load_country(country_code.upper())
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Country {country_code} not found")

@app.get("/api/country/{country_code}/economy")
async def get_economy(country_code: str):
    """Get economy data only"""
    data = db_service.load_country(country_code.upper())
    return {
        "economy": data.get("economy", {}),
        "budget": data.get("budget", {})
    }

@app.get("/api/country/{country_code}/military")
async def get_military(country_code: str):
    """Get military data only"""
    data = db_service.load_country(country_code.upper())
    return {
        "military": data.get("military", {}),
        "inventory": data.get("military_inventory", {})
    }

@app.get("/api/country/{country_code}/demographics")
async def get_demographics(country_code: str):
    """Get demographics and workforce"""
    data = db_service.load_country(country_code.upper())
    return {
        "demographics": data.get("demographics", {}),
        "workforce": data.get("workforce", {})
    }

@app.get("/api/game/state")
async def get_game_state():
    """Get current game state"""
    return db_service.load_game_state()

@app.post("/api/game/clock")
async def update_clock(action: str, speed: float = 1.0):
    """Control game clock: pause, resume, set_speed"""
    state = db_service.load_game_state()
    
    if action == "pause":
        state["paused"] = True
    elif action == "resume":
        state["paused"] = False
    elif action == "set_speed":
        state["speed"] = speed
    
    db_service.save_game_state(state)
    return state
```

---

## Frontend Implementation

### Step 2.1: HTML Structure

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Country Simulator</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="app">
        <!-- Header with clock -->
        <header class="header">
            <div class="country-info">
                <span class="flag" id="country-flag">🇮🇱</span>
                <h1 id="country-name">Israel</h1>
            </div>
            <div class="game-clock">
                <div class="date" id="game-date">January 1, 2024</div>
                <div class="clock-controls">
                    <button id="btn-pause">⏸️</button>
                    <button id="btn-play">▶️</button>
                    <select id="speed-select">
                        <option value="1">1x</option>
                        <option value="2">2x</option>
                        <option value="5">5x</option>
                        <option value="10">10x</option>
                    </select>
                </div>
            </div>
        </header>

        <!-- Main Dashboard -->
        <main class="dashboard">
            <!-- Row 1: Overview -->
            <section class="panel panel-overview" id="panel-overview">
                <h2>Overview</h2>
                <div class="panel-content" id="overview-content"></div>
            </section>

            <!-- Row 2: Economy & Budget -->
            <section class="panel panel-economy" id="panel-economy">
                <h2>💰 Economy</h2>
                <div class="panel-content" id="economy-content"></div>
            </section>

            <section class="panel panel-budget" id="panel-budget">
                <h2>📊 Budget</h2>
                <div class="panel-content" id="budget-content"></div>
            </section>

            <!-- Row 3: Demographics & Workforce -->
            <section class="panel panel-demographics" id="panel-demographics">
                <h2>👥 Demographics</h2>
                <div class="panel-content" id="demographics-content"></div>
            </section>

            <section class="panel panel-workforce" id="panel-workforce">
                <h2>👷 Workforce</h2>
                <div class="panel-content" id="workforce-content"></div>
            </section>

            <!-- Row 4: Sectors -->
            <section class="panel panel-sectors panel-wide" id="panel-sectors">
                <h2>🏭 Sectors</h2>
                <div class="panel-content" id="sectors-content"></div>
            </section>

            <!-- Row 5: Infrastructure -->
            <section class="panel panel-infrastructure panel-wide" id="panel-infrastructure">
                <h2>🏗️ Infrastructure</h2>
                <div class="panel-content" id="infrastructure-content"></div>
            </section>

            <!-- Row 6: Military -->
            <section class="panel panel-military" id="panel-military">
                <h2>⚔️ Military</h2>
                <div class="panel-content" id="military-content"></div>
            </section>

            <section class="panel panel-inventory" id="panel-inventory">
                <h2>🛡️ Inventory</h2>
                <div class="panel-content" id="inventory-content"></div>
            </section>

            <!-- Row 7: Relations & Indices -->
            <section class="panel panel-relations" id="panel-relations">
                <h2>🌍 Relations</h2>
                <div class="panel-content" id="relations-content"></div>
            </section>

            <section class="panel panel-indices" id="panel-indices">
                <h2>📈 Indices</h2>
                <div class="panel-content" id="indices-content"></div>
            </section>
        </main>
    </div>

    <script src="js/api.js"></script>
    <script src="js/clock.js"></script>
    <script src="js/components/dashboard.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

### Step 2.2: CSS (Dark Theme)

```css
/* frontend/css/style.css */
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #6e7681;
    --border-color: #30363d;
    --accent-blue: #58a6ff;
    --accent-green: #3fb950;
    --accent-yellow: #d29922;
    --accent-red: #f85149;
    --accent-purple: #a371f7;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.5;
}

.app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
}

.country-info {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.country-info .flag {
    font-size: 2rem;
}

.country-info h1 {
    font-size: 1.5rem;
    font-weight: 600;
}

.game-clock {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.game-clock .date {
    font-size: 1.25rem;
    font-weight: 500;
    font-family: 'Courier New', monospace;
    color: var(--accent-blue);
}

.clock-controls {
    display: flex;
    gap: 0.5rem;
}

.clock-controls button {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1rem;
}

.clock-controls button:hover {
    background: var(--border-color);
}

.clock-controls select {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 0.5rem;
    border-radius: 6px;
}

/* Dashboard Grid */
.dashboard {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    padding: 1.5rem;
}

.panel {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
}

.panel.panel-wide {
    grid-column: span 2;
}

.panel h2 {
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-secondary);
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-color);
}

.panel-content {
    padding: 1rem;
}

/* KPI Display Helpers */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.kpi-item {
    display: flex;
    flex-direction: column;
}

.kpi-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.25rem;
}

.kpi-value {
    font-size: 1.25rem;
    font-weight: 600;
}

.kpi-value.positive { color: var(--accent-green); }
.kpi-value.negative { color: var(--accent-red); }
.kpi-value.neutral { color: var(--text-primary); }

/* Progress Bars */
.progress-bar {
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.progress-bar .fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-bar .fill.low { background: var(--accent-red); }
.progress-bar .fill.medium { background: var(--accent-yellow); }
.progress-bar .fill.high { background: var(--accent-green); }

/* Sector Bars */
.sector-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.sector-item {
    display: grid;
    grid-template-columns: 120px 1fr 60px;
    align-items: center;
    gap: 1rem;
}

.sector-name {
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.sector-bar {
    height: 20px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
}

.sector-bar .fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
}

.sector-value {
    font-size: 0.85rem;
    font-weight: 600;
    text-align: right;
}

/* Relations List */
.relations-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.relation-item {
    display: grid;
    grid-template-columns: 30px 100px 1fr 80px;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--bg-tertiary);
    border-radius: 4px;
}

.relation-flag {
    font-size: 1.25rem;
}

.relation-country {
    font-size: 0.85rem;
}

.relation-bar {
    height: 6px;
    background: var(--bg-primary);
    border-radius: 3px;
    overflow: hidden;
}

.relation-bar .fill {
    height: 100%;
}

.relation-bar .fill.hostile { background: var(--accent-red); }
.relation-bar .fill.tense { background: var(--accent-yellow); }
.relation-bar .fill.neutral { background: var(--text-muted); }
.relation-bar .fill.friendly { background: var(--accent-green); }
.relation-bar .fill.ally { background: var(--accent-blue); }

.relation-score {
    font-size: 0.85rem;
    text-align: right;
    font-weight: 600;
}

/* Inventory Tables */
.inventory-category {
    margin-bottom: 1.5rem;
}

.inventory-category h3 {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color);
}

.inventory-table {
    width: 100%;
    font-size: 0.8rem;
}

.inventory-table th {
    text-align: left;
    color: var(--text-muted);
    padding: 0.25rem 0.5rem;
    font-weight: 500;
}

.inventory-table td {
    padding: 0.25rem 0.5rem;
}

.inventory-table tr:nth-child(even) {
    background: var(--bg-tertiary);
}

/* Loading & Error States */
.loading {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    color: var(--text-muted);
}

.error {
    color: var(--accent-red);
    padding: 1rem;
    text-align: center;
}

/* Responsive */
@media (max-width: 1024px) {
    .dashboard {
        grid-template-columns: 1fr;
    }
    
    .panel.panel-wide {
        grid-column: span 1;
    }
}
```

### Step 2.3: API Client

```javascript
// frontend/js/api.js
const API_BASE = '/api';

const api = {
    async getCountry(code) {
        const response = await fetch(`${API_BASE}/country/${code}`);
        if (!response.ok) throw new Error(`Failed to load country: ${code}`);
        return response.json();
    },
    
    async getGameState() {
        const response = await fetch(`${API_BASE}/game/state`);
        return response.json();
    },
    
    async controlClock(action, speed = 1.0) {
        const response = await fetch(`${API_BASE}/game/clock?action=${action}&speed=${speed}`, {
            method: 'POST'
        });
        return response.json();
    }
};
```

### Step 2.4: Clock Component

```javascript
// frontend/js/clock.js
class GameClock {
    constructor() {
        this.currentDate = new Date(2024, 0, 1);
        this.paused = true;
        this.speed = 1;
        this.intervalId = null;
        this.listeners = [];
    }
    
    start() {
        if (this.intervalId) return;
        
        this.intervalId = setInterval(() => {
            if (!this.paused) {
                this.tick();
            }
        }, 1000 / this.speed);
    }
    
    tick() {
        this.currentDate.setDate(this.currentDate.getDate() + 1);
        this.notifyListeners();
        this.updateDisplay();
    }
    
    pause() {
        this.paused = true;
    }
    
    resume() {
        this.paused = false;
    }
    
    setSpeed(speed) {
        this.speed = speed;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
            this.start();
        }
    }
    
    updateDisplay() {
        const dateEl = document.getElementById('game-date');
        if (dateEl) {
            dateEl.textContent = this.currentDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }
    
    addListener(callback) {
        this.listeners.push(callback);
    }
    
    notifyListeners() {
        this.listeners.forEach(cb => cb(this.currentDate));
    }
    
    setDate(year, month, day) {
        this.currentDate = new Date(year, month - 1, day);
        this.updateDisplay();
    }
}

const gameClock = new GameClock();
```

### Step 2.5: Main App

```javascript
// frontend/js/app.js
let countryData = null;

async function init() {
    try {
        // Load country data
        countryData = await api.getCountry('ISR');
        
        // Set initial date from data
        const meta = countryData.meta;
        gameClock.setDate(
            meta.current_date.year,
            meta.current_date.month,
            meta.current_date.day
        );
        
        // Render all panels
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
        
        // Setup clock controls
        setupClockControls();
        
        // Start clock
        gameClock.start();
        
    } catch (error) {
        console.error('Failed to initialize:', error);
        document.body.innerHTML = `<div class="error">Failed to load game: ${error.message}</div>`;
    }
}

function setupClockControls() {
    document.getElementById('btn-pause').addEventListener('click', () => {
        gameClock.pause();
    });
    
    document.getElementById('btn-play').addEventListener('click', () => {
        gameClock.resume();
    });
    
    document.getElementById('speed-select').addEventListener('change', (e) => {
        gameClock.setSpeed(parseFloat(e.target.value));
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', init);
```

---

## Panel Render Functions

Create `frontend/js/components/dashboard.js` with all render functions:

```javascript
// frontend/js/components/dashboard.js

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
    const { economy, demographics, indices, military } = data;
    
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
                    <span class="sector-name">${name.replace('_', ' ')}</span>
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
    const { military_inventory: inv } = data;
    
    el.innerHTML = `
        <div class="inventory-category">
            <h3>Aircraft</h3>
            <table class="inventory-table">
                <tr><th>Type</th><th>Model</th><th>Qty</th><th>Ready</th></tr>
                ${(inv.aircraft?.fighters || []).map(a => `
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
                ${(inv.ground_forces?.tanks || []).map(a => `
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
                ${(inv.air_defense?.systems || []).map(a => `
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
                             style="width: ${Math.abs(rel.score)}%"></div>
                    </div>
                    <span class="relation-score">${rel.score > 0 ? '+' : ''}${rel.score}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function renderIndices(data) {
    const el = document.getElementById('indices-content');
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
```

---

## Verification Checklist

After MVP implementation, verify:

- [ ] Server starts without errors
- [ ] `/api/country/ISR` returns full JSON
- [ ] Frontend loads without console errors
- [ ] Clock displays and ticks
- [ ] Pause/Resume works
- [ ] Speed control works
- [ ] All 10 panels render with data
- [ ] No layout breaks on resize

---

## Next Steps

After MVP is working:

1. **Read**: `04-GAME-ENGINE-PLAN.md` - Full game logic implementation
2. **Read**: `05-TESTING-STRATEGY.md` - Add tests before game logic
