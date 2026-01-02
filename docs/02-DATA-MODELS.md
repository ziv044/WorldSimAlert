# 02 - Data Models

## Overview

This document defines all data structures used in the game. These models represent the complete state of a country and the game world.

---

## Model Hierarchy

```
GAME_STATE
├── meta                 # Game metadata
├── country              # Basic country info
├── demographics         # Population breakdown
├── workforce            # Skills & expertise pools (CONSTRAINT SOURCE)
├── infrastructure       # Physical facilities (CONSTRAINT SOURCE)
├── economy              # GDP, debt, reserves
├── budget               # Government allocation
├── sectors              # Economic sectors with constraints
├── military             # Personnel & readiness
├── military_inventory   # Actual equipment
├── relations            # Bilateral relations per country
└── trade                # Import/export per country
```

---

## 1. META

Game session metadata.

```python
# backend/models/meta.py
from pydantic import BaseModel
from datetime import date

class TimeConfig(BaseModel):
    real_seconds_per_game_day: float = 1.0
    paused: bool = False

class GameDate(BaseModel):
    year: int = 2024
    month: int = 1
    day: int = 1
    
    @property
    def as_date(self) -> date:
        return date(self.year, self.month, self.day)

class Meta(BaseModel):
    country_code: str                    # "ISR", "USA", etc.
    country_name: str                    # "Israel"
    government_type: str                 # "Parliamentary Democracy"
    game_start_year: int = 2024
    current_date: GameDate
    time_config: TimeConfig
    total_game_days_elapsed: int = 0
```

**JSON Example** (`db/game_state.json`):
```json
{
  "meta": {
    "country_code": "ISR",
    "country_name": "Israel",
    "government_type": "Parliamentary Democracy",
    "game_start_year": 2024,
    "current_date": {
      "year": 2024,
      "month": 1,
      "day": 1
    },
    "time_config": {
      "real_seconds_per_game_day": 1.0,
      "paused": false
    },
    "total_game_days_elapsed": 0
  }
}
```

---

## 2. DEMOGRAPHICS

Population breakdown by age groups.

```python
# backend/models/demographics.py
from pydantic import BaseModel
from typing import Dict

class AgeGroup(BaseModel):
    count: int
    percent: float

class Demographics(BaseModel):
    total_population: int
    
    by_age_group: Dict[str, AgeGroup]  # "0_14", "15_24", "25_54", "55_64", "65_plus"
    
    working_age_population: int        # 15-64
    labor_force_participation: float   # 0.0-1.0
    active_labor_force: int
    
    median_age: float
    life_expectancy: float
    birth_rate_per_1000: float
    death_rate_per_1000: float
    net_migration_per_1000: float
    
    urbanization_percent: float
    population_growth_rate: float      # Annual %
```

**JSON Example**:
```json
{
  "demographics": {
    "total_population": 9500000,
    "by_age_group": {
      "0_14": {"count": 2660000, "percent": 28},
      "15_24": {"count": 1140000, "percent": 12},
      "25_54": {"count": 3610000, "percent": 38},
      "55_64": {"count": 950000, "percent": 10},
      "65_plus": {"count": 1140000, "percent": 12}
    },
    "working_age_population": 5700000,
    "labor_force_participation": 0.64,
    "active_labor_force": 3648000,
    "median_age": 30.5,
    "life_expectancy": 83.0,
    "birth_rate_per_1000": 17.6,
    "death_rate_per_1000": 5.2,
    "net_migration_per_1000": 2.0,
    "urbanization_percent": 93,
    "population_growth_rate": 1.5
  }
}
```

---

## 3. WORKFORCE (Constraint Source)

This is **critical** - determines what the country CAN do.

