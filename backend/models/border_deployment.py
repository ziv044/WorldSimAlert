"""
Border deployment zone models for tracking troop positions along borders.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

from .map import Coordinates


class DeploymentAlertLevel(str, Enum):
    """Alert level for a border deployment zone."""
    PEACETIME = "peacetime"           # Minimal presence, routine patrols
    ELEVATED = "elevated"             # Increased patrols, heightened awareness
    HIGH_ALERT = "high_alert"         # Combat ready, active threat
    ACTIVE_DEFENSE = "active_defense" # Engaged, responding to incursion


class BorderDeploymentZone(BaseModel):
    """A deployment zone along a border with a neighbor country."""
    id: str                                    # e.g., "bdz_ISR_LBN"
    country_code: str                          # Owner country
    neighbor_code: str                         # Which neighbor this borders
    name: str                                  # e.g., "Northern Front - Lebanon"

    # Location - center point for marker placement
    center: Coordinates
    border_length_km: float = 0.0

    # Troop deployment
    active_troops: int = Field(default=0, ge=0)
    reserve_troops: int = Field(default=0, ge=0)
    max_capacity: int = Field(default=50000, ge=0)

    # Equipment deployment
    deployed_unit_ids: List[str] = []
    equipment_summary: Dict[str, int] = {}    # e.g., {"tanks": 50, "apcs": 120}

    # Defense systems in zone
    air_defense_batteries: int = Field(default=0, ge=0)
    artillery_units: int = Field(default=0, ge=0)

    # Status
    alert_level: DeploymentAlertLevel = DeploymentAlertLevel.PEACETIME
    readiness_percent: float = Field(default=80.0, ge=0, le=100)
    fortification_level: int = Field(default=50, ge=0, le=100)

    # Threat assessment (0-100, calculated from neighbor relations)
    threat_level: int = Field(default=0, ge=0, le=100)
    last_incident: Optional[datetime] = None

    @property
    def total_troops(self) -> int:
        """Total troops deployed in this zone."""
        return self.active_troops + self.reserve_troops

    @property
    def capacity_percent(self) -> float:
        """Percentage of capacity used."""
        if self.max_capacity == 0:
            return 0.0
        return (self.total_troops / self.max_capacity) * 100

    def can_deploy(self, additional: int) -> bool:
        """Check if zone can accept additional troops."""
        return self.total_troops + additional <= self.max_capacity


class BorderDeploymentList(BaseModel):
    """All border deployment zones for a country."""
    country_code: str
    zones: List[BorderDeploymentZone] = []

    # Aggregate stats
    total_active_deployed: int = 0
    total_reserves_deployed: int = 0

    def get_by_id(self, zone_id: str) -> Optional[BorderDeploymentZone]:
        """Get zone by ID."""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None

    def get_by_neighbor(self, neighbor_code: str) -> List[BorderDeploymentZone]:
        """Get all zones bordering a specific neighbor."""
        return [z for z in self.zones if z.neighbor_code == neighbor_code]

    def get_high_threat(self, min_threat: int = 50) -> List[BorderDeploymentZone]:
        """Get zones with threat level at or above threshold."""
        return [z for z in self.zones if z.threat_level >= min_threat]

    def recalculate_totals(self) -> None:
        """Recalculate aggregate totals from zone data."""
        self.total_active_deployed = sum(z.active_troops for z in self.zones)
        self.total_reserves_deployed = sum(z.reserve_troops for z in self.zones)


class TroopTransfer(BaseModel):
    """Tracks troop movement between zones or from reserves pool."""
    id: str
    country_code: str
    from_zone_id: Optional[str] = None       # None if from reserves pool
    to_zone_id: str
    troop_count: int
    is_reserves: bool = False                # True if calling up reserves
    started_at: datetime
    estimated_arrival: datetime
    progress_percent: float = Field(default=0.0, ge=0, le=100)
    status: str = "in_transit"               # in_transit, arrived, cancelled
