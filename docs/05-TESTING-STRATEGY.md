# 05 - Testing Strategy

## Overview

This document defines the testing approach for the game, focusing on core functionality that must work correctly for the game to be playable and balanced.

---

## Testing Principles

1. **Test business logic, not framework** - Focus on game rules, not FastAPI/Pydantic
2. **Test constraints heavily** - Wrong constraint = broken game
3. **Test calculations** - Economy math must be correct
4. **Test edge cases** - Zero values, negative values, overflow
5. **Keep tests fast** - No database/network in unit tests

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_models/
│   ├── test_country.py      # Model validation
│   └── test_inventory.py    # Inventory models
├── test_services/
│   └── test_db_service.py   # File operations
├── test_engine/
│   ├── test_constraints.py  # Constraint engine (CRITICAL)
│   ├── test_economy.py      # Economic calculations
│   ├── test_budget.py       # Budget operations
│   ├── test_sectors.py      # Sector development
│   ├── test_procurement.py  # Weapon purchases
│   ├── test_events.py       # Event probability
│   └── test_tick.py         # Tick processing
└── test_api/
    └── test_endpoints.py    # API integration tests
```

---

## Fixtures (conftest.py)

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path
from copy import deepcopy

@pytest.fixture
def sample_country_data():
    """Base country data for testing"""
    return {
        "meta": {
            "country_code": "TST",
            "country_name": "Test Country",
            "government_type": "Democracy",
            "game_start_year": 2024,
            "current_date": {"year": 2024, "month": 1, "day": 1},
            "time_config": {"real_seconds_per_game_day": 1.0, "paused": False},
            "total_game_days_elapsed": 0
        },
        "demographics": {
            "total_population": 10_000_000,
            "working_age_population": 6_000_000,
            "labor_force_participation": 0.65,
            "active_labor_force": 3_900_000,
            "median_age": 35,
            "life_expectancy": 80,
            "birth_rate_per_1000": 12,
            "death_rate_per_1000": 8,
            "net_migration_per_1000": 2,
            "urbanization_percent": 80,
            "population_growth_rate": 1.0,
            "by_age_group": {
                "0_14": {"count": 2_000_000, "percent": 20},
                "15_24": {"count": 1_500_000, "percent": 15},
                "25_54": {"count": 4_000_000, "percent": 40},
                "55_64": {"count": 1_500_000, "percent": 15},
                "65_plus": {"count": 1_000_000, "percent": 10}
            }
        },
        "workforce": {
            "total_employed": 3_700_000,
            "unemployed": 200_000,
            "unemployment_rate": 5.1,
            "by_education": {
                "no_formal": {"count": 185_000, "percent": 5},
                "high_school": {"count": 1_110_000, "percent": 30},
                "vocational": {"count": 555_000, "percent": 15},
                "bachelors": {"count": 1_110_000, "percent": 30},
                "masters": {"count": 555_000, "percent": 15},
                "doctorate": {"count": 185_000, "percent": 5}
            },
            "expertise_pools": {
                "engineering_software": {"available": 100_000, "employed": 95_000, "quality_index": 80},
                "engineering_mechanical": {"available": 50_000, "employed": 48_000, "quality_index": 75},
                "engineering_aerospace": {"available": 10_000, "employed": 9_500, "quality_index": 85},
                "military_pilots": {"available": 1_000, "employed": 900, "quality_index": 90},
                "technicians_electronics": {"available": 80_000, "employed": 75_000, "quality_index": 70}
            },
            "annual_graduates": {
                "high_school": 100_000,
                "vocational": 30_000,
                "bachelors": 50_000,
                "masters": 15_000,
                "doctorate": 2_000
            },
            "migration_balance": {"skilled_inflow": 5_000, "skilled_outflow": 3_000, "net": 2_000}
        },
        "infrastructure": {
            "energy": {"level": 70, "generation_capacity_gw": 15, "grid_reliability": 85},
            "transportation": {"level": 65, "road_quality": 70},
            "digital": {"level": 80, "internet_penetration": 90, "cybersecurity_index": 75},
            "water": {"level": 75},
            "industrial_facilities": {"level": 60, "military_factories": 20, "aircraft_facilities": 2},
            "healthcare_facilities": {"level": 70, "hospitals": 50},
            "education_facilities": {"level": 72, "universities": 30, "research_universities": 5}
        },
        "economy": {
            "gdp_billions_usd": 400,
            "gdp_per_capita_usd": 40_000,
            "gdp_growth_rate": 3.0,
            "gdp_growth_potential": 4.0,
            "inflation_rate": 3.0,
            "interest_rate": 4.0,
            "exchange_rate_to_usd": 1.0,
            "debt": {
                "total_billions": 200,
                "debt_to_gdp_percent": 50,
                "external_debt_billions": 80,
                "debt_service_billions": 10,
                "credit_rating": "A"
            },
            "reserves": {
                "foreign_reserves_billions": 100,
                "months_of_imports_covered": 10,
                "gold_reserves_tons": 50
            },
            "currency_stability": 85
        },
        "budget": {
            "fiscal_year": 2024,
            "total_revenue_billions": 140,
            "total_expenditure_billions": 150,
            "deficit_billions": 10,
            "deficit_to_gdp_percent": 2.5,
            "revenue_sources": {
                "income_tax": 50,
                "corporate_tax": 30,
                "vat": 40,
                "customs": 10,
                "other": 10
            },
            "allocation": {
                "defense": {
                    "amount": 20,
                    "percent_of_budget": 13.3,
                    "percent_of_gdp": 5.0,
                    "breakdown": {
                        "personnel": 8,
                        "operations_maintenance": 5,
                        "procurement": 4,
                        "research_development": 2,
                        "infrastructure": 1
                    }
                },
                "healthcare": {"amount": 15, "percent_of_budget": 10.0, "percent_of_gdp": 3.75},
                "education": {"amount": 12, "percent_of_budget": 8.0, "percent_of_gdp": 3.0},
                "welfare": {"amount": 30, "percent_of_budget": 20.0, "percent_of_gdp": 7.5},
                "infrastructure": {"amount": 10, "percent_of_budget": 6.7, "percent_of_gdp": 2.5},
                "debt_service": {"amount": 10, "percent_of_budget": 6.7, "percent_of_gdp": 2.5},
                "other": {"amount": 53, "percent_of_budget": 35.3}
            }
        },
        "sectors": {
            "technology": {
                "level": 75,
                "gdp_contribution_percent": 15,
                "gdp_contribution_billions": 60,
                "employment": 300_000,
                "constraints": {
                    "workforce_required": {"engineering_software": 80_000},
                    "infrastructure_required": {"digital.level": 70}
                }
            },
            "defense_industry": {
                "level": 70,
                "gdp_contribution_percent": 8,
                "gdp_contribution_billions": 32,
                "employment": 100_000,
                "constraints": {
                    "workforce_required": {
                        "engineering_aerospace": 5_000,
                        "engineering_mechanical": 20_000,
                        "technicians_electronics": 30_000
                    },
                    "infrastructure_required": {
                        "industrial_facilities.military_factories": 15,
                        "industrial_facilities.aircraft_facilities": 1
                    }
                },
                "capabilities": {
                    "small_arms": True,
                    "armored_vehicles": True,
                    "missiles_short_range": True,
                    "fighter_aircraft": False,
                    "submarines": False
                }
            },
            "manufacturing": {
                "level": 60,
                "gdp_contribution_percent": 12,
                "gdp_contribution_billions": 48,
                "employment": 400_000,
                "constraints": {
                    "workforce_required": {"engineering_mechanical": 15_000}
                }
            }
        },
        "military": {
            "personnel": {
                "active_duty": 150_000,
                "reserves": 400_000,
                "paramilitary": 5_000,
                "by_branch": {
                    "army": {"active": 110_000, "reserves": 350_000},
                    "air_force": {"active": 30_000, "reserves": 40_000},
                    "navy": {"active": 10_000, "reserves": 10_000}
                },
                "constraints": {
                    "max_active_percent_of_workforce": 5,
                    "current_percent": 4.1
                }
            },
            "readiness": {
                "overall": 80,
                "army": 78,
                "air_force": 85,
                "navy": 75,
                "factors": {
                    "training_level": 82,
                    "equipment_maintenance": 78,
                    "supply_stock_days": 30,
                    "fuel_reserves_days": 20
                }
            },
            "strength_index": 70,
            "nuclear_status": "none"
        },
        "military_inventory": {
            "aircraft": {
                "fighters": [
                    {
                        "model": "F-16C",
                        "type": "4th_gen_multirole",
                        "quantity": 60,
                        "source_country": "USA",
                        "unit_cost_millions": 70,
                        "readiness_percent": 80,
                        "prerequisites_to_operate": {
                            "workforce": {"military_pilots": 80, "technicians_electronics": 200},
                            "parts_source": ["USA"]
                        }
                    }
                ]
            },
            "ground_forces": {
                "tanks": [
                    {
                        "model": "M1A2 Abrams",
                        "type": "main_battle_tank",
                        "quantity": 200,
                        "source_country": "USA",
                        "readiness_percent": 75
                    }
                ]
            },
            "air_defense": {
                "systems": [
                    {
                        "model": "Patriot PAC-3",
                        "type": "high_altitude_defense",
                        "batteries": 4,
                        "source_country": "USA"
                    }
                ]
            }
        },
        "relations": {
            "USA": {
                "country_code": "USA",
                "country_name": "United States",
                "score": 80,
                "status": "ally",
                "allows_weapons_purchase": True,
                "weapons_catalog_access": "full",
                "trade": {"your_exports_billions": 15, "your_imports_billions": 25, "balance_billions": -10}
            },
            "CHN": {
                "country_code": "CHN",
                "country_name": "China",
                "score": 30,
                "status": "neutral",
                "allows_weapons_purchase": False,
                "weapons_catalog_access": "none",
                "trade": {"your_exports_billions": 5, "your_imports_billions": 20, "balance_billions": -15}
            },
            "RUS": {
                "country_code": "RUS",
                "country_name": "Russia",
                "score": 20,
                "status": "tense",
                "allows_weapons_purchase": False,
                "weapons_catalog_access": "none",
                "trade": {"your_exports_billions": 2, "your_imports_billions": 5, "balance_billions": -3}
            }
        },
        "indices": {
            "happiness": 65,
            "hdi": 0.85,
            "inequality_gini": 0.35,
            "corruption": 30,
            "stability": 70,
            "public_trust": 55
        },
        "active_projects": []
    }


@pytest.fixture
def sample_weapons_catalog():
    """Weapons catalog for testing"""
    return {
        "F-35": {
            "id": "F-35",
            "name": "F-35 Lightning II",
            "type": "5th_gen_fighter",
            "category": "aircraft",
            "subcategory": "fighters",
            "manufacturer_country": "USA",
            "unit_cost_millions": 120,
            "export_restricted": True,
            "allowed_buyers": ["TST", "USA", "GBR", "ISR", "JPN"],
            "prerequisites_for_buyer": {
                "min_relations": 70,
                "not_operating": ["S-400", "Su-35"]
            },
            "delivery_time_years": "3-5",
            "production_rate_per_year": 150
        },
        "S-400": {
            "id": "S-400",
            "name": "S-400 Triumf",
            "type": "air_defense_system",
            "category": "air_defense",
            "subcategory": "systems",
            "manufacturer_country": "RUS",
            "unit_cost_millions": 400,
            "export_restricted": False,
            "allowed_buyers": [],  # Open to anyone with relations
            "prerequisites_for_buyer": {
                "min_relations": 40
            },
            "delivery_time_years": "2-3"
        },
        "Leopard-2": {
            "id": "Leopard-2",
            "name": "Leopard 2A7",
            "type": "main_battle_tank",
            "category": "ground_forces",
            "subcategory": "tanks",
            "manufacturer_country": "DEU",
            "unit_cost_millions": 8,
            "export_restricted": False,
            "allowed_buyers": [],
            "prerequisites_for_buyer": {
                "min_relations": 40
            },
            "delivery_time_years": "1-2"
        }
    }


@pytest.fixture
def sample_events_catalog():
    """Events catalog for testing"""
    return {
        "recession": {
            "id": "recession",
            "name": "Economic Recession",
            "category": "economic",
            "base_probability_annual": 0.05,
            "triggers": {
                "economy.debt.debt_to_gdp_percent > 80": {"add": 0.15},
                "economy.inflation_rate > 8": {"add": 0.10},
                "economy.gdp_growth_rate < 0": {"add": 0.20}
            },
            "prevention": {
                "economy.reserves.months_of_imports_covered > 12": {"subtract": 0.05},
                "economy.debt.debt_to_gdp_percent < 40": {"subtract": 0.08}
            },
            "effects": {
                "economy.gdp_growth_rate": -3.0,
                "workforce.unemployment_rate": 5.0,
                "indices.happiness": -10,
                "indices.stability": -8
            },
            "duration_months": 12
        },
        "civil_unrest": {
            "id": "civil_unrest",
            "name": "Civil Unrest",
            "category": "political",
            "base_probability_annual": 0.03,
            "triggers": {
                "indices.happiness < 40": {"add": 0.20},
                "workforce.unemployment_rate > 12": {"add": 0.15}
            },
            "prevention": {
                "indices.stability > 70": {"subtract": 0.10}
            },
            "effects": {
                "indices.stability": -15,
                "indices.public_trust": -10,
                "economy.gdp_growth_rate": -1.0
            },
            "duration_months": 6
        }
    }
```