```python
# backend/models/workforce.py
from pydantic import BaseModel
from typing import Dict

class EducationLevel(BaseModel):
    count: int
    percent: float

class ExpertisePool(BaseModel):
    available: int                # Total in country
    employed: int                 # Currently working
    quality_index: int            # 0-100, affects output quality
    
    @property
    def unemployed(self) -> int:
        return self.available - self.employed

class MigrationBalance(BaseModel):
    skilled_inflow: int           # Per year
    skilled_outflow: int
    net: int

class Workforce(BaseModel):
    total_employed: int
    unemployed: int
    unemployment_rate: float
    
    by_education: Dict[str, EducationLevel]
    # Keys: "no_formal", "high_school", "vocational", "bachelors", "masters", "doctorate"
    
    expertise_pools: Dict[str, ExpertisePool]
    # Keys defined below
    
    annual_graduates: Dict[str, int]
    # Keys: "high_school", "vocational", "bachelors", "masters", "doctorate"
    
    migration_balance: MigrationBalance
```

**Expertise Pool Keys**:
```python
EXPERTISE_POOLS = [
    # Engineering
    "engineering_mechanical",
    "engineering_electrical",
    "engineering_software",
    "engineering_aerospace",
    "engineering_nuclear",
    "engineering_civil",
    
    # Scientists
    "scientists_physics",
    "scientists_chemistry",
    "scientists_biology",
    "scientists_computer",
    
    # Medical
    "medical_doctors",
    "medical_nurses",
    "medical_specialists",
    
    # Technicians
    "technicians_industrial",
    "technicians_electronics",
    "technicians_it",
    
    # Military
    "military_officers",
    "military_pilots",
    "military_naval",
    "military_specialists",
    
    # Other
    "skilled_trades",
    "agriculture_specialists",
    "finance_professionals",
    "legal_professionals",
    "educators",
]
```

---

## 4. INFRASTRUCTURE (Constraint Source)

Physical prerequisites for activities.

```python
# backend/models/infrastructure.py
from pydantic import BaseModel
from typing import Dict

class EnergyInfra(BaseModel):
    generation_capacity_gw: float
    current_demand_gw: float
    reserve_margin_percent: float
    grid_reliability: int                # 0-100
    sources: Dict[str, float]            # % breakdown
    level: int                           # 0-100 overall

class TransportInfra(BaseModel):
    road_quality: int
    rail_coverage: int
    ports_capacity: int
    airports_capacity: int
    level: int

class DigitalInfra(BaseModel):
    internet_penetration: int
    broadband_speed_index: int
    five_g_coverage: int
    cybersecurity_index: int
    level: int

class WaterInfra(BaseModel):
    access_percent: int
    desalination_capacity: int
    treatment_capacity: int
    level: int

class IndustrialFacilities(BaseModel):
    manufacturing_plants: int
    tech_parks: int
    research_centers: int
    military_factories: int
    shipyards: int
    aircraft_facilities: int
    level: int

class HealthcareFacilities(BaseModel):
    hospitals: int
    hospital_beds_per_1000: float
    icu_beds: int
    clinics: int
    level: int

class EducationFacilities(BaseModel):
    universities: int
    research_universities: int
    vocational_schools: int
    schools: int
    level: int

class Infrastructure(BaseModel):
    energy: EnergyInfra
    transportation: TransportInfra
    digital: DigitalInfra
    water: WaterInfra
    industrial_facilities: IndustrialFacilities
    healthcare_facilities: HealthcareFacilities
    education_facilities: EducationFacilities
```

---

## 5. ECONOMY

```python
# backend/models/economy.py
from pydantic import BaseModel

class Debt(BaseModel):
    total_billions: float
    debt_to_gdp_percent: float
    external_debt_billions: float
    debt_service_billions: float         # Annual payment
    credit_rating: str                   # "AAA", "A+", "BBB", etc.

class Reserves(BaseModel):
    foreign_reserves_billions: float
    months_of_imports_covered: float
    gold_reserves_tons: float

class Economy(BaseModel):
    gdp_billions_usd: float
    gdp_per_capita_usd: float
    gdp_growth_rate: float               # Current %
    gdp_growth_potential: float          # Max possible %
    
    inflation_rate: float
    interest_rate: float
    exchange_rate_to_usd: float          # Local currency per USD
    
    debt: Debt
    reserves: Reserves
    currency_stability: int              # 0-100
```

---

## 6. BUDGET

Government allocation.

