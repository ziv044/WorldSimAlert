from pydantic import BaseModel
from typing import Dict, List, Optional


class OperationPrerequisites(BaseModel):
    workforce: Dict[str, int]  # pool_name -> count needed
    infrastructure: Optional[Dict[str, int]] = None
    training_months: Optional[int] = None
    parts_source: List[str]  # Country codes for spare parts


class PurchasePrerequisites(BaseModel):
    relations: Dict[str, int]  # country_code -> min relation score
    political_approval: bool = False
    not_operating: List[str] = []  # Incompatible systems


class MilitaryAsset(BaseModel):
    model: str  # "F-35I Adir"
    type: str  # "5th_gen_multirole"
    quantity: int
    on_order: int = 0
    delivery_year_remaining: Optional[int] = None
    source_country: str  # "USA", "LOCAL", etc.
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
