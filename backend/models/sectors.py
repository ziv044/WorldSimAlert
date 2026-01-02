from pydantic import BaseModel
from typing import Dict, Optional


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


class WorkforceRequirement(BaseModel):
    """Minimum workforce needed for sector to function"""
    pool_name: str  # e.g., "engineering_software"
    minimum_count: int


class InfrastructureRequirement(BaseModel):
    """Infrastructure level needed"""
    infra_path: str  # e.g., "digital.level"
    minimum_value: float


class SectorConstraints(BaseModel):
    workforce_required: Dict[str, int]  # pool_name -> min count
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
    level: int  # 0-100
    export_share: float  # % of sector exports


class Sector(BaseModel):
    level: int  # 0-100
    gdp_contribution_percent: float
    gdp_contribution_billions: float
    employment: int
    growth_rate: Optional[float] = None
    exports_billions: Optional[float] = None

    constraints: SectorConstraints

    subsectors: Optional[Dict[str, Subsector]] = None
    capabilities: Optional[ProductionCapabilities] = None  # For defense_industry only
    outputs: Optional[Dict[str, float]] = None  # Sector-specific outputs
