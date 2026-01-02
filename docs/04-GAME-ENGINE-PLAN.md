# 04 - Game Engine Implementation Plan

## Overview

This document outlines the phased implementation of game mechanics after MVP display is complete.

**Remember**: No AI/CPU players yet. Single player only.

---

## Implementation Phases

```
Phase 1: Clock & Tick System         (Foundation)
Phase 2: Constraint Engine           (Validation)
Phase 3: Economy Engine              (KPI changes)
Phase 4: Budget System               (Player decisions)
Phase 5: Sector Development          (Player investment)
Phase 6: Military Procurement        (Buy weapons)
Phase 7: Military Operations         (Use weapons)
Phase 8: Events System               (Crises)
Phase 9: Save/Load System            (Persistence)
```

---

## Player Actions Overview

The player affects KPIs through **decisions** in 6 categories:

```
┌──────────────────────────────────────────────────────────────┐
│  1. BUDGET        - Where does government money go?          │
│  2. DEVELOPMENT   - What do we build/improve?                │
│  3. MILITARY      - What do we buy/do with armed forces?     │
│  4. DIPLOMACY     - How do we interact with other countries? │
│  5. POLICY        - What rules govern the country?           │
│  6. CRISIS        - How do we respond to events?             │
└──────────────────────────────────────────────────────────────┘
```

---

### Player Action 1: BUDGET ACTIONS

| Action | Cost | Constraints | KPI Effects |
|--------|------|-------------|-------------|
| **Reallocate budget** | None | Total must = 100% | Sector funding ↑↓ |
| **Raise taxes** | Happiness | Min 15%, Max 50% | Revenue ↑, Happiness ↓, Growth ↓ |
| **Lower taxes** | Revenue | Can't go negative | Revenue ↓, Happiness ↑, Growth ↑ |
| **Take debt** | Future interest | Credit rating limit | Immediate cash, Debt ratio ↑ |
| **Repay debt** | Budget | Must have surplus | Debt ↓, Credit rating ↑ |

**Example: Reallocate Budget**

Player moves slider: Defense 12% → 15%

```
IMMEDIATE:
├── Defense budget: $20B → $25B
├── Must choose what to cut OR how to fund:
│   ├── Option A: Cut education 10% → 7%
│   ├── Option B: Take $5B debt
│   └── Option C: Raise taxes 2%

DELAYED (3-6 months):
├── If funded properly:
│   ├── Military readiness +3
│   ├── Procurement budget +$1B
│   └── Deterrence index +2
└── Trade-off effects from funding choice
```

---

### Player Action 2: DEVELOPMENT ACTIONS

| Action | Cost | Time | Prerequisites | KPI Effects |
|--------|------|------|---------------|-------------|
| **Invest in sector** | $1-10B | 2-8 quarters | Workforce, Infrastructure | Sector level ↑ |
| **Build power plant** | $5B | 3 years | Engineers | Energy capacity ↑ |
| **Build highway** | $2B | 2 years | Budget | Transport level ↑ |
| **Build port** | $4B | 4 years | Coastal access | Trade capacity ↑ |
| **Build airport** | $3B | 3 years | Land, Budget | Transport ↑, Tourism ↑ |
| **Build university** | $1B | 2 years | Educators | Graduates ↑, Research ↑ |
| **Build hospital** | $0.5B | 1 year | Medical staff | Healthcare ↑ |
| **Build military factory** | $3B | 3 years | Engineers, Security | Local production unlocked |
| **Build research center** | $2B | 2 years | Scientists | Tech level ↑ |

**Example: Invest in Technology Sector**

Player clicks: Invest $3B in Technology

```
VALIDATION:
├── Budget available? $4B procurement → ✓
├── Workforce met?
│   ├── Need: 80,000 software engineers
│   ├── Have: 100,000 available
│   └── ✓ Satisfied
├── Infrastructure met?
│   ├── Need: Digital level 70
│   ├── Have: 80
│   └── ✓ Satisfied
└── ALL CONSTRAINTS MET → Can proceed

EFFECTS PREVIEW:
├── Cost: $3B (from development budget)
├── Duration: 4 quarters
├── Tech sector: 75 → 81 (+6 levels)
├── GDP contribution: +$5B/year (after completion)
├── Employment: +15,000 jobs
└── Unlocks: AI/ML subsector at level 80
```

---

### Player Action 3: MILITARY ACTIONS

| Action | Cost | Time | Prerequisites | KPI Effects |
|--------|------|------|---------------|-------------|
| **Buy weapons** | Varies | 1-6 years | Relations, Budget, No exclusions | Inventory ↑ |
| **Sell weapons** | Revenue | Immediate | Production capability | Budget ↑, Relations ↑ |
| **Increase conscription** | Political | 6 months | Population | Personnel ↑, Happiness ↓ |
| **Reduce military** | Savings | Immediate | None | Budget ↑, Strength ↓ |
| **Raise readiness** | Budget | 1 month | Equipment, Personnel | Readiness ↑ |
| **Conduct operation** | Assets, Munitions | Varies | Readiness, Intel | See operations table |
| **Start local production** | $$$, Time | 3-10 years | Sector level, Workforce | Independence ↑ |

**Example: Buy F-35 Fighters**

Player clicks: Purchase 20x F-35 from USA

```
VALIDATION:
├── Weapon exists in catalog? ✓
├── Budget: Need $2.4B, Have $4B → ✓
├── Relations: Need USA ≥70, Have 80 → ✓
├── Exclusion: Not operating S-400 → ✓
├── Allowed buyer: ISR in list → ✓
└── ALL CONSTRAINTS MET → Can proceed

ORDER CREATED:
├── Cost: $2.4B (paid over 5 years)
├── Delivery start: 2028
├── Delivery rate: 5/year
├── Completion: 2031
└── Requires: Pilots, Technicians, Parts from USA
```

**Military Operations Table**

| Operation | Assets Used | Munitions | Risk | Effects |
|-----------|-------------|-----------|------|---------|
| **Air strike** | Fighters | Bombs, Missiles | Aircraft loss 2-10% | Target destroyed, Relations ↓↓ |
| **Intercept** | Air defense | Interceptors | System damage 5% | Threat neutralized |
| **Ground assault** | Tanks, Infantry | Shells, Fuel | Heavy casualties | Territory gained |
| **Naval patrol** | Ships | Fuel | Low | Security ↑, Intel ↑ |
| **Cyber attack** | Cyber unit | None | Attribution risk | Target disrupted |