---

## Constraint Engine Tests (CRITICAL)

```python
# tests/test_engine/test_constraints.py
import pytest
from backend.engine.constraint_engine import ConstraintEngine, ConstraintType

class TestBudgetConstraints:
    """Test budget availability checks"""
    
    def test_budget_available(self, sample_country_data):
        """Should pass when budget is available"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(2.0, "procurement")
        
        assert result.satisfied is True
        assert result.current_value == 4.0  # From fixture
        assert result.required_value == 2.0
    
    def test_budget_insufficient(self, sample_country_data):
        """Should fail when budget is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(10.0, "procurement")
        
        assert result.satisfied is False
        assert "Need $10.0B" in result.message
    
    def test_budget_exact_amount(self, sample_country_data):
        """Should pass when budget exactly matches"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(4.0, "procurement")
        
        assert result.satisfied is True
    
    def test_budget_zero(self, sample_country_data):
        """Should pass when requesting zero budget"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_budget(0, "procurement")
        
        assert result.satisfied is True


class TestWorkforceConstraints:
    """Test workforce availability checks"""
    
    def test_workforce_available(self, sample_country_data):
        """Should pass when workforce is available"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"engineering_software": 3_000}  # Have 5000 free
        result = engine.check_workforce(requirements)
        
        assert result.satisfied is True
    
    def test_workforce_insufficient(self, sample_country_data):
        """Should fail when workforce is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"engineering_software": 10_000}  # Only 5000 free
        result = engine.check_workforce(requirements)
        
        assert result.satisfied is False
        assert "engineering_software" in str(result.missing_items)
    
    def test_workforce_multiple_pools(self, sample_country_data):
        """Should check multiple pools"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {
            "engineering_software": 3_000,
            "military_pilots": 50
        }
        result = engine.check_workforce(requirements)
        
        assert result.satisfied is True
    
    def test_workforce_one_fails(self, sample_country_data):
        """Should fail if any pool is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {
            "engineering_software": 3_000,
            "military_pilots": 500  # Only 100 free
        }
        result = engine.check_workforce(requirements)
        
        assert result.satisfied is False
        assert any("military_pilots" in item for item in result.missing_items)
    
    def test_workforce_unknown_pool(self, sample_country_data):
        """Should fail for unknown pool"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"nonexistent_pool": 100}
        result = engine.check_workforce(requirements)
        
        assert result.satisfied is False
        assert "not found" in str(result.missing_items)


class TestRelationsConstraints:
    """Test diplomatic relations checks"""
    
    def test_relations_sufficient(self, sample_country_data):
        """Should pass when relations are high enough"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("USA", 70)
        
        assert result.satisfied is True
        assert result.current_value == 80
    
    def test_relations_insufficient(self, sample_country_data):
        """Should fail when relations are too low"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("RUS", 50)  # Score is 20
        
        assert result.satisfied is False
        assert result.current_value == 20
        assert result.required_value == 50
    
    def test_relations_unknown_country(self, sample_country_data):
        """Should fail for unknown country"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_relations("XYZ", 50)
        
        assert result.satisfied is False
        assert result.current_value == 0


class TestInfrastructureConstraints:
    """Test infrastructure level checks"""
    
    def test_infrastructure_sufficient(self, sample_country_data):
        """Should pass when infrastructure is sufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"digital.level": 70}
        result = engine.check_infrastructure(requirements)
        
        assert result.satisfied is True
    
    def test_infrastructure_insufficient(self, sample_country_data):
        """Should fail when infrastructure is insufficient"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"digital.level": 95}
        result = engine.check_infrastructure(requirements)
        
        assert result.satisfied is False
    
    def test_infrastructure_nested_path(self, sample_country_data):
        """Should handle nested paths"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"industrial_facilities.military_factories": 15}
        result = engine.check_infrastructure(requirements)
        
        assert result.satisfied is True
    
    def test_infrastructure_invalid_path(self, sample_country_data):
        """Should fail for invalid path"""
        engine = ConstraintEngine(sample_country_data)
        requirements = {"nonexistent.path": 50}
        result = engine.check_infrastructure(requirements)
        
        assert result.satisfied is False


class TestExclusionConstraints:
    """Test system exclusion checks"""
    
    def test_no_conflicts(self, sample_country_data):
        """Should pass when no conflicting systems"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion(["S-400", "Su-35"])
        
        assert result.satisfied is True
    
    def test_has_conflict(self, sample_country_data):
        """Should fail when operating conflicting system"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_exclusion(["F-16C"])  # We have this
        
        assert result.satisfied is False
        assert "F-16C" in result.missing_items


class TestSectorLevelConstraints:
    """Test sector development level checks"""
    
    def test_sector_sufficient(self, sample_country_data):
        """Should pass when sector level is high enough"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_sector_level("technology", 70)
        
        assert result.satisfied is True
    
    def test_sector_insufficient(self, sample_country_data):
        """Should fail when sector level is too low"""
        engine = ConstraintEngine(sample_country_data)
        result = engine.check_sector_level("manufacturing", 80)
        
        assert result.satisfied is False
        assert result.current_value == 60


class TestCombinedConstraints:
    """Test checking multiple constraints together"""
    
    def test_all_pass(self, sample_country_data):
        """Should pass when all constraints are met"""
        engine = ConstraintEngine(sample_country_data)
        
        constraints = {
            "budget": {"amount_billions": 2.0, "budget_category": "procurement"},
            "relations": {"USA": 70},
            "workforce": {"engineering_software": 1_000}
        }
        
        all_satisfied, results = engine.check_all(constraints)
        
        assert all_satisfied is True
        assert all(r.satisfied for r in results)
    
    def test_one_fails(self, sample_country_data):
        """Should fail when any constraint fails"""
        engine = ConstraintEngine(sample_country_data)
        
        constraints = {
            "budget": {"amount_billions": 2.0, "budget_category": "procurement"},
            "relations": {"RUS": 70}  # Only 20
        }
        
        all_satisfied, results = engine.check_all(constraints)
        
        assert all_satisfied is False
        failed = [r for r in results if not r.satisfied]
        assert len(failed) == 1
        assert failed[0].constraint_type == ConstraintType.RELATIONS
    
    def test_f35_purchase_scenario(self, sample_country_data):
        """Should correctly evaluate F-35 purchase constraints"""
        engine = ConstraintEngine(sample_country_data)
        
        # F-35 requirements
        constraints = {
            "budget": {"amount_billions": 2.4, "budget_category": "procurement"},
            "relations": {"USA": 70},
            "exclusion": ["S-400", "Su-35"]
        }
        
        all_satisfied, results = engine.check_all(constraints)
        
        assert all_satisfied is True
```

