# Current Sprint

**Sprint Goal**: Get MVP visible - see country data on screen with working clock

**Sprint Duration**: ~3 days

---

## 📋 Sprint Backlog

### In Progress
_None currently - awaiting PM to assign_

### Ready for Dev
- [ ] **Create ISR.json seed data**
  - Priority: HIGH
  - Estimate: 1 hour
  - Acceptance Criteria:
    - Contains all fields from 02-DATA-MODELS.md
    - Uses realistic Israel data
    - Valid JSON, passes schema validation

- [ ] **Create FastAPI skeleton**
  - Priority: HIGH
  - Estimate: 1 hour
  - Acceptance Criteria:
    - Server starts without errors
    - GET /api/country/ISR returns data
    - GET /api/game/state returns clock state
    - CORS enabled for local dev

- [ ] **Create Dashboard HTML**
  - Priority: HIGH
  - Estimate: 2 hours
  - Acceptance Criteria:
    - Loads data from API
    - Displays all KPI panels
    - Clock ticks and displays
    - Pause/Resume works

---

## ✅ Completed This Sprint

_Nothing yet_

---

## 🚫 Blocked

_Nothing blocked_

---

## 📊 Sprint Metrics

| Metric | Value |
|--------|-------|
| Tasks Planned | 3 |
| Tasks Completed | 0 |
| Tasks In Progress | 0 |
| Bugs Found | 0 |
| Bugs Fixed | 0 |

---

## 📝 Notes

- Focus on SEEING something first, then iterate
- Don't over-engineer MVP
- Keep first implementation simple