---

### Player Action 4: DIPLOMACY ACTIONS

| Action | Cost | Cooldown | Prerequisites | KPI Effects |
|--------|------|----------|---------------|-------------|
| **Diplomatic visit** | $0 | 6 months | Relations > -50 | Relations +2 |
| **Economic aid** | $0.5B | 3 months | Budget | Relations +5 |
| **Military aid** | $1B | 6 months | Budget, Equipment | Relations +8 |
| **Trade deal** | Negotiation | 12 months | Relations > 20 | Trade ↑, Relations +3 |
| **Sanctions** | Trade loss | Immediate | None | Relations -20, Target GDP ↓ |
| **Break relations** | Trade loss | Immediate | None | Relations = -100 |
| **Request alliance** | Commitment | Once | Relations > 70 | Protection, Obligations |
| **Intelligence sharing** | Security risk | 6 months | Relations > 30 | Relations +4, Intel ↑ |

**Example: Send Economic Aid to Jordan**

```
ACTION: Send $500M aid to Jordan

EFFECTS:
├── Immediate:
│   ├── Budget: -$0.5B
│   └── Jordan relations: 45 → 50 (+5)
├── Delayed (6 months):
│   ├── Trade with Jordan: +$200M/year
│   └── Border security cooperation: +10%
└── Cooldown: Cannot send more aid for 3 months
```

---

### Player Action 5: POLICY ACTIONS

| Action | Cost | Time to Effect | KPI Effects |
|--------|------|----------------|-------------|
| **Education reform** | Budget | 5 years | Graduate quality ↑, Workforce ↑ |
| **Healthcare reform** | Budget | 3 years | Life expectancy ↑, Productivity ↑ |
| **Immigration policy OPEN** | Political | 1 year | Population ↑, Workforce ↑, Tension ↑ |
| **Immigration policy CLOSED** | Political | 1 year | Brain drain risk, Homogeneity ↑ |
| **Environmental regulation** | GDP | 2 years | Pollution ↓, Manufacturing ↓ |
| **Deregulation** | Political | 1 year | Business growth ↑, Inequality ↑ |
| **Minimum wage increase** | Business | 6 months | Happiness ↑, Unemployment ↑ |
| **Privatization** | Political | 2 years | Efficiency ↑, Public jobs ↓ |
| **Nationalization** | Budget | 2 years | Control ↑, Efficiency ↓ |

**Example: Open Immigration Policy**

```
ACTION: Set immigration policy to OPEN

EFFECTS OVER TIME:
├── Year 1:
│   ├── Net migration: +2/1000 → +5/1000
│   ├── Population growth: +0.3%
│   └── Social stability: -3
├── Year 2-3:
│   ├── Workforce: +50,000/year (mixed skills)
│   ├── Housing pressure: +5%
│   └── Cultural tension events: +10% probability
├── Year 5+:
│   ├── GDP growth: +0.5% (more workers)
│   ├── Innovation: +3% (diversity)
│   └── Integration challenges ongoing
└── Can reverse policy (takes 1 year to see effects)
```

---

### Player Action 6: CRISIS RESPONSE ACTIONS

When events trigger, player must respond:

**Economic Crisis Response**

| Response | Cost | Effects |
|----------|------|---------|
| **Austerity** | Political capital | Deficit ↓, Happiness ↓↓, Recovery slow |
| **Stimulus** | Debt | Deficit ↑, Happiness stable, Recovery fast |
| **Bailout (request)** | Sovereignty | IMF conditions, Debt managed |
| **Do nothing** | Time | Prolonged recession, Instability ↑ |

**Military Threat Response**

| Response | Cost | Effects |
|----------|------|---------|
| **Mobilize reserves** | Budget, Economy | Readiness ↑↑, GDP ↓ |
| **Preemptive strike** | Assets, Relations | Threat ↓, World opinion ↓↓ |
| **Defensive posture** | Budget | Readiness ↑, Deterrence ↑ |
| **Seek mediation** | Political | Tension ↓, Seen as weak |
| **Negotiate** | Concessions | Peace possible, May lose assets |

**Civil Unrest Response**

| Response | Cost | Effects |
|----------|------|---------|
| **Concessions** | Budget, Policy | Happiness ↑, Precedent set |
| **Crackdown** | Political, Relations | Stability short-term, Resentment ↑ |
| **Dialogue** | Time | Slow resolution, Trust ↑ |
| **Ignore** | Risk | May escalate or fade |

---

### Action → KPI Effect Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                  WHAT AFFECTS WHAT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TO INCREASE GDP:                                               │
│  ├── Invest in productive sectors (tech, manufacturing)         │
│  ├── Build infrastructure (transport, energy)                   │
│  ├── Lower taxes (long-term growth)                             │
│  ├── Sign trade deals                                           │
│  └── Improve education (workforce quality)                      │
│                                                                 │
│  TO INCREASE HAPPINESS:                                         │
│  ├── Fund healthcare, education, welfare                        │
│  ├── Lower taxes                                                │
│  ├── Reduce unemployment (invest in sectors)                    │
│  ├── Lower corruption (governance reforms)                      │
│  └── Avoid unpopular decisions                                  │
│                                                                 │
│  TO INCREASE MILITARY STRENGTH:                                 │
│  ├── Buy modern weapons                                         │
│  ├── Increase defense budget                                    │
│  ├── Build military factories (independence)                    │
│  ├── Train personnel (readiness)                                │
│  └── Secure alliances                                           │
│                                                                 │
│  TO IMPROVE RELATIONS:                                          │
│  ├── Send aid (economic/military)                               │
│  ├── Sign trade deals                                           │
│  ├── Diplomatic visits                                          │
│  ├── Support their positions                                    │
│  └── Don't buy from their enemies                               │
│                                                                 │
│  TO REDUCE EVENT RISK:                                          │
│  ├── Keep debt below 60% GDP                                    │
│  ├── Keep unemployment below 8%                                 │
│  ├── Keep happiness above 50                                    │
│  ├── Keep military strength > neighbors                         │
│  └── Maintain foreign reserves > 6 months                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### UI Action Points

Where player interacts:

| Screen | Actions Available |
|--------|-------------------|
| **Dashboard** | Quick view only |
| **Budget Panel** | Reallocate %, Tax rate, Debt |
| **Sectors Panel** | Invest in sector, View constraints |
| **Infrastructure Panel** | Start construction projects |
| **Military Panel** | Set readiness, Conscription |
| **Procurement Panel** | Browse catalog, Buy weapons |
| **Operations Panel** | Plan and execute military operations |
| **Diplomacy Panel** | Per-country actions (aid, treaties, sanctions) |
| **Policy Panel** | Set national policies |
| **Events Panel** | Respond to active crises |