---

## Economy Engine Tests

```python
# tests/test_engine/test_economy.py
import pytest
from backend.engine.economy_engine import EconomyEngine

class TestGDPCalculations:
    """Test GDP growth calculations"""
    
    def test_positive_growth(self, sample_country_data):
        """GDP should grow with good conditions"""
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()
        
        assert changes['gdp'] > 0
    
    def test_unemployment_penalty(self, sample_country_data):
        """High unemployment should reduce growth"""
        sample_country_data['workforce']['unemployment_rate'] = 15.0
        
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()
        
        # Should be lower than baseline
        assert changes['gdp'] < 0.3  # Normal monthly growth ~0.25
    
    def test_gdp_per_capita_updates(self, sample_country_data):
        """GDP per capita should update with GDP"""
        engine = EconomyEngine(sample_country_data)
        old_gdp_per_capita = sample_country_data['economy']['gdp_per_capita_usd']
        
        engine.process_monthly_tick()
        
        new_gdp_per_capita = sample_country_data['economy']['gdp_per_capita_usd']
        assert new_gdp_per_capita != old_gdp_per_capita


class TestDebtCalculations:
    """Test debt and deficit calculations"""
    
    def test_deficit_increases_debt(self, sample_country_data):
        """Running a deficit should increase debt"""
        engine = EconomyEngine(sample_country_data)
        old_debt = sample_country_data['economy']['debt']['total_billions']
        
        engine.process_monthly_tick()
        
        new_debt = sample_country_data['economy']['debt']['total_billions']
        assert new_debt > old_debt
    
    def test_debt_ratio_updates(self, sample_country_data):
        """Debt-to-GDP ratio should update"""
        engine = EconomyEngine(sample_country_data)
        
        engine.process_monthly_tick()
        
        debt = sample_country_data['economy']['debt']
        gdp = sample_country_data['economy']['gdp_billions_usd']
        expected_ratio = (debt['total_billions'] / gdp) * 100
        
        assert abs(debt['debt_to_gdp_percent'] - expected_ratio) < 0.1


class TestInflationCalculations:
    """Test inflation mechanics"""
    
    def test_high_debt_increases_inflation(self, sample_country_data):
        """High debt should increase inflation"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 90
        
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()
        
        # Inflation should be higher than base
        assert changes['inflation'] > 3.0
    
    def test_low_debt_stable_inflation(self, sample_country_data):
        """Low debt should keep inflation stable"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 30
        
        engine = EconomyEngine(sample_country_data)
        changes = engine.process_monthly_tick()
        
        # Inflation should be near base
        assert 2.5 < changes['inflation'] < 4.0
```

