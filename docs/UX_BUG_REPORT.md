# UX End-to-End Testing Bug Report

## Test Date: 2026-01-02
## Tested By: Game Tester Agent

---

## Summary

| Category | Total Actions | Working | Broken | Partial |
|----------|--------------|---------|--------|---------|
| Budget | 4 | 1 | 2 | 1 |
| Sectors | 3 | 2 | 0 | 1 |
| Procurement | 3 | 1 | 2 | 0 |
| Operations | 3 | 1 | 1 | 1 |
| Save/Load | 4 | 4 | 0 | 0 |

---

## CRITICAL BUGS (Blocking)

### BUG-001: Budget > Adjust Allocation - Wrong Category Names
- **Severity**: CRITICAL
- **Status**: BROKEN
- **Location**: `frontend/js/actions/budget.js` lines 3-11
- **Issue**: Frontend budget categories don't match backend categories
- **Frontend sends**: `welfare`, `science`, `administration`
- **Backend expects**: `social_welfare`, `research`, `internal_security`, `pensions`, etc.
- **Symptom**: API returns 400 error "Unknown category"
- **Fix Required**: Update `budgetCategories` in budget.js to match backend

### BUG-002: Budget > Adjust Tax - Wrong Rate Format
- **Severity**: HIGH
- **Status**: PARTIAL
- **Location**: `frontend/js/actions/budget.js` line 104
- **Issue**: Frontend divides rate by 100 before sending (`rate / 100`)
- **Backend expects**: Rate as percentage (15-50), not decimal
- **Symptom**: API receives 0.25 when user selects 25%, returns error "Tax rate cannot go below 15%"
- **Fix Required**: Remove division by 100 in `showAdjustTax()`

### BUG-003: Budget > Take Debt - Requires Additional Fields
- **Severity**: HIGH
- **Status**: BROKEN
- **Location**: Backend `budget_engine.py`
- **Issue**: Backend requires credit rating check but ISR country data has negative debt (-363B = surplus)
- **Symptom**: Internal Server Error because debt calculation fails with negative numbers
- **Fix Required**: Handle surplus/negative debt in take_debt engine

