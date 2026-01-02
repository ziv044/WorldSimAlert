from pydantic import BaseModel
from typing import Dict, List, Optional


class WeaponDefinition(BaseModel):
    """Weapon catalog entry"""
    id: str  # "F-35"
    name: str  # "F-35 Lightning II"
    type: str  # "5th_gen_fighter"
    category: str  # "aircraft"
    manufacturer_country: str  # "USA"
    unit_cost_millions: float
    export_restricted: bool

    allowed_buyers: List[str]  # Country codes, or "any_with_relations_X"
    prerequisites_for_buyer: Dict
    consequences_for_buyer: Optional[Dict] = None

    delivery_time_years: str  # "3-6"
    production_rate_per_year: int

    specs: Dict  # Weapon-specific specifications


class EventDefinition(BaseModel):
    """Event catalog entry"""
    id: str  # "recession"
    name: str  # "Economic Recession"
    category: str  # "economic", "political", "military", "natural"

    base_probability_annual: float

    triggers: Dict[str, Dict]  # condition -> probability modifier
    prevention: Dict[str, Dict]  # condition -> probability modifier

    effects: Dict[str, float]  # KPI changes
    effects_by_severity: Optional[Dict[str, Dict]] = None

    duration_range: str  # "4-12 quarters"


class ActiveEvent(BaseModel):
    """An event currently affecting the game"""
    event_id: str
    started_date: str
    expected_end_date: str
    severity: str = "normal"  # "mild", "normal", "severe"
    effects_applied: Dict[str, float]
