"""
Military API routes for border deployments and personnel management.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.military_service import military_service


router = APIRouter(prefix="/api/military", tags=["Military"])


# =============================================================================
# Request Models
# =============================================================================

class DeployTroopsRequest(BaseModel):
    zone_id: str
    active_troops: int = 0
    reserve_troops: int = 0


class WithdrawTroopsRequest(BaseModel):
    zone_id: str
    active_troops: int = 0
    reserve_troops: int = 0


class CallupReservesRequest(BaseModel):
    count: int
    zone_id: Optional[str] = None


class StandDownReservesRequest(BaseModel):
    count: int


class SetAlertLevelRequest(BaseModel):
    zone_id: str
    alert_level: str


# =============================================================================
# Deployment Endpoints
# =============================================================================

@router.get("/deployments/{country_code}")
async def get_border_deployments(country_code: str):
    """Get all border deployment zones and their status."""
    try:
        deployments = military_service.load_deployments(country_code.upper())
        return {
            "country_code": country_code.upper(),
            "total_zones": len(deployments.zones),
            "total_active_deployed": deployments.total_active_deployed,
            "total_reserves_deployed": deployments.total_reserves_deployed,
            "zones": [zone.model_dump() for zone in deployments.zones]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments/{country_code}/{zone_id}")
async def get_deployment_zone(country_code: str, zone_id: str):
    """Get details of a specific deployment zone."""
    deployments = military_service.load_deployments(country_code.upper())
    zone = deployments.get_by_id(zone_id)

    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")

    return zone.model_dump()


@router.post("/deployments/{country_code}/deploy")
async def deploy_troops(country_code: str, request: DeployTroopsRequest):
    """Deploy troops to a border zone."""
    result = military_service.deploy_troops(
        country_code.upper(),
        request.zone_id,
        request.active_troops,
        request.reserve_troops
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/deployments/{country_code}/withdraw")
async def withdraw_troops(country_code: str, request: WithdrawTroopsRequest):
    """Withdraw troops from a border zone."""
    result = military_service.withdraw_troops(
        country_code.upper(),
        request.zone_id,
        request.active_troops,
        request.reserve_troops
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/deployments/{country_code}/alert")
async def set_zone_alert_level(country_code: str, request: SetAlertLevelRequest):
    """Set alert level for a border zone."""
    result = military_service.set_alert_level(
        country_code.upper(),
        request.zone_id,
        request.alert_level
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# =============================================================================
# Reserve Management Endpoints
# =============================================================================

@router.post("/reserves/{country_code}/callup")
async def callup_reserves(country_code: str, request: CallupReservesRequest):
    """Call up reserve personnel."""
    result = military_service.callup_reserves(
        country_code.upper(),
        request.count,
        request.zone_id
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.post("/reserves/{country_code}/stand-down")
async def stand_down_reserves(country_code: str, request: StandDownReservesRequest):
    """Release reserve personnel back to civilian status."""
    result = military_service.stand_down_reserves(
        country_code.upper(),
        request.count
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# =============================================================================
# Personnel Status Endpoints
# =============================================================================

@router.get("/personnel/{country_code}")
async def get_personnel_status(country_code: str):
    """Get overall personnel deployment status."""
    try:
        status = military_service.get_personnel_status(country_code.upper())
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Threat Assessment
# =============================================================================

@router.post("/deployments/{country_code}/recalculate-threats")
async def recalculate_threat_levels(country_code: str):
    """Recalculate threat levels based on current relations."""
    try:
        military_service.calculate_threat_levels(country_code.upper())
        deployments = military_service.load_deployments(country_code.upper())
        return {
            "success": True,
            "zones": [
                {"id": z.id, "name": z.name, "threat_level": z.threat_level}
                for z in deployments.zones
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
