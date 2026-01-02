# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Operations tracking system (operations_ISR.json)
- Enhanced unit data model (kills, losses, movement, operation assignment)

### Changed
- Enriched country data with economic simulation results

### Fixed
- Modal close race condition in frontend

---

## [0.1.0] - 2026-01-03

### Added
- Project documentation (01-PROJECT-SETUP.md, 02-DATA-MODELS.md, etc.)
- Complete FastAPI backend with 40+ endpoints
- 10 game engines (budget, economy, sector, procurement, operations, events, constraints, demographics, unit, location_operations)
- Dashboard MVP with all KPI panels
- Working game clock with pause/resume and speed control
- WebSocket real-time updates
- Save/Load system with slots
- Map integration with Leaflet.js
- Complete action system (budget, sectors, procurement, operations)
- Seed data for Israel (ISR.json)
- Military units and bases data
- 247 passing tests

### Fixed
- 8 UX bugs (see UX_BUG_REPORT.md)
- Frontend-backend API alignment issues

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2026-01-03 | MVP - Full game systems, 247 tests |
| 0.2.0 | TBD | Polish & Events |
| 0.3.0 | TBD | AI Neighbors |
| 0.4.0 | TBD | Multiple Countries |
| 1.0.0 | TBD | Playable Game |