---

## Phase 1: Clock & Tick System

**Goal**: Make time actually affect the game state.

### 1.1 Tick Types

| Tick Type | Game Days | Real Seconds (1x) | Purpose |
|-----------|-----------|-------------------|---------|
| Daily | 1 | 1s | UI update, micro changes |
| Weekly | 7 | 7s | Minor adjustments |
| Monthly | 30 | 30s | Economic update |
| Quarterly | 90 | 90s | Sector progress |
| Yearly | 365 | 365s | Demographics, elections |

### 1.2 Clock Service

```python
# backend/services/clock_service.py
from datetime import date, timedelta
from typing import Callable, List, Dict
import asyncio

class TickType:
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class ClockService:
    def __init__(self):
        self.current_date: date = date(2024, 1, 1)
        self.day_count: int = 0
        self.paused: bool = True
        self.speed: float = 1.0
        self.tick_handlers: Dict[str, List[Callable]] = {
            TickType.DAILY: [],
            TickType.WEEKLY: [],
            TickType.MONTHLY: [],
            TickType.QUARTERLY: [],
            TickType.YEARLY: [],
        }
    
    def register_handler(self, tick_type: str, handler: Callable):
        """Register a function to be called on specific tick type"""
        self.tick_handlers[tick_type].append(handler)
    
    async def advance_day(self):
        """Advance game by one day and trigger appropriate ticks"""
        if self.paused:
            return
        
        self.day_count += 1
        self.current_date += timedelta(days=1)
        
        # Always trigger daily
        await self._trigger_handlers(TickType.DAILY)
        
        # Check for other tick types
        if self.day_count % 7 == 0:
            await self._trigger_handlers(TickType.WEEKLY)
        
        if self.current_date.day == 1:  # First of month
            await self._trigger_handlers(TickType.MONTHLY)
            
            if self.current_date.month in [1, 4, 7, 10]:  # Quarters
                await self._trigger_handlers(TickType.QUARTERLY)
            
            if self.current_date.month == 1:  # New year
                await self._trigger_handlers(TickType.YEARLY)
    
    async def _trigger_handlers(self, tick_type: str):
        """Trigger all handlers for a tick type"""
        for handler in self.tick_handlers[tick_type]:
            await handler(self.current_date, self.day_count)
    
    async def run(self):
        """Main game loop"""
        while True:
            if not self.paused:
                await self.advance_day()
            await asyncio.sleep(1.0 / self.speed)

clock_service = ClockService()
```

### 1.3 Tick Processor

```python
# backend/engine/tick_processor.py
from backend.services.clock_service import clock_service, TickType
from backend.services.db_service import db_service
from datetime import date

class TickProcessor:
    def __init__(self, country_code: str):
        self.country_code = country_code
        self._register_handlers()
    
    def _register_handlers(self):
        clock_service.register_handler(TickType.DAILY, self.on_daily)
        clock_service.register_handler(TickType.MONTHLY, self.on_monthly)
        clock_service.register_handler(TickType.QUARTERLY, self.on_quarterly)
        clock_service.register_handler(TickType.YEARLY, self.on_yearly)
    
    async def on_daily(self, game_date: date, day_count: int):
        """Daily updates - mostly UI sync"""
        data = db_service.load_country(self.country_code)
        data['meta']['current_date'] = {
            'year': game_date.year,
            'month': game_date.month,
            'day': game_date.day
        }
        data['meta']['total_game_days_elapsed'] = day_count
        db_service.save_country(self.country_code, data)
    
    async def on_monthly(self, game_date: date, day_count: int):
        """Monthly economic update"""
        data = db_service.load_country(self.country_code)
        
        # TODO: Phase 3 - Economic calculations
        # - Revenue collection
        # - Expense processing
        # - Inflation adjustment
        # - Trade balance update
        
        db_service.save_country(self.country_code, data)
    
    async def on_quarterly(self, game_date: date, day_count: int):
        """Quarterly sector/project updates"""
        data = db_service.load_country(self.country_code)
        
        # TODO: Phase 5 - Sector development progress
        # - Project completion checks
        # - Sector level adjustments
        # - Workforce reallocation effects
        
        db_service.save_country(self.country_code, data)
    
    async def on_yearly(self, game_date: date, day_count: int):
        """Yearly demographic/political updates"""
        data = db_service.load_country(self.country_code)
        
        # TODO: Phase 3 - Demographics
        # - Population growth
        # - Age distribution shift
        # - Migration effects
        # - Graduate production
        
        db_service.save_country(self.country_code, data)
```

### 1.4 Integration with FastAPI

```python
# backend/main.py (additions)
from fastapi import BackgroundTasks
from backend.services.clock_service import clock_service
from backend.engine.tick_processor import TickProcessor

# Initialize on startup
@app.on_event("startup")
async def startup():
    # Initialize tick processor for default country
    processor = TickProcessor("ISR")
    
    # Start clock in background
    asyncio.create_task(clock_service.run())

# SSE endpoint for real-time updates
@app.get("/api/stream")
async def stream_updates():
    async def event_generator():
        last_day = 0
        while True:
            if clock_service.day_count > last_day:
                last_day = clock_service.day_count
                data = db_service.load_country("ISR")
                yield f"data: {json.dumps(data['meta'])}\n\n"
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

---

## Phase 2: Constraint Engine

**Goal**: Validate player actions against prerequisites.

### 2.1 Constraint Types

```python
# backend/engine/constraint_engine.py
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel

class ConstraintType(Enum):
    BUDGET = "budget"              # Has enough money?
    WORKFORCE = "workforce"        # Has required workers?
    INFRASTRUCTURE = "infrastructure"  # Has facilities?
    RELATIONS = "relations"        # Good enough relations?
    SECTOR_LEVEL = "sector_level"  # Sector developed enough?
    EXCLUSION = "exclusion"        # Not operating incompatible system?
    POLITICAL = "political"        # Political approval needed?
    TIME = "time"                  # Enough time passed?

class ConstraintResult(BaseModel):
    satisfied: bool
    constraint_type: ConstraintType
    message: str
    current_value: Optional[float] = None
    required_value: Optional[float] = None
    missing_items: Optional[List[str]] = None
