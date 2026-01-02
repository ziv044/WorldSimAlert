# Backlog

## 🔴 High Priority

### Extended Features
- [ ] **AI Neighbors** - CPU-controlled countries that act independently
- [ ] **Diplomacy Actions** - Improve/damage relations with other countries
- [ ] **Multiple Countries** - Play as different nations (USA, etc.)

### Polish
- [ ] **Response Format Standardization** - Unify API response format across all endpoints
- [ ] **Error Code Taxonomy** - Define error codes for programmatic error handling

---

## 🟡 Medium Priority

### Extended Features
- [ ] **Scenarios** - Historical situations to play through
- [ ] **Event Catalog Expansion** - More diverse events and crises

### Polish
- [ ] **Isometric Map View** - Enhanced visual map display
- [ ] **Sound/Music** - Audio feedback for actions
- [ ] **Animations** - UI transitions and feedback

---

## 🟢 Low Priority

### Nice to Have
- [ ] **Multiplayer** - Multiple players controlling different countries
- [ ] **Mod Support** - Allow custom countries and events

---

## 🐛 Bugs

_None currently - last verified 2026-01-03_

---

## 🔧 Tech Debt

- [ ] **API Response Standardization** - Unify `success`, `valid`, `eligible` fields
- [ ] **Service Layer** - Extract common save-after-success pattern from endpoints
- [ ] **Clock API Consolidation** - Merge redundant pause/resume/speed endpoints
- [ ] Add API documentation (OpenAPI/Swagger auto-generation)
- [ ] Add structured logging throughout
- [x] Add comprehensive test coverage (247 tests, ~90%+)

---

## ✅ Completed (v0.1.0)

### Core Engine
- [x] Constraint Engine (budget, workforce, infrastructure, relations)
- [x] Economy Engine (GDP, inflation, trade balance)
- [x] Clock/Tick System (pause, speed control, tick processing)
- [x] Budget Engine (allocation, tax, debt)
- [x] Sector Engine (investment, infrastructure projects)
- [x] Procurement Engine (buy/sell weapons, orders)
- [x] Operations Engine (military operations, readiness)
- [x] Event Engine (active events, responses)
- [x] Demographics Engine (population, workforce)
- [x] Unit Engine (deploy, return, movement)
- [x] Location Operations Engine (tactical operations)

### Data
- [x] Seed Data: Israel (complete country model)
- [x] Weapons Catalog (30+ weapons)
- [x] Events Catalog (economic and military events)
- [x] Constraints Catalog (validation rules)
- [x] Map Data (cities, bases, units, borders)

### API
- [x] 40+ REST endpoints
- [x] WebSocket real-time updates
- [x] Map API routes

### Frontend
- [x] Dashboard MVP with all KPI panels
- [x] Action system (budget, sectors, procurement, operations, units, events, saves)
- [x] Map integration with Leaflet.js
- [x] Modal/form system
- [x] Real-time WebSocket updates

### Testing
- [x] 247 tests passing
- [x] UX end-to-end verification (21 actions)
- [x] 8 UX bugs fixed
