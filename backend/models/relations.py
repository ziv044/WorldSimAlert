from pydantic import BaseModel
from typing import List, Optional


class Aid(BaseModel):
    military_aid_annual_billions: float
    economic_aid_annual_billions: float


class BilateralTrade(BaseModel):
    your_exports_billions: float
    your_imports_billions: float
    balance_billions: float


class Dependencies(BaseModel):
    spare_parts_critical: List[str]  # Equipment dependent on this country
    joint_programs: List[str]


class RelationshipFactors(BaseModel):
    historical: int  # -50 to +50
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
    score: int  # -100 to +100
    status: str  # "strategic_ally", "ally", "neutral", "tense", "hostile"
    treaty: Optional[str] = None

    # Weapons access
    allows_weapons_purchase: bool
    weapons_catalog_access: str  # "full", "limited", "restricted", "none"
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
    threat_level: Optional[str] = None  # "primary", "secondary", "low"