```

### 2.2 Constraint Checker

```python
# backend/engine/constraint_engine.py (continued)

class ConstraintEngine:
    def __init__(self, country_data: dict):
        self.data = country_data
    
    def check_budget(
        self, 
        amount_billions: float, 
        budget_category: str = "procurement"
    ) -> ConstraintResult:
        """Check if budget is available"""
        available = self._get_available_budget(budget_category)
        
        return ConstraintResult(
            satisfied=available >= amount_billions,
            constraint_type=ConstraintType.BUDGET,
            message=f"Need ${amount_billions}B, have ${available}B available",
            current_value=available,
            required_value=amount_billions
        )
    
    def check_workforce(
        self, 
        requirements: Dict[str, int]
    ) -> ConstraintResult:
        """Check if workforce requirements are met"""
        pools = self.data['workforce']['expertise_pools']
        missing = []
        
        for pool_name, required_count in requirements.items():
            if pool_name not in pools:
                missing.append(f"{pool_name}: pool not found")
                continue
            
            available = pools[pool_name]['available'] - pools[pool_name]['employed']
            if available < required_count:
                missing.append(f"{pool_name}: need {required_count}, have {available} free")
        
        return ConstraintResult(
            satisfied=len(missing) == 0,
            constraint_type=ConstraintType.WORKFORCE,
            message="Workforce requirements " + ("met" if not missing else "not met"),
            missing_items=missing if missing else None
        )
    
    def check_infrastructure(
        self, 
        requirements: Dict[str, float]
    ) -> ConstraintResult:
        """Check infrastructure requirements (dot notation paths)"""
        missing = []
        
        for path, required_value in requirements.items():
            current = self._get_nested_value(self.data['infrastructure'], path)
            if current is None:
                missing.append(f"{path}: not found")
            elif current < required_value:
                missing.append(f"{path}: need {required_value}, have {current}")
        
        return ConstraintResult(
            satisfied=len(missing) == 0,
            constraint_type=ConstraintType.INFRASTRUCTURE,
            message="Infrastructure requirements " + ("met" if not missing else "not met"),
            missing_items=missing if missing else None
        )
    
    def check_relations(
        self, 
        country_code: str, 
        min_score: int
    ) -> ConstraintResult:
        """Check if relations with a country are high enough"""
        relations = self.data.get('relations', {})
        current_score = relations.get(country_code, {}).get('score', 0)
        
        return ConstraintResult(
            satisfied=current_score >= min_score,
            constraint_type=ConstraintType.RELATIONS,
            message=f"Relations with {country_code}: {current_score} (need {min_score})",
            current_value=current_score,
            required_value=min_score
        )
    
    def check_sector_level(
        self, 
        sector_name: str, 
        min_level: int
    ) -> ConstraintResult:
        """Check if sector is developed enough"""
        sectors = self.data.get('sectors', {})
        current_level = sectors.get(sector_name, {}).get('level', 0)
        
        return ConstraintResult(
            satisfied=current_level >= min_level,
            constraint_type=ConstraintType.SECTOR_LEVEL,
            message=f"Sector {sector_name}: level {current_level} (need {min_level})",
            current_value=current_level,
            required_value=min_level
        )
    
    def check_exclusion(
        self, 
        forbidden_systems: List[str]
    ) -> ConstraintResult:
        """Check if country operates forbidden systems"""
        inventory = self.data.get('military_inventory', {})
        operating = self._get_all_system_models(inventory)
        
        conflicts = [sys for sys in forbidden_systems if sys in operating]
        
        return ConstraintResult(
            satisfied=len(conflicts) == 0,
            constraint_type=ConstraintType.EXCLUSION,
            message="No conflicting systems" if not conflicts else f"Conflicts: {conflicts}",
            missing_items=conflicts if conflicts else None
        )
    
    def check_all(
        self, 
        constraints: Dict
    ) -> Tuple[bool, List[ConstraintResult]]:
        """Check multiple constraints, return overall result and details"""
        results = []
        
        if 'budget' in constraints:
            results.append(self.check_budget(**constraints['budget']))
        
        if 'workforce' in constraints:
            results.append(self.check_workforce(constraints['workforce']))
        
        if 'infrastructure' in constraints:
            results.append(self.check_infrastructure(constraints['infrastructure']))
        
        if 'relations' in constraints:
            for country, min_score in constraints['relations'].items():
                results.append(self.check_relations(country, min_score))
        
        if 'sector_level' in constraints:
            for sector, min_level in constraints['sector_level'].items():
                results.append(self.check_sector_level(sector, min_level))
        
        if 'exclusion' in constraints:
            results.append(self.check_exclusion(constraints['exclusion']))
        
        all_satisfied = all(r.satisfied for r in results)
        return all_satisfied, results
    
    # Helper methods
    def _get_available_budget(self, category: str) -> float:
        budget = self.data.get('budget', {}).get('allocation', {})
        defense = budget.get('defense', {})
        if category == 'procurement':
            return defense.get('breakdown', {}).get('procurement', 0)
        return 0
    
    def _get_nested_value(self, data: dict, path: str):
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def _get_all_system_models(self, inventory: dict) -> List[str]:
        """Extract all weapon model names from inventory"""
        models = []
        for category in inventory.values():
            if isinstance(category, dict):
                for subcategory in category.values():
                    if isinstance(subcategory, list):
                        for item in subcategory:
                            if isinstance(item, dict) and 'model' in item:
                                models.append(item['model'])
        return models
```

### 2.3 Usage Example

```python
# Example: Check if can purchase F-35
constraints = {
    'budget': {'amount_billions': 2.4, 'budget_category': 'procurement'},
    'relations': {'USA': 70},
    'exclusion': ['S-400', 'Su-35']
}

engine = ConstraintEngine(country_data)
can_purchase, results = engine.check_all(constraints)

if not can_purchase:
    for result in results:
        if not result.satisfied:
            print(f"BLOCKED: {result.message}")
```

---

## Phase 3: Economy Engine

**Goal**: Make economy actually work (monthly tick).

### 3.1 Economic Calculations

```python
# backend/engine/economy_engine.py

