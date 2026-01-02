"""
Unit Engine for managing military unit deployment, movement, and state updates.
Handles unit positioning, transit calculations, and status management.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from backend.models.map import Coordinates
from backend.models.units import MilitaryUnit, UnitList, UnitCategory, UnitStatus, UnitMovement
from backend.models.bases import MilitaryBase, BaseList
from backend.services.map_service import map_service


class MovementResult(Enum):
    SUCCESS = "success"
    UNIT_NOT_FOUND = "unit_not_found"
    UNIT_CANNOT_MOVE = "unit_cannot_move"
    DESTINATION_INVALID = "destination_invalid"
    OUT_OF_RANGE = "out_of_range"
    BASE_NOT_FOUND = "base_not_found"
    BASE_AT_CAPACITY = "base_at_capacity"
    INSUFFICIENT_FUEL = "insufficient_fuel"


class UnitEngine:
    """Engine for managing military unit operations."""

    # Default speeds by category (km/h)
    DEFAULT_SPEEDS = {
        UnitCategory.AIRCRAFT: 800,
        UnitCategory.HELICOPTER: 250,
        UnitCategory.GROUND: 50,
        UnitCategory.NAVAL: 45,
        UnitCategory.AIR_DEFENSE: 30,
        UnitCategory.MISSILE: 0,  # Stationary
        UnitCategory.SPECIAL_OPS: 40
    }

    # Fuel consumption per hour of travel (percent)
    FUEL_CONSUMPTION_RATES = {
        UnitCategory.AIRCRAFT: 5.0,
        UnitCategory.HELICOPTER: 4.0,
        UnitCategory.GROUND: 2.0,
        UnitCategory.NAVAL: 1.5,
        UnitCategory.AIR_DEFENSE: 1.0,
        UnitCategory.MISSILE: 0,
        UnitCategory.SPECIAL_OPS: 1.0
    }

    def __init__(self, country_code: str):
        self.country_code = country_code.upper()

    def _get_unit_speed(self, unit: MilitaryUnit) -> float:
        """Get unit speed in km/h."""
        if unit.speed_kmh and unit.speed_kmh > 0:
            return unit.speed_kmh
        return self.DEFAULT_SPEEDS.get(unit.category, 50)

    def _calculate_travel_time(self, unit: MilitaryUnit, distance_km: float) -> timedelta:
        """Calculate travel time for a unit to cover a distance."""
        speed = self._get_unit_speed(unit)
        if speed <= 0:
            return timedelta(hours=9999)  # Effectively infinite for stationary units

        hours = distance_km / speed
        return timedelta(hours=hours)

    def _calculate_fuel_consumption(self, unit: MilitaryUnit, travel_hours: float) -> float:
        """Calculate fuel consumed for travel (percent of tank)."""
        rate = self.FUEL_CONSUMPTION_RATES.get(unit.category, 2.0)
        return rate * travel_hours

    def get_unit(self, unit_id: str) -> Optional[MilitaryUnit]:
        """Get a unit by ID."""
        return map_service.get_unit(self.country_code, unit_id)

    def get_all_units(self) -> UnitList:
        """Get all units."""
        return map_service.load_units(self.country_code)

    def get_available_units(self) -> List[MilitaryUnit]:
        """Get all units available for deployment."""
        unit_list = self.get_all_units()
        return unit_list.get_available()

    def get_units_at_location(self, location: Coordinates, radius_km: float = 10) -> List[MilitaryUnit]:
        """Get all units near a location."""
        unit_list = self.get_all_units()
        return unit_list.get_in_radius(location, radius_km)

    def can_unit_move(self, unit: MilitaryUnit) -> Tuple[bool, str]:
        """Check if a unit can move and return reason if not."""
        if unit.status == UnitStatus.DESTROYED:
            return False, "Unit is destroyed"

        if unit.status == UnitStatus.IN_COMBAT:
            return False, "Unit is in combat"

        if unit.status == UnitStatus.IN_TRANSIT:
            return False, "Unit is already in transit"

        if unit.status == UnitStatus.MAINTENANCE:
            return False, "Unit is under maintenance"

        if unit.health_percent < 20:
            return False, "Unit health too low"

        if unit.fuel_percent < 10:
            return False, "Insufficient fuel"

        return True, "OK"

    def deploy_unit(
        self,
        unit_id: str,
        destination: Coordinates,
        instant: bool = False
    ) -> Tuple[MovementResult, Dict[str, Any]]:
        """
        Deploy a unit to a new location.

        Args:
            unit_id: The unit to deploy
            destination: Target coordinates
            instant: If True, move instantly (for testing/debug)

        Returns:
            Tuple of (result_code, details_dict)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return MovementResult.UNIT_NOT_FOUND, {"error": "Unit not found"}

        can_move, reason = self.can_unit_move(unit)
        if not can_move:
            return MovementResult.UNIT_CANNOT_MOVE, {"error": reason}

        # Calculate distance and travel time
        distance_km = unit.location.distance_to(destination)
        travel_time = self._calculate_travel_time(unit, distance_km)
        travel_hours = travel_time.total_seconds() / 3600

        # Check fuel
        fuel_needed = self._calculate_fuel_consumption(unit, travel_hours)
        if fuel_needed > unit.fuel_percent:
            return MovementResult.INSUFFICIENT_FUEL, {
                "error": "Insufficient fuel",
                "fuel_needed": fuel_needed,
                "fuel_available": unit.fuel_percent
            }

        # Check range for aircraft
        if unit.combat_radius_km and distance_km > unit.combat_radius_km * 2:
            return MovementResult.OUT_OF_RANGE, {
                "error": "Destination out of range",
                "distance_km": distance_km,
                "max_range_km": unit.combat_radius_km * 2
            }

        now = datetime.utcnow()

        if instant:
            # Instant movement (for testing)
            unit.location = destination
            unit.status = UnitStatus.DEPLOYED
            unit.current_base_id = None
            unit.fuel_percent -= fuel_needed
            unit.movement = None
        else:
            # Set up transit
            unit.movement = UnitMovement(
                origin=unit.location,
                destination=destination,
                started_at=now,
                eta=now + travel_time,
                speed_kmh=self._get_unit_speed(unit)
            )
            unit.status = UnitStatus.IN_TRANSIT
            unit.current_base_id = None

        map_service.update_unit(self.country_code, unit)

        return MovementResult.SUCCESS, {
            "unit_id": unit_id,
            "destination": {"lat": destination.lat, "lng": destination.lng},
            "distance_km": distance_km,
            "travel_time_hours": travel_hours,
            "fuel_consumed": fuel_needed,
            "status": unit.status.value
        }

    def return_to_base(self, unit_id: str, instant: bool = False) -> Tuple[MovementResult, Dict[str, Any]]:
        """
        Return a unit to its home base.

        Args:
            unit_id: The unit to return
            instant: If True, move instantly

        Returns:
            Tuple of (result_code, details_dict)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return MovementResult.UNIT_NOT_FOUND, {"error": "Unit not found"}

        base = map_service.get_base(self.country_code, unit.home_base_id)
        if not base:
            return MovementResult.BASE_NOT_FOUND, {"error": "Home base not found"}

        result, details = self.deploy_unit(unit_id, base.location, instant)

        if result == MovementResult.SUCCESS:
            # Update unit to mark it as returning to base
            unit = self.get_unit(unit_id)
            if instant:
                unit.status = UnitStatus.IDLE
                unit.current_base_id = unit.home_base_id
                unit.assigned_operation_id = None
            else:
                unit.status = UnitStatus.RETURNING

            map_service.update_unit(self.country_code, unit)
            details["base_id"] = unit.home_base_id

        return result, details

    def transfer_to_base(
        self,
        unit_id: str,
        target_base_id: str,
        instant: bool = False
    ) -> Tuple[MovementResult, Dict[str, Any]]:
        """
        Transfer a unit to a different base.

        Args:
            unit_id: The unit to transfer
            target_base_id: The destination base
            instant: If True, move instantly

        Returns:
            Tuple of (result_code, details_dict)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return MovementResult.UNIT_NOT_FOUND, {"error": "Unit not found"}

        base = map_service.get_base(self.country_code, target_base_id)
        if not base:
            return MovementResult.BASE_NOT_FOUND, {"error": "Target base not found"}

        # Check base capacity (simplified)
        units_at_base = map_service.load_units(self.country_code).get_at_base(target_base_id)
        # For now, allow transfers without capacity check
        # In production, would check base.capabilities vs current usage

        result, details = self.deploy_unit(unit_id, base.location, instant)

        if result == MovementResult.SUCCESS:
            unit = self.get_unit(unit_id)
            if instant:
                unit.status = UnitStatus.IDLE
                unit.current_base_id = target_base_id
            details["target_base_id"] = target_base_id

            map_service.update_unit(self.country_code, unit)

        return result, details

    def process_unit_movements(self, current_time: datetime) -> List[Dict[str, Any]]:
        """
        Process all unit movements, completing any that have arrived.
        Should be called on each tick.

        Returns:
            List of units that completed their movement
        """
        completed = []
        unit_list = self.get_all_units()

        for unit in unit_list.units:
            if unit.status != UnitStatus.IN_TRANSIT or not unit.movement:
                continue

            if current_time >= unit.movement.eta:
                # Movement complete
                travel_hours = (unit.movement.eta - unit.movement.started_at).total_seconds() / 3600
                fuel_consumed = self._calculate_fuel_consumption(unit, travel_hours)

                unit.location = unit.movement.destination
                unit.fuel_percent = max(0, unit.fuel_percent - fuel_consumed)
                unit.movement = None

                # Determine final status
                if unit.status == UnitStatus.RETURNING:
                    unit.status = UnitStatus.IDLE
                    unit.current_base_id = unit.home_base_id
                    unit.assigned_operation_id = None
                else:
                    unit.status = UnitStatus.DEPLOYED

                map_service.update_unit(self.country_code, unit)

                completed.append({
                    "unit_id": unit.id,
                    "location": unit.location.model_dump(),
                    "status": unit.status.value
                })

        return completed

    def update_unit_status(
        self,
        unit_id: str,
        status: Optional[UnitStatus] = None,
        health_delta: float = 0,
        fuel_delta: float = 0,
        ammo_delta: float = 0,
        morale_delta: int = 0,
        experience_delta: int = 0
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Update unit stats (for combat results, resupply, etc.).

        Returns:
            Tuple of (success, updated_stats)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return False, {"error": "Unit not found"}

        if status:
            unit.status = status

        unit.health_percent = max(0, min(100, unit.health_percent + health_delta))
        unit.fuel_percent = max(0, min(100, unit.fuel_percent + fuel_delta))
        unit.ammo_percent = max(0, min(100, unit.ammo_percent + ammo_delta))
        unit.morale = max(0, min(100, unit.morale + morale_delta))
        unit.experience_level = max(0, min(100, unit.experience_level + experience_delta))

        # Check if unit is destroyed
        if unit.health_percent <= 0:
            unit.status = UnitStatus.DESTROYED

        map_service.update_unit(self.country_code, unit)

        return True, {
            "unit_id": unit_id,
            "status": unit.status.value,
            "health": unit.health_percent,
            "fuel": unit.fuel_percent,
            "ammo": unit.ammo_percent,
            "morale": unit.morale,
            "experience": unit.experience_level
        }

    def resupply_unit(self, unit_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Fully resupply a unit (fuel, ammo). Unit must be at a base.

        Returns:
            Tuple of (success, details)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return False, {"error": "Unit not found"}

        if not unit.current_base_id:
            return False, {"error": "Unit must be at a base to resupply"}

        unit.fuel_percent = 100
        unit.ammo_percent = 100

        map_service.update_unit(self.country_code, unit)

        return True, {
            "unit_id": unit_id,
            "fuel": 100,
            "ammo": 100
        }

    def repair_unit(self, unit_id: str, repair_amount: float = 20) -> Tuple[bool, Dict[str, Any]]:
        """
        Repair a unit. Unit must be at a base.

        Returns:
            Tuple of (success, details)
        """
        unit = self.get_unit(unit_id)
        if not unit:
            return False, {"error": "Unit not found"}

        if not unit.current_base_id:
            return False, {"error": "Unit must be at a base to repair"}

        base = map_service.get_base(self.country_code, unit.current_base_id)
        if not base or not base.capabilities.repair_capability:
            return False, {"error": "Base does not have repair capability"}

        old_health = unit.health_percent
        unit.health_percent = min(100, unit.health_percent + repair_amount)

        # If was in maintenance and now healthy, make idle
        if unit.status == UnitStatus.MAINTENANCE and unit.health_percent >= 80:
            unit.status = UnitStatus.IDLE

        map_service.update_unit(self.country_code, unit)

        return True, {
            "unit_id": unit_id,
            "old_health": old_health,
            "new_health": unit.health_percent,
            "status": unit.status.value
        }

    def get_unit_summary(self) -> Dict[str, Any]:
        """Get summary of all units."""
        unit_list = self.get_all_units()

        by_category = {}
        by_status = {}
        total_strength = 0

        for unit in unit_list.units:
            cat = unit.category.value
            by_category[cat] = by_category.get(cat, 0) + unit.quantity

            status = unit.status.value
            by_status[status] = by_status.get(status, 0) + 1

            if unit.status not in [UnitStatus.DESTROYED, UnitStatus.MAINTENANCE]:
                total_strength += unit.get_effective_strength() * unit.quantity

        return {
            "total_units": len(unit_list.units),
            "by_category": by_category,
            "by_status": by_status,
            "available_for_deployment": len(unit_list.get_available()),
            "total_effective_strength": round(total_strength, 2)
        }
