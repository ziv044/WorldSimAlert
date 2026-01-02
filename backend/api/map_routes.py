"""
Map API routes for geographic data, cities, bases, units, and operations.
"""
from typing import Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.map_service import map_service
from backend.models.map import Coordinates
from backend.models.units import UnitStatus
from backend.models.active_operation import (
    ActiveOperation, OperationType, OperationStatus, OperationResult
)


router = APIRouter(prefix="/api/map", tags=["Map"])


# =============================================================================
# Request Models
# =============================================================================

class DeployUnitRequest(BaseModel):
    destination_lat: float
    destination_lng: float
    destination_name: Optional[str] = None


class MoveUnitRequest(BaseModel):
    destination_lat: float
    destination_lng: float


class CreateOperationRequest(BaseModel):
    name: str
    operation_type: str
    target_lat: float
    target_lng: float
    target_name: Optional[str] = None
    target_country_code: Optional[str] = None
    unit_ids: List[str]
    duration_hours: int = 24
    is_covert: bool = False


# =============================================================================
# Map Data Endpoints
# =============================================================================

@router.get("/data/{country_code}")
async def get_map_data(country_code: str):
    """Get complete map data for a country."""
    try:
        data = map_service.get_full_map_data(country_code.upper())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/borders/{country_code}")
async def get_borders(country_code: str):
    """Get country borders and neighbors."""
    borders = map_service.load_borders(country_code.upper())
    if not borders:
        raise HTTPException(status_code=404, detail=f"Borders for {country_code} not found")

    neighbors = map_service.get_neighbor_data(country_code.upper())
    return {
        "borders": borders.model_dump(),
        "neighbors": neighbors
    }


# =============================================================================
# Cities Endpoints
# =============================================================================

@router.get("/cities/{country_code}")
async def get_cities(country_code: str):
    """Get all cities for a country."""
    city_list = map_service.load_cities(country_code.upper())
    return {
        "country_code": country_code.upper(),
        "total_urban_population": city_list.total_urban_population,
        "cities": [c.model_dump() for c in city_list.cities]
    }


@router.get("/cities/{country_code}/{city_id}")
async def get_city(country_code: str, city_id: str):
    """Get a specific city."""
    city = map_service.get_city(country_code.upper(), city_id)
    if not city:
        raise HTTPException(status_code=404, detail=f"City {city_id} not found")
    return city.model_dump()


@router.get("/cities/{country_code}/radius")
async def get_cities_in_radius(
    country_code: str,
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(50, description="Radius in kilometers")
):
    """Get cities within radius of a point."""
    city_list = map_service.load_cities(country_code.upper())
    center = Coordinates(lat=lat, lng=lng)
    nearby = city_list.get_cities_in_radius(center, radius_km)
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "cities": [c.model_dump() for c in nearby]
    }


# =============================================================================
# Bases Endpoints
# =============================================================================

@router.get("/bases/{country_code}")
async def get_bases(country_code: str):
    """Get all military bases for a country."""
    base_list = map_service.load_bases(country_code.upper())
    return {
        "country_code": country_code.upper(),
        "bases": [b.model_dump() for b in base_list.bases]
    }


@router.get("/bases/{country_code}/{base_id}")
async def get_base(country_code: str, base_id: str):
    """Get a specific base."""
    base = map_service.get_base(country_code.upper(), base_id)
    if not base:
        raise HTTPException(status_code=404, detail=f"Base {base_id} not found")
    return base.model_dump()


