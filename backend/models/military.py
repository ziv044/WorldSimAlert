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
    # Border deployment tracking
    reserves_called: int = 0          # Currently mobilized reserves
    deployed_to_borders: int = 0      # Active troops at border zones


class ReadinessFactors(BaseModel):
    training_level: int
    equipment_maintenance: int
    supply_stock_days: int
    fuel_reserves_days: int


class Readiness(BaseModel):
    overall: int  # 0-100
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
    strength_index: int  # Composite score for deterrence
    nuclear_status: str  # "none", "developing", "declared", "undeclared"
    annual_costs: AnnualMilitaryCosts