### BUG-004: Procurement > Buy Weapons - Wrong Weapon IDs
- **Severity**: CRITICAL
- **Status**: BROKEN
- **Location**: Frontend needs to use catalog structure
- **Issue**: Weapon IDs in catalog are nested (`weapons.infantry.rifle`, `weapons.armor.mbt`)
- **Frontend sends**: `f35`, `merkava` (flat IDs that don't exist)
- **Symptom**: API returns "Unknown weapon: f35"
- **Fix Required**: Either flatten catalog or update frontend to build proper weapon_id

### BUG-005: Operations > Create Map Operation - Wrong Request Format
- **Severity**: HIGH
- **Status**: BROKEN
- **Location**: Frontend sends `location: {lat, lng}` but backend expects `target_lat`, `target_lng`
- **Symptom**: API returns 422 "Field required: target_lat, target_lng"
- **Fix Required**: Update frontend to send flat coordinates or update backend to accept nested

---

## MEDIUM BUGS (Degraded Experience)

### BUG-006: Budget Categories Mismatch
- **Severity**: MEDIUM
- **Location**: `frontend/js/actions/budget.js` lines 3-11
- **Details**:
  - Frontend has: `defense`, `healthcare`, `education`, `infrastructure`, `welfare`, `administration`, `science`
  - Backend has: `defense`, `healthcare`, `education`, `infrastructure`, `social_welfare`, `pensions`, `research`, `foreign_affairs`, `internal_security`, `administration`
- **Missing in frontend**: `pensions`, `foreign_affairs`, `internal_security`
- **Wrong names**: `welfare` should be `social_welfare`, `science` should be `research`

### BUG-007: Funding Sources Mismatch
- **Severity**: MEDIUM
- **Location**: `frontend/js/actions/budget.js` lines 13-17
- **Details**:
  - Frontend has: `rebalance`, `debt`, `reserves`
  - Backend expects: `rebalance`, `debt`, `taxes`
- **Fix**: Change `reserves` to `taxes` in fundingSources

### BUG-008: Sectors > Invest - Constraint Errors Not User-Friendly
- **Severity**: LOW
- **Location**: Backend returns technical constraint errors
- **Issue**: Error message shows "software_engineers: pool not found" instead of user-friendly message
- **Symptom**: User doesn't understand why investment failed

---

## WORKING FEATURES

### Budget > Tax Rate
- **Status**: WORKS (after frontend fix for rate format)
- **API Response**: Returns success with old/new rates and effects

### Sectors > View Projects
- **Status**: WORKS
- **API Response**: Returns projects with progress, eta, type

### Procurement > Active Orders
- **Status**: WORKS
- **API Response**: Returns orders with progress, delivery_date

### Operations > Get Types
- **Status**: WORKS
- **API Response**: Returns all operation types with requirements

### Operations > Set Readiness
- **Status**: WORKS
- **API Response**: Returns success with new level and cost multiplier

### Save/Load > All Functions
- **Status**: ALL WORK
- Save Game: Works
- Load Game: Works
- Quick Save: Works
- Quick Load: Works
- List Saves: Works
- Delete Save: Works

---

## FIXES REQUIRED

### Priority 1 (Critical - Blocking Features)

| # | File | Change |
|---|------|--------|
| 1 | `frontend/js/actions/budget.js` | Fix budgetCategories to match backend |
| 2 | `frontend/js/actions/budget.js` | Remove `/ 100` in showAdjustTax() |
| 3 | `frontend/js/actions/budget.js` | Fix fundingSources (`reserves` -> `taxes`) |
| 4 | `backend/engine/budget_engine.py` | Handle negative debt in take_debt() |
| 5 | Frontend procurement | Fix weapon_id to match catalog structure |
| 6 | `frontend/js/actions/operations.js` OR `backend/api/map_routes.py` | Fix coordinate format mismatch |

### Priority 2 (Medium)

| # | File | Change |
|---|------|--------|
| 7 | `backend/engine/sector_engine.py` | User-friendly workforce constraint messages |
| 8 | Frontend | Add missing budget categories UI |

---

## TEST COMMANDS USED

```bash
# Budget
curl -X POST /api/budget/ISR/adjust -d '{"category":"defense","new_percent":25,"funding_source":"rebalance"}'
curl -X POST /api/budget/ISR/tax -d '{"new_rate":32}'
curl -X POST /api/budget/ISR/debt/take -d '{"amount_billions":5}'

# Sectors
curl /api/country/ISR/sectors
curl -X POST /api/sectors/ISR/invest -d '{"sector_name":"technology","investment_billions":1.0,"target_improvement":5}'
curl /api/sectors/ISR/projects

# Procurement
curl /api/procurement/catalog
curl /api/procurement/ISR/orders
curl -X POST /api/procurement/ISR/check -d '{"weapon_id":"f35","quantity":1}'

# Operations
curl /api/operations/types
curl -X POST /api/operations/ISR/readiness?level=high
curl -X POST /api/map/operations/ISR/create -d '{"operation_type":"air_strike","name":"Test","duration_hours":24,"location":{"lat":33.5,"lng":36.3},"unit_ids":["f35_squadron_140"]}'

# Save/Load
curl /api/saves
curl -X POST /api/saves/ISR -d '{"slot_name":"test","description":"Test"}'
curl -X POST /api/saves/ISR/quick
```

---

## Recommended Fix Order

1. **BUG-002**: Quick 1-line fix - remove `/ 100` in tax rate
2. **BUG-001/006/007**: Budget categories and funding sources - frontend only
3. **BUG-005**: Map operations coordinate format - frontend or backend
4. **BUG-004**: Procurement weapon IDs - needs catalog structure analysis
5. **BUG-003**: Take debt with negative debt - backend logic fix
