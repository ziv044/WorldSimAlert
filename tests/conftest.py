# tests/conftest.py
import pytest
import json
from pathlib import Path
from copy import deepcopy
from fastapi.testclient import TestClient
from httpx import AsyncClient

from backend.main import app


@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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
                "debt_to_gdp > 80": {"add": 0.15},
                "inflation > 8": {"add": 0.10},
                "gdp_growth < 0": {"add": 0.20}
            },
            "prevention": {
                "foreign_reserves > 12": {"subtract": 0.05},
                "debt_to_gdp < 40": {"subtract": 0.08}
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
                "happiness < 40": {"add": 0.20},
                "unemployment > 12": {"add": 0.15}
            },
            "prevention": {
                "stability > 70": {"subtract": 0.10}
            },
            "effects": {
                "indices.stability": -15,
                "indices.public_trust": -10,
                "economy.gdp_growth_rate": -1.0
            },
            "duration_months": 6
        }
    }