@router.get("/bases/{country_code}/type/{base_type}")
async def get_bases_by_type(country_code: str, base_type: str):
    """Get bases by type (air_base, naval_base, army_base, etc.)."""
    from backend.models.bases import BaseType
    try:
        bt = BaseType(base_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid base type: {base_type}")

    base_list = map_service.load_bases(country_code.upper())
    filtered = base_list.get_by_type(bt)
    return {
        "base_type": base_type,
        "bases": [b.model_dump() for b in filtered]
    }


# =============================================================================
# Units Endpoints
# =============================================================================

@router.get("/units/{country_code}")
async def get_units(country_code: str):
    """Get all military units for a country."""
    unit_list = map_service.load_units(country_code.upper())
    return {
        "country_code": country_code.upper(),
        "total_units": len(unit_list.units),
        "units": [u.model_dump() for u in unit_list.units]
    }


@router.get("/units/{country_code}/{unit_id}")
async def get_unit(country_code: str, unit_id: str):
    """Get a specific unit."""
    unit = map_service.get_unit(country_code.upper(), unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")
    return unit.model_dump()


@router.get("/units/{country_code}/available")
async def get_available_units(country_code: str):
    """Get all units available for deployment."""
    unit_list = map_service.load_units(country_code.upper())
    available = unit_list.get_available()
    return {
        "available_count": len(available),
        "units": [u.model_dump() for u in available]
    }


@router.get("/units/{country_code}/base/{base_id}")
async def get_units_at_base(country_code: str, base_id: str):
    """Get all units at a specific base."""
    unit_list = map_service.load_units(country_code.upper())
    at_base = unit_list.get_at_base(base_id)
    return {
        "base_id": base_id,
        "unit_count": len(at_base),
        "units": [u.model_dump() for u in at_base]
    }


@router.get("/units/{country_code}/radius")
async def get_units_in_radius(
    country_code: str,
    lat: float = Query(..., description="Center latitude"),
    lng: float = Query(..., description="Center longitude"),
    radius_km: float = Query(100, description="Radius in kilometers")
):
    """Get units within radius of a point."""
    unit_list = map_service.load_units(country_code.upper())
    center = Coordinates(lat=lat, lng=lng)
    nearby = unit_list.get_in_radius(center, radius_km)
    return {
        "center": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "unit_count": len(nearby),
        "units": [u.model_dump() for u in nearby]
    }


@router.post("/units/{country_code}/{unit_id}/deploy")
async def deploy_unit(country_code: str, unit_id: str, request: DeployUnitRequest):
    """Deploy a unit to a location."""
    unit = map_service.get_unit(country_code.upper(), unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")

    if not unit.can_deploy():
        raise HTTPException(
            status_code=400,
            detail=f"Unit cannot deploy. Status: {unit.status}, Health: {unit.health_percent}%"
        )

    # Update unit location and status
    unit.location = Coordinates(lat=request.destination_lat, lng=request.destination_lng)
    unit.status = UnitStatus.DEPLOYED
    unit.current_base_id = None

    map_service.update_unit(country_code.upper(), unit)

    return {
        "success": True,
        "unit_id": unit_id,
        "new_location": unit.location.model_dump(),
        "status": unit.status
    }


@router.post("/units/{country_code}/{unit_id}/return")
async def return_unit_to_base(country_code: str, unit_id: str):
    """Return a unit to its home base."""
    unit = map_service.get_unit(country_code.upper(), unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")

    # Get home base location
    base = map_service.get_base(country_code.upper(), unit.home_base_id)
    if not base:
        raise HTTPException(status_code=404, detail=f"Home base {unit.home_base_id} not found")

    # Update unit
    unit.location = base.location
    unit.status = UnitStatus.IDLE
    unit.current_base_id = unit.home_base_id
    unit.assigned_operation_id = None

    map_service.update_unit(country_code.upper(), unit)

    return {
        "success": True,
        "unit_id": unit_id,
        "base_id": unit.home_base_id,
        "status": unit.status
    }


# =============================================================================
# Operations Endpoints
# =============================================================================

@router.get("/operations/{country_code}")
async def get_operations(country_code: str, active_only: bool = True):
    """Get operations for a country."""
    ops_list = map_service.load_operations(country_code.upper())

    if active_only:
        ops = ops_list.get_active()
    else:
        ops = ops_list.operations

    return {
        "country_code": country_code.upper(),
        "total": len(ops),
        "operations": [op.model_dump() for op in ops]
    }


@router.get("/operations/{country_code}/{operation_id}")
async def get_operation(country_code: str, operation_id: str):
    """Get a specific operation."""
    op = map_service.get_operation(country_code.upper(), operation_id)
    if not op:
        raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")
    return op.model_dump()


@router.post("/operations/{country_code}/create")
async def create_operation(country_code: str, request: CreateOperationRequest):
    """Create a new military operation."""
    # Validate operation type
    try:
        op_type = OperationType(request.operation_type)
    except ValueError:
        valid_types = [t.value for t in OperationType]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid operation type. Valid types: {valid_types}"
        )

    # Validate units exist and are available
    unit_list = map_service.load_units(country_code.upper())
    assigned_units = []
    origin_location = None

    for unit_id in request.unit_ids:
        unit = unit_list.get_by_id(unit_id)
        if not unit:
            raise HTTPException(status_code=404, detail=f"Unit {unit_id} not found")
        if not unit.can_deploy():
            raise HTTPException(
                status_code=400,
                detail=f"Unit {unit_id} cannot deploy: {unit.status}"
            )
        assigned_units.append(unit)
        if origin_location is None:
            origin_location = unit.location

    # Create operation
    operation = ActiveOperation(
        id=f"op_{uuid.uuid4().hex[:8]}",
        name=request.name,
        country_code=country_code.upper(),
        operation_type=op_type,
        status=OperationStatus.PLANNING,
        created_at=datetime.utcnow(),
        origin_location=origin_location,
        target_location=Coordinates(lat=request.target_lat, lng=request.target_lng),
        target_name=request.target_name,
        target_country_code=request.target_country_code,
        assigned_unit_ids=request.unit_ids,
        duration_hours=request.duration_hours,
        is_covert=request.is_covert,
        unit_types_involved={u.unit_type: 1 for u in assigned_units}
    )

    # Calculate success probability based on unit strength
    avg_strength = sum(u.get_effective_strength() for u in assigned_units) / len(assigned_units)
    operation.success_probability = min(0.95, avg_strength * 0.85 + 0.1)

    # Update units to assigned status
    for unit in assigned_units:
        unit.assigned_operation_id = operation.id
        unit.status = UnitStatus.DEPLOYED
        map_service.update_unit(country_code.upper(), unit)

    # Save operation
    map_service.add_operation(country_code.upper(), operation)

    return {
        "success": True,
        "operation": operation.model_dump()
    }


@router.post("/operations/{country_code}/{operation_id}/start")
async def start_operation(country_code: str, operation_id: str):
    """Start a planned operation."""
    op = map_service.get_operation(country_code.upper(), operation_id)
    if not op:
        raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")

    if op.status != OperationStatus.PLANNING:
        raise HTTPException(
            status_code=400,
            detail=f"Operation cannot be started. Current status: {op.status}"
        )

    op.status = OperationStatus.ACTIVE
    op.started_at = datetime.utcnow()
    op.estimated_completion = datetime.utcnow()  # Would calculate based on duration

    map_service.update_operation(country_code.upper(), op)

    return {
        "success": True,
        "operation_id": operation_id,
        "status": op.status
    }


@router.delete("/operations/{country_code}/{operation_id}")
async def cancel_operation(country_code: str, operation_id: str):
    """Cancel an operation."""
    op = map_service.get_operation(country_code.upper(), operation_id)
    if not op:
        raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")

    if not op.can_cancel():
        raise HTTPException(
            status_code=400,
            detail=f"Operation cannot be cancelled. Status: {op.status}"
        )

    # Return units to idle
    unit_list = map_service.load_units(country_code.upper())
    for unit_id in op.assigned_unit_ids:
        unit = unit_list.get_by_id(unit_id)
        if unit:
            unit.assigned_operation_id = None
            unit.status = UnitStatus.IDLE
            map_service.update_unit(country_code.upper(), unit)

    op.status = OperationStatus.CANCELLED
    op.completed_at = datetime.utcnow()
    map_service.update_operation(country_code.upper(), op)

    return {
        "success": True,
        "operation_id": operation_id,
        "status": "cancelled"
    }


# =============================================================================
# Overlay Endpoints (for map visualization)
# =============================================================================

@router.get("/overlay/{country_code}/military")
async def get_military_overlay(country_code: str):
    """Get military overlay data (unit positions, threat levels)."""
    units = map_service.load_units(country_code.upper())
    bases = map_service.load_bases(country_code.upper())
    operations = map_service.load_operations(country_code.upper())

    return {
        "units": [
            {
                "id": u.id,
                "location": u.location.model_dump(),
                "category": u.category,
                "status": u.status,
                "strength": u.get_effective_strength()
            }
            for u in units.units
        ],
        "bases": [
            {
                "id": b.id,
                "location": b.location.model_dump(),
                "type": b.base_type,
                "status": b.status,
                "readiness": b.readiness_percent
            }
            for b in bases.bases
        ],
        "active_operations": [
            {
                "id": op.id,
                "type": op.operation_type,
                "target": op.target_location.model_dump(),
                "progress": op.progress_percent
            }
            for op in operations.get_active()
        ]
    }


@router.get("/overlay/{country_code}/economic")
async def get_economic_overlay(country_code: str):
    """Get economic overlay data (city GDP contributions)."""
    cities = map_service.load_cities(country_code.upper())

    return {
        "cities": [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location.model_dump(),
                "gdp_percent": c.gdp_contribution_percent,
                "unemployment": c.unemployment_rate,
                "population": c.population
            }
            for c in cities.cities
        ]
    }


@router.get("/overlay/{country_code}/infrastructure")
async def get_infrastructure_overlay(country_code: str):
    """Get infrastructure overlay data."""
    cities = map_service.load_cities(country_code.upper())
    bases = map_service.load_bases(country_code.upper())

    return {
        "cities": [
            {
                "id": c.id,
                "location": c.location.model_dump(),
                "is_port": c.is_port,
                "has_airport": c.has_airport,
                "infrastructure": c.infrastructure.model_dump()
            }
            for c in cities.cities
        ],
        "military_facilities": [
            {
                "id": b.id,
                "location": b.location.model_dump(),
                "type": b.base_type,
                "has_runway": b.capabilities.has_runway,
                "has_port": b.capabilities.has_port
            }
            for b in bases.bases
        ]
    }
