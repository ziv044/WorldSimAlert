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
    amount: float  # Billions
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
