from pydantic import BaseModel
from typing import Dict


class AgeGroup(BaseModel):
    count: int
    percent: float


class Demographics(BaseModel):
    total_population: int

    by_age_group: Dict[str, AgeGroup]  # "0_14", "15_24", "25_54", "55_64", "65_plus"

    working_age_population: int  # 15-64
    labor_force_participation: float  # 0.0-1.0
    active_labor_force: int

    median_age: float
    life_expectancy: float
    birth_rate_per_1000: float
    death_rate_per_1000: float
    net_migration_per_1000: float

    urbanization_percent: float
    population_growth_rate: float  # Annual %