```python
# backend/models/budget.py
from pydantic import BaseModel
from typing import Dict, Optional

class BudgetBreakdown(BaseModel):
    personnel: Optional[float] = None
    operations_maintenance: Optional[float] = None
    procurement: Optional[float] = None
    research_development: Optional[float] = None
    infrastructure: Optional[float] = None
    hospitals: Optional[float] = None
    public_health: Optional[float] = None
    research: Optional[float] = None
    subsidies: Optional[float] = None
    k12: Optional[float] = None
    higher_education: Optional[float] = None
    research_grants: Optional[float] = None

class BudgetAllocation(BaseModel):
    amount: float                        # Billions
    percent_of_budget: float
    percent_of_gdp: float
    breakdown: Optional[BudgetBreakdown] = None

class RevenueSources(BaseModel):
    income_tax: float
    corporate_tax: float
    vat: float
    customs: float
    other: float

class Budget(BaseModel):
    fiscal_year: int
    total_revenue_billions: float
    total_expenditure_billions: float
    deficit_billions: float
    deficit_to_gdp_percent: float
    
    revenue_sources: RevenueSources
    
    allocation: Dict[str, BudgetAllocation]
    # Keys: "defense", "healthcare", "education", "welfare", "infrastructure",
    #       "debt_service", "public_safety", "administration", "research_development", "other"
```

---

## 7. SECTORS (With Constraints)

Economic sectors - player develops these.

```python
# backend/models/sectors.py
from pydantic import BaseModel
from typing import Dict, Optional

class WorkforceRequirement(BaseModel):
    """Minimum workforce needed for sector to function"""
    pool_name: str                       # e.g., "engineering_software"
    minimum_count: int

class InfrastructureRequirement(BaseModel):
    """Infrastructure level needed"""
    infra_path: str                      # e.g., "digital.level"
    minimum_value: float

class SectorConstraints(BaseModel):
    workforce_required: Dict[str, int]   # pool_name -> min count
    infrastructure_required: Dict[str, float]  # infra_path -> min value

class ProductionCapabilities(BaseModel):
    """What defense industry can produce locally"""
    small_arms: bool = False
    ammunition: bool = False
    armored_vehicles: bool = False
    main_battle_tanks: bool = False
    artillery: bool = False
    missiles_short_range: bool = False
    missiles_medium_range: bool = False
    missiles_long_range: bool = False
    air_defense_systems: bool = False
    drones_tactical: bool = False
    drones_combat: bool = False
    fighter_aircraft: bool = False
    helicopters: bool = False
    naval_vessels_small: bool = False
    naval_vessels_large: bool = False
    submarines: bool = False
    satellites: bool = False
    cyber_weapons: bool = False

class Subsector(BaseModel):
    level: int                           # 0-100
    export_share: float                  # % of sector exports

class Sector(BaseModel):
    level: int                           # 0-100
    gdp_contribution_percent: float
    gdp_contribution_billions: float
    employment: int
    growth_rate: Optional[float] = None
    exports_billions: Optional[float] = None
    
    constraints: SectorConstraints
    
    subsectors: Optional[Dict[str, Subsector]] = None
    capabilities: Optional[ProductionCapabilities] = None  # For defense_industry only
    outputs: Optional[Dict[str, float]] = None  # Sector-specific outputs
```

**Sector Keys**:
```python
SECTORS = [
    "technology",
    "defense_industry",
    "healthcare",
    "education",
    "manufacturing",
    "agriculture",
    "finance",
    "energy",
    "construction",
    "tourism",
    "retail",
]
```

---

## 8. MILITARY

Personnel and readiness.