class EconomyEngine:
    def __init__(self, country_data: dict):
        self.data = country_data
    
    def process_monthly_tick(self) -> dict:
        """Process all monthly economic changes"""
        changes = {}
        
        # 1. Calculate GDP change
        gdp_change = self._calculate_gdp_change()
        changes['gdp'] = gdp_change
        
        # 2. Process government revenue
        revenue = self._calculate_revenue()
        changes['revenue'] = revenue
        
        # 3. Process expenditures
        expenditure = self._calculate_expenditure()
        changes['expenditure'] = expenditure
        
        # 4. Update debt
        debt_change = self._update_debt(revenue, expenditure)
        changes['debt'] = debt_change
        
        # 5. Inflation adjustment
        inflation = self._calculate_inflation()
        changes['inflation'] = inflation
        
        # 6. Trade balance
        trade = self._calculate_trade_balance()
        changes['trade'] = trade
        
        # 7. Reserves change
        reserves = self._update_reserves(trade)
        changes['reserves'] = reserves
        
        # Apply changes
        self._apply_changes(changes)
        
        return changes
    
    def _calculate_gdp_change(self) -> float:
        """GDP growth based on sectors, workforce, infrastructure"""
        economy = self.data['economy']
        sectors = self.data['sectors']
        workforce = self.data['workforce']
        
        base_growth = economy.get('gdp_growth_potential', 3.0)
        
        # Modifiers
        unemployment_penalty = max(0, (workforce['unemployment_rate'] - 5) * 0.1)
        
        sector_avg_level = sum(s['level'] for s in sectors.values()) / len(sectors)
        sector_bonus = (sector_avg_level - 50) * 0.02  # +/- based on 50 baseline
        
        monthly_growth = (base_growth + sector_bonus - unemployment_penalty) / 12
        
        return monthly_growth
    
    def _calculate_revenue(self) -> float:
        """Monthly government revenue"""
        budget = self.data['budget']
        economy = self.data['economy']
        
        annual_revenue = budget['total_revenue_billions']
        # Revenue is % of GDP, so scales with GDP
        gdp_ratio = economy['gdp_billions_usd'] / 500  # Normalize to base
        
        return (annual_revenue * gdp_ratio) / 12
    
    def _calculate_expenditure(self) -> float:
        """Monthly government expenditure"""
        budget = self.data['budget']
        return budget['total_expenditure_billions'] / 12
    
    def _update_debt(self, revenue: float, expenditure: float) -> float:
        """Update debt based on deficit"""
        monthly_deficit = expenditure - revenue
        return monthly_deficit  # Positive = debt increases
    
    def _calculate_inflation(self) -> float:
        """Inflation based on various factors"""
        economy = self.data['economy']
        
        base_inflation = economy.get('inflation_rate', 3.0)
        
        # High debt increases inflation
        debt_ratio = economy['debt']['debt_to_gdp_percent']
        debt_pressure = max(0, (debt_ratio - 60) * 0.05)
        
        # Strong growth can increase inflation
        growth_pressure = max(0, (economy['gdp_growth_rate'] - 3) * 0.2)
        
        return base_inflation + debt_pressure + growth_pressure
    
    def _calculate_trade_balance(self) -> float:
        """Calculate trade balance from relations"""
        relations = self.data.get('relations', {})
        total_balance = 0
        
        for country, rel_data in relations.items():
            trade = rel_data.get('trade', {})
            total_balance += trade.get('balance_billions', 0)
        
        return total_balance / 12  # Monthly
    
    def _update_reserves(self, trade_balance: float) -> float:
        """Reserves change based on trade"""
        return trade_balance  # Simplified: trade surplus = reserve increase
    
    def _apply_changes(self, changes: dict):
        """Apply calculated changes to data"""
        economy = self.data['economy']
        
        # GDP
        growth_rate = changes['gdp']
        economy['gdp_growth_rate'] = growth_rate * 12  # Annualize for display
        economy['gdp_billions_usd'] *= (1 + growth_rate / 100)
        economy['gdp_per_capita_usd'] = (
            economy['gdp_billions_usd'] * 1e9 / 
            self.data['demographics']['total_population']
        )
        
        # Debt
        economy['debt']['total_billions'] += changes['debt']
        economy['debt']['debt_to_gdp_percent'] = (
            economy['debt']['total_billions'] / economy['gdp_billions_usd'] * 100
        )
        
        # Inflation
        economy['inflation_rate'] = changes['inflation']
        
        # Reserves
        economy['reserves']['foreign_reserves_billions'] += changes['reserves']
        economy['reserves']['months_of_imports_covered'] = (
            economy['reserves']['foreign_reserves_billions'] / 
            (self.data['budget']['total_expenditure_billions'] * 0.3 / 12)  # ~30% is imports
        )
```

### 3.2 Demographics Engine (Yearly)

```python
# backend/engine/demographics_engine.py

class DemographicsEngine:
    def __init__(self, country_data: dict):
        self.data = country_data
    
    def process_yearly_tick(self) -> dict:
        """Process annual demographic changes"""
        demo = self.data['demographics']
        workforce = self.data['workforce']
        
        changes = {}
        
        # Population growth
        births = demo['total_population'] * (demo['birth_rate_per_1000'] / 1000)
        deaths = demo['total_population'] * (demo['death_rate_per_1000'] / 1000)
        migration = demo['total_population'] * (demo['net_migration_per_1000'] / 1000)
        
        population_change = births - deaths + migration
        demo['total_population'] += int(population_change)
        changes['population_change'] = int(population_change)
        
        # Update working age population (rough estimate)
        demo['working_age_population'] = int(demo['total_population'] * 0.6)
        demo['active_labor_force'] = int(
            demo['working_age_population'] * demo['labor_force_participation']
        )
        
        # Median age drift (aging population)
        if demo['birth_rate_per_1000'] < demo['death_rate_per_1000']:
            demo['median_age'] += 0.2
        
        # Workforce graduates
        for level, count in workforce['annual_graduates'].items():
            if level in workforce['by_education']:
                workforce['by_education'][level]['count'] += count
        
        # Update expertise pools (simplified)
        self._update_expertise_pools(workforce)
        
        return changes
    
    def _update_expertise_pools(self, workforce: dict):
        """Update expertise pools based on education"""
        # Simplified: graduates increase pools
        graduate_boost = workforce['annual_graduates'].get('bachelors', 0) * 0.3
        
        for pool_name, pool in workforce['expertise_pools'].items():
            if 'engineering' in pool_name or 'scientist' in pool_name:
                pool['available'] += int(graduate_boost * 0.1)
```

---

## Phase 4: Budget System

**Goal**: Allow player to adjust budget allocation.

### 4.1 Budget Actions

```python
# backend/engine/budget_engine.py