---

## Procurement Engine Tests

```python
# tests/test_engine/test_procurement.py
import pytest
from backend.engine.procurement_engine import ProcurementEngine

class TestPurchaseValidation:
    """Test weapon purchase validation"""
    
    def test_valid_purchase(self, sample_country_data, sample_weapons_catalog):
        """Should allow valid purchase"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 10)
        
        assert result['success'] is True
        assert result['order']['quantity'] == 10
    
    def test_insufficient_budget(self, sample_country_data, sample_weapons_catalog):
        """Should reject if budget insufficient"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 100)  # Way too many
        
        assert result['success'] is False
        assert any('budget' in str(c).lower() for c in result.get('failed_constraints', []))
    
    def test_insufficient_relations(self, sample_country_data, sample_weapons_catalog):
        """Should reject if relations too low"""
        sample_country_data['relations']['USA']['score'] = 50  # Below 70
        
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)
        
        assert result['success'] is False
        assert any('relations' in str(c).lower() for c in result.get('failed_constraints', []))
    
    def test_not_allowed_buyer(self, sample_country_data, sample_weapons_catalog):
        """Should reject if not in allowed buyers list"""
        sample_country_data['meta']['country_code'] = 'XXX'
        
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)
        
        assert result['success'] is False
        assert 'not an approved buyer' in result['error']
    
    def test_exclusion_conflict(self, sample_country_data, sample_weapons_catalog):
        """Should reject if operating incompatible system"""
        # Add S-400 to inventory
        sample_country_data['military_inventory']['air_defense']['systems'].append({
            "model": "S-400",
            "type": "air_defense_system",
            "batteries": 2
        })
        
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("F-35", 1)
        
        assert result['success'] is False
    
    def test_unknown_weapon(self, sample_country_data, sample_weapons_catalog):
        """Should reject unknown weapon"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        result = engine.request_purchase("UnknownWeapon", 1)
        
        assert result['success'] is False
        assert 'Unknown weapon' in result['error']


class TestDeliveries:
    """Test weapon delivery processing"""
    
    def test_delivery_starts_on_time(self, sample_country_data, sample_weapons_catalog):
        """Deliveries should start in expected year"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)
        
        # Move to delivery year
        delivered = engine.process_deliveries(2028)
        
        assert len(delivered) > 0
        assert delivered[0]['weapon'] == "F-35 Lightning II"
    
    def test_no_delivery_before_time(self, sample_country_data, sample_weapons_catalog):
        """No deliveries before scheduled"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 10)
        
        delivered = engine.process_deliveries(2025)  # Too early
        
        assert len(delivered) == 0
    
    def test_inventory_updated(self, sample_country_data, sample_weapons_catalog):
        """Inventory should be updated on delivery"""
        engine = ProcurementEngine(sample_country_data, sample_weapons_catalog)
        engine.request_purchase("F-35", 5)
        
        engine.process_deliveries(2028)
        
        # Check inventory
        fighters = sample_country_data['military_inventory']['aircraft']['fighters']
        f35 = next((f for f in fighters if f['model'] == "F-35 Lightning II"), None)
        
        assert f35 is not None
        assert f35['quantity'] > 0
```

