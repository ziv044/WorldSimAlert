"""
Military unit data models for map system.
Tracks individual deployable units with positions and status.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

from .map import Coordinates


class UnitCategory(str, Enum):
    AIRCRAFT = "aircraft"
    HELICOPTER = "helicopter"
    GROUND = "ground"
    NAVAL = "naval"
    AIR_DEFENSE = "air_defense"
    MISSILE = "missile"
    SPECIAL_OPS = "special_ops"


class UnitStatus(str, Enum):
    IDLE = "idle"  # At base, ready
    DEPLOYED = "deployed"  # In field position
    IN_TRANSIT = "in_transit"  # Moving between locations
    IN_COMBAT = "in_combat"  # Active operation
    RETURNING = "returning"  # Moving back to base
    MAINTENANCE = "maintenance"  # Under repair
    DAMAGED = "damaged"  # Combat damage, reduced capability
    DESTROYED = "destroyed"


class UnitMovement(BaseModel):
    """Tracks unit movement between locations."""
    origin: Coordinates
    destination: Coordinates
    started_at: datetime
    eta: datetime
    speed_kmh: float


class MilitaryUnit(BaseModel):
    """A deployable military unit."""
    id: str
    name: str  # e.g., "69th Squadron", "7th Armored Brigade"
    country_code: str
    unit_type: str  # e.g., "F-35I", "Merkava_Mk4", "Sa'ar_6"
    category: UnitCategory
    quantity: int  # Number of assets in this unit

    # Location
    location: Coordinates
    home_base_id: str
    current_base_id: Optional[str] = None  # If stationed at a base
    deployed_city_id: Optional[str] = None  # If deployed to defend a city

    # Status
    status: UnitStatus = UnitStatus.IDLE
    health_percent: float = Field(default=100.0, ge=0, le=100)
    readiness_percent: float = Field(default=100.0, ge=0, le=100)
    fuel_percent: float = Field(default=100.0, ge=0, le=100)
    ammo_percent: float = Field(default=100.0, ge=0, le=100)

    # Movement tracking
    movement: Optional[UnitMovement] = None

    # Operation assignment
    assigned_operation_id: Optional[str] = None

    # Combat stats
    experience_level: int = Field(default=50, ge=0, le=100)
    morale: int = Field(default=80, ge=0, le=100)
    kills: int = 0
    losses: int = 0

    # Capabilities (inherited from asset type but can be modified)
    combat_radius_km: Optional[float] = None
    range_km: Optional[float] = None
    speed_kmh: Optional[float] = None

    def can_deploy(self) -> bool:
        """Check if unit can be deployed."""
        return (
            self.status in [UnitStatus.IDLE, UnitStatus.DEPLOYED] and
            self.health_percent >= 50 and
            self.readiness_percent >= 50 and
            self.fuel_percent >= 20 and
            self.ammo_percent >= 20
        )

    def get_effective_strength(self) -> float:
        """Calculate effective combat strength (0-1)."""
        health_factor = self.health_percent / 100
        readiness_factor = self.readiness_percent / 100
        supply_factor = min(self.fuel_percent, self.ammo_percent) / 100
        morale_factor = self.morale / 100
        experience_factor = 0.5 + (self.experience_level / 200)  # 0.5-1.0

        return health_factor * readiness_factor * supply_factor * morale_factor * experience_factor


class UnitList(BaseModel):
    """Collection of military units for a country."""
    country_code: str
    units: List[MilitaryUnit]

    def get_by_id(self, unit_id: str) -> Optional[MilitaryUnit]:
        """Get unit by ID."""
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None

    def get_by_category(self, category: UnitCategory) -> List[MilitaryUnit]:
        """Get all units of a category."""
        return [u for u in self.units if u.category == category]

    def get_by_status(self, status: UnitStatus) -> List[MilitaryUnit]:
        """Get all units with a specific status."""
        return [u for u in self.units if u.status == status]

    def get_available(self) -> List[MilitaryUnit]:
        """Get all units available for deployment."""
        return [u for u in self.units if u.can_deploy()]

    def get_at_base(self, base_id: str) -> List[MilitaryUnit]:
        """Get all units at a specific base."""
        return [u for u in self.units if u.current_base_id == base_id or u.home_base_id == base_id]

    def get_in_radius(self, center: Coordinates, radius_km: float) -> List[MilitaryUnit]:
        """Get all units within radius of a point."""
        return [
            unit for unit in self.units
            if center.distance_to(unit.location) <= radius_km
        ]

    def get_in_operation(self, operation_id: str) -> List[MilitaryUnit]:
        """Get all units assigned to an operation."""
        return [u for u in self.units if u.assigned_operation_id == operation_id]
