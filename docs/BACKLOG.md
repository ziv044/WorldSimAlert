# Backlog

## 🔴 High Priority

### Core Engine
- [ ] **Constraint Engine** - Validate player actions against prerequisites
  - Budget checks
  - Workforce checks
  - Infrastructure checks
  - Relations checks
  - Exclusion checks (incompatible systems)
  
- [ ] **Economy Engine** - Monthly economic calculations
  - GDP growth/decline
  - Inflation adjustments
  - Debt accumulation
  - Trade balance

- [ ] **Clock/Tick System** - Time progression
  - Daily/Monthly/Quarterly/Yearly ticks
  - Trigger appropriate updates
  - Pausable, adjustable speed

### Data
- [ ] **Seed Data: Israel** - Complete ISR.json with real-ish data
  - Demographics
  - Economy
  - Military inventory
  - Relations

- [ ] **Weapons Catalog** - All purchasable weapons
  - Prerequisites per weapon
  - Allowed buyers
  - Costs and delivery times

### API
- [ ] **Basic Endpoints** - FastAPI routes
  - GET /api/country/{code}
  - GET /api/game/state
  - POST /api/game/clock

### Frontend
- [ ] **Dashboard MVP** - See KPIs on screen
  - Load data from API
  - Display all panels
  - Working clock display

---

## 🟡 Medium Priority

### Player Actions
- [ ] **Budget System** - Reallocate budget percentages
- [ ] **Sector Investment** - Invest in sector development
- [ ] **Procurement System** - Buy weapons
- [ ] **Diplomacy Actions** - Improve/damage relations

### Events
- [ ] **Event Engine** - Probability-based events
- [ ] **Event Catalog** - Define all events
- [ ] **Crisis Response UI** - Choose responses

### Persistence
- [ ] **Save/Load System** - Persist game state

---

## 🟢 Low Priority

### Polish
- [ ] **Isometric Map View** - Visual map display
- [ ] **Sound/Music** - Audio feedback
- [ ] **Animations** - UI transitions

### Extended Features
- [ ] **Multiple Countries** - Play as different nations
- [ ] **Scenarios** - Historical situations
- [ ] **AI Neighbors** - CPU-controlled countries

---

## 🐛 Bugs

_None yet_

---

## 🔧 Tech Debt

- [ ] Add comprehensive test coverage (target: 90%)
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Add logging throughout
- [ ] Add configuration validation

---

## ✅ Completed

- [x] Project documentation (01-05 docs)
- [x] Data models design
- [x] Game engine plan
- [x] Player actions design
- [x] Testing strategy
- [x] Player guide
- [x] Isometric mockup prototype
