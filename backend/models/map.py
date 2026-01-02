"""
Geographic data models for map system.
Provides coordinate system, regions, and terrain definitions.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class TerrainType(str, Enum):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    DESERT = "desert"
    MOUNTAIN = "mountain"
    FOREST = "forest"
    WATER = "water"
    COASTAL = "coastal"


class Coordinates(BaseModel):
    """Geographic coordinates (WGS84)."""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")

    def distance_to(self, other: "Coordinates") -> float:
        """Calculate approximate distance in km using Haversine formula."""
        import math
        R = 6371  # Earth's radius in km

        lat1, lat2 = math.radians(self.lat), math.radians(other.lat)
        dlat = math.radians(other.lat - self.lat)
        dlng = math.radians(other.lng - self.lng)

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c


class BoundingBox(BaseModel):
    """Geographic bounding box for a region."""
    north: float = Field(..., ge=-90, le=90)
    south: float = Field(..., ge=-90, le=90)
    east: float = Field(..., ge=-180, le=180)
    west: float = Field(..., ge=-180, le=180)

    def contains(self, coord: Coordinates) -> bool:
        """Check if coordinate is within bounding box."""
        return (self.south <= coord.lat <= self.north and
                self.west <= coord.lng <= self.east)


class MapRegion(BaseModel):
    """A named geographic region (e.g., district, governorate)."""
    id: str
    name: str
    country_code: str
    terrain_type: TerrainType
    center: Coordinates
    bounding_box: BoundingBox
    polygon: Optional[List[Coordinates]] = None  # GeoJSON-style boundary
    population: int = 0
    strategic_value: int = Field(default=50, ge=0, le=100)  # Military importance


class CountryBorders(BaseModel):
    """Country border definition."""
    country_code: str
    name: str
    bounding_box: BoundingBox
    center: Coordinates
    land_area_km2: float
    neighbors: List[str] = []  # Adjacent country codes
    polygon: Optional[List[Coordinates]] = None


class MapData(BaseModel):
    """Complete map data for a game session."""
    country_code: str
    borders: CountryBorders
    regions: List[MapRegion] = []
    neighbor_borders: List[CountryBorders] = []
