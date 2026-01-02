from pydantic import BaseModel
from typing import Dict


class EnergyInfra(BaseModel):
    generation_capacity_gw: float
    current_demand_gw: float
    reserve_margin_percent: float
    grid_reliability: int  # 0-100
    sources: Dict[str, float]  # % breakdown
    level: int  # 0-100 overall


class TransportInfra(BaseModel):
    road_quality: int
    rail_coverage: int
    ports_capacity: int
    airports_capacity: int
    level: int


class DigitalInfra(BaseModel):
    internet_penetration: int
    broadband_speed_index: int
    five_g_coverage: int
    cybersecurity_index: int
    level: int


class WaterInfra(BaseModel):
    access_percent: int
    desalination_capacity: int
    treatment_capacity: int
    level: int


class IndustrialFacilities(BaseModel):
    manufacturing_plants: int
    tech_parks: int
    research_centers: int
    military_factories: int
    shipyards: int
    aircraft_facilities: int
    level: int


class HealthcareFacilities(BaseModel):
    hospitals: int
    hospital_beds_per_1000: float
    icu_beds: int
    clinics: int
    level: int


class EducationFacilities(BaseModel):
    universities: int
    research_universities: int
    vocational_schools: int
    schools: int
    level: int


class Infrastructure(BaseModel):
    energy: EnergyInfra
    transportation: TransportInfra
    digital: DigitalInfra
    water: WaterInfra
    industrial_facilities: IndustrialFacilities
    healthcare_facilities: HealthcareFacilities
    education_facilities: EducationFacilities
