from pydantic import BaseModel
from typing import Dict


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


class EducationLevel(BaseModel):
    count: int
    percent: float


class ExpertisePool(BaseModel):
    available: int  # Total in country
    employed: int  # Currently working
    quality_index: int  # 0-100, affects output quality

    @property
    def unemployed(self) -> int:
        return self.available - self.employed


class MigrationBalance(BaseModel):
    skilled_inflow: int  # Per year
    skilled_outflow: int
    net: int


class Workforce(BaseModel):
    total_employed: int
    unemployed: int
    unemployment_rate: float

    by_education: Dict[str, EducationLevel]
    # Keys: "no_formal", "high_school", "vocational", "bachelors", "masters", "doctorate"

    expertise_pools: Dict[str, ExpertisePool]
    # Keys defined in EXPERTISE_POOLS

    annual_graduates: Dict[str, int]
    # Keys: "high_school", "vocational", "bachelors", "masters", "doctorate"

    migration_balance: MigrationBalance
