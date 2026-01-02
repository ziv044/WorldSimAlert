from pydantic import BaseModel


class Debt(BaseModel):
    total_billions: float
    debt_to_gdp_percent: float
    external_debt_billions: float
    debt_service_billions: float  # Annual payment
    credit_rating: str  # "AAA", "A+", "BBB", etc.


class Reserves(BaseModel):
    foreign_reserves_billions: float
    months_of_imports_covered: float
    gold_reserves_tons: float


class Economy(BaseModel):
    gdp_billions_usd: float
    gdp_per_capita_usd: float
    gdp_growth_rate: float  # Current %
    gdp_growth_potential: float  # Max possible %

    inflation_rate: float
    interest_rate: float
    exchange_rate_to_usd: float  # Local currency per USD

    debt: Debt
    reserves: Reserves
    currency_stability: int  # 0-100