class BudgetEngine:
    def __init__(self, country_data: dict):
        self.data = country_data
        self.constraint_engine = ConstraintEngine(country_data)
    
    def adjust_allocation(
        self, 
        category: str, 
        new_percent: float,
        funding_source: str = "rebalance"  # "rebalance", "debt", "taxes"
    ) -> dict:
        """Adjust budget allocation for a category"""
        budget = self.data['budget']
        allocation = budget['allocation']
        
        if category not in allocation:
            return {'success': False, 'error': f'Unknown category: {category}'}
        
        old_percent = allocation[category]['percent_of_budget']
        delta = new_percent - old_percent
        
        if funding_source == "rebalance":
            # Must reduce other categories
            result = self._rebalance_budget(category, new_percent, delta)
        elif funding_source == "debt":
            # Increase expenditure, increase debt
            result = self._fund_from_debt(category, new_percent, delta)
        elif funding_source == "taxes":
            # Increase revenue (with happiness cost)
            result = self._fund_from_taxes(category, new_percent, delta)
        
        return result
    
    def _rebalance_budget(
        self, 
        category: str, 
        new_percent: float, 
        delta: float
    ) -> dict:
        """Redistribute budget from other categories"""
        budget = self.data['budget']
        allocation = budget['allocation']
        
        # Find categories that can be reduced
        reducible = {
            k: v for k, v in allocation.items() 
            if k != category and k != 'debt_service'  # Can't reduce debt service
        }
        
        if delta > 0:
            # Need to take from others
            total_reducible = sum(a['percent_of_budget'] for a in reducible.values())
            if total_reducible < delta:
                return {
                    'success': False, 
                    'error': f'Cannot free up {delta}% from other categories'
                }
            
            # Proportionally reduce others
            for k, v in reducible.items():
                reduction = (v['percent_of_budget'] / total_reducible) * delta
                v['percent_of_budget'] -= reduction
                v['amount'] = budget['total_expenditure_billions'] * (v['percent_of_budget'] / 100)
        
        # Apply new allocation
        allocation[category]['percent_of_budget'] = new_percent
        allocation[category]['amount'] = budget['total_expenditure_billions'] * (new_percent / 100)
        
        return {
            'success': True,
            'category': category,
            'old_percent': new_percent - delta,
            'new_percent': new_percent,
            'method': 'rebalance'
        }
    
    def _fund_from_debt(
        self, 
        category: str, 
        new_percent: float, 
        delta: float
    ) -> dict:
        """Increase budget via debt"""
        budget = self.data['budget']
        economy = self.data['economy']
        
        additional_spending = budget['total_expenditure_billions'] * (delta / 100)
        
        # Update totals
        budget['total_expenditure_billions'] += additional_spending
        budget['deficit_billions'] += additional_spending
        budget['deficit_to_gdp_percent'] = (
            budget['deficit_billions'] / economy['gdp_billions_usd'] * 100
        )
        
        # Update allocation
        budget['allocation'][category]['percent_of_budget'] = new_percent
        budget['allocation'][category]['amount'] += additional_spending
        
        return {
            'success': True,
            'category': category,
            'additional_spending': additional_spending,
            'new_deficit': budget['deficit_billions'],
            'method': 'debt',
            'warning': 'Increased debt may trigger negative events'
        }
    
    def _fund_from_taxes(
        self, 
        category: str, 
        new_percent: float, 
        delta: float
    ) -> dict:
        """Increase budget via tax increase"""
        budget = self.data['budget']
        indices = self.data['indices']
        
        additional_revenue = budget['total_revenue_billions'] * (delta / 100)
        
        # Update revenue
        budget['total_revenue_billions'] += additional_revenue
        
        # Happiness penalty for tax increase
        happiness_penalty = delta * 0.5  # 0.5 happiness per 1% tax increase
        indices['happiness'] = max(0, indices['happiness'] - happiness_penalty)
        indices['public_trust'] = max(0, indices['public_trust'] - happiness_penalty * 0.5)
        
        # Update allocation
        budget['allocation'][category]['percent_of_budget'] = new_percent
        budget['allocation'][category]['amount'] += additional_revenue
        
        return {
            'success': True,
            'category': category,
            'additional_revenue': additional_revenue,
            'happiness_cost': happiness_penalty,
            'method': 'taxes'
        }
```

### 4.2 Budget API Endpoints

```python
# backend/api/budget.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/budget", tags=["budget"])

class BudgetAdjustment(BaseModel):
    category: str
    new_percent: float
    funding_source: str = "rebalance"

@router.post("/{country_code}/adjust")
async def adjust_budget(country_code: str, adjustment: BudgetAdjustment):
    data = db_service.load_country(country_code.upper())
    engine = BudgetEngine(data)
    
    result = engine.adjust_allocation(
        adjustment.category,
        adjustment.new_percent,
        adjustment.funding_source
    )
    
    if result['success']:
        db_service.save_country(country_code.upper(), data)
    
    return result
```

---

## Phase 5: Sector Development

**Goal**: Allow player to invest in sectors.

### 5.1 Sector Investment

```python
# backend/engine/sector_engine.py

class SectorEngine:
    def __init__(self, country_data: dict):
        self.data = country_data
        self.constraint_engine = ConstraintEngine(country_data)
    
    def invest_in_sector(
        self, 
        sector_name: str, 
        investment_billions: float,
        target_improvement: int = 5  # Level points to gain
    ) -> dict:
        """Start a sector improvement project"""
        sectors = self.data['sectors']
        
        if sector_name not in sectors:
            return {'success': False, 'error': f'Unknown sector: {sector_name}'}
        
        sector = sectors[sector_name]
        
        # Check constraints
        can_invest, results = self.constraint_engine.check_all({
            'budget': {'amount_billions': investment_billions, 'budget_category': 'development'},
            'workforce': sector['constraints'].get('workforce_required', {}),
            'infrastructure': sector['constraints'].get('infrastructure_required', {})
        })
        
        if not can_invest:
            failed = [r for r in results if not r.satisfied]
            return {
                'success': False,
                'error': 'Constraints not met',
                'failed_constraints': [r.message for r in failed]
            }
        
        # Calculate time based on investment vs sector size
        base_quarters = 4
        efficiency = investment_billions / (sector['gdp_contribution_billions'] * 0.1)
        time_quarters = max(2, int(base_quarters / efficiency))
        
        # Create project
        project = {
            'type': 'sector_development',
            'sector': sector_name,
            'investment': investment_billions,
            'target_improvement': target_improvement,
            'start_date': self.data['meta']['current_date'],
            'duration_quarters': time_quarters,
            'quarters_remaining': time_quarters,
            'status': 'in_progress'
        }
        
        # Add to active projects
        if 'active_projects' not in self.data:
            self.data['active_projects'] = []
        self.data['active_projects'].append(project)
        
        return {
            'success': True,
            'project': project
        }
    
    def process_quarterly_progress(self) -> List[dict]:
        """Process all sector projects"""
        completed = []
        
        projects = self.data.get('active_projects', [])
        for project in projects:
            if project['type'] != 'sector_development':
                continue
            
            project['quarters_remaining'] -= 1
            
            if project['quarters_remaining'] <= 0:
                # Complete project
                sector = self.data['sectors'][project['sector']]
                sector['level'] = min(100, sector['level'] + project['target_improvement'])
                project['status'] = 'completed'
                completed.append(project)
        
        # Remove completed projects
        self.data['active_projects'] = [
            p for p in projects if p['status'] != 'completed'
        ]
        
        return completed
