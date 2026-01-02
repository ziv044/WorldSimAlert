"""
Location-based Operations Engine.
Extends operations to support geographic targeting and unit-based execution.
"""
import random
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from backend.models.map import Coordinates
from backend.models.units import MilitaryUnit, UnitCategory, UnitStatus
from backend.models.active_operation import (
    ActiveOperation, OperationType, OperationStatus, OperationResult as OpResult
)
from backend.services.map_service import map_service
from backend.engine.unit_engine import UnitEngine


class OperationError(Exception):
    """Exception for operation errors."""
    pass


class LocationOperationsEngine:
    """
    Engine for location-based military operations.

    Integrates with the map system to:
    - Target specific coordinates
    - Assign specific units to operations
    - Track operation progress over time
    - Calculate distance-based effects
    """

    # Operation configurations
    OPERATION_CONFIG = {
        OperationType.AIR_STRIKE: {
            'allowed_categories': [UnitCategory.AIRCRAFT],
            'min_units': 1,
            'base_success_rate': 0.75,
            'base_loss_rate': 0.05,
            'duration_hours': 2,
            'political_cost': 10,
            'relations_penalty': -15,
            'fuel_consumption': 30,
            'ammo_consumption': 50
        },
        OperationType.AIR_PATROL: {
            'allowed_categories': [UnitCategory.AIRCRAFT],
            'min_units': 2,
            'base_success_rate': 0.95,
            'base_loss_rate': 0.01,
            'duration_hours': 8,
            'political_cost': 1,
            'relations_penalty': 0,
            'fuel_consumption': 40,
            'ammo_consumption': 0
        },
        OperationType.GROUND_ASSAULT: {
            'allowed_categories': [UnitCategory.GROUND],
            'min_units': 2,
            'base_success_rate': 0.60,
            'base_loss_rate': 0.15,
            'duration_hours': 24,
            'political_cost': 20,
            'relations_penalty': -25,
            'fuel_consumption': 50,
            'ammo_consumption': 60
        },
        OperationType.GROUND_PATROL: {
            'allowed_categories': [UnitCategory.GROUND],
            'min_units': 1,
            'base_success_rate': 0.90,
            'base_loss_rate': 0.02,
            'duration_hours': 12,
            'political_cost': 2,
            'relations_penalty': 0,
            'fuel_consumption': 20,
            'ammo_consumption': 5
        },
        OperationType.NAVAL_PATROL: {
            'allowed_categories': [UnitCategory.NAVAL],
            'min_units': 2,
            'base_success_rate': 0.95,
            'base_loss_rate': 0.01,
            'duration_hours': 48,
            'political_cost': 1,
            'relations_penalty': 0,
            'fuel_consumption': 25,
            'ammo_consumption': 0
        },
        OperationType.NAVAL_BLOCKADE: {
            'allowed_categories': [UnitCategory.NAVAL],
            'min_units': 3,
            'base_success_rate': 0.70,
            'base_loss_rate': 0.03,
            'duration_hours': 168,  # 1 week
            'political_cost': 15,
            'relations_penalty': -20,
            'fuel_consumption': 40,
            'ammo_consumption': 10
        },
        OperationType.RECONNAISSANCE: {
            'allowed_categories': [UnitCategory.AIRCRAFT],
            'min_units': 1,
            'base_success_rate': 0.90,
            'base_loss_rate': 0.05,
            'duration_hours': 4,
            'political_cost': 2,
            'relations_penalty': -3,
            'fuel_consumption': 20,
            'ammo_consumption': 0
        },
        OperationType.MISSILE_STRIKE: {
            'allowed_categories': [UnitCategory.MISSILE, UnitCategory.AIR_DEFENSE],
            'min_units': 1,
            'base_success_rate': 0.85,
            'base_loss_rate': 0.0,
            'duration_hours': 1,
            'political_cost': 15,
            'relations_penalty': -20,
            'fuel_consumption': 0,
            'ammo_consumption': 100  # Uses missiles
        },
        OperationType.SPECIAL_OPS: {
            'allowed_categories': [UnitCategory.SPECIAL_OPS, UnitCategory.HELICOPTER],
            'min_units': 1,
            'base_success_rate': 0.55,
            'base_loss_rate': 0.10,
            'duration_hours': 6,
            'political_cost': 8,
            'relations_penalty': -12,
            'fuel_consumption': 30,
            'ammo_consumption': 30
        }
    }

    def __init__(self, country_code: str):
        self.country_code = country_code.upper()
        self.unit_engine = UnitEngine(country_code)

    def _validate_units_for_operation(
        self,
        operation_type: OperationType,
        unit_ids: List[str]
    ) -> Tuple[bool, str, List[MilitaryUnit]]:
        """
        Validate that units can perform the operation.

        Returns:
            Tuple of (is_valid, error_message, units)
        """
        config = self.OPERATION_CONFIG.get(operation_type)
        if not config:
            return False, f"Unknown operation type: {operation_type}", []

        if len(unit_ids) < config['min_units']:
            return False, f"Need at least {config['min_units']} units", []

        units = []
        for unit_id in unit_ids:
            unit = self.unit_engine.get_unit(unit_id)
            if not unit:
                return False, f"Unit {unit_id} not found", []

            if unit.category not in config['allowed_categories']:
                return False, f"Unit {unit_id} ({unit.category}) cannot perform {operation_type.value}", []

            if not unit.can_deploy():
                return False, f"Unit {unit_id} cannot deploy (status: {unit.status})", []

            units.append(unit)

        return True, "OK", units

    def _calculate_operation_success(
        self,
        operation_type: OperationType,
        units: List[MilitaryUnit],
        distance_km: float
    ) -> float:
        """Calculate success probability for an operation."""
        config = self.OPERATION_CONFIG[operation_type]

        # Base success rate
        success_rate = config['base_success_rate']

        # Average unit effectiveness
        avg_strength = sum(u.get_effective_strength() for u in units) / len(units)
        success_rate *= (0.7 + 0.3 * avg_strength)  # 70-100% of base based on strength

        # Distance penalty for aircraft/missiles
        for unit in units:
            if unit.combat_radius_km and unit.combat_radius_km > 0:
                if distance_km > unit.combat_radius_km:
                    # Significant penalty for beyond combat radius
                    success_rate *= 0.5
                elif distance_km > unit.combat_radius_km * 0.8:
                    # Minor penalty at edge of range
                    success_rate *= 0.9

        # More units = slightly better odds (diminishing returns)
        unit_bonus = min(1.2, 1 + 0.05 * (len(units) - 1))
        success_rate *= unit_bonus

        return min(0.95, max(0.1, success_rate))

    def plan_operation(
        self,
        operation_type: str,
        target_location: Coordinates,
        unit_ids: List[str],
        target_name: Optional[str] = None,
        target_country_code: Optional[str] = None,
        is_covert: bool = False
    ) -> Dict:
        """
        Plan an operation and get estimated outcomes.

        Does not execute the operation.
        """
        try:
            op_type = OperationType(operation_type)
        except ValueError:
            return {
                'valid': False,
                'error': f'Unknown operation type: {operation_type}',
                'available_types': [t.value for t in OperationType if t in self.OPERATION_CONFIG]
            }

        # Validate units
        is_valid, error, units = self._validate_units_for_operation(op_type, unit_ids)
        if not is_valid:
            return {'valid': False, 'error': error}

        # Calculate distance
        if units:
            origin = units[0].location
            distance_km = origin.distance_to(target_location)
        else:
            distance_km = 0

        # Check range
        for unit in units:
            if unit.combat_radius_km and distance_km > unit.combat_radius_km * 2:
                return {
                    'valid': False,
                    'error': f"Unit {unit.id} out of range ({distance_km:.0f}km > {unit.combat_radius_km * 2:.0f}km)"
                }

        config = self.OPERATION_CONFIG[op_type]

        # Calculate estimates
        success_rate = self._calculate_operation_success(op_type, units, distance_km)
        travel_time_hours = self._estimate_travel_time(units, distance_km)
        total_duration = config['duration_hours'] + travel_time_hours * 2  # Round trip

        return {
            'valid': True,
            'operation_type': operation_type,
            'target_location': {'lat': target_location.lat, 'lng': target_location.lng},
            'target_name': target_name,
            'target_country_code': target_country_code,
            'unit_ids': unit_ids,
            'units_summary': [{'id': u.id, 'type': u.unit_type, 'strength': u.get_effective_strength()} for u in units],
            'distance_km': round(distance_km, 1),
            'estimated_success_rate': round(success_rate * 100, 1),
            'estimated_loss_rate': round(config['base_loss_rate'] * 100, 1),
            'estimated_duration_hours': round(total_duration, 1),
            'political_cost': config['political_cost'],
            'relations_impact': config['relations_penalty'],
            'fuel_consumption': config['fuel_consumption'],
            'ammo_consumption': config['ammo_consumption'],
            'is_covert': is_covert
        }

    def _estimate_travel_time(self, units: List[MilitaryUnit], distance_km: float) -> float:
        """Estimate travel time for units."""
        if not units:
            return 0

        # Use slowest unit speed
        speeds = [u.speed_kmh or 100 for u in units]
        min_speed = min(speeds)

        return distance_km / min_speed if min_speed > 0 else 0

    def create_operation(
        self,
        operation_type: str,
        name: str,
        target_location: Coordinates,
        unit_ids: List[str],
        target_name: Optional[str] = None,
        target_country_code: Optional[str] = None,
        duration_hours: Optional[int] = None,
        is_covert: bool = False
    ) -> Tuple[bool, Dict]:
        """
        Create and queue a new operation.

        Returns:
            Tuple of (success, operation_details_or_error)
        """
        # Plan first to validate
        plan = self.plan_operation(
            operation_type, target_location, unit_ids,
            target_name, target_country_code, is_covert
        )

        if not plan.get('valid'):
            return False, plan

        op_type = OperationType(operation_type)
        config = self.OPERATION_CONFIG[op_type]

        # Get units and origin
        _, _, units = self._validate_units_for_operation(op_type, unit_ids)
        origin_location = units[0].location

        # Create operation
        now = datetime.utcnow()
        op_duration = duration_hours or config['duration_hours']

        operation = ActiveOperation(
            id=f"op_{uuid.uuid4().hex[:8]}",
            name=name,
            country_code=self.country_code,
            operation_type=op_type,
            status=OperationStatus.PLANNING,
            created_at=now,
            origin_location=origin_location,
            target_location=target_location,
            target_name=target_name,
            target_country_code=target_country_code,
            assigned_unit_ids=unit_ids,
            duration_hours=op_duration,
            success_probability=plan['estimated_success_rate'] / 100,
            loss_probability=plan['estimated_loss_rate'] / 100,
            political_cost=config['political_cost'],
            estimated_cost_millions=self._estimate_cost(units, config),
            is_covert=is_covert,
            unit_types_involved={u.unit_type: 1 for u in units}
        )

        # Save operation
        map_service.add_operation(self.country_code, operation)

        # Update units
        for unit in units:
            unit.assigned_operation_id = operation.id
            map_service.update_unit(self.country_code, unit)

        return True, {
            'operation_id': operation.id,
            'status': operation.status.value,
            'estimated_success': plan['estimated_success_rate'],
            'estimated_duration': plan['estimated_duration_hours']
        }

    def _estimate_cost(self, units: List[MilitaryUnit], config: Dict) -> float:
        """Estimate operation cost in millions."""
        # Base cost from fuel and ammo
        cost = 0
        for unit in units:
            # Rough cost estimate per unit
            if unit.category == UnitCategory.AIRCRAFT:
                cost += 0.5  # $500K per sortie
            elif unit.category == UnitCategory.NAVAL:
                cost += 0.2  # $200K per day
            elif unit.category == UnitCategory.GROUND:
                cost += 0.1  # $100K per day

        # Add munitions cost
        cost += config['ammo_consumption'] * 0.01  # $10K per ammo unit

        return round(cost, 2)

    def start_operation(self, operation_id: str) -> Tuple[bool, Dict]:
        """
        Start a planned operation (deploy units).

        Returns:
            Tuple of (success, details)
        """
        operation = map_service.get_operation(self.country_code, operation_id)
        if not operation:
            return False, {'error': 'Operation not found'}

        if operation.status != OperationStatus.PLANNING:
            return False, {'error': f'Cannot start operation in status: {operation.status}'}

        now = datetime.utcnow()

        # Deploy units
        for unit_id in operation.assigned_unit_ids:
            result, _ = self.unit_engine.deploy_unit(
                unit_id,
                operation.target_location,
                instant=False
            )

        # Update operation status
        operation.status = OperationStatus.DEPLOYING
        operation.started_at = now

        # Calculate ETA based on slowest unit
        unit_list = map_service.load_units(self.country_code)
        travel_times = []
        for unit_id in operation.assigned_unit_ids:
            unit = unit_list.get_by_id(unit_id)
            if unit and unit.movement:
                travel_times.append((unit.movement.eta - now).total_seconds())

        if travel_times:
            max_travel = max(travel_times)
            operation.estimated_completion = now + timedelta(
                seconds=max_travel + operation.duration_hours * 3600
            )

        map_service.update_operation(self.country_code, operation)

        return True, {
            'operation_id': operation_id,
            'status': operation.status.value,
            'estimated_completion': operation.estimated_completion.isoformat() if operation.estimated_completion else None
        }

    def process_operations(self, current_time: datetime) -> List[Dict]:
        """
        Process all active operations, updating progress and completing finished ones.

        Should be called on each tick.

        Returns:
            List of operation updates
        """
        updates = []
        ops_list = map_service.load_operations(self.country_code)

        for operation in ops_list.operations:
            if not operation.is_active():
                continue

            update = self._process_single_operation(operation, current_time)
            if update:
                updates.append(update)

        return updates

    def _process_single_operation(
        self,
        operation: ActiveOperation,
        current_time: datetime
    ) -> Optional[Dict]:
        """Process a single operation."""
        # Check if units have arrived (for deploying operations)
        if operation.status == OperationStatus.DEPLOYING:
            units_arrived = self._check_units_arrived(operation)
            if units_arrived:
                operation.status = OperationStatus.ACTIVE
                operation.phase = "engagement"
                map_service.update_operation(self.country_code, operation)
                return {
                    'operation_id': operation.id,
                    'event': 'units_arrived',
                    'status': operation.status.value
                }

        # Update progress for active operations
        if operation.status == OperationStatus.ACTIVE and operation.started_at:
            elapsed = (current_time - operation.started_at).total_seconds() / 3600
            total_duration = operation.duration_hours

            operation.progress_percent = min(100, (elapsed / total_duration) * 100)

            # Check if operation is complete
            if operation.progress_percent >= 100:
                return self._complete_operation(operation)

            map_service.update_operation(self.country_code, operation)

        return None

    def _check_units_arrived(self, operation: ActiveOperation) -> bool:
        """Check if all units have arrived at target."""
        unit_list = map_service.load_units(self.country_code)

        for unit_id in operation.assigned_unit_ids:
            unit = unit_list.get_by_id(unit_id)
            if not unit:
                continue
            if unit.status == UnitStatus.IN_TRANSIT:
                return False

        return True

    def _complete_operation(self, operation: ActiveOperation) -> Dict:
        """
        Complete an operation and calculate results.

        Returns:
            Operation completion details
        """
        config = self.OPERATION_CONFIG.get(operation.operation_type, {})

        # Roll for success
        roll = random.random()
        success = roll < operation.success_probability

        # Calculate losses
        friendly_losses = {}
        unit_list = map_service.load_units(self.country_code)

        for unit_id in operation.assigned_unit_ids:
            unit = unit_list.get_by_id(unit_id)
            if not unit:
                continue

            # Chance of losses
            loss_roll = random.random()
            loss_rate = operation.loss_probability
            if not success:
                loss_rate *= 1.5

            if loss_roll < loss_rate:
                # Calculate damage
                damage = random.uniform(10, 40)
                if not success:
                    damage *= 1.5

                # Apply damage
                self.unit_engine.update_unit_status(
                    unit_id,
                    health_delta=-damage,
                    fuel_delta=-config.get('fuel_consumption', 20),
                    ammo_delta=-config.get('ammo_consumption', 20),
                    experience_delta=5 if success else 2,
                    morale_delta=10 if success else -10
                )

                if damage > 30:
                    friendly_losses[unit.unit_type] = friendly_losses.get(unit.unit_type, 0) + 1
            else:
                # No damage, just resource consumption
                self.unit_engine.update_unit_status(
                    unit_id,
                    fuel_delta=-config.get('fuel_consumption', 20) * 0.5,
                    ammo_delta=-config.get('ammo_consumption', 20) * 0.5,
                    experience_delta=3 if success else 1
                )

        # Calculate enemy casualties
        enemy_casualties = 0
        enemy_equipment = {}
        if success:
            enemy_casualties = random.randint(10, 100)
            enemy_equipment = {'equipment': random.randint(1, 10)}

        # Create result
        result = OpResult(
            success=success,
            objectives_achieved=1 if success else 0,
            objectives_total=1,
            enemy_casualties=enemy_casualties,
            enemy_equipment_destroyed=enemy_equipment,
            friendly_casualties=sum(friendly_losses.values()),
            friendly_equipment_lost=friendly_losses,
            cost_millions=operation.estimated_cost_millions,
            diplomatic_impact={operation.target_country_code: config.get('relations_penalty', 0)}
            if operation.target_country_code else {}
        )

        # Update operation
        operation.status = OperationStatus.COMPLETED if success else OperationStatus.FAILED
        operation.completed_at = datetime.utcnow()
        operation.progress_percent = 100
        operation.result = result

        map_service.update_operation(self.country_code, operation)

        # Return units to base
        for unit_id in operation.assigned_unit_ids:
            self.unit_engine.return_to_base(unit_id, instant=False)

        return {
            'operation_id': operation.id,
            'event': 'completed',
            'success': success,
            'result': result.model_dump()
        }

    def cancel_operation(self, operation_id: str) -> Tuple[bool, Dict]:
        """Cancel a planned or deploying operation."""
        operation = map_service.get_operation(self.country_code, operation_id)
        if not operation:
            return False, {'error': 'Operation not found'}

        if not operation.can_cancel():
            return False, {'error': f'Cannot cancel operation in status: {operation.status}'}

        # Return units
        for unit_id in operation.assigned_unit_ids:
            unit = self.unit_engine.get_unit(unit_id)
            if unit:
                unit.assigned_operation_id = None
                if unit.status in [UnitStatus.IN_TRANSIT, UnitStatus.DEPLOYED]:
                    self.unit_engine.return_to_base(unit_id, instant=False)
                else:
                    unit.status = UnitStatus.IDLE
                    map_service.update_unit(self.country_code, unit)

        operation.status = OperationStatus.CANCELLED
        operation.completed_at = datetime.utcnow()
        map_service.update_operation(self.country_code, operation)

        return True, {
            'operation_id': operation_id,
            'status': 'cancelled'
        }

    def get_active_operations(self) -> List[Dict]:
        """Get all active operations."""
        ops_list = map_service.load_operations(self.country_code)
        return [op.model_dump() for op in ops_list.get_active()]

    def get_operation_summary(self) -> Dict:
        """Get summary of all operations."""
        ops_list = map_service.load_operations(self.country_code)

        by_status = {}
        by_type = {}

        for op in ops_list.operations:
            status = op.status.value
            by_status[status] = by_status.get(status, 0) + 1

            op_type = op.operation_type.value
            by_type[op_type] = by_type.get(op_type, 0) + 1

        return {
            'total': len(ops_list.operations),
            'active': len(ops_list.get_active()),
            'by_status': by_status,
            'by_type': by_type
        }