```python
# backend/models/military.py
from pydantic import BaseModel
from typing import Dict

class BranchPersonnel(BaseModel):
    active: int
    reserves: int

class PersonnelConstraints(BaseModel):
    max_active_percent_of_workforce: float
    current_percent: float
    conscription: bool
    service_length_months: int

class Personnel(BaseModel):
    active_duty: int
    reserves: int
    paramilitary: int
    by_branch: Dict[str, BranchPersonnel]  # "army", "air_force", "navy"
    constraints: PersonnelConstraints

class ReadinessFactors(BaseModel):
    training_level: int
    equipment_maintenance: int
    supply_stock_days: int
    fuel_reserves_days: int

class Readiness(BaseModel):
    overall: int                         # 0-100
    army: int
    air_force: int
    navy: int
    factors: ReadinessFactors

class AnnualMilitaryCosts(BaseModel):
    personnel_billions: float
    operations_billions: float
    maintenance_billions: float
    fuel_billions: float

class Military(BaseModel):
    personnel: Personnel
    readiness: Readiness
    strength_index: int                  # Composite score for deterrence
    nuclear_status: str                  # "none", "developing", "declared", "undeclared"
    annual_costs: AnnualMilitaryCosts
```

---

## 9. MILITARY INVENTORY

Actual equipment with full details.

```python
# backend/models/military_inventory.py
from pydantic import BaseModel
from typing import Dict, List, Optional

class OperationPrerequisites(BaseModel):
    workforce: Dict[str, int]            # pool_name -> count needed
    infrastructure: Optional[Dict[str, int]] = None
    training_months: Optional[int] = None
    parts_source: List[str]              # Country codes for spare parts

class PurchasePrerequisites(BaseModel):
    relations: Dict[str, int]            # country_code -> min relation score
    political_approval: bool = False
    not_operating: List[str] = []        # Incompatible systems

class MilitaryAsset(BaseModel):
    model: str                           # "F-35I Adir"
    type: str                            # "5th_gen_multirole"
    quantity: int
    on_order: int = 0
    delivery_year_remaining: Optional[int] = None
    source_country: str                  # "USA", "LOCAL", etc.
    unit_cost_millions: float
    annual_maintenance_cost_millions: Optional[float] = None
    crew_required: Optional[int] = None
    lifespan_years: Optional[int] = None
    avg_age_years: Optional[float] = None
    readiness_percent: int
    
    # Capabilities
    combat_radius_km: Optional[int] = None
    range_km: Optional[int] = None
    special_capability: Optional[str] = None
    
    # Constraints
    prerequisites_to_operate: Optional[OperationPrerequisites] = None
    prerequisites_to_purchase: Optional[PurchasePrerequisites] = None

class MunitionStock(BaseModel):
    quantity: int
    unit_cost_usd: Optional[int] = None
    monthly_production_capacity: Optional[int] = None
    source: str
    reorder_point: Optional[int] = None
    reorder_lead_time_months: Optional[int] = None
    days_of_combat: Optional[int] = None

class MilitaryInventory(BaseModel):
    aircraft: Dict[str, List[MilitaryAsset]]
    # Keys: "fighters", "helicopters", "transport", "uav", "tankers"
    
    ground_forces: Dict[str, List[MilitaryAsset]]
    # Keys: "tanks", "apc_ifv", "artillery", "mlrs", "engineering"
    
    air_defense: Dict[str, List[MilitaryAsset]]
    # Keys: "systems"
    
    navy: Dict[str, List[MilitaryAsset]]
    # Keys: "submarines", "surface", "patrol", "amphibious"
    
    missiles: Dict[str, List[MilitaryAsset]]
    # Keys: "strategic", "tactical", "cruise"
    
    munitions_stockpile: Dict[str, MunitionStock]
    
    total_combat_aircraft: int
    total_tanks: int
    total_armored_vehicles: int
    annual_maintenance_total_billions: float
```

---

## 10. RELATIONS (Bilateral)

Per-country relationship data.