```

---

## Phase 6: Military Procurement

**Goal**: Allow player to buy weapons.

### 6.1 Procurement System

```python
# backend/engine/procurement_engine.py
from typing import Optional
import json

class ProcurementEngine:
    def __init__(self, country_data: dict, weapons_catalog: dict):
        self.data = country_data
        self.catalog = weapons_catalog
        self.constraint_engine = ConstraintEngine(country_data)
    
    def request_purchase(
        self,
        weapon_id: str,
        quantity: int
    ) -> dict:
        """Request to purchase a weapon system"""
        
        # Check weapon exists
        if weapon_id not in self.catalog:
            return {'success': False, 'error': f'Unknown weapon: {weapon_id}'}
        
        weapon = self.catalog[weapon_id]
        total_cost = weapon['unit_cost_millions'] * quantity / 1000  # Convert to billions
        
        # Build constraints from weapon definition
        constraints = {
            'budget': {'amount_billions': total_cost, 'budget_category': 'procurement'}
        }
        
        # Add relation constraints
        if weapon.get('manufacturer_country'):
            min_relations = weapon.get('prerequisites_for_buyer', {}).get('min_relations', 50)
            constraints['relations'] = {weapon['manufacturer_country']: min_relations}
        
        # Add exclusion constraints
        if 'not_operating' in weapon.get('prerequisites_for_buyer', {}):
            constraints['exclusion'] = weapon['prerequisites_for_buyer']['not_operating']
        
        # Check all constraints
        can_purchase, results = self.constraint_engine.check_all(constraints)
        
        if not can_purchase:
            failed = [r for r in results if not r.satisfied]
            return {
                'success': False,
                'error': 'Cannot purchase',
                'failed_constraints': [{'type': r.constraint_type.value, 'message': r.message} for r in failed]
            }
        
        # Check if allowed buyer
        allowed = weapon.get('allowed_buyers', [])
        country_code = self.data['meta']['country_code']
        if allowed and country_code not in allowed:
            return {
                'success': False,
                'error': f'{country_code} is not an approved buyer for {weapon_id}'
            }
        
        # Create procurement order
        delivery_time = weapon.get('delivery_time_years', '2-4')
        min_years, max_years = map(int, delivery_time.split('-'))
        avg_years = (min_years + max_years) // 2
        
        order = {
            'type': 'weapon_procurement',
            'weapon_id': weapon_id,
            'weapon_model': weapon['name'],
            'quantity': quantity,
            'total_cost_billions': total_cost,
            'source_country': weapon['manufacturer_country'],
            'start_date': self.data['meta']['current_date'],
            'delivery_start_year': self.data['meta']['current_date']['year'] + avg_years,
            'delivery_per_year': max(1, quantity // avg_years),
            'delivered': 0,
            'status': 'ordered'
        }
        
        # Deduct from budget
        self._deduct_procurement_budget(total_cost)
        
        # Add to active projects
        if 'active_projects' not in self.data:
            self.data['active_projects'] = []
        self.data['active_projects'].append(order)
        
        return {
            'success': True,
            'order': order
        }
    
    def process_deliveries(self, current_year: int) -> List[dict]:
        """Process weapon deliveries for current year"""
        delivered = []
        
        projects = self.data.get('active_projects', [])
        for project in projects:
            if project['type'] != 'weapon_procurement':
                continue
            
            if current_year >= project['delivery_start_year']:
                # Deliver batch
                to_deliver = min(
                    project['delivery_per_year'],
                    project['quantity'] - project['delivered']
                )
                
                if to_deliver > 0:
                    # Add to inventory
                    self._add_to_inventory(project['weapon_id'], to_deliver, project['source_country'])
                    project['delivered'] += to_deliver
                    delivered.append({
                        'weapon': project['weapon_model'],
                        'quantity': to_deliver,
                        'remaining': project['quantity'] - project['delivered']
                    })
                
                if project['delivered'] >= project['quantity']:
                    project['status'] = 'completed'
        
        # Clean up completed
        self.data['active_projects'] = [
            p for p in projects if p.get('status') != 'completed'
        ]
        
        return delivered
    
    def _deduct_procurement_budget(self, amount: float):
        """Deduct from procurement budget"""
        defense = self.data['budget']['allocation']['defense']
        if 'breakdown' in defense and 'procurement' in defense['breakdown']:
            defense['breakdown']['procurement'] -= amount
    
    def _add_to_inventory(self, weapon_id: str, quantity: int, source: str):
        """Add delivered weapons to inventory"""
        weapon = self.catalog[weapon_id]
        inventory = self.data['military_inventory']
        
        category = weapon.get('category', 'other')
        subcategory = weapon.get('subcategory', 'other')
        
        if category not in inventory:
            inventory[category] = {}
        if subcategory not in inventory[category]:
            inventory[category][subcategory] = []
        
        # Check if already have this model
        existing = None
        for item in inventory[category][subcategory]:
            if item.get('model') == weapon['name']:
                existing = item
                break
        
        if existing:
            existing['quantity'] += quantity
        else:
            # Add new entry
            inventory[category][subcategory].append({
                'model': weapon['name'],
                'type': weapon['type'],
                'quantity': quantity,
                'source_country': source,
                'unit_cost_millions': weapon['unit_cost_millions'],
                'readiness_percent': 100,  # New equipment
                'avg_age_years': 0
            })
```

---

## Phase 7: Military Operations

**Goal**: Allow player to conduct military operations.

_(Detailed implementation deferred - complex subsystem)_

### 7.1 Operation Types

- Strike operations (air strikes on targets)
- Defensive operations (intercept threats)
- Ground operations (territory control)
- Naval operations (patrol, blockade)

### 7.2 Key Mechanics

- Assets committed → risk of loss
- Munitions consumed
- Success probability based on: equipment, training, intel, enemy
- Political/economic consequences

---

## Phase 8: Events System

**Goal**: Generate events based on KPI thresholds.

### 8.1 Event Engine

```python
# backend/engine/event_engine.py
import random
from typing import List, Optional

class EventEngine:
    def __init__(self, country_data: dict, event_catalog: dict):
        self.data = country_data
        self.catalog = event_catalog
    
    def check_events(self) -> List[dict]:
        """Check for event triggers, return triggered events"""
        triggered = []
        
        for event_id, event_def in self.catalog.items():
            probability = self._calculate_probability(event_def)
            
            if random.random() < probability:
                triggered.append(self._create_event_instance(event_id, event_def))
        
        return triggered
    
    def _calculate_probability(self, event_def: dict) -> float:
        """Calculate event probability based on current KPIs"""
        base = event_def.get('base_probability_annual', 0.05) / 12  # Monthly
        
        # Add trigger modifiers
        for condition, modifier in event_def.get('triggers', {}).items():
            if self._evaluate_condition(condition):
                base += modifier.get('add', 0)
        
        # Subtract prevention modifiers
        for condition, modifier in event_def.get('prevention', {}).items():
            if self._evaluate_condition(condition):
                base -= modifier.get('subtract', 0)
        
        return max(0, min(1, base))  # Clamp 0-1
    
    def _evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string like 'debt_to_gdp > 80'"""
        # Parse condition
        parts = condition.replace('_', '.').split()
        if len(parts) != 3:
            return False
        
        path, operator, value = parts
        current = self._get_value(path)
        target = float(value)
        
        if operator == '>':
            return current > target
        elif operator == '<':
            return current < target
        elif operator == '>=':
            return current >= target
        elif operator == '<=':
            return current <= target
        elif operator == '==':
            return current == target
        
        return False
    
    def _get_value(self, path: str) -> float:
        """Get value from data using dot notation"""
        keys = path.split('.')
        current = self.data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return 0
        
        return float(current) if current else 0
    
    def _create_event_instance(self, event_id: str, event_def: dict) -> dict:
        """Create an active event instance"""
        return {
            'id': event_id,
            'name': event_def['name'],
            'category': event_def['category'],
            'effects': event_def.get('effects', {}),
            'duration_months': event_def.get('duration_months', 6),
            'months_remaining': event_def.get('duration_months', 6),
            'triggered_date': self.data['meta']['current_date'].copy(),
            'status': 'active'
        }
    
    def apply_event_effects(self, event: dict):
        """Apply event effects to country data"""
        for kpi_path, change in event['effects'].items():
            self._apply_change(kpi_path, change)
    
    def _apply_change(self, path: str, change: float):
        """Apply a change to a KPI"""
        keys = path.split('.')
        current = self.data
        
        for key in keys[:-1]:
            current = current[key]
        
        final_key = keys[-1]
        if final_key in current:
            current[final_key] += change
```

---

## Phase 9: Save/Load System

**Goal**: Persist game state properly.

### 9.1 Save Game

```python
# backend/services/save_service.py
import json
import shutil
from datetime import datetime
from pathlib import Path

class SaveService:
    def __init__(self, saves_dir: Path = Path("db/saves")):
        self.saves_dir = saves_dir
        self.saves_dir.mkdir(parents=True, exist_ok=True)
    
    def save_game(self, country_code: str, slot_name: str = None) -> dict:
        """Save current game state"""
        if not slot_name:
            slot_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        save_dir = self.saves_dir / slot_name
        save_dir.mkdir(exist_ok=True)
        
        # Copy country file
        src = Path(f"db/countries/{country_code}.json")
        dst = save_dir / f"{country_code}.json"
        shutil.copy(src, dst)
        
        # Copy game state
        shutil.copy(Path("db/game_state.json"), save_dir / "game_state.json")
        
        # Save metadata
        meta = {
            'slot_name': slot_name,
            'country_code': country_code,
            'save_time': datetime.now().isoformat(),
            'game_date': self._get_game_date(country_code)
        }
        with open(save_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)
        
        return meta
    
    def load_game(self, slot_name: str) -> dict:
        """Load a saved game"""
        save_dir = self.saves_dir / slot_name
        
        if not save_dir.exists():
            raise FileNotFoundError(f"Save not found: {slot_name}")
        
        # Load metadata
        with open(save_dir / "meta.json") as f:
            meta = json.load(f)
        
        country_code = meta['country_code']
        
        # Restore country file
        src = save_dir / f"{country_code}.json"
        dst = Path(f"db/countries/{country_code}.json")
        shutil.copy(src, dst)
        
        # Restore game state
        shutil.copy(save_dir / "game_state.json", Path("db/game_state.json"))
        
        return meta
    
    def list_saves(self) -> List[dict]:
        """List all save slots"""
        saves = []
        for save_dir in self.saves_dir.iterdir():
            if save_dir.is_dir():
                meta_file = save_dir / "meta.json"
                if meta_file.exists():
                    with open(meta_file) as f:
                        saves.append(json.load(f))
        return sorted(saves, key=lambda x: x['save_time'], reverse=True)
    
    def _get_game_date(self, country_code: str) -> dict:
        with open(f"db/countries/{country_code}.json") as f:
            data = json.load(f)
        return data['meta']['current_date']
```

---

## Implementation Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Clock & Tick | 2-3 days | MVP complete |
| Phase 2: Constraints | 2-3 days | Phase 1 |
| Phase 3: Economy | 3-4 days | Phase 1, 2 |
| Phase 4: Budget | 2-3 days | Phase 2, 3 |
| Phase 5: Sectors | 2-3 days | Phase 2, 3, 4 |
| Phase 6: Procurement | 3-4 days | Phase 2, 5 |
| Phase 7: Operations | 5-7 days | Phase 6 |
| Phase 8: Events | 3-4 days | Phase 3 |
| Phase 9: Save/Load | 1-2 days | Any time |

**Total: ~25-35 days for full implementation**

---

## Next: 05-TESTING-STRATEGY.md

How to test each phase.