---

## Event Engine Tests

```python
# tests/test_engine/test_events.py
import pytest
from unittest.mock import patch
from backend.engine.event_engine import EventEngine

class TestProbabilityCalculation:
    """Test event probability calculations"""
    
    def test_base_probability(self, sample_country_data, sample_events_catalog):
        """Should use base probability with no triggers"""
        engine = EventEngine(sample_country_data, sample_events_catalog)
        
        # Get recession probability (debt and growth are fine)
        prob = engine._calculate_probability(sample_events_catalog['recession'])
        
        # Should be near base (0.05/12 = ~0.004)
        assert 0.001 < prob < 0.01
    
    def test_trigger_increases_probability(self, sample_country_data, sample_events_catalog):
        """Triggers should increase probability"""
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 90
        
        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])
        
        # Should be higher than base
        assert prob > 0.01
    
    def test_prevention_decreases_probability(self, sample_country_data, sample_events_catalog):
        """Prevention factors should decrease probability"""
        sample_country_data['economy']['reserves']['months_of_imports_covered'] = 15
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 30
        
        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])
        
        # Should be very low or zero
        assert prob < 0.005
    
    def test_probability_clamped(self, sample_country_data, sample_events_catalog):
        """Probability should be clamped between 0 and 1"""
        # Set extreme values
        sample_country_data['economy']['debt']['debt_to_gdp_percent'] = 200
        sample_country_data['economy']['inflation_rate'] = 50
        sample_country_data['economy']['gdp_growth_rate'] = -10
        
        engine = EventEngine(sample_country_data, sample_events_catalog)
        prob = engine._calculate_probability(sample_events_catalog['recession'])
        
        assert 0 <= prob <= 1


class TestEventEffects:
    """Test event effect application"""
    
    def test_apply_effects(self, sample_country_data, sample_events_catalog):
        """Effects should be applied to country data"""
        engine = EventEngine(sample_country_data, sample_events_catalog)
        
        event = {
            'effects': {
                'economy.gdp_growth_rate': -3.0,
                'indices.happiness': -10
            }
        }
        
        old_happiness = sample_country_data['indices']['happiness']
        engine.apply_event_effects(event)
        
        assert sample_country_data['indices']['happiness'] == old_happiness - 10
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_engine/test_constraints.py

# Run specific test class
pytest tests/test_engine/test_constraints.py::TestBudgetConstraints

# Run with verbose output
pytest -v

# Run only failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "budget"
```

---

## pytest.ini Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

---

## Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| constraint_engine.py | 95%+ |
| economy_engine.py | 90%+ |
| procurement_engine.py | 90%+ |
| event_engine.py | 85%+ |
| budget_engine.py | 85%+ |
| db_service.py | 80%+ |
| API endpoints | 75%+ |

---

## Test-Driven Development Flow

For each new feature:

1. **Write failing test** - Define expected behavior
2. **Implement minimum code** - Make test pass
3. **Refactor** - Clean up while keeping tests green
4. **Add edge case tests** - Cover boundaries
5. **Verify coverage** - Ensure critical paths tested

---

## Next Steps

1. Implement MVP display (doc 03)
2. Write constraint engine tests first
3. Implement constraint engine to pass tests
4. Continue with economy, procurement, events
5. Maintain >90% coverage on game logic
