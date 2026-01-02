"""
City data models for map system.
Defines cities, their attributes, and garrison information.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from .map import Coordinates


class CityType(str, Enum):
    CAPITAL = "capital"
    MAJOR = "major"
    MEDIUM = "medium"
    SMALL = "small"
    TOWN = "town"


class CityInfrastructure(BaseModel):
    """City-level infrastructure metrics."""
    power_reliability: int = Field(default=80, ge=0, le=100)
    water_supply: int = Field(default=80, ge=0, le=100)
    healthcare_access: int = Field(default=70, ge=0, le=100)
    education_access: int = Field(default=70, ge=0, le=100)
    transportation: int = Field(default=70, ge=0, le=100)


class City(BaseModel):
    """A city within a country."""
    id: str
    name: str
    country_code: str
    location: Coordinates
    population: int
    city_type: CityType
    is_capital: bool = False

    # Economic indicators
    gdp_contribution_percent: float = Field(default=0, ge=0, le=100)
    unemployment_rate: float = Field(default=5.0, ge=0, le=100)

    # Infrastructure
    infrastructure: CityInfrastructure = Field(default_factory=CityInfrastructure)

    # Military presence
    garrison_unit_ids: List[str] = []  # Unit IDs stationed in city
    has_military_base: bool = False
    military_base_id: Optional[str] = None

    # Strategic value for military operations
    strategic_value: int = Field(default=50, ge=0, le=100)
    is_port: bool = False
    has_airport: bool = False

    # Defense
    air_defense_coverage: bool = False
    fortification_level: int = Field(default=0, ge=0, le=100)


class CityList(BaseModel):
    """Collection of cities for a country."""
    country_code: str
    cities: List[City]
    total_urban_population: int = 0

    def get_capital(self) -> Optional[City]:
        """Get the capital city."""
        for city in self.cities:
            if city.is_capital:
                return city
        return None

    def get_by_id(self, city_id: str) -> Optional[City]:
        """Get city by ID."""
        for city in self.cities:
            if city.id == city_id:
                return city
        return None

    def get_cities_in_radius(self, center: Coordinates, radius_km: float) -> List[City]:
        """Get all cities within radius of a point."""
        return [
            city for city in self.cities
            if center.distance_to(city.location) <= radius_km
        ]
