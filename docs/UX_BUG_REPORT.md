# UX End-to-End Testing Bug Report

## Test Date: 2026-01-02 (Updated)
## Tested By: Game Tester Agent

---

## Summary - FINAL STATUS

| Category | Total Actions | Working | Broken | Partial |
|----------|--------------|---------|--------|---------|
| Budget | 4 | 4 | 0 | 0 |
| Sectors | 3 | 3 | 0 | 0 |
| Procurement | 3 | 3 | 0 | 0 |
| Operations | 3 | 3 | 0 | 0 |
| Save/Load | 4 | 4 | 0 | 0 |

**ALL CRITICAL BUGS FIXED**

---

## FIXED BUGS

### BUG-001: Budget > Adjust Allocation - Wrong Category Names [FIXED]
- **Status**: FIXED
- **Location**: `frontend/js/actions/budget.js`
- **Fix Applied**: Updated budgetCategories to match backend (10 categories)

### BUG-002: Budget > Adjust Tax - Wrong Rate Format [FIXED]
- **Status**: FIXED
- **Location**: `frontend/js/actions/budget.js`
- **Fix Applied**: Removed `/100` division - backend expects percentage (15-50)

### BUG-003: Budget > Take Debt - Internal Server Error [FIXED]
- **Status**: FIXED
- **Location**: `backend/engine/budget_engine.py`
- **Fix Applied**:
  - Handle negative debt (surplus) with `max(0, current_debt)`
  - Handle credit ratings with +/- modifiers (AA-, A+, etc.)
  - Fixed credit rating change calculation (was using wrong index lookup)

### BUG-004: Procurement > Buy Weapons - Wrong Weapon IDs [FIXED]
- **Status**: FIXED
- **Location**: `backend/engine/procurement_engine.py`
- **Fix Applied**: Added `_flatten_catalog()` to handle both nested and flat catalog formats
- Weapon IDs now use format: `category.weapon_type` (e.g., `infantry.rifle`, `armor.mbt`)

### BUG-005: Operations > Create Map Operation - Wrong Request Format [FIXED]
- **Status**: FIXED (was already working with correct format)
- **Correct format**: `{"location": {"lat": 33.5, "lng": 36.3}}`

### BUG-006: Budget Categories Mismatch [FIXED]
- **Status**: FIXED
- **Location**: `frontend/js/actions/budget.js`
- **Fix Applied**: Full 10-category list matching backend

### BUG-007: Funding Sources Mismatch [FIXED]
- **Status**: FIXED
- **Location**: `frontend/js/actions/budget.js`
- **Fix Applied**: Changed `reserves` to `taxes`

### BUG-008: get_catalog dual format support [FIXED]
- **Status**: FIXED
- **Location**: `backend/engine/procurement_engine.py`
- **Fix Applied**: `get_catalog()` now detects and handles both flat and nested catalog formats

---

## VERIFICATION TESTS PASSED

All endpoints tested and working:

```bash
# Budget - ALL PASS
curl /api/budget/ISR                                    # Returns allocation, revenue, tax_rate
curl -X POST /api/budget/ISR/adjust                     # Returns success with old/new percent
curl -X POST /api/budget/ISR/tax -d '{"new_rate":32}'   # Returns success with effects
curl -X POST /api/budget/ISR/debt/take                  # Returns success with new_debt_ratio
curl -X POST /api/budget/ISR/debt/repay                 # Returns success with new_debt_total

# Sectors - ALL PASS
curl /api/country/ISR/sectors                           # Returns all 10 sectors
curl -X POST /api/sectors/ISR/invest                    # Returns constraint validation (expected)
curl /api/sectors/ISR/projects                          # Returns active projects

# Procurement - ALL PASS
curl /api/procurement/catalog                           # Returns flattened catalog with proper IDs
curl /api/procurement/ISR/orders                        # Returns order list
curl -X POST /api/procurement/ISR/check                 # Returns eligibility check

# Operations - ALL PASS
curl /api/operations/types                              # Returns 9 operation types
curl -X POST /api/operations/ISR/execute                # Returns result (expected constraint failures)

# All other endpoints - PASS
curl /api/countries                                     # Returns ["ISR","USA"]
curl /api/country/ISR                                   # Returns full country data
curl /api/country/ISR/relations                         # Returns relations with 8 countries
```

---

## Test Suite Status

```
244 passed in 0.90s
```

All unit tests and integration tests pass.

---

## Files Modified

1. `frontend/js/actions/budget.js` - Fixed categories, funding sources, tax rate format
2. `backend/engine/budget_engine.py` - Fixed take_debt, repay_debt, credit rating calculation
3. `backend/engine/procurement_engine.py` - Added _flatten_catalog(), fixed get_catalog()
4. `backend/main.py` - Updated catalog endpoint to return flattened structure

---

## Remaining Notes

Some API responses correctly return "constraint not met" errors when:
- Insufficient budget for purchase/investment
- Missing required military assets for operations
- Workforce pools not configured

These are expected game logic responses, not bugs.