```python
# backend/models/relations.py
from pydantic import BaseModel
from typing import Dict, List, Optional

class Aid(BaseModel):
    military_aid_annual_billions: float
    economic_aid_annual_billions: float

class BilateralTrade(BaseModel):
    your_exports_billions: float
    your_imports_billions: float
    balance_billions: float

class Dependencies(BaseModel):
    spare_parts_critical: List[str]      # Equipment dependent on this country
    joint_programs: List[str]

class RelationshipFactors(BaseModel):
    historical: int                      # -50 to +50
    strategic_value: int
    economic_ties: int
    shared_values: int
    lobby_influence: int

class ConflictFactors(BaseModel):
    proxy_wars: List[str] = []
    nuclear_program: bool = False
    rhetoric: str = "neutral"

class BilateralRelation(BaseModel):
    country_code: str
    country_name: str
    score: int                           # -100 to +100
    status: str                          # "strategic_ally", "ally", "neutral", "tense", "hostile"
    treaty: Optional[str] = None
    
    # Weapons access
    allows_weapons_purchase: bool
    weapons_catalog_access: str          # "full", "limited", "restricted", "none"
    restricted_items: List[str] = []
    
    # Economics
    aid: Optional[Aid] = None
    trade: BilateralTrade
    
    # Dependencies
    dependencies: Optional[Dependencies] = None
    
    # Factors
    relationship_factors: Optional[RelationshipFactors] = None
    conflict_factors: Optional[ConflictFactors] = None
    
    # Threat level (for hostile)
    threat_level: Optional[str] = None   # "primary", "secondary", "low"
```

---

## 11. INDICES (Quality Indicators)

Composite scores and indices.

```python
# backend/models/indices.py
from pydantic import BaseModel

class Indices(BaseModel):
    happiness: int                       # 0-100
    hdi: float                           # 0-1 (Human Development Index)
    inequality_gini: float               # 0-1 (lower = more equal)
    corruption: int                      # 0-100 (lower = cleaner)
    stability: int                       # 0-100
    public_trust: int                    # 0-100
    press_freedom: int                   # 0-100
    ease_of_business: int                # 0-100
```

---

## 12. COMPLETE COUNTRY STATE

Full country file structure.

```python
# backend/models/country.py
from pydantic import BaseModel
from .meta import Meta
from .demographics import Demographics
from .workforce import Workforce
from .infrastructure import Infrastructure
from .economy import Economy
from .budget import Budget
from .sectors import Sector
from .military import Military
from .military_inventory import MilitaryInventory
from .relations import BilateralRelation
from .indices import Indices
from typing import Dict

class CountryState(BaseModel):
    meta: Meta
    demographics: Demographics
    workforce: Workforce
    infrastructure: Infrastructure
    economy: Economy
    budget: Budget
    sectors: Dict[str, Sector]
    military: Military
    military_inventory: MilitaryInventory
    relations: Dict[str, BilateralRelation]
    indices: Indices
```

---

## 13. CATALOG FILES (Static Data)

### Weapons Catalog

```python
# Stored in db/catalog/weapons_catalog.json
class WeaponDefinition(BaseModel):
    id: str                              # "F-35"
    name: str                            # "F-35 Lightning II"
    type: str                            # "5th_gen_fighter"
    category: str                        # "aircraft"
    manufacturer_country: str            # "USA"
    unit_cost_millions: float
    export_restricted: bool
    
    allowed_buyers: List[str]            # Country codes, or "any_with_relations_X"
    prerequisites_for_buyer: Dict
    consequences_for_buyer: Optional[Dict] = None
    
    delivery_time_years: str             # "3-6"
    production_rate_per_year: int
    
    specs: Dict                          # Weapon-specific specifications
```

### Events Catalog

```python
# Stored in db/catalog/events_catalog.json
class EventDefinition(BaseModel):
    id: str                              # "recession"
    name: str                            # "Economic Recession"
    category: str                        # "economic", "political", "military", "natural"
    
    base_probability_annual: float
    
    triggers: Dict[str, Dict]            # condition -> probability modifier
    prevention: Dict[str, Dict]          # condition -> probability modifier
    
    effects: Dict[str, float]            # KPI changes
    effects_by_severity: Optional[Dict[str, Dict]] = None
    
    duration_range: str                  # "4-12 quarters"
```

---

## File Locations Summary

```
db/
├── countries/
│   └── ISR.json          # Complete CountryState
├── catalog/
│   ├── weapons_catalog.json
│   ├── events_catalog.json
│   └── constraints.json
├── relations/
│   └── global_relations.json  # All country-to-country relations
└── game_state.json       # Current game meta (selected country, time)
```

---

## Next: 03-MVP-DISPLAY.md

Plan for displaying these KPIs on screen.
