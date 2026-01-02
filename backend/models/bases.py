"""
Military base data models for map system.
Defines military installations and their capabilities.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

from .map import Coordinates


class BaseType(str, Enum):
    AIR_BASE = "air_base"
    NAVAL_BASE = "naval_base"
    ARMY_BASE = "army_base"
    COMMAND_CENTER = "command_center"
    LOGISTICS_HUB = "logistics_hub"
    TRAINING_CENTER = "training_center"
    MISSILE_SITE = "missile_site"
    RADAR_STATION = "radar_station"


class BaseStatus(str, Enum):
    OPERATIONAL = "operational"
    REDUCED = "reduced"  # Limited operations
    MAINTENANCE = "maintenance"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"


class BaseCapabilities(BaseModel):
    """What a base can support."""
    max_aircraft: int = 0
    max_helicopters: int = 0
    max_ground_vehicles: int = 0
    max_naval_vessels: int = 0
    max_personnel: int = 0
    has_runway: bool = False
    runway_length_m: int = 0
    has_hangar: bool = False
    has_bunker: bool = False
    has_port: bool = False
    has_dry_dock: bool = False
    fuel_storage_days: int = 30
    ammo_storage_days: int = 30
    repair_capability: bool = False
    air_defense_systems: int = 0


class MilitaryBase(BaseModel):
    """A military installation."""
    id: str
    name: str
    country_code: str
    location: Coordinates
    base_type: BaseType
    status: BaseStatus = BaseStatus.OPERATIONAL

    # Capacity and current usage
    capabilities: BaseCapabilities = Field(default_factory=BaseCapabilities)
    stationed_unit_ids: List[str] = []
    current_personnel: int = 0

    # Operational status
    readiness_percent: int = Field(default=80, ge=0, le=100)
    supply_level_percent: int = Field(default=100, ge=0, le=100)
    fuel_level_percent: int = Field(default=100, ge=0, le=100)

    # Defense
    fortification_level: int = Field(default=50, ge=0, le=100)
    camouflage_level: int = Field(default=30, ge=0, le=100)
    air_defense_coverage: bool = True

    # Command structure
    command_level: int = Field(default=1, ge=1, le=5)  # 1=local, 5=strategic
    parent_base_id: Optional[str] = None

    # City association
    nearest_city_id: Optional[str] = None
    distance_to_city_km: float = 0


class BaseList(BaseModel):
    """Collection of military bases for a country."""
    country_code: str
    bases: List[MilitaryBase]

    def get_by_id(self, base_id: str) -> Optional[MilitaryBase]:
        """Get base by ID."""
        for base in self.bases:
            if base.id == base_id:
                return base
        return None

    def get_by_type(self, base_type: BaseType) -> List[MilitaryBase]:
        """Get all bases of a specific type."""
        return [b for b in self.bases if b.base_type == base_type]

    def get_operational(self) -> List[MilitaryBase]:
        """Get all operational bases."""
        return [b for b in self.bases if b.status == BaseStatus.OPERATIONAL]

    def get_air_bases(self) -> List[MilitaryBase]:
        """Get all air bases."""
        return self.get_by_type(BaseType.AIR_BASE)

    def get_naval_bases(self) -> List[MilitaryBase]:
        """Get all naval bases."""
        return self.get_by_type(BaseType.NAVAL_BASE)

    def get_bases_in_radius(self, center: Coordinates, radius_km: float) -> List[MilitaryBase]:
        """Get all bases within radius of a point."""
        return [
            base for base in self.bases
            if center.distance_to(base.location) <= radius_km
        ]
