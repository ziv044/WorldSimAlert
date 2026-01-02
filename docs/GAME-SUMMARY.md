# World Sim - Game Summary

## What Is This Game?

A **single-player country simulation** where you control a real nation (Israel as test case) and make strategic decisions across economics, military, diplomacy, and policy. Inspired by SimCity (economics), Victoria (grand strategy), and Red Alert (military realism).

**Core Loop**: Time advances in real-time (pauseable). Make decisions, watch consequences ripple through interconnected systems over days, months, and years.

---

## Features

### Implemented
- **Game Clock** - Real-time simulation with pause/resume and speed controls (1x, 2x, 5x, 10x)
- **Budget Management** - Allocate funds across 10 categories (defense, healthcare, education, etc.)
- **Economic Simulation** - GDP growth, taxes, debt, inflation, trade balance
- **Military Inventory** - Realistic weapons catalog with procurement system
- **Sector Development** - 11 economic sectors (tech, defense, energy, etc.) with investment options
- **Constraint System** - Validates actions against budget, workforce, relations, prerequisites
- **Save/Load System** - Multiple save slots with quick-save
- **Dashboard UI** - Dark-themed display of all country KPIs
- **40+ API Endpoints** - Full REST API for all game actions

### Partially Implemented
- Military operations (9 operation types defined)
- Event system (economic crises, military tensions, natural disasters)
- Demographics (population, workforce, expertise pools)
- Diplomatic relations matrix

---

## Core Logic

### Decision Dimensions (6)
| Dimension | What You Control |
|-----------|------------------|
| **Budget** | Tax rates, category allocation, debt management |
| **Development** | Sector investment, infrastructure projects |
| **Military** | Weapon procurement, readiness levels, operations |
| **Diplomacy** | Relations, treaties, trade agreements |
| **Policy** | Domestic policies affecting happiness/productivity |
| **Crisis** | Respond to random events (wars, disasters, scandals) |

### Tick System
- **Daily**: Minor resource updates
- **Monthly**: Economic calculations (GDP, revenue, expenses, debt)
- **Quarterly**: Sector development progress
- **Yearly**: Demographics, weapon deliveries, major recalculations

### Constraint Validation
Every action checked against:
- Available budget in relevant category
- Required workforce (engineers, scientists, military personnel)
- Infrastructure prerequisites
- Diplomatic relation thresholds
- Technology/sector level requirements

---

## How to Play

### Starting the Game
```bash
# Terminal 1 - Start backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Serve frontend
cd frontend
python -m http.server 8080

# Open browser to http://localhost:8080
```

### Game Controls
- **Pause/Resume**: Control time flow
- **Speed**: Adjust simulation speed (1x-10x)
- **Save/Load**: Preserve and restore game state

### Making Decisions
1. **Review Dashboard** - Check KPIs across all panels
2. **Allocate Budget** - Balance spending priorities
3. **Invest in Sectors** - Develop your economy
4. **Build Military** - Procure weapons, maintain readiness
5. **Handle Events** - Respond to crises as they occur

### Winning/Losing
No explicit win condition. Success measured by:
- Economic stability (GDP growth, low debt)
- Military strength (readiness, modern equipment)
- Population welfare (low unemployment, high happiness)
- Diplomatic standing (allies, trade partners)

---

## Codebase Status

### What We Have

| Component | Status | Files |
|-----------|--------|-------|
| Data Models | Complete | 12 Pydantic models |
| API Layer | Complete | 40+ endpoints in main.py |
| Game Clock | Complete | clock_service.py |
| Constraint Engine | Complete | constraint_engine.py |
| Database Service | Complete | JSON file operations |
| Save System | Complete | save_service.py |
| Frontend UI | Complete | Dashboard layout + dark theme |
| Economy Engine | Partial | GDP, debt calculations |
| Budget Engine | Partial | Allocation logic |
| Sector Engine | Partial | Investment system |
| Procurement Engine | Partial | Purchase validation |

### What's Missing

| Gap | Description | Priority |
|-----|-------------|----------|
| **Frontend Interactivity** | No buttons/forms for player actions | High |
| **Engine Wiring** | Calculations exist but don't apply changes to data | High |
| **Event Responses** | Events trigger but player can't respond | Medium |
| **Operations Execution** | Military ops defined but not executable | Medium |
| **More Countries** | Only Israel has full data (USA is stub) | Low |
| **Expanded Catalogs** | Limited weapons/events definitions | Low |
| **Integration Tests** | API tests missing | Low |

### File Structure
```
world_sim/
├── backend/
│   ├── main.py           # FastAPI app (40+ endpoints)
│   ├── models/           # 12 data models
│   ├── services/         # DB + Save services
│   └── engine/           # 10 game engines
├── frontend/
│   ├── index.html        # Dashboard layout
│   ├── css/style.css     # Dark theme
│   └── js/               # API client + components
├── db/
│   ├── countries/        # ISR.json (full), USA.json (stub)
│   ├── catalog/          # Weapons, events, constraints
│   └── game_state.json   # Current game meta
├── docs/                 # 5 planning documents
└── tests/                # pytest suite (partial)
```

---

## Completion Estimate

**~60% Complete**

- Foundation is solid (models, API, clock, constraints)
- Display layer works (data loads and shows)
- **Main gap**: Game loop not fully wired - ticks calculate but don't consistently update state
- **Biggest need**: Frontend forms to let players actually take actions

### Next Steps
1. Wire tick processors to update displayed data
2. Add frontend forms for budget/investment/procurement actions
3. Complete engine calculations (apply changes to data)
4. Implement event response handling
5. Expand country data and catalogs
